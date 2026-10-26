"""Call the official Meterless H-MEM TypeScript engine through a JSON adapter."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping

BRIDGE = Path(__file__).resolve().parent / "hmem_bridge" / "server.ts"
DOCUMENTS = Path(__file__).resolve().parents[3]
DEFAULT_TSX = DOCUMENTS / "hmem-reference" / "reference" / "node_modules" / ".bin" / "tsx"
DEFAULT_PERSIST = Path.home() / ".local" / "state" / "dispute-demo" / "hmem"


def _tsx_bin() -> Path:
    override = os.environ.get("HMEM_TSX")
    if override:
        return Path(override)
    if DEFAULT_TSX.exists():
        return DEFAULT_TSX
    found = shutil.which("tsx")
    if found:
        return Path(found)
    raise FileNotFoundError("tsx is required to run the official H-MEM reference engine")


class HmemClient:
    """One subprocess call per operation; H-MEM reloads persistDir state.json."""

    def __init__(self, persist_dir: str | Path, *, actor: str = "dispute-agent"):
        self.persist_dir = Path(persist_dir).expanduser()
        self.persist_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.actor = actor

    def _invoke(self, payload: Mapping[str, Any]) -> dict:
        cmd = [_tsx_bin().as_posix(), BRIDGE.as_posix()]
        node = shutil.which("node")
        env = os.environ.copy()
        if node:
            env["PATH"] = str(Path(node).parent) + os.pathsep + env.get("PATH", "")
        completed = subprocess.run(
            cmd,
            input=json.dumps({**payload, "persistDir": str(self.persist_dir), "actor": self.actor}),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "H-MEM adapter failed")
        body = completed.stdout.strip().splitlines()[-1]
        parsed = json.loads(body)
        if not parsed.get("ok"):
            raise RuntimeError(parsed.get("error") or "H-MEM adapter returned an error")
        return parsed

    def add(self, input_record: Mapping[str, Any]) -> dict:
        return self._invoke({"op": "add", "input": dict(input_record)})["memory"]

    def query(self, query: str, *, chat_id: str, top_n: int = 5, threshold: float = 0.35) -> dict:
        return self._invoke({
            "op": "query",
            "query": query,
            "chatId": chat_id,
            "topN": top_n,
            "threshold": threshold,
        })["result"]

    def list(self) -> list[dict]:
        return self._invoke({"op": "list"})["memories"]
