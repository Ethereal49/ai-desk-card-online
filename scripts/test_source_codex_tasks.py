import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import source_codex_tasks


NOW = datetime(2026, 7, 23, 8, 0, tzinfo=timezone.utc)


def lifecycle(latest_type=None, minutes_ago=0, completed=False):
    latest_at = NOW - timedelta(minutes=minutes_ago) if latest_type else None
    return source_codex_tasks.LifecycleSummary(
        latest_type,
        latest_at,
        latest_at if latest_type == "task_started" else None,
        (NOW,) if completed else (),
    )


def thread(identifier, title, minutes_ago=0, archived=0):
    updated = NOW - timedelta(minutes=minutes_ago)
    return {
        "id": identifier,
        "rollout_path": "/private/path",
        "created_at_ms": int((updated - timedelta(hours=1)).timestamp() * 1000),
        "updated_at_ms": int(updated.timestamp() * 1000),
        "title": title,
        "tokens_used": 123,
        "archived": archived,
        "model": "gpt-test",
    }


class SourceCodexTasksTests(unittest.TestCase):
    def test_lifecycle_parser_reads_only_bounded_event_types(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout.jsonl"
            path.write_text(
                json.dumps({"type": "message", "payload": {"text": "private transcript"}})
                + "\n"
                + json.dumps({"timestamp": "2026-07-23T07:00:00Z", "type": "event_msg", "payload": {"type": "task_complete", "private": "secret"}})
                + "\n"
                + json.dumps({"timestamp": "2026-07-23T07:30:00Z", "type": "event_msg", "payload": {"type": "task_started", "private": "secret"}})
                + "\n",
                encoding="utf-8",
            )
            summary = source_codex_tasks.lifecycle_summary(path, tail_bytes=4096)

        self.assertEqual(summary.latest_type, "task_started")
        self.assertEqual(summary.current_started_at, datetime(2026, 7, 23, 7, 30, tzinfo=timezone.utc))
        self.assertEqual(summary.completed_at, (datetime(2026, 7, 23, 7, 0, tzinfo=timezone.utc),))
        self.assertNotIn("private", repr(summary))

    def test_state_precedence_and_running_guard(self):
        recent = thread("recent", "Recent", minutes_ago=5)
        stale = thread("stale", "Stale", minutes_ago=60)
        self.assertEqual(
            source_codex_tasks.classify_thread(recent, {"status": "blocked"}, lifecycle("task_started", 5), now=NOW),
            "running",
        )
        self.assertEqual(
            source_codex_tasks.classify_thread(stale, {"status": "blocked"}, lifecycle("task_started", 60), now=NOW),
            "blocked",
        )
        self.assertEqual(
            source_codex_tasks.classify_thread(recent, {"status": "paused"}, lifecycle("task_complete", 5), now=NOW),
            "waiting",
        )
        self.assertEqual(
            source_codex_tasks.classify_thread(recent, None, lifecycle("turn_aborted", 5), now=NOW),
            "waiting",
        )
        self.assertIsNone(
            source_codex_tasks.classify_thread(stale, None, lifecycle("task_complete", 25 * 60), now=NOW)
        )

    def test_projection_counts_distinct_completion_and_selects_recent_unfinished(self):
        threads = [thread("one", "Visible newest", 1), thread("two", "Visible blocked", 2), thread("done", "Done", 3, archived=1)]
        goals = {"two": {"status": "blocked", "updated_at_ms": int(NOW.timestamp() * 1000)}}
        lifecycles = {
            "one": lifecycle("task_started", 1, completed=True),
            "two": lifecycle("task_complete", 2),
            "done": lifecycle("task_complete", 3, completed=True),
        }

        widgets = source_codex_tasks.project_codex(threads, goals, lifecycles, now=NOW)

        self.assertEqual(widgets["ai-status"]["task"], "Visible newest")
        self.assertEqual(widgets["ai-status"]["session_name"], "RUNNING")
        self.assertEqual(widgets["ai-tasks"]["counts"], {"running": 1, "waiting": 0, "blocked": 1, "completed_today": 2})
        output = json.dumps(widgets)
        self.assertNotIn("/private/path", output)
        self.assertNotIn('"id"', output)

    def test_schema_checked_read_only_queries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state = root / "state.sqlite"
            goals = root / "goals.sqlite"
            with sqlite3.connect(state) as connection:
                connection.execute("CREATE TABLE threads (id TEXT, rollout_path TEXT, created_at_ms INTEGER, updated_at_ms INTEGER, title TEXT, tokens_used INTEGER, archived INTEGER, model TEXT)")
                connection.execute("INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ("id", str(root / "rollout.jsonl"), 1, 2, "Title", 3, 0, "Codex"))
            with sqlite3.connect(goals) as connection:
                connection.execute("CREATE TABLE thread_goals (thread_id TEXT, status TEXT, updated_at_ms INTEGER)")
                connection.execute("INSERT INTO thread_goals VALUES ('id', 'active', 2)")

            self.assertEqual(source_codex_tasks.read_threads(state)[0]["title"], "Title")
            self.assertEqual(source_codex_tasks.read_goals(goals)["id"]["status"], "active")

            broken = root / "broken.sqlite"
            with sqlite3.connect(broken) as connection:
                connection.execute("CREATE TABLE threads (id TEXT)")
            with self.assertRaises(source_codex_tasks.CodexSourceError):
                source_codex_tasks.read_threads(broken)


if __name__ == "__main__":
    unittest.main()
