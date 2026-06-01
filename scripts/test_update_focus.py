#!/usr/bin/env python3
"""Tests for explicit low-sensitivity focus widget updates."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import update_focus


BASE_WIDGETS = {
    "updated_at": "2026-06-01T00:00:00+08:00",
    "layout": "dashboard",
    "refresh_seconds": 300,
    "widgets": [
        {"slot": "glance-left", "type": "weather", "data": {"location": "Shenzhen"}},
        {"slot": "glance-right", "type": "ai-status", "data": {"session_name": "Codex"}},
        {"slot": "detail-left", "type": "ai-tasks", "data": {"counts": {}}},
        {"slot": "detail-middle", "type": "calendar", "data": {"events": []}},
        {"slot": "detail-right", "type": "todo", "data": {"items": []}},
    ],
}


class UpdateFocusTests(unittest.TestCase):
    def test_builds_only_cropped_focus_fields(self) -> None:
        args = argparse.Namespace(
            task="Write the focus updater",
            big_text="45m",
            subtitle="current focus",
        )

        focus = update_focus.build_focus(args)

        self.assertEqual(
            focus,
            {
                "task": "Write the focus updater",
                "big_text": "45m",
                "subtitle": "current focus",
            },
        )
        self.assertNotIn("notes", focus)
        self.assertNotIn("source_url", focus)

    def test_updates_focus_without_touching_other_widgets(self) -> None:
        args = argparse.Namespace(
            task="Write the focus updater",
            big_text="45m",
            subtitle="current focus",
        )
        document = json.loads(json.dumps(BASE_WIDGETS))
        updated = update_focus.update_focus_document(document, args)

        self.assertEqual(
            [widget["type"] for widget in updated["widgets"]],
            ["weather", "ai-status", "focus", "ai-tasks", "calendar", "todo"],
        )
        self.assertEqual(updated["widgets"][2]["slot"], "headline")
        self.assertEqual(updated["widgets"][2]["data"]["task"], "Write the focus updater")
        self.assertEqual(updated["widgets"][0]["data"]["location"], "Shenzhen")
        self.assertEqual(updated["widgets"][3]["type"], "ai-tasks")

    def test_cli_writes_web_readable_widgets_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            widgets = Path(temp_dir) / "widgets.json"
            widgets.write_text(json.dumps(BASE_WIDGETS), encoding="utf-8")

            update_focus.main(
                [
                    "--widgets",
                    str(widgets),
                    "--task",
                    "Focus smoke",
                    "--big-text",
                    "NOW",
                    "--subtitle",
                    "manual focus",
                ]
            )

            data = json.loads(widgets.read_text(encoding="utf-8"))
            mode = widgets.stat().st_mode & 0o777

        self.assertEqual(mode, 0o644)
        self.assertEqual(data["widgets"][2]["data"]["task"], "Focus smoke")
        self.assertEqual(data["widgets"][2]["data"]["big_text"], "NOW")


if __name__ == "__main__":
    unittest.main()
