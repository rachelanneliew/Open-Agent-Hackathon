"""Hard deadlines for JDBC/Psycopg; credentials never enter arguments or traces."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

from integration.fresh_reads import MAX_BUNDLE_BYTES, _json
from .action_service import CommitRequest, commit_simulated_decision
from .fresh_tools import FreshSnapshot, get_snapshot
from .schemas import CommitResult

ROOT = Path(__file__).resolve().parents[1]


class BoundaryError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _action_environment():
    # Load just this application's DSN. Never source shell or print credentials.
    if not os.environ.get('DISPUTE_ACTION_DSN'):
        path = ROOT / '.env.local'
        if path.exists():
            for line in path.read_text().splitlines():
                key, sep, value = line.partition('=')
                if sep and key.strip() == 'DISPUTE_ACTION_DSN':
                    os.environ[key.strip()] = ' '.join(shlex.split(value, comments=True))


def _call(operation, payload, timeout_seconds):
    try:
        encoded = json.dumps({'operation': operation, 'payload': payload}, allow_nan=False)
        if len(encoded.encode()) > MAX_BUNDLE_BYTES:
            raise BoundaryError('input_too_large')
        completed = subprocess.run([sys.executable, '-m', 'app.runtime_io'], input=encoded,
            text=True, capture_output=True, timeout=timeout_seconds, cwd=ROOT, check=False)
        if completed.returncode:
            raise BoundaryError(operation + '_unavailable')
        response = _json(completed.stdout)
        if type(response) is not dict or set(response) != {'result'}:
            raise BoundaryError(operation + '_unavailable')
        return response['result']
    except subprocess.TimeoutExpired:
        # subprocess.run kills and waits. Commit could have reached PostgreSQL;
        # the controller retains the identical request and reports unconfirmed.
        raise BoundaryError(operation + '_timeout') from None
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        raise BoundaryError(operation + '_unavailable') from None


def read_snapshot(dispute_id, *, timeout_seconds):
    return FreshSnapshot.from_dict(_call('read', {'dispute_id': dispute_id}, timeout_seconds))


def commit(request, *, timeout_seconds):
    return CommitResult.from_dict(_call('commit', request.to_dict(), timeout_seconds))


def _main():
    try:
        request = _json(sys.stdin.read(MAX_BUNDLE_BYTES + 1))
        if set(request) != {'operation', 'payload'}:
            raise ValueError()
        if request['operation'] == 'read' and set(request['payload']) == {'dispute_id'}:
            result = get_snapshot(request['payload']['dispute_id'])
        elif request['operation'] == 'commit':
            payload = CommitRequest.from_dict(request['payload'])
            _action_environment()
            result = commit_simulated_decision(payload)
        else:
            raise ValueError()
        encoded = json.dumps({'result': result.to_dict()}, allow_nan=False)
        if len(encoded.encode()) > MAX_BUNDLE_BYTES:
            raise ValueError()
    except Exception:
        encoded = '{"error":"boundary_unavailable"}'
    print(encoded)


if __name__ == '__main__':
    _main()
