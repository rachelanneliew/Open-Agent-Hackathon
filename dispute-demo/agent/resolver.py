"""Retired prototype. Use app.main; memory integration belongs to T10.

No import-time clients, local ledger paths, sys.path mutation, recall or writes.
The former three-claim default was not policy and is no longer exposed.
"""


def investigate_dispute(*args, **kwargs):
    return {'status': 'unavailable', 'reason_code': 'LEGACY_RESOLVER_RETIRED',
            'persisted': False, 'stored_memory': None}
