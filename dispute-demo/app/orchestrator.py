"""Canonical bounded workflow. Only the controller may reach the writer."""
from dataclasses import dataclass, replace
import math
import time
from uuid import uuid4

from integration.get_dispute_context import validate_dispute_id
from .action_service import CommitRequest
from .critic import review_proposal
from .fresh_tools import FreshReadTools, FreshSnapshot
from .investigator import InvestigatorResult, ReadObservation
from .policy_engine import evaluate_policy
from .reviewer_contract import validate_review
from .runtime_io import BoundaryError
from .schemas import (CommitResult, CriticVerdict, ExecutionStatus, RunPhase, RunState, require)
from .tools import ReadStatus, ReadToolRegistry


@dataclass(frozen=True)
class Budgets:
    model_calls: int = 6
    tool_calls: int = 3  # includes initial required snapshot and every attempted read
    total_seconds: float = 300
    model_seconds: float = 120
    read_seconds: float = 45
    commit_seconds: float = 25

    def __post_init__(self):
        require(type(self.model_calls) is int and 1 <= self.model_calls <= 8, 'Invalid model budget')
        require(type(self.tool_calls) is int and 1 <= self.tool_calls <= 8, 'Invalid tool budget')
        for name, maximum in (('total_seconds', 600), ('model_seconds', 180),
                              ('read_seconds', 90), ('commit_seconds', 60)):
            value = getattr(self, name)
            require(type(value) in (int, float) and math.isfinite(value) and 0 < value <= maximum,
                    'Invalid duration budget')


@dataclass(frozen=True)
class WorkflowResult:
    state: RunState
    events: tuple
    mode: str
    recovery_request: str | None = None
    memory_mode: str = 'no_memory'

    @property
    def persisted(self):
        return self.state.commit_result is not None and self.state.commit_result.status in (
            ExecutionStatus.COMMITTED, ExecutionStatus.REUSED)

    def to_dict(self):
        return dict(state=self.state.to_dict(), events=list(self.events), mode=self.mode,
                    memory_mode=self.memory_mode, persisted=self.persisted, recovery_request=self.recovery_request)


