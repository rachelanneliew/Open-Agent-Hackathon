"""Synthetic contract stubs for memory tests; not database receipts."""
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5
from app.schemas import ContextRef, Recommendation, Outcome
from agent.memory_service import CommittedSummary, UnverifiedNote, source_reference


def ident(value):
    return str(uuid5(NAMESPACE_URL, 'memory-contract-test/' + str(value)))


def summary(index=1, customer='CUST-006'):
    instant = datetime(2026, 10, 27, tzinfo=timezone.utc)
    decision = ident(index)
    return CommittedSummary(customer_id=customer, decision_id=decision, run_id=ident('run' + str(index)),
        proposal_id=ident('proposal' + str(index)),
        reference=ContextRef(dispute_id=f'DP-{index:04}', snapshot_id=ident('snapshot' + str(index)),
            evaluation_at=instant, policy_version='v2', source_revision=3),
        recommendation=Recommendation(outcome=Outcome.PROVISIONAL_CREDIT, amount_minor=6000, currency='SGD'),
        committed_at=instant, simulated_credit_id=ident('credit' + str(index)), reason_code='not_received',
        source_reference=source_reference(decision))


def note():
    s = summary()
    return UnverifiedNote(note_id=ident('note'), customer_id=s.customer_id,
        dispute_id=s.reference.dispute_id, policy_version='v2', noted_at=s.committed_at,
        text='Analyst correction awaiting authoritative source verification.',
        correction_to_decision_id=s.decision_id)
