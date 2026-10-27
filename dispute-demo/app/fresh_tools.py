"""A coherent, current Zetaris snapshot and its four bounded read projections."""
from dataclasses import dataclass, replace

from integration import get_dispute_context as source
from integration.fresh_reads import read_bundle
from .action_service import CommitRequest
from .schemas import (CommitResult, Contract, Dispute, DisputeContext, ExecutionStatus,
                      Transaction, require)
from .tools import (CustomerHistory, DecisionHistory, DisputeState, HistoricalDispute,
                    ReadResult, ReadStatus, _row, context_from_rows)


@dataclass(frozen=True, kw_only=True)
class FreshSnapshot(Contract):
    context: DisputeContext
    history: CustomerHistory
    decisions: DecisionHistory

    def _check(self):
        c, h, d = self.context, self.history, self.decisions
        require(c.reference.source_revision is not None, 'Fresh snapshot needs a revision')
        require(h.dispute_id == c.reference.dispute_id and h.snapshot_id == c.reference.snapshot_id and
                h.evaluation_at == c.reference.evaluation_at and h.source_revision == c.reference.source_revision and
                h.customer_id in {t.customer_id for t in c.transactions}, 'History binding mismatch')
        require(d.reference == c.reference and h.captured_at == d.captured_at == c.captured_at and
                h.source_channel == d.source_channel == c.source_channel, 'Snapshot binding mismatch')


def snapshot_from_bundle(bundle, captured, *, source_channel='zetaris'):
    """Strict mapping, also exercised against an isolated real PostgreSQL view."""
    raw, did = bundle['context'], bundle['context']['dispute']['dispute_id']
    result = context_from_rows(raw, did, captured_at=captured, source_channel=source_channel)
    c = result.data
    c = replace(c, reference=replace(c.reference, source_revision=bundle['source_revision']))
    anchor = next((t for t in c.transactions if t.transaction_id == c.dispute.transaction_id), None)
    require(anchor is not None, 'Visible primary transaction required')
    cases = []
    for row in bundle['history']:
        require(type(row) is dict and set(row) == {'dispute', 'transaction'}, 'Invalid history row')
        case = HistoricalDispute(dispute=_row(Dispute, row['dispute'], source.DISPUTE_COLUMNS),
            primary_transaction=_row(Transaction, row['transaction'], source.TRANSACTION_COLUMNS))
        require(case.primary_transaction.customer_id == anchor.customer_id and case.dispute.dispute_id != did,
                'History outside customer scope')
        if case.dispute.opened_at <= c.reference.evaluation_at and case.primary_transaction.recorded_at <= c.reference.evaluation_at:
            cases.append(case)
    history = CustomerHistory(dispute_id=did, customer_id=anchor.customer_id,
        snapshot_id=c.reference.snapshot_id, evaluation_at=c.reference.evaluation_at,
        captured_at=captured, source_channel=source_channel, source_revision=c.reference.source_revision,
        cases=tuple(sorted(cases, key=lambda x: (x.dispute.opened_at, x.dispute.dispute_id))))
    decisions = []
    for row in bundle['decisions']:
        require(type(row) is dict and set(row) == {'request', 'decision_id', 'committed_at', 'simulated_credit_id'},
                'Invalid stored receipt')
        request = CommitRequest.from_dict(row['request'])
        require(request.context.reference.dispute_id == did, 'Stored receipt outside case scope')
        decisions.append(CommitResult.from_dict(dict(run_id=request.run_id,
            proposal_id=request.proposal.proposal_id, idempotency_key=request.idempotency_key,
            reference=request.context.reference.to_dict(), status=ExecutionStatus.COMMITTED.value,
            message='Observed original committed decision.', decision_id=row['decision_id'],
            recommendation=request.proposal.recommendation.to_dict(), committed_at=row['committed_at'],
            simulated_credit_id=row['simulated_credit_id'])))
    return FreshSnapshot(context=c, history=history, decisions=DecisionHistory(reference=c.reference,
        captured_at=captured, source_channel=source_channel, decisions=tuple(decisions)))


def get_snapshot(dispute_id):
    bundle, captured = read_bundle(dispute_id)
    return snapshot_from_bundle(bundle, captured)


class FreshReadTools:
    """Projections of ONE verified snapshot; controller obtains a new one per read."""
    def __init__(self, snapshot):
        self.snapshot = FreshSnapshot.from_dict(snapshot.to_dict())

    def _result(self, dispute_id, value):
        require(dispute_id == self.snapshot.context.reference.dispute_id, 'Case scope mismatch')
        issues = value.data_issues if isinstance(value, DisputeContext) else ()
        return ReadResult(status=ReadStatus.INCOMPLETE if issues else ReadStatus.OK,
            message='Fresh source snapshot projection', data=value, issues=issues)

    def get_dispute_context(self, dispute_id):
        return self._result(dispute_id, self.snapshot.context)

    def get_customer_history(self, dispute_id):
        return self._result(dispute_id, self.snapshot.history)

    def get_dispute_state(self, dispute_id):
        c = self.snapshot.context
        return self._result(dispute_id, DisputeState(dispute=c.dispute, captured_at=c.captured_at,
            source_channel=c.source_channel, source_revision=c.reference.source_revision))

    def get_existing_decisions(self, dispute_id):
        return self._result(dispute_id, self.snapshot.decisions)
