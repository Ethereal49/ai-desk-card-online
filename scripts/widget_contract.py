#!/usr/bin/env python3
"""Validate and merge the public desk-card widget contract."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


SLOTS = {
    "weather": "glance-left",
    "ai-status": "glance-right",
    "focus": "headline",
    "ai-tasks": "detail-left",
    "calendar": "detail-middle",
    "todo": "detail-right",
}
OWNED_WIDGETS = frozenset({"ai-status", "focus", "ai-tasks", "calendar", "todo"})
MAX_TODO_ITEMS = 5
MAX_CALENDAR_EVENTS = 4
MAX_TEXT_LENGTH = 192
MAX_SHORT_TEXT_LENGTH = 128
PRIVACY_KEYS = frozenset(
    {
        "id",
        "identifier",
        "url",
        "uri",
        "link",
        "links",
        "notes",
        "attendees",
        "transcript",
        "prompt",
        "response",
        "preview",
        "cwd",
        "path",
        "rollout_path",
        "token",
        "api_key",
        "meeting_link",
    }
)


class ContractError(ValueError):
    """Raised when a candidate would violate the public widget contract."""


@dataclass(frozen=True)
class SourceResult:
    source: str
    owned_types: tuple[str, ...]
    health: str
    observed_at: str
    widgets: dict[str, dict[str, Any]] = field(default_factory=dict)
    error: str | None = None

    @classmethod
    def success(
        cls,
        source: str,
        widgets: dict[str, dict[str, Any]],
        observed_at: str,
    ) -> "SourceResult":
        return cls(source, tuple(widgets), "ok", observed_at, widgets)

    @classmethod
    def failure(
        cls,
        source: str,
        owned_types: tuple[str, ...],
        error: str,
        observed_at: str,
        *,
        configuration: bool = False,
    ) -> "SourceResult":
        health = "configuration_error" if configuration else "stale"
        return cls(source, owned_types, health, observed_at, error=error)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _validate_text(value: Any, field_name: str, maximum: int = MAX_TEXT_LENGTH) -> None:
    _expect(isinstance(value, str), f"{field_name} must be a string")
    _expect(bool(value.strip()), f"{field_name} must not be empty")
    _expect(len(value) <= maximum, f"{field_name} exceeds {maximum} characters")


def reject_private_keys(value: Any, path: str = "document") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in PRIVACY_KEYS:
                raise ContractError(f"private field is forbidden at {path}.{key}")
            reject_private_keys(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            reject_private_keys(nested, f"{path}[{index}]")


def _validate_freshness(data: dict[str, Any], field_name: str) -> None:
    if "source" in data:
        _validate_text(data["source"], f"{field_name}.source", MAX_SHORT_TEXT_LENGTH)
    if "updated_at" in data:
        _validate_text(data["updated_at"], f"{field_name}.updated_at", MAX_SHORT_TEXT_LENGTH)
    if "stale" in data:
        _expect(isinstance(data["stale"], bool), f"{field_name}.stale must be boolean")
    if "last_attempt_at" in data:
        _validate_text(
            data["last_attempt_at"],
            f"{field_name}.last_attempt_at",
            MAX_SHORT_TEXT_LENGTH,
        )
    if "error" in data:
        _validate_text(data["error"], f"{field_name}.error", MAX_SHORT_TEXT_LENGTH)


def _validate_widget_data(widget_type: str, data: dict[str, Any]) -> None:
    common = {"source", "updated_at", "stale", "last_attempt_at", "error"}
    allowed = {
        "focus": common | {"task", "big_text", "subtitle"},
        "todo": common | {"title", "selected_count", "total_count", "items"},
        "calendar": common | {"now_iso", "selected_count", "total_count", "events"},
        "ai-tasks": common | {"title", "counts"},
        "ai-status": common
        | {"session_name", "model", "task", "context", "elapsed_seconds", "quota"},
        "weather": common | {"location", "current", "forecast"},
    }
    _expect(set(data) <= allowed[widget_type], f"{widget_type}.data has unknown fields")
    _validate_freshness(data, widget_type)
    if widget_type == "focus":
        _validate_text(data.get("task"), "focus.task")
        _validate_text(data.get("big_text"), "focus.big_text", MAX_SHORT_TEXT_LENGTH)
        _validate_text(data.get("subtitle"), "focus.subtitle", MAX_SHORT_TEXT_LENGTH)
    elif widget_type == "todo":
        _validate_text(data.get("title"), "todo.title", MAX_SHORT_TEXT_LENGTH)
        items = data.get("items")
        _expect(isinstance(items, list), "todo.items must be a list")
        _expect(len(items) <= MAX_TODO_ITEMS, "todo.items exceeds five items")
        for index, item in enumerate(items):
            _expect(isinstance(item, dict), f"todo.items[{index}] must be an object")
            _expect(set(item) <= {"text", "tag"}, f"todo.items[{index}] has unknown fields")
            _validate_text(item.get("text"), f"todo.items[{index}].text")
            if "tag" in item:
                _validate_text(item["tag"], f"todo.items[{index}].tag", MAX_SHORT_TEXT_LENGTH)
        for count_name in ("selected_count", "total_count"):
            if count_name in data:
                _expect(
                    isinstance(data[count_name], int) and data[count_name] >= 0,
                    f"todo.{count_name} is invalid",
                )
    elif widget_type == "calendar":
        _validate_text(data.get("now_iso"), "calendar.now_iso", MAX_SHORT_TEXT_LENGTH)
        events = data.get("events")
        _expect(isinstance(events, list), "calendar.events must be a list")
        _expect(len(events) <= MAX_CALENDAR_EVENTS, "calendar.events exceeds four events")
        for index, event in enumerate(events):
            _expect(isinstance(event, dict), f"calendar.events[{index}] must be an object")
            _expect(
                set(event) <= {"start", "title", "end"},
                f"calendar.events[{index}] has unknown fields",
            )
            _validate_text(event.get("start"), f"calendar.events[{index}].start", 32)
            _validate_text(event.get("title"), f"calendar.events[{index}].title")
            if "end" in event:
                _validate_text(event["end"], f"calendar.events[{index}].end", 32)
        for count_name in ("selected_count", "total_count"):
            if count_name in data:
                _expect(
                    isinstance(data[count_name], int) and data[count_name] >= 0,
                    f"calendar.{count_name} is invalid",
                )
    elif widget_type == "ai-tasks":
        _validate_text(data.get("title"), "ai-tasks.title", MAX_SHORT_TEXT_LENGTH)
        counts = data.get("counts")
        _expect(isinstance(counts, dict), "ai-tasks.counts must be an object")
        _expect(
            set(counts) == {"running", "waiting", "blocked", "completed_today"},
            "ai-tasks.counts has the wrong fields",
        )
        for key, value in counts.items():
            _expect(isinstance(value, int) and value >= 0, f"ai-tasks.counts.{key} is invalid")
    elif widget_type == "ai-status":
        for key in ("session_name", "model", "task"):
            _validate_text(data.get(key), f"ai-status.{key}")
        _expect(
            isinstance(data.get("elapsed_seconds"), int) and data["elapsed_seconds"] >= 0,
            "ai-status.elapsed_seconds must be non-negative",
        )
        context = data.get("context")
        _expect(isinstance(context, dict), "ai-status.context must be an object")
        _expect(set(context) == {"used", "limit"}, "ai-status.context has the wrong fields")
        for key, value in context.items():
            _expect(isinstance(value, int) and value >= 0, f"ai-status.context.{key} is invalid")
        quota = data.get("quota")
        if quota is not None:
            _expect(isinstance(quota, dict), "ai-status.quota must be an object")
            _expect(
                set(quota)
                <= {
                    "source",
                    "updated_at",
                    "stale",
                    "last_attempt_at",
                    "error",
                    "five_hour",
                    "weekly",
                },
                "ai-status.quota has unknown fields",
            )
            _validate_freshness(quota, "ai-status.quota")
            for key in ("five_hour", "weekly"):
                window = quota.get(key)
                if window is None:
                    continue
                _expect(isinstance(window, dict), f"ai-status.quota.{key} must be an object")
                _expect(
                    set(window) <= {"remaining_percent", "window_minutes", "resets_at"},
                    f"ai-status.quota.{key} has unknown fields",
                )
                remaining = window.get("remaining_percent")
                _expect(
                    isinstance(remaining, (int, float))
                    and not isinstance(remaining, bool)
                    and 0 <= remaining <= 100,
                    f"ai-status.quota.{key}.remaining_percent is invalid",
                )
    elif widget_type == "weather":
        if "location" in data:
            _validate_text(data["location"], "weather.location", MAX_SHORT_TEXT_LENGTH)
        current = data.get("current")
        _expect(isinstance(current, dict), "weather.current must be an object")
        _expect(set(current) <= {"temp_c", "condition"}, "weather.current has unknown fields")
        if "condition" in current:
            _validate_text(current["condition"], "weather.current.condition")
        forecast = data.get("forecast")
        _expect(isinstance(forecast, list), "weather.forecast must be a list")
        _expect(len(forecast) <= 2, "weather.forecast exceeds two entries")
        for index, item in enumerate(forecast):
            _expect(isinstance(item, dict), f"weather.forecast[{index}] must be an object")
            _expect(
                set(item) <= {"day", "high", "low", "condition"},
                f"weather.forecast[{index}] has unknown fields",
            )
            _validate_text(item.get("day"), f"weather.forecast[{index}].day", 32)
            _validate_text(item.get("condition"), f"weather.forecast[{index}].condition")


def validate_widget(widget: Any, *, owned_only: bool = False) -> None:
    _expect(isinstance(widget, dict), "widget must be an object")
    _expect(set(widget) == {"slot", "type", "data"}, "widget has unknown fields")
    widget_type = widget.get("type")
    _expect(widget_type in SLOTS, "widget type is unsupported")
    if owned_only:
        _expect(widget_type in OWNED_WIDGETS, "publisher does not own this widget")
    _expect(widget.get("slot") == SLOTS[widget_type], f"wrong slot for {widget_type}")
    data = widget.get("data")
    _expect(isinstance(data, dict), f"{widget_type}.data must be an object")
    reject_private_keys(data, f"{widget_type}.data")
    _validate_widget_data(widget_type, data)


def validate_document(document: Any, *, require_all: bool = True) -> None:
    _expect(isinstance(document, dict), "document must be an object")
    _expect(
        set(document) == {"updated_at", "layout", "refresh_seconds", "widgets"},
        "document has unknown or missing top-level fields",
    )
    _validate_text(document.get("updated_at"), "updated_at", MAX_SHORT_TEXT_LENGTH)
    _expect(document.get("layout") == "dashboard", "layout must be dashboard")
    refresh_seconds = document.get("refresh_seconds")
    _expect(
        isinstance(refresh_seconds, int) and 30 <= refresh_seconds <= 86400,
        "refresh_seconds is invalid",
    )
    widgets = document.get("widgets")
    _expect(isinstance(widgets, list), "widgets must be a list")
    seen_types: set[str] = set()
    seen_slots: set[str] = set()
    for widget in widgets:
        validate_widget(widget)
        widget_type = widget["type"]
        slot = widget["slot"]
        _expect(widget_type not in seen_types, f"duplicate widget type: {widget_type}")
        _expect(slot not in seen_slots, f"duplicate widget slot: {slot}")
        seen_types.add(widget_type)
        seen_slots.add(slot)
    if require_all:
        _expect(seen_types == set(SLOTS), "document must contain all six widgets")


def widget_map(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {widget["type"]: widget for widget in document.get("widgets", [])}


def build_widget(widget_type: str, data: dict[str, Any]) -> dict[str, Any]:
    widget = {"slot": SLOTS[widget_type], "type": widget_type, "data": data}
    validate_widget(widget, owned_only=widget_type in OWNED_WIDGETS)
    return widget


def _stale_data(
    existing: dict[str, Any],
    source: str,
    observed_at: str,
    error: str,
) -> dict[str, Any]:
    data = copy.deepcopy(existing)
    data.setdefault("source", source)
    data["stale"] = True
    data["last_attempt_at"] = observed_at
    data["error"] = error
    return data


def merge_source_results(
    baseline: dict[str, Any],
    results: list[SourceResult],
) -> tuple[dict[str, Any], list[str]]:
    validate_document(baseline)
    merged = copy.deepcopy(baseline)
    by_type = widget_map(merged)

    for result in results:
        _expect(result.health in {"ok", "stale"}, "configuration errors cannot be merged")
        for widget_type in result.owned_types:
            _expect(widget_type in OWNED_WIDGETS, f"source cannot own {widget_type}")
            if result.health == "ok":
                _expect(widget_type in result.widgets, f"source omitted {widget_type}")
                data = copy.deepcopy(result.widgets[widget_type])
                data["source"] = result.source
                data["updated_at"] = result.observed_at
                data["stale"] = False
                data.pop("last_attempt_at", None)
                data.pop("error", None)
            else:
                data = _stale_data(
                    by_type[widget_type]["data"],
                    result.source,
                    result.observed_at,
                    result.error or "source unavailable",
                )
            by_type[widget_type] = build_widget(widget_type, data)

    merged["widgets"] = [by_type[widget_type] for widget_type in SLOTS]
    validate_document(merged)
    baseline_widgets = widget_map(baseline)
    changed = [
        widget_type
        for widget_type in SLOTS
        if by_type[widget_type] != baseline_widgets[widget_type]
    ]
    return merged, changed


def merge_quota(
    candidate: dict[str, Any],
    quota: dict[str, Any] | None,
    observed_at: str,
    existing_quota: dict[str, Any] | None = None,
) -> None:
    ai_status = widget_map(candidate)["ai-status"]["data"]
    if quota is None:
        prior = copy.deepcopy(existing_quota or ai_status.get("quota") or {})
        prior.setdefault("source", "codex-rollout")
        prior["stale"] = True
        prior["last_attempt_at"] = observed_at
        prior["error"] = "quota unavailable"
        ai_status["quota"] = prior
    else:
        ai_status["quota"] = copy.deepcopy(quota)
    validate_widget(widget_map(candidate)["ai-status"])


def owned_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    validate_document(candidate)
    widgets = [
        copy.deepcopy(widget)
        for widget in candidate["widgets"]
        if widget["type"] in OWNED_WIDGETS
    ]
    for widget in widgets:
        validate_widget(widget, owned_only=True)
    return {"widgets": widgets}
