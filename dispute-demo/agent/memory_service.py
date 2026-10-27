"""Source-linked H-MEM summaries. Recall is untrusted until T10 source verification.

Committed inputs come only from the trusted action caller. A persisted memory
is not a ledger or proof that a decision exists. No history threshold is defined.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import json
import re

from app.schemas import (CommitResult, ContextRef, Contract, ContractError,
    DisputeContext, ExecutionStatus, Outcome, Recommendation, require, source_id, uuid_id)
from agent.hmem_client import HmemClient, MemoryError, customer_scope, strict_json


def source_reference(decision_id):
    uuid_id(decision_id)
    return f'postgresql:dispute_demo/dispute_actions.decisions/{decision_id}'


@dataclass(frozen=True, kw_only=True)
class CommittedSummary(Contract):
    customer_id: str
    decision_id: str
    run_id: str
    proposal_id: str
    reference: ContextRef
    recommendation: Recommendation
    committed_at: datetime
    simulated_credit_id: str | None
    reason_code: str
    source_reference: str

    def _check(self):
        customer_scope(self.customer_id)
        for value in (self.decision_id, self.run_id, self.proposal_id):
            uuid_id(value)
        require(self.reference.source_revision is not None, 'Committed summary needs a source revision')
        require(self.committed_at >= self.reference.evaluation_at, 'Commit precedes source evaluation')
        require(self.source_reference == source_reference(self.decision_id), 'Invalid decision source reference')
        require(self.reason_code in ('refund_missing', 'not_received', 'duplicate_charge'), 'Invalid reason')
        if self.recommendation.outcome is Outcome.PROVISIONAL_CREDIT:
            uuid_id(self.simulated_credit_id)
        else:
            require(self.simulated_credit_id is None, 'Noncredit summary cannot have a credit effect')

    @classmethod
    def from_commit(cls, context: DisputeContext, result: CommitResult):
        require(type(context) is DisputeContext and type(result) is CommitResult, 'Typed commit and context required')
        require(result.status in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED), 'Confirmed commit required')
        require(result.reference == context.reference, 'Commit/context mismatch')
        anchor = next(t for t in context.transactions if t.transaction_id == context.dispute.transaction_id)
        return cls(customer_id=anchor.customer_id, decision_id=result.decision_id,
            run_id=result.run_id, proposal_id=result.proposal_id, reference=result.reference,
            recommendation=result.recommendation, committed_at=result.committed_at,
            simulated_credit_id=result.simulated_credit_id, reason_code=context.dispute.reason_code,
            source_reference=source_reference(result.decision_id))


@dataclass(frozen=True, kw_only=True)
class UnverifiedNote(Contract):
    note_id: str
    customer_id: str
    dispute_id: str
    policy_version: str
    noted_at: datetime
    text: str
    correction_to_decision_id: str | None = None

    def _check(self):
        uuid_id(self.note_id)
        customer_scope(self.customer_id)
        source_id(self.dispute_id, 'DP')
        require(re.fullmatch(r'v[1-9][0-9]*', self.policy_version), 'Invalid policy version')
        require(len(self.text) <= 2000, 'Note too long')
        if self.correction_to_decision_id:
            uuid_id(self.correction_to_decision_id)


@dataclass(frozen=True)
class MemorySaveResult:
    status: str
    source_id: str
    memory_id: str | None = None
    error: str | None = None


def record_input(item):
    require(type(item) in (CommittedSummary, UnverifiedNote), 'Unsupported memory input')
    committed = type(item) is CommittedSummary
    kind = 'committed_summary' if committed else 'unverified_note'
    ident = item.decision_id if committed else item.note_id
    source = ('decision:' if committed else 'unverified-note:') + ident
    did = item.reference.dispute_id if committed else item.dispute_id
    version = item.reference.policy_version if committed else item.policy_version
    timestamp = item.committed_at if committed else item.noted_at
    scope = customer_scope(item.customer_id)
    refs = [did, item.customer_id, source_reference(ident) if committed else source]
    return dict(content=json.dumps(dict(kind=kind, data=item.to_dict()), sort_keys=True, separators=(',', ':')),
        type='factual', layer='working', confidence=1, source=source, chatId=scope,
        tags=[scope, 'dispute:' + did, 'kind:' + kind, 'policy:' + version],
        provenance=dict(origin='plan_completion' if committed else 'manual',
            learnedAt=int(timestamp.timestamp() * 1000), label=kind, refs=refs))


def parse_record(record):
    """Decode claimed provenance, NOT authoritative verification."""
    body = strict_json(record['content'])
    require(type(body) is dict and set(body) == {'kind', 'data'}, 'Invalid memory envelope')
    require(body['kind'] in ('committed_summary', 'unverified_note'), 'Invalid memory kind')
    cls = CommittedSummary if body['kind'] == 'committed_summary' else UnverifiedNote
    item = cls.from_dict(body['data'])
    expected = record_input(item)
    for key in ('content', 'source', 'chatId', 'tags', 'provenance'):
        require(record[key] == expected[key], 'Memory provenance mismatch')
    return item


class DisputeMemory:
    def __init__(self, client: HmemClient):
        self.client = client

    def save(self, item: CommittedSummary | UnverifiedNote):
        """Retry this same source ID only. Never invoke a financial action."""
        record = record_input(item)
        try:
            result = self.client.add(record)
            require(parse_record(result['memory']) == item, 'Memory response differs from input')
            return MemorySaveResult(result['storage_status'], record['source'], result['memory']['id'])
        except MemoryError as exc:
            return MemorySaveResult('failed', record['source'], error=str(exc))
        except (ValueError, TypeError, KeyError):
            return MemorySaveResult('failed', record['source'], error='memory_response_invalid')

    def remember_commit(self, context: DisputeContext, result: CommitResult):
        return self.save(CommittedSummary.from_commit(context, result))

    def recall(self, customer_id, *, query='committed dispute decision', top_n=5, threshold=.35):
        result = self.client.query(query, chat_id=customer_scope(customer_id), top_n=top_n, threshold=threshold)
        candidates = []
        for record in result['memories']:
            try:
                item = parse_record(record)
                require(item.customer_id == customer_id, 'Memory customer mismatch')
            except (ValueError, TypeError, KeyError):
                raise MemoryError('memory_provenance_invalid') from None
            candidates.append(item)
        return tuple(candidates)
