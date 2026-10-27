"""Compatibility import for the pure critic; the SQLite writer is retired.

Existing local ledger files are neither opened, migrated nor deleted. The old
resolver receives an explicit unavailable result until T05/T08 provide the
canonical PostgreSQL action boundary. Validation is available via review_proposal.
"""
from app.critic import policy_rationale, review_proposal

# Retain the old resolver's optional argument without resolving any state path.
DEFAULT_LEDGER = None


def review_and_simulate(context, proposal, *, ledger_path=None):
    """Fail closed for legacy callers. Never validate or record an action."""
    return {
        'status': 'unavailable',
        'reason_code': 'LEGACY_ACTION_PATH_RETIRED',
        'explanation': 'Use app.critic.review_proposal for pure validation; '
                       'PostgreSQL action integration is pending T05/T08.',
        'simulated_credit_created': False,
    }
