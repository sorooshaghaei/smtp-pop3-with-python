from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

CHECKS = [
    Check(
        "compile",
        [
            PYTHON,
            "-m",
            "compileall",
            "-q",
            "email_app",
            "tests",
            "main.py",
            "smtp app.py",
            "pop3 app.py",
        ],
    ),
    Check("tests", [PYTHON, "-m", "unittest"]),
    Check("main help", [PYTHON, "main.py", "--help"]),
    Check("module help", [PYTHON, "-m", "email_app", "--help"]),
]


def main() -> int:
    verbose = os.environ.get("CHECK_VERBOSE") == "1"

    for check in CHECKS:
        print(f"==> {check.name}", flush=True)
        result = subprocess.run(
            check.command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if verbose or result.returncode != 0:
            print(result.stdout, end="")
        if result.returncode != 0:
            print(f"FAILED: {check.name}", file=sys.stderr)
            return result.returncode
        print("OK", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
