"""Collect both test roots in separate processes and report exact counts.

Default: offline tests with explicit integration skips. --integrations enables
disposable PostgreSQL, pinned H-MEM and local HTTP fixtures, never live providers.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FLAGS = ('DISPUTE_ACTION_TESTS', 'DISPUTE_STORAGE_TESTS', 'DISPUTE_HMEM_TESTS',
         'DISPUTE_NIGHTSHIFT_HTTP_TESTS', 'DISPUTE_UI_HTTP_TESTS')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrations', action='store_true')
    parser.add_argument('--root', choices=('tests', 'agent/tests'), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.root:
        loader = unittest.TestLoader()
        suite = loader.discover(args.root)
        collected = suite.countTestCases()
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        report = dict(root=args.root, collected=collected, run=result.testsRun,
            passed=result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
                - len(result.expectedFailures) - len(result.unexpectedSuccesses),
            failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
            expected_failures=len(result.expectedFailures), unexpected_successes=len(result.unexpectedSuccesses),
            collection_errors=len(loader.errors))
        print('SUITE_JSON=' + json.dumps(report))
        return 0 if collected and not loader.errors and result.wasSuccessful() else 1
    env = {k:v for k,v in os.environ.items() if k not in (*FLAGS, 'DISPUTE_REPLAY_TESTS')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    if args.integrations:
        env.update({key:'1' for key in FLAGS})
    reports, successful = [], True
    for root in ('tests', 'agent/tests'):
        child = subprocess.run([sys.executable, '-m', 'demo.verify', '--root', root],
            cwd=ROOT, env=env, text=True, capture_output=True)
        sys.stderr.write(child.stderr)
        rows = [line.removeprefix('SUITE_JSON=') for line in child.stdout.splitlines() if line.startswith('SUITE_JSON=')]
        successful = successful and child.returncode == 0 and len(rows) == 1
        reports.append(json.loads(rows[0]) if len(rows) == 1 else dict(root=root, error='suite_report_unavailable'))
    print(json.dumps(dict(status='passed' if successful else 'failed', python=platform.python_version(),
        mode='isolated_integrations' if args.integrations else 'offline',
        live_zetaris='NOT RUN', live_nightshift='NOT RUN', suites=reports), indent=2))
    return 0 if successful else 1


if __name__ == '__main__':
    raise SystemExit(main())
