#!/usr/bin/env python3
"""Bounded, read-only Zetaris JDBC retrieval; no fixture or model access.

The dictionary API remains available for the prototypes. Canonical callers use
app.tools, which validates source rows, scope and visibility against T01 types.
"""
import argparse
from datetime import datetime
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
from types import SimpleNamespace

PROJECT = Path(__file__).resolve().parents[2]
MAX_ROWS = 1000
DISPUTE_COLUMNS = ('dispute_id', 'transaction_id', 'related_transaction_id',
                   'reason_code', 'claimed_amount_minor', 'currency',
                   'customer_statement', 'opened_at', 'evaluation_at', 'dispute_status')
TRANSACTION_COLUMNS = ('transaction_id', 'order_id', 'customer_id', 'merchant_id',
                       'amount_minor', 'currency', 'transaction_status', 'occurred_at', 'recorded_at')
SETTLEMENT_COLUMNS = ('settlement_id', 'transaction_id', 'movement_type', 'amount_minor',
                      'currency', 'settlement_status', 'occurred_at', 'recorded_at')
EVIDENCE_COLUMNS = ('evidence_id', 'dispute_id', 'related_settlement_id', 'evidence_type',
                    'source_type', 'integrity_status', 'event_at', 'available_at')
POLICY_COLUMNS = ('policy_rule_id', 'policy_version', 'priority', 'effective_from',
                  'effective_to', 'reason_code', 'condition_json', 'action',
                  'parameters_json', 'explanation')


class SourceError(ValueError):
    """Sanitized source failure; never contains SQL, configuration or raw errors."""


class CaseNotFound(SourceError):
    pass


class InvalidSource(SourceError):
    pass


class ReadUnavailable(SourceError):
    pass


class ReadIncomplete(SourceError):
    pass


def validate_dispute_id(dispute_id):
    if type(dispute_id) is not str or not re.fullmatch(r'DP-[0-9]{4}', dispute_id):
        raise ValueError('Expected a canonical dispute ID such as DP-0014')


