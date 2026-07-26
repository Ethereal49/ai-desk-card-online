#!/usr/bin/env python3
"""Tests for the local Codex rollout quota updater."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import update_codex_usage


BASE_WIDGETS = {
    "updated_at": "2026-07-12T00:00:00+08:00",
    "layout": "dashboard",
    "refresh_seconds": 300,
    "widgets": [
        {"slot": "glance-left", "type": "weather", "data": {"location": "Shenzhen"}},
        {
            "slot": "glance-right",
            "type": "ai-status",
            "data": {
                "session_name": "Codex task",
                "task": "Keep session fields",
                "context": {"used": 1000, "limit": 30000},
            },
        },
        {"slot": "headline", "type": "focus", "data": {"task": "Keep focus"}},
    ],
}


def event_line(rate_limits: dict, timestamp: str = "2026-07-12T12:00:00Z") -> str:
    return json.dumps(
        {
            "timestamp": timestamp,
            "type": "event_msg",
            "payload": {
                "type": "token_count",
                "rate_limits": rate_limits,
            },
        }
    )


class UpdateCodexUsageTests(unittest.TestCase):
    def test_classifies_windows_by_duration_not_slot_name(self) -> None:
        event = update_codex_usage.parse_rate_limit_event(
            event_line(
                {
                    "primary": {
                        "used_percent": 25,
                        "window_minutes": 10080,
                        "resets_at": 200,
                    },
                    "secondary": {
                        "used_percentage": 10,
                        "window_minutes": 300,
                        "resets_at": 100,
                    },
                }
            )
        )

        self.assertEqual(event["windows"]["five_hour"]["remaining_percent"], 90.0)
        self.assertEqual(event["windows"]["weekly"]["remaining_percent"], 75.0)
        self.assertEqual(event["windows"]["five_hour"]["resets_at"], 100)

    def test_supports_api_style_window_field_names(self) -> None:
        event = update_codex_usage.parse_rate_limit_event(
            event_line(
                {
                    "primary_window": {
                        "used_percent": 30,
                        "limit_window_seconds": 18000,
                        "reset_at": 300,
                    },
                    "secondary_window": {
                        "used_percent": 40,
                        "limit_window_seconds": 604800,
                        "reset_at": 400,
                    },
                }
            )
        )

        self.assertEqual(event["windows"]["five_hour"]["window_minutes"], 300)
        self.assertEqual(event["windows"]["weekly"]["window_minutes"], 10080)

    def test_free_plan_single_weekly_window_is_not_misclassified(self) -> None:
        event = update_codex_usage.parse_rate_limit_event(
            event_line(
                {
                    "primary": {
                        "used_percent": 20,
                        "window_minutes": 10080,
                    }
                }
            )
        )

        self.assertNotIn("five_hour", event["windows"])
        self.assertEqual(event["windows"]["weekly"]["remaining_percent"], 80.0)

    def test_latest_rollout_event_wins_and_raw_fields_are_not_copied(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            older = root / "rollout-old.jsonl"
            newer = root / "rollout-new.jsonl"
            older.write_text(
                event_line({"primary": {"used_percent": 70, "window_minutes": 300}}) + "\n",
                encoding="utf-8",
            )
            newer.write_text(
                json.dumps({"type": "message", "secret": "must-not-copy"})
                + "\n"
                + event_line(
                    {"primary": {"used_percent": 12, "window_minutes": 300}},
                    "2026-07-12T13:00:00Z",
                )
                + "\n",
                encoding="utf-8",
            )
            os.utime(older, (1, 1))
            os.utime(newer, (2, 2))

            quota = update_codex_usage.find_latest_quota(
                root,
                max_files=80,
                tail_bytes=4096,
                current_time=datetime(2026, 7, 12, 13, 5, tzinfo=timezone.utc),
            )

        self.assertEqual(quota["five_hour"]["remaining_percent"], 88.0)
        self.assertEqual(quota["source"], "codex-rollout")
        self.assertFalse(quota["stale"])
        self.assertNotIn("secret", json.dumps(quota))

    def test_event_timestamp_wins_over_rollout_file_modification_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            old_file = root / "rollout-recently-touched.jsonl"
            new_file = root / "rollout-older-file.jsonl"
            old_file.write_text(
                event_line(
                    {"primary": {"used_percent": 80, "window_minutes": 300}},
                    "2026-07-12T10:00:00Z",
                )
                + "\n",
                encoding="utf-8",
            )
            new_file.write_text(
                event_line(
                    {"primary": {"used_percent": 20, "window_minutes": 300}},
                    "2026-07-12T12:00:00Z",
                )
                + "\n",
                encoding="utf-8",
            )
            os.utime(old_file, (3, 3))
            os.utime(new_file, (1, 1))

            quota = update_codex_usage.find_latest_quota(
                root,
                max_files=80,
                tail_bytes=4096,
                current_time=datetime(2026, 7, 12, 12, 5, tzinfo=timezone.utc),
            )

        self.assertEqual(quota["updated_at"], "2026-07-12T12:00:00Z")
        self.assertEqual(quota["five_hour"]["remaining_percent"], 80.0)

    def test_old_rollout_event_is_marked_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rollout = Path(temp_dir) / "rollout-old.jsonl"
            rollout.write_text(
                event_line(
                    {"primary": {"used_percent": 12, "window_minutes": 300}},
                    "2026-07-12T10:00:00Z",
                )
                + "\n",
                encoding="utf-8",
            )

            quota = update_codex_usage.find_latest_quota(
                Path(temp_dir),
                max_files=80,
                tail_bytes=4096,
                current_time=datetime(2026, 7, 12, 13, 0, tzinfo=timezone.utc),
            )

        self.assertTrue(quota["stale"])

    def test_scans_backwards_past_the_last_chunk_for_latest_valid_quota(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rollout = Path(temp_dir) / "rollout-large.jsonl"
            valid = event_line(
                {"primary": {"used_percent": 22, "window_minutes": 300}},
                "2026-07-12T12:55:00Z",
            )
            empty = event_line(
                {"primary": None, "secondary": None},
                "2026-07-12T12:59:00Z",
            )
            filler = json.dumps({"type": "message", "payload": "x" * 300})
            rollout.write_text(
                valid + "\n" + "\n".join([filler] * 20) + "\n" + empty + "\n",
                encoding="utf-8",
            )

            event = update_codex_usage.latest_event_in_file(rollout, tail_bytes=1024)

        self.assertEqual(event["timestamp"], "2026-07-12T12:55:00Z")
        self.assertEqual(event["windows"]["five_hour"]["remaining_percent"], 78.0)

    def test_updates_only_quota_and_preserves_existing_widgets(self) -> None:
        document = json.loads(json.dumps(BASE_WIDGETS))
        quota = {
            "source": "codex-rollout",
            "updated_at": "2026-07-12T13:00:00Z",
            "stale": False,
            "five_hour": {"remaining_percent": 88.0},
        }

        updated = update_codex_usage.update_codex_quota_document(document, quota)
        widgets = {widget["type"]: widget for widget in updated["widgets"]}

        self.assertEqual(widgets["ai-status"]["data"]["task"], "Keep session fields")
        self.assertEqual(widgets["ai-status"]["data"]["quota"], quota)
        self.assertEqual(widgets["weather"]["data"]["location"], "Shenzhen")
        self.assertEqual(widgets["focus"]["data"]["task"], "Keep focus")

    def test_missing_event_preserves_old_quota_and_marks_it_stale(self) -> None:
        old = {
            "source": "codex-rollout",
            "updated_at": "2026-07-12T10:00:00Z",
            "stale": False,
            "weekly": {"remaining_percent": 60.0},
        }

        stale = update_codex_usage.stale_quota(old)

        self.assertTrue(stale["stale"])
        self.assertEqual(stale["weekly"]["remaining_percent"], 60.0)
        self.assertEqual(stale["error"], "quota unavailable")

    def test_cli_writes_atomic_web_readable_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sessions = root / "sessions"
            sessions.mkdir()
            rollout = sessions / "rollout-test.jsonl"
            rollout.write_text(
                event_line({"primary": {"used_percent": 15, "window_minutes": 300}}) + "\n",
                encoding="utf-8",
            )
            widgets = root / "widgets.json"
            widgets.write_text(json.dumps(BASE_WIDGETS), encoding="utf-8")

            update_codex_usage.main(
                ["--widgets", str(widgets), "--sessions", str(sessions)]
            )
            data = json.loads(widgets.read_text(encoding="utf-8"))
            mode = widgets.stat().st_mode & 0o777

        ai_status = next(widget for widget in data["widgets"] if widget["type"] == "ai-status")
        self.assertEqual(mode, 0o644)
        self.assertEqual(ai_status["data"]["quota"]["five_hour"]["remaining_percent"], 85.0)


if __name__ == "__main__":
    unittest.main()
