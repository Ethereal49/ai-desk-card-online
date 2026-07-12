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
  web_update.py        # complete public demo generator
  test_*.py            # unittest coverage, colocated by script name
deploy/
  caddy/               # checked-in Caddy examples
  scripts/             # live verification gates
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
- Do not add shared helper modules until repeated behavior has a concrete need
  for one; the current duplication is intentional and keeps each CLI portable.

## Examples

- `scripts/update_weather.py`: external-source updater with failure isolation.
- `scripts/update_ai_session.py`: manual updater that preserves unrelated data.
- `scripts/update_codex_usage.py`: bounded parser for local rollout JSONL.
- `deploy/scripts/verify_ip_https.sh`: executable live acceptance gate.
