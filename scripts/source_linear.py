#!/usr/bin/env python3
"""Read assigned Linear issues and project only todo display fields."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from widget_contract import SourceResult, now_iso


LINEAR_URL = "https://api.linear.app/graphql"
TEAM_KEYS = ("CODE", "LIFE")
ALLOWED_STATES = frozenset({"started", "unstarted"})
PRIORITY_ORDER = {1: 0, 2: 1, 3: 2, 4: 3, 0: 4, None: 4}
MAX_ISSUES = 500
QUERY = """
query DeskCardIssues($after: String) {
  issues(
    first: 100
    after: $after
    filter: {
      team: { key: { in: [\"CODE\", \"LIFE\"] } }
      assignee: { isMe: { eq: true } }
      state: { type: { in: [\"started\", \"unstarted\"] } }
    }
  ) {
    nodes {
      id
      identifier
      title
      priority
      dueDate
      updatedAt
      parent { id }
      state { type }
      team { key }
    }
    pageInfo { hasNextPage endCursor }
  }
}
""".strip()


class LinearError(RuntimeError):
    pass


class LinearConfigurationError(LinearError):
    pass


class LinearAuthenticationError(LinearConfigurationError):
    pass


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def load_local_config(
    repo_root: Path,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    env = dict(environ if environ is not None else os.environ)
    result: dict[str, str] = {}
    for path in (repo_root / ".env.local", repo_root / ".env"):
        for key, value in _parse_env_file(path).items():
            result.setdefault(key, value)
    for key, value in env.items():
        if value:
            result[key] = value
    return result


def load_api_key(repo_root: Path, environ: Mapping[str, str] | None = None) -> str:
    value = load_local_config(repo_root, environ).get("LINEAR_API_KEY", "").strip()
    if not value:
        raise LinearConfigurationError("linear credential missing")
    return value


def _post_graphql(
    api_key: str,
    variables: dict[str, Any],
    *,
    timeout: float,
    opener: Any = urllib.request.urlopen,
) -> dict[str, Any]:
    payload = json.dumps({"query": QUERY, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        LINEAR_URL,
        data=payload,
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener(request, timeout=timeout) as response:
            document = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            raise LinearAuthenticationError("linear authentication rejected") from None
        raise LinearError("linear request failed") from exc
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise LinearError("linear request failed") from exc
    if not isinstance(document, dict):
        raise LinearError("linear response malformed")
    if document.get("errors"):
        text = json.dumps(document["errors"]).lower()
        if "auth" in text or "unauthorized" in text or "forbidden" in text:
            raise LinearAuthenticationError("linear authentication rejected")
        raise LinearError("linear graphql rejected request")
    return document


def fetch_issues(
    api_key: str,
    *,
    timeout: float = 12.0,
    opener: Any = urllib.request.urlopen,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        document = _post_graphql(api_key, {"after": cursor}, timeout=timeout, opener=opener)
        connection = ((document.get("data") or {}).get("issues") or {})
        nodes = connection.get("nodes")
        page_info = connection.get("pageInfo") or {}
        if not isinstance(nodes, list):
            raise LinearError("linear response malformed")
        issues.extend(node for node in nodes if isinstance(node, dict))
        if len(issues) > MAX_ISSUES:
            raise LinearError("linear result exceeds safety limit")
        if not page_info.get("hasNextPage"):
            return issues
        next_cursor = page_info.get("endCursor")
        if not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            raise LinearError("linear pagination malformed")
        cursor = next_cursor


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _parse_datetime(value: Any) -> datetime:
    if not isinstance(value, str):
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def due_tag(due: date | None, today: date) -> str:
    if due is None:
        return ""
    if due < today:
        return "overdue"
    if due == today:
        return "today"
    if due == today + timedelta(days=1):
        return "tomorrow"
    if due <= today + timedelta(days=7):
        return "this-week"
    return "later"


def _sort_key(issue: dict[str, Any], today: date) -> tuple[Any, ...]:
    due = _parse_date(issue.get("dueDate"))
    due_key = (1, date.max) if due is None else (0, due)
    state_type = ((issue.get("state") or {}).get("type") or "").lower()
    updated = _parse_datetime(issue.get("updatedAt"))
    priority = issue.get("priority")
    return (
        PRIORITY_ORDER.get(priority, 4),
        due_key,
        0 if state_type == "started" else 1,
        -updated.timestamp(),
        str(issue.get("identifier") or issue.get("id") or ""),
    )


def select_issues(
    issues: list[dict[str, Any]],
    *,
    today: date,
    limit: int = 5,
) -> tuple[list[dict[str, str]], int]:
    parent_ids = {
        parent.get("id")
        for issue in issues
        if isinstance(issue.get("parent"), dict)
        for parent in [issue["parent"]]
        if parent.get("id")
    }
    eligible: list[dict[str, Any]] = []
    for issue in issues:
        state_type = ((issue.get("state") or {}).get("type") or "").lower()
        team_key = ((issue.get("team") or {}).get("key") or "").upper()
        title = issue.get("title")
        if (
            state_type not in ALLOWED_STATES
            or team_key not in TEAM_KEYS
            or issue.get("id") in parent_ids
            or not isinstance(title, str)
            or not title.strip()
        ):
            continue
        eligible.append(issue)
    eligible.sort(key=lambda issue: _sort_key(issue, today))
    selected = []
    for issue in eligible[: max(0, limit)]:
        item = {"text": issue["title"].strip()}
        tag = due_tag(_parse_date(issue.get("dueDate")), today)
        if tag:
            item["tag"] = tag
        selected.append(item)
    return selected, len(eligible)


def project_widgets(
    issues: list[dict[str, Any]],
    *,
    today: date,
) -> dict[str, dict[str, Any]]:
    items, total = select_issues(issues, today=today)
    return {
        "todo": {
            "title": "Todo",
            "selected_count": len(items),
            "total_count": total,
            "items": items,
        },
    }


def collect_linear(
    repo_root: Path,
    *,
    current_time: datetime | None = None,
    environ: Mapping[str, str] | None = None,
    opener: Any = urllib.request.urlopen,
) -> SourceResult:
    observed_at = now_iso()
    try:
        api_key = load_api_key(repo_root, environ)
        issues = fetch_issues(api_key, opener=opener)
        now = current_time or datetime.now().astimezone()
        widgets = project_widgets(issues, today=now.date())
        return SourceResult.success("linear", widgets, observed_at)
    except LinearConfigurationError as exc:
        return SourceResult.failure(
            "linear",
            ("todo",),
            str(exc),
            observed_at,
            configuration=True,
        )
    except LinearError:
        return SourceResult.failure(
            "linear", ("todo",), "linear unavailable", observed_at
        )
