#!/usr/bin/env python3
"""Tests for explicit low-sensitivity calendar widget updates."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import update_calendar


BASE_WIDGETS = {
    "updated_at": "2026-06-01T00:00:00+08:00",
    "layout": "dashboard",
    "refresh_seconds": 300,
    "widgets": [
        {"slot": "glance-left", "type": "weather", "data": {"location": "Shenzhen"}},
        {"slot": "glance-right", "type": "ai-status", "data": {"session_name": "Codex"}},
        {"slot": "headline", "type": "focus", "data": {"task": "Keep focus"}},
        {"slot": "detail-left", "type": "ai-tasks", "data": {"counts": {}}},
        {"slot": "detail-right", "type": "todo", "data": {"items": []}},
    ],
}


class UpdateCalendarTests(unittest.TestCase):
    def test_builds_only_cropped_calendar_fields(self) -> None:
        args = argparse.Namespace(
            event=[
                "09:30|Deep work|11:00",
                "14:00|Project checkpoint|",
            ],
        )

        calendar = update_calendar.build_calendar(args)

        self.assertEqual(
            calendar["events"],
            [
                {"start": "09:30", "title": "Deep work", "end": "11:00"},
                {"start": "14:00", "title": "Project checkpoint"},
            ],
        )
        self.assertIn("now_iso", calendar)
        self.assertNotIn("location", calendar["events"][0])
        self.assertNotIn("attendees", calendar["events"][0])
        self.assertNotIn("meet_url", calendar["events"][0])

    def test_limits_calendar_to_four_events(self) -> None:
        args = argparse.Namespace(
            event=[
                "09:00|one|",
                "10:00|two|",
                "11:00|three|",
                "12:00|four|",
                "13:00|five|",
            ],
        )

        calendar = update_calendar.build_calendar(args)

        self.assertEqual([event["title"] for event in calendar["events"]], ["one", "two", "three", "four"])

    def test_updates_calendar_without_touching_other_widgets(self) -> None:
        args = argparse.Namespace(event=["09:30|Deep work|11:00"])
        document = json.loads(json.dumps(BASE_WIDGETS))
        updated = update_calendar.update_calendar_document(document, args)

        self.assertEqual(
            [widget["type"] for widget in updated["widgets"]],
            ["weather", "ai-status", "focus", "ai-tasks", "calendar", "todo"],
        )
        self.assertEqual(updated["widgets"][4]["slot"], "detail-middle")
        self.assertEqual(updated["widgets"][4]["data"]["events"][0]["title"], "Deep work")
        self.assertEqual(updated["widgets"][0]["data"]["location"], "Shenzhen")
        self.assertEqual(updated["widgets"][5]["type"], "todo")

    def test_rejects_malformed_event_argument(self) -> None:
        args = argparse.Namespace(event=["09:30|Missing end separator?"])

        with self.assertRaises(ValueError):
            update_calendar.build_calendar(args)

    def test_cli_has_manual_only_privacy_boundary(self) -> None:
        help_text = update_calendar.build_parser().format_help()

        self.assertIn("manual", help_text)
        self.assertIn("does not publish to live", help_text)
        self.assertIn("raw Calendar", help_text)

    def test_cli_writes_web_readable_widgets_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            widgets = Path(temp_dir) / "widgets.json"
            widgets.write_text(json.dumps(BASE_WIDGETS), encoding="utf-8")

            update_calendar.main(
                [
                    "--widgets",
                    str(widgets),
                    "--event",
                    "09:30|Calendar smoke|10:00",
                ]
            )

            data = json.loads(widgets.read_text(encoding="utf-8"))
            mode = widgets.stat().st_mode & 0o777

        self.assertEqual(mode, 0o644)
        self.assertEqual(data["widgets"][4]["data"]["events"][0]["title"], "Calendar smoke")


if __name__ == "__main__":
    unittest.main()
