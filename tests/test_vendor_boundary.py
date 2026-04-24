from __future__ import annotations

from pathlib import Path

from scripts.check_vendor_boundary import check_manifest, write_manifest


def test_vendor_boundary_manifest_detects_drift(tmp_path: Path) -> None:
    vendor = tmp_path / "vendor"
    vendor.mkdir()
    (vendor / "VENDOR.md").write_text("- Version: **v1.0.0**\n- Source commit: abc123\n", encoding="utf-8")
    target = vendor / "file.txt"
    target.write_text("original", encoding="utf-8")
    manifest = "vendor/VENDOR_HASHES.json"

    write_manifest(root=tmp_path, manifest_path=manifest, targets=["vendor"])
    ok, messages = check_manifest(root=tmp_path, manifest_path=manifest)
    assert ok is True
    assert messages == []

    target.write_text("changed", encoding="utf-8")
    ok, messages = check_manifest(root=tmp_path, manifest_path=manifest)
    assert ok is False
    assert messages == ["modified vendored file: vendor/file.txt"]


def test_vendor_boundary_manifest_ignores_manifest_and_pycache(tmp_path: Path) -> None:
    vendor = tmp_path / "vendor"
    pycache = vendor / "__pycache__"
    pycache.mkdir(parents=True)
    (vendor / "file.txt").write_text("original", encoding="utf-8")
    (pycache / "file.pyc").write_bytes(b"compiled")
    manifest = "vendor/VENDOR_HASHES.json"

    write_manifest(root=tmp_path, manifest_path=manifest, targets=["vendor"])
    ok, messages = check_manifest(root=tmp_path, manifest_path=manifest)

    assert ok is True
    assert messages == []
