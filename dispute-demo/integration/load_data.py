#!/usr/bin/env python3
"""Preview SQL by default; --apply writes only to the separate dispute Postgres."""
import argparse
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_synthetic_data import FIELDS
from validate_synthetic_data import validate


def literal(text):
    return "'" + str(text).replace("'", "''") + "'"


def create_and_copy(table, fields, rows):
    definitions = []
    for i, field in enumerate(fields):
        # Store UTC timestamps as ISO text for predictable JDBC mapping across the two engines.
        # The fixed YYYY-MM-DDTHH:MM:SSZ format preserves chronological ordering.
        datatype = 'BIGINT' if field.endswith('_minor') or field == 'priority' else 'TEXT'
        constraint = ' PRIMARY KEY' if i == 0 else ''
        definitions.append(f'"{field}" {datatype}{constraint}')
    header = f'CREATE TABLE {table} (' + ', '.join(definitions) + ');\n'
    buf = io.StringIO(newline='')
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerows(rows)
    # CSV multiline values are handled by COPY; guard its special terminator.
    if any(line == '\\.' for line in buf.getvalue().splitlines()):
        raise ValueError('A field contains a COPY end marker; refusing unsafe import.')
    return header + f'COPY {table} FROM STDIN WITH (FORMAT CSV);\n' + buf.getvalue() + '\\.\n'


def make_sql(stage):
    # This is an initial loader, not a privileged reset path around T04 guards.
    preamble = """BEGIN;
DO $$ BEGIN
    IF to_regclass('dispute_control.source_revision') IS NOT NULL THEN
        RAISE EXCEPTION 'Guarded database: initial loader is disabled; use a coordinated source writer';
    END IF;
END $$;
"""
    if stage == 'probe':
        return preamble + create_and_copy('connection_probe', ['probe_id', 'message'], [['PROBE-001', 'Synthetic dispute database connected']]) + 'GRANT SELECT ON connection_probe TO dispute_reader;\nCOMMIT;\n'
    validate(ROOT / 'data/synthetic', json.loads((ROOT / 'tests/fixtures/expected_results.json').read_text()))
    sql = preamble
    names = ['transactions', 'settlements', 'disputes', 'evidence', 'policy_rules']
    for name in names:
        with (ROOT / f'data/synthetic/{name}.csv').open(encoding='utf-8', newline='') as file:
            rows = list(csv.reader(file))
        if rows.pop(0) != FIELDS[name]:
            raise ValueError(f'Unexpected columns in {name}')
        sql += create_and_copy(name, FIELDS[name], rows)
    with (ROOT / 'data/synthetic/evidence.csv').open(encoding='utf-8', newline='') as file:
        documents = [[r['evidence_id'], (ROOT / 'data/synthetic' / r['document_path']).read_text(encoding='utf-8')] for r in csv.DictReader(file)]
    sql += create_and_copy('evidence_documents', ['evidence_id', 'content'], documents)
    sql += 'ALTER TABLE settlements ADD FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id);\n'
    sql += 'ALTER TABLE disputes ADD FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id);\n'
    sql += 'ALTER TABLE evidence ADD FOREIGN KEY (dispute_id) REFERENCES disputes(dispute_id);\n'
    sql += 'ALTER TABLE evidence_documents ADD FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id);\n'
    sql += 'GRANT SELECT ON ' + ', '.join(names + ['evidence_documents']) + ' TO dispute_reader;\nCOMMIT;\n'
    return sql


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=['probe', 'full'])
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    sql = make_sql(args.stage)
    if not args.apply:
        print('-- PREVIEW ONLY. No Docker or database commands are executed.')
        print('-- Creates new tables; does not drop, truncate or replace existing tables.')
        print(sql)
        return
    command = ['docker', 'compose', '--env-file', str(ROOT / '.env.local'), '-f', str(ROOT / 'integration/compose.yml'),
               'exec', '-T', 'dispute-postgres', 'psql', '-U', 'dispute_loader', '-d', 'dispute_demo', '-v', 'ON_ERROR_STOP=1']
    subprocess.run(command, input=sql, text=True, check=True)
    print('Load completed. Existing tables cause a rollback rather than replacement.')


if __name__ == '__main__':
    main()
