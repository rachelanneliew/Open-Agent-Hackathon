"""Durable UI request coordination; all decisions still use Controller.

A request ID identifies a UI operation, not a financial idempotency key. The
canonical journal owns the exact action request. Interrupted operations never
restart automatically: recover their saved request or start again if no action
was dispatched. One server owns the private operation directory via flock.
"""
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import tempfile
import threading

from integration.fresh_reads import _json
from integration.get_dispute_context import validate_dispute_id
from .journal import FileJournal, load_request
from .schemas import require, uuid_id


class JobError(ValueError):
    pass


def _save(path, value):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            os.chmod(temporary, 0o600)
            json.dump(value, file, allow_nan=False)
            file.flush()
            os.fsync(file.fileno())
            os.replace(temporary, path)
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        finally:
            temporary.unlink(missing_ok=True)


class Jobs:
    def __init__(self, directory, journal_directory, *, controller_factory, memory_retry):
        self.directory, self.journal_directory = Path(directory), Path(journal_directory)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lease = open(self.directory / '.lock', 'a+b')
        os.chmod(self.directory / '.lock', 0o600)
        try:
            fcntl.flock(self.lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lease.close()
            raise JobError('ui_store_already_open') from None
        self.lock, self.active, self.threads = threading.RLock(), None, []
        self.controller_factory, self.memory_retry = controller_factory, memory_retry

    def close(self):
        for thread in self.threads:
            thread.join()
        self.lease.close()

    def _path(self, operation_id):
        uuid_id(operation_id)
        return self.directory / (operation_id + '.json')

    def get(self, operation_id):
        with self.lock:
            path = self._path(operation_id)
            with path.open('rb') as file:
                # UI traces are bounded independently of strict action payloads.
                raw = file.read(16 * 1024 * 1024 + 1)
            require(len(raw) <= 16 * 1024 * 1024, 'UI record too large')
            value = json.loads(raw)
            require(value['operation_id'] == operation_id, 'Operation mismatch')
            if value['status'] == 'running' and operation_id != self.active:
                value['status'], value['error'] = 'interrupted', 'server_interrupted_recover_saved_request'
            return value

    def submit(self, payload):
        require(type(payload) is dict and set(payload) == {'operation_id', 'dispute_id', 'kind', 'run_id'}, 'Invalid operation')
        operation_id, did = payload['operation_id'], payload['dispute_id']
        path = self._path(operation_id)
        validate_dispute_id(did)
        require(payload['kind'] in ('investigate', 'recover', 'memory'), 'Invalid operation kind')
        if payload['kind'] == 'investigate':
            require(payload['run_id'] is None, 'New investigation cannot supply a run')
        else:
            uuid_id(payload['run_id'])
            saved = load_request(self.journal_directory / (payload['run_id'] + '.request.json'))
            require(saved.context.reference.dispute_id == did, 'Recovery outside case')
        with self.lock:
            if path.exists():
                old = self.get(operation_id)
                if old['input'] != payload:
                    raise JobError('operation_id_conflict')
                return old
            if self.active:
                old = self.get(self.active)
                if old['input']['dispute_id'] == did and old['input']['kind'] == payload['kind'] and old['input']['run_id'] == payload['run_id']:
                    return old
                raise JobError('another_operation_running')
            if len(list(self.directory.glob('*.json'))) >= 1000:
                raise JobError('ui_history_capacity_reached')
            job = dict(operation_id=operation_id, input=deepcopy(payload), status='running',
                       run_id=payload['run_id'], result=None, error=None)
            _save(path, job)  # Must succeed BEFORE running any workflow.
            self.active = operation_id
            thread = threading.Thread(target=self._run, args=(job,), daemon=False)
            self.threads = [t for t in self.threads if t.is_alive()] + [thread]
            thread.start()
            return deepcopy(job)

    def _run(self, job):
        owner, captured = self, {}
        class Journal(FileJournal):
            def prepare(self, request):
                path = super().prepare(request)
                # Durable association before Controller may dispatch the action.
                job['run_id'] = request.run_id
                captured['context'] = request.context.to_dict()
                with owner.lock:
                    _save(owner._path(job['operation_id']), job)
                return path
        try:
            journal = Journal(self.journal_directory)
            controller = self.controller_factory(journal)
            original_read = controller.read_snapshot
            def read(did, **kwargs):
                value = original_read(did, **kwargs)
                if did == job['input']['dispute_id']:
                    captured['context'] = value.context.to_dict()
                return value
            controller.read_snapshot = read
            kind = job['input']['kind']
            if kind == 'investigate':
                result = controller.run(job['input']['dispute_id'])
            else:
                path = self.journal_directory / (job['run_id'] + '.request.json')
                request = load_request(path)
                captured['context'] = request.context.to_dict()
                if kind == 'memory':
                    job['result'] = self.memory_retry(self.journal_directory / (job['run_id'] + '.trace.json'))
                    result = None
                else:
                    result = controller.retry(request, str(path.resolve()))
                    captured.update(policy=request.policy.to_dict(), proposal=request.proposal.to_dict(),
                                    critic=request.critic.to_dict())
            if result is not None:
                job['run_id'] = result.state.run_id
                job['result'] = result.to_dict()
                job['result'].pop('recovery_request', None)  # No local paths in browser data.
                job['result']['display'] = captured
            job['status'] = 'finished'
        except Exception:
            job['status'], job['error'] = 'failed', 'operation_unavailable_check_saved_request'
        finally:
            with self.lock:
                try:
                    _save(self._path(job['operation_id']), job)
                finally:
                    self.active = None

    def recoveries(self, did):
        """Known local requests, including pre-UI runs. No auto-dispatch on read."""
        validate_dispute_id(did)
        paths = sorted(self.journal_directory.glob('*.request.json'))
        if len(paths) > 1000:
            raise JobError('recovery_inventory_capacity_reached')
        rows = []
        for path in paths:
            request = load_request(path)
            if request.context.reference.dispute_id != did:
                continue
            trace = self.journal_directory / (request.run_id + '.trace.json')
            status = 'unconfirmed'
            if trace.exists():
                from .schemas import RunState
                with trace.open('rb') as file:
                    value = _json(file.read(2 * 1024 * 1024 + 1).decode())
                state = RunState.from_dict(value['state'])
                require(state.run_id == request.run_id, 'Trace identity mismatch')
                if state.commit_result:
                    status = state.commit_result.status.value
            rows.append(dict(run_id=request.run_id, status=status,
                             memory_retry_available=status in ('committed', 'reused')))
        return rows
