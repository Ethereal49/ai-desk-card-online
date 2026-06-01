#!/usr/bin/env python3
"""Explicitly update the low-sensitivity todo widget in widgets.json."""

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
MAX_TODO_ITEMS = 5


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


def build_todo(args: argparse.Namespace) -> dict[str, Any]:
    tags = args.tag or []
    items = []
    for index, text in enumerate((args.item or [])[:MAX_TODO_ITEMS]):
        item = {"text": text}
        if index < len(tags) and tags[index]:
            item["tag"] = tags[index]
        items.append(item)
    return {
        "title": args.title,
        "items": items,
    }


def update_todo_document(
    document: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    widgets = list(document.get("widgets") or [])
    for widget in widgets:
        if widget.get("type") == "todo":
            widget["slot"] = "detail-right"
            widget["data"] = build_todo(args)
            break
    else:
        widgets.append(
            {
                "slot": "detail-right",
                "type": "todo",
                "data": build_todo(args),
            }
        )

    document["updated_at"] = now_iso()
    document.setdefault("layout", "dashboard")
    document.setdefault("refresh_seconds", DEFAULT_REFRESH_SECONDS)
    document["widgets"] = widgets
    return document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Manually update only the cropped todo widget. This script writes "
            "a local widgets.json file and does not publish to live."
        ),
        epilog=(
            "Calling convention: manual only. Allowed fields are title plus up to five item text/tag pairs. "
            "Do not pass raw Reminders, Notion rows, source IDs, URLs, completion "
            "history, transcripts, tokens, or raw logs."
        ),
    )
    parser.add_argument("--widgets", type=Path, default=DEFAULT_WIDGETS)
    parser.add_argument("--title", default="Todo")
    parser.add_argument("--item", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    document = load_widgets(args.widgets)
    atomic_write_json(args.widgets, update_todo_document(document, args))
    print(f"updated todo widget in {args.widgets}")


if __name__ == "__main__":
    main()
