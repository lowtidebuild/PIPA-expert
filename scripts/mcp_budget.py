#!/usr/bin/env python3
"""Track per-session MCP call budget for PIPA workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.mcp_budget import DEFAULT_LIMIT, budget_path, load_budget, record_call, remaining, write_budget


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", help="Session id. Defaults to PIPA_SESSION_ID or 'default'.")
    parser.add_argument("--path", help="Explicit budget JSON path.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Print current budget JSON.")
    subparsers.add_parser("init", help="Create or reset budget JSON.")

    record = subparsers.add_parser("record", help="Record one planned MCP call.")
    record.add_argument("--tool", required=True)
    record.add_argument("--purpose", required=True)
    record.add_argument("--query", required=True)
    record.add_argument("--cost", type=int, default=1)

    args = parser.parse_args(argv)
    path = Path(args.path) if args.path else budget_path(args.session)

    if args.command == "init":
        budget = {"session_id": args.session or "default", "limit": args.limit, "used": 0, "calls": []}
        write_budget(path, budget)
        print(json.dumps(budget, ensure_ascii=False, indent=2))
        return 0

    if args.command == "status":
        budget = load_budget(path, session_id=args.session, limit=args.limit)
        print(json.dumps(budget, ensure_ascii=False, indent=2))
        return 0

    result = record_call(
        path,
        tool=args.tool,
        purpose=args.purpose,
        query=args.query,
        cost=args.cost,
        limit=args.limit,
        session_id=args.session,
    )
    print(json.dumps(result.budget, ensure_ascii=False, indent=2))
    if not result.allowed:
        print(f"[MCP RATE LIMITED] {result.reason}; remaining={remaining(result.budget)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
