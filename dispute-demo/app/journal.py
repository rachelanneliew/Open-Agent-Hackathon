"""Private local recovery request saved durably BEFORE any action dispatch."""
import json
import os
from pathlib import Path
import tempfile

from integration.fresh_reads import MAX_BUNDLE_BYTES, _json
from .action_service import CommitRequest
from .schemas import uuid_id


class FileJournal:
    def __init__(self, directory):
        self.directory = Path(directory)

    def prepare(self, request):
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = self.directory / (request.run_id + '.request.json')
        encoded = json.dumps(request.to_dict(), indent=2, allow_nan=False).encode()
        if len(encoded) > MAX_BUNDLE_BYTES:
            raise ValueError('Request too large')
        # Exclusive create prevents replacing a recovery payload with new facts.
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        fd = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return str(target.resolve())

    def finish(self, result):
        uuid_id(result.state.run_id)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = self.directory / (result.state.run_id + '.trace.json')
        with tempfile.NamedTemporaryFile(mode='w', dir=self.directory, delete=False) as file:
            temporary = Path(file.name)
            try:
                os.chmod(temporary, 0o600)
                json.dump(result.to_dict(), file, indent=2, allow_nan=False)
                file.flush()
                os.fsync(file.fileno())
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)


def load_request(path):
    with Path(path).open('rb') as file:
        data = file.read(MAX_BUNDLE_BYTES + 1)
    return CommitRequest.from_dict(_json(data.decode('utf-8')))
