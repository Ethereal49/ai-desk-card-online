#!/usr/bin/env python3
"""Regression tests for the Codex plan freshness hook."""

from __future__ import annotations

import importlib.util
import tempfile
import time
import unittest
from pathlib import Path


HOOK_PATH = Path(__file__).resolve().parents[1] / ".codex" / "hooks" / "ensure_plan_updated.py"
spec = importlib.util.spec_from_file_location("ensure_plan_updated", HOOK_PATH)
assert spec and spec.loader
ensure_plan_updated = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ensure_plan_updated)


class PlanGuardTest(unittest.TestCase):
    def test_fresh_plan_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            changed = root / "web" / "app.js"
            changed.parent.mkdir()
            changed.write_text("console.log('x')\n", encoding="utf-8")
            time.sleep(0.01)
            plan = root / "PLAN_web.md"
            plan.write_text("updated\n", encoding="utf-8")

            self.assertEqual(ensure_plan_updated.stale_files(root, plan), [])

    def test_older_plan_reports_newer_project_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("old\n", encoding="utf-8")
            time.sleep(0.01)
            changed = root / "web" / "app.js"
            changed.parent.mkdir()
            changed.write_text("console.log('x')\n", encoding="utf-8")

            self.assertEqual(ensure_plan_updated.stale_files(root, plan), [changed])

    def test_ignores_output_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("old\n", encoding="utf-8")
            time.sleep(0.01)
            artifact = root / "output" / "shot.png"
            artifact.parent.mkdir()
            artifact.write_text("artifact\n", encoding="utf-8")

            self.assertEqual(ensure_plan_updated.stale_files(root, plan), [])

    def test_ignores_playwright_mcp_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("old\n", encoding="utf-8")
            time.sleep(0.01)
            artifact = root / ".playwright-mcp" / "page.yml"
            artifact.parent.mkdir()
            artifact.write_text("snapshot\n", encoding="utf-8")

            self.assertEqual(ensure_plan_updated.stale_files(root, plan), [])

    def test_ignores_code_review_graph_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("old\n", encoding="utf-8")
            time.sleep(0.01)
            artifact = root / ".code-review-graph" / "graph.db"
            artifact.parent.mkdir()
            artifact.write_text("graph cache\n", encoding="utf-8")

            self.assertEqual(ensure_plan_updated.stale_files(root, plan), [])


if __name__ == "__main__":
    unittest.main()
