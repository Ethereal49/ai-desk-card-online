#!/usr/bin/env python3
"""Codex Stop hook: keep PLAN_web.md current after project work."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


IGNORED_DIRS = {
    ".code-review-graph",
    ".git",
    ".playwright-mcp",
    ".playwright-cli",
    "__pycache__",
    "output",
}

# Trellis writes these records after the last product-plan update during its
# mandatory archive -> journal closeout sequence. Active tasks and specs remain
# plan-relevant because they are not below either prefix.
IGNORED_RELATIVE_DIRS = {
    Path(".trellis/tasks/archive"),
    Path(".trellis/workspace"),
}

IGNORED_FILES = {
    ".DS_Store",
    "PLAN_web.md",
}


def iter_project_files(root: Path) -> list[Path]:
    files: list[Path] = []
    ignored_paths = {root / path for path in IGNORED_RELATIVE_DIRS}
    for current_root, dirnames, filenames in os.walk(root):
        current = Path(current_root)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in IGNORED_DIRS and current / name not in ignored_paths
        ]
        for filename in filenames:
            if filename in IGNORED_FILES:
                continue
            path = current / filename
            if path.is_file():
                files.append(path)
    return files


def stale_files(root: Path, plan: Path) -> list[Path]:
    if not plan.exists():
        return [root]

    plan_mtime = plan.stat().st_mtime
    stale = []
    for path in iter_project_files(root):
        try:
            if path.stat().st_mtime > plan_mtime:
                stale.append(path)
        except FileNotFoundError:
            continue
    return sorted(stale, key=lambda item: item.stat().st_mtime, reverse=True)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    plan = root / "PLAN_web.md"
    stale = stale_files(root, plan)
    if not stale:
        print("{}")
        return 0

    examples = ", ".join(str(path.relative_to(root)) for path in stale[:8])
    if len(stale) > 8:
        examples += f", ... +{len(stale) - 8} more"

    reason = (
        "PLAN_web.md is older than project changes. Update PLAN_web.md with "
        f"the current status before finishing. Newer files: {examples}"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
