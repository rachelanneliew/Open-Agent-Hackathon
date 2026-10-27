"""Strict model feedback and application-owned review binding; no I/O or authority."""
from dataclasses import dataclass

from .schemas import Contract, ContextRef, require, uuid_id, unique, source_id, rule_id
from .nightshift import label

ISSUE_CODES = ('conflicting_evidence', 'unsupported_claim', 'material_omission',
               'requires_authoritative_read', 'unresolved_risk')


@dataclass(frozen=True, kw_only=True)
class ReviewerFeedback(Contract):
    verdict: str
    issue_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    policy_rule_ids: tuple[str, ...]
    feedback: str
    uncertainties: tuple[str, ...]

    def _check(self):
        require(self.verdict in ('accept', 'revise', 'escalate'), 'Invalid review verdict')
        unique(self.issue_codes)
        require(set(self.issue_codes) <= set(ISSUE_CODES), 'Invalid review issue')
        require(1 <= len(self.feedback) <= 500, 'Feedback exceeds bound')
        require(len(self.evidence_ids) <= 1000 and len(self.policy_rule_ids) <= 1000,
                'Citation bound exceeded')
        require(len(self.uncertainties) <= 8 and all(1 <= len(x) <= 240 for x in self.uncertainties),
                'Uncertainty bound exceeded')
        require(self.verdict != 'accept' or (not self.issue_codes and not self.uncertainties),
                'Acceptance cannot contain unresolved issues')
        require(self.verdict == 'accept' or bool(self.issue_codes), 'Objection needs an issue code')
        unique(self.evidence_ids)
        unique(self.policy_rule_ids)
        for value in self.evidence_ids:
            source_id(value, 'EV')
        for value in self.policy_rule_ids:
            rule_id(value)


@dataclass(frozen=True, kw_only=True)
class ReviewerResult(Contract):
    status: str
    run_id: str
    proposal_id: str
    reference: ContextRef
    attempt: int
    requested_route: str
    feedback: ReviewerFeedback | None = None
    response_model: str | None = None
    error: str | None = None

    def _check(self):
        uuid_id(self.run_id)
        uuid_id(self.proposal_id)
        require(self.attempt in (0, 1), 'Invalid review attempt')
        require(self.status in ('reviewed', 'invalid_output', 'unavailable', 'timeout', 'unauthorized'),
                'Invalid reviewer status')
        require((self.status == 'reviewed') == (self.feedback is not None), 'Invalid review payload')
        require(label(self.requested_route) is not None and
                (self.response_model is None or label(self.response_model) is not None), 'Invalid model metadata')
        require(self.error is None or self.error in ('invalid_output', 'provider_failure',
                'response_contract_rejected'), 'Invalid diagnostic')


def validate_review(result, context, policy, proposal, *, attempt=None):
    """Recheck identity and source vocabulary at controller/correction boundaries."""
    require(type(result) is ReviewerResult, 'Typed review required')
    ReviewerResult.from_dict(result.to_dict())
    require(result.run_id == proposal.run_id and result.proposal_id == proposal.proposal_id and
            result.reference == proposal.reference == context.reference == policy.reference,
            'Review binding mismatch')
    require(attempt is None or result.attempt == attempt, 'Review attempt mismatch')
    if result.feedback is not None:
        f = result.feedback
        require(set(f.evidence_ids) <= {e.evidence_id for e in context.evidence}, 'Unknown evidence')
        require(set(f.policy_rule_ids) <= {r.policy_rule_id for r in policy.rule_checks
                if r.status != 'not_evaluated'}, 'Unknown or unevaluated rule')
    return result


def response_schema(context, policy):
    def array(ids):
        return dict(type='array', maxItems=len(ids), items=dict(type='string', enum=list(ids))
                    if ids else dict(type='string'))
    properties = dict(verdict=dict(type='string', enum=['accept', 'revise', 'escalate']),
        issue_codes=array(ISSUE_CODES),
        evidence_ids=array([e.evidence_id for e in context.evidence]),
        policy_rule_ids=array([r.policy_rule_id for r in policy.rule_checks if r.status != 'not_evaluated']),
        feedback=dict(type='string', minLength=1, maxLength=500),
        uncertainties=dict(type='array', maxItems=8, items=dict(type='string', minLength=1, maxLength=240)))
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)
