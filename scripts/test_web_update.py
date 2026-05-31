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

        self.assertEqual(data["layout"], "dashboard")
        self.assertEqual(data["refresh_seconds"], 300)
        self.assertIn("T", data["updated_at"])
        self.assertEqual(
            [widget["type"] for widget in data["widgets"]],
            ["focus", "weather", "calendar", "todo"],
        )
        self.assertEqual(data["widgets"][0]["data"]["task"], "Ship IP-only demo gate")
        self.assertEqual(data["widgets"][3]["data"]["items"][1]["text"], "Keep data public")


if __name__ == "__main__":
    unittest.main()