@lru_cache(maxsize=1)
def _jdbc_helper():
    # Load the existing helper by its known repository path, without changing
    # sys.path or importing Java/reading private configuration on module import.
    path = PROJECT / 'getting-started/scripts/zetaris_sql.py'
    spec = importlib.util.spec_from_file_location('_dispute_zetaris_sql', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _ReadChannel:
    def __init__(self):
        helper = _jdbc_helper()
        helper.load_env()
        self.channel = helper.JdbcChannel()

    def run(self, query, limit):
        # JdbcChannel.run catches fetch errors and returns an empty Result.
        # Reuse its connection/cursor, but propagate fetch errors so failure
        # cannot masquerade as a missing case or empty history.
        cursor = self.channel._cur
        cursor.execute(query)
        return SimpleNamespace(rows=cursor.fetchmany(limit))

    def close(self):
        self.channel.close()


def records(channel, query, columns):
    try:
        result = channel.run(query + f' LIMIT {MAX_ROWS + 1}', limit=MAX_ROWS + 1)
    except Exception:
        raise ReadUnavailable('Zetaris read failed') from None
    if not hasattr(result, 'rows') or type(result.rows) not in (list, tuple):
        raise InvalidSource('Unexpected Zetaris response')
    if len(result.rows) > MAX_ROWS:
        raise ReadIncomplete('Source row limit exceeded; result is incomplete')
    if any(type(row) not in (list, tuple) or len(row) != len(columns) for row in result.rows):
        raise InvalidSource('Unexpected Zetaris response columns')
    return [dict(zip(columns, row)) for row in result.rows]


def _select(alias, columns):
    return ', '.join(f'{alias}.{name}' for name in columns)


def _time(value):
    # The loader stores UTC timestamps as text. Compare parsed instants so
    # optional fractional seconds cannot make lexicographic SQL ordering wrong.
    if type(value) is not str or not re.fullmatch(
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z', value):
        raise InvalidSource('Malformed source timestamp')
    try:
        return datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError:
        raise InvalidSource('Malformed source timestamp') from None


def _read_dispute(channel, dispute_id):
    rows = records(channel, f"SELECT {_select('d', DISPUTE_COLUMNS)} FROM dispute.disputes d "
                   f"WHERE d.dispute_id = '{dispute_id}'", DISPUTE_COLUMNS)
    if not rows:
        raise CaseNotFound('Dispute not found')
    if len(rows) != 1 or rows[0]['dispute_id'] != dispute_id:
        raise InvalidSource('Dispute identity is not unique')
    if _time(rows[0]['opened_at']) > _time(rows[0]['evaluation_at']):
        raise InvalidSource('Evaluation precedes dispute opening')
    return rows[0]


def _with_channel(dispute_id, reader, channel_factory):
    validate_dispute_id(dispute_id)
    channel = None
    try:
        try:
            channel = channel_factory()
        except Exception:
            raise ReadUnavailable('Zetaris connection unavailable') from None
        return reader(channel, _read_dispute(channel, dispute_id))
    finally:
        if channel is not None:
            try:
                channel.close()
            except Exception:
                raise ReadUnavailable('Zetaris connection did not close cleanly') from None


def get_dispute_state(dispute_id, *, channel_factory=_ReadChannel):
    """Read the source's current stored dispute row, not a commit-time lock."""
    return _with_channel(dispute_id, lambda channel, case: case, channel_factory)


def get_dispute_context(dispute_id, *, channel_factory=_ReadChannel):
    def read(channel, case):
        scope = f"d.dispute_id = '{dispute_id}'"
        linked = '(t.transaction_id = d.transaction_id OR t.transaction_id = d.related_transaction_id)'
        transactions = records(channel, f"SELECT {_select('t', TRANSACTION_COLUMNS)} "
            f'FROM dispute.transactions t JOIN dispute.disputes d ON {linked} '
            f'WHERE {scope}', TRANSACTION_COLUMNS)
        settlements = records(channel, f"SELECT {_select('s', SETTLEMENT_COLUMNS)} "
            'FROM dispute.settlements s JOIN dispute.disputes d ON '
            '(s.transaction_id = d.transaction_id OR s.transaction_id = d.related_transaction_id) '
            f'WHERE {scope}',
            SETTLEMENT_COLUMNS)
        evidence = records(channel, f"SELECT {_select('e', EVIDENCE_COLUMNS)}, doc.content "
            'FROM dispute.evidence e JOIN dispute.disputes d ON e.dispute_id = d.dispute_id '
            'LEFT JOIN dispute.evidence_documents doc ON doc.evidence_id = e.evidence_id '
            f'WHERE {scope}', (*EVIDENCE_COLUMNS, 'content'))
        rules = records(channel, f"SELECT {_select('p', POLICY_COLUMNS)} "
            'FROM dispute.policy_rules p JOIN dispute.disputes d ON '
            "(p.reason_code = 'ALL' OR p.reason_code = d.reason_code) "
            f'WHERE {scope} ORDER BY p.priority', POLICY_COLUMNS)
        cutoff, opened = _time(case['evaluation_at']), _time(case['opened_at'])
        transactions = [t for t in transactions if _time(t['recorded_at']) <= cutoff]
        settlements = [s for s in settlements if _time(s['recorded_at']) <= cutoff and _time(s['occurred_at']) <= cutoff]
        evidence = [e for e in evidence if _time(e['available_at']) <= cutoff]
        rules = [p for p in rules if _time(p['effective_from']) <= opened and
                 (p['effective_to'] is None or p['effective_to'] == '' or opened < _time(p['effective_to']))]
        return {'dispute': case, 'transactions': transactions, 'settlements': settlements,
                'evidence': evidence, 'policy_rules': rules}
    return _with_channel(dispute_id, read, channel_factory)


def get_customer_history(dispute_id, *, channel_factory=_ReadChannel):
    """Resolve ownership from the current primary transaction, never memory tags.

    Return only source dispute/primary-transaction rows. Stored outcomes and
    decisions do not exist yet and are not inferred from source dispute status.
    """
    def read(channel, case):
        anchors = records(channel, f"SELECT {_select('t', TRANSACTION_COLUMNS)} "
            'FROM dispute.transactions t JOIN dispute.disputes d ON t.transaction_id = d.transaction_id '
            f"WHERE d.dispute_id = '{dispute_id}'", TRANSACTION_COLUMNS)
        if not anchors:
            raise ReadIncomplete('Visible primary transaction unavailable for history scope')
        if len(anchors) != 1:
            raise InvalidSource('Primary transaction is not unique')
        cutoff = _time(case['evaluation_at'])
        if _time(anchors[0]['recorded_at']) > cutoff:
            raise ReadIncomplete('Visible primary transaction unavailable for history scope')
        # All interpolated input is the validated dispute ID. Customer and cutoff
        # come from source joins; neither is supplied by the model.
        columns = tuple('dispute_' + c for c in DISPUTE_COLUMNS) + tuple('transaction_' + c for c in TRANSACTION_COLUMNS)
        rows = records(channel, f"SELECT {_select('h', DISPUTE_COLUMNS)}, {_select('t', TRANSACTION_COLUMNS)} "
            'FROM dispute.disputes h JOIN dispute.transactions t ON t.transaction_id = h.transaction_id '
            'JOIN dispute.transactions current_t ON current_t.customer_id = t.customer_id '
            'JOIN dispute.disputes d ON d.transaction_id = current_t.transaction_id '
            f"WHERE d.dispute_id = '{dispute_id}' AND h.dispute_id <> d.dispute_id "
            'ORDER BY h.opened_at, h.dispute_id', columns)
        rows = [r for r in rows if _time(r['dispute_opened_at']) <= cutoff and
                _time(r['transaction_recorded_at']) <= cutoff]
        return {'dispute': case, 'anchor_transaction': anchors[0], 'history': [
            {'dispute': {c: row['dispute_' + c] for c in DISPUTE_COLUMNS},
             'transaction': {c: row['transaction_' + c] for c in TRANSACTION_COLUMNS}} for row in rows]}
    return _with_channel(dispute_id, read, channel_factory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id')
    args = parser.parse_args()
    try:
        print(json.dumps(get_dispute_context(args.dispute_id), indent=2, default=str))
    except ValueError as error:
        parser.exit(1, str(error) + '\n')
