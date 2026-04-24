#!/usr/bin/env python3
"""Check that vendored citation-auditor files have not drifted locally."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ".claude/skills/citation-auditor/VENDOR_HASHES.json"
DEFAULT_TARGETS = [
    "citation_auditor",
    ".claude/skills/citation-auditor",
    ".claude/skills/verifiers",
    ".claude/commands/audit.md",
]
EXCLUDED_NAMES = {".DS_Store", "__pycache__", "VENDOR_HASHES.json"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def build_manifest(
    *,
    root: Path = PROJECT_ROOT,
    targets: list[str] | None = None,
    manifest_path: str = DEFAULT_MANIFEST,
) -> dict[str, Any]:
    target_paths = targets or DEFAULT_TARGETS
    files = collect_hashes(root=root, targets=target_paths, manifest_path=manifest_path)
    vendor_md = root / ".claude" / "skills" / "citation-auditor" / "VENDOR.md"
    metadata = _read_vendor_metadata(vendor_md)
    return {
        "vendor": "citation-auditor",
        "version": metadata.get("Version"),
        "source_commit": metadata.get("Source commit"),
        "source_tag": metadata.get("Source tag"),
        "manifest_version": 1,
        "targets": target_paths,
        "files": files,
    }


def collect_hashes(
    *,
    root: Path = PROJECT_ROOT,
    targets: list[str] | None = None,
    manifest_path: str = DEFAULT_MANIFEST,
) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for target in targets or DEFAULT_TARGETS:
        path = root / target
        if path.is_file():
            if _include(path, root=root, manifest_path=manifest_path):
                hashes[_rel(path, root)] = _sha256(path)
            continue
        if not path.exists():
            continue
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and _include(file_path, root=root, manifest_path=manifest_path):
                hashes[_rel(file_path, root)] = _sha256(file_path)
    return hashes


def check_manifest(
    *,
    root: Path = PROJECT_ROOT,
    manifest_path: str = DEFAULT_MANIFEST,
) -> tuple[bool, list[str]]:
    manifest_file = root / manifest_path
    if not manifest_file.exists():
        return False, [f"missing manifest: {manifest_path}"]

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    expected = manifest.get("files", {})
    if not isinstance(expected, dict):
        return False, ["manifest files payload is invalid"]

    actual = collect_hashes(root=root, targets=list(manifest.get("targets") or DEFAULT_TARGETS), manifest_path=manifest_path)
    messages: list[str] = []
    for rel_path in sorted(set(expected) - set(actual)):
        messages.append(f"missing vendored file: {rel_path}")
    for rel_path in sorted(set(actual) - set(expected)):
        messages.append(f"new vendored file not in manifest: {rel_path}")
    for rel_path in sorted(set(expected) & set(actual)):
        if expected[rel_path] != actual[rel_path]:
            messages.append(f"modified vendored file: {rel_path}")
    return not messages, messages


def write_manifest(
    *,
    root: Path = PROJECT_ROOT,
    manifest_path: str = DEFAULT_MANIFEST,
    targets: list[str] | None = None,
) -> Path:
    manifest = build_manifest(root=root, targets=targets, manifest_path=manifest_path)
    output = root / manifest_path
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _include(path: Path, *, root: Path, manifest_path: str) -> bool:
    rel_path = _rel(path, root)
    if rel_path == manifest_path:
        return False
    if any(part in EXCLUDED_NAMES for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _read_vendor_metadata(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    metadata: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- "):
            continue
        key, sep, value = line[2:].partition(":")
        if sep:
            metadata[key.strip()] = value.strip().strip("*").strip()
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--write", action="store_true", help="Write/update the local hash manifest.")
    args = parser.parse_args(argv)

    if args.write:
        output = write_manifest(manifest_path=args.manifest)
        print(f"wrote {output}")
        return 0

    ok, messages = check_manifest(manifest_path=args.manifest)
    if ok:
        print("vendor boundary: PASS")
        return 0
    print("vendor boundary: FAIL")
    for message in messages:
        print(f"  - {message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
