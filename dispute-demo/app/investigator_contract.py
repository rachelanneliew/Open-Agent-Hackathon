"""Model-owned draft and request schema; application metadata never needs echoing.

This is a transport contract, not a policy evaluator. The assembled proposal
still passes the canonical AgentProposal, critic and commit-time checks.
"""
from dataclasses import dataclass

from .schemas import Contract, EvidenceRequirement, Outcome, Recommendation, require


@dataclass(frozen=True, kw_only=True)
class ProposalDraft(Contract):
    recommendation: Recommendation
    evidence_ids: tuple[str, ...]
    policy_rule_ids: tuple[str, ...]
    missing_evidence: tuple[EvidenceRequirement, ...]

    @classmethod
    def from_dict(cls, payload):
        # Recommendation's canonical default remains compatible with saved
        # records; the model wire contract requires an explicit null instead.
        if type(payload) is dict and type(payload.get('recommendation')) is dict:
            require('amount_minor' in payload['recommendation'], 'Explicit amount field required',
                    path=('recommendation', 'amount_minor'), code='missing_field')
        return super().from_dict(payload)


def _object(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def response_schema(tool_names, policy):
    """Bind citation vocabulary to canonical checks, never model-selected facts.

    The schema does not choose the outcome or amount. The local critic remains
    authoritative for those values, source support and complete citations.
    """
    currency = dict(type='string', pattern='^[A-Z]{3}$')
    credit = _object(dict(outcome=dict(type='string', enum=[Outcome.PROVISIONAL_CREDIT.value]),
        currency=currency, amount_minor=dict(type='integer', minimum=1, maximum=2**63 - 1)))
    noncredit = _object(dict(outcome=dict(type='string', enum=[o.value for o in Outcome
        if o is not Outcome.PROVISIONAL_CREDIT]), currency=currency, amount_minor=dict(type='null')))
    rule = dict(type='string', pattern='^v[1-9][0-9]*-[A-Z][A-Z0-9_]*$')
    requirement = _object(dict(category=dict(type='string', enum=[
        'receipt', 'delivery_record', 'refund_confirmation', 'two_completed_captures_same_order']),
        reason=dict(type='string', enum=['absent', 'unusable', 'not_yet_available']), policy_rule_id=rule))
    evaluated = [check for check in policy.rule_checks if check.status != 'not_evaluated']
    evidence = sorted({eid for check in evaluated for eid in check.evidence_ids})
    rules = [check.policy_rule_id for check in evaluated]
    def citations(ids):
        # Empty enum is invalid on some providers; maxItems=0 is unambiguous.
        item = dict(type='string', enum=ids) if ids else dict(type='string')
        # Uniqueness is checked locally by AgentProposal. The live route accepted
        # array bounds; its uniqueItems capability probe did not succeed.
        return dict(type='array', items=item, minItems=len(ids), maxItems=len(ids))
    draft = _object(dict(recommendation=dict(anyOf=[credit, noncredit]),
        evidence_ids=citations(evidence), policy_rule_ids=citations(rules),
        missing_evidence=dict(type='array', items=requirement)))
    read = _object(dict(name=dict(type='string', enum=list(tool_names)),
        dispute_id=dict(type='string', enum=[policy.reference.dispute_id])))
    # Both payload slots are required; the inactive slot must be null locally.
    # Nullable nested objects avoid a union at the schema root.
    return _object(dict(kind=dict(type='string', enum=['proposal', 'read']),
        proposal=dict(anyOf=[draft, dict(type='null')]),
        request=dict(anyOf=[read, dict(type='null')]),
        uncertainties=dict(type='array', maxItems=8,
            items=dict(type='string', minLength=1, maxLength=240))))
