import plistlib
import re
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PUBLIC_PATHS = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    "docs/assets/dashboard-preview.png",
)

CURRENT_FACING_PATHS = (
    "README.md",
    "AGENTS.md",
    "PLAN_web.md",
    "web/README.md",
    "deploy/README.md",
    "scripts/refresh_dashboard.py",
    "deploy/scripts/verify_ip_https.sh",
    "deploy/scripts/verify_ip_only.sh",
    "deploy/caddy/Caddyfile.example",
    "deploy/caddy/Caddyfile.ip-https.example",
    "deploy/caddy/Caddyfile.ip-only.example",
    "deploy/launchd/com.example.ai-desk-card-refresh.plist.example",
    "deploy/systemd/ai-desk-card-weather.service",
    ".trellis/spec/backend/certificate-renewal-contract.md",
    ".trellis/spec/backend/real-data-publish-contract.md",
)

FORBIDDEN_CURRENT_ANCHORS = (
    "myecs",
    "112.74.73.134",
    "/Users/ethereal",
    "com.ethereal",
    "web-before-role-",
    "widgets-before-smoke-",
)


def run_shell_gate(script: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/sh", str(REPO_ROOT / script)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class OpenSourceContractTests(unittest.TestCase):
    def test_required_public_project_files_exist(self):
        missing = [
            path for path in REQUIRED_PUBLIC_PATHS if not (REPO_ROOT / path).is_file()
        ]
        self.assertEqual(missing, [])

    def test_license_is_mit_with_approved_holder(self):
        text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("MIT License\n"))
        self.assertIn("Copyright (c) 2026 Ethereal49", text)
        self.assertIn("THE SOFTWARE IS PROVIDED \"AS IS\"", text)

    def test_documentation_screenshot_is_real_target_size_png(self):
        data = (REPO_ROOT / "docs/assets/dashboard-preview.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(data[12:16], b"IHDR")
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (758, 1024))

    def test_root_markdown_local_links_resolve(self):
        markdown_paths = (
            REPO_ROOT / "README.md",
            REPO_ROOT / "CONTRIBUTING.md",
            REPO_ROOT / "SECURITY.md",
            REPO_ROOT / "CODE_OF_CONDUCT.md",
        )
        failures = []
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for markdown_path in markdown_paths:
            text = markdown_path.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = target.split("#", 1)[0]
                if not path_text:
                    continue
                resolved = (markdown_path.parent / path_text).resolve()
                if not resolved.exists():
                    failures.append(f"{markdown_path.name}: {target}")
        self.assertEqual(failures, [])

    def test_current_facing_files_exclude_owner_specific_anchors(self):
        failures = []
        for relative_path in CURRENT_FACING_PATHS:
            path = REPO_ROOT / relative_path
            text = path.read_text(encoding="utf-8")
            for anchor in FORBIDDEN_CURRENT_ANCHORS:
                if anchor in text:
                    failures.append(f"{relative_path}: {anchor}")
        self.assertEqual(failures, [])

    def test_launchd_example_is_valid_and_uses_neutral_placeholders(self):
        path = (
            REPO_ROOT
            / "deploy/launchd/com.example.ai-desk-card-refresh.plist.example"
        )
        with path.open("rb") as handle:
            document = plistlib.load(handle)

        self.assertEqual(document["Label"], "com.example.ai-desk-card-refresh")
        self.assertIn("/ABSOLUTE/PATH/TO/ai-desk-card-online", str(document))
        self.assertNotIn(str(Path.home()), str(document))

    def test_ci_is_read_only_and_actions_are_full_sha_pinned(self):
        text = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("pull_request_target:", text)
        action_uses = re.findall(r"uses:\s+([^\s]+)", text)
        self.assertGreaterEqual(len(action_uses), 2)
        for action in action_uses:
            self.assertRegex(action, r"^actions/[a-z-]+@[0-9a-f]{40}$")

    def test_ip_only_gate_requires_url_before_curl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            marker = root / "curl-called"
            fake_curl = root / "curl"
            fake_curl.write_text(
                f"#!/bin/sh\n: > {marker}\nexit 99\n",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)
            env = {
                "PATH": f"{root}:/usr/bin:/bin",
            }

            result = run_shell_gate("deploy/scripts/verify_ip_only.sh", env)

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            self.assertIn("AI_DESK_CARD_URL", result.stderr)

    def test_ip_https_gate_requires_endpoint_inputs_before_curl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            marker = root / "curl-called"
            fake_curl = root / "curl"
            fake_curl.write_text(
                f"#!/bin/sh\n: > {marker}\nexit 99\n",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)
            env = {
                "PATH": f"{root}:/usr/bin:/bin",
                "AI_DESK_CARD_AUTH_PASSWORD": "test-only",
            }

            result = run_shell_gate("deploy/scripts/verify_ip_https.sh", env)

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            self.assertIn("AI_DESK_CARD_BASE_URL", result.stderr)


if __name__ == "__main__":
    unittest.main()
