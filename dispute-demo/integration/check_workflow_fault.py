"""Explicit live fault demo; never imported by the normal runtime.

Overstates the first real model credit by one minor unit. The trace is labelled
fault_injection. The same critic/writer must correct or refuse it. May persist
a policy-permitted corrected sandbox decision; a credited case must refuse an
extra credit. No source rows, policies, identities or references are altered.
"""
import argparse
from dataclasses import replace
import json
from pathlib import Path

from app.investigator import Investigator
from app.reviewer import Reviewer
from app.journal import FileJournal
from app.nightshift import NightshiftClient, NightshiftConfig
from app.orchestrator import Controller
from app.runtime_io import commit, read_snapshot
from app.schemas import Outcome
from integration.get_dispute_context import validate_dispute_id


class OverstatedCredit:
    def __init__(self, investigator):
        self.investigator, self.injected = investigator, False

    def step(self, *args, **kwargs):
        result = self.investigator.step(*args, **kwargs)
        if (not self.injected and result.proposal is not None and
                result.proposal.recommendation.outcome is Outcome.PROVISIONAL_CREDIT):
            self.injected = True
            result = replace(result, message='EXPLICIT FAULT INJECTION: model credit overstated by one minor unit.',
                proposal=replace(result.proposal, recommendation=replace(result.proposal.recommendation,
                    amount_minor=result.proposal.recommendation.amount_minor + 1)))
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id')
    parser.add_argument('--inject-credit-overstatement', action='store_true', required=True)
    args = parser.parse_args()
    validate_dispute_id(args.dispute_id)
    model = OverstatedCredit(Investigator(NightshiftClient(NightshiftConfig.from_environment())))
    controller = Controller(investigator=model, reviewer=Reviewer(NightshiftClient(NightshiftConfig.from_environment())), read_snapshot=read_snapshot, commit=commit,
        journal=FileJournal(Path(__file__).resolve().parents[1] / 'outputs/runs'), mode='fault_injection')
    result = controller.run(args.dispute_id)
    print(json.dumps(result.to_dict(), indent=2))
    # Fault acceptance is read from the explicit trace, not from an exit zero.
    return 0 if result.persisted else 1


if __name__ == '__main__':
    raise SystemExit(main())
