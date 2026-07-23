# Backend Directory Structure

## Current Boundary

This repository has no backend service or API. The server-side behavior is a
small set of Python CLI updaters plus deployment configuration. Do not create a
backend merely to organize code; future server work belongs in `web-server/`
only after `PLAN_web.md` is updated.

## Layout

```text
scripts/
  update_*.py          # narrow widgets.json updaters
  source_*.py          # deterministic read-only real-data adapters
  widget_contract.py   # shared public JSON/privacy contract
  refresh_dashboard.py # preview/publish orchestrator
  run_scheduled_refresh.py # bounded LaunchAgent entrypoint
  web_update.py        # complete public demo generator
  test_*.py            # unittest coverage, colocated by script name
deploy/
  caddy/               # checked-in Caddy examples
  launchd/             # credential-free macOS scheduler template
  scripts/             # live verification gates and remote installer
  systemd/             # service and timer units
web/
  widgets.json         # runtime state
  widgets.example.json # documented contract example
```

## Organization Rules

- Keep each updater as a standalone standard-library Python script.
- Put deterministic parsing and document-update functions above CLI parsing so
  tests can import them directly.
- Use `Path(__file__).resolve().parents[1]` for repository-relative defaults.
- Keep deployment assets under `deploy/`; never mix server configuration into
  `web/`.
- Name scripts `update_<widget>.py` and tests `test_update_<widget>.py`.
- Shared helpers require a concrete cross-source contract. `widget_contract.py`
  is the single validator/merge boundary for source adapters and publication;
  narrow manual `update_*.py` scripts remain independently executable.

## Examples

- `scripts/update_weather.py`: external-source updater with failure isolation.
- `scripts/update_ai_session.py`: manual updater that preserves unrelated data.
- `scripts/update_codex_usage.py`: bounded parser for local rollout JSONL.
- `deploy/scripts/verify_ip_https.sh`: executable live acceptance gate.
