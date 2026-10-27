"""Read-only development verifier: exact raw/USL parity, identities and joins.

No model or action calls. Run after setup: python -m integration.usl.verify_live.
Output is sanitized evidence, not a freshness or business-quality certificate.
"""
from datetime import datetime, timezone
import json

from integration.get_dispute_context import _ReadChannel

MODEL = 'lightning.metastore.dispute_usl_v1.dispute_resolution_usl'
CASE = ('dispute_id', 'transaction_id', 'customer_id', 'claimed_amount_minor', 'currency', 'opened_at')
MERCHANT = ('evidence_id', 'dispute_id', 'customer_id', 'evidence_type', 'integrity_status', 'source_updated_at', 'source_version')
HISTORY = ('history_id', 'current_dispute_id', 'customer_id', 'prior_dispute_id', 'prior_outcome', 'observed_at', 'source_version')


def verify():
    channel = _ReadChannel()
    def rows(query):
        values = channel.run(query, 1001).rows
        if len(values) > 1000:
            raise ValueError('overflow')
        return [list(row) for row in values]
    try:
        definitions = rows('LOAD USL dispute_resolution_usl NAMESPACE lightning.metastore.dispute_usl_v1')
        queries = {
            'dispute_case': ('SELECT d.dispute_id, d.transaction_id, t.customer_id, d.claimed_amount_minor, d.currency, d.opened_at '
                'FROM dispute.disputes d JOIN dispute.transactions t ON t.transaction_id=d.transaction_id', CASE),
            'merchant_evidence': ('SELECT ' + ', '.join(MERCHANT) + ' FROM dispute_merchant_v1.evidence', MERCHANT),
            'prior_case': ('SELECT ' + ', '.join('h.' + c for c in HISTORY) +
                ' FROM dispute_customer_v1.history_raw LATERAL VIEW explode(history) AS h', HISTORY),
        }
        results = {}
        for table, (query, columns) in queries.items():
            raw = rows(query + ' LIMIT 1001')
            usl = rows('SELECT ' + ', '.join(columns) + f' FROM {MODEL}.{table} LIMIT 1001')
            if not raw or sorted(raw) != sorted(usl) or len({r[0] for r in usl}) != len(usl):
                raise ValueError('parity_or_identity')
            results[table] = dict(count=len(usl), rows=[dict(zip(columns, row)) for row in usl])
        cases = {r['dispute_id']:r for r in results['dispute_case']['rows']}
        for row in results['merchant_evidence']['rows']:
            if cases[row['dispute_id']]['customer_id'] != row['customer_id']:
                raise ValueError('ownership')
        for row in results['prior_case']['rows']:
            if (row['current_dispute_id'] == row['prior_dispute_id'] or
                cases[row['current_dispute_id']]['customer_id'] != row['customer_id'] or
                cases[row['prior_dispute_id']]['customer_id'] != row['customer_id']):
                raise ValueError('ownership')
        joined = rows(f"SELECT d.dispute_id, d.claimed_amount_minor, COUNT(DISTINCT e.evidence_id), COUNT(DISTINCT h.history_id) "
            f'FROM {MODEL}.dispute_case d LEFT JOIN {MODEL}.merchant_evidence e ON e.dispute_id=d.dispute_id '
            f'LEFT JOIN {MODEL}.prior_case h ON h.current_dispute_id=d.dispute_id '
            "WHERE d.dispute_id='DP-0020' GROUP BY d.dispute_id, d.claimed_amount_minor")
        if joined != [['DP-0020', 11400, 2, 2]]:
            raise ValueError('joined_counts')
        return dict(status='passed', evidence_category='live_zetaris', captured_at=datetime.now(timezone.utc).isoformat(),
            model=MODEL, definition=json.loads(definitions[0][0]), sources=results, dp0020_join=joined,
            ownership='matched_for_all_fixture_rows', source_to_usl_parity='exact',
            atomic_snapshot=False, financial_action_called=False)
    finally:
        channel.close()


if __name__ == '__main__':
    try:
        print(json.dumps(verify(), indent=2))
    except Exception:
        print('{"status":"failed","error":"live_usl_verification_unavailable"}')
        raise SystemExit(1)
