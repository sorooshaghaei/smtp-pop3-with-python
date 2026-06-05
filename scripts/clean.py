from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED_PATHS = [
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "build",
    "dist",
    "smtp_pop3_email_client.egg-info",
]


def main() -> int:
    for name in GENERATED_PATHS:
        shutil.rmtree(ROOT / name, ignore_errors=True)

    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
