#!/usr/bin/env python3
"""Explicitly update the low-sensitivity focus widget in widgets.json."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WIDGETS = REPO_ROOT / "web" / "widgets.json"
DEFAULT_REFRESH_SECONDS = 300


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(path.parent),
        delete=False,
    ) as temp_file:
        temp_file.write(payload)
        temp_name = temp_file.name
    os.chmod(temp_name, 0o644)
    os.replace(temp_name, path)


def load_widgets(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "updated_at": now_iso(),
        "layout": "dashboard",
        "refresh_seconds": DEFAULT_REFRESH_SECONDS,
        "widgets": [],
    }


def build_focus(args: argparse.Namespace) -> dict[str, str]:
    return {
        "task": args.task,
        "big_text": args.big_text,
        "subtitle": args.subtitle,
    }


def update_focus_document(
    document: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    widgets = list(document.get("widgets") or [])
    for widget in widgets:
        if widget.get("type") == "focus":
            widget["slot"] = "headline"
            widget["data"] = build_focus(args)
            break
    else:
        widgets.insert(
            min(2, len(widgets)),
            {
                "slot": "headline",
                "type": "focus",
                "data": build_focus(args),
            },
        )

    document["updated_at"] = now_iso()
    document.setdefault("layout", "dashboard")
    document.setdefault("refresh_seconds", DEFAULT_REFRESH_SECONDS)
    document["widgets"] = widgets
    return document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Manually update only the cropped focus widget. This script writes "
            "a local widgets.json file and does not publish to live."
        ),
        epilog=(
            "Allowed fields are task, big_text, and subtitle. Do not pass notes, "
            "source URLs, transcripts, tokens, or raw task-manager records."
        ),
    )
    parser.add_argument("--widgets", type=Path, default=DEFAULT_WIDGETS)
    parser.add_argument("--task", required=True)
    parser.add_argument("--big-text", default="NOW")
    parser.add_argument("--subtitle", default="current focus")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    document = load_widgets(args.widgets)
    atomic_write_json(args.widgets, update_focus_document(document, args))
    print(f"updated focus widget in {args.widgets}")


if __name__ == "__main__":
    main()
