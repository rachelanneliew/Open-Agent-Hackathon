"""Fresh, coherent reads through the existing approved Zetaris JDBC channel.

Migration 002 builds each case bundle in one PostgreSQL statement snapshot.
Never return a revision for independently cached source rows. Every SELECT must
have a verified direct JDBC scan plan, a current source-side clock, and matching
before/bundle/after revisions. Unknown plans/caches/overflow fail closed.
"""
from datetime import datetime, timezone
import json
from numbers import Integral

from . import get_dispute_context as source

MAX_BUNDLE_BYTES = 2 * 1024 * 1024


def _json(text):
    def pairs(items):
        if len(dict(items)) != len(items):
            raise ValueError('Duplicate keys')
        return dict(items)
    def constant(_):
        raise ValueError('Nonfinite value')
    if type(text) is not str or len(text.encode()) > MAX_BUNDLE_BYTES:
        raise source.ReadIncomplete('Source bundle too large')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


class DirectReadChannel:
    """Application-owned constants only; never exposes EXPLAIN/SQL to a model."""
    def __init__(self, channel):
        self.channel = channel

    def run(self, query, limit):
        if not query.startswith('SELECT '):
            raise source.ReadUnavailable('Only approved SELECTs are supported')
        plan_rows = self.channel.run('EXPLAIN ' + query, 100).rows
        plan = '\n'.join(str(column) for row in plan_rows for column in row)
        scans = [line for line in plan.splitlines() if 'Scan ' in line]
        if (not scans or any('Scan InsertableJDBCTableRelation(' not in line for line in scans)
                or any(marker in plan for marker in ('InMemory', 'Cached', 'LocalTableScan'))
                or any('DISPUTE.' not in line for line in scans)):
            raise source.ReadUnavailable('Uncached source scan could not be verified')
        return self.channel.run(query, limit)


def read_bundle(dispute_id, *, channel_factory=source._ReadChannel, clock=None, attempts=2):
    source.validate_dispute_id(dispute_id)
    if type(attempts) is not int or not 1 <= attempts <= 2:
        raise source.ReadUnavailable('Invalid read retry budget')
    clock = clock or (lambda: datetime.now(timezone.utc))
    for _ in range(attempts):
        raw_channel = None
        try:
            started = clock()
            raw_channel = channel_factory()
            channel = DirectReadChannel(raw_channel)
            def revision():
                rows = source.records(channel, 'SELECT revision FROM dispute.dispute_source_revision', ('revision',))
                if len(rows) != 1:
                    raise source.InvalidSource('Source revision missing')
                value = rows[0]['revision']
                if not isinstance(value, Integral) or isinstance(value, bool) or not 0 <= value <= 2**63 - 1:
                    raise source.InvalidSource('Invalid source revision')
                return int(value)
            before = revision()
            rows = source.records(channel, "SELECT payload FROM dispute.dispute_read_bundle "
                                  f"WHERE dispute_id = '{dispute_id}'", ('payload',))
            after = revision()
            if before != after:
                continue
            if not rows:
                raise source.CaseNotFound('Dispute not found')
            if len(rows) != 1:
                raise source.InvalidSource('Duplicate case bundle')
            bundle = _json(rows[0]['payload'])
            if (type(bundle) is not dict or set(bundle) != {'schema_version', 'source_revision',
                    'evaluation_at', 'context', 'history', 'decisions'} or
                    type(bundle['schema_version']) is not int or bundle['schema_version'] != 1 or
                    type(bundle['source_revision']) is not int or bundle['source_revision'] != before):
                raise source.InvalidSource('Invalid coherent read envelope')
            cutoff, captured = source._time(bundle['evaluation_at']), clock()
            if not started <= cutoff <= captured:
                raise source.ReadUnavailable('Source clock is stale or inconsistent')
            raw = bundle['context']
            if type(raw) is not dict or set(raw) != {'dispute', 'transactions', 'settlements', 'evidence', 'policy_rules'}:
                raise source.InvalidSource('Invalid source context')
            if (type(raw['dispute']) is not dict or raw['dispute'].get('dispute_id') != dispute_id
                    or raw['dispute'].get('evaluation_at') != bundle['evaluation_at']):
                raise source.InvalidSource('Source identity or cutoff mismatch')
            for collection in [raw[name] for name in ('transactions', 'settlements', 'evidence', 'policy_rules')] + [bundle['history'], bundle['decisions']]:
                if type(collection) is not list:
                    raise source.InvalidSource('Invalid source collection')
                if len(collection) > source.MAX_ROWS:
                    raise source.ReadIncomplete('Source row limit exceeded')
            return bundle, captured
        except source.SourceError:
            raise
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
            raise source.InvalidSource('Malformed source bundle') from None
        except Exception:
            raise source.ReadUnavailable('Coherent Zetaris read unavailable') from None
        finally:
            if raw_channel is not None:
                try:
                    raw_channel.close()
                except Exception:
                    raise source.ReadUnavailable('Read connection did not close cleanly') from None
    raise source.ReadIncomplete('Source revision changed during bounded read attempts')
