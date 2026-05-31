# AGENTS.md

## Project Intent

This repository builds a browser-based AI desk card for a `758x1024` e-ink display.
The first version is a static web dashboard fed by `web/widgets.json`.

The source project to reuse is `/Users/ethereal/Documents/Code/ai-desk-card`.
That repository is the reference for product intent, widget taxonomy, schema naming, and e-ink design lessons.

## Working Rules

- Follow this repository's `PLAN_web.md` as the product and architecture source of truth.
- The confirmed device viewport and validation target is `758x1024` (`width x height`).
- UI/layout validation must use the Codex built-in Browser by default.
- Keep the MVP static: HTML, CSS, vanilla JavaScript, and JSON.
- Do not add React, Vite, Astro, backend APIs, build steps, firmware code, BLE, USB, or daemon logic unless the plan is updated first.
- Make the smallest change that satisfies the current phase.
- Keep code under the directory that owns it. Web MVP files live in `web/`.
- Generated QA artifacts live in `output/` and should not be committed.
- At the end of each Codex work turn, keep `PLAN_web.md` updated. The project-local Codex `Stop` hook in `.codex/hooks.json` enforces this by checking plan freshness.

## Reuse Boundary

Reuse from `/Users/ethereal/Documents/Code/ai-desk-card`:

- product principles from `PRODUCT.md`, `README.md`, and the source repository's `PLAN_web.md` as historical reference;
- widget type and field naming ideas from `plugin/skills/card-widget/schemas/*.schema.json`;
- e-ink layout lessons from `daemon/card_render.py` and `daemon/card_render_color.py`, as reference only.

Do not copy or depend on:

- firmware under `src/`;
- `platformio.ini`;
- BLE, USB serial, raw frame, `/frame`, `/cmd`, or mDNS transport code;
- `daemon/card_daemon.py` transport behavior;
- Pillow image rendering as the default web rendering path.

## Structure

```text
.codex/
  hooks.json
  hooks/
    ensure_plan_updated.py
web/
  README.md
  index.html
  styles.css
  app.js
  widgets.example.json
  widgets.json
scripts/
  test_plan_guard.py
  web_update.py
  test_web_update.py
deploy/
  README.md
  caddy/
    Caddyfile.example
    Caddyfile.ip-only.example
  scripts/
    verify_ip_only.sh
output/
  browser/
```

Future server work, if needed, belongs in `web-server/`, not inside `web/`.
Deployment configuration belongs in `deploy/`; it must not contain real passwords,
tokens, private keys, or server-only generated files.

## Data Contract

- `widgets.json` is the runtime data file.
- `widgets.example.json` is the documented example.
- Keep top-level fields stable: `updated_at`, `layout`, `refresh_seconds`, `widgets`.
- Supported Phase 1 widget types: `focus`, `weather`, `calendar`, `todo`.
- The UI must tolerate missing fields and failed fetches without blanking the page.

## Layout Rules

- Primary target viewport: `758x1024` (`width x height`).
- No vertical scrolling at the target viewport.
- No animation, transitions, hover-only UI, gradients, or decorative shadows.
- Use high contrast and large text suitable for e-ink.
- If a plan dimension conflicts with the no-scroll target, the no-scroll target wins.

## Validation

Before calling Phase 1 done:

- Serve `web/` with a static server.
- Verify the page loads from `widgets.json`.
- Capture or inspect a `758x1024` viewport with the Codex built-in Browser.
- Confirm `document.scrollingElement.scrollHeight <= window.innerHeight`.
- Confirm the UI still renders if `widgets.json` cannot be fetched.
