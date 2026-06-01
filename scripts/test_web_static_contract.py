import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class WebStaticContractTests(unittest.TestCase):
    def test_ai_status_and_ai_tasks_contracts_are_present_in_static_web_assets(self):
        example = json.loads(
            (REPO_ROOT / "web" / "widgets.example.json").read_text(encoding="utf-8")
        )
        index_html = (REPO_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "web" / "app.js").read_text(encoding="utf-8")
        styles_css = (REPO_ROOT / "web" / "styles.css").read_text(encoding="utf-8")

        widgets = {widget["type"]: widget for widget in example["widgets"]}
        self.assertIn("ai-status", widgets)
        self.assertEqual(widgets["ai-status"]["slot"], "glance-right")
        self.assertIn("session_name", widgets["ai-status"]["data"])
        self.assertIn("context", widgets["ai-status"]["data"])
        self.assertNotIn("session_name", widgets["focus"]["data"])
        self.assertIn("ai-tasks", widgets)
        self.assertEqual(widgets["ai-tasks"]["slot"], "detail-left")
        self.assertEqual(
            sorted(widgets["ai-tasks"]["data"]["counts"]),
            ["blocked", "completed_today", "running", "waiting"],
        )

        self.assertIn('id="widget-ai-status"', index_html)
        self.assertIn('id="widget-ai-tasks"', index_html)
        self.assertIn("renderAiStatus", app_js)
        self.assertIn("renderAiTasks", app_js)
        self.assertIn("widget-ai-status", app_js)
        self.assertIn("widget-ai-tasks", app_js)
        self.assertIn("grid-template-rows: 64px 210px 320px 278px 56px", styles_css)
        self.assertIn("grid-template-columns: 180px minmax(0, 1fr) minmax(0, 1fr)", styles_css)


if __name__ == "__main__":
    unittest.main()
