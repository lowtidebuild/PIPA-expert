"""Session-scoped MCP budget tracking for PIPA agent workflows."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_LIMIT = 15


@dataclass(frozen=True)
class BudgetResult:
    allowed: bool
    budget: dict[str, Any]
    reason: str | None = None


def budget_path(session_id: str | None = None, *, base_dir: str | Path = "/tmp") -> Path:
    session = session_id or os.environ.get("PIPA_SESSION_ID") or "default"
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in session)
    return Path(base_dir) / f"mcp-budget-{safe}.json"


def load_budget(path: str | Path, *, session_id: str | None = None, limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    budget_file = Path(path)
    if budget_file.exists():
        return json.loads(budget_file.read_text(encoding="utf-8"))
    return {
        "session_id": session_id or _session_from_path(budget_file),
        "limit": limit,
        "used": 0,
        "calls": [],
    }


def write_budget(path: str | Path, budget: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(budget, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_call(
    path: str | Path,
    *,
    tool: str,
    purpose: str,
    query: str,
    cost: int = 1,
    limit: int = DEFAULT_LIMIT,
    session_id: str | None = None,
) -> BudgetResult:
    budget = load_budget(path, session_id=session_id, limit=limit)
    budget.setdefault("limit", limit)
    budget.setdefault("used", 0)
    budget.setdefault("calls", [])

    if int(budget["used"]) + cost > int(budget["limit"]):
        return BudgetResult(False, budget, "MCP budget exceeded")

    budget["used"] = int(budget["used"]) + cost
    budget["calls"].append(
        {
            "ts": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "tool": tool,
            "purpose": purpose,
            "query": query,
            "cost": cost,
        }
    )
    write_budget(path, budget)
    return BudgetResult(True, budget)


def remaining(budget: dict[str, Any]) -> int:
    return max(0, int(budget.get("limit", DEFAULT_LIMIT)) - int(budget.get("used", 0)))


def _session_from_path(path: Path) -> str:
    name = path.name
    prefix = "mcp-budget-"
    suffix = ".json"
    if name.startswith(prefix) and name.endswith(suffix):
        return name[len(prefix) : -len(suffix)]
    return "default"
