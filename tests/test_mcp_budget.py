from __future__ import annotations

import json
import subprocess
import sys

from scripts.lib.mcp_budget import budget_path, record_call, remaining


def test_budget_path_sanitizes_session_id(tmp_path) -> None:
    path = budget_path("session/with spaces", base_dir=tmp_path)

    assert path.name == "mcp-budget-session-with-spaces.json"


def test_record_call_persists_until_limit(tmp_path) -> None:
    path = tmp_path / "budget.json"

    first = record_call(path, tool="korean-law", purpose="freshness", query="개인정보 보호법", limit=2)
    second = record_call(path, tool="korean-law", purpose="case-law", query="제15조", limit=2)
    third = record_call(path, tool="korean-law", purpose="extra", query="제17조", limit=2)

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["used"] == 2
    assert remaining(payload) == 0


def test_mcp_budget_cli_record_blocks_when_exceeded(tmp_path) -> None:
    path = tmp_path / "budget.json"
    base = [
        sys.executable,
        "scripts/mcp_budget.py",
        "--path",
        str(path),
        "--limit",
        "1",
        "record",
        "--tool",
        "korean-law",
        "--purpose",
        "freshness",
        "--query",
        "개인정보 보호법",
    ]

    first = subprocess.run(base, check=True, capture_output=True, text=True)
    second = subprocess.run(base, check=False, capture_output=True, text=True)

    assert '"used": 1' in first.stdout
    assert second.returncode == 2
    assert "[MCP RATE LIMITED]" in second.stderr
