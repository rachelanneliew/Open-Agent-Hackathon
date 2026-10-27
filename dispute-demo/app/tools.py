"""Typed read boundary and case-bound tool dispatch. No writes or model calls.

Run from dispute-demo: python -m app.tools DP-0014 [--tool get_customer_history]
All injected sources/clocks are application configuration, never tool arguments.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
from numbers import Integral
from uuid import uuid4

from integration import get_dispute_context as source
from .schemas import (Contract, ContractError, ContextRef, Dispute, DisputeContext,
                      CommitResult, Evidence, Outcome, PolicyRule, Settlement, Transaction,
                      require, source_id, unique, uuid_id)


class ReadStatus(str, Enum):
    OK = 'ok'
    INCOMPLETE = 'incomplete'
    NOT_FOUND = 'not_found'
    MALFORMED = 'malformed'
    UNAVAILABLE = 'unavailable'
    UNSUPPORTED = 'unsupported'
    INVALID_REQUEST = 'invalid_request'


@dataclass(frozen=True, kw_only=True)
class HistoricalDispute(Contract):
    """Source IDs and facts only; no inferred decision or memory verification tag."""
    dispute: Dispute
    primary_transaction: Transaction

    def _check(self):
        require(self.dispute.transaction_id == self.primary_transaction.transaction_id,
                'History transaction does not belong to dispute')


@dataclass(frozen=True, kw_only=True)
class CustomerHistory(Contract):
    dispute_id: str
    customer_id: str
    snapshot_id: str
    evaluation_at: datetime
    captured_at: datetime
    source_channel: str
    cases: tuple[HistoricalDispute, ...]
    source_revision: int | None = None
    decisions_supported: bool = False

    def _check(self):
        source_id(self.dispute_id, 'DP')
        source_id(self.customer_id, 'CUST', 3)
        uuid_id(self.snapshot_id)
        require(self.source_revision is None or self.source_revision >= 0, 'Invalid revision')
        require(self.source_channel in ('zetaris', 'offline_test'), 'Invalid source channel')
        require(self.captured_at >= self.evaluation_at, 'Capture precedes cutoff')
        require(not self.decisions_supported, 'Use the separate decision-history projection')
        unique(tuple(c.dispute.dispute_id for c in self.cases))
        for case in self.cases:
            require(case.dispute.dispute_id != self.dispute_id, 'Current case is not history')
            require(case.primary_transaction.customer_id == self.customer_id, 'History outside customer scope')
            require(case.dispute.opened_at <= self.evaluation_at and
                    case.primary_transaction.recorded_at <= self.evaluation_at, 'History after cutoff')


@dataclass(frozen=True, kw_only=True)
class DisputeState(Contract):
    """Source row projection; only the fresh adapter supplies a verified revision."""
    dispute: Dispute
    captured_at: datetime
    source_channel: str
    source_revision: int | None = None

    def _check(self):
        require(self.source_channel in ('zetaris', 'offline_test'), 'Invalid source channel')
        require(self.source_revision is None or self.source_revision >= 0, 'Invalid revision')
        require(self.captured_at >= self.dispute.evaluation_at, 'Capture precedes cutoff')


@dataclass(frozen=True, kw_only=True)
class DecisionHistory(Contract):
    """Observed original receipts, never claims of actions by this read/run."""
    reference: ContextRef
    captured_at: datetime
    source_channel: str
    decisions: tuple[CommitResult, ...]

    def _check(self):
        require(self.source_channel in ('zetaris', 'offline_test'), 'Invalid source channel')
        require(self.reference.source_revision is not None, 'Decision reads require a revision')
        require(self.captured_at >= self.reference.evaluation_at, 'Capture precedes cutoff')
        unique(tuple(d.decision_id for d in self.decisions))
        for d in self.decisions:
            require(d.decision_id is not None and d.reference.dispute_id == self.reference.dispute_id,
                    'Invalid stored decision scope')
            require(d.committed_at <= self.reference.evaluation_at, 'Decision after cutoff')


@dataclass(frozen=True, kw_only=True)
class ReadResult(Contract):
    status: ReadStatus
    message: str
    data: DisputeContext | CustomerHistory | DisputeState | DecisionHistory | None = None
    issues: tuple[str, ...] = ()

    def _check(self):
        if self.status is ReadStatus.OK:
            require(self.data is not None and not self.issues, 'Successful read requires data without input issues')
            if isinstance(self.data, DisputeContext):
                require(not self.data.data_issues, 'Incomplete context cannot be successful')
        elif self.status is ReadStatus.INCOMPLETE:
            require(bool(self.issues), 'Incomplete read requires issues')
            require(self.data is None or (isinstance(self.data, DisputeContext) and
                    self.data.data_issues == self.issues), 'Partial context must carry its issues')
        else:
            require(self.data is None, 'Failed or unsupported reads cannot expose data')


def _row(cls, raw, columns):
    require(type(raw) is dict and set(raw) == set(columns), 'Unexpected source fields')
    payload = dict(raw)
    for key, value in payload.items():
        # JDBC BIGINT may be a Java integral wrapper. Do not coerce floats,
        # booleans or numeric strings into money. T01 contracts stay strict.
        if key.endswith('_minor') or key == 'priority':
            require(isinstance(value, Integral) and not isinstance(value, bool), 'Invalid source integer')
            payload[key] = int(value)
        if key in ('related_transaction_id', 'related_settlement_id', 'effective_to') and value == '':
            payload[key] = None
    return cls.from_dict(payload)


def _json_object(text):
    def pairs(items):
        require(len(items) == len(dict(items)), 'Duplicate JSON keys')
        return dict(items)
    require(type(text) is str, 'Expected source JSON text')
    def invalid_constant(value):
        raise ContractError('Non-finite JSON constant')
    result = json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)
    require(type(result) is dict, 'Expected JSON object')
    return result


def _policy(raw):
    require(type(raw) is dict and set(raw) == set(source.POLICY_COLUMNS), 'Unexpected policy fields')
    payload = dict(raw)
    condition = _json_object(payload.pop('condition_json'))
    require(set(condition) == {'predicate'}, 'Unsupported predicate envelope')
    payload['predicate'] = condition['predicate']
    actions = {'recommend_refund': Outcome.PROVISIONAL_CREDIT.value, 'reject': Outcome.DECLINE.value,
               'request_evidence': Outcome.REQUEST_EVIDENCE.value, 'escalate': Outcome.HUMAN_REVIEW.value}
    require(type(payload['action']) is str and payload['action'] in actions, 'Unsupported source action')
    payload['action'] = actions[payload['action']]
    _json_object(payload['parameters_json'])
    return _row(PolicyRule, payload, tuple(payload))


def _case(raw, dispute_id):
    case = _row(Dispute, raw, source.DISPUTE_COLUMNS)
    require(case.dispute_id == dispute_id, 'Dispute outside requested scope')
    return case


def context_from_rows(raw, dispute_id, *, captured_at, source_channel):
    """Explicit raw-to-typed boundary, also used by offline adversarial tests."""
    require(type(raw) is dict and set(raw) == {'dispute', 'transactions', 'settlements', 'evidence', 'policy_rules'},
            'Unexpected context fields')
    case = _case(raw['dispute'], dispute_id)
    for name in ('transactions', 'settlements', 'evidence', 'policy_rules'):
        require(type(raw[name]) is list, 'Expected source row collection')
    cutoff = case.evaluation_at
    linked_ids = {case.transaction_id, case.related_transaction_id} - {None}
    transactions = tuple(_row(Transaction, r, source.TRANSACTION_COLUMNS) for r in raw['transactions'])
    settlements = tuple(_row(Settlement, r, source.SETTLEMENT_COLUMNS) for r in raw['settlements'])
    issues, evidence = [], []
    for row in raw['evidence']:
        require(type(row) is dict, 'Expected evidence row')
        payload = dict(row)
        content = payload.get('content')
        require(content is None or type(content) is str, 'Invalid evidence content')
        if content is None or not content.strip() or payload.get('integrity_status') != 'valid':
            payload['content'] = None
        item = _row(Evidence, payload, (*source.EVIDENCE_COLUMNS, 'content'))
        evidence.append(item)
    rules = tuple(_policy(r) for r in raw['policy_rules'])
    require(all(t.transaction_id in linked_ids for t in transactions), 'Transaction outside case scope')
    require(all(s.transaction_id in linked_ids for s in settlements), 'Settlement outside case scope')
    require(all(e.dispute_id == dispute_id for e in evidence), 'Evidence outside case scope')
    for collection, key in ((transactions, 'transaction_id'), (settlements, 'settlement_id'),
                            (evidence, 'evidence_id'), (rules, 'policy_rule_id')):
        unique(tuple(getattr(item, key) for item in collection))
    require(len({t.customer_id for t in transactions}) <= 1, 'Transactions cross customer scope')
    # Defense in depth: the backend's filters are not an authorization boundary.
    transactions = tuple(t for t in transactions if t.recorded_at <= cutoff)
    settlements = tuple(s for s in settlements if s.occurred_at <= cutoff and s.recorded_at <= cutoff)
    evidence = tuple(e for e in evidence if e.available_at <= cutoff)
    rules = tuple(p for p in rules if p.effective_from <= case.opened_at and
                  (p.effective_to is None or case.opened_at < p.effective_to) and
                  p.reason_code in ('ALL', case.reason_code))
    versions = {p.policy_version for p in rules}
    if not versions:
        # ContextRef requires an actual selected version. Do not invent one just
        # to force an incomplete case into a valid context.
        raise source.ReadIncomplete('Applicable policy unavailable; no context version can be established')
    require(len(versions) == 1, 'Overlapping policy versions')
    unique(tuple(p.priority for p in rules))
    for tx_id in sorted(linked_ids - {t.transaction_id for t in transactions}):
        issues.append('transaction_unavailable:' + tx_id)
    for item in evidence:
        if item.content is None:
            issues.append('evidence_text_unavailable:' + item.evidence_id)
        if item.related_settlement_id is not None and item.related_settlement_id not in {s.settlement_id for s in settlements}:
            issues.append('evidence_settlement_unavailable:' + item.evidence_id)
    context = DisputeContext(
        reference=ContextRef(dispute_id=dispute_id, snapshot_id=str(uuid4()), evaluation_at=cutoff,
                             policy_version=next(iter(versions)), source_revision=None),
        captured_at=captured_at, source_channel=source_channel, dispute=case,
        transactions=transactions, settlements=settlements, evidence=evidence,
        policy_rules=tuple(sorted(rules, key=lambda p: p.priority)), data_issues=tuple(issues))
    return ReadResult(status=ReadStatus.INCOMPLETE if issues else ReadStatus.OK,
                      message='Case retrieved with input issues' if issues else 'Case retrieved',
                      data=context, issues=tuple(issues))


class ReadTools:
    """Application-owned source injection; defaults to the existing JDBC path."""
    def __init__(self, *, backend=source, source_channel='zetaris', clock=None):
        require(source_channel in ('zetaris', 'offline_test'), 'Invalid source channel')
        self.backend = backend
        self.source_channel = source_channel
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _read(self, dispute_id, operation):
        try:
            source.validate_dispute_id(dispute_id)
        except ValueError:
            return ReadResult(status=ReadStatus.INVALID_REQUEST, message='Invalid dispute ID')
        try:
            return operation()
        except source.CaseNotFound:
            return ReadResult(status=ReadStatus.NOT_FOUND, message='Dispute not found')
        except source.ReadIncomplete:
            # Do not forward exception text, including from injected backends.
            return ReadResult(status=ReadStatus.INCOMPLETE, message='Source data incomplete',
                              issues=('source_incomplete_or_limit_exceeded',))
        except source.ReadUnavailable:
            return ReadResult(status=ReadStatus.UNAVAILABLE, message='Zetaris read unavailable')
        except (source.InvalidSource, ContractError, ValueError, TypeError, KeyError):
            return ReadResult(status=ReadStatus.MALFORMED, message='Source data failed validation')
        except Exception:
            return ReadResult(status=ReadStatus.UNAVAILABLE, message='Read backend unavailable')

    def get_dispute_context(self, dispute_id):
        return self._read(dispute_id, lambda: context_from_rows(
            self.backend.get_dispute_context(dispute_id), dispute_id,
            captured_at=self.clock(), source_channel=self.source_channel))

    def get_dispute_state(self, dispute_id):
        def read():
            case = _case(self.backend.get_dispute_state(dispute_id), dispute_id)
            return ReadResult(status=ReadStatus.OK, message='Current source row retrieved; freshness unsupported',
                data=DisputeState(dispute=case, captured_at=self.clock(), source_channel=self.source_channel))
        return self._read(dispute_id, read)

    def get_customer_history(self, dispute_id):
        def read():
            raw = self.backend.get_customer_history(dispute_id)
            require(type(raw) is dict and set(raw) == {'dispute', 'anchor_transaction', 'history'}, 'Invalid history envelope')
            case = _case(raw['dispute'], dispute_id)
            anchor = _row(Transaction, raw['anchor_transaction'], source.TRANSACTION_COLUMNS)
            require(anchor.transaction_id == case.transaction_id, 'Invalid history anchor')
            if anchor.recorded_at > case.evaluation_at:
                raise source.ReadIncomplete('Visible primary transaction unavailable for history scope')
            require(type(raw['history']) is list, 'Invalid history collection')
            cases = []
            for item in raw['history']:
                require(type(item) is dict and set(item) == {'dispute', 'transaction'}, 'Invalid history row')
                old = HistoricalDispute(dispute=_row(Dispute, item['dispute'], source.DISPUTE_COLUMNS),
                    primary_transaction=_row(Transaction, item['transaction'], source.TRANSACTION_COLUMNS))
                require(old.primary_transaction.customer_id == anchor.customer_id, 'History outside customer scope')
                require(old.dispute.dispute_id != dispute_id, 'Current case returned as history')
                if old.dispute.opened_at <= case.evaluation_at and old.primary_transaction.recorded_at <= case.evaluation_at:
                    cases.append(old)
            history = CustomerHistory(dispute_id=dispute_id, customer_id=anchor.customer_id,
                snapshot_id=str(uuid4()), evaluation_at=case.evaluation_at, captured_at=self.clock(),
                source_channel=self.source_channel,
                cases=tuple(sorted(cases, key=lambda c: (c.dispute.opened_at, c.dispute.dispute_id))))
            return ReadResult(status=ReadStatus.OK, message='Source history retrieved; decisions unsupported', data=history)
        return self._read(dispute_id, read)

    def get_existing_decisions(self, dispute_id):
        return self._read(dispute_id, lambda: ReadResult(status=ReadStatus.UNSUPPORTED,
            message='Historical adapter has no decision projection; use the fresh snapshot adapter'))


TOOL_NAMES = ('get_dispute_context', 'get_customer_history', 'get_dispute_state', 'get_existing_decisions')


class ReadToolRegistry:
    """Construct in trusted application code for one authorized dispute.

    The model cannot choose a customer, cutoff, connection, path or SQL query.
    Tool dispatch grants no action/memory write capability.
    """
    def __init__(self, dispute_id, *, tools=None):
        source.validate_dispute_id(dispute_id)
        self.dispute_id = dispute_id
        tools = tools or ReadTools()
        self._handlers = {name: getattr(tools, name) for name in TOOL_NAMES}

    def definitions(self):
        return tuple({'name': name, 'parameters': {'type': 'object', 'properties': {
            'dispute_id': {'type': 'string', 'enum': [self.dispute_id]}},
            'required': ['dispute_id'], 'additionalProperties': False}} for name in TOOL_NAMES)

    def dispatch(self, name, arguments):
        if (type(name) is not str or name not in self._handlers or type(arguments) is not dict or
                set(arguments) != {'dispute_id'} or type(arguments['dispute_id']) is not str or
                arguments['dispute_id'] != self.dispute_id):
            return ReadResult(status=ReadStatus.INVALID_REQUEST, message='Tool or arguments outside allowed case scope')
        return self._handlers[name](self.dispute_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id')
    parser.add_argument('--tool', choices=TOOL_NAMES, default='get_dispute_context')
    args = parser.parse_args()
    try:
        registry = ReadToolRegistry(args.dispute_id)
    except ValueError:
        parser.error('Invalid dispute ID')
    result = registry.dispatch(args.tool, {'dispute_id': args.dispute_id})
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.status is ReadStatus.OK else 1


if __name__ == '__main__':
    raise SystemExit(main())
