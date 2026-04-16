from pathlib import Path

from scripts.lib.paths import is_within_repo, repo_root


def test_repo_root_points_to_repository():
    root = repo_root()
    assert root.name == "PIPA-expert"
    assert (root / "CLAUDE.md").exists()


def test_is_within_repo_detects_repo_member():
    assert is_within_repo(repo_root() / "CLAUDE.md") is True


def test_is_within_repo_rejects_external_path():
    assert is_within_repo(Path("/tmp/pipa-outside")) is False
