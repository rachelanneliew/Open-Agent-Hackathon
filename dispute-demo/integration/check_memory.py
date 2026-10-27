"""Reference-only receipt replay. No source reads, model calls or action retries.

A saved receipt is trusted local input, not a fresh authoritative verification.
This command demonstrates memory persistence separately from the live workflow.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

from app.schemas import CommitResult, DisputeContext, require
from agent.hmem_client import HmemClient, MemoryError, strict_json
from agent.memory_service import DisputeMemory, CommittedSummary, parse_record, record_input


def read_json(path):
    with path.open('rb') as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    require(len(raw) <= 2 * 1024 * 1024, 'Input exceeds size limit')
    return strict_json(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--trace', type=Path, required=True)
    parser.add_argument('--persist-dir', type=Path, required=True)
    parser.add_argument('--recall-only', action='store_true')
    args = parser.parse_args()
    try:
        request, trace = read_json(args.request), read_json(args.trace)
        require(trace['persisted'] is True, 'Confirmed receipt required')
        context = DisputeContext.from_dict(request['context'])
        receipt = CommitResult.from_dict(trace['state']['commit_result'])
        summary = CommittedSummary.from_commit(context, receipt)
        require(receipt.run_id == request['run_id'] and receipt.idempotency_key == request['idempotency_key'] and
                receipt.proposal_id == request['proposal']['proposal_id'] and
                receipt.recommendation.to_dict() == request['proposal']['recommendation'], 'Receipt request mismatch')
        client = HmemClient(args.persist_dir)
        saved = None if args.recall_only else asdict(DisputeMemory(client).save(summary))
        recalled = client.query(record_input(summary)['content'], chat_id='customer:' + summary.customer_id)
        found = any(parse_record(r) == summary for r in recalled['memories'])
        print(json.dumps(dict(mode='reference_hmem_saved_receipt', source_freshly_verified=False,
            action_called=False, summary=summary.to_dict(), save=saved, recalled_after_new_node_process=found), indent=2))
        return 0 if found and (saved is None or saved['status'] in ('stored', 'reused')) else 1
    except (OSError, ValueError, TypeError, KeyError, MemoryError):
        print(json.dumps(dict(mode='reference_hmem_saved_receipt', action_called=False,
            error='reference_memory_check_failed')))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
