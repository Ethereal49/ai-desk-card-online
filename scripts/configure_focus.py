#!/usr/bin/env python3
"""Safely inspect and replace the private local Focus configuration."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from focus_config import (
    ALLOWED_SOURCES,
    DEFAULT_FOCUS_CONFIG,
    DEFAULT_SOURCE,
    FocusConfig,
    FocusConfigurationError,
    load_focus_config,
    parse_focus_config,
)


def config_document(config: FocusConfig) -> dict[str, str]:
    document = {"source": config.source}
    for key in ("task", "subtitle", "big_text"):
        value = getattr(config, key)
        if value is not None:
            document[key] = value
    return document


def status_line(config: FocusConfig) -> str:
    fields = " ".join(
        f"{key}={'present' if getattr(config, key) is not None else 'absent'}"
        for key in ("task", "subtitle", "big_text")
    )
    return f"focus-config=ok source={config.source} {fields}"


def ensure_private_parent(path: Path) -> None:
    parent = path.parent
    created = False
    try:
        parent.mkdir(mode=0o700, parents=True, exist_ok=False)
        created = True
    except FileExistsError:
        pass
    if not parent.is_dir():
        raise NotADirectoryError(str(parent))
    if created:
        os.chmod(parent, 0o700)


def sync_directory(path: Path) -> None:
    descriptor: int | None = None
    try:
        descriptor = os.open(path, os.O_RDONLY)
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def atomic_write_config(path: Path, config: FocusConfig) -> None:
    ensure_private_parent(path)
    payload = json.dumps(config_document(config), ensure_ascii=False, indent=2) + "\n"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(payload)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)
        temp_path = None
        sync_directory(path.parent)
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def validate_existing(path: Path) -> None:
    if path.exists():
        load_focus_config(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or replace the private local Focus configuration. "
            "Output reports structure only and this command does not publish."
        ),
        epilog="Never print configured text; the next normal refresh reads a valid change.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_FOCUS_CONFIG)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("get", help="Validate and report configuration structure")
    set_parser = commands.add_parser(
        "set", help="Validate and atomically replace configuration"
    )
    set_parser.add_argument("--source", required=True, choices=sorted(ALLOWED_SOURCES))
    set_parser.add_argument("--task")
    set_parser.add_argument("--subtitle")
    set_parser.add_argument("--big-text")
    commands.add_parser("reset", help="Write the explicit todo.first default")
    return parser


def candidate_from_args(args: argparse.Namespace) -> FocusConfig:
    document = {"source": args.source}
    for key in ("task", "subtitle", "big_text"):
        value = getattr(args, key)
        if value is not None:
            document[key] = value
    return parse_focus_config(document)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "get":
            config = load_focus_config(args.config)
        elif args.command == "set":
            config = candidate_from_args(args)
            validate_existing(args.config)
            atomic_write_config(args.config, config)
        elif args.command == "reset":
            config = parse_focus_config({"source": DEFAULT_SOURCE})
            validate_existing(args.config)
            atomic_write_config(args.config, config)
        else:
            raise AssertionError(f"unsupported command: {args.command}")
        print(status_line(config))
        return 0
    except FocusConfigurationError as exc:
        if isinstance(exc.__cause__, OSError):
            print("focus-config=fatal reason=local-io", file=sys.stderr)
            return 1
        print("focus-config=fatal reason=configuration", file=sys.stderr)
        return 3
    except OSError:
        print("focus-config=fatal reason=local-io", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
