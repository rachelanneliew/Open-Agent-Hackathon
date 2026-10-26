"""Immutable, strict transport contracts. No I/O, policy evaluation or action writes.

Construct with typed Python values, or use ``from_dict`` for JSON-shaped input.
See ../docs/contracts.md for source semantics and the future commit protocol.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from enum import Enum
import re
from types import UnionType
from typing import get_args, get_origin, get_type_hints
from uuid import UUID


class ContractError(ValueError):
    """A payload does not satisfy the structural contract."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def _typed(value, annotation, path, *, decode=False):
    """Validate the deliberately small type vocabulary used by these contracts."""
    origin, args = get_origin(annotation), get_args(annotation)
    if origin is UnionType:
        for alternative in args:
            try:
                return _typed(value, alternative, path, decode=decode)
            except ContractError:
                pass
        raise ContractError(f'{path}: unexpected type or value')
    if origin is tuple:
        require(type(value) is tuple or (decode and type(value) is list), f'{path}: expected array')
        return tuple(_typed(item, args[0], f'{path}[{i}]', decode=decode)
                     for i, item in enumerate(value))
    if annotation is datetime:
        if decode and type(value) is str:
            require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z', value),
                    f'{path}: expected UTC ISO timestamp ending in Z')
            try:
                value = datetime.fromisoformat(value[:-1] + '+00:00')
            except ValueError as exc:
                raise ContractError(f'{path}: invalid timestamp') from exc
        require(type(value) is datetime and value.utcoffset() == timedelta(0), f'{path}: expected UTC datetime')
        return value
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        if decode and type(value) is str:
            try:
                value = annotation(value)
            except ValueError as exc:
                raise ContractError(f'{path}: unsupported {annotation.__name__}') from exc
        require(type(value) is annotation, f'{path}: expected {annotation.__name__}')
        return value
    if isinstance(annotation, type) and issubclass(annotation, Contract):
        if decode and type(value) is dict:
            value = annotation.from_dict(value)
        require(type(value) is annotation, f'{path}: expected {annotation.__name__}')
        return value
    require(type(value) is annotation, f'{path}: expected {annotation.__name__}')
    if annotation is str:
        require(bool(value.strip()), f'{path}: must not be blank')
    return value


class Contract:
    def __post_init__(self):
        hints = get_type_hints(type(self))
        for field in fields(self):
            _typed(getattr(self, field.name), hints[field.name], field.name)
        self._check()

    def _check(self):
        pass

    @classmethod
    def from_dict(cls, payload):
        require(type(payload) is dict, f'{cls.__name__}: expected object')
        hints = get_type_hints(cls)
        require(not (payload.keys() - hints.keys()), f'{cls.__name__}: unknown fields')
        decoded = {key: _typed(value, hints[key], key, decode=True) for key, value in payload.items()}
        try:
            return cls(**decoded)
        except TypeError as exc:
            raise ContractError(f'{cls.__name__}: missing required fields') from exc

    def to_dict(self):
        def encode(value):
            if isinstance(value, Contract):
                return value.to_dict()
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, datetime):
                return value.isoformat().replace('+00:00', 'Z')
            if isinstance(value, tuple):
                return [encode(item) for item in value]
            return value
        return {field.name: encode(getattr(self, field.name)) for field in fields(self)}


def source_id(value, prefix, digits=4):
    require(type(value) is str and re.fullmatch(rf'{prefix}-[0-9]{{{digits}}}', value), f'Invalid {prefix} ID')


def uuid_id(value):
    try:
        require(type(value) is str and str(UUID(value)) == value and UUID(value).int != 0, 'Expected canonical nonzero UUID')
    except (ValueError, AttributeError) as exc:
        raise ContractError('Expected canonical nonzero UUID') from exc


def money(value, *, minimum=0):
    require(type(value) is int and minimum <= value <= 2**63 - 1, 'Expected integer minor units within BIGINT range')


def currency_code(value):
    require(type(value) is str and re.fullmatch('[A-Z]{3}', value), 'Expected three-letter currency code')


