#!/usr/bin/env python3
"""Generate a complete public-demo widgets.json for the static desk card."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "web" / "widgets.json"
DEFAULT_REFRESH_SECONDS = 300


def build_widgets(args: argparse.Namespace) -> dict:
    now = datetime.now(timezone.utc).astimezone()
    todos = args.todo or [
        "Verify IP-only demo page",
        "Keep widgets public",
        "Review next product signal",
    ]

    return {
        "updated_at": now.isoformat(timespec="seconds"),
        "layout": "dashboard",
        "refresh_seconds": DEFAULT_REFRESH_SECONDS,
        "widgets": [
            {
                "slot": "hero",
                "type": "focus",
                "data": {
                    "task": args.focus,
                    "big_text": args.focus_state,
                    "subtitle": "public demo",
                },
            },
            {
                "slot": "top-right",
                "type": "weather",
                "data": {
                    "location": args.weather_location,
                    "current": {
                        "temp_c": args.weather_temp,
                        "condition": args.weather_condition,
                    },
                    "forecast": [
                        {
                            "day": "Today",
                            "high": args.weather_temp + 2,
                            "low": args.weather_temp - 4,
                            "condition": args.weather_condition,
                        },
                        {
                            "day": "Tomorrow",
                            "high": args.weather_temp + 1,
                            "low": args.weather_temp - 3,
                            "condition": "Public demo",
                        },
                    ],
                },
            },
            {
                "slot": "middle",
                "type": "calendar",
                "data": {
                    "now_iso": now.isoformat(timespec="seconds"),
                    "events": [
                        {"start": "09:30", "title": "Public demo check"},
                        {"start": "14:00", "title": "Update widgets.json"},
                        {"start": "20:30", "title": "Review next step"},
                    ],
                },
            },
            {
                "slot": "bottom",
                "type": "todo",
                "data": {
                    "title": "Todo",
                    "items": [
                        {"text": item, "tag": "demo"} for item in todos[:4]
                    ],
                },
            },
        ],
    }


def atomic_write_json(path: Path, data: dict) -> None:
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
    os.replace(temp_name, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a complete public-demo web/widgets.json file."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--focus", default="Review the AI desk card")
    parser.add_argument("--focus-state", default="READY")
    parser.add_argument("--todo", action="append", default=[])
    parser.add_argument("--weather-location", default="Local")
    parser.add_argument("--weather-condition", default="Clear")
    parser.add_argument("--weather-temp", type=int, default=24)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    atomic_write_json(args.output, build_widgets(args))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
