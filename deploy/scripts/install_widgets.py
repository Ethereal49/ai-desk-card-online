#!/usr/bin/env python3
"""Merge validated local-owned widgets into the live document under a shared lock."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from widget_contract import OWNED_WIDGETS, SLOTS, validate_document, validate_widget, widget_map


DEFAULT_LIVE = Path("/srv/ai-desk-card-online/widgets.json")
DEFAULT_LOCK = Path("/run/lock/ai-desk-card-widgets.lock")
DEFAULT_BACKUP_DIR = Path("/srv/ai-desk-card-online.backups")
DEFAULT_KEEP_BACKUPS = 24


class InstallError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot read valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise InstallError(f"JSON root must be an object: {path}")
    return value


def load_owned_payload(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if set(payload) != {"widgets"} or not isinstance(payload["widgets"], list):
        raise InstallError("payload contract is invalid")
    seen: set[str] = set()
    for widget in payload["widgets"]:
        validate_widget(widget, owned_only=True)
        widget_type = widget["type"]
        if widget_type in seen:
            raise InstallError(f"duplicate payload widget: {widget_type}")
        seen.add(widget_type)
    if seen != set(OWNED_WIDGETS):
        raise InstallError("payload must contain every locally owned widget")
    return payload["widgets"]


def atomic_write(path: Path, document: dict[str, Any]) -> None:
    payload = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), delete=False
    ) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    try:
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def prune_backups(directory: Path, keep: int) -> None:
    backups = sorted(
        directory.glob("widgets-before-publish-*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in backups[max(1, keep) :]:
        path.unlink()


def install_payload(
    live_path: Path,
    payload_path: Path,
    backup_dir: Path,
    *,
    keep_backups: int = DEFAULT_KEEP_BACKUPS,
) -> str:
    current = load_json(live_path)
    validate_document(current)
    owned_widgets = load_owned_payload(payload_path)
    current_by_type = widget_map(current)
    next_by_type = dict(current_by_type)
    next_by_type.update({widget["type"]: widget for widget in owned_widgets})
    next_widgets = [next_by_type[widget_type] for widget_type in SLOTS]
    if next_widgets == current["widgets"]:
        os.chmod(live_path, 0o644)
        return "no-change"

    candidate = dict(current)
    candidate["updated_at"] = now_iso()
    candidate["widgets"] = next_widgets
    validate_document(candidate)

    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    backup = backup_dir / f"widgets-before-publish-{stamp}.json"
    suffix = 1
    while backup.exists():
        backup = backup_dir / f"widgets-before-publish-{stamp}-{suffix}.json"
        suffix += 1
    shutil.copy2(live_path, backup)
    os.chmod(backup, 0o600)

    install_started = False
    try:
        install_started = True
        atomic_write(live_path, candidate)
        verified = load_json(live_path)
        validate_document(verified)
        if verified != candidate or (live_path.stat().st_mode & 0o777) != 0o644:
            raise InstallError("installed document verification failed")
    except Exception:
        if install_started:
            restored = load_json(backup)
            atomic_write(live_path, restored)
        raise
    prune_backups(backup_dir, keep_backups)
    return "updated"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install owned widgets under a shared lock")
    parser.add_argument("--live", type=Path, default=DEFAULT_LIVE)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    parser.add_argument("--keep-backups", type=int, default=DEFAULT_KEEP_BACKUPS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.lock.parent.mkdir(parents=True, exist_ok=True)
    with args.lock.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        result = install_payload(
            args.live,
            args.payload,
            args.backup_dir,
            keep_backups=max(1, args.keep_backups),
        )
    print(f"publish={result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