def rule_id(value, version=None):
    require(type(value) is str and re.fullmatch(r'v[1-9][0-9]*-[A-Z][A-Z0-9_]*', value), 'Invalid policy rule ID')
    if version is not None:
        require(value.startswith(version + '-'), 'Rule ID has a different policy version')


def unique(values):
    require(len(values) == len(set(values)), 'Duplicate identifiers or values')


def citations(evidence_ids, policy_rule_ids, version):
    unique(evidence_ids)
    unique(policy_rule_ids)
    for value in evidence_ids:
        source_id(value, 'EV')
    for value in policy_rule_ids:
        rule_id(value, version)


class Outcome(str, Enum):
    PROVISIONAL_CREDIT = 'provisional_credit'
    REQUEST_EVIDENCE = 'request_evidence'
    DECLINE = 'decline'
    HUMAN_REVIEW = 'human_review'


class MovementType(str, Enum):
    CAPTURE = 'capture'
    REFUND = 'refund'
    REVERSAL = 'reversal'


class SettlementStatus(str, Enum):
    COMPLETED = 'completed'
    PENDING = 'pending'
    FAILED = 'failed'


class ExecutionStatus(str, Enum):
    COMMITTED = 'committed'
    REUSED = 'reused'
    REJECTED = 'rejected'
    UNAVAILABLE = 'unavailable'
    FAILED = 'failed'


class CriticVerdict(str, Enum):
    ACCEPTED = 'accepted'
    REVISE = 'revise'
    HUMAN_REVIEW = 'human_review'


class RunPhase(str, Enum):
    CREATED = 'created'
    RETRIEVED = 'retrieved'
    EVALUATED = 'evaluated'
    PROPOSED = 'proposed'
    VALIDATED = 'validated'
    FINISHED = 'finished'
    FAILED = 'failed'


@dataclass(frozen=True, kw_only=True)
class ContextRef(Contract):
    dispute_id: str
    snapshot_id: str
    evaluation_at: datetime
    policy_version: str
    source_revision: int | None = None

    def _check(self):
        source_id(self.dispute_id, 'DP')
        uuid_id(self.snapshot_id)
        require(re.fullmatch(r'v[1-9][0-9]*', self.policy_version), 'Invalid policy version')
        if self.source_revision is not None:
            money(self.source_revision)


@dataclass(frozen=True, kw_only=True)
class Recommendation(Contract):
    outcome: Outcome
    currency: str
    amount_minor: int | None = None

    def _check(self):
        currency_code(self.currency)
        if self.outcome is Outcome.PROVISIONAL_CREDIT:
            money(self.amount_minor, minimum=1)
        else:
            require(self.amount_minor is None, 'Non-credit outcomes must have no amount')


def from_legacy_recommendation(outcome: str, recommended_refund_minor: int, currency: str) -> Recommendation:
    """Explicit recommendation-only mapping; never pass settlement movements here.

    The caller supplies a legacy recommendation amount. Fixture loading belongs
    only in tests, not in this module or future runtime tools.
    """
    mapping = {'recommend_refund': Outcome.PROVISIONAL_CREDIT, 'reject': Outcome.DECLINE,
               'request_evidence': Outcome.REQUEST_EVIDENCE, 'escalate': Outcome.HUMAN_REVIEW}
    require(type(outcome) is str and outcome in mapping, 'Unsupported legacy recommendation')
    money(recommended_refund_minor)
    if outcome != 'recommend_refund':
        require(recommended_refund_minor == 0, 'Legacy non-credit amount must be zero')
    return Recommendation(outcome=mapping[outcome], currency=currency,
                          amount_minor=recommended_refund_minor if outcome == 'recommend_refund' else None)


@dataclass(frozen=True, kw_only=True)
class Dispute(Contract):
    dispute_id: str
    transaction_id: str
    reason_code: str
    claimed_amount_minor: int
    currency: str
    customer_statement: str
    opened_at: datetime
    evaluation_at: datetime
    dispute_status: str
    related_transaction_id: str | None = None

    def _check(self):
        source_id(self.dispute_id, 'DP')
        source_id(self.transaction_id, 'TX')
        money(self.claimed_amount_minor, minimum=1)
        currency_code(self.currency)
        require(self.reason_code in ('refund_missing', 'not_received', 'duplicate_charge'), 'Unsupported dispute reason')
        require(self.opened_at <= self.evaluation_at, 'Evaluation precedes opening')
        if self.related_transaction_id is not None:
            source_id(self.related_transaction_id, 'TX')
            require(self.related_transaction_id != self.transaction_id, 'Companion must be a different transaction')
        # Do not interpret unknown source lifecycle states as permission to act.


