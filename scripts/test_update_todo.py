#!/usr/bin/env python3
"""Tests for explicit low-sensitivity todo widget updates."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import update_todo


BASE_WIDGETS = {
    "updated_at": "2026-06-01T00:00:00+08:00",
    "layout": "dashboard",
    "refresh_seconds": 300,
    "widgets": [
        {"slot": "glance-left", "type": "weather", "data": {"location": "Shenzhen"}},
        {"slot": "glance-right", "type": "ai-status", "data": {"session_name": "Codex"}},
        {"slot": "headline", "type": "focus", "data": {"task": "Keep focus"}},
        {"slot": "detail-left", "type": "ai-tasks", "data": {"counts": {}}},
        {"slot": "detail-middle", "type": "calendar", "data": {"events": []}},
    ],
}


class UpdateTodoTests(unittest.TestCase):
    def test_builds_only_cropped_todo_fields(self) -> None:
        args = argparse.Namespace(
            title="Todo",
            item=["Write todo updater", "Verify layout"],
            tag=["today", "qa"],
        )

        todo = update_todo.build_todo(args)

        self.assertEqual(
            todo,
            {
                "title": "Todo",
                "items": [
                    {"text": "Write todo updater", "tag": "today"},
                    {"text": "Verify layout", "tag": "qa"},
                ],
            },
        )
        self.assertNotIn("source_id", todo["items"][0])
        self.assertNotIn("completed", todo["items"][0])
        self.assertNotIn("url", todo["items"][0])

    def test_limits_todos_to_five_items(self) -> None:
        args = argparse.Namespace(
            title="Todo",
            item=["one", "two", "three", "four", "five", "six"],
            tag=[],
        )

        todo = update_todo.build_todo(args)

        self.assertEqual([item["text"] for item in todo["items"]], ["one", "two", "three", "four", "five"])

    def test_updates_todo_without_touching_other_widgets(self) -> None:
        args = argparse.Namespace(
            title="Todo",
            item=["Write todo updater"],
            tag=["today"],
        )
        document = json.loads(json.dumps(BASE_WIDGETS))
        updated = update_todo.update_todo_document(document, args)

        self.assertEqual(
            [widget["type"] for widget in updated["widgets"]],
            ["weather", "ai-status", "focus", "ai-tasks", "calendar", "todo"],
        )
        self.assertEqual(updated["widgets"][5]["slot"], "detail-right")
        self.assertEqual(updated["widgets"][5]["data"]["items"][0]["text"], "Write todo updater")
        self.assertEqual(updated["widgets"][0]["data"]["location"], "Shenzhen")
        self.assertEqual(updated["widgets"][2]["data"]["task"], "Keep focus")

    def test_cli_has_manual_only_privacy_boundary(self) -> None:
        help_text = update_todo.build_parser().format_help()

        self.assertIn("manual", help_text)
        self.assertIn("does not publish to live", help_text)
        self.assertIn("Do not pass raw Reminders", help_text)

    def test_cli_writes_web_readable_widgets_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            widgets = Path(temp_dir) / "widgets.json"
            widgets.write_text(json.dumps(BASE_WIDGETS), encoding="utf-8")

            update_todo.main(
                [
                    "--widgets",
                    str(widgets),
                    "--title",
                    "Today",
                    "--item",
                    "Todo smoke",
                    "--tag",
                    "manual",
                ]
            )

            data = json.loads(widgets.read_text(encoding="utf-8"))
            mode = widgets.stat().st_mode & 0o777

        self.assertEqual(mode, 0o644)
        self.assertEqual(data["widgets"][5]["data"]["title"], "Today")
        self.assertEqual(data["widgets"][5]["data"]["items"][0]["tag"], "manual")


if __name__ == "__main__":
    unittest.main()
