"""Fetch the exact public reference into ignored outputs; never overwrite a tree.

Run from dispute-demo: python scripts/setup_hmem.py [--archive downloaded.tar.gz]
Then install the bridge's package-lock with npm ci using its pinned Node version.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'agent/hmem_bridge/reference-pin.json').read_text())
DEST = ROOT / 'outputs/dependencies/hmem'


def verify(root):
    for rel, digest in PIN['runtime_sha256'].items():
        if hashlib.sha256((root / 'reference/src' / rel).read_bytes()).hexdigest() != digest:
            raise ValueError('Reference hash mismatch; existing source preserved')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    if DEST.exists():
        verify(DEST)
        print('Pinned reference already present; unchanged')
        return
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DEST.parent) as tmp:
        archive = args.archive
        if archive is None:
            archive = Path(tmp) / 'reference.tar.gz'
            url = f"https://codeload.github.com/Meterless/Meterless/tar.gz/{PIN['revision']}"
            with urllib.request.urlopen(url, timeout=60) as response, archive.open('wb') as target:
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > 64 * 1024 * 1024:
                        raise ValueError('Archive exceeds download limit')
                    target.write(chunk)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != PIN['archive_sha256']:
            raise ValueError('Archive hash mismatch; nothing installed')
        staged = Path(tmp) / 'hmem'
        staged.mkdir()
        prefix = f"Meterless-{PIN['revision']}/engines/hmem/"
        with tarfile.open(archive) as bundle:
            for member in bundle:
                if not member.name.startswith(prefix) or not member.isfile():
                    continue
                rel = PurePosixPath(member.name[len(prefix):])
                if rel.is_absolute() or '..' in rel.parts:
                    raise ValueError('Unsafe archive member')
                output = staged / str(rel)
                output.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, output.open('xb') as target:
                    shutil.copyfileobj(source, target)
        verify(staged)
        staged.rename(DEST)
    print('Pinned official reference installed; deterministic mock embeddings, no network runtime')


if __name__ == '__main__':
    main()
