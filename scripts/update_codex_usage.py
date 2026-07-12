#!/usr/bin/env python3
"""Update the low-sensitivity Codex quota summary from local rollout JSONL files."""

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
DEFAULT_SESSIONS = Path.home() / ".codex" / "sessions"
DEFAULT_REFRESH_SECONDS = 300
DEFAULT_MAX_FILES = 80
DEFAULT_TAIL_BYTES = 1_048_576
DEFAULT_STALE_AFTER_SECONDS = 600


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


def number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_window(slot: dict[str, Any]) -> dict[str, Any] | None:
    used = number(slot.get("used_percent"))
    if used is None:
        used = number(slot.get("used_percentage"))
    if used is None:
        return None

    window_minutes = number(slot.get("window_minutes"))
    if window_minutes is None:
        seconds = number(slot.get("limit_window_seconds"))
        window_minutes = seconds / 60 if seconds is not None else None

    resets_at = number(slot.get("resets_at"))
    if resets_at is None:
        resets_at = number(slot.get("reset_at"))

    result: dict[str, Any] = {
        "remaining_percent": round(max(0.0, min(100.0, 100.0 - used)), 1),
    }
    if window_minutes is not None:
        result["window_minutes"] = int(window_minutes)
    if resets_at is not None:
        result["resets_at"] = int(resets_at)
    return result


def classify_windows(rate_limits: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots: list[tuple[str, dict[str, Any]]] = []
    for key in ("primary", "secondary", "primary_window", "secondary_window"):
        value = rate_limits.get(key)
        if isinstance(value, dict):
            slots.append((key, value))

    windows: dict[str, dict[str, Any]] = {}
    for key, slot in slots:
        parsed = parse_window(slot)
        if parsed is None:
            continue
        minutes = parsed.get("window_minutes")
        if isinstance(minutes, int):
            role = "five_hour" if minutes <= 300 else "weekly"
        elif key.startswith("secondary"):
            role = "weekly"
        elif len(slots) > 1:
            role = "five_hour"
        else:
            continue
        windows[role] = parsed
    return windows


def parse_rate_limit_event(line: str) -> dict[str, Any] | None:
    try:
        event = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        return None
    if event.get("type") != "event_msg":
        return None
    payload = event.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "token_count":
        return None
    rate_limits = payload.get("rate_limits")
    if not isinstance(rate_limits, dict):
        return None

    windows = classify_windows(rate_limits)
    if not windows:
        return None
    return {
        "timestamp": event.get("timestamp"),
        "windows": windows,
    }


def latest_event_in_file(path: Path, tail_bytes: int) -> dict[str, Any] | None:
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        offset = handle.tell()
        partial = b""
        while offset > 0:
            read_size = min(tail_bytes, offset)
            offset -= read_size
            handle.seek(offset)
            chunk = handle.read(read_size)
            lines = (chunk + partial).split(b"\n")
            if offset > 0:
                partial = lines[0]
                lines = lines[1:]
            else:
                partial = b""
            for raw_line in reversed(lines):
                if not raw_line:
                    continue
                event = parse_rate_limit_event(raw_line.decode("utf-8", errors="replace"))
                if event is not None:
                    return event
    return None


def rollout_files(root: Path, max_files: int) -> list[Path]:
    if root.is_file():
        return [root] if root.name.startswith("rollout-") and root.suffix == ".jsonl" else []
    if not root.exists():
        return []
    files = [
        path
        for path in root.rglob("rollout-*.jsonl")
        if path.is_file()
    ]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:max_files]


def find_latest_quota(
    root: Path,
    max_files: int,
    tail_bytes: int,
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
    current_time: datetime | None = None,
) -> dict[str, Any] | None:
    latest_event: dict[str, Any] | None = None
    latest_time: datetime | None = None
    for path in rollout_files(root, max_files):
        event = latest_event_in_file(path, tail_bytes)
        if event is None:
            continue
        event_time = parse_timestamp(event.get("timestamp"))
        if latest_event is None or (
            event_time is not None
            and (latest_time is None or event_time > latest_time)
        ):
            latest_event = event
            latest_time = event_time

    if latest_event is None:
        return None

    timestamp = latest_event.get("timestamp")
    now = (current_time or datetime.now(timezone.utc)).astimezone(timezone.utc)
    stale = latest_time is None or (now - latest_time).total_seconds() > stale_after_seconds
    return {
        "source": "codex-rollout",
        "updated_at": timestamp or now_iso(),
        "stale": stale,
        **latest_event["windows"],
    }


def find_ai_status_widget(widgets: list[dict[str, Any]]) -> dict[str, Any] | None:
    for widget in widgets:
        if widget.get("type") == "ai-status":
            return widget
    return None


def stale_quota(existing: dict[str, Any] | None) -> dict[str, Any]:
    quota = dict(existing or {})
    quota.setdefault("source", "codex-rollout")
    quota["stale"] = True
    quota["last_attempt_at"] = now_iso()
    quota["error"] = "quota unavailable"
    return quota


def update_codex_quota_document(
    document: dict[str, Any],
    quota: dict[str, Any],
) -> dict[str, Any]:
    widgets = list(document.get("widgets") or [])
    widget = find_ai_status_widget(widgets)
    if widget is None:
        widget = {
            "slot": "glance-right",
            "type": "ai-status",
            "data": {},
        }
        widgets.insert(min(1, len(widgets)), widget)
    data = dict(widget.get("data") or {})
    data["quota"] = quota
    widget["slot"] = "glance-right"
    widget["data"] = data

    document["updated_at"] = now_iso()
    document.setdefault("layout", "dashboard")
    document.setdefault("refresh_seconds", DEFAULT_REFRESH_SECONDS)
    document["widgets"] = widgets
    return document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read low-sensitivity Codex quota windows from local rollout JSONL files "
            "and update only ai-status.data.quota. This does not publish to live."
        )
    )
    parser.add_argument("--widgets", type=Path, default=DEFAULT_WIDGETS)
    parser.add_argument("--sessions", type=Path, default=DEFAULT_SESSIONS)
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--tail-bytes", type=int, default=DEFAULT_TAIL_BYTES)
    parser.add_argument(
        "--stale-after-seconds",
        type=int,
        default=DEFAULT_STALE_AFTER_SECONDS,
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    document = load_widgets(args.widgets)
    widget = find_ai_status_widget(document.get("widgets") or [])
    existing = (widget.get("data") or {}).get("quota") if widget else None
    quota = find_latest_quota(
        args.sessions,
        max(1, args.max_files),
        max(1024, args.tail_bytes),
        max(0, args.stale_after_seconds),
    )
    if quota is None:
        quota = stale_quota(existing if isinstance(existing, dict) else None)
    atomic_write_json(args.widgets, update_codex_quota_document(document, quota))
    state = "stale" if quota.get("stale") else "fresh"
    print(f"updated Codex quota ({state}) in {args.widgets}")


if __name__ == "__main__":
    main()
