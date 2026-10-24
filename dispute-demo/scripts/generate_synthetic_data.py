#!/usr/bin/env python3
"""Generate fictional dispute inputs and independent scenario fixtures. No services required."""
import argparse
import csv
import hashlib
import json
import random
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'
BOUNDARY = datetime(2026, 10, 1, tzinfo=timezone.utc)
FIELDS = {
    'transactions': ['transaction_id', 'order_id', 'customer_id', 'merchant_id', 'amount_minor', 'currency', 'transaction_status', 'occurred_at', 'recorded_at'],
    'settlements': ['settlement_id', 'transaction_id', 'movement_type', 'amount_minor', 'currency', 'settlement_status', 'occurred_at', 'recorded_at'],
    'disputes': ['dispute_id', 'transaction_id', 'related_transaction_id', 'reason_code', 'claimed_amount_minor', 'currency', 'customer_statement', 'opened_at', 'evaluation_at', 'dispute_status'],
    'evidence': ['evidence_id', 'dispute_id', 'related_settlement_id', 'evidence_type', 'source_type', 'document_path', 'event_at', 'available_at', 'integrity_status'],
    'policy_rules': ['policy_rule_id', 'rule_code', 'policy_version', 'effective_from', 'effective_to', 'reason_code', 'priority', 'condition_json', 'action', 'parameters_json', 'explanation'],
    'decisions': ['decision_id', 'run_id', 'dispute_id', 'revision', 'supersedes_decision_id', 'policy_version', 'outcome', 'recommended_refund_minor', 'currency', 'reason_codes_json', 'evidence_ids_json', 'policy_rule_ids_json', 'rationale', 'validation_status', 'created_at'],
}
BASE_COUNTS = {'supported': 8, 'full_refund': 5, 'partial_refund': 5, 'missing_evidence': 5, 'conflicting_evidence': 5, 'outside_window': 4, 'policy_pair': 4, 'settlement_anomaly': 4}


def stamp(value):
    return value.isoformat(timespec='seconds').replace('+00:00', 'Z')


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def allocation(count):
    if count == 40:
        return BASE_COUNTS.copy()
    # Preserve both policy pairs and four distinct settlement anomalies at every size.
    result = {key: (4 if key in ('policy_pair', 'settlement_anomaly') else 1) for key in BASE_COUNTS}
    while sum(result.values()) < count:
        key = max((k for k in result if k not in ('policy_pair', 'settlement_anomaly')),
                  key=lambda k: (BASE_COUNTS[k] * count / 40 - result[k], -list(result).index(k)))
        result[key] += 1
    return result


def policy_rows():
    definitions = [
        ('DATA_INTEGRITY', 10, 'data_integrity_or_pending', 'escalate', {}, 'Escalate missing or inconsistent capture data, negative balance, currency mismatch, or a pending movement.'),
        ('FILING_WINDOW', 20, 'filing_window_exceeded', 'reject', {}, 'Reject filing later than the allowed elapsed days. Exactly the limit remains eligible.'),
        ('ALREADY_REFUNDED', 30, 'remaining_balance_zero', 'reject', {}, 'Reject an additional refund when the validated remaining balance is zero.'),
        ('CONFLICTING_EVIDENCE', 40, 'material_evidence_conflict', 'escalate', {}, 'Escalate unresolved material contradictions. A full refund promise and a partial actual refund are compatible.'),
        ('MISSING_EVIDENCE', 50, 'required_evidence_missing', 'request_evidence', {
            'refund_missing': ['refund_confirmation'], 'not_received': ['receipt', 'delivery_record'],
            'duplicate_charge': ['receipt', 'two_completed_captures_same_order']}, 'Request required evidence that is missing, unusable or unavailable at the evaluation cutoff.'),
        ('UNSUPPORTED', 60, 'claim_not_supported', 'reject', {}, 'Reject a claim contradicted by complete, unambiguous evidence; conflicts have already been escalated.'),
        ('REVIEW_THRESHOLD', 70, 'proposed_refund_above_limit', 'escalate', {'review_threshold_minor': 20000}, 'Escalate an otherwise eligible refund above 20000 SGD cents; exactly 20000 is allowed.'),
        ('APPROVE', 80, 'all_preceding_checks_pass', 'recommend_refund', {}, 'Recommend min(claimed amount, completed captures minus completed refunds and reversals).'),
    ]
    rows = []
    for version, days, start, end in [('v1', 30, '2026-01-01T00:00:00Z', stamp(BOUNDARY)), ('v2', 45, stamp(BOUNDARY), '')]:
        for code, priority, predicate, action, params, explanation in definitions:
            parameters = {'filing_window_days': days} if code == 'FILING_WINDOW' else params
            rows.append(dict(zip(FIELDS['policy_rules'], [f'{version}-{code}', code, version, start, end, 'ALL', priority,
                         json.dumps({'predicate': predicate}, sort_keys=True), action, json.dumps(parameters, sort_keys=True), explanation])))
    return rows


