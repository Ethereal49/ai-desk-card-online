# Error Handling

## Principles

Fail loudly for invalid commands and broken local contracts, but isolate
expected external-source failures so one widget cannot blank the dashboard.

## CLI And Parsing

- Use `argparse` for validation and required arguments.
- Reject malformed structured input instead of guessing. For example,
  `scripts/update_calendar.py` validates `START|TITLE|END` input.
- Let invalid existing JSON raise rather than overwriting it with defaults.
- Parser helpers return `None` only for explicitly unsupported or malformed
  source records, as in `parse_rate_limit_event`.

## Source Failure Isolation

- Preserve the last valid target-widget data.
- Mark that widget `stale` and record a low-sensitivity error label.
- Update other widgets only when the updater owns them.
- Print the underlying operational failure for the CLI operator, but never
  copy exception text into public JSON.

`scripts/update_weather.py:build_weather_data` is the reference pattern: it
catches the network/source failure, preserves previous weather values, writes
`error: "weather unavailable"`, and reports the exception on stdout.

## Shell Gates

Deployment verification scripts use `set -eu`, explicit expected statuses,
and non-zero exits. A skipped or failed check is not a pass.

## Forbidden Patterns

- Empty `except` blocks or silent fallback to a blank document.
- Catching all exceptions around deterministic document updates.
- Publishing secrets or raw external error bodies in `widgets.json` or logs.
