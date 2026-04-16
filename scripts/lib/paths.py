from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def output_dir() -> Path:
    return Path(os.environ.get("PIPA_OUTPUT_DIR", "output/opinions")).expanduser().resolve()


def inbox_dir() -> Path:
    return Path(os.environ.get("PIPA_INBOX_DIR", "library/inbox")).expanduser().resolve()


def private_dir() -> Path:
    return Path(os.environ.get("PIPA_PRIVATE_DIR", "_private")).expanduser().resolve()


def repo_root() -> Path:
    return REPO_ROOT


def is_within_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return False
    return True