def generate(seed, reference_date, count, output):
    """All expected results below are authored by scenario, not computed by an agent."""
    rng = random.Random(seed)
    data = {name: [] for name in FIELDS if name != 'decisions'}
    data['policy_rules'] = policy_rows()
    fixtures = []
    documents = {}
    reference = datetime.strptime(reference_date, '%Y-%m-%d').replace(hour=9, tzinfo=timezone.utc)
    if reference.date() < datetime(2026, 10, 10).date() or reference.year != 2026:
        raise ValueError('Use a reference date in 2026 on or after 2026-10-10 for these fixed policy-boundary scenarios.')

    def movement(txid, kind, amount, status, event):
        sid = f'ST-{len(data["settlements"]) + 1:04d}'
        data['settlements'].append(dict(zip(FIELDS['settlements'], [sid, txid, kind, amount, 'SGD', status, stamp(event), stamp(event + timedelta(minutes=1))])))
        return sid

    index = 0
    for scenario, quota in allocation(count).items():
        for variant in range(quota):
            index += 1
            did, txid, order = f'DP-{index:04d}', f'TX-{index:04d}', f'OR-{index:04d}'
            amount = rng.randrange(50, 176) * 100
            opened = reference - timedelta(days=5 + index % 4)
            age = timedelta(days=10)
            reason = 'refund_missing'
            if scenario == 'supported':
                reason = ['refund_missing', 'not_received', 'duplicate_charge'][variant % 3]
                if variant == 0:  # exactly 30 days under v1
                    opened, age = BOUNDARY - timedelta(seconds=1), timedelta(days=30)
                elif variant == 1:  # exactly 45 days under v2
                    age = timedelta(days=45)
                elif variant == 2:
                    amount = 20000
                elif variant == 7:
                    amount = 25000
            if scenario == 'outside_window':
                if variant % 2 == 0:
                    opened, age = BOUNDARY - timedelta(seconds=1), timedelta(days=30, seconds=1)
                else:
                    age = timedelta(days=45, seconds=1)
            if scenario == 'policy_pair':
                opened = BOUNDARY - timedelta(seconds=1) if variant % 2 == 0 else BOUNDARY
                age, amount = timedelta(days=35), 10000 + (variant // 2) * 2000
            if scenario == 'partial_refund':
                amount = 10000 if variant == 0 else amount
            if scenario == 'conflicting_evidence':
                reason = 'not_received'
            tx_time, cutoff = opened - age, opened + timedelta(days=1)
            version = 'v1' if opened < BOUNDARY else 'v2'
            customer, merchant = f'CUST-{rng.randrange(1, 16):03d}', f'MER-{rng.randrange(1, 5):03d}'
            data['transactions'].append(dict(zip(FIELDS['transactions'], [txid, order, customer, merchant, amount, 'SGD', 'captured', stamp(tx_time), stamp(tx_time + timedelta(minutes=1))])))
            cap_status = 'pending' if scenario == 'settlement_anomaly' and variant == 1 else 'completed'
            cap_amount = amount - 100 if scenario == 'settlement_anomaly' and variant == 3 else amount
            capture_id = movement(txid, 'capture', cap_amount, cap_status, tx_time + timedelta(hours=1))
            related_tx, refund_id = '', ''
            refund = 0
            if reason == 'duplicate_charge':
                related_tx = f'TX-{count + index:04d}'
                data['transactions'].append(dict(zip(FIELDS['transactions'], [related_tx, order, customer, merchant, amount, 'SGD', 'captured', stamp(tx_time + timedelta(minutes=2)), stamp(tx_time + timedelta(minutes=3))])))
                movement(related_tx, 'capture', amount, 'completed', tx_time + timedelta(hours=2))
            if scenario in ('full_refund', 'partial_refund'):
                refund = amount if scenario == 'full_refund' else amount * 40 // 100
                refund_id = movement(txid, 'refund', refund, 'completed', opened - timedelta(days=2))
            if scenario == 'settlement_anomaly' and variant in (0, 2):
                refund_id = movement(txid, 'refund', amount if variant == 0 else amount + 100, 'pending' if variant == 0 else 'completed', opened - timedelta(days=2))
            statement = {'refund_missing': 'The merchant promised a full refund. Please check whether the payment has returned.',
                         'not_received': 'I paid for this order, but it has not arrived.',
                         'duplicate_charge': 'I see two charges for one order. Please investigate the extra charge.'}[reason]
            data['disputes'].append(dict(zip(FIELDS['disputes'], [did, txid, related_tx, reason, amount, 'SGD', statement, stamp(opened), stamp(cutoff), 'open'])))
            case_evidence, forbidden = [], []

            def evidence(kind, source, body, *, related='', late=False):
                eid = f'EV-{len(data["evidence"]) + 1:04d}'
                event = tx_time if kind == 'receipt' else opened - timedelta(days=1)
                available = cutoff + timedelta(days=1) if late else event + timedelta(hours=1)
                path = f'evidence_documents/{eid}.txt'
                data['evidence'].append(dict(zip(FIELDS['evidence'], [eid, did, related, kind, source, path, stamp(event), stamp(available), 'valid'])))
                documents[path] = '\n'.join(['SYNTHETIC DEMONSTRATION DOCUMENT', 'All entities and events are fictional.', f'evidence_id: {eid}', f'dispute_id: {did}', f'transaction_id: {txid}', f'order_id: {order}', f'document_type: {kind}', f'source_type: {source}', f'event_at: {stamp(event)}', f'available_at: {stamp(available)}', '', body, ''])
                (forbidden if late else case_evidence).append(eid)
                return eid

            receipt = evidence('receipt', 'merchant', f'One order was purchased for SGD {amount // 100}.{amount % 100:02d}. Customer reference {customer}.')
            if reason == 'not_received':
                evidence('delivery_record', 'carrier', 'Carrier record: parcel was lost in transit and has not been delivered.')
                if scenario == 'conflicting_evidence':
                    evidence('delivery_record', 'carrier', 'Carrier record for the same order: delivery completed and signed for by the customer.')
            elif reason == 'refund_missing':
                if scenario != 'missing_evidence' or variant == 0:
                    evidence('refund_confirmation', 'merchant', f'The merchant committed to refund the full SGD {amount // 100}.{amount % 100:02d}. This commitment is not confirmation that the payment movement has completed.', related=refund_id, late=scenario == 'missing_evidence')
            else:
                evidence('merchant_response', 'merchant', f'There was only one order. Charge references {txid} and {related_tx} refer to that same order, not separate purchases.')

            # Independent fixture templates: do not call a production rule evaluator here.
            outcome, expected, code, rule = 'recommend_refund', amount, 'SUPPORTED_CLAIM', 'APPROVE'
            if scenario == 'full_refund':
                outcome, expected, code, rule = 'reject', 0, 'ALREADY_REFUNDED', 'ALREADY_REFUNDED'
            elif scenario == 'partial_refund':
                expected, code = amount - refund, 'PARTIAL_REFUND_OUTSTANDING'
            elif scenario == 'missing_evidence':
                outcome, expected, code, rule = 'request_evidence', 0, 'MISSING_EVIDENCE', 'MISSING_EVIDENCE'
            elif scenario == 'conflicting_evidence':
                outcome, expected, code, rule = 'escalate', 0, 'CONFLICTING_EVIDENCE', 'CONFLICTING_EVIDENCE'
            elif scenario == 'outside_window' or (scenario == 'policy_pair' and variant % 2 == 0):
                outcome, expected, code, rule = 'reject', 0, 'OUT_OF_WINDOW', 'FILING_WINDOW'
            elif scenario == 'settlement_anomaly':
                outcome, expected, code, rule = 'escalate', 0, 'DATA_INTEGRITY', 'DATA_INTEGRITY'
            elif scenario == 'supported' and variant == 7:
                outcome, expected, code, rule = 'escalate', 0, 'REVIEW_THRESHOLD', 'REVIEW_THRESHOLD'
            required = case_evidence if scenario in ('supported', 'partial_refund', 'conflicting_evidence', 'policy_pair') and outcome != 'reject' else []
            fixtures.append({'dispute_id': did, 'scenario_id': f'{scenario}:{variant + 1}', 'expected_policy_version': version,
                             'expected_outcome': outcome, 'expected_refund_minor': expected, 'required_reason_codes': [code],
                             'required_evidence_ids': required, 'forbidden_evidence_ids': forbidden,
                             'required_policy_rule_ids': list(dict.fromkeys([f'{version}-{rule}'] + ([] if rule == 'DATA_INTEGRITY' else [f'{version}-FILING_WINDOW'])))})

    for name, rows in data.items():
        with (output / f'{name}.csv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS[name], lineterminator='\n')
            writer.writeheader()
            writer.writerows(sorted(rows, key=lambda row: row[FIELDS[name][0]]))
    for name, body in documents.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf-8', newline='\n')
    hashes = {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(output.rglob('*')) if path.is_file()}
    write_json(output / 'generation_manifest.json', {'dataset_id': 'synthetic_disputes_v1', 'seed': seed, 'reference_date': reference_date,
               'dispute_count': count, 'currency': 'SGD', 'generator_version': VERSION, 'runtime_version': sys.version.split()[0],
               'schema_version': '1.0.0', 'row_counts': {name: len(rows) for name, rows in data.items()}, 'file_hashes': hashes, 'synthetic': True})
    return fixtures, data['policy_rules']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seed', type=int, default=2026)
    p.add_argument('--reference-date', default='2026-10-20')
    p.add_argument('--disputes', type=int, default=40)
    p.add_argument('--out', type=Path, default=ROOT / 'data/synthetic')
    p.add_argument('--fixtures-out', type=Path, default=ROOT / 'tests/fixtures/expected_results.json')
    p.add_argument('--policies-out', type=Path, default=ROOT / 'policies')
    p.add_argument('--overwrite', action='store_true')
    args = p.parse_args()
    if not 20 <= args.disputes <= 50:
        p.error('--disputes must be between 20 and 50')
    target = args.out.resolve()
    if target.exists() and not args.overwrite:
        p.error(f'Output already exists: {target}. Choose a new --out directory or use --overwrite.')
    if target.exists():
        manifest_path = target / 'generation_manifest.json'
        if not manifest_path.is_file() or json.loads(manifest_path.read_text()).get('dataset_id') != 'synthetic_disputes_v1':
            p.error('Refusing to replace a directory not identified as this generated dataset.')
        expected_files = set(json.loads(manifest_path.read_text())['file_hashes']) | {'generation_manifest.json'}
        actual_files = {str(f.relative_to(target)) for f in target.rglob('*') if f.is_file()}
        if actual_files != expected_files:
            p.error('Output folder contains added or missing files. Use a fresh --out directory to preserve your work.')
    if (args.fixtures_out.exists() or any((args.policies_out / f'synthetic_policy_{v}.md').exists() for v in ('v1', 'v2'))) and not args.overwrite:
        p.error('Fixtures or policy files already exist. Select fresh destinations or use --overwrite.')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.dispute-build-', dir=target.parent) as temp:
        staging = Path(temp) / 'synthetic'
        staging.mkdir()
        fixtures, rules = generate(args.seed, args.reference_date, args.disputes, staging)
        from validate_synthetic_data import validate
        validate(staging, fixtures)
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(staging), str(target))
    write_json(args.fixtures_out, fixtures)
    args.policies_out.mkdir(parents=True, exist_ok=True)
    for version in ('v1', 'v2'):
        subset = [r for r in rules if r['policy_version'] == version]
        text = f'# Synthetic policy {version}\n\nFictional demonstration policy. Not payment-network or legal guidance.\n\n'
        text += f'Effective from {subset[0]["effective_from"]} (inclusive) to {subset[0]["effective_to"] or "no end"} (exclusive if present). Select by dispute opened_at.\n\n'
        text += 'Evaluate in ascending priority. The first applicable terminal action wins. Only use records visible at evaluation_at. Non-refund outcomes have amount zero.\n\n'
        for row in subset:
            text += f'## {row["priority"]}. {row["rule_code"]}\n\n{row["explanation"]}\n\nAction: {row["action"]}. Parameters: `{row["parameters_json"]}`.\n\n'
        (args.policies_out / f'synthetic_policy_{version}.md').write_text(text, encoding='utf-8', newline='\n')
    print(f'Created and validated {args.disputes} disputes in {target}')
    print(f'Independent scenario fixtures: {args.fixtures_out.resolve()}')
    print('Decisions are not pre-generated. Agents must create their own outputs.')


if __name__ == '__main__':
    main()
