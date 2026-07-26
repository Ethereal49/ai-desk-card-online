import argparse
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import refresh_dashboard
from focus_config import FocusConfig, FocusConfigurationError
from test_widget_contract import baseline_document
from widget_contract import SourceResult, now_iso


def source_results(health="ok"):
    observed = "2026-07-23T09:00:00+08:00"
    if health == "configuration_error":
        return [
            SourceResult.failure(
                "linear",
                ("todo",),
                "linear credential missing",
                observed,
                configuration=True,
            )
        ]
    return [
        SourceResult.success(
            "linear",
            {
                "todo": {"title": "Todo", "selected_count": 1, "total_count": 1, "items": [{"text": "New focus"}]},
            },
            observed,
        ),
        SourceResult.failure(
            "apple-calendar",
            ("calendar",),
            "calendar unavailable",
            observed,
        ),
        SourceResult.success(
            "codex-metadata",
            {
                "ai-status": {"session_name": "IDLE", "model": "Codex", "task": "No active task", "context": {"used": 0, "limit": 0}, "elapsed_seconds": 0},
                "ai-tasks": {"title": "AI Tasks", "counts": {"running": 0, "waiting": 0, "blocked": 0, "completed_today": 1}},
            },
            observed,
        ),
    ]


class RefreshDashboardTests(unittest.TestCase):
    def test_preview_composes_results_preserves_weather_and_marks_failure_stale(self):
        baseline = baseline_document()
        candidate, changed = refresh_dashboard.compose_candidate(baseline, source_results(), None)
        widgets = {widget["type"]: widget for widget in candidate["widgets"]}

        self.assertEqual(widgets["weather"], baseline["widgets"][0])
        self.assertEqual(widgets["focus"]["data"]["task"], "New focus")
        self.assertTrue(widgets["calendar"]["data"]["stale"])
        self.assertTrue(widgets["ai-status"]["data"]["quota"]["stale"])
        self.assertEqual(set(changed), {"ai-status", "focus", "ai-tasks", "calendar", "todo"})

    def test_quota_failure_preserves_prior_windows_after_codex_status_replacement(self):
        baseline = baseline_document()
        baseline["widgets"][1]["data"]["quota"] = {
            "source": "codex-rollout",
            "updated_at": "2026-07-23T08:00:00+08:00",
            "stale": False,
            "weekly": {"remaining_percent": 61.0},
        }

        candidate, _ = refresh_dashboard.compose_candidate(baseline, source_results(), None)
        quota = candidate["widgets"][1]["data"]["quota"]

        self.assertEqual(quota["weekly"]["remaining_percent"], 61.0)
        self.assertTrue(quota["stale"])
        self.assertEqual(quota["error"], "quota unavailable")

    def test_health_output_has_no_titles_paths_or_error_bodies(self):
        line = refresh_dashboard.health_line(source_results(), None)
        self.assertEqual(
            line,
            "sources linear=ok apple-calendar=stale codex-metadata=ok codex-quota=stale",
        )
        self.assertNotIn("New focus", line)
        self.assertNotIn("unavailable", line)

    def test_configuration_failure_stops_before_baseline_or_publish(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(
            refresh_dashboard, "collect_sources", return_value=(source_results("configuration_error"), None)
        ), mock.patch.object(refresh_dashboard, "read_baseline") as read_baseline, mock.patch.object(
            refresh_dashboard, "publish_candidate"
        ) as publish, tempfile.TemporaryDirectory() as temp_dir, redirect_stdout(stdout), redirect_stderr(stderr):
            code = refresh_dashboard.main(["--publish", "--local-lock", str(Path(temp_dir) / "lock")])

        self.assertEqual(code, 3)
        read_baseline.assert_not_called()
        publish.assert_not_called()
        self.assertNotIn("credential missing", stdout.getvalue())

    def test_parser_reads_remote_host_from_environment(self):
        with mock.patch.dict(
            "os.environ",
            {"AI_DESK_CARD_SSH_HOST": "desk-card.example"},
            clear=False,
        ):
            args = refresh_dashboard.build_parser().parse_args(["--preview"])

        self.assertEqual(args.host, "desk-card.example")

    def test_source_check_does_not_require_remote_host(self):
        with mock.patch.dict("os.environ", {}, clear=True), mock.patch.object(
            refresh_dashboard,
            "collect_sources",
            return_value=(source_results(), None),
        ), mock.patch.object(refresh_dashboard, "read_baseline") as read_baseline:
            with tempfile.TemporaryDirectory() as temp_dir, redirect_stdout(
                io.StringIO()
            ):
                code = refresh_dashboard.main(
                    [
                        "--source-check",
                        "--local-lock",
                        str(Path(temp_dir) / "lock"),
                    ]
                )

        self.assertEqual(code, 2)
        read_baseline.assert_not_called()

    def test_remote_preview_without_host_fails_before_sources_or_ssh(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True), mock.patch.object(
            refresh_dashboard, "collect_sources"
        ) as collect, mock.patch.object(
            refresh_dashboard, "read_baseline"
        ) as read_baseline, redirect_stdout(stdout), redirect_stderr(stderr):
            code = refresh_dashboard.main(["--preview", "--host", ""])

        self.assertEqual(code, 3)
        collect.assert_not_called()
        read_baseline.assert_not_called()
        self.assertEqual(
            stderr.getvalue(),
            "refresh=fatal reason=configuration\n",
        )

    def test_publish_with_local_baseline_still_requires_remote_host(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline_path = root / "widgets.json"
            baseline_path.write_text(
                json.dumps(baseline_document()),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with mock.patch.dict("os.environ", {}, clear=True), mock.patch.object(
                refresh_dashboard, "collect_sources"
            ) as collect, mock.patch.object(
                refresh_dashboard, "publish_candidate"
            ) as publish, redirect_stderr(stderr):
                code = refresh_dashboard.main(
                    [
                        "--publish",
                        "--baseline",
                        str(baseline_path),
                        "--host",
                        "",
                        "--local-lock",
                        str(root / "lock"),
                    ]
                )

        self.assertEqual(code, 3)
        collect.assert_not_called()
        publish.assert_not_called()
        self.assertEqual(
            stderr.getvalue(),
            "refresh=fatal reason=configuration\n",
        )

    def test_focus_configuration_failure_stops_before_sources_baseline_or_publish(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(
            refresh_dashboard,
            "load_focus_config",
            side_effect=FocusConfigurationError("private configured text"),
        ), mock.patch.object(refresh_dashboard, "collect_sources") as collect, mock.patch.object(
            refresh_dashboard, "read_baseline"
        ) as read_baseline, mock.patch.object(
            refresh_dashboard, "publish_candidate"
        ) as publish, tempfile.TemporaryDirectory() as temp_dir, redirect_stdout(
            stdout
        ), redirect_stderr(stderr):
            code = refresh_dashboard.main(
                ["--publish", "--local-lock", str(Path(temp_dir) / "lock")]
            )

        self.assertEqual(code, 3)
        collect.assert_not_called()
        read_baseline.assert_not_called()
        publish.assert_not_called()
        self.assertNotIn("private configured text", stdout.getvalue() + stderr.getvalue())

    def test_compose_supports_a_non_linear_focus_source(self):
        candidate, changed = refresh_dashboard.compose_candidate(
            baseline_document(),
            source_results(),
            None,
            FocusConfig(source="ai-status.task", subtitle="Current AI"),
        )
        focus = next(widget for widget in candidate["widgets"] if widget["type"] == "focus")

        self.assertEqual(focus["data"]["task"], "No active task")
        self.assertEqual(focus["data"]["subtitle"], "Current AI")
        self.assertIn("focus", changed)

    def test_baseline_fixture_preview_never_writes_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline_path = root / "widgets.json"
            baseline_path.write_text(json.dumps(baseline_document()), encoding="utf-8")
            before = baseline_path.read_bytes()
            stdout = io.StringIO()
            with mock.patch.object(
                refresh_dashboard, "collect_sources", return_value=(source_results(), None)
            ), redirect_stdout(stdout):
                code = refresh_dashboard.main(
                    ["--preview", "--baseline", str(baseline_path), "--local-lock", str(root / "lock")]
                )

            self.assertEqual(code, 2)
            self.assertEqual(baseline_path.read_bytes(), before)
            self.assertIn("publish=preview", stdout.getvalue())

    def test_stale_quota_alone_returns_partial_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline_path = root / "widgets.json"
            baseline_path.write_text(json.dumps(baseline_document()), encoding="utf-8")
            all_ok = [result for result in source_results() if result.health == "ok"]
            stale_quota = {
                "source": "codex-rollout",
                "updated_at": "2026-07-23T08:00:00+08:00",
                "stale": True,
                "weekly": {"remaining_percent": 50.0},
            }
            with mock.patch.object(
                refresh_dashboard, "collect_sources", return_value=(all_ok, stale_quota)
            ), redirect_stdout(io.StringIO()):
                code = refresh_dashboard.main(
                    ["--preview", "--baseline", str(baseline_path), "--local-lock", str(root / "lock")]
                )
        self.assertEqual(code, 2)

    def test_publish_uses_unique_remote_directory_and_cleans_it(self):
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            if "mktemp -d /tmp/ai-desk-card-publish.XXXXXX" in command:
                return subprocess.CompletedProcess(command, 0, "/tmp/ai-desk-card-publish.abc123\n", "")
            if command[0] == "scp":
                return subprocess.CompletedProcess(command, 0, "", "")
            if any("install_widgets.py" in part for part in command):
                return subprocess.CompletedProcess(command, 0, "publish=updated\n", "")
            return subprocess.CompletedProcess(command, 0, "", "")

        args = argparse.Namespace(
            host="example",
            remote_path="/srv/widgets.json",
            remote_lock="/run/lock/widgets.lock",
            remote_backups="/srv/backups",
        )
        result = refresh_dashboard.publish_candidate(baseline_document(), args, runner=runner)

        self.assertEqual(result, "updated")
        self.assertTrue(any(command[0] == "scp" for command in calls))
        self.assertTrue(any(any("rm -rf" in part for part in command) for command in calls))

    def test_successful_install_fails_loudly_when_remote_cleanup_fails(self):
        def runner(command, **kwargs):
            if "mktemp -d /tmp/ai-desk-card-publish.XXXXXX" in command:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    "/tmp/ai-desk-card-publish.abc123\n",
                    "",
                )
            if command[0] == "scp":
                return subprocess.CompletedProcess(command, 0, "", "")
            if any("install_widgets.py" in part for part in command):
                return subprocess.CompletedProcess(
                    command,
                    0,
                    "publish=updated\n",
                    "",
                )
            if any("rm -rf" in part for part in command):
                return subprocess.CompletedProcess(command, 1, "", "")
            return subprocess.CompletedProcess(command, 0, "", "")

        args = argparse.Namespace(
            host="example",
            remote_path="/srv/widgets.json",
            remote_lock="/run/lock/widgets.lock",
            remote_backups="/srv/backups",
        )

        with self.assertRaisesRegex(
            refresh_dashboard.RefreshError,
            "remote cleanup failed",
        ):
            refresh_dashboard.publish_candidate(
                baseline_document(),
                args,
                runner=runner,
            )

    def test_cleanup_failure_does_not_mask_primary_publish_error(self):
        def runner(command, **kwargs):
            if "mktemp -d /tmp/ai-desk-card-publish.XXXXXX" in command:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    "/tmp/ai-desk-card-publish.abc123\n",
                    "",
                )
            return subprocess.CompletedProcess(command, 1, "", "")

        args = argparse.Namespace(
            host="example",
            remote_path="/srv/widgets.json",
            remote_lock="/run/lock/widgets.lock",
            remote_backups="/srv/backups",
        )
        stderr = io.StringIO()

        with redirect_stderr(stderr), self.assertRaisesRegex(
            refresh_dashboard.RefreshError,
            "external command failed",
        ):
            refresh_dashboard.publish_candidate(
                baseline_document(),
                args,
                runner=runner,
            )

        self.assertEqual(
            stderr.getvalue(),
            "publish=warning reason=remote-cleanup\n",
        )


if __name__ == "__main__":
    unittest.main()