@dataclass(frozen=True, kw_only=True)
class Transaction(Contract):
    transaction_id: str
    order_id: str
    customer_id: str
    merchant_id: str
    amount_minor: int
    currency: str
    transaction_status: str
    occurred_at: datetime
    recorded_at: datetime

    def _check(self):
        for value, prefix, digits in ((self.transaction_id, 'TX', 4), (self.order_id, 'OR', 4),
                                      (self.customer_id, 'CUST', 3), (self.merchant_id, 'MER', 3)):
            source_id(value, prefix, digits)
        money(self.amount_minor, minimum=1)
        currency_code(self.currency)
        require(self.transaction_status in ('authorized', 'captured', 'reversed', 'failed'), 'Invalid transaction status')
        require(self.occurred_at <= self.recorded_at, 'Transaction recorded before occurrence')


@dataclass(frozen=True, kw_only=True)
class Settlement(Contract):
    settlement_id: str
    transaction_id: str
    movement_type: MovementType
    amount_minor: int
    currency: str
    settlement_status: SettlementStatus
    occurred_at: datetime
    recorded_at: datetime

    def _check(self):
        source_id(self.settlement_id, 'ST')
        source_id(self.transaction_id, 'TX')
        money(self.amount_minor, minimum=1)
        currency_code(self.currency)
        require(self.occurred_at <= self.recorded_at, 'Settlement recorded before occurrence')


@dataclass(frozen=True, kw_only=True)
class Evidence(Contract):
    evidence_id: str
    dispute_id: str
    evidence_type: str
    source_type: str
    integrity_status: str
    event_at: datetime
    available_at: datetime
    content: str | None
    related_settlement_id: str | None = None

    def _check(self):
        source_id(self.evidence_id, 'EV')
        source_id(self.dispute_id, 'DP')
        if self.related_settlement_id is not None:
            source_id(self.related_settlement_id, 'ST')
        require(self.evidence_type in ('receipt', 'delivery_record', 'refund_confirmation', 'merchant_response'), 'Invalid evidence type')
        require(self.source_type in ('customer', 'merchant', 'carrier', 'payment_system'), 'Invalid evidence source')
        require(self.integrity_status in ('valid', 'unreadable', 'incomplete'), 'Invalid integrity status')
        require(self.event_at <= self.available_at, 'Evidence available before event')


@dataclass(frozen=True, kw_only=True)
class EvidenceRequirement(Contract):
    category: str
    reason: str
    policy_rule_id: str

    def _check(self):
        require(self.category in ('receipt', 'delivery_record', 'refund_confirmation', 'two_completed_captures_same_order'),
                'Unknown evidence requirement')
        require(self.reason in ('absent', 'unusable', 'not_yet_available'), 'Invalid missing-evidence reason')
        rule_id(self.policy_rule_id)


@dataclass(frozen=True, kw_only=True)
class PolicyRule(Contract):
    policy_rule_id: str
    policy_version: str
    priority: int
    effective_from: datetime
    effective_to: datetime | None
    predicate: str
    action: Outcome
    parameters_json: str
    reason_code: str
    explanation: str

    def _check(self):
        import json
        rule_id(self.policy_rule_id, self.policy_version)
        require(self.reason_code in ('ALL', 'refund_missing', 'not_received', 'duplicate_charge'), 'Invalid rule reason scope')
        money(self.priority, minimum=1)
        require(self.effective_to is None or self.effective_from < self.effective_to, 'Invalid policy period')
        try:
            require(type(json.loads(self.parameters_json)) is dict, 'Policy parameters must be an object')
        except ValueError as exc:
            raise ContractError('Invalid policy parameter JSON') from exc


