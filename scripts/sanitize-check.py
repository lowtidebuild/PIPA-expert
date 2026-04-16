#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.sanitize import sanitize_fetched_text, write_audit_sidecar


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize-check a text blob")
    parser.add_argument("path", help="File path or - for stdin")
    args = parser.parse_args()

    try:
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"io error: {exc}", file=sys.stderr)
        return 2

    result = sanitize_fetched_text(text, source="cli")
    if result.aborted:
        print("sanitizer unavailable", file=sys.stderr)
        return 3

    tmp_dir = Path(tempfile.mkdtemp(prefix="pipa-sanitize-"))
    sanitized_path = tmp_dir / "input.sanitized.md"
    sanitized_path.write_text(result.text, encoding="utf-8")
    write_audit_sidecar(sanitized_path, result)
    audit_path = sanitized_path.with_suffix(".sanitize.json")

    print(f"matches: {len(result.matches)}")
    for match in result.matches:
        print(
            f"  [{match.pattern_id}] offset={match.start}-{match.end} "
            f'"{match.snippet}"'
        )
    print(f"wrapped text written to: {sanitized_path}")
    print(f"audit json: {audit_path}")
    return 1 if result.matches else 0


if __name__ == "__main__":
    raise SystemExit(main())
