"""Advisory recall verified through the existing authoritative snapshot reader.

Memory never grants a read scope, a policy exception, or an action retry.
Only source customer-history membership authorizes reading a prior case.
"""
from dataclasses import asdict
from pathlib import Path
import time

from agent.memory_service import CommittedSummary, source_reference
from .fresh_tools import FreshSnapshot
from .history import HistoricalDecision, VerifiedHistory
from .runtime_io import BoundaryError
from .schemas import ExecutionStatus, require


def source_summary(snapshot, receipt):
    """Build from source ownership/reason plus an authoritative committed receipt."""
    c = snapshot.context
    anchor = next(t for t in c.transactions if t.transaction_id == c.dispute.transaction_id)
    require(receipt in snapshot.decisions.decisions and receipt.status in (
        ExecutionStatus.COMMITTED, ExecutionStatus.REUSED), 'Source receipt required')
    return CommittedSummary(customer_id=anchor.customer_id, decision_id=receipt.decision_id,
        run_id=receipt.run_id, proposal_id=receipt.proposal_id, reference=receipt.reference,
        recommendation=receipt.recommendation, committed_at=receipt.committed_at,
        simulated_credit_id=receipt.simulated_credit_id, reason_code=c.dispute.reason_code,
        source_reference=source_reference(receipt.decision_id))


def recall_verified(snapshot, memory, read_prior, event):
    """read_prior consumes the same controller read/time budget as current reads."""
    customer = snapshot.history.customer_id
    reference = snapshot.context.reference
    empty = VerifiedHistory(reference=reference, customer_id=customer)
    # Source IDs improve reference mock-embedding recall; they do not prove truth.
    scope = {x.dispute.dispute_id: x for x in snapshot.history.cases}
    query = 'committed_summary ' + customer + ' ' + snapshot.context.dispute.reason_code + ' ' + ' '.join(sorted(scope))
    try:
        # The reference hash embedder's relevance threshold misses structured
        # summaries. Rank up to five scoped candidates without a similarity gate;
        # authoritative verification, never similarity, decides what may be used.
        candidates = memory.recall(customer, query=query[:2048], top_n=5, threshold=0)
        require(type(candidates) is tuple and len(candidates) <= 5, 'Invalid recall bounds')
    except Exception:
        event('memory_recall', status='unavailable', advisory=True)
        return empty
    event('memory_recall', status='available', candidates=len(candidates), advisory=True,
          complete_history=False)
    verified, seen, cache = [], set(), {}
    for candidate in candidates:
        code, did = None, None
        if type(candidate) is not CommittedSummary:
            event('memory_ignored', code='unverified_note_or_invalid_record')
            continue
        try:
            candidate = CommittedSummary.from_dict(candidate.to_dict())
            did = candidate.reference.dispute_id
            if candidate.customer_id != customer:
                code = 'cross_customer'
            elif did not in scope:
                code = 'not_in_source_customer_history'
            elif candidate.committed_at > reference.evaluation_at:
                code = 'future_decision'
            else:
                if did not in cache:
                    cache[did] = read_prior(did)
                prior = cache[did]
                require(type(prior) is FreshSnapshot, 'Invalid prior snapshot')
                prior = FreshSnapshot.from_dict(prior.to_dict())
                if prior.context.reference.source_revision != reference.source_revision:
                    raise BoundaryError('source_revision_changed_during_memory_verification')
                require(prior.context.reference.dispute_id == did and
                    prior.context.reference.source_revision == reference.source_revision and
                    prior.context.source_channel == snapshot.context.source_channel and
                    prior.history.customer_id == customer, 'Source verification binding mismatch')
                # Fresh source may use a later evaluation timestamp; compare the
                # stable owner/reason/primary identity with the authorized anchor.
                member = scope[did]
                require(prior.context.dispute.transaction_id == member.dispute.transaction_id and
                    prior.context.dispute.reason_code == member.dispute.reason_code, 'Source identity changed')
                receipts = prior.decisions.decisions
                exact = next((r for r in receipts if r.decision_id == candidate.decision_id), None)
                visible = [r for r in receipts if r.committed_at <= reference.evaluation_at]
                newest = max((r.committed_at for r in visible), default=None)
                latest = [r for r in visible if r.committed_at == newest]
                if exact is None:
                    code = 'missing_source_decision'
                elif len(latest) != 1 or exact != latest[0]:
                    code = 'stale_or_ambiguous_decision'
                elif source_summary(prior, exact) != candidate:
                    code = 'source_summary_mismatch'
                elif did in seen:
                    code = 'duplicate_case'
                else:
                    verified.append(HistoricalDecision(decision_id=exact.decision_id,
                        original_reference=exact.reference, recommendation=exact.recommendation,
                        committed_at=exact.committed_at, reason_code=candidate.reason_code,
                        source_reference=candidate.source_reference, verified_reference=prior.context.reference))
                    seen.add(did)
        except BoundaryError as exc:
            if exc.code == 'source_revision_changed_during_memory_verification':
                raise
            code = 'source_verification_budget_or_read_unavailable'
        except Exception:
            code = 'source_verification_unavailable'
        if code:
            # Do not echo rejected text, customer IDs or decision payloads.
            event('memory_ignored', code=code)
    result = VerifiedHistory(reference=reference, customer_id=customer, records=tuple(verified))
    event('memory_verified', history=result.to_dict(), distinct_cases=len(verified),
          complete_history=False, binding_rule=None)
    return result


