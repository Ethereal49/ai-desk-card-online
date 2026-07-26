#!/usr/bin/env python3
"""Project privacy-safe Codex task state from local metadata and lifecycle tails."""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from widget_contract import SourceResult, now_iso


LIFECYCLE_TYPES = frozenset({"task_started", "task_complete", "turn_aborted"})
BLOCKED_GOALS = frozenset({"blocked", "usage_limited", "budget_limited"})
WAITING_GOALS = frozenset({"active", "paused"})
DEFAULT_TAIL_BYTES = 1_048_576
MAX_THREADS = 600


class CodexSourceError(RuntimeError):
    pass


@dataclass(frozen=True)
class LifecycleSummary:
    latest_type: str | None
    latest_at: datetime | None
    current_started_at: datetime | None
    completed_at: tuple[datetime, ...]


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def lifecycle_summary(path: Path, *, tail_bytes: int = DEFAULT_TAIL_BYTES) -> LifecycleSummary:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max(1024, tail_bytes)))
            payload = handle.read()
    except OSError:
        return LifecycleSummary(None, None, None, ())
    if size > tail_bytes:
        payload = payload.split(b"\n", 1)[-1]

    events: list[tuple[datetime, str]] = []
    for raw_line in payload.splitlines():
        try:
            event = json.loads(raw_line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if event.get("type") != "event_msg" or not isinstance(event.get("payload"), dict):
            continue
        lifecycle_type = event["payload"].get("type")
        timestamp = parse_timestamp(event.get("timestamp"))
        if lifecycle_type in LIFECYCLE_TYPES and timestamp is not None:
            events.append((timestamp, lifecycle_type))
    events.sort()
    latest_at, latest_type = events[-1] if events else (None, None)
    current_started_at = latest_at if latest_type == "task_started" else None
    completed_at = tuple(
        timestamp for timestamp, event_type in events if event_type == "task_complete"
    )
    return LifecycleSummary(latest_type, latest_at, current_started_at, completed_at)


def _readonly_connection(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise CodexSourceError("codex database missing")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _require_columns(connection: sqlite3.Connection, table: str, required: set[str]) -> None:
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    if not required <= columns:
        raise CodexSourceError("codex database schema changed")


def read_threads(path: Path) -> list[dict[str, Any]]:
    required = {
        "id",
        "rollout_path",
        "created_at_ms",
        "updated_at_ms",
        "title",
        "tokens_used",
        "archived",
        "model",
    }
    with _readonly_connection(path) as connection:
        _require_columns(connection, "threads", required)
        total = connection.execute("SELECT COUNT(*) FROM threads").fetchone()[0]
        if total > MAX_THREADS:
            raise CodexSourceError("codex thread count exceeds safety limit")
        rows = connection.execute(
            "SELECT id, rollout_path, created_at_ms, updated_at_ms, title, "
            "tokens_used, archived, model FROM threads "
            "ORDER BY updated_at_ms DESC LIMIT ?",
            (MAX_THREADS,),
        ).fetchall()
    return [dict(row) for row in rows]


def read_goals(path: Path) -> dict[str, dict[str, Any]]:
    required = {"thread_id", "status", "updated_at_ms"}
    with _readonly_connection(path) as connection:
        _require_columns(connection, "thread_goals", required)
        rows = connection.execute(
            "SELECT thread_id, status, updated_at_ms FROM thread_goals"
        ).fetchall()
    return {row["thread_id"]: dict(row) for row in rows}


def _from_ms(value: Any) -> datetime:
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return datetime.min.replace(tzinfo=timezone.utc)


def classify_thread(
    thread: dict[str, Any],
    goal: dict[str, Any] | None,
    lifecycle: LifecycleSummary,
    *,
    now: datetime,
) -> str | None:
    updated = _from_ms(thread.get("updated_at_ms"))
    activity_at = max(updated, lifecycle.latest_at or updated)
    if (
        not thread.get("archived")
        and lifecycle.current_started_at is not None
        and activity_at >= now - timedelta(minutes=30)
    ):
        return "running"
    goal_status = (goal or {}).get("status")
    if not thread.get("archived") and goal_status in BLOCKED_GOALS:
        return "blocked"
    if not thread.get("archived") and goal_status in WAITING_GOALS:
        return "waiting"
    if (
        not thread.get("archived")
        and goal is None
        and lifecycle.latest_type in {"task_complete", "turn_aborted"}
        and lifecycle.latest_at is not None
        and lifecycle.latest_at >= now - timedelta(hours=24)
    ):
        return "waiting"
    return None


def project_codex(
    threads: list[dict[str, Any]],
    goals: dict[str, dict[str, Any]],
    lifecycles: dict[str, LifecycleSummary],
    *,
    now: datetime,
) -> dict[str, dict[str, Any]]:
    counts = {"running": 0, "waiting": 0, "blocked": 0, "completed_today": 0}
    candidates: list[tuple[datetime, dict[str, Any], str, LifecycleSummary]] = []
    completed: set[str] = set()
    today = now.astimezone().date()
    for thread in threads:
        thread_id = str(thread.get("id") or "")
        lifecycle = lifecycles.get(thread_id, LifecycleSummary(None, None, None, ()))
        goal = goals.get(thread_id)
        state = classify_thread(thread, goal, lifecycle, now=now.astimezone(timezone.utc))
        if state is not None:
            counts[state] += 1
            candidates.append((_from_ms(thread.get("updated_at_ms")), thread, state, lifecycle))
        goal_completed_today = (
            goal is not None
            and goal.get("status") == "complete"
            and _from_ms(goal.get("updated_at_ms")).astimezone().date() == today
        )
        if any(timestamp.astimezone().date() == today for timestamp in lifecycle.completed_at) or goal_completed_today:
            completed.add(thread_id)
    counts["completed_today"] = len(completed)
    candidates.sort(key=lambda item: (item[0], str(item[1].get("id") or "")), reverse=True)

    if candidates:
        _, selected, state, lifecycle = candidates[0]
        title = str(selected.get("title") or "Untitled Codex task").strip()
        model = str(selected.get("model") or "Codex").strip()
        created = _from_ms(selected.get("created_at_ms"))
        if state == "running" and lifecycle.current_started_at is not None:
            elapsed = max(0, int((now.astimezone(timezone.utc) - lifecycle.current_started_at).total_seconds()))
        else:
            elapsed = max(0, int((_from_ms(selected.get("updated_at_ms")) - created).total_seconds()))
        ai_status = {
            "session_name": state.upper(),
            "model": model,
            "task": title,
            "context": {"used": max(0, int(selected.get("tokens_used") or 0)), "limit": 0},
            "elapsed_seconds": elapsed,
        }
    else:
        ai_status = {
            "session_name": "IDLE",
            "model": "Codex",
            "task": "No active Codex task",
            "context": {"used": 0, "limit": 0},
            "elapsed_seconds": 0,
        }
    return {
        "ai-status": ai_status,
        "ai-tasks": {"title": "AI Tasks", "counts": counts},
    }


def collect_codex(
    state_db: Path,
    goals_db: Path,
    *,
    current_time: datetime | None = None,
    tail_bytes: int = DEFAULT_TAIL_BYTES,
) -> SourceResult:
    observed_at = now_iso()
    now = current_time or datetime.now().astimezone()
    try:
        threads = read_threads(state_db)
        goals = read_goals(goals_db)
        lifecycles = {
            str(thread["id"]): lifecycle_summary(
                Path(str(thread["rollout_path"])), tail_bytes=tail_bytes
            )
            for thread in threads
        }
        widgets = project_codex(threads, goals, lifecycles, now=now)
        return SourceResult.success("codex-metadata", widgets, observed_at)
    except (CodexSourceError, sqlite3.Error, OSError, ValueError):
        return SourceResult.failure(
            "codex-metadata",
            ("ai-status", "ai-tasks"),
            "codex metadata unavailable",
            observed_at,
        )
