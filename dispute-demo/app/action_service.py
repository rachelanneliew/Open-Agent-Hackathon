"""T05 atomic sandbox writer. Application API only; never a model read tool.

The caller supplies an immutable request and a fresh, exclusively owned Psycopg
connection (or configures DISPUTE_ACTION_DSN). No connections on import. No
SQLite, fixture, model or memory fallback. See docs/actions.md for deployment.
"""
from dataclasses import dataclass, replace
from datetime import timezone
import json
import os
from uuid import uuid4

from integration import get_dispute_context as source
from .critic import review_proposal
from .policy_engine import evaluate_policy
from .schemas import (AgentProposal, CommitResult, Contract, ContractError,
                      CriticResult, CriticVerdict, DisputeContext, ExecutionStatus,
                      Outcome, PolicyResult, require, uuid_id)
from .tools import context_from_rows


@dataclass(frozen=True, kw_only=True)
class CommitRequest(Contract):
    run_id: str
    idempotency_key: str
    context: DisputeContext
    policy: PolicyResult
    proposal: AgentProposal
    critic: CriticResult

    def _check(self):
        uuid_id(self.run_id)
        uuid_id(self.idempotency_key)


class _Refused(Exception):
    def __init__(self, code, status=ExecutionStatus.REJECTED):
        self.code, self.status = code, status


def _connect():
    # Credentials are application configuration, never request fields or logs.
    import psycopg
    dsn = os.environ.get('DISPUTE_ACTION_DSN')
    if not dsn:
        raise RuntimeError('Action connection is not configured')
    return psycopg.connect(dsn, connect_timeout=5, autocommit=False)


def _rows(cursor, query, params, columns):
    cursor.execute(query + f' LIMIT {source.MAX_ROWS + 1}', params)
    rows = cursor.fetchall()
    if len(rows) > source.MAX_ROWS:
        raise _Refused('source_limit_exceeded', ExecutionStatus.UNAVAILABLE)
    return [dict(zip(columns, row)) for row in rows]


def _load_current(cursor, request):
    """Protected commit-time read, not an alternate investigation read tool.

    Read every current scoped row before applying the requested cutoff. A late
    refund/evidence row cannot disappear behind the historical visibility filter.
    Reuse the T02 typed mapping and T03 semantics, including opening-date policy.
    """
    ref = request.context.reference
    did = ref.dispute_id
    def columns(alias, names):
        return ', '.join(f'{alias}.{name}' for name in names)
    cases = _rows(cursor, f'SELECT {columns("d", source.DISPUTE_COLUMNS)} '
                  'FROM public.disputes d WHERE d.dispute_id = %s', (did,), source.DISPUTE_COLUMNS)
    if len(cases) != 1:
        raise _Refused('case_not_found')
    case = cases[0]
    if case['dispute_status'] != 'open':
        raise _Refused('unsupported_dispute_status')
    # This is the explicit new evaluation's cutoff, not a source-row mutation.
    case['evaluation_at'] = ref.evaluation_at.isoformat().replace('+00:00', 'Z')
    linked = (case['transaction_id'], case['related_transaction_id'])
    raw = {'dispute': case}
    for name, names in (('transactions', source.TRANSACTION_COLUMNS),
                        ('settlements', source.SETTLEMENT_COLUMNS)):
        raw[name] = _rows(cursor, f'SELECT {columns("s", names)} FROM public.{name} s '
                         'WHERE s.transaction_id IN (%s, %s)', linked, names)
    raw['evidence'] = _rows(cursor, f'SELECT {columns("e", source.EVIDENCE_COLUMNS)}, doc.content '
        'FROM public.evidence e LEFT JOIN public.evidence_documents doc USING (evidence_id) '
        'WHERE e.dispute_id = %s', (did,), (*source.EVIDENCE_COLUMNS, 'content'))
    raw['policy_rules'] = _rows(cursor, f'SELECT {columns("p", source.POLICY_COLUMNS)} '
        "FROM public.policy_rules p WHERE p.reason_code IN ('ALL', %s) ORDER BY p.priority",
        (case['reason_code'],), source.POLICY_COLUMNS)
    for name, times in (('transactions', ('occurred_at', 'recorded_at')),
                        ('settlements', ('occurred_at', 'recorded_at')),
                        ('evidence', ('event_at', 'available_at'))):
        if any(source._time(row[t]) > ref.evaluation_at for row in raw[name] for t in times):
            raise _Refused('post_cutoff_source_requires_new_evaluation')
    current = context_from_rows(raw, did, captured_at=request.context.captured_at,
                                source_channel=request.context.source_channel).data
    if current.reference.policy_version != ref.policy_version:
        raise _Refused('policy_version_changed')
    # Preserve the submitted immutable identity only after checking its sources.
    return replace(current, reference=ref)


