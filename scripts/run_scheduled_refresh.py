#!/usr/bin/env python3
"""Run one bounded publish and replace the prior low-sensitivity status file."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = Path.home() / "Library" / "Logs" / "ai-desk-card-online" / "latest.log"
DEFAULT_TIMEOUT = 150
MAX_STATUS_BYTES = 8192


def write_status(path: Path, content: str) -> None:
    normalized = content.encode("utf-8", errors="replace")[-MAX_STATUS_BYTES:].decode(
        "utf-8", errors="replace"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), delete=False
    ) as handle:
        handle.write(normalized.rstrip() + "\n")
        temporary = Path(handle.name)
    try:
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def run_refresh(
    status_path: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    runner: Any = subprocess.run,
) -> int:
    command = [sys.executable, str(REPO_ROOT / "scripts" / "refresh_dashboard.py"), "--publish"]
    try:
        completed = runner(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        content = (completed.stdout or "") + (completed.stderr or "")
        code = completed.returncode
    except subprocess.TimeoutExpired:
        content = "refresh=fatal reason=scheduled-timeout"
        code = 124
    except OSError:
        content = "refresh=fatal reason=scheduler-exec-failed"
        code = 1
    write_status(status_path, content or f"refresh=fatal reason=empty-output code={code}")
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one bounded scheduled desk-card publish")
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_refresh(args.status, timeout=max(30, args.timeout))


if __name__ == "__main__":
    raise SystemExit(main())
