"""Pure T06 proposal validation. Acceptance is never a persisted decision.

Inputs come from the trusted controller, not model-selected contexts/policies.
Only the existing bounded synthetic policy/evidence semantics are supported.
See docs/critic.md for citation, rationale and correction requirements.
"""
from .policy_engine import evaluate_policy
from .schemas import (AgentProposal, CriticResult, CriticVerdict, DisputeContext,
                      Outcome, PolicyResult, require)


def policy_rationale(policy: PolicyResult) -> str:
    """Render the supported explanation vocabulary; this grants no approval.

    Free-form prose has no machine-checkable claim structure in T01. Require the
    exact deterministic explanation (ignoring surrounding whitespace) instead
    of pretending to understand arbitrary assertions or trusting citation IDs.
    """
    require(type(policy) is PolicyResult, 'Expected PolicyResult')
    explanations = [f'{check.policy_rule_id}: {check.explanation}'
                    for check in policy.rule_checks if check.status != 'not_evaluated']
    if not explanations:
        return 'Required authoritative inputs or supported policy semantics are unavailable; human review is required.'
    return '\n'.join(explanations)


def review_proposal(context: DisputeContext, policy: PolicyResult,
                    proposal: AgentProposal) -> CriticResult:
    """Validate without I/O, clock reads, state mutation or action dispatch.

    Malformed transport inputs raise ContractError; no valid identity can be
    invented for them. A typed proposal always receives a result bound to its
    own proposal ID/reference, including on mismatch. Revision 0 can receive one
    correction; invalid revision 1, stale inputs and unsupported semantics route
    to review. The controller must enforce run identity/budgets across calls.
    """
    for value, contract in ((context, DisputeContext), (policy, PolicyResult),
                            (proposal, AgentProposal)):
        require(type(value) is contract, f'Expected {contract.__name__}')
        # Recheck nested transport/scope/time invariants at this trust boundary.
        contract.from_dict(value.to_dict())

    failures, corrections = [], []
    terminal = False

    def fail(code, correction, *, review=False):
        nonlocal terminal
        failures.append(code)
        corrections.append(correction)
        terminal = terminal or review

    def result():
        if not failures:
            return CriticResult(proposal_id=proposal.proposal_id, reference=proposal.reference,
                verdict=CriticVerdict.ACCEPTED,
                feedback='Proposal matches the supplied context and deterministic policy. '
                         'No action was executed; commit-time freshness and persistence remain required.')
        verdict = (CriticVerdict.HUMAN_REVIEW if terminal or proposal.revision == 1
                   else CriticVerdict.REVISE)
        suffix = (' One correction is permitted with revision 1 and a new proposal ID.'
                  if verdict is CriticVerdict.REVISE else
                  ' Do not commit this proposal. This verdict does not create a review-queue entry.')
        return CriticResult(proposal_id=proposal.proposal_id, reference=proposal.reference,
            verdict=verdict, failed_checks=tuple(failures), feedback=' '.join(corrections) + suffix)

    if policy.reference != context.reference:
        fail('policy_reference_mismatch', 'Retrieve and reevaluate one consistent context.', review=True)
    if proposal.reference != context.reference:
        fail('proposal_reference_mismatch', 'Create a new proposal from the current evaluated context.', review=True)
    if failures:
        return result()

    # Reuse the canonical evaluator, never a second copy of its business rules.
    # A well-formed PolicyResult is not proof that trusted evaluation occurred.
    expected = evaluate_policy(context)
    if policy != expected:
        fail('policy_result_mismatch', 'Reevaluate policy from the supplied source context; '
             'do not reuse or edit a prior policy result.', review=True)
        return result()

    recommendation = proposal.recommendation
    if recommendation.outcome not in expected.allowed_outcomes:
        fail('outcome_not_allowed', 'Use the policy-permitted outcome: ' +
             ', '.join(o.value for o in expected.allowed_outcomes) + '.',
             review=expected.allowed_outcomes == (Outcome.HUMAN_REVIEW,))
    if recommendation.currency != expected.currency:
        fail('currency_mismatch', 'Use the evaluated case currency: ' + expected.currency + '.')
    if recommendation.outcome is Outcome.PROVISIONAL_CREDIT:
        # APPROVE specifies min(claimed, balance), not a discretionary smaller
        # award. Both underpayment and overpayment contradict the written rule.
        if recommendation.amount_minor != expected.credit_limit_minor:
            correction = ('Credit is unavailable for this policy result.' if expected.credit_limit_minor is None
                          else f'Use exactly {expected.credit_limit_minor} {expected.currency} minor units.')
            fail('amount_mismatch', correction)

    evaluated = {check.policy_rule_id: check for check in expected.rule_checks
                 if check.status != 'not_evaluated'}
    cited_rules = set(proposal.policy_rule_ids)
    if cited_rules - evaluated.keys():
        fail('unverified_rule', 'Cite only rules actually evaluated for this context.')
    # Earlier gates establish precedence; citing APPROVE alone omits those gates.
    if evaluated.keys() - cited_rules:
        fail('missing_rule_citations', 'Include every evaluated rule ID: ' + ', '.join(evaluated) + '.')

    evidence = {item.evidence_id: item for item in context.evidence}
    cited_evidence = set(proposal.evidence_ids)
    if cited_evidence - evidence.keys():
        fail('evidence_outside_context', 'Remove evidence absent from this case at its evaluation cutoff.')
    # The real policy checks corroborate whole source templates and metadata.
    # Existing but unusable text is not supporting evidence. Review proposals may
    # cite such visible documents as material needing examination, never credit.
    supported = {eid for check in evaluated.values() for eid in check.evidence_ids}
    unsupported = (cited_evidence & evidence.keys()) - supported
    if unsupported and recommendation.outcome is not Outcome.HUMAN_REVIEW:
        fail('unsupported_evidence', 'Cited documents do not establish the proposed conclusion; '
             'obtain authoritative support or route unresolved material to review.', review=True)
    if supported - cited_evidence:
        fail('missing_evidence_citations', 'Include the evidence used by the evaluated policy: ' +
             ', '.join(sorted(supported)) + '.')

    expected_missing = set(expected.missing_evidence)
    if (set(proposal.missing_evidence) != expected_missing or
            len(proposal.missing_evidence) != len(expected_missing)):
        requirements = ', '.join(f'{item.category} ({item.reason}, {item.policy_rule_id})'
                                 for item in expected.missing_evidence) or 'none'
        fail('missing_requirements_mismatch', 'Use exactly these missing requirements: ' + requirements + '.')

    if proposal.rationale.strip() != policy_rationale(expected):
        fail('unsupported_rationale', 'Use policy_rationale(policy) for the supported explanation. '
             'Arbitrary prose, memory claims and contradictory conclusions cannot be verified.', review=True)
    return result()
