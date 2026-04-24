#!/usr/bin/env python3
"""Write audit_status.json from citation-auditor aggregated verdict JSON."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.audit_status import build_audit_status, load_json, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aggregated_json", help="citation-auditor aggregated verdict JSON.")
    parser.add_argument("--output", required=True, help="audit_status.json output path.")
    parser.add_argument("--input-path", help="Original artifact path.")
    parser.add_argument("--expected-count", type=int, help="Expected claim count before aggregation.")
    parser.add_argument("--inserted-count", type=int, default=0)
    parser.add_argument("--invalid-span-count", type=int, default=0)
    parser.add_argument("--invalid-claim-id", action="append", default=[])
    parser.add_argument("--skipped-claim-id", action="append", default=[])
    parser.add_argument("--failed-verifier", action="append", default=[])
    parser.add_argument("--reason")
    args = parser.parse_args(argv)

    status = build_audit_status(
        load_json(args.aggregated_json),
        input_path=args.input_path,
        claim_count_expected=args.expected_count,
        inserted_count=args.inserted_count,
        invalid_span_count=args.invalid_span_count,
        invalid_claim_ids=args.invalid_claim_id,
        skipped_claim_ids=args.skipped_claim_id,
        failed_verifiers=args.failed_verifier,
        reason=args.reason,
    )
    write_json(args.output, status)
    print(f"wrote {args.output}: {status['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
