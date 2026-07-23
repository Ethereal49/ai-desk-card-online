import copy
import unittest

import widget_contract


def baseline_document():
    return {
        "updated_at": "2026-07-23T08:00:00+08:00",
        "layout": "dashboard",
        "refresh_seconds": 300,
        "widgets": [
            {
                "slot": "glance-left",
                "type": "weather",
                "data": {"current": {}, "forecast": []},
            },
            {
                "slot": "glance-right",
                "type": "ai-status",
                "data": {
                    "session_name": "IDLE",
                    "model": "Codex",
                    "task": "No active task",
                    "context": {"used": 0, "limit": 0},
                    "elapsed_seconds": 0,
                },
            },
            {
                "slot": "headline",
                "type": "focus",
                "data": {"task": "Old focus", "big_text": "NOW", "subtitle": "old"},
            },
            {
                "slot": "detail-left",
                "type": "ai-tasks",
                "data": {
                    "title": "AI Tasks",
                    "counts": {"running": 0, "waiting": 0, "blocked": 0, "completed_today": 0},
                },
            },
            {
                "slot": "detail-middle",
                "type": "calendar",
                "data": {"now_iso": "2026-07-23T08:00:00+08:00", "events": []},
            },
            {
                "slot": "detail-right",
                "type": "todo",
                "data": {"title": "Todo", "items": [{"text": "Old task"}]},
            },
        ],
    }


class WidgetContractTests(unittest.TestCase):
    def test_successful_source_replaces_only_owned_widgets(self):
        baseline = baseline_document()
        result = widget_contract.SourceResult.success(
            "linear",
            {
                "focus": {"task": "First", "big_text": "NOW", "subtitle": "Linear priority"},
                "todo": {
                    "title": "Todo",
                    "selected_count": 1,
                    "total_count": 1,
                    "items": [{"text": "First", "tag": "today"}],
                },
            },
            "2026-07-23T09:00:00+08:00",
        )

        merged, changed = widget_contract.merge_source_results(baseline, [result])
        widgets = widget_contract.widget_map(merged)

        self.assertEqual(widgets["focus"]["data"]["task"], "First")
        self.assertEqual(widgets["todo"]["data"]["items"][0]["text"], "First")
        self.assertEqual(widgets["weather"], baseline["widgets"][0])
        self.assertEqual(changed, ["focus", "todo"])

    def test_failed_source_preserves_last_known_good_and_marks_stale(self):
        baseline = baseline_document()
        result = widget_contract.SourceResult.failure(
            "apple-calendar",
            ("calendar",),
            "calendar unavailable",
            "2026-07-23T09:00:00+08:00",
        )

        merged, _ = widget_contract.merge_source_results(baseline, [result])
        data = widget_contract.widget_map(merged)["calendar"]["data"]

        self.assertEqual(data["events"], [])
        self.assertTrue(data["stale"])
        self.assertEqual(data["error"], "calendar unavailable")

    def test_rejects_private_keys_duplicate_widgets_and_oversized_lists(self):
        private = baseline_document()
        widget_contract.widget_map(private)["todo"]["data"]["items"][0]["url"] = "secret"
        with self.assertRaises(widget_contract.ContractError):
            widget_contract.validate_document(private)

        duplicate = baseline_document()
        duplicate["widgets"].append(copy.deepcopy(duplicate["widgets"][-1]))
        with self.assertRaises(widget_contract.ContractError):
            widget_contract.validate_document(duplicate)

        too_many = baseline_document()
        widget_contract.widget_map(too_many)["todo"]["data"]["items"] = [
            {"text": str(index)} for index in range(6)
        ]
        with self.assertRaises(widget_contract.ContractError):
            widget_contract.validate_document(too_many)

        unknown_quota = baseline_document()
        widget_contract.widget_map(unknown_quota)["ai-status"]["data"]["quota"] = {
            "source": "codex-rollout",
            "stale": False,
            "account": "must-not-pass",
        }
        with self.assertRaises(widget_contract.ContractError):
            widget_contract.validate_document(unknown_quota)

    def test_configuration_errors_cannot_be_merged(self):
        result = widget_contract.SourceResult.failure(
            "linear",
            ("focus", "todo"),
            "linear credential missing",
            "2026-07-23T09:00:00+08:00",
            configuration=True,
        )
        with self.assertRaises(widget_contract.ContractError):
            widget_contract.merge_source_results(baseline_document(), [result])


if __name__ == "__main__":
    unittest.main()
