"""Bounded analyst inventory through the same uncached Zetaris read channel.

This is display data, never a committable case snapshot or a model tool.
Queue membership comes exclusively from the persisted pending-review view.
"""
from datetime import datetime, timezone
from numbers import Integral

from app.schemas import currency_code, money, require, uuid_id
from . import get_dispute_context as source
from .fresh_reads import DirectReadChannel

CASE_COLUMNS = ('dispute_id', 'reason_code', 'claimed_amount_minor', 'currency', 'dispute_status')
QUEUE_COLUMNS = ('decision_id', 'status', 'dispute_id')


def read_inventory(*, channel_factory=source._ReadChannel):
    for _ in range(2):
        raw = None
        try:
            raw = channel_factory()
            channel = DirectReadChannel(raw)
            def revision():
                rows = source.records(channel, 'SELECT revision FROM dispute.dispute_source_revision', ('revision',))
                require(len(rows) == 1, 'Missing revision')
                value = rows[0]['revision']
                require(isinstance(value, Integral) and not isinstance(value, bool), 'Invalid revision')
                money(int(value))
                return int(value)
            before = revision()
            cases = source.records(channel, 'SELECT ' + ', '.join(CASE_COLUMNS) +
                ' FROM dispute.disputes ORDER BY dispute_id', CASE_COLUMNS)
            # Zetaris omits the UUID-typed ID in this existing view. Resolve its
            # textual ID through the registered history view on the same case
            # and commit instant. Independently read queue membership and require
            # a one-to-one match; lost joins/precision/ambiguity are unavailable,
            # never an empty queue or guessed ID. No schema/registration change.
            members = source.records(channel, 'SELECT dispute_id, status '
                'FROM dispute.dispute_pending_reviews ORDER BY dispute_id', ('dispute_id', 'status'))
            queue = source.records(channel, 'SELECT h.decision_id, q.status, q.dispute_id '
                'FROM dispute.dispute_pending_reviews q JOIN dispute.dispute_decision_history h '
                'ON q.dispute_id = h.dispute_id AND q.committed_at = h.committed_at '
                "WHERE h.outcome = 'human_review' ORDER BY q.dispute_id", QUEUE_COLUMNS)
            if revision() != before:
                continue
            seen, queued = set(), set()
            for row in cases:
                source.validate_dispute_id(row['dispute_id'])
                require(row['dispute_id'] not in seen, 'Duplicate case')
                seen.add(row['dispute_id'])
                require(row['reason_code'] in ('refund_missing', 'not_received', 'duplicate_charge'), 'Invalid reason')
                require(isinstance(row['claimed_amount_minor'], Integral) and
                        not isinstance(row['claimed_amount_minor'], bool), 'Invalid amount')
                row['claimed_amount_minor'] = int(row['claimed_amount_minor'])
                money(row['claimed_amount_minor'], minimum=1)
                currency_code(row['currency'])
                require(type(row['dispute_status']) is str and bool(row['dispute_status'].strip()), 'Invalid source status')
            for row in queue:
                uuid_id(row['decision_id'])
                require(row['status'] == 'queued' and row['dispute_id'] in seen and
                        row['dispute_id'] not in queued, 'Invalid persisted queue')
                queued.add(row['dispute_id'])
            require(len(members) == len(queue) and
                sorted((r['dispute_id'], r['status']) for r in members) ==
                sorted((r['dispute_id'], r['status']) for r in queue), 'Queue receipt join incomplete')
            return dict(cases=cases, queue=queue, source_revision=before,
                source_channel='zetaris', captured_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
        except source.SourceError:
            raise
        except Exception:
            raise source.ReadUnavailable('Analyst inventory unavailable') from None
        finally:
            if raw is not None:
                try:
                    raw.close()
                except Exception:
                    raise source.ReadUnavailable('Analyst connection did not close') from None
    raise source.ReadIncomplete('Inventory changed during bounded read attempts')
