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

    def test_ignores_trellis_closeout_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("current product state\n", encoding="utf-8")
            time.sleep(0.01)

            journal = root / ".trellis" / "workspace" / "developer" / "journal-1.md"
            journal.parent.mkdir(parents=True)
            journal.write_text("closeout journal\n", encoding="utf-8")

            archived_task = (
                root
                / ".trellis"
                / "tasks"
                / "archive"
                / "2026-07"
                / "07-27-finished"
                / "task.json"
            )
            archived_task.parent.mkdir(parents=True)
            archived_task.write_text('{"status":"completed"}\n', encoding="utf-8")

            self.assertEqual(ensure_plan_updated.stale_files(root, plan), [])

    def test_newer_active_trellis_task_remains_plan_relevant(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("old\n", encoding="utf-8")
            time.sleep(0.01)
            active_prd = root / ".trellis" / "tasks" / "07-27-active" / "prd.md"
            active_prd.parent.mkdir(parents=True)
            active_prd.write_text("new requirement\n", encoding="utf-8")

            self.assertEqual(
                ensure_plan_updated.stale_files(root, plan),
                [active_prd],
            )

    def test_newer_trellis_spec_remains_plan_relevant(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = root / "PLAN_web.md"
            plan.write_text("old\n", encoding="utf-8")
            time.sleep(0.01)
            quality_spec = root / ".trellis" / "spec" / "backend" / "quality.md"
            quality_spec.parent.mkdir(parents=True)
            quality_spec.write_text("new contract\n", encoding="utf-8")

            self.assertEqual(
                ensure_plan_updated.stale_files(root, plan),
                [quality_spec],
            )


if __name__ == "__main__":
    unittest.main()
