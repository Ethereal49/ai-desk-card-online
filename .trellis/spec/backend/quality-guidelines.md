# Backend Quality Guidelines

## Required Properties

- Python scripts use the standard library and remain directly executable.
- Updaters preserve unrelated widgets and stable top-level fields.
- Runtime JSON writes are atomic and result in mode `0644`.
- External failures preserve last known good values and expose stale state.
- Privacy boundaries are tested through allowed and forbidden output fields.
- Live deployment claims require the executable verification gate, not config
  inspection alone.
- Current-facing public files and examples contain no owner host, live IP,
  owner home path, or historical backup identifier. Archived Trellis evidence
  remains immutable.
- GitHub Actions uses read-only permissions, full-SHA-pinned official actions,
  and no secrets or live-network product checks.

## Testing

Use `unittest` with temporary directories and local fixtures. Tests import
deterministic helpers directly and exercise the CLI when file permissions or
argument behavior matters.

Reference tests:

- `scripts/test_update_weather.py`: parsing, targeted update, stale fallback,
  CLI fixture, and permissions.
- `scripts/test_update_ai_session.py`: privacy boundary and preservation.
- `scripts/test_update_codex_usage.py`: schema variants, bounded scanning,
  event ordering, stale behavior, and atomic output.
- `scripts/test_web_update.py`: complete public demo contract.
- `scripts/test_open_source_contract.py`: public project files and links,
  generic examples, neutral plist, workflow permissions/action pins, and
  pre-network shell configuration failures.

Run the full suite with:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

## Review Checklist

- Does the test fail if the intended privacy or preservation rule regresses?
- Is network behavior covered with a fixture rather than a live dependency?
- Does malformed input fail loudly?
- Are skipped checks reported as skipped rather than passed?
- Was `PLAN_web.md` updated after the project state changed?