def save_confirmed(context, receipt, memory_factory, timeout, event):
    """After commit only; failures cannot change the confirmed action result."""
    if receipt.status not in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED):
        return
    event('memory_save', status='pending', decision_id=receipt.decision_id)
    try:
        item = CommittedSummary.from_commit(context, receipt)
        saved = memory_factory(timeout()).save(item)
        require(saved.status in ('stored', 'reused', 'failed'), 'Invalid save status')
        event('memory_save', **asdict(saved), decision_id=receipt.decision_id,
              committed_result_preserved=True)
    except Exception:
        event('memory_save', status='failed', error='memory_save_unavailable',
              decision_id=receipt.decision_id, committed_result_preserved=True)


def retry_memory(trace_path, *, read_snapshot, memory_factory, budgets):
    """Reverify a saved receipt, then retry memory only; no action callback exists."""
    from agent.hmem_client import strict_json
    from .journal import load_request
    from .schemas import RunState
    start = time.monotonic()
    with Path(trace_path).open('rb') as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    require(len(raw) <= 2 * 1024 * 1024, 'Trace exceeds limit')
    trace = strict_json(raw)
    state = RunState.from_dict(trace['state'])
    receipt = state.commit_result
    require(receipt is not None and receipt.status in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED),
            'Confirmed receipt required for memory-only retry')
    request = load_request(Path(trace_path).with_name(state.run_id + '.request.json'))
    require(receipt.run_id == request.run_id and receipt.proposal_id == request.proposal.proposal_id and
        receipt.idempotency_key == request.idempotency_key and receipt.recommendation == request.proposal.recommendation,
        'Saved receipt binding mismatch')
    expected = CommittedSummary.from_commit(request.context, receipt)
    snapshot = read_snapshot(expected.reference.dispute_id,
        timeout_seconds=min(budgets.read_seconds, budgets.total_seconds))
    require(type(snapshot) is FreshSnapshot, 'Fresh verification required')
    snapshot = FreshSnapshot.from_dict(snapshot.to_dict())
    found = next((r for r in snapshot.decisions.decisions if r.decision_id == expected.decision_id), None)
    require(found is not None and source_summary(snapshot, found) == expected, 'Source receipt mismatch')
    def timeout():
        remaining = min(15, budgets.total_seconds - (time.monotonic() - start))
        require(remaining > 0, 'Memory retry time exhausted')
        return remaining
    events = []
    save_confirmed(request.context, receipt, memory_factory, timeout,
                   lambda kind, **values: events.append(dict(kind=kind, **values)))
    return dict(mode='memory_retry', source_channel=snapshot.context.source_channel,
        source_freshly_verified=True, action_called=False, persisted=True,
        decision_id=receipt.decision_id, memory_save=events[-1])