@dataclass(frozen=True, kw_only=True)
class DisputeContext(Contract):
    reference: ContextRef
    captured_at: datetime
    source_channel: str
    dispute: Dispute
    transactions: tuple[Transaction, ...]
    settlements: tuple[Settlement, ...]
    evidence: tuple[Evidence, ...]
    policy_rules: tuple[PolicyRule, ...]
    data_issues: tuple[str, ...] = ()

    def _check(self):
        require(self.source_channel in ('zetaris', 'offline_test'), 'Invalid source channel')
        require(self.reference.dispute_id == self.dispute.dispute_id and
                self.reference.evaluation_at == self.dispute.evaluation_at, 'Context identity/cutoff mismatch')
        require(self.captured_at >= self.reference.evaluation_at, 'Snapshot captured before evaluation cutoff')
        for collection, key in ((self.transactions, 'transaction_id'), (self.settlements, 'settlement_id'),
                                (self.evidence, 'evidence_id'), (self.policy_rules, 'policy_rule_id')):
            unique(tuple(getattr(item, key) for item in collection))
        tx_ids = {self.dispute.transaction_id, self.dispute.related_transaction_id}
        require(all(t.transaction_id in tx_ids for t in self.transactions), 'Transaction outside case scope')
        require(all(s.transaction_id in tx_ids for s in self.settlements), 'Settlement outside case scope')
        require(all(e.dispute_id == self.reference.dispute_id for e in self.evidence), 'Evidence outside case scope')
        require(all(p.policy_version == self.reference.policy_version for p in self.policy_rules), 'Mixed policy versions')
        cutoff = self.reference.evaluation_at
        require(all(t.recorded_at <= cutoff for t in self.transactions), 'Transaction after evaluation cutoff')
        require(all(s.recorded_at <= cutoff for s in self.settlements), 'Settlement after evaluation cutoff')
        require(all(e.available_at <= cutoff for e in self.evidence), 'Evidence after evaluation cutoff')
        require(all(p.effective_from <= self.dispute.opened_at and
                    (p.effective_to is None or self.dispute.opened_at < p.effective_to)
                    for p in self.policy_rules), 'Policy does not apply at dispute opening')
        if not self.data_issues:
            require(self.dispute.transaction_id in {t.transaction_id for t in self.transactions}, 'Missing primary transaction needs data issue')
            require(bool(self.policy_rules), 'Missing policy needs data issue')
        # Business anomalies (pending captures, contradictions, missing support)
        # remain representable. Source verification and rule evaluation are T02/T03.


@dataclass(frozen=True, kw_only=True)
class RuleCheck(Contract):
    policy_rule_id: str
    status: str
    explanation: str
    evidence_ids: tuple[str, ...] = ()

    def _check(self):
        rule_id(self.policy_rule_id)
        require(self.status in ('matched', 'not_matched', 'not_evaluated'), 'Invalid rule-check status')
        citations(self.evidence_ids, (), '')


@dataclass(frozen=True, kw_only=True)
class PolicyResult(Contract):
    reference: ContextRef
    allowed_outcomes: tuple[Outcome, ...]
    blocked_outcomes: tuple[Outcome, ...]
    rule_checks: tuple[RuleCheck, ...]
    currency: str
    credit_limit_minor: int | None = None
    missing_evidence: tuple[EvidenceRequirement, ...] = ()
    data_issues: tuple[str, ...] = ()

    def _check(self):
        currency_code(self.currency)
        unique(self.allowed_outcomes)
        unique(self.blocked_outcomes)
        require(bool(self.allowed_outcomes), 'A policy result must state an allowed safe outcome')
        require(not set(self.allowed_outcomes) & set(self.blocked_outcomes), 'Allowed and blocked outcomes overlap')
        require(set(self.allowed_outcomes) | set(self.blocked_outcomes) == set(Outcome), 'Every outcome needs an explicit disposition')
        require(bool(self.rule_checks or self.data_issues), 'Policy result needs checks or explicit input failures')
        if self.data_issues:
            require(self.allowed_outcomes == (Outcome.HUMAN_REVIEW,), 'Unresolved input failures require human review')
        if Outcome.PROVISIONAL_CREDIT in self.allowed_outcomes:
            money(self.credit_limit_minor, minimum=1)
        else:
            require(self.credit_limit_minor is None, 'No credit limit when credit is blocked')
        unique(tuple(check.policy_rule_id for check in self.rule_checks))
        for check in (*self.rule_checks, *self.missing_evidence):
            rule_id(check.policy_rule_id, self.reference.policy_version)


