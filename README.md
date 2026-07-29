# AI Desk Card Online

**English** | [简体中文](README.zh-CN.md)

[![CI](https://github.com/Ethereal49/ai-desk-card-online/actions/workflows/ci.yml/badge.svg)](https://github.com/Ethereal49/ai-desk-card-online/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org/downloads/)
[![Vanilla JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A static, privacy-conscious dashboard for `758x1024` e-ink browsers.

AI Desk Card Online turns a small set of deliberately cropped signals into an
ambient desk display. The browser renders plain HTML, CSS, JavaScript, and
`widgets.json`; there is no frontend build step or application server.

![AI Desk Card dashboard at 758x1024](docs/assets/dashboard-preview.png)

## Why This Project Exists

Most dashboards optimize for interaction and density. This one optimizes for a
glance from 30–50 cm away:

- a fixed portrait surface with no scrolling at the target viewport;
- high contrast, large type, and no animation or decorative effects;
- six bounded widgets with explicit source ownership;
- resilient rendering when data is missing, stale, or temporarily offline;
- a privacy boundary that publishes display fields instead of raw source
  records.

## Architecture

```text
read-only sources
  -> bounded privacy projection
  -> last-known-good merge and Focus resolution
  -> widgets.json
  -> static browser dashboard
```

The production deployment can publish five locally owned widgets over SSH
while a server timer owns weather. The locked installer re-reads the live
document, preserves server-owned weather, validates the complete payload, and
installs it atomically.

## Widgets

| Widget | Purpose | Maximum public detail |
| --- | --- | --- |
| `weather` | Current conditions and forecast | Current plus two forecast rows |
| `ai-status` | AI session and quota summary | Bounded status fields |
| `focus` | One headline priority | One selected projection |
| `ai-tasks` | AI work-state counts | Four aggregate counts |
| `calendar` | Upcoming schedule | Four cropped events |
| `todo` | Ranked next actions | Five cropped items |

The stable top-level contract is:
`updated_at`, `layout`, `refresh_seconds`, and `widgets`. See
[the public example](web/widgets.example.json) and the detailed
[web contract](web/README.md).

## Quick Start

Requirements: Python 3.11+ and a modern browser.

```bash
git clone https://github.com/Ethereal49/ai-desk-card-online.git
cd ai-desk-card-online
python3 -m http.server 4173 --directory web
```

Open <http://127.0.0.1:4173/>. The checked-in `web/widgets.json` is safe demo
data; `web/widgets.example.json` documents the same public schema.

For an isolated example-data preview:

```bash
temporary_dir="$(mktemp -d)"
cp -R web/. "$temporary_dir/"
cp web/widgets.example.json "$temporary_dir/widgets.json"
python3 -m http.server 4173 --directory "$temporary_dir"
```

Remove the temporary directory after stopping the server.

## Real Data And Privacy

Real-source refresh is optional. It reads local Linear, Apple Calendar, and
Codex metadata, then projects only allowlisted display fields. Configuration is
loaded from environment variables or an ignored mode-`0600` `.env.local`:

```text
LINEAR_API_KEY=<read-only API key>
AI_DESK_CARD_CALENDARS=["Work","Personal"]
AI_DESK_CARD_SSH_HOST=card-host
```

Run the source and publication stages explicitly:

```bash
scripts/refresh_dashboard.py --source-check
scripts/refresh_dashboard.py --preview
scripts/refresh_dashboard.py --publish
```

`--source-check` never needs an SSH host. A remote preview or publish requires
`AI_DESK_CARD_SSH_HOST` or `--host`; missing remote configuration fails before
SSH.

Never put tokens, credentials, transcripts, prompts, responses, source IDs,
paths, meeting links, attendees, or private notes in `widgets.json`. Cropped
real titles can still be sensitive, so private deployments require HTTPS and
access control. Read the [deployment guide](deploy/README.md) before publishing
real data.

## Validation

The deterministic checks use only Python, Node.js, and shell tools:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m compileall -q scripts .codex/hooks .trellis/scripts deploy/scripts
node --check web/app.js
bash -n deploy/scripts/*.sh
python3 .codex/hooks/ensure_plan_updated.py
git diff --check
```

Frontend and screenshot changes also require Browser validation at exactly
`758x1024`, including `scrollHeight <= innerHeight`, all six widgets, and the
failed-fetch fallback. The physical device remains the final readability
authority.

## Known Limitations

- No stable privacy-safe local source currently provides fresh Codex quota
  windows. Last-known-good quota stays explicitly stale and refresh exits `2`.
- The browser currently creates its polling interval from the initial
  `300`-second fallback. A later non-300 `refresh_seconds` value changes the
  label but does not reschedule that interval.
- A `weather.current` Focus can lag one local scheduler tick if server weather
  changes concurrently with a publish.
- Browsers without line-clamp support keep content bounded but may not show a
  visible ellipsis.

## Project Guides

- [Web behavior and diagnostic tools](web/README.md)
- [Deployment and operator guide](deploy/README.md)
- [Product and architecture plan](PLAN_web.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## License

[MIT](LICENSE) © 2026 Ethereal49.
