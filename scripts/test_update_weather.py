#!/usr/bin/env python3
"""Tests for the Phase 3 wttr.in weather updater."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import update_weather


BASE_WIDGETS = {
    "updated_at": "2026-05-31T00:00:00+08:00",
    "layout": "dashboard",
    "refresh_seconds": 300,
    "widgets": [
        {"slot": "hero", "type": "focus", "data": {"task": "Keep focus"}},
        {
            "slot": "top-right",
            "type": "weather",
            "data": {
                "location": "Shanghai",
                "current": {"temp_c": 24, "condition": "Clear"},
                "forecast": [],
            },
        },
        {"slot": "bottom", "type": "todo", "data": {"items": []}},
    ],
}


WTTR_FIXTURE = {
    "current_condition": [
        {
            "temp_C": "26",
            "weatherDesc": [{"value": "Clear "}],
        }
    ],
    "weather": [
        {
            "date": "2026-05-31",
            "maxtempC": "29",
            "mintempC": "24",
            "hourly": [{"weatherDesc": [{"value": "Light rain shower"}]}],
        },
        {
            "date": "2026-06-01",
            "maxtempC": "30",
            "mintempC": "25",
            "hourly": [{"weatherDesc": [{"value": "Cloudy"}]}],
        },
    ],
}


class UpdateWeatherTests(unittest.TestCase):
    def test_parses_wttr_payload(self) -> None:
        data = update_weather.parse_wttr_weather(WTTR_FIXTURE, "Shenzhen")

        self.assertEqual(data["location"], "Shenzhen")
        self.assertEqual(data["source"], "wttr.in")
        self.assertFalse(data["stale"])
        self.assertEqual(data["current"]["temp_c"], 26)
        self.assertEqual(data["current"]["condition"], "Clear")
        self.assertEqual(data["forecast"][0]["high"], 29)
        self.assertEqual(data["forecast"][1]["condition"], "Cloudy")

    def test_updates_only_weather_widget(self) -> None:
        document = json.loads(json.dumps(BASE_WIDGETS))
        weather = update_weather.parse_wttr_weather(WTTR_FIXTURE, "Shenzhen")
        updated = update_weather.update_weather_document(document, weather)

        self.assertEqual(updated["widgets"][0]["data"]["task"], "Keep focus")
        self.assertEqual(updated["widgets"][1]["type"], "weather")
        self.assertEqual(updated["widgets"][1]["data"]["location"], "Shenzhen")
        self.assertEqual(updated["widgets"][2]["type"], "todo")

    def test_failed_update_marks_existing_weather_stale(self) -> None:
        existing = BASE_WIDGETS["widgets"][1]["data"]
        stale = update_weather.mark_weather_stale(existing, "Shenzhen", "now")

        self.assertTrue(stale["stale"])
        self.assertEqual(stale["last_attempt_at"], "now")
        self.assertEqual(stale["current"]["temp_c"], 24)

    def test_cli_fixture_writes_widgets_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            widgets = Path(temp_dir) / "widgets.json"
            fixture = Path(temp_dir) / "wttr.json"
            widgets.write_text(json.dumps(BASE_WIDGETS), encoding="utf-8")
            fixture.write_text(json.dumps(WTTR_FIXTURE), encoding="utf-8")

            args = update_weather.argparse.Namespace(
                widgets=widgets,
                location="Shenzhen",
                timeout=1,
                fixture=fixture,
            )
            document = update_weather.load_widgets(args.widgets)
            current_weather = update_weather.find_weather_widget(document["widgets"])
            weather_data = update_weather.build_weather_data(
                args,
                current_weather["data"],
            )
            update_weather.atomic_write_json(
                args.widgets,
                update_weather.update_weather_document(document, weather_data),
            )

            data = json.loads(widgets.read_text(encoding="utf-8"))

        self.assertEqual(data["widgets"][1]["data"]["location"], "Shenzhen")
        self.assertEqual(data["widgets"][1]["data"]["source"], "wttr.in")

    def test_atomic_write_uses_web_readable_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "widgets.json"
            update_weather.atomic_write_json(output, {"ok": True})

            mode = output.stat().st_mode & 0o777

        self.assertEqual(mode, 0o644)


if __name__ == "__main__":
    unittest.main()
