import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "web_update.py"


class WebUpdateTests(unittest.TestCase):
    def test_demo_update_writes_complete_public_widgets_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "widgets.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output",
                    str(output),
                    "--focus",
                    "Ship IP-only demo gate",
                    "--todo",
                    "Verify static page",
                    "--todo",
                    "Keep data public",
                    "--weather-location",
                    "Shanghai",
                ],
                check=True,
            )

            data = json.loads(output.read_text(encoding="utf-8"))
            mode = output.stat().st_mode & 0o777

        self.assertEqual(data["layout"], "dashboard")
        self.assertEqual(mode, 0o644)
        self.assertEqual(data["refresh_seconds"], 300)
        self.assertIn("T", data["updated_at"])
        self.assertEqual(
            [widget["type"] for widget in data["widgets"]],
            ["weather", "ai-status", "focus", "ai-tasks", "calendar", "todo"],
        )
        ai_status = data["widgets"][1]["data"]
        focus = data["widgets"][2]["data"]
        ai_tasks = data["widgets"][3]["data"]
        self.assertEqual(ai_status["session_name"], "Public demo")
        self.assertEqual(ai_status["model"], "Codex")
        self.assertIn("context", ai_status)
        self.assertNotIn("session_name", focus)
        self.assertEqual(focus["task"], "Ship IP-only demo gate")
        self.assertEqual(
            {
                "running": 1,
                "waiting": 0,
                "blocked": 0,
                "completed_today": 2,
            },
            ai_tasks["counts"],
        )
        self.assertEqual(data["widgets"][5]["data"]["items"][1]["text"], "Keep data public")


if __name__ == "__main__":
    unittest.main()
