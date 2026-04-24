#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.paths import inbox_dir, is_within_repo, output_dir, private_dir, repo_root


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def _unexpected_entries(path: Path, *, allowed: set[str]) -> list[Path]:
    if not path.exists():
        return []
    return sorted(entry for entry in path.iterdir() if entry.name not in allowed)


def audit_findings(*, strict: bool = False) -> list[Finding]:
    root = repo_root()
    findings: list[Finding] = []

    resolved_paths = {
        "PIPA_OUTPUT_DIR": output_dir(),
        "PIPA_INBOX_DIR": inbox_dir(),
        "PIPA_PRIVATE_DIR": private_dir(),
    }

    for env_name, resolved in resolved_paths.items():
        if not resolved.exists():
            findings.append(Finding(_path_level(strict), f"{env_name} missing: {resolved}"))
        elif is_within_repo(resolved):
            findings.append(Finding(_path_level(strict), f"{env_name} points inside repo: {resolved}"))

    if sorted(root.glob("*.docx")):
        findings.append(Finding("FAIL", "Root-level .docx files still present in repo"))

    if _unexpected_entries(root / "_private", allowed={".gitkeep"}):
        findings.append(Finding("FAIL", "_private contains files beyond .gitkeep"))

    if _unexpected_entries(root / "library" / "inbox", allowed={".gitkeep"}):
        findings.append(Finding("FAIL", "library/inbox contains files beyond .gitkeep"))

    if _unexpected_entries(root / "output" / "opinions", allowed={".gitkeep", ".DS_Store"}):
        findings.append(Finding("FAIL", "output/opinions still contains private artifacts"))

    return findings


def _path_level(strict: bool) -> str:
    return "FAIL" if strict else "WARN"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit private workspace paths and repo artifact leakage.")
    parser.add_argument("--strict", action="store_true", help="Treat repo-internal or missing private paths as failures.")
    args = parser.parse_args(argv)

    findings = audit_findings(strict=args.strict)
    failures = [finding for finding in findings if finding.level == "FAIL"]
    warnings = [finding for finding in findings if finding.level == "WARN"]

    if failures:
        print("security audit: FAIL")
        for finding in failures:
            print(f"  - [FAIL] {finding.message}")
        for finding in warnings:
            print(f"  - [WARN] {finding.message}")
        return 1

    if warnings:
        print("security audit: WARN")
        for finding in warnings:
            print(f"  - [WARN] {finding.message}")
        print("  - run with --strict before release or external sharing")
        return 0

    print("security audit: PASS")
    for env_name, resolved in {
        "PIPA_OUTPUT_DIR": output_dir(),
        "PIPA_INBOX_DIR": inbox_dir(),
        "PIPA_PRIVATE_DIR": private_dir(),
    }.items():
        print(f"  - {env_name}: {resolved}")
    print("  - repo placeholders are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
