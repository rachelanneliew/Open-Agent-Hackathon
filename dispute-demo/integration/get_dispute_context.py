#!/usr/bin/env python3
"""Read-only Zetaris JDBC retrieval. Never queries expected-result fixtures."""
import argparse
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / 'getting-started/scripts'))
import zetaris_sql as z


def records(channel, query, columns):
    result = channel.run(query, limit=1000)
    if any(len(row) != len(columns) for row in result.rows):
        raise ValueError('Unexpected Zetaris response column count')
    return [dict(zip(columns, row)) for row in result.rows]


def get_dispute_context(dispute_id):
    if not re.fullmatch(r'DP-\d{4}', dispute_id):
        raise ValueError('Expected a dispute ID such as DP-0014')
    z.load_env()
    channel = z.JdbcChannel()
    try:
        base = f" FROM dispute.disputes d WHERE d.dispute_id = '{dispute_id}'"
        cases = records(channel, 'SELECT d.dispute_id, d.transaction_id, d.related_transaction_id, d.reason_code, d.claimed_amount_minor, d.currency, d.customer_statement, d.opened_at, d.evaluation_at' + base,
                        ['dispute_id', 'transaction_id', 'related_transaction_id', 'reason_code', 'claimed_amount_minor', 'currency', 'customer_statement', 'opened_at', 'evaluation_at'])
        if len(cases) != 1:
            raise ValueError('Dispute was not found uniquely')
        tx = records(channel, f"SELECT t.transaction_id, t.order_id, t.customer_id, t.amount_minor, t.currency, t.occurred_at FROM dispute.transactions t JOIN dispute.disputes d ON (t.transaction_id = d.transaction_id OR t.transaction_id = d.related_transaction_id) WHERE d.dispute_id = '{dispute_id}' AND t.recorded_at <= d.evaluation_at",
                     ['transaction_id', 'order_id', 'customer_id', 'amount_minor', 'currency', 'occurred_at'])
        settlements = records(channel, f"SELECT s.settlement_id, s.transaction_id, s.movement_type, s.amount_minor, s.currency, s.settlement_status, s.occurred_at, s.recorded_at FROM dispute.settlements s JOIN dispute.disputes d ON (s.transaction_id = d.transaction_id OR s.transaction_id = d.related_transaction_id) WHERE d.dispute_id = '{dispute_id}' AND s.recorded_at <= d.evaluation_at AND s.occurred_at <= d.evaluation_at",
                              ['settlement_id', 'transaction_id', 'movement_type', 'amount_minor', 'currency', 'settlement_status', 'occurred_at', 'recorded_at'])
        evidence = records(channel, f"SELECT e.evidence_id, e.evidence_type, e.source_type, e.integrity_status, e.available_at, doc.content FROM dispute.evidence e JOIN dispute.disputes d ON e.dispute_id = d.dispute_id JOIN dispute.evidence_documents doc ON doc.evidence_id = e.evidence_id WHERE d.dispute_id = '{dispute_id}' AND e.available_at <= d.evaluation_at",
                           ['evidence_id', 'evidence_type', 'source_type', 'integrity_status', 'available_at', 'content'])
        rules = records(channel, f"SELECT p.policy_rule_id, p.policy_version, p.priority, p.condition_json, p.action, p.parameters_json FROM dispute.policy_rules p JOIN dispute.disputes d ON p.effective_from <= d.opened_at WHERE d.dispute_id = '{dispute_id}' AND (p.effective_to IS NULL OR p.effective_to > d.opened_at) AND (p.reason_code = 'ALL' OR p.reason_code = d.reason_code) ORDER BY p.priority",
                        ['policy_rule_id', 'policy_version', 'priority', 'condition_json', 'action', 'parameters_json'])
        return {'dispute': cases[0], 'transactions': tx, 'settlements': settlements, 'evidence': evidence, 'policy_rules': rules}
    finally:
        channel.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dispute_id')
    args = p.parse_args()
    print(json.dumps(get_dispute_context(args.dispute_id), indent=2, default=str))
