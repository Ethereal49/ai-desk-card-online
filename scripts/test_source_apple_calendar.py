import json
import subprocess
import unittest
from datetime import datetime

import source_apple_calendar


TZ = datetime.now().astimezone().tzinfo


def dt(value):
    return datetime.fromisoformat(value).replace(tzinfo=TZ)


class Completed:
    def __init__(self, payload, returncode=0):
        self.stdout = json.dumps(payload)
        self.stderr = "private failure body"
        self.returncode = returncode


class SourceAppleCalendarTests(unittest.TestCase):
    def test_allowlist_requires_non_empty_json_array(self):
        for value in (None, "", "[]", "{}", '[""]', "not-json"):
            with self.subTest(value=value):
                with self.assertRaises(source_apple_calendar.CalendarConfigurationError):
                    source_apple_calendar.parse_calendar_allowlist(value)
        self.assertEqual(
            source_apple_calendar.parse_calendar_allowlist('["Work", "Work", "Home"]'),
            ["Work", "Home"],
        )

    def test_overlap_ordering_cancellation_and_four_item_crop(self):
        now = dt("2026-07-23T23:30:00")
        records = [
            {"title": "Past", "start": dt("2026-07-23T20:00:00").isoformat(), "end": dt("2026-07-23T21:00:00").isoformat()},
            {"title": "Ongoing", "start": dt("2026-07-23T23:00:00").isoformat(), "end": dt("2026-07-24T00:30:00").isoformat()},
            {"title": "All day", "start": dt("2026-07-24T00:00:00").isoformat(), "end": dt("2026-07-25T00:00:00").isoformat(), "all_day": True},
            {"title": "Tomorrow one", "start": dt("2026-07-24T09:00:00").isoformat(), "end": dt("2026-07-24T10:00:00").isoformat()},
            {"title": "Tomorrow two", "start": dt("2026-07-24T11:00:00").isoformat(), "end": dt("2026-07-24T12:00:00").isoformat()},
            {"title": "Overflow", "start": dt("2026-07-24T13:00:00").isoformat(), "end": dt("2026-07-24T14:00:00").isoformat()},
            {"title": "Canceled", "start": dt("2026-07-24T08:00:00").isoformat(), "end": dt("2026-07-24T08:30:00").isoformat(), "status": "cancelled"},
            {"title": "After boundary", "start": dt("2026-07-25T00:00:00").isoformat(), "end": dt("2026-07-25T01:00:00").isoformat()},
        ]

        events, total = source_apple_calendar.project_events(records, now=now)

        self.assertEqual(total, 5)
        self.assertEqual([event["title"] for event in events], ["Ongoing", "All day", "Tomorrow one", "Tomorrow two"])
        self.assertEqual(events[0]["start"], "NOW")
        self.assertEqual(events[1]["start"], "ALL DAY")

    def test_osascript_filters_with_allowlist_and_rejects_unmatched_or_malformed(self):
        observed = {}

        def runner(command, **kwargs):
            observed["command"] = command
            return Completed({"matched_count": 1, "events": []})

        result = source_apple_calendar.run_osascript(["Work"], now=dt("2026-07-23T10:00:00"), runner=runner)
        self.assertEqual(result, [])
        self.assertIn('["Work"]', observed["command"])

        with self.assertRaises(source_apple_calendar.CalendarConfigurationError):
            source_apple_calendar.run_osascript(
                ["Missing"],
                now=dt("2026-07-23T10:00:00"),
                runner=lambda *args, **kwargs: Completed({"matched_count": 0, "events": []}),
            )
        with self.assertRaises(source_apple_calendar.CalendarError):
            source_apple_calendar.run_osascript(
                ["Work"],
                now=dt("2026-07-23T10:00:00"),
                runner=lambda *args, **kwargs: Completed("not-object"),
            )

    def test_permission_denial_and_timeout_are_low_sensitivity_failures(self):
        def denied(*args, **kwargs):
            return Completed({}, returncode=1)

        with self.assertRaisesRegex(source_apple_calendar.CalendarError, "permission"):
            source_apple_calendar.run_osascript(["Work"], now=dt("2026-07-23T10:00:00"), runner=denied)

        def timed_out(*args, **kwargs):
            raise subprocess.TimeoutExpired("osascript", 1)

        with self.assertRaisesRegex(source_apple_calendar.CalendarError, "unavailable"):
            source_apple_calendar.run_osascript(["Work"], now=dt("2026-07-23T10:00:00"), runner=timed_out)

    def test_projection_removes_location_notes_links_and_attendees(self):
        now = dt("2026-07-23T10:00:00")
        records = [{
            "title": "Visible title",
            "start": dt("2026-07-23T11:00:00").isoformat(),
            "end": dt("2026-07-23T12:00:00").isoformat(),
            "location": "private",
            "notes": "private",
            "url": "private",
            "attendees": ["private"],
        }]
        output = json.dumps(source_apple_calendar.project_events(records, now=now)[0])
        self.assertNotIn("private", output)


if __name__ == "__main__":
    unittest.main()
