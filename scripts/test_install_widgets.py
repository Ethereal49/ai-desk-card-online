import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_widget_contract import baseline_document


MODULE_PATH = Path(__file__).resolve().parents[1] / "deploy" / "scripts" / "install_widgets.py"
SPEC = importlib.util.spec_from_file_location("install_widgets", MODULE_PATH)
install_widgets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(install_widgets)


def payload_from(document):
    return {
        "widgets": [
            copy.deepcopy(widget)
            for widget in document["widgets"]
            if widget["type"] != "weather"
        ]
    }


class InstallWidgetsTests(unittest.TestCase):
    def test_install_preserves_weather_backs_up_and_writes_mode_0644(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            live = root / "widgets.json"
            payload = root / "payload.json"
            backups = root / "backups"
            baseline = baseline_document()
            replacement = payload_from(baseline)
            next(widget for widget in replacement["widgets"] if widget["type"] == "focus")["data"]["task"] = "New focus"
            live.write_text(json.dumps(baseline), encoding="utf-8")
            payload.write_text(json.dumps(replacement), encoding="utf-8")

            result = install_widgets.install_payload(live, payload, backups)
            installed = json.loads(live.read_text(encoding="utf-8"))

            self.assertEqual(result, "updated")
            self.assertEqual(installed["widgets"][0], baseline["widgets"][0])
            self.assertEqual(installed["widgets"][2]["data"]["task"], "New focus")
            self.assertEqual(live.stat().st_mode & 0o777, 0o644)
            self.assertEqual(len(list(backups.glob("*.json"))), 1)

    def test_identical_payload_is_no_change_without_backup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            live = root / "widgets.json"
            payload = root / "payload.json"
            backups = root / "backups"
            baseline = baseline_document()
            live.write_text(json.dumps(baseline), encoding="utf-8")
            payload.write_text(json.dumps(payload_from(baseline)), encoding="utf-8")

            result = install_widgets.install_payload(live, payload, backups)

            self.assertEqual(result, "no-change")
            self.assertFalse(backups.exists())

    def test_payload_must_not_replace_weather_or_omit_owned_widgets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            live = root / "widgets.json"
            payload = root / "payload.json"
            baseline = baseline_document()
            live.write_text(json.dumps(baseline), encoding="utf-8")
            payload.write_text(json.dumps({"widgets": baseline["widgets"]}), encoding="utf-8")
            with self.assertRaises(Exception):
                install_widgets.install_payload(live, payload, root / "backups")

            omitted = payload_from(baseline)
            omitted["widgets"].pop()
            payload.write_text(json.dumps(omitted), encoding="utf-8")
            with self.assertRaises(install_widgets.InstallError):
                install_widgets.install_payload(live, payload, root / "backups")

    def test_backup_retention_is_bounded(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backups = root / "backups"
            backups.mkdir()
            for index in range(5):
                path = backups / f"widgets-before-publish-{index}.json"
                path.write_text("{}", encoding="utf-8")
            install_widgets.prune_backups(backups, 2)
            self.assertEqual(len(list(backups.glob("*.json"))), 2)

    def test_failure_after_atomic_replace_restores_backup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            live = root / "widgets.json"
            payload = root / "payload.json"
            backups = root / "backups"
            baseline = baseline_document()
            replacement = payload_from(baseline)
            next(
                widget for widget in replacement["widgets"] if widget["type"] == "focus"
            )["data"]["task"] = "New focus"
            live.write_text(json.dumps(baseline), encoding="utf-8")
            payload.write_text(json.dumps(replacement), encoding="utf-8")
            atomic_write = install_widgets.atomic_write
            writes = 0

            def fail_after_first_replace(path, document):
                nonlocal writes
                writes += 1
                atomic_write(path, document)
                if writes == 1:
                    raise OSError("simulated post-replace failure")

            with mock.patch.object(
                install_widgets, "atomic_write", side_effect=fail_after_first_replace
            ):
                with self.assertRaises(OSError):
                    install_widgets.install_payload(live, payload, backups)

            self.assertEqual(json.loads(live.read_text(encoding="utf-8")), baseline)
            self.assertEqual(live.stat().st_mode & 0o777, 0o644)


if __name__ == "__main__":
    unittest.main()
