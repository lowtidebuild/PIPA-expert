#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.paths import inbox_dir, is_within_repo, output_dir, private_dir, repo_root


def _unexpected_entries(path: Path, *, allowed: set[str]) -> list[Path]:
    if not path.exists():
        return []
    return sorted(entry for entry in path.iterdir() if entry.name not in allowed)


def main() -> int:
    root = repo_root()
    failures: list[str] = []

    resolved_paths = {
        "PIPA_OUTPUT_DIR": output_dir(),
        "PIPA_INBOX_DIR": inbox_dir(),
        "PIPA_PRIVATE_DIR": private_dir(),
    }

    for env_name, resolved in resolved_paths.items():
        if not resolved.exists():
            failures.append(f"{env_name} missing: {resolved}")
        elif is_within_repo(resolved):
            failures.append(f"{env_name} still points inside repo: {resolved}")

    if sorted(root.glob("*.docx")):
        failures.append("Root-level .docx files still present in repo")

    if _unexpected_entries(root / "_private", allowed={".gitkeep"}):
        failures.append("_private contains files beyond .gitkeep")

    if _unexpected_entries(root / "library" / "inbox", allowed={".gitkeep"}):
        failures.append("library/inbox contains files beyond .gitkeep")

    if _unexpected_entries(root / "output" / "opinions", allowed={".gitkeep", ".DS_Store"}):
        failures.append("output/opinions still contains private artifacts")

    if failures:
        print("security audit: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("security audit: PASS")
    for env_name, resolved in resolved_paths.items():
        print(f"  - {env_name}: {resolved}")
    print("  - repo placeholders are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
