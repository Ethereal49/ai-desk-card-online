# Design: Complete Phase 3 Real-Use Gates

## Scope And Architecture

Keep the existing static architecture unchanged:

```text
local Codex rollout JSONL
        |
        v
scripts/update_codex_usage.py
        |
        v
web/widgets.json
        |
        v
authenticated Caddy static site
        |
        v
e-ink device browser
```

This task adds one opt-in diagnostic behavior to the static page, uses physical
device evidence to make one layout decision, and publishes the already-built
quota feature. It does not add a route, backend, database, framework, or new
data source.

## Viewport Diagnostic

The existing page accepts `?viewport=1`.

- Query detection lives in `web/app.js` and follows the file's compatibility
  style: plain functions, `var`, and no new browser APIs that are less compatible
  than the current `XMLHttpRequest` implementation.
- When enabled, the existing `source-label` footer slot displays
  `viewport: <innerWidth>x<innerHeight>`.
- The value is derived from the same viewport fallbacks used by
  `applyViewportScale` and refreshes during the existing resize handler.
- Without the flag, the footer remains `source: widgets.json`.
- The diagnostic remains in production after the task. It exposes only browser
  dimensions and does not change Caddy's runtime-file allowlist.

## Automatic Device Fit

The physical browser differs from desktop Chromium when a fixed-size child is
transformed at an `overflow: hidden` clipping boundary. To avoid depending on
that ordering:

- derive available dimensions from `window.visualViewport` when present, then
  fall back to `window.innerWidth` / `window.innerHeight`;
- when the viewport is below `758x1024`, reserve a 4px safe inset so the card is
  not placed exactly on the lower clipping edge;
- prefer CSS `zoom` when the browser exposes it because it participates in
  layout before clipping;
- retain the existing transform path as a compatibility fallback;
- listen to visual-viewport resize as well as window resize so browser chrome
  and pinch state cannot leave stale sizing.

The diagnostic displays the dimensions actually used by this algorithm. The
detail grid remains three columns; ellipsis continues to be the explicit
overflow behavior for narrow text.

## Device Evidence Gate

After the diagnostic and quota-aware runtime candidate reach live, the user
opens the authenticated URL with `?viewport=1` on the physical device and
records:

- displayed viewport dimensions and observation date;
- font readability at 30-50 cm;
- truncation or overlap in each detail widget;
- visible ghosting or disruptive refresh behavior;
- whether all three detail widgets can be scanned without interaction.

No layout code changes before this evidence exists.

The evidence selects exactly one branch:

1. Keep the current three-column row when it is readable and stable.
2. Add a compact mode when the same simultaneous information architecture can
   work with smaller spacing or type adjustments.
3. Rotate detail widgets only when simultaneous display is not viable and
   periodic replacement is acceptable on the e-ink device.

Do not blend branches. The selected branch becomes the only supported layout;
unselected alternatives remain out of scope.

The 2026-07-18 device evidence selects branch 1: keep the three-column row. The
only layout correction is viewport fitting and a lower-edge safe inset.

## Quota Publication

The existing local updater remains the only ingestion path. Before upload:

- run `scripts/update_codex_usage.py` locally;
- inspect only the resulting `ai-status.data.quota` field boundary;
- confirm no rollout text, paths, account identifiers, credentials, or token
  details appear in `web/widgets.json`;
- preserve stale values when no current event exists.

Publish the diagnostic, quota-aware `app.js`/`styles.css`, and cropped runtime
JSON as one coherent candidate through the existing explicit `scp` plus remote
`sudo install` boundary. This avoids running a new `app.js` against stale live
CSS or JSON. Do not copy local session files or add server-side rollout access.

## Verification Boundaries

Local verification covers unit/static-contract tests and the built-in Browser
at `758x1024`, including normal URL, `?viewport=1`, and failed JSON fetch.

Live verification covers:

- HTTP redirect and HTTPS Basic Auth;
- authenticated runtime `200` and non-runtime `404`;
- security headers and TLS IP SAN;
- authenticated Browser layout and quota rendering;
- the physical device observations above.

Simulated Browser evidence cannot replace physical-device evidence. Config
inspection cannot replace the live HTTPS gate.

## Rollout And Rollback

Before each live sync, create a timestamped remote backup of the affected
runtime files. Deploy one coherent diagnostic + quota candidate, collect device
evidence against that final information density, then deploy only the selected
layout branch if a layout change is justified.

If a live gate fails, restore the latest backup and rerun the gate. If the
device result is ambiguous, retain the current three-column layout and leave the
layout acceptance criteria incomplete rather than guessing.
