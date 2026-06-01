#!/usr/bin/env python3
"""Tests for explicit low-sensitivity AI session widget updates."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import update_ai_session


BASE_WIDGETS = {
    "updated_at": "2026-06-01T00:00:00+08:00",
    "layout": "dashboard",
    "refresh_seconds": 300,
    "widgets": [
        {"slot": "glance-left", "type": "weather", "data": {"location": "Shenzhen"}},
        {
            "slot": "headline",
            "type": "focus",
            "data": {"task": "Keep focus", "big_text": "READY"},
        },
        {"slot": "detail-middle", "type": "calendar", "data": {"events": []}},
        {"slot": "detail-right", "type": "todo", "data": {"items": []}},
    ],
}


class UpdateAiSessionTests(unittest.TestCase):
    def test_cli_has_manual_only_calling_convention(self) -> None:
        help_text = update_ai_session.build_parser().format_help()

        self.assertIn("manual", help_text)
        self.assertIn("does not publish to live", help_text)
        self.assertIn("do not pass transcripts", help_text)
        self.assertNotIn("AI_DESK_CARD_AUTH_PASSWORD", help_text)

    def test_builds_only_low_sensitivity_ai_widgets_from_cli_args(self) -> None:
        args = argparse.Namespace(
            session_name="Codex work turn",
            model="Codex",
            task="Define explicit AI session update",
            context_used=2000,
            context_limit=30000,
            elapsed_seconds=600,
            running=1,
            waiting=2,
            blocked=0,
            completed_today=3,
        )

        status = update_ai_session.build_ai_status(args)
        tasks = update_ai_session.build_ai_tasks(args)

        self.assertEqual(status["session_name"], "Codex work turn")
        self.assertEqual(status["context"], {"used": 2000, "limit": 30000})
        self.assertNotIn("last_message_preview", status)
        self.assertNotIn("transcript", status)
        self.assertEqual(
            tasks["counts"],
            {
                "running": 1,
                "waiting": 2,
                "blocked": 0,
                "completed_today": 3,
            },
        )

    def test_updates_ai_widgets_without_touching_other_widgets(self) -> None:
        args = argparse.Namespace(
            session_name="Codex work turn",
            model="Codex",
            task="Define explicit AI session update",
            context_used=2000,
            context_limit=30000,
            elapsed_seconds=600,
            running=1,
            waiting=2,
            blocked=0,
            completed_today=3,
        )
        document = json.loads(json.dumps(BASE_WIDGETS))
        updated = update_ai_session.update_ai_session_document(document, args)

        self.assertEqual(
            [widget["type"] for widget in updated["widgets"]],
            ["weather", "ai-status", "focus", "ai-tasks", "calendar", "todo"],
        )
        self.assertEqual(updated["widgets"][0]["data"]["location"], "Shenzhen")
        self.assertEqual(updated["widgets"][2]["data"]["task"], "Keep focus")
        self.assertEqual(updated["widgets"][1]["slot"], "glance-right")
        self.assertEqual(updated["widgets"][3]["slot"], "detail-left")

    def test_cli_writes_web_readable_widgets_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            widgets = Path(temp_dir) / "widgets.json"
            widgets.write_text(json.dumps(BASE_WIDGETS), encoding="utf-8")

            update_ai_session.main(
                [
                    "--widgets",
                    str(widgets),
                    "--session-name",
                    "Codex smoke",
                    "--task",
                    "Run explicit update smoke",
                    "--context-used",
                    "1234",
                    "--context-limit",
                    "30000",
                    "--running",
                    "1",
                    "--waiting",
                    "0",
                    "--blocked",
                    "0",
                    "--completed-today",
                    "1",
                ]
            )

            data = json.loads(widgets.read_text(encoding="utf-8"))
            mode = widgets.stat().st_mode & 0o777

        self.assertEqual(mode, 0o644)
        self.assertEqual(data["widgets"][1]["data"]["session_name"], "Codex smoke")
        self.assertEqual(data["widgets"][3]["data"]["counts"]["completed_today"], 1)


if __name__ == "__main__":
    unittest.main()
