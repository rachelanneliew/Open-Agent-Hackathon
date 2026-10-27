"""Opt-in reset/replay of disposable PostgreSQL and memory test namespaces.

No target DSN, existing container, memory path or live provider can be supplied.
The established integration harness owns creation, fresh-state reset and cleanup.
This is a scripted rehearsal, not a Zetaris or Nightshift demonstration.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PLAN = {
    'mode': 'scripted_isolated_replay',
    'reset_scope': 'New disposable PostgreSQL container; two fresh cloned databases and private temporary memory/journal namespaces; owned resources removed afterward.',
    'sources': 'Read-only copies of committed synthetic files; shared database and memory untouched.',
    'real_components': ['PostgreSQL', 'canonical policy/critic/controller/action service', 'pinned H-MEM reference with mock embeddings'],
    'simulated_components': ['model responses', 'Zetaris transport (direct isolated PostgreSQL bundle read)'],
    'requires': ['Docker already running', 'existing postgres:16-alpine image', 'application Python dependencies', 'pinned H-MEM/Node setup'],
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reset-isolated-demo', action='store_true',
                        help='Intentionally create, reset/replay twice and clean only owned disposable demo state.')
    args = parser.parse_args(argv)
    if not args.reset_isolated_demo:
        print(json.dumps(dict(PLAN, status='preview_only', next='Repeat with --reset-isolated-demo to execute.'), indent=2))
        return 0
    env = dict(os.environ, DISPUTE_REPLAY_TESTS='1', DISPUTE_ACTION_TESTS='1',
               DISPUTE_HMEM_TESTS='1', PYTHONDONTWRITEBYTECODE='1')
    # No timeout kill: unittest owns finally/cleanup. The underlying model-free
    # database/reference operations already have finite deadlines.
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_reliability.py', '-k', 'test_reset_replay_twice', '-v'],
        cwd=ROOT, env=env, text=True, capture_output=True)
    records = [line.removeprefix('REPLAY_JSON=') for line in result.stdout.splitlines()
               if line.startswith('REPLAY_JSON=')]
    if result.returncode or len(records) != 1:
        # Test diagnostics contain only synthetic fixture details, not private
        # application config. Preserve them for actionable setup/failure evidence.
        sys.stderr.write(result.stderr)
        print(json.dumps(dict(PLAN, status='failed', report=None), indent=2))
        return 1
    report = json.loads(records[0])
    print(json.dumps(dict(PLAN, status='passed', report=report), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
