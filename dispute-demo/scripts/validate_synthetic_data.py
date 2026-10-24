#!/usr/bin/env python3
"""Validate the synthetic files and scenario fixtures without running any agents."""
import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def instant(value):
    if not value.endswith('Z'):
        raise ValueError(f'Timestamp is not UTC: {value}')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(folder, fixtures=None):
    from generate_synthetic_data import FIELDS
    folder = Path(folder)
    tables, indexes = {}, {}
    for name, fields in FIELDS.items():
        if name == 'decisions':
            continue
        with (folder / f'{name}.csv').open(encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            require(reader.fieldnames == fields, f'{name}: unexpected column names or order')
            rows = list(reader)
        require(all(None not in row and None not in row.values() for row in rows), f'{name}: malformed row')
        ids = [row[fields[0]] for row in rows]
        require(all(ids) and len(set(ids)) == len(ids), f'{name}: missing or duplicated primary key')
        tables[name] = rows
        indexes[name] = dict(zip(ids, rows))
    txs, cases = indexes['transactions'], indexes['disputes']
    for tx in txs.values():
        require(int(tx['amount_minor']) > 0 and tx['currency'] == 'SGD', f'{tx["transaction_id"]}: invalid money')
        require(tx['transaction_status'] in ('authorized', 'captured', 'reversed', 'failed'), 'Invalid transaction status')
        require(instant(tx['recorded_at']) >= instant(tx['occurred_at']), 'Transaction recorded before event')
    for row in tables['settlements']:
        tx = txs.get(row['transaction_id'])
        require(tx is not None, f'{row["settlement_id"]}: missing parent transaction')
        require(int(row['amount_minor']) > 0 and row['currency'] == tx['currency'], 'Invalid settlement money')
        require(row['movement_type'] in ('capture', 'refund', 'reversal'), 'Invalid movement type')
        require(row['settlement_status'] in ('completed', 'pending', 'failed'), 'Invalid settlement status')
        require(instant(row['recorded_at']) >= instant(row['occurred_at']) >= instant(tx['occurred_at']), 'Invalid settlement chronology')
    versions = {}
    for row in tables['policy_rules']:
        period = (row['effective_from'], row['effective_to'])
        require(versions.setdefault(row['policy_version'], period) == period, 'Inconsistent policy period')
        require(int(row['priority']) > 0, 'Invalid rule priority')
        require(row['action'] in ('recommend_refund', 'reject', 'request_evidence', 'escalate'), 'Invalid policy action')
        require(isinstance(json.loads(row['parameters_json']), dict) and isinstance(json.loads(row['condition_json']), dict), 'Policy JSON must be objects')
    ordered = sorted(versions.values())
    for i, (start, end) in enumerate(ordered):
        require(not end or instant(end) > instant(start), 'Invalid policy period')
        if i + 1 < len(ordered):
            require(end and instant(end) <= instant(ordered[i + 1][0]), 'Policy versions overlap')
    selected_versions = {}
    for row in cases.values():
        did = row['dispute_id']
        require(row['transaction_id'] in txs, f'{did}: missing transaction')
        tx = txs[row['transaction_id']]
        require(row['currency'] == tx['currency'] and 0 < int(row['claimed_amount_minor']) <= int(tx['amount_minor']), f'{did}: invalid claim')
        require(row['reason_code'] in ('refund_missing', 'not_received', 'duplicate_charge'), f'{did}: invalid reason')
        opened, cutoff = instant(row['opened_at']), instant(row['evaluation_at'])
        require(instant(tx['recorded_at']) <= opened <= cutoff, f'{did}: invalid chronology')
        candidates = [version for version, (start, end) in versions.items() if instant(start) <= opened and (not end or opened < instant(end))]
        require(len(candidates) == 1, f'{did}: does not have exactly one policy version')
        selected_versions[did] = candidates[0]
        if row['reason_code'] == 'duplicate_charge':
            other = txs.get(row['related_transaction_id'])
            require(other is not None and other['transaction_id'] != tx['transaction_id'], f'{did}: missing companion charge')
            require(all(other[key] == tx[key] for key in ('order_id', 'merchant_id', 'customer_id', 'currency')), f'{did}: companion does not match order')
        else:
            require(not row['related_transaction_id'], f'{did}: unexpected companion charge')
    for row in tables['evidence']:
        eid, did = row['evidence_id'], row['dispute_id']
        require(did in cases, f'{eid}: missing dispute')
        require(row['evidence_type'] in ('receipt', 'delivery_record', 'refund_confirmation', 'merchant_response'), f'{eid}: invalid type')
        require(row['source_type'] in ('customer', 'merchant', 'carrier', 'payment_system'), f'{eid}: invalid source')
        require(row['integrity_status'] in ('valid', 'unreadable', 'incomplete'), f'{eid}: invalid integrity status')
        require(instant(row['available_at']) >= instant(row['event_at']), f'{eid}: invalid chronology')
        sid = row['related_settlement_id']
        if sid:
            require(sid in indexes['settlements'] and indexes['settlements'][sid]['transaction_id'] == cases[did]['transaction_id'], f'{eid}: bad settlement reference')
        require(row['document_path'] == f'evidence_documents/{eid}.txt', f'{eid}: unsafe document path')
        document = (folder / row['document_path']).read_text(encoding='utf-8')
        require('SYNTHETIC DEMONSTRATION DOCUMENT' in document and f'evidence_id: {eid}' in document and f'dispute_id: {did}' in document, f'{eid}: document does not match metadata')
        require(not any(word in document for word in ('expected_outcome', 'expected_refund_minor', 'scenario_id')), f'{eid}: answer leakage')
    manifest = json.loads((folder / 'generation_manifest.json').read_text())
    require(manifest['synthetic'] is True, 'Synthetic flag missing')
    require(manifest['dispute_count'] == len(cases), 'Dispute count mismatch')
    for name, rows in tables.items():
        require(manifest['row_counts'][name] == len(rows), f'{name}: row count mismatch')
    actual_paths = {str(path.relative_to(folder)) for path in folder.rglob('*') if path.is_file()}
    require(actual_paths == set(manifest['file_hashes']) | {'generation_manifest.json'}, 'Missing or extra files in generated input folder')
    for name, digest in manifest['file_hashes'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe manifest path')
        require(hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, f'File changed since generation: {name}')
    if fixtures is not None:
        require(len(fixtures) == len(cases) and {f['dispute_id'] for f in fixtures} == set(cases), 'Fixture coverage mismatch')
        for fixture in fixtures:
            did = fixture['dispute_id']
            case = cases[did]
            require(fixture['expected_policy_version'] == selected_versions[did], f'{did}: wrong fixture policy')
            require(fixture['expected_outcome'] in ('recommend_refund', 'reject', 'request_evidence', 'escalate'), f'{did}: invalid expected outcome')
            require(type(fixture['expected_refund_minor']) is int and fixture['expected_refund_minor'] >= 0, f'{did}: invalid expected amount')
            if fixture['expected_outcome'] != 'recommend_refund':
                require(fixture['expected_refund_minor'] == 0, f'{did}: non-refund outcome has money')
            for eid in fixture['required_evidence_ids']:
                item = indexes['evidence'].get(eid)
                require(item and item['dispute_id'] == did and instant(item['available_at']) <= instant(case['evaluation_at']), f'{did}: bad required evidence')
            for eid in fixture['forbidden_evidence_ids']:
                item = indexes['evidence'].get(eid)
                require(item and item['dispute_id'] == did and instant(item['available_at']) > instant(case['evaluation_at']), f'{did}: bad forbidden evidence')
            for rid in fixture['required_policy_rule_ids']:
                require(rid in indexes['policy_rules'] and indexes['policy_rules'][rid]['policy_version'] == selected_versions[did], f'{did}: bad required rule')
            # Independent settlement arithmetic verifies the proposed positive award.
            movements = [r for r in tables['settlements'] if r['transaction_id'] == case['transaction_id'] and r['settlement_status'] == 'completed' and instant(r['occurred_at']) <= instant(case['evaluation_at']) and instant(r['recorded_at']) <= instant(case['evaluation_at'])]
            balance = sum(int(r['amount_minor']) * (1 if r['movement_type'] == 'capture' else -1) for r in movements)
            if fixture['expected_outcome'] == 'recommend_refund':
                require(fixture['expected_refund_minor'] == min(int(case['claimed_amount_minor']), balance), f'{did}: wrong expected refund amount')
            scenario = fixture['scenario_id'].split(':')[0]
            if scenario != 'settlement_anomaly':
                require(balance >= 0, f'{did}: unplanned negative balance')
            if scenario == 'missing_evidence':
                usable = [r for r in tables['evidence'] if r['dispute_id'] == did and r['evidence_type'] == 'refund_confirmation' and instant(r['available_at']) <= instant(case['evaluation_at'])]
                require(not usable, f'{did}: missing-evidence scenario contains usable required evidence')
    return {name: len(rows) for name, rows in tables.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir', type=Path, default=ROOT / 'data/synthetic')
    p.add_argument('--fixtures', type=Path, default=ROOT / 'tests/fixtures/expected_results.json')
    args = p.parse_args()
    fixtures = json.loads(args.fixtures.read_text(encoding='utf-8'))
    try:
        counts = validate(args.data_dir, fixtures)
    except (ValueError, KeyError, OSError) as error:
        p.exit(1, f'VALIDATION FAILED: {error}\n')
    print('VALIDATION PASSED')
    for name, count in counts.items():
        print(f'  {name}: {count} rows')
    print('Keys, timestamps, policy coverage, documents, hashes and fixture references checked.')
    print('This validates the generated data, not agent decisions or Zetaris connectivity.')


if __name__ == '__main__':
    main()
