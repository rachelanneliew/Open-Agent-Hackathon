"""Optional case-scoped USL inspection. No imports from the decision workflow.

This is not a FreshSnapshot. Static external records remain unverified for
freshness and cannot authorize any action. The public entry uses a bounded child.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from numbers import Integral
from pathlib import Path
import re
import selectors
import subprocess
import sys
import time

from .get_dispute_context import _ReadChannel, validate_dispute_id

MODEL = 'lightning.metastore.dispute_usl_v1.dispute_resolution_usl'
MAX_ROWS = 100
MAX_BYTES = 256 * 1024
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Case:
    dispute_id: str
    transaction_id: str
    customer_id: str
    claimed_amount_minor: int
    currency: str
    opened_at: str


@dataclass(frozen=True)
class MerchantEvidence:
    evidence_id: str
    dispute_id: str
    customer_id: str
    evidence_type: str
    integrity_status: str
    source_updated_at: str
    source_version: str


@dataclass(frozen=True)
class PriorCase:
    history_id: str
    current_dispute_id: str
    customer_id: str
    prior_dispute_id: str
    prior_outcome: str
    observed_at: str
    source_version: str


@dataclass(frozen=True)
class Preview:
    dispute_id: str
    status: str
    captured_at: str
    case: Case | None = None
    merchant_evidence: tuple[MerchantEvidence, ...] = ()
    prior_cases: tuple[PriorCase, ...] = ()
    issues: tuple[str, ...] = ()
    joined_counts: tuple[int, int] | None = None

    def to_dict(self):
        value = asdict(self)
        value.update(model=MODEL, model_revision=None, activation_timestamp=None,
            source_channel='zetaris_usl' if self.case else None,
            financial_action_authority=False, atomic_snapshot=False,
            freshness='unverified', native_dq='not_executed_by_preview',
            counts={'merchant_evidence':len(self.merchant_evidence), 'prior_cases':len(self.prior_cases)} if self.case else None,
            provenance={
                'case':'dispute PostgreSQL via dispute_case USL',
                'merchant_evidence':'dispute_merchant_v1 FileStore CSV via merchant_evidence USL',
                'prior_cases':'dispute_customer_v1 REST via prior_case USL',
                'ownership_check':'current dispute PostgreSQL primary transactions',
            } if self.case else {})
        return value


def _stamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _require(condition):
    if not condition:
        raise ValueError('unverified_source')


def _id(value, pattern):
    _require(type(value) is str and re.fullmatch(pattern, value) is not None)


def _timestamp(value, now):
    _id(value, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    _require(parsed <= now)
    return parsed


def _read_preview(dispute_id, *, channel_factory=_ReadChannel):
    """Worker/test boundary: only fixed SELECTs, with case input validated first."""
    validate_dispute_id(dispute_id)
    channel = None
    now = datetime.now(timezone.utc)
    try:
        channel = channel_factory()
        consumed = 0
        def rows(sql, width):
            nonlocal consumed
            values = channel.run(sql + f' LIMIT {MAX_ROWS + 1}', MAX_ROWS + 1).rows
            _require(type(values) in (list, tuple) and len(values) <= MAX_ROWS)
            for row in values:
                _require(type(row) in (list, tuple) and len(row) == width)
                for cell in row:
                    _require(cell is None or type(cell) is str or (isinstance(cell, Integral) and not isinstance(cell, bool)))
                    if type(cell) is str:
                        _require(len(cell) <= 256)
                consumed += len(json.dumps(list(row), default=int).encode())
                _require(consumed <= MAX_BYTES)
            return values
        # Compare USL fields with the current independently registered source.
        # A left join preserves missing ownership instead of hiding the bad row.
        case_rows = rows('SELECT c.dispute_id, c.transaction_id, c.customer_id, c.claimed_amount_minor, c.currency, c.opened_at, '
            'd.transaction_id, t.customer_id, d.claimed_amount_minor, d.currency, d.opened_at '
            f'FROM {MODEL}.dispute_case c LEFT JOIN dispute.disputes d ON d.dispute_id=c.dispute_id '
            'LEFT JOIN dispute.transactions t ON t.transaction_id=d.transaction_id '
            f"WHERE c.dispute_id='{dispute_id}'", 11)
        _require(len(case_rows) == 1)
        c = case_rows[0]
        _require(c[0] == dispute_id and tuple(c[1:6]) == tuple(c[6:11]))
        _id(c[1], r'TX-[0-9]{4}')
        _id(c[2], r'CUST-[0-9]{3}')
        _require(isinstance(c[3], Integral) and not isinstance(c[3], bool) and 0 <= c[3] <= 2**63-1 and c[4] == 'SGD')
        _timestamp(c[5], now)
        case = Case(c[0], c[1], c[2], int(c[3]), c[4], c[5])
        merchant_rows = rows('SELECT evidence_id, dispute_id, customer_id, evidence_type, integrity_status, source_updated_at, source_version '
            f"FROM {MODEL}.merchant_evidence WHERE dispute_id='{dispute_id}' ORDER BY evidence_id", 7)
        merchants, keys = [], set()
        for row in merchant_rows:
            _id(row[0], r'ME-[0-9]{4}')
            _require(row[0] not in keys and row[1] == dispute_id and row[2] == case.customer_id)
            keys.add(row[0])
            _require(row[3] in ('merchant_contact', 'refund_promise') and row[4] == 'received_unverified')
            _timestamp(row[5], now)
            _require(row[6] == 'merchant-v1')
            merchants.append(MerchantEvidence(*row))
        history_rows = rows('SELECT h.history_id, h.current_dispute_id, h.customer_id, h.prior_dispute_id, h.prior_outcome, '
            'h.observed_at, h.source_version, t.customer_id, p.opened_at '
            f'FROM {MODEL}.prior_case h LEFT JOIN dispute.disputes p ON p.dispute_id=h.prior_dispute_id '
            'LEFT JOIN dispute.transactions t ON t.transaction_id=p.transaction_id '
            f"WHERE h.current_dispute_id='{dispute_id}' ORDER BY h.history_id", 9)
        history, keys, prior_ids = [], set(), set()
        for row in history_rows:
            _id(row[0], r'CH-[0-9]{4}')
            validate_dispute_id(row[3])
            _require(row[0] not in keys and row[3] not in prior_ids and row[3] != dispute_id and
                row[1] == dispute_id and row[2] == case.customer_id == row[7])
            keys.add(row[0])
            prior_ids.add(row[3])
            observed = _timestamp(row[5], now)
            _require(_timestamp(row[8], now) <= observed and row[4] == 'unknown' and row[6] == 'customer-v1')
            history.append(PriorCase(*row[:7]))
        joined = rows('SELECT d.dispute_id, COUNT(DISTINCT e.evidence_id), COUNT(DISTINCT h.history_id) '
            f'FROM {MODEL}.dispute_case d LEFT JOIN {MODEL}.merchant_evidence e ON e.dispute_id=d.dispute_id '
            f'LEFT JOIN {MODEL}.prior_case h ON h.current_dispute_id=d.dispute_id '
            f"WHERE d.dispute_id='{dispute_id}' GROUP BY d.dispute_id", 3)
        _require(len(joined) == 1 and list(joined[0]) == [dispute_id, len(merchants), len(history)])
        issues = ['static_external_freshness_unverified', 'cross_source_atomicity_unverified',
                  'native_dq_not_executed_by_preview']
        if not merchants:
            issues.append('merchant_source_empty_for_case')
        if not history:
            issues.append('history_source_empty_for_case')
        result = Preview(dispute_id, 'unverified', _stamp(), case, tuple(merchants), tuple(history), tuple(issues),
                         (int(joined[0][1]), int(joined[0][2])))
    except Exception:
        result = Preview(dispute_id, 'unavailable', _stamp(), issues=('source_missing_malformed_or_unavailable',))
    finally:
        if channel is not None:
            try:
                channel.close()
            except Exception:
                result = Preview(dispute_id, 'unavailable', _stamp(), issues=('source_close_failed',))
    return result


def _bounded_worker(dispute_id, timeout_seconds):
    """Bound wall time and actual pipe bytes, including a malfunctioning child."""
    process = subprocess.Popen([sys.executable, '-m', 'integration.usl_reads', '--worker', dispute_id],
        cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    data = bytearray()
    deadline = time.monotonic() + timeout_seconds
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError()
                if not selector.select(remaining):
                    raise TimeoutError()
                chunk = process.stdout.read1(8192)
                if not chunk:
                    break
                data.extend(chunk)
                _require(len(data) <= MAX_BYTES)
        _require(process.wait(timeout=max(.01, deadline-time.monotonic())) == 0)
        return bytes(data)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        process.stdout.close()


def preview_case(dispute_id, *, enabled=False, timeout_seconds=180):
    """Public UI/CLI read. Disabled by default; never falls back to local data."""
    validate_dispute_id(dispute_id)
    _require(type(enabled) is bool and type(timeout_seconds) in (int, float) and 0 < timeout_seconds <= 240)
    if not enabled:
        return Preview(dispute_id, 'disabled', _stamp(), issues=('enable_usl_preview_explicitly',)).to_dict()
    try:
        raw = _bounded_worker(dispute_id, timeout_seconds)
        _require(len(raw) <= MAX_BYTES)
        value = json.loads(raw)
        _require(type(value) is dict and value['dispute_id'] == dispute_id and
            value['status'] in ('unavailable', 'unverified') and value['financial_action_authority'] is False and
            value['atomic_snapshot'] is False and value['model'] == MODEL)
        return value
    except (TimeoutError, subprocess.TimeoutExpired):
        return Preview(dispute_id, 'unavailable', _stamp(), issues=('preview_timeout',)).to_dict()
    except Exception:
        return Preview(dispute_id, 'unavailable', _stamp(), issues=('preview_unavailable',)).to_dict()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id')
    parser.add_argument('--enable', action='store_true')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        value = _read_preview(args.dispute_id).to_dict() if args.worker else preview_case(args.dispute_id, enabled=args.enable)
        print(json.dumps(value, allow_nan=False))
        raise SystemExit(1 if value['status'] == 'unavailable' else 0)
    except ValueError:
        parser.error('Expected a canonical dispute ID')
