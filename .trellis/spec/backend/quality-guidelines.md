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
- The plan freshness guard ignores only Trellis-managed closeout records under
  `.trellis/tasks/archive/` and `.trellis/workspace/`; active task artifacts,
  code-specs, and ordinary project files remain plan-relevant.

## Plan Freshness Boundary

Trellis writes archive and journal records after the last valid product-plan
update:

```text
plan/work commit -> task archive auto-commit -> journal auto-commit
```

Ignoring those two closeout roots makes the sequence terminate. Do not ignore
all of `.trellis/`: a newer active task PRD or code-spec must still block a
stale plan.

Required assertions in `scripts/test_plan_guard.py`:

- newer `.trellis/tasks/archive/**` and `.trellis/workspace/**` files are
  excluded;
- newer `.trellis/tasks/<active-task>/**` files are reported;
- newer ordinary project files are reported.

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
- Can Trellis archive and journal auto-commits complete without creating a
  plan/journal freshness loop?
