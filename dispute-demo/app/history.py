"""Bounded advisory history; transport validation is not source verification."""
from dataclasses import dataclass
from datetime import datetime

from .schemas import (ContextRef, Contract, Recommendation, require, source_id,
                      unique, uuid_id)


@dataclass(frozen=True, kw_only=True)
class HistoricalDecision(Contract):
    decision_id: str
    original_reference: ContextRef
    recommendation: Recommendation
    committed_at: datetime
    reason_code: str
    source_reference: str
    verified_reference: ContextRef

    def _check(self):
        uuid_id(self.decision_id)
        require(self.reason_code in ('refund_missing', 'not_received', 'duplicate_charge'), 'Invalid reason')
        require(self.source_reference == 'postgresql:dispute_demo/dispute_actions.decisions/' + self.decision_id,
                'Invalid source reference')
        require(self.original_reference.dispute_id == self.verified_reference.dispute_id and
                self.original_reference.source_revision is not None and
                self.verified_reference.source_revision is not None, 'Invalid verification reference')
        require(self.original_reference.evaluation_at <= self.committed_at <= self.verified_reference.evaluation_at,
                'Invalid decision visibility')


@dataclass(frozen=True, kw_only=True)
class VerifiedHistory(Contract):
    reference: ContextRef
    customer_id: str
    records: tuple[HistoricalDecision, ...] = ()
    scope: str = 'advisory_no_binding_history_rule'

    def _check(self):
        source_id(self.customer_id, 'CUST', 3)
        require(self.scope == 'advisory_no_binding_history_rule', 'No binding history rule exists')
        require(self.reference.source_revision is not None and len(self.records) <= 5, 'Invalid history bounds')
        unique(tuple(r.original_reference.dispute_id for r in self.records))
        unique(tuple(r.decision_id for r in self.records))
        for record in self.records:
            require(record.original_reference.dispute_id != self.reference.dispute_id and
                    record.committed_at <= self.reference.evaluation_at and
                    record.verified_reference.source_revision == self.reference.source_revision,
                    'History is outside current snapshot scope')


def validate_history(context, history):
    if history is None:
        return
    require(type(history) is VerifiedHistory, 'Expected verified history')
    VerifiedHistory.from_dict(history.to_dict())
    anchor = next(t for t in context.transactions if t.transaction_id == context.dispute.transaction_id)
    require(history.reference == context.reference and history.customer_id == anchor.customer_id,
            'Advisory history binding mismatch')
