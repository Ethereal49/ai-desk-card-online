#!/usr/bin/env python3
"""Update the weather widget from wttr.in while preserving other widgets."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WIDGETS = REPO_ROOT / "web" / "widgets.json"
DEFAULT_LOCATION = "Shenzhen"
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


def text_value(items: list[dict[str, Any]] | None, default: str = "") -> str:
    if not items:
        return default
    value = items[0].get("value")
    return str(value).strip() if value is not None else default


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def forecast_condition(day: dict[str, Any]) -> str:
    hourly = day.get("hourly") or []
    if hourly:
        middle = hourly[min(len(hourly) // 2, len(hourly) - 1)]
        return text_value(middle.get("weatherDesc"), "")
    return ""


def parse_wttr_weather(payload: dict[str, Any], location: str) -> dict[str, Any]:
    current_rows = payload.get("current_condition") or []
    current = current_rows[0] if current_rows else {}
    weather_rows = payload.get("weather") or []
    generated_at = now_iso()

    forecast = []
    labels = ["Today", "Tomorrow"]
    for index, day in enumerate(weather_rows[:2]):
        forecast.append(
            {
                "day": labels[index] if index < len(labels) else str(day.get("date", "")),
                "high": int_value(day.get("maxtempC"), int_value(day.get("avgtempC"))),
                "low": int_value(day.get("mintempC"), int_value(day.get("avgtempC"))),
                "condition": forecast_condition(day),
            }
        )

    return {
        "location": location,
        "source": "wttr.in",
        "updated_at": generated_at,
        "stale": False,
        "current": {
            "temp_c": int_value(current.get("temp_C")),
            "condition": text_value(current.get("weatherDesc"), "--"),
        },
        "forecast": forecast,
    }


def fetch_wttr(location: str, timeout: float) -> dict[str, Any]:
    query = urllib.parse.quote(location)
    url = f"https://wttr.in/{query}?format=j1"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ai-desk-card-online/phase3-weather"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def find_weather_widget(widgets: list[dict[str, Any]]) -> dict[str, Any] | None:
    for widget in widgets:
        if widget.get("type") == "weather":
            return widget
    return None


def mark_weather_stale(data: dict[str, Any], location: str, generated_at: str) -> dict[str, Any]:
    existing = dict(data)
    existing.setdefault("location", location)
    existing["location"] = existing.get("location") or location
    existing["source"] = existing.get("source") or "wttr.in"
    existing["stale"] = True
    existing["last_attempt_at"] = generated_at
    return existing


def update_weather_document(
    document: dict[str, Any],
    weather_data: dict[str, Any],
) -> dict[str, Any]:
    widgets = list(document.get("widgets") or [])
    weather_widget = find_weather_widget(widgets)
    if weather_widget is None:
        widgets.insert(
            0,
            {
                "slot": "glance-left",
                "type": "weather",
                "data": weather_data,
            },
        )
    else:
        weather_widget["data"] = weather_data

    document["updated_at"] = now_iso()
    document.setdefault("layout", "dashboard")
    document.setdefault("refresh_seconds", DEFAULT_REFRESH_SECONDS)
    document["widgets"] = widgets
    return document


def build_weather_data(args: argparse.Namespace, current_data: dict[str, Any]) -> dict[str, Any]:
    generated_at = now_iso()
    try:
        if args.fixture:
            payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        else:
            payload = fetch_wttr(args.location, args.timeout)
        return parse_wttr_weather(payload, args.location)
    except Exception as exc:  # noqa: BLE001 - failure is intentionally isolated to weather.
        stale = mark_weather_stale(current_data, args.location, generated_at)
        stale["error"] = "weather unavailable"
        print(f"weather update failed: {exc}")
        return stale


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update only the weather widget in widgets.json."
    )
    parser.add_argument("--widgets", type=Path, default=DEFAULT_WIDGETS)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--fixture", type=Path, help="Read wttr.in JSON from a fixture file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document = load_widgets(args.widgets)
    current_weather = find_weather_widget(document.get("widgets") or [])
    current_data = current_weather.get("data", {}) if current_weather else {}
    weather_data = build_weather_data(args, current_data)
    atomic_write_json(args.widgets, update_weather_document(document, weather_data))
    stale_label = "stale" if weather_data.get("stale") else "fresh"
    print(f"updated weather for {weather_data.get('location', args.location)} ({stale_label})")


if __name__ == "__main__":
    main()
