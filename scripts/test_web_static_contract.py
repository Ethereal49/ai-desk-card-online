import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class WebStaticContractTests(unittest.TestCase):
    def test_viewport_diagnostic_is_query_gated_and_normal_label_stays_default(self):
        index_html = (REPO_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "web" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="source-label">source: widgets.json', index_html)
        self.assertIn('src="./app.js?v=phase-5"', index_html)
        self.assertIn("viewport=1", app_js)
        self.assertIn("if (viewportDiagnostic)", app_js)
        self.assertIn('"viewport: " + viewportWidth + "x" + viewportHeight', app_js)
        self.assertIn("window.visualViewport", app_js)
        self.assertIn('"zoom" in card.style', app_js)
        self.assertIn("SAFE_VIEWPORT_INSET = 4", app_js)

    def test_long_text_fit_and_five_item_renderer_contract_is_present(self):
        app_js = (REPO_ROOT / "web" / "app.js").read_text(encoding="utf-8")
        styles_css = (REPO_ROOT / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("MAX_TODO_ITEMS = 5", app_js)
        self.assertIn("fitListWidget", app_js)
        self.assertIn("fit-secondary-hidden", app_js)
        self.assertIn("overflow-wrap: anywhere", styles_css)
        self.assertNotIn("text-overflow: ellipsis", styles_css)

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
        self.assertEqual(
            sorted(widgets["ai-status"]["data"]["quota"]),
            ["five_hour", "source", "stale", "updated_at", "weekly"],
        )
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
        self.assertIn("formatQuotaWindow", app_js)
        self.assertIn("ai-quota", styles_css)
        self.assertIn("renderAiTasks", app_js)
        self.assertIn("widget-ai-status", app_js)
        self.assertIn("widget-ai-tasks", app_js)
        self.assertIn("grid-template-rows: 64px 210px 320px 278px 56px", styles_css)
        self.assertIn("grid-template-columns: 180px minmax(0, 1fr) minmax(0, 1fr)", styles_css)


if __name__ == "__main__":
    unittest.main()