def _facts(context):
    payload = context.to_dict()
    for field in ('reference', 'captured_at', 'source_channel'):
        payload.pop(field)
    for name, key in (('transactions', 'transaction_id'), ('settlements', 'settlement_id'),
                      ('evidence', 'evidence_id'), ('policy_rules', 'policy_rule_id')):
        payload[name].sort(key=lambda row: row[key])
    payload['data_issues'].sort()
    return payload


def _stored(cursor, key, status):
    cursor.execute('SELECT d.request_payload, d.decision_id::text, d.committed_at, '
        'c.simulated_credit_id::text FROM dispute_actions.decisions d '
        'LEFT JOIN dispute_actions.simulated_credits c USING (decision_id) '
        'WHERE d.idempotency_key = %s', (key,))
    row = cursor.fetchone()
    if row is None:
        return None
    payload, decision_id, committed_at, credit_id = row
    original = CommitRequest.from_dict(payload)
    result = CommitResult(run_id=original.run_id, proposal_id=original.proposal.proposal_id,
        idempotency_key=original.idempotency_key, reference=original.context.reference,
        status=status, message='Original committed decision reused.' if status is ExecutionStatus.REUSED
        else 'Synthetic decision committed.', decision_id=decision_id,
        recommendation=original.proposal.recommendation,
        committed_at=committed_at.astimezone(timezone.utc), simulated_credit_id=credit_id)
    return payload, result


def _insert(cursor, table, row, json_fields):
    # Table/column names come only from the two constant calls below, never input.
    values = [json.dumps(value) if key in json_fields else value for key, value in row.items()]
    placeholders = ['%s::jsonb' if key in json_fields else '%s' for key in row]
    cursor.execute(f'INSERT INTO dispute_actions.{table} ({", ".join(row)}) '
                   f'VALUES ({", ".join(placeholders)})', values)


