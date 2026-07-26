#!/usr/bin/env python3
"""Load a bounded local Focus selection and resolve it from projected widgets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from widget_contract import (
    MAX_SHORT_TEXT_LENGTH,
    MAX_TEXT_LENGTH,
    build_widget,
    now_iso,
    widget_map,
)


DEFAULT_FOCUS_CONFIG = Path.home() / ".config" / "ai-desk-card-online" / "focus.json"
DEFAULT_SOURCE = "todo.first"
MAX_CONFIG_BYTES = 8192
ALLOWED_SOURCES = frozenset(
    {"todo.first", "calendar.next", "ai-status.task", "weather.current", "manual"}
)
ALLOWED_KEYS = frozenset({"source", "task", "subtitle", "big_text"})


class FocusConfigurationError(ValueError):
    """Raised for invalid local configuration without exposing its content."""


@dataclass(frozen=True)
class FocusConfig:
    source: str = DEFAULT_SOURCE
    task: str | None = None
    subtitle: str | None = None
    big_text: str | None = None


def _text(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise FocusConfigurationError(f"focus {name} is invalid")
    return value.strip()


def parse_focus_config(value: Any) -> FocusConfig:
    if not isinstance(value, dict) or set(value) - ALLOWED_KEYS:
        raise FocusConfigurationError("focus configuration shape is invalid")
    source = value.get("source", DEFAULT_SOURCE)
    if not isinstance(source, str) or source not in ALLOWED_SOURCES:
        raise FocusConfigurationError("focus source is invalid")
    task = value.get("task")
    subtitle = value.get("subtitle")
    big_text = value.get("big_text")
    if source == "manual":
        task = _text(task, "task", MAX_TEXT_LENGTH)
    elif task is not None:
        raise FocusConfigurationError("focus task is allowed only for manual source")
    if subtitle is not None:
        subtitle = _text(subtitle, "subtitle", MAX_SHORT_TEXT_LENGTH)
    if big_text is not None:
        big_text = _text(big_text, "big_text", MAX_SHORT_TEXT_LENGTH)
    return FocusConfig(source=source, task=task, subtitle=subtitle, big_text=big_text)


def load_focus_config(path: Path = DEFAULT_FOCUS_CONFIG) -> FocusConfig:
    if not path.exists():
        return FocusConfig()
    try:
        if not path.is_file() or path.stat().st_size > MAX_CONFIG_BYTES:
            raise FocusConfigurationError("focus configuration file is invalid")
        raw = path.read_bytes()
        if len(raw) > MAX_CONFIG_BYTES:
            raise FocusConfigurationError("focus configuration file is too large")
        document = json.loads(raw.decode("utf-8"))
    except FocusConfigurationError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FocusConfigurationError("focus configuration cannot be read") from exc
    return parse_focus_config(document)


def _source_state(data: dict[str, Any]) -> dict[str, Any]:
    state = {
        "updated_at": data.get("updated_at") or now_iso(),
        "stale": bool(data.get("stale", False)),
    }
    for key in ("last_attempt_at", "error"):
        if key in data:
            state[key] = data[key]
    return state


def _temperature(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{round(value)}°C"
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "--"


def resolve_focus(document: dict[str, Any], config: FocusConfig) -> dict[str, Any]:
    widgets = widget_map(document)
    if config.source == "manual":
        data = {
            "task": config.task,
            "big_text": config.big_text or "FOCUS",
            "subtitle": config.subtitle or "Manual",
            "source": "focus-config:manual",
            "updated_at": now_iso(),
            "stale": False,
        }
    elif config.source == "todo.first":
        source = widgets["todo"]["data"]
        items = source.get("items") or []
        task = items[0].get("text") if items else "No todo task selected"
        data = {
            "task": task,
            "big_text": "NOW" if items else "CLEAR",
            "subtitle": "Todo priority",
            "source": "focus-config:todo.first",
            **_source_state(source),
        }
    elif config.source == "calendar.next":
        source = widgets["calendar"]["data"]
        events = source.get("events") or []
        event = events[0] if events else {}
        data = {
            "task": event.get("title") or "No upcoming event",
            "big_text": event.get("start") or "CLEAR",
            "subtitle": "Next event",
            "source": "focus-config:calendar.next",
            **_source_state(source),
        }
    elif config.source == "ai-status.task":
        source = widgets["ai-status"]["data"]
        data = {
            "task": source.get("task") or "No active AI task",
            "big_text": "AI",
            "subtitle": source.get("model") or "AI task",
            "source": "focus-config:ai-status.task",
            **_source_state(source),
        }
    else:
        source = widgets["weather"]["data"]
        current = source.get("current") or {}
        data = {
            "task": current.get("condition") or "No weather condition",
            "big_text": _temperature(current.get("temp_c")),
            "subtitle": source.get("location") or "Weather",
            "source": "focus-config:weather.current",
            **_source_state(source),
        }
    if config.subtitle is not None:
        data["subtitle"] = config.subtitle
    if config.big_text is not None:
        data["big_text"] = config.big_text
    return build_widget("focus", data)["data"]

