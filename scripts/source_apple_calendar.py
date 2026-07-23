#!/usr/bin/env python3
"""Read allowlisted Apple Calendar events through one bounded osascript call."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any, Mapping

from source_linear import load_local_config
from widget_contract import SourceResult, now_iso


MAX_SOURCE_EVENTS = 256
JXA_SCRIPT = r"""
function run(argv) {
  var allowed = JSON.parse(argv[0]);
  var lower = new Date(argv[1]);
  var upper = new Date(argv[2]);
  var app = Application('Calendar');
  var calendars = app.calendars();
  var events = [];
  var matched = 0;
  for (var i = 0; i < calendars.length; i += 1) {
    var calendar = calendars[i];
    var name = String(calendar.name());
    if (allowed.indexOf(name) === -1) continue;
    matched += 1;
    var calendarEvents = calendar.events();
    for (var j = 0; j < calendarEvents.length && events.length < 256; j += 1) {
      var event = calendarEvents[j];
      var start = event.startDate();
      var end = event.endDate();
      if (end <= lower || start > upper) continue;
      events.push({
        title: String(event.summary() || ''),
        start: start.toISOString(),
        end: end.toISOString(),
        all_day: Boolean(event.alldayEvent()),
        status: String(event.status() || '')
      });
    }
  }
  return JSON.stringify({matched_count: matched, events: events});
}
""".strip()


class CalendarError(RuntimeError):
    pass


class CalendarConfigurationError(CalendarError):
    pass


def parse_calendar_allowlist(value: str | None) -> list[str]:
    if not value:
        raise CalendarConfigurationError("calendar allowlist missing")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise CalendarConfigurationError("calendar allowlist malformed") from exc
    if (
        not isinstance(parsed, list)
        or not parsed
        or any(not isinstance(item, str) or not item.strip() for item in parsed)
    ):
        raise CalendarConfigurationError("calendar allowlist must be a non-empty JSON array")
    return list(dict.fromkeys(item.strip() for item in parsed))


def calendar_window(now: datetime) -> tuple[datetime, datetime]:
    if now.tzinfo is None:
        now = now.astimezone()
    tomorrow = now.date() + timedelta(days=1)
    upper = datetime.combine(tomorrow, time(23, 59, 59), tzinfo=now.tzinfo)
    return now, upper


def _parse_timestamp(value: Any, timezone_info: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone_info)
    return parsed.astimezone(timezone_info)


def project_events(
    records: list[dict[str, Any]],
    *,
    now: datetime,
    limit: int = 4,
) -> tuple[list[dict[str, str]], int]:
    lower, upper = calendar_window(now)
    eligible: list[tuple[bool, datetime, datetime, bool, str]] = []
    for record in records[:MAX_SOURCE_EVENTS]:
        if not isinstance(record, dict):
            continue
        title = record.get("title")
        start = _parse_timestamp(record.get("start"), lower.tzinfo)
        end = _parse_timestamp(record.get("end"), lower.tzinfo)
        status = str(record.get("status") or "").lower()
        if (
            not isinstance(title, str)
            or not title.strip()
            or start is None
            or end is None
            or end <= lower
            or start > upper
            or "cancel" in status
        ):
            continue
        eligible.append((start <= lower < end, start, end, bool(record.get("all_day")), title.strip()))
    eligible.sort(key=lambda item: (0 if item[0] else 1, item[1], item[2], item[4]))
    projected: list[dict[str, str]] = []
    for ongoing, start, end, all_day, title in eligible[: max(0, limit)]:
        if ongoing:
            start_label = "NOW"
        elif all_day:
            start_label = "ALL DAY"
        elif start.date() > lower.date():
            start_label = "TMR " + start.strftime("%H:%M")
        else:
            start_label = start.strftime("%H:%M")
        event = {"start": start_label, "title": title}
        if not all_day:
            event["end"] = end.strftime("%H:%M")
        projected.append(event)
    return projected, len(eligible)


def run_osascript(
    calendars: list[str],
    *,
    now: datetime,
    timeout: float = 15.0,
    runner: Any = subprocess.run,
) -> list[dict[str, Any]]:
    lower, upper = calendar_window(now)
    command = [
        "/usr/bin/osascript",
        "-l",
        "JavaScript",
        "-e",
        JXA_SCRIPT,
        "--",
        json.dumps(calendars, ensure_ascii=False),
        lower.isoformat(),
        upper.isoformat(),
    ]
    try:
        completed = runner(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CalendarError("calendar unavailable") from exc
    if completed.returncode != 0:
        raise CalendarError("calendar permission or source failure")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CalendarError("calendar response malformed") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise CalendarError("calendar response malformed")
    if payload.get("matched_count") == 0:
        raise CalendarConfigurationError("calendar allowlist matched no calendars")
    if len(payload["events"]) > MAX_SOURCE_EVENTS:
        raise CalendarError("calendar result exceeds safety limit")
    return payload["events"]


def collect_calendar(
    repo_root: Path,
    *,
    current_time: datetime | None = None,
    environ: Mapping[str, str] | None = None,
    runner: Any = subprocess.run,
) -> SourceResult:
    observed_at = now_iso()
    now = current_time or datetime.now().astimezone()
    try:
        config = load_local_config(repo_root, environ)
        calendars = parse_calendar_allowlist(config.get("AI_DESK_CARD_CALENDARS"))
        records = run_osascript(calendars, now=now, runner=runner)
        events, total = project_events(records, now=now)
        return SourceResult.success(
            "apple-calendar",
            {
                "calendar": {
                    "now_iso": now.isoformat(timespec="seconds"),
                    "selected_count": len(events),
                    "total_count": total,
                    "events": events,
                }
            },
            observed_at,
        )
    except CalendarConfigurationError as exc:
        return SourceResult.failure(
            "apple-calendar",
            ("calendar",),
            str(exc),
            observed_at,
            configuration=True,
        )
    except CalendarError:
        return SourceResult.failure(
            "apple-calendar", ("calendar",), "calendar unavailable", observed_at
        )