class Controller:
    """Injected dependencies are trusted application configuration, never model tools.

    Production read/write callbacks enforce deadlines in short-lived processes;
    investigator uses the independently bounded Nightshift transport. Tests must
    label their mode and explicitly supply mocks; no runtime fallback is present.
    """
    def __init__(self, *, investigator, read_snapshot, commit, journal,
                 budgets=None, mode='live', clock=time.monotonic, post_commit=None,
                 memory_factory=None, reviewer=None):
        require(mode in ('live', 'offline_test', 'fault_injection'), 'Invalid execution mode')
        self.investigator, self.read_snapshot, self.commit = investigator, read_snapshot, commit
        self.journal, self.budgets, self.mode = journal, budgets or Budgets(), mode
        self.clock, self.post_commit = clock, post_commit
        self.memory_factory = memory_factory
        self.reviewer = reviewer

    def run(self, dispute_id):
        validate_dispute_id(dispute_id)
        b, start = self.budgets, self.clock()
        state = RunState(run_id=str(uuid4()), phase=RunPhase.CREATED)
        events, recovery = [], None
        def event(kind, **values):
            events.append(dict(kind=kind, **values))
        def remaining(cap):
            value = min(cap, b.total_seconds - (self.clock() - start))
            if value <= 0:
                raise BoundaryError('total_duration_exhausted')
            return value
        def finish(error=None):
            nonlocal state
            if error is not None:
                state = replace(state, phase=RunPhase.FAILED, error=error)
                event('failed', code=error, persisted=False)
            result = WorkflowResult(state, tuple(events), self.mode, recovery,
                'verified_advisory' if self.memory_factory else 'no_memory')
            try:
                self.journal.finish(result)
            except Exception:
                event('trace_save_failed', committed_result_preserved=result.persisted)
                result = replace(result, events=tuple(events))
            return result
        def read(target=dispute_id):
            nonlocal state
            if state.tool_calls >= b.tool_calls:
                raise BoundaryError('tool_budget_exhausted')
            timeout = remaining(b.read_seconds)
            state = replace(state, tool_calls=state.tool_calls + 1)
            value = self.read_snapshot(target, timeout_seconds=timeout)
            require(type(value) is FreshSnapshot, 'Invalid read response')
            value = FreshSnapshot.from_dict(value.to_dict())
            require(value.context.reference.dispute_id == target, 'Snapshot outside case')
            if self.mode == 'live':
                require(value.context.source_channel == 'zetaris', 'Live source required')
            remaining(b.total_seconds)
            return value
        try:
            if self.reviewer is None:
                return finish('reviewer_required_no_action')
            snapshot = read()
            observations, previous, critique = (), None, None
            reviewer_feedback, review_attempt = None, 0
            history = None
            while True:
                context = snapshot.context
                state = replace(state, phase=RunPhase.RETRIEVED, reference=context.reference)
                event('facts', reference=context.reference.to_dict(),
                    transactions=[t.to_dict() for t in context.transactions],
                    settlements=[s.to_dict() for s in context.settlements],
                    evidence_ids=[e.evidence_id for e in context.evidence], issues=list(context.data_issues),
                    prior_decisions=[d.to_dict() for d in snapshot.decisions.decisions])
                if self.memory_factory and (history is None or history.reference != context.reference):
                    from .memory_workflow import recall_verified
                    from .history import VerifiedHistory
                    try:
                        memory = self.memory_factory(remaining(15))
                        history = recall_verified(snapshot, memory, read, event)
                    except BoundaryError:
                        raise
                    except Exception:
                        history = VerifiedHistory(reference=context.reference,
                                                  customer_id=snapshot.history.customer_id)
                        event('memory_recall', status='unavailable', advisory=True)
                policy = evaluate_policy(context, advisory_history=history)
                state = replace(state, phase=RunPhase.EVALUATED)
                event('policy', result=policy.to_dict())
                if state.model_calls >= b.model_calls:
                    return finish('model_budget_exhausted')
                timeout = remaining(b.model_seconds)
                state = replace(state, model_calls=state.model_calls + 1)
                proposal_id = str(uuid4())
                response = self.investigator.step(context, policy, run_id=state.run_id,
                    proposal_id=proposal_id, revision=state.proposal_revision, previous=previous,
                    critique=critique, observations=observations, timeout_seconds=timeout,
                    advisory_history=history, reviewer_feedback=reviewer_feedback)
                require(type(response) is InvestigatorResult, 'Invalid investigator result')
                response = InvestigatorResult.from_dict(response.to_dict())
                event('investigator', result=response.to_dict(), run_id=state.run_id,
                    proposal_id=proposal_id, reference=context.reference.to_dict(),
                    revision=state.proposal_revision, model_call=state.model_calls)
                remaining(b.total_seconds)
                if response.status not in ('read', 'proposal'):
                    return finish('investigator_' + response.status)
                if response.uncertainties:
                    return finish('unresolved_model_uncertainty')
                if response.status == 'read':
                    request = response.read_request
                    if request.dispute_id != dispute_id:
                        return finish('read_scope_rejected')
                    # A new source timestamp/reference invalidates the earlier
                    # correction binding. Never reset the one-correction budget.
                    if state.proposal_revision:
                        return finish('new_read_during_correction_requires_new_run')
                    snapshot = read()
                    registry = ReadToolRegistry(dispute_id, tools=FreshReadTools(snapshot))
                    result = registry.dispatch(request.name, request.arguments())
                    if result.status not in (ReadStatus.OK, ReadStatus.INCOMPLETE) or result.data is None:
                        return finish('required_read_unavailable')
                    observations = (ReadObservation(request=request, result=result),)
                    event('read', name=request.name, reference=snapshot.context.reference.to_dict(),
                          previous_facts_invalidated=True)
                    continue  # policy recomputed before next proposal
                proposal = response.proposal
                require(proposal.proposal_id == proposal_id and proposal.run_id == state.run_id and proposal.reference == context.reference and
                        proposal.revision == state.proposal_revision, 'Proposal binding mismatch')
                state = replace(state, phase=RunPhase.PROPOSED)
                critique = review_proposal(context, policy, proposal)
                event('critic', result=critique.to_dict(), run_id=state.run_id,
                    proposal_id=proposal.proposal_id, revision=proposal.revision)
                if critique.verdict is CriticVerdict.REVISE and state.proposal_revision == 0:
                    state = replace(state, proposal_revision=1)
                    previous = proposal
                    reviewer_feedback = None
                    event('correction', source='python_critic', proposal_id=proposal.proposal_id, revision=1)
                    continue
                if critique.verdict is not CriticVerdict.ACCEPTED:
                    # Honest no-credit failure; never recast a rejected credit
                    # as a persisted human-review decision.
                    return finish('critic_unresolved_no_action')
                if state.model_calls >= b.model_calls:
                    return finish('model_budget_exhausted')
                timeout = remaining(b.model_seconds)
                state = replace(state, model_calls=state.model_calls + 1)
                try:
                    reviewed = self.reviewer.review(context, policy, proposal, critique,
                        attempt=review_attempt, timeout_seconds=timeout, advisory_history=history)
                    validate_review(reviewed, context, policy, proposal, attempt=review_attempt)
                except Exception:
                    event('reviewer', status='invalid_or_unavailable', run_id=state.run_id,
                        proposal_id=proposal.proposal_id, reference=context.reference.to_dict(),
                        attempt=review_attempt, model_call=state.model_calls)
                    return finish('reviewer_invalid_or_unavailable_no_action')
                event('reviewer', result=reviewed.to_dict(), model_call=state.model_calls)
                remaining(b.total_seconds)
                if reviewed.status != 'reviewed':
                    return finish('reviewer_' + reviewed.status)
                if reviewed.feedback.verdict == 'revise' and state.proposal_revision == 0:
                    previous, reviewer_feedback = proposal, reviewed
                    review_attempt += 1
                    state = replace(state, proposal_revision=1)
                    event('correction', source='independent_reviewer', proposal_id=proposal.proposal_id, revision=1)
                    continue
                if reviewed.feedback.verdict != 'accept':
                    return finish('reviewer_unresolved_no_action')
                # Recompute the pure gate on the exact final reviewed proposal.
                final_critic = review_proposal(context, policy, proposal)
                if final_critic != critique or final_critic.verdict is not CriticVerdict.ACCEPTED:
                    return finish('final_critic_rejected_no_action')
                validate_review(reviewed, context, policy, proposal, attempt=review_attempt)
                event('final_gate', run_id=state.run_id, proposal_id=proposal.proposal_id,
                    reference=context.reference.to_dict(), critic='accepted', reviewer='accept')
                state = replace(state, phase=RunPhase.VALIDATED)
                request = CommitRequest(run_id=state.run_id, idempotency_key=str(uuid4()), context=context,
                    policy=policy, proposal=proposal, critic=critique)
                remaining(b.commit_seconds)
                recovery = self.journal.prepare(request)
                timeout = remaining(b.commit_seconds)
                try:
                    result = self.commit(request, timeout_seconds=timeout)
                    result = self._bound_result(request, result)
                except Exception:
                    result = self._unconfirmed(request)
                state = replace(state, phase=RunPhase.FINISHED, commit_result=result)
                event('commit', result=result.to_dict(), new_simulated_credit=(
                    result.status is ExecutionStatus.COMMITTED and result.simulated_credit_id is not None))
                if self.memory_factory:
                    from .memory_workflow import save_confirmed
                    save_confirmed(context, result, self.memory_factory, lambda: remaining(15), event)
                if result.status in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED) and self.post_commit:
                    try:
                        self.post_commit(result)
                    except Exception:
                        event('optional_post_commit_failed', committed_result_preserved=True)
                return finish()
        except BoundaryError as exc:
            return finish(exc.code)
        except Exception:
            return finish('workflow_unavailable_no_action')

    @staticmethod
    def _bound_result(request, result):
        require(type(result) is CommitResult, 'Invalid commit response')
        result = CommitResult.from_dict(result.to_dict())
        require(result.run_id == request.run_id and result.proposal_id == request.proposal.proposal_id and
                result.idempotency_key == request.idempotency_key and result.reference == request.context.reference,
                'Commit result binding mismatch')
        if result.status in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED):
            require(result.recommendation == request.proposal.recommendation, 'Commit outcome mismatch')
        return result

    @staticmethod
    def _unconfirmed(request):
        return CommitResult(run_id=request.run_id, proposal_id=request.proposal.proposal_id,
            idempotency_key=request.idempotency_key, reference=request.context.reference,
            status=ExecutionStatus.FAILED, message='commit_unconfirmed_retry_identical_request')

    def retry(self, request, recovery_path):
        """Recovery ONLY: exact saved request, no model/read/replacement identities."""
        started = self.clock()
        request = CommitRequest.from_dict(request.to_dict())
        try:
            result = self._bound_result(request, self.commit(request,
                timeout_seconds=min(self.budgets.commit_seconds, self.budgets.total_seconds)))
        except Exception:
            result = self._unconfirmed(request)
        state = RunState(run_id=request.run_id, phase=RunPhase.FINISHED,
                         reference=request.context.reference, commit_result=result)
        events = [dict(kind='recovery', result=result.to_dict())]
        if self.memory_factory:
            from .memory_workflow import save_confirmed
            def memory_timeout():
                left = min(15, self.budgets.total_seconds - (self.clock() - started))
                if left <= 0:
                    raise BoundaryError('total_duration_exhausted')
                return left
            save_confirmed(request.context, result, self.memory_factory, memory_timeout,
                           lambda kind, **values: events.append(dict(kind=kind, **values)))
        outcome = WorkflowResult(state, tuple(events), self.mode, recovery_path,
                                 'verified_advisory' if self.memory_factory else 'no_memory')
        try:
            self.journal.finish(outcome)
        except Exception:
            outcome = replace(outcome, events=outcome.events + ({'kind': 'trace_save_failed'},))
        return outcome
