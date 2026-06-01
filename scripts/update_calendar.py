#!/usr/bin/env python3
"""Explicitly update the low-sensitivity calendar widget in widgets.json."""

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
MAX_EVENTS = 4


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


def parse_event(value: str) -> dict[str, str]:
    parts = value.split("|")
    if len(parts) != 3:
        raise ValueError("calendar event must use START|TITLE|END")
    start, title, end = [part.strip() for part in parts]
    if not start or not title:
        raise ValueError("calendar event requires non-empty START and TITLE")
    event = {
        "start": start,
        "title": title,
    }
    if end:
        event["end"] = end
    return event


def build_calendar(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "now_iso": now_iso(),
        "events": [parse_event(value) for value in (args.event or [])[:MAX_EVENTS]],
    }


def update_calendar_document(
    document: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    widgets = list(document.get("widgets") or [])
    for widget in widgets:
        if widget.get("type") == "calendar":
            widget["slot"] = "detail-middle"
            widget["data"] = build_calendar(args)
            break
    else:
        insert_at = min(4, len(widgets))
        widgets.insert(
            insert_at,
            {
                "slot": "detail-middle",
                "type": "calendar",
                "data": build_calendar(args),
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
            "Manually update only the cropped calendar widget. This script writes "
            "a local widgets.json file and does not publish to live."
        ),
        epilog=(
            "Calling convention: manual only. Pass each event as START|TITLE|END. "
            "Do not pass raw Calendar or Google Calendar records, locations, attendees, "
            "meeting links, notes, calendar IDs, event IDs, transcripts, tokens, or raw logs."
        ),
    )
    parser.add_argument("--widgets", type=Path, default=DEFAULT_WIDGETS)
    parser.add_argument("--event", action="append", default=[])
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    document = load_widgets(args.widgets)
    atomic_write_json(args.widgets, update_calendar_document(document, args))
    print(f"updated calendar widget in {args.widgets}")


if __name__ == "__main__":
    main()
