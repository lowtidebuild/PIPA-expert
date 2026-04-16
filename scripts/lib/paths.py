from __future__ import annotations

import os
from pathlib import Path


def output_dir() -> Path:
    return Path(os.environ.get("PIPA_OUTPUT_DIR", "output/opinions")).expanduser().resolve()


def inbox_dir() -> Path:
    return Path(os.environ.get("PIPA_INBOX_DIR", "library/inbox")).expanduser().resolve()


def private_dir() -> Path:
    return Path(os.environ.get("PIPA_PRIVATE_DIR", "_private")).expanduser().resolve()
