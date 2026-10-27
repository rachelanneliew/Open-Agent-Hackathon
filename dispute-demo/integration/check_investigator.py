"""Read-only live T07 check: Zetaris -> policy -> Nightshift -> pure critic.

Run from dispute-demo: python -m integration.check_investigator DP-0014
Run the documented JDBC preflight first. No model tool dispatch or action writes.
This probe is not the T08 controller and never claims workflow persistence.
"""
import argparse
import json
from uuid import uuid4

from app.critic import review_proposal
from app.investigator import Investigator
from app.nightshift import ModelError, NightshiftClient, NightshiftConfig
from app.policy_engine import evaluate_policy
from app.schemas import DisputeContext
from app.tools import ReadTools


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id')
    parser.add_argument('--timeout', type=float, default=180)
    args = parser.parse_args()
    try:
        client = NightshiftClient(NightshiftConfig.from_environment())
        client.discover()
        read = ReadTools().get_dispute_context(args.dispute_id)
        if not isinstance(read.data, DisputeContext):
            print(json.dumps({'mode': 'live_read_only', 'read_status': read.status.value,
                              'message': read.message, 'persisted': False}))
            return 1
        policy = evaluate_policy(read.data)
        result = Investigator(client).step(read.data, policy, run_id=str(uuid4()),
                                          proposal_id=str(uuid4()), timeout_seconds=args.timeout)
        critic = review_proposal(read.data, policy, result.proposal) if result.proposal else None
        usable = critic is not None and critic.verdict.value == 'accepted' and not result.uncertainties
        print(json.dumps({'mode': 'live_read_only', 'source_channel': read.data.source_channel,
            'read_status': read.status.value, 'investigator': result.to_dict(),
            'critic': critic.to_dict() if critic else None, 'usable_proposal': usable,
            'persisted': False}, indent=2))
        return 0 if usable else 1
    except ModelError as exc:
        print(json.dumps({'mode': 'live_read_only', 'error': exc.code, 'persisted': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