def commit_simulated_decision(request: CommitRequest, *, connect=None) -> CommitResult:
    """Commit once, or return an honest refusal/unconfirmed result.

    Malformed transport raises ContractError before I/O; a typed request gets a
    bound CommitResult. Each invocation owns a NEW idle non-autocommit connection.
    Retry the exact request/key after any unconfirmed outcome. Never regenerate
    identities, relabel a stale reference, or retry a changed proposal as reuse.
    """
    require(type(request) is CommitRequest, 'Expected CommitRequest')
    request = CommitRequest.from_dict(request.to_dict())  # deep boundary check
    def failure(code, status=ExecutionStatus.REJECTED):
        return CommitResult(run_id=request.run_id, proposal_id=request.proposal.proposal_id,
            idempotency_key=request.idempotency_key, reference=request.context.reference,
            status=status, message=code)
    connection = None
    committing = False
    try:
        connection = (connect or _connect)()
        if connection.autocommit or connection.info.transaction_status != 0:
            raise _Refused('requires_new_idle_transaction', ExecutionStatus.UNAVAILABLE)
        with connection.cursor() as cursor:
            cursor.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED, READ WRITE')
            cursor.execute("SET LOCAL statement_timeout = '10s'")
            cursor.execute("SET LOCAL lock_timeout = '5s'")
            cursor.execute("SET LOCAL idle_in_transaction_session_timeout = '15s'")
            cursor.execute("SET LOCAL synchronous_commit = 'on'")
            cursor.execute("SET LOCAL search_path = pg_catalog")
            cursor.execute("SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls, "
                "pg_has_role(session_user, 'dispute_storage_owner', 'MEMBER'), "
                "pg_has_role(session_user, 'dispute_source_writer', 'MEMBER'), "
                "pg_has_role(current_user, 'dispute_action_writer', 'USAGE') "
                'FROM pg_roles WHERE rolname = session_user')
            privileged, owner, source_writer, action_writer = cursor.fetchone()
            if privileged or owner or source_writer or not action_writer:
                raise _Refused('restricted_action_login_required', ExecutionStatus.UNAVAILABLE)
            # A separate statement AFTER waiting is vital under READ COMMITTED.
            cursor.execute('SELECT dispute_control.lock_source_revision()')
            revision = cursor.fetchone()[0]
            stored = _stored(cursor, request.idempotency_key, ExecutionStatus.REUSED)
            if stored:
                if stored[0] != request.to_dict():
                    raise _Refused('idempotency_payload_conflict')
                return stored[1]
            ref, proposal = request.context.reference, request.proposal
            if ref.source_revision is None:
                raise _Refused('source_revision_unknown')
            if ref.source_revision != revision:
                raise _Refused('source_revision_stale')
            if (request.run_id != proposal.run_id or request.policy.reference != ref or
                    proposal.reference != ref or request.critic.reference != ref or
                    request.critic.proposal_id != proposal.proposal_id or
                    request.critic.verdict is not CriticVerdict.ACCEPTED):
                raise _Refused('proposal_critic_binding_invalid')
            cursor.execute('SELECT clock_timestamp()')
            now = cursor.fetchone()[0]
            if ref.evaluation_at > now or request.context.captured_at > now:
                raise _Refused('future_snapshot')
            current = _load_current(cursor, request)
            if _facts(current) != _facts(request.context):
                raise _Refused('authoritative_context_mismatch')
            policy = evaluate_policy(current)
            if policy != request.policy:
                raise _Refused('current_policy_mismatch')
            critic = review_proposal(current, policy, proposal)
            if critic.verdict is not CriticVerdict.ACCEPTED or critic != request.critic:
                raise _Refused('current_critic_rejected')
            cursor.execute('SELECT decision_id::text FROM dispute_actions.current_decisions '
                           'WHERE dispute_id = %s', (ref.dispute_id,))
            previous = cursor.fetchone()
            if proposal.recommendation.outcome is Outcome.PROVISIONAL_CREDIT:
                cursor.execute('SELECT 1 FROM dispute_actions.credit_reservations '
                    'WHERE transaction_id IN (%s, %s)',
                    (current.dispute.transaction_id, current.dispute.related_transaction_id))
                if cursor.fetchone():
                    raise _Refused('effective_credit_already_exists')
            payload = request.to_dict()
            _insert(cursor, 'investigations', dict(run_id=request.run_id, proposal_id=proposal.proposal_id,
                dispute_id=ref.dispute_id, transaction_id=current.dispute.transaction_id,
                snapshot_id=ref.snapshot_id, evaluation_at=ref.evaluation_at,
                policy_version=ref.policy_version, source_revision=revision,
                context_payload=payload['context'], proposal_payload=payload['proposal'],
                critic_payload=payload['critic']), {'context_payload', 'proposal_payload', 'critic_payload'})
            _insert(cursor, 'decisions', dict(decision_id=str(uuid4()), run_id=request.run_id,
                dispute_id=ref.dispute_id, transaction_id=current.dispute.transaction_id,
                idempotency_key=request.idempotency_key, request_payload=payload,
                previous_decision_id=previous[0] if previous else None,
                outcome=proposal.recommendation.outcome.value, currency=proposal.recommendation.currency,
                amount_minor=proposal.recommendation.amount_minor, rationale=proposal.rationale,
                evidence_ids=list(proposal.evidence_ids), policy_rule_ids=list(proposal.policy_rule_ids),
                missing_evidence=[item.to_dict() for item in proposal.missing_evidence]),
                {'request_payload', 'evidence_ids', 'policy_rule_ids', 'missing_evidence'})
            result = _stored(cursor, request.idempotency_key, ExecutionStatus.COMMITTED)[1]
        committing = True
        connection.commit()  # Never expose the constructed result before acknowledgement.
        return result
    except _Refused as exc:
        return failure(exc.code, exc.status)
    except Exception as exc:
        if committing:
            return failure('commit_unconfirmed_retry_identical_request', ExecutionStatus.FAILED)
        if isinstance(exc, (ContractError, source.SourceError, ValueError, TypeError, KeyError)):
            return failure('source_or_stored_payload_invalid')
        sqlstate = getattr(exc, 'sqlstate', None)
        if sqlstate and (sqlstate.startswith('23') or sqlstate == 'P0001'):
            return failure('storage_constraint_rejected')
        status = ExecutionStatus.UNAVAILABLE if connection is None or sqlstate in (
            '42P01', '42883', '42501', '55P03', '57014') else ExecutionStatus.FAILED
        return failure('storage_unavailable' if status is ExecutionStatus.UNAVAILABLE else
                       'transaction_failed_retry_identical_request', status)
    finally:
        if connection is not None:
            # Cleanup failures must not erase an acknowledged commit or leak DSNs.
            try:
                connection.rollback()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass
