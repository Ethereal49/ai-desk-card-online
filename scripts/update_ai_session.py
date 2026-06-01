#!/usr/bin/env python3
"""Explicitly update low-sensitivity AI session widgets in widgets.json."""

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


def build_ai_status(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "session_name": args.session_name,
        "model": args.model,
        "task": args.task,
        "context": {
            "used": max(0, args.context_used),
            "limit": max(0, args.context_limit),
        },
        "elapsed_seconds": max(0, args.elapsed_seconds),
        "updated_at": now_iso(),
    }


def build_ai_tasks(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "title": "AI Tasks",
        "counts": {
            "running": max(0, args.running),
            "waiting": max(0, args.waiting),
            "blocked": max(0, args.blocked),
            "completed_today": max(0, args.completed_today),
        },
        "updated_at": now_iso(),
    }


def upsert_widget(
    widgets: list[dict[str, Any]],
    widget_type: str,
    slot: str,
    data: dict[str, Any],
    insert_at: int,
) -> None:
    for widget in widgets:
        if widget.get("type") == widget_type:
            widget["slot"] = slot
            widget["data"] = data
            return
    widgets.insert(
        min(insert_at, len(widgets)),
        {
            "slot": slot,
            "type": widget_type,
            "data": data,
        },
    )


def update_ai_session_document(
    document: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    widgets = list(document.get("widgets") or [])
    upsert_widget(widgets, "ai-status", "glance-right", build_ai_status(args), 1)
    upsert_widget(widgets, "ai-tasks", "detail-left", build_ai_tasks(args), 3)

    document["updated_at"] = now_iso()
    document.setdefault("layout", "dashboard")
    document.setdefault("refresh_seconds", DEFAULT_REFRESH_SECONDS)
    document["widgets"] = widgets
    return document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Manually update only low-sensitivity AI status and task counters. "
            "This script writes a local widgets.json file and does not publish to live."
        ),
        epilog=(
            "Calling convention: manual only. Run this explicitly at the end of a meaningful Codex "
            "work turn or milestone. Do not run it from cron, do not auto-collect "
            "session state, and do not pass transcripts, message previews, tokens, "
            "private task text, or raw logs."
        ),
    )
    parser.add_argument("--widgets", type=Path, default=DEFAULT_WIDGETS)
    parser.add_argument("--session-name", required=True)
    parser.add_argument("--model", default="Codex")
    parser.add_argument("--task", required=True)
    parser.add_argument("--context-used", type=int, default=0)
    parser.add_argument("--context-limit", type=int, default=0)
    parser.add_argument("--elapsed-seconds", type=int, default=0)
    parser.add_argument("--running", type=int, default=0)
    parser.add_argument("--waiting", type=int, default=0)
    parser.add_argument("--blocked", type=int, default=0)
    parser.add_argument("--completed-today", type=int, default=0)
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    document = load_widgets(args.widgets)
    atomic_write_json(args.widgets, update_ai_session_document(document, args))
    print(f"updated AI session widgets in {args.widgets}")


if __name__ == "__main__":
    main()
