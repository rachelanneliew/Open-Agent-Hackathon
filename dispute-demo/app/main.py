"""Run a synthetic case: python -m app.main DP-0014 --no-memory.

Use --retry-request outputs/runs/<run>.request.json for identical recovery.
Ordinary reprocessing obtains new facts and may reject an existing credit;
only exact saved-request recovery can return the original result as REUSED.
"""
import argparse
import json
from pathlib import Path

from integration.get_dispute_context import validate_dispute_id
from .investigator import Investigator
from .journal import FileJournal, load_request
from .nightshift import ModelError, NightshiftClient, NightshiftConfig
from .orchestrator import Budgets, Controller
from .runtime_io import commit, read_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id', nargs='?')
    parser.add_argument('--retry-request', type=Path)
    parser.add_argument('--no-memory', action='store_true', help='Explicit no-memory milestone (default)')
    parser.add_argument('--model-calls', type=int, default=4)
    parser.add_argument('--tool-calls', type=int, default=3)
    parser.add_argument('--total-seconds', type=float, default=300)
    parser.add_argument('--model-seconds', type=float, default=120)
    parser.add_argument('--read-seconds', type=float, default=45)
    parser.add_argument('--commit-seconds', type=float, default=25)
    args = parser.parse_args()
    if bool(args.dispute_id) == bool(args.retry_request):
        parser.error('Provide one dispute ID or --retry-request')
    try:
        budgets = Budgets(**{key: getattr(args, key) for key in (
            'model_calls', 'tool_calls', 'total_seconds', 'model_seconds', 'read_seconds', 'commit_seconds')})
        if args.dispute_id:
            validate_dispute_id(args.dispute_id)
        investigator = None if args.retry_request else Investigator(NightshiftClient(NightshiftConfig.from_environment()))
        controller = Controller(investigator=investigator, read_snapshot=read_snapshot, commit=commit,
            journal=FileJournal(Path(__file__).resolve().parents[1] / 'outputs/runs'), budgets=budgets)
        result = controller.retry(load_request(args.retry_request), str(args.retry_request.resolve())) if args.retry_request else controller.run(args.dispute_id)
    except (ValueError, ModelError, OSError):
        print(json.dumps({'persisted': False, 'memory_mode': 'no_memory', 'error': 'invalid_input_or_configuration'}))
        return 2
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.persisted else 1


if __name__ == '__main__':
    raise SystemExit(main())
