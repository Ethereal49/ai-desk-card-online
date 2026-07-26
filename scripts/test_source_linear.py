import io
import json
import tempfile
import unittest
import urllib.error
from datetime import date
from pathlib import Path

import source_linear


def issue(
    identifier,
    title,
    *,
    priority=3,
    due=None,
    state="unstarted",
    parent=None,
    team="LIFE",
    updated="2026-07-23T00:00:00Z",
):
    return {
        "id": "id-" + identifier,
        "identifier": identifier,
        "title": title,
        "priority": priority,
        "dueDate": due,
        "updatedAt": updated,
        "parent": {"id": parent} if parent else None,
        "state": {"type": state},
        "team": {"key": team},
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class SourceLinearTests(unittest.TestCase):
    def test_environment_precedes_local_files_and_local_fallback_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env").write_text("LINEAR_API_KEY=base\n", encoding="utf-8")
            (root / ".env.local").write_text("LINEAR_API_KEY=local\n", encoding="utf-8")
            self.assertEqual(source_linear.load_api_key(root, {}), "local")
            self.assertEqual(
                source_linear.load_api_key(root, {"LINEAR_API_KEY": "exported"}),
                "exported",
            )

    def test_missing_or_empty_key_fails_without_exposing_a_value(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(source_linear.LinearConfigurationError, "credential missing"):
                source_linear.load_api_key(Path(temp_dir), {"LINEAR_API_KEY": ""})

    def test_parent_is_excluded_but_child_and_no_due_issue_remain(self):
        records = [
            issue("LIFE-1", "Container", priority=1),
            issue("LIFE-2", "Child", priority=2, parent="id-LIFE-1"),
            issue("CODE-1", "No due", priority=3, team="CODE"),
        ]

        selected, total = source_linear.select_issues(records, today=date(2026, 7, 23))

        self.assertEqual(total, 2)
        self.assertEqual([item["text"] for item in selected], ["Child", "No due"])

    def test_ordering_covers_priority_due_state_update_and_identifier(self):
        records = [
            issue("LIFE-9", "No priority", priority=0, due="2026-07-20"),
            issue("LIFE-8", "High future", priority=2, due="2026-07-24"),
            issue("LIFE-7", "High overdue", priority=2, due="2026-07-22"),
            issue("LIFE-6", "Normal waiting", priority=3, due="2026-07-23"),
            issue("LIFE-5", "Normal started old", priority=3, due="2026-07-23", state="started", updated="2026-07-22T00:00:00Z"),
            issue("LIFE-4", "Normal started new B", priority=3, due="2026-07-23", state="started", updated="2026-07-24T00:00:00Z"),
            issue("LIFE-3", "Normal started new A", priority=3, due="2026-07-23", state="started", updated="2026-07-24T00:00:00Z"),
        ]

        selected, total = source_linear.select_issues(records, today=date(2026, 7, 23), limit=10)

        self.assertEqual(total, 7)
        self.assertEqual(
            [item["text"] for item in selected],
            [
                "High overdue",
                "High future",
                "Normal started new A",
                "Normal started new B",
                "Normal started old",
                "Normal waiting",
                "No priority",
            ],
        )
        self.assertEqual(selected[0]["tag"], "overdue")
        self.assertEqual(selected[1]["tag"], "tomorrow")

    def test_projection_has_one_todo_owner_and_empty_state_is_explicit(self):
        widgets = source_linear.project_widgets(
            [issue("LIFE-1", "First", priority=1)], today=date(2026, 7, 23)
        )
        self.assertEqual(set(widgets), {"todo"})
        self.assertEqual(widgets["todo"]["items"][0]["text"], "First")

        empty = source_linear.project_widgets([], today=date(2026, 7, 23))
        self.assertEqual(empty["todo"]["items"], [])

    def test_pagination_and_unauthorized_response(self):
        pages = [
            {"data": {"issues": {"nodes": [issue("LIFE-1", "One")], "pageInfo": {"hasNextPage": True, "endCursor": "next"}}}},
            {"data": {"issues": {"nodes": [issue("LIFE-2", "Two")], "pageInfo": {"hasNextPage": False, "endCursor": None}}}},
        ]

        def opener(request, timeout):
            return FakeResponse(pages.pop(0))

        self.assertEqual(len(source_linear.fetch_issues("secret", opener=opener)), 2)

        def unauthorized(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 401, "no", {}, io.BytesIO())

        with self.assertRaises(source_linear.LinearAuthenticationError):
            source_linear.fetch_issues("secret", opener=unauthorized)

    def test_projection_never_emits_ids_links_or_raw_fields(self):
        record = issue("LIFE-1", "Visible")
        record.update({"url": "private", "description": "private", "labels": ["private"]})
        output = json.dumps(
            source_linear.project_widgets([record], today=date(2026, 7, 23)),
            ensure_ascii=False,
        )
        self.assertNotIn("LIFE-1", output)
        self.assertNotIn("private", output)


if __name__ == "__main__":
    unittest.main()