@dataclass(frozen=True, kw_only=True)
class AgentProposal(Contract):
    proposal_id: str
    run_id: str
    reference: ContextRef
    recommendation: Recommendation
    rationale: str
    evidence_ids: tuple[str, ...]
    policy_rule_ids: tuple[str, ...]
    missing_evidence: tuple[EvidenceRequirement, ...] = ()
    revision: int = 0

    def _check(self):
        uuid_id(self.proposal_id)
        uuid_id(self.run_id)
        require(self.revision in (0, 1), 'Only the initial proposal and one correction are supported')
        citations(self.evidence_ids, self.policy_rule_ids, self.reference.policy_version)
        for item in self.missing_evidence:
            rule_id(item.policy_rule_id, self.reference.policy_version)
        if self.recommendation.outcome is Outcome.REQUEST_EVIDENCE:
            require(bool(self.missing_evidence), 'Evidence request needs requirement categories')
        # Valid syntax is not factual support or approval; that is the T06 critic.


@dataclass(frozen=True, kw_only=True)
class CriticResult(Contract):
    proposal_id: str
    reference: ContextRef
    verdict: CriticVerdict
    feedback: str
    failed_checks: tuple[str, ...] = ()

    def _check(self):
        uuid_id(self.proposal_id)
        require((self.verdict is CriticVerdict.ACCEPTED) == (not self.failed_checks),
                'Accepted critique has no failures; other verdicts require failed checks')


@dataclass(frozen=True, kw_only=True)
class CommitResult(Contract):
    run_id: str
    proposal_id: str
    idempotency_key: str
    reference: ContextRef
    status: ExecutionStatus
    message: str
    decision_id: str | None = None
    recommendation: Recommendation | None = None
    committed_at: datetime | None = None
    simulated_credit_id: str | None = None

    def _check(self):
        for value in (self.run_id, self.proposal_id, self.idempotency_key):
            uuid_id(value)
        persisted = self.status in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED)
        if persisted:
            require(self.decision_id is not None and self.recommendation is not None and self.committed_at is not None,
                    'Persisted result needs decision, outcome and commit time')
            uuid_id(self.decision_id)
            require(self.reference.source_revision is not None, 'Persistence requires a verified source revision')
            require(self.committed_at >= self.reference.evaluation_at, 'Commit precedes evaluation')
            if self.recommendation.outcome is Outcome.PROVISIONAL_CREDIT:
                uuid_id(self.simulated_credit_id)
            else:
                require(self.simulated_credit_id is None, 'Non-credit decision must not have a credit effect')
        else:
            require(all(value is None for value in (self.decision_id, self.recommendation, self.committed_at, self.simulated_credit_id)),
                    'Unsuccessful commit must not claim persisted decision or effects')


@dataclass(frozen=True, kw_only=True)
class RunState(Contract):
    run_id: str
    phase: RunPhase
    model_calls: int = 0
    tool_calls: int = 0
    proposal_revision: int = 0
    reference: ContextRef | None = None
    commit_result: CommitResult | None = None
    error: str | None = None

    def _check(self):
        uuid_id(self.run_id)
        money(self.model_calls)
        money(self.tool_calls)
        require(self.proposal_revision in (0, 1), 'At most one correction is supported')
        if self.phase not in (RunPhase.CREATED, RunPhase.FAILED):
            require(self.reference is not None, 'This phase requires context')
        if self.commit_result is not None:
            require(self.phase is RunPhase.FINISHED, 'Only a finished run holds a commit result')
            require(self.commit_result.run_id == self.run_id and self.commit_result.reference == self.reference,
                    'Run/commit identity mismatch')
        if self.phase is RunPhase.FINISHED:
            require(self.commit_result is not None, 'Finished run needs explicit commit execution status')
        require((self.phase is RunPhase.FAILED) == (self.error is not None), 'Only failed runs require an error')
