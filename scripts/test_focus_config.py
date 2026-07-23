import json
import tempfile
import unittest
from pathlib import Path

import focus_config
from test_widget_contract import baseline_document


class FocusConfigTests(unittest.TestCase):
    def test_missing_file_uses_todo_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = focus_config.load_focus_config(Path(temp_dir) / "missing.json")
        self.assertEqual(config, focus_config.FocusConfig(source="todo.first"))

    def test_loader_accepts_manual_and_rejects_malformed_oversized_or_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "focus.json"
            path.write_text(
                json.dumps(
                    {
                        "source": "manual",
                        "task": "Read the complete task",
                        "subtitle": "Personal",
                        "big_text": "NOW",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(focus_config.load_focus_config(path).task, "Read the complete task")

            invalid_values = [
                "not json",
                json.dumps({"source": "todo.first", "task": "not allowed"}),
                json.dumps({"source": "manual"}),
                json.dumps({"source": "unknown"}),
                json.dumps({"source": "manual", "task": "Visible", "notes": "private"}),
                json.dumps({"source": "manual", "task": 123}),
                json.dumps({"source": "manual", "task": "x" * 193}),
                json.dumps({"source": "manual", "task": "Visible", "subtitle": 1}),
                json.dumps({"source": "manual", "task": "Visible", "big_text": ""}),
            ]
            for value in invalid_values:
                path.write_text(value, encoding="utf-8")
                with self.subTest(value=value), self.assertRaises(
                    focus_config.FocusConfigurationError
                ):
                    focus_config.load_focus_config(path)

            path.write_bytes(b"x" * (focus_config.MAX_CONFIG_BYTES + 1))
            with self.assertRaises(focus_config.FocusConfigurationError):
                focus_config.load_focus_config(path)

            path.unlink()
            path.mkdir()
            with self.assertRaises(focus_config.FocusConfigurationError):
                focus_config.load_focus_config(path)

    def test_every_linked_source_projects_only_focus_fields(self):
        document = baseline_document()
        widgets = {widget["type"]: widget["data"] for widget in document["widgets"]}
        widgets["todo"].update(
            {
                "items": [{"text": "First"}],
                "updated_at": "2026-07-23T09:00:00+08:00",
                "stale": False,
            }
        )
        widgets["calendar"]["events"] = [
            {"start": "14:00", "title": "Review layout", "end": "15:00"}
        ]
        widgets["ai-status"]["task"] = "Implement Focus resolver"
        widgets["weather"].update(
            {
                "location": "Shenzhen",
                "current": {"temp_c": 26.4, "condition": "Cloudy"},
            }
        )

        expected = {
            "todo.first": ("First", "NOW", "Todo priority"),
            "calendar.next": ("Review layout", "14:00", "Next event"),
            "ai-status.task": ("Implement Focus resolver", "AI", "Codex"),
            "weather.current": ("Cloudy", "26°C", "Shenzhen"),
        }
        for source, values in expected.items():
            with self.subTest(source=source):
                result = focus_config.resolve_focus(document, focus_config.FocusConfig(source))
                self.assertEqual(
                    (result["task"], result["big_text"], result["subtitle"]), values
                )
                self.assertEqual(
                    set(result), {"task", "big_text", "subtitle", "source", "updated_at", "stale"}
                )

    def test_overrides_empty_states_and_stale_propagation(self):
        document = baseline_document()
        widgets = {widget["type"]: widget["data"] for widget in document["widgets"]}
        widgets["todo"]["items"] = []
        widgets["todo"].update(
            {
                "updated_at": "2026-07-23T09:00:00+08:00",
                "stale": True,
                "last_attempt_at": "2026-07-23T09:05:00+08:00",
                "error": "linear unavailable",
            }
        )

        result = focus_config.resolve_focus(
            document,
            focus_config.FocusConfig(
                source="todo.first", subtitle="Selected", big_text="NEXT"
            ),
        )

        self.assertEqual(result["task"], "No todo task selected")
        self.assertEqual(result["subtitle"], "Selected")
        self.assertEqual(result["big_text"], "NEXT")
        self.assertTrue(result["stale"])
        self.assertEqual(result["error"], "linear unavailable")

    def test_manual_projection_contains_no_configuration_shape(self):
        result = focus_config.resolve_focus(
            baseline_document(),
            focus_config.FocusConfig(source="manual", task="Write Phase 6"),
        )
        self.assertEqual(result["task"], "Write Phase 6")
        self.assertEqual(result["big_text"], "FOCUS")
        self.assertEqual(result["subtitle"], "Manual")
        self.assertNotIn("config", {key for key in result if key != "source"})


if __name__ == "__main__":
    unittest.main()
