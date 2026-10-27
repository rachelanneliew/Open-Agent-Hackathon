"""Bounded, serialized adapter to the pinned official H-MEM reference.

Each call starts a new Node process. Customer state and ledger are published
atomically only after successful reference execution. No financial action IO.
"""
from __future__ import annotations
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import tempfile
import time

BRIDGE_DIR = Path(__file__).resolve().parent / 'hmem_bridge'
DEFAULT_REFERENCE = Path(__file__).resolve().parents[1] / 'outputs/dependencies/hmem/reference/src/index.ts'
DEFAULT_PERSIST = Path(__file__).resolve().parents[1] / 'outputs/hmem-v1'
MAX_OUTPUT = 256 * 1024
MAX_STATE = 8 * 1024 * 1024
CUSTOMER = re.compile(r'^CUST-\d{3,}$')


class MemoryError(RuntimeError):
    """Stable public error code, never subprocess output or private paths."""


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('nonfinite JSON')
    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError('nonfinite JSON')
        return parsed
    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid, parse_float=number)
    except RecursionError:
        raise ValueError('excessively nested JSON') from None
    pending = [(result, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > 64:
            raise ValueError('excessively nested JSON')
        if type(value) is dict:
            pending.extend((v, depth + 1) for v in value.values())
        elif type(value) is list:
            pending.extend((v, depth + 1) for v in value)
    return result


def customer_scope(customer_id):
    if type(customer_id) is not str or not CUSTOMER.fullmatch(customer_id):
        raise MemoryError('memory_customer_invalid')
    return 'customer:' + customer_id


def bounded_process(command, payload, *, env, deadline):
    """Cap both pipes while running; kill/reap the process group on failure."""
    with tempfile.TemporaryFile() as incoming:
        incoming.write(payload)
        incoming.seek(0)
        try:
            proc = subprocess.Popen(command, stdin=incoming, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, env=env, start_new_session=True)
        except OSError:
            raise MemoryError('memory_runtime_missing') from None
        output, total = bytearray(), 0
        try:
            with selectors.DefaultSelector() as selector:
                for stream in (proc.stdout, proc.stderr):
                    os.set_blocking(stream.fileno(), False)
                    selector.register(stream, selectors.EVENT_READ)
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise MemoryError('memory_timeout')
                    for key, _ in selector.select(min(remaining, .05)):
                        chunk = os.read(key.fileobj.fileno(), 16384)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        total += len(chunk)
                        if total > MAX_OUTPUT:
                            raise MemoryError('memory_output_limit')
                        if key.fileobj is proc.stdout:
                            output.extend(chunk)
            proc.wait(timeout=max(.001, deadline - time.monotonic()))
            if proc.returncode:
                raise MemoryError('memory_reference_failed')
            return bytes(output)
        except subprocess.TimeoutExpired:
            raise MemoryError('memory_timeout') from None
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            proc.stdout.close()
            proc.stderr.close()


class HmemClient:
    def __init__(self, persist_dir=DEFAULT_PERSIST, *, timeout=15):
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 60:
            raise MemoryError('memory_timeout_invalid')
        self.persist_dir = Path(persist_dir).expanduser().resolve()
        self.timeout = timeout

    def _runtime(self, deadline):
        pin = json.loads((BRIDGE_DIR / 'reference-pin.json').read_text())
        reference = Path(os.environ.get('HMEM_REFERENCE_SRC', DEFAULT_REFERENCE)).expanduser().resolve()
        runner = Path(os.environ.get('HMEM_TSX_PACKAGE', BRIDGE_DIR / 'node_modules/tsx')).expanduser().resolve()
        node = os.environ.get('HMEM_NODE') or shutil.which('node')
        if not node or not reference.is_file() or not (runner / 'package.json').is_file():
            raise MemoryError('memory_dependency_missing')
        try:
            for rel, expected in pin['runtime_sha256'].items():
                if hashlib.sha256((reference.parent / rel).read_bytes()).hexdigest() != expected:
                    raise MemoryError('memory_reference_pin_mismatch')
            if json.loads((runner / 'package.json').read_text())['version'] != pin['tsx']:
                raise MemoryError('memory_runner_pin_mismatch')
        except (OSError, ValueError, KeyError):
            raise MemoryError('memory_dependency_invalid') from None
        env = {'PATH': str(Path(node).parent), 'TSX_DISABLE_CACHE': '1',
               'HMEM_REFERENCE_SRC': str(reference)}
        if bounded_process([node, '--version'], b'', env=env, deadline=deadline).strip().decode() != 'v' + pin['node']:
            raise MemoryError('memory_node_pin_mismatch')
        return [node, '--import', str(runner / 'dist/loader.mjs'), str(BRIDGE_DIR / 'server.ts')], env

    @contextmanager
    def _locked(self, customer_id, deadline):
        customer_scope(customer_id)
        self.persist_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        partition = self.persist_dir / customer_id
        if partition.is_symlink():
            raise MemoryError('memory_store_invalid')
        partition.mkdir(mode=0o700, exist_ok=True)
        fd = os.open(partition / '.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'a') as lock:
            while True:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise MemoryError('memory_lock_timeout') from None
                    time.sleep(.02)
            try:
                yield partition
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    @staticmethod
    def _read(path, limit=MAX_STATE):
        if path.is_symlink():
            raise MemoryError('memory_store_invalid')
        with path.open('rb') as stream:
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            raise MemoryError('memory_store_limit')
        return raw

    def _invoke(self, customer_id, payload):
        deadline = time.monotonic() + self.timeout
        customer_scope(customer_id)
        try:
            command, env = self._runtime(deadline)
            with self._locked(customer_id, deadline) as partition:
                snapshot = partition / 'snapshot.json'
                with tempfile.TemporaryDirectory(prefix='.operation-', dir=partition) as directory:
                    stage = Path(directory)
                    if snapshot.exists():
                        saved = strict_json(self._read(snapshot))
                        if (type(saved) is not dict or set(saved) != {'version', 'state', 'ledger'} or
                                type(saved['version']) is not int or saved['version'] != 1):
                            raise MemoryError('memory_store_invalid')
                        if type(saved['ledger']) is not list or type(saved['state']) is not dict:
                            raise MemoryError('memory_store_invalid')
                        (stage / 'state.json').write_text(json.dumps(saved['state'], allow_nan=False))
                        (stage / 'ledger.jsonl').write_text(''.join(json.dumps(x, allow_nan=False) + '\n' for x in saved['ledger']))
                    request = dict(payload, persistDir=str(stage), chatId=customer_scope(customer_id))
                    wire = json.dumps(request, allow_nan=False).encode()
                    if len(wire) > 32 * 1024:
                        raise MemoryError('memory_input_limit')
                    raw = bounded_process(command, wire, env=env, deadline=deadline)
                    result = strict_json(raw)
                    self._validate_result(result, payload['op'], customer_id)
                    state = strict_json(self._read(stage / 'state.json'))
                    ledger = [strict_json(line) for line in self._read(stage / 'ledger.jsonl').splitlines() if line]
                    packed = json.dumps(dict(version=1, state=state, ledger=ledger), allow_nan=False).encode()
                    if len(packed) > MAX_STATE:
                        raise MemoryError('memory_store_limit')
                    pending = stage / 'snapshot.json'
                    with pending.open('xb') as stream:
                        os.chmod(pending, 0o600)
                        stream.write(packed)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(pending, snapshot)
                    folder = os.open(partition, os.O_RDONLY)
                    try:
                        os.fsync(folder)
                    finally:
                        os.close(folder)
                    return result
        except MemoryError:
            raise
        except (OSError, ValueError, TypeError, KeyError, UnicodeError):
            raise MemoryError('memory_storage_or_protocol_failed') from None

    @staticmethod
    def _validate_result(result, op, customer_id):
        expected = {'ok', 'memory', 'storage_status'} if op == 'add' else {'ok', 'memories'}
        if type(result) is not dict or set(result) != expected or result['ok'] is not True:
            raise MemoryError('memory_protocol_invalid')
        if op == 'add':
            if result['storage_status'] not in ('stored', 'reused'):
                raise MemoryError('memory_protocol_invalid')
            records = [result['memory']]
        else:
            records = result['memories']
            if type(records) is not list or len(records) > 100:
                raise MemoryError('memory_protocol_invalid')
        fields = {'id', 'content', 'source', 'chatId', 'tags', 'provenance', 'timestamp'}
        for record in records:
            if type(record) is not dict or set(record) != fields or not re.fullmatch(r'mem-[1-9][0-9]*', str(record['id'])):
                raise MemoryError('memory_protocol_invalid')
            if type(record['tags']) is not list or any(type(t) is not str for t in record['tags']):
                raise MemoryError('memory_protocol_invalid')
            if record['chatId'] != customer_scope(customer_id) or customer_scope(customer_id) not in record['tags']:
                raise MemoryError('memory_scope_violation')
            if type(record['content']) is not str or len(record['content']) > 8192 or type(record['timestamp']) is not int:
                raise MemoryError('memory_protocol_invalid')
            if type(record['source']) is not str or type(record['provenance']) is not dict:
                raise MemoryError('memory_protocol_invalid')

    def add(self, input_record):
        if type(input_record) is not dict:
            raise MemoryError('memory_input_invalid')
        scope = input_record.get('chatId', '')
        if type(scope) is not str or not scope.startswith('customer:'):
            raise MemoryError('memory_customer_invalid')
        return self._invoke(scope[9:], {'op': 'add', 'input': dict(input_record)})

    def query(self, query, *, chat_id, top_n=5, threshold=.35):
        if type(query) is not str or not 1 <= len(query) <= 2048 or type(top_n) is not int or not 1 <= top_n <= 20:
            raise MemoryError('memory_query_invalid')
        if type(threshold) not in (int, float) or not math.isfinite(threshold) or not 0 <= threshold <= 1:
            raise MemoryError('memory_query_invalid')
        if type(chat_id) is not str or not chat_id.startswith('customer:'):
            raise MemoryError('memory_customer_invalid')
        return self._invoke(chat_id[9:], dict(op='query', query=query, topN=top_n, threshold=threshold))

    def list(self, *, customer_id):
        return self._invoke(customer_id, {'op': 'list'})['memories']
