#!/usr/bin/env python3
"""Collect real local sources and preview or publish the sanitized dashboard."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shlex
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from focus_config import (
    DEFAULT_FOCUS_CONFIG,
    FocusConfig,
    FocusConfigurationError,
    load_focus_config,
    resolve_focus,
)
from source_apple_calendar import collect_calendar
from source_codex_tasks import collect_codex
from source_linear import collect_linear
from update_codex_usage import (
    DEFAULT_MAX_FILES,
    DEFAULT_SESSIONS,
    DEFAULT_STALE_AFTER_SECONDS,
    DEFAULT_TAIL_BYTES,
    find_latest_quota,
)
from widget_contract import (
    ContractError,
    SourceResult,
    build_widget,
    merge_quota,
    merge_source_results,
    owned_payload,
    validate_document,
    widget_map,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_DB = Path.home() / ".codex" / "state_5.sqlite"
DEFAULT_GOALS_DB = Path.home() / ".codex" / "goals_1.sqlite"
REMOTE_HOST_ENV = "AI_DESK_CARD_SSH_HOST"
DEFAULT_REMOTE_PATH = "/srv/ai-desk-card-online/widgets.json"
DEFAULT_REMOTE_LOCK = "/run/lock/ai-desk-card-widgets.lock"
DEFAULT_REMOTE_BACKUPS = "/srv/ai-desk-card-online.backups"
DEFAULT_LOCAL_LOCK = Path("/tmp/ai-desk-card-refresh.lock")
COMMAND_TIMEOUT = 30.0


class RefreshError(RuntimeError):
    pass


class RefreshConfigurationError(RefreshError):
    pass


class AlreadyRunning(RefreshError):
    pass


@contextmanager
def local_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise AlreadyRunning("refresh already running") from exc
        yield


def run_command(
    command: list[str],
    *,
    timeout: float = COMMAND_TIMEOUT,
    runner: Any = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = runner(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RefreshError("external command failed") from exc
    if completed.returncode != 0:
        raise RefreshError("external command failed")
    return completed


def read_baseline(
    host: str,
    remote_path: str,
    *,
    runner: Any = subprocess.run,
) -> dict[str, Any]:
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        host,
        "cat -- " + shlex.quote(remote_path),
    ]
    completed = run_command(command, runner=runner)
    try:
        document = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RefreshError("live widgets JSON is invalid") from exc
    validate_document(document)
    return document


def collect_sources(args: argparse.Namespace) -> tuple[list[SourceResult], dict[str, Any] | None]:
    now = datetime.now().astimezone()
    linear = collect_linear(REPO_ROOT, current_time=now)
    calendar = collect_calendar(REPO_ROOT, current_time=now)
    codex = collect_codex(args.state_db, args.goals_db, current_time=now)
    quota = find_latest_quota(
        args.sessions,
        max(1, args.max_rollout_files),
        max(1024, args.tail_bytes),
        max(0, args.quota_stale_after_seconds),
        current_time=now,
    )
    return [linear, calendar, codex], quota


def health_line(results: list[SourceResult], quota: dict[str, Any] | None) -> str:
    health = [f"{result.source}={result.health}" for result in results]
    quota_health = "stale" if quota is None or quota.get("stale") else "ok"
    health.append(f"codex-quota={quota_health}")
    return "sources " + " ".join(health)


def compose_candidate(
    baseline: dict[str, Any],
    results: list[SourceResult],
    quota: dict[str, Any] | None,
    focus_config: FocusConfig | None = None,
) -> tuple[dict[str, Any], list[str]]:
    existing_quota = widget_map(baseline)["ai-status"]["data"].get("quota")
    candidate, _ = merge_source_results(baseline, results)
    observed_at = next(
        (result.observed_at for result in results if result.source == "codex-metadata"),
        datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    merge_quota(
        candidate,
        quota,
        observed_at,
        existing_quota if isinstance(existing_quota, dict) else None,
    )
    focus_data = resolve_focus(candidate, focus_config or FocusConfig())
    candidate["widgets"] = [
        build_widget("focus", focus_data) if widget["type"] == "focus" else widget
        for widget in candidate["widgets"]
    ]
    baseline_by_type = widget_map(baseline)
    changed = [
        widget_type
        for widget_type, widget in widget_map(candidate).items()
        if widget != baseline_by_type[widget_type]
    ]
    validate_document(candidate)
    return candidate, changed


def publish_candidate(
    candidate: dict[str, Any],
    args: argparse.Namespace,
    *,
    runner: Any = subprocess.run,
) -> str:
    remote_dir = ""
    with tempfile.TemporaryDirectory(prefix="ai-desk-card-publish-") as temp_dir:
        local_dir = Path(temp_dir)
        payload_path = local_dir / "owned-widgets.json"
        payload_path.write_text(
            json.dumps(owned_payload(candidate), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.chmod(payload_path, 0o600)
        try:
            create = run_command(
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    args.host,
                    "mktemp -d /tmp/ai-desk-card-publish.XXXXXX",
                ],
                runner=runner,
            )
            remote_dir = create.stdout.strip()
            if not remote_dir.startswith("/tmp/ai-desk-card-publish.") or "\n" in remote_dir:
                raise RefreshError("remote staging path is invalid")
            run_command(
                [
                    "scp",
                    "-q",
                    str(payload_path),
                    str(REPO_ROOT / "deploy" / "scripts" / "install_widgets.py"),
                    str(REPO_ROOT / "scripts" / "widget_contract.py"),
                    f"{args.host}:{remote_dir}/",
                ],
                runner=runner,
            )
            remote_command = " ".join(
                [
                    "sudo",
                    "python3",
                    shlex.quote(remote_dir + "/install_widgets.py"),
                    "--live",
                    shlex.quote(args.remote_path),
                    "--payload",
                    shlex.quote(remote_dir + "/owned-widgets.json"),
                    "--lock",
                    shlex.quote(args.remote_lock),
                    "--backup-dir",
                    shlex.quote(args.remote_backups),
                ]
            )
            installed = run_command(
                ["ssh", "-o", "BatchMode=yes", args.host, remote_command],
                runner=runner,
            )
            result = installed.stdout.strip()
            if result not in {"publish=updated", "publish=no-change"}:
                raise RefreshError("remote installer response is invalid")
            return result.split("=", 1)[1]
        finally:
            if remote_dir:
                cleanup_failed = False
                try:
                    cleaned = runner(
                        [
                            "ssh",
                            "-o",
                            "BatchMode=yes",
                            args.host,
                            "rm -rf -- " + shlex.quote(remote_dir),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=COMMAND_TIMEOUT,
                        check=False,
                    )
                    cleanup_failed = cleaned.returncode != 0
                except (OSError, subprocess.TimeoutExpired):
                    cleanup_failed = True
                if cleanup_failed:
                    if sys.exc_info()[0] is None:
                        raise RefreshError("remote cleanup failed")
                    print(
                        "publish=warning reason=remote-cleanup",
                        file=sys.stderr,
                    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh the desk card from deterministic read-only local sources"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--source-check", action="store_true")
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument(
        "--host",
        default=os.environ.get(REMOTE_HOST_ENV, ""),
        help=f"SSH host (default: ${REMOTE_HOST_ENV})",
    )
    parser.add_argument("--remote-path", default=DEFAULT_REMOTE_PATH)
    parser.add_argument("--remote-lock", default=DEFAULT_REMOTE_LOCK)
    parser.add_argument("--remote-backups", default=DEFAULT_REMOTE_BACKUPS)
    parser.add_argument("--local-lock", type=Path, default=DEFAULT_LOCAL_LOCK)
    parser.add_argument("--focus-config", type=Path, default=DEFAULT_FOCUS_CONFIG)
    parser.add_argument("--state-db", type=Path, default=DEFAULT_STATE_DB)
    parser.add_argument("--goals-db", type=Path, default=DEFAULT_GOALS_DB)
    parser.add_argument("--sessions", type=Path, default=DEFAULT_SESSIONS)
    parser.add_argument("--max-rollout-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--tail-bytes", type=int, default=DEFAULT_TAIL_BYTES)
    parser.add_argument(
        "--quota-stale-after-seconds",
        type=int,
        default=DEFAULT_STALE_AFTER_SECONDS,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        needs_remote_host = args.publish or (
            not args.source_check and args.baseline is None
        )
        if needs_remote_host and not args.host.strip():
            raise RefreshConfigurationError("remote host is required")
        with local_lock(args.local_lock):
            focus_config = load_focus_config(args.focus_config)
            results, quota = collect_sources(args)
            print(health_line(results, quota))
            partial = any(result.health == "stale" for result in results) or (
                quota is None or bool(quota.get("stale"))
            )
            if any(result.health == "configuration_error" for result in results):
                print("refresh=fatal reason=configuration", file=sys.stderr)
                return 3
            if args.source_check:
                return 2 if partial else 0
            if args.baseline:
                baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
                validate_document(baseline)
            else:
                baseline = read_baseline(args.host, args.remote_path)
            candidate, changed = compose_candidate(baseline, results, quota, focus_config)
            print("changed=" + (",".join(changed) if changed else "none"))
            if args.publish:
                result = publish_candidate(candidate, args)
                print(f"publish={result}")
            else:
                print("publish=preview")
            return 2 if partial else 0
    except AlreadyRunning:
        print("refresh=skipped reason=already-running", file=sys.stderr)
        return 4
    except RefreshConfigurationError:
        print("refresh=fatal reason=configuration", file=sys.stderr)
        return 3
    except RefreshError as exc:
        print(f"refresh=fatal reason={str(exc)}", file=sys.stderr)
        return 1
    except ContractError:
        print("refresh=fatal reason=contract", file=sys.stderr)
        return 1
    except FocusConfigurationError:
        print("refresh=fatal reason=focus-configuration", file=sys.stderr)
        return 3
    except (OSError, json.JSONDecodeError):
        print("refresh=fatal reason=local-io", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
