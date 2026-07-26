import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import configure_focus
import focus_config


class ConfigureFocusTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = configure_focus.main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_help_documents_stable_commands_and_no_publish_boundary(self) -> None:
        help_text = configure_focus.build_parser().format_help()

        self.assertIn("{get,set,reset}", help_text)
        self.assertIn("does not publish", help_text)
        self.assertIn("configured text", help_text)

    def test_get_missing_config_reports_explicit_default_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing" / "focus.json"

            code, stdout, stderr = self.run_cli("--config", str(path), "get")

            self.assertFalse(path.exists())

        self.assertEqual(code, 0)
        self.assertEqual(
            stdout,
            "focus-config=ok source=todo.first task=absent subtitle=absent big_text=absent\n",
        )
        self.assertEqual(stderr, "")

    def test_set_round_trips_every_source_through_shared_parser(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "private" / "focus.json"
            for source in sorted(focus_config.ALLOWED_SOURCES):
                args = [
                    "--config",
                    str(path),
                    "set",
                    "--source",
                    source,
                    "--subtitle",
                    "Selected",
                    "--big-text",
                    "NOW",
                ]
                if source == "manual":
                    args.extend(["--task", "Private manual task"])

                with self.subTest(source=source), mock.patch.object(
                    configure_focus,
                    "parse_focus_config",
                    wraps=focus_config.parse_focus_config,
                ) as parser:
                    code, stdout, stderr = self.run_cli(*args)
                    loaded = focus_config.load_focus_config(path)

                self.assertEqual(code, 0)
                self.assertEqual(loaded.source, source)
                self.assertEqual(loaded.subtitle, "Selected")
                self.assertEqual(loaded.big_text, "NOW")
                self.assertEqual(loaded.task, "Private manual task" if source == "manual" else None)
                self.assertIn(f"source={source}", stdout)
                self.assertNotIn("Private manual task", stdout + stderr)
                parser.assert_called_once()

    def test_manual_requires_task_and_linked_sources_reject_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "focus.json"
            path.write_text('{"source":"todo.first"}\n', encoding="utf-8")
            before = path.read_bytes()

            manual = self.run_cli(
                "--config", str(path), "set", "--source", "manual"
            )
            linked = self.run_cli(
                "--config",
                str(path),
                "set",
                "--source",
                "todo.first",
                "--task",
                "must stay private",
            )

            self.assertEqual(path.read_bytes(), before)

        for code, stdout, stderr in (manual, linked):
            self.assertEqual(code, 3)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "focus-config=fatal reason=configuration\n")
            self.assertNotIn("must stay private", stdout + stderr)

    def test_argparse_errors_use_exit_two_and_validation_output_is_redacted(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as invalid_source:
            configure_focus.main(["set", "--source", "unknown"])

        self.assertEqual(invalid_source.exception.code, 2)
        self.assertIn("invalid choice", stderr.getvalue())

        secret = "PRIVATE-OVERLONG-" * 20
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "focus.json"
            path.write_text('{"source":"todo.first"}\n', encoding="utf-8")
            before = path.read_bytes()

            code, stdout, config_stderr = self.run_cli(
                "--config",
                str(path),
                "set",
                "--source",
                "manual",
                "--task",
                secret,
            )

            self.assertEqual(path.read_bytes(), before)

        self.assertEqual(code, 3)
        self.assertEqual(stdout, "")
        self.assertEqual(config_stderr, "focus-config=fatal reason=configuration\n")
        self.assertNotIn(secret, config_stderr)

    def test_get_reports_presence_without_printing_configured_text(self) -> None:
        secrets = ("PRIVATE-TASK-91", "PRIVATE-SUBTITLE-82", "PRIVATE-BIG-73")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "focus.json"
            path.write_text(
                json.dumps(
                    {
                        "source": "manual",
                        "task": secrets[0],
                        "subtitle": secrets[1],
                        "big_text": secrets[2],
                    }
                ),
                encoding="utf-8",
            )

            code, stdout, stderr = self.run_cli("--config", str(path), "get")

        self.assertEqual(code, 0)
        self.assertEqual(
            stdout,
            "focus-config=ok source=manual task=present subtitle=present big_text=present\n",
        )
        for secret in secrets:
            self.assertNotIn(secret, stdout + stderr)

    def test_writes_private_modes_on_create_and_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "private" / "focus.json"

            code, _, _ = self.run_cli(
                "--config", str(path), "set", "--source", "calendar.next"
            )
            first_dir_mode = path.parent.stat().st_mode & 0o777
            first_file_mode = path.stat().st_mode & 0o777
            os.chmod(path, 0o644)
            code_replace, _, _ = self.run_cli(
                "--config", str(path), "set", "--source", "weather.current"
            )

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["source"],
                "weather.current",
            )
            replaced_mode = path.stat().st_mode & 0o777

        self.assertEqual(code, 0)
        self.assertEqual(code_replace, 0)
        self.assertEqual(first_dir_mode, 0o700)
        self.assertEqual(first_file_mode, 0o600)
        self.assertEqual(replaced_mode, 0o600)

    def test_validation_and_replace_failures_preserve_existing_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "focus.json"
            original = b'{"source":"todo.first"}\n'
            path.write_bytes(original)
            entries_before = {entry.name for entry in path.parent.iterdir()}

            with mock.patch.object(
                configure_focus.os, "replace", side_effect=OSError("private detail")
            ):
                code, stdout, stderr = self.run_cli(
                    "--config", str(path), "set", "--source", "calendar.next"
                )

            self.assertEqual(path.read_bytes(), original)
            self.assertEqual({entry.name for entry in path.parent.iterdir()}, entries_before)

            path.write_bytes(b"{malformed private config")
            malformed = path.read_bytes()
            reset_code, reset_stdout, reset_stderr = self.run_cli(
                "--config", str(path), "reset"
            )
            self.assertEqual(path.read_bytes(), malformed)

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "focus-config=fatal reason=local-io\n")
        self.assertNotIn("private detail", stderr)
        self.assertEqual(reset_code, 3)
        self.assertEqual(reset_stdout, "")
        self.assertEqual(reset_stderr, "focus-config=fatal reason=configuration\n")

    def test_file_and_parent_type_errors_are_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_directory = root / "focus.json"
            config_directory.mkdir()
            get_result = self.run_cli("--config", str(config_directory), "get")

            parent_file = root / "not-a-directory"
            parent_file.write_text("private parent detail", encoding="utf-8")
            set_result = self.run_cli(
                "--config",
                str(parent_file / "focus.json"),
                "set",
                "--source",
                "todo.first",
            )

        self.assertEqual(get_result, (3, "", "focus-config=fatal reason=configuration\n"))
        self.assertEqual(set_result, (1, "", "focus-config=fatal reason=local-io\n"))

    def test_wrapped_read_error_uses_local_io_exit(self) -> None:
        read_error = focus_config.FocusConfigurationError("private read detail")
        read_error.__cause__ = PermissionError("private path detail")

        with mock.patch.object(
            configure_focus, "load_focus_config", side_effect=read_error
        ):
            code, stdout, stderr = self.run_cli("get")

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "focus-config=fatal reason=local-io\n")
        self.assertNotIn("private", stderr)

    def test_reset_writes_explicit_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "focus.json"
            path.write_text(
                json.dumps({"source": "manual", "task": "Private"}),
                encoding="utf-8",
            )

            code, stdout, stderr = self.run_cli("--config", str(path), "reset")

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"source": "todo.first"},
            )

        self.assertEqual(code, 0)
        self.assertIn("source=todo.first", stdout)
        self.assertEqual(stderr, "")

    def test_cli_never_mutates_widgets_or_invokes_publish_processes(self) -> None:
        source = Path(configure_focus.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "refresh_dashboard",
            "update_focus",
            "widgets.json",
            "subprocess",
            "ssh",
            "scp",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            widgets = root / "web" / "widgets.json"
            widgets.parent.mkdir()
            widgets.write_bytes(b"widgets-sentinel")
            config = root / "private" / "focus.json"

            with mock.patch.object(subprocess, "run") as runner:
                code, _, _ = self.run_cli(
                    "--config", str(config), "set", "--source", "todo.first"
                )

            self.assertEqual(widgets.read_bytes(), b"widgets-sentinel")
            runner.assert_not_called()

        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
