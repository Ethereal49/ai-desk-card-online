import subprocess
import tempfile
import unittest
from pathlib import Path

import run_scheduled_refresh


class RunScheduledRefreshTests(unittest.TestCase):
    def test_status_is_replaced_bounded_and_private_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "latest.log"
            path.write_text("old status\n", encoding="utf-8")

            def runner(*args, **kwargs):
                return subprocess.CompletedProcess(args[0], 2, "sources linear=ok\npublish=updated\n", "")

            code = run_scheduled_refresh.run_refresh(path, runner=runner)

            self.assertEqual(code, 2)
            self.assertNotIn("old status", path.read_text(encoding="utf-8"))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_timeout_writes_stable_failure_without_exception_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "latest.log"

            def runner(*args, **kwargs):
                raise subprocess.TimeoutExpired("private command", 1, stderr="private")

            code = run_scheduled_refresh.run_refresh(path, timeout=30, runner=runner)

            self.assertEqual(code, 124)
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "refresh=fatal reason=scheduled-timeout\n",
            )


if __name__ == "__main__":
    unittest.main()
