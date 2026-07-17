# Complete Phase 3 real-use gates

## Goal

Close the remaining Phase 3 evidence gaps so the desk card has a verified live
Codex quota display and a device-backed decision for the detail-row layout.

The task must produce evidence, not speculative redesign. The current
three-column layout remains unchanged unless real e-ink device observations
show a concrete readability or rendering problem.

## Background

- The static app and six-widget role-based layout already pass the simulated
  `758x1024` Browser gate with no page or widget overflow.
- The live site already has HTTPS, Basic Auth, security headers, and weather
  automation, but its `app.js`, `styles.css`, and `widgets.json` do not yet
  expose the completed Codex quota feature.
- `scripts/update_codex_usage.py` already parses bounded local rollout JSONL,
  normalizes 5-hour and weekly windows, preserves old quota as stale, and has
  unit coverage for malformed or missing data.
- `PLAN_web.md` makes the physical e-ink device the authority for choosing
  between the current three columns, a compact mode, or rotating detail
  widgets.
- The physical e-ink device is available for this task. Device measurement and
  readability evidence therefore precede any layout decision.
- The device browser can open the existing authenticated live URL with query
  parameters. A query-gated viewport readout can therefore use the existing
  page without adding a public diagnostic file or changing Caddy's allowlist.
- Physical-device evidence on 2026-07-18 reports `740x951`, readable text, no
  overlap, no ghosting, visible quota states, and acceptable three-column
  information architecture. Text truncation is frequent but acceptable.
- After the fit fix, the device reports a `467x600` visual viewport. This is
  the content area used for automatic fitting; the earlier `740x951` value is
  the browser layout viewport, not the final visible CSS area.
- The physical browser clips the lower border and requires manual pinch-out on
  initial load even though desktop Chromium fits the same viewport. Automatic
  fit must therefore use the actual visual viewport and avoid relying solely on
  a transformed box at the clipping boundary.

## Requirements

- Record the real device's `window.innerWidth` and `window.innerHeight`.
- Expose the viewport readout only when an explicit query parameter is present;
  the normal live URL must remain visually unchanged.
- Keep the query-gated viewport diagnostic after this task so future device or
  browser changes can be measured without redeploying a temporary probe.
- Evaluate the current detail row at normal viewing distance for font size,
  truncation, overlap, ghosting, and general scanability.
- Select exactly one layout outcome from real evidence: keep three columns,
  add a compact mode, or rotate detail widgets.
- Do not change layout CSS before device evidence identifies a problem.
- Automatically fit the complete card on initial load without manual pinch
  gestures, while retaining the current three-column detail layout.
- Leave a small safe inset when the real viewport is smaller than the design
  target so the bottom border is not placed exactly on the clipping boundary.
- Publish the completed quota-aware static assets and a cropped quota summary
  through the existing explicit deployment boundary.
- Do not upload local rollout files, OAuth credentials, account identifiers,
  transcripts, token details, or session paths.
- Verify quota behavior for fresh data and stale/unavailable data without
  clearing the last known values.
- Keep the implementation static: HTML, CSS, vanilla JavaScript, JSON, and the
  existing Python updater scripts.
- Update `PLAN_web.md` with the measured device result, selected layout, live
  verification snapshot, and any remaining Phase 4 gate.

## Acceptance Criteria

- [x] Real device viewport dimensions are recorded with the observation date.
- [x] `?viewport=1` shows the current viewport dimensions in the existing page,
      updates after resize, and does not change the normal URL presentation.
- [x] Real device readability findings cover font size, truncation, overlap,
      ghosting, and 30-50 cm viewing.
- [x] One layout outcome is selected and justified by the recorded evidence.
- [x] On a fresh device page load, the complete card and lower border fit
      automatically without manual pinch zoom; the visual viewport is
      `467x600` on this device.
- [x] If the layout changes, static contract tests and the `758x1024` Browser
      gate are updated and pass; if it does not change, that no-change decision
      is explicitly recorded.
- [x] Live assets include the quota UI and authenticated `/widgets.json`
      contains only the approved low-sensitivity quota fields.
- [x] HTTP redirect, unauthenticated `401`, authenticated runtime `200`,
      authenticated non-runtime `404`, security headers, and TLS SAN gates pass.
- [x] Authenticated live Browser validation reports no page or widget overflow
      at `758x1024` and displays the six widgets plus 5h/7d quota states.
- [x] Fresh and stale/unavailable quota paths are verified without copying raw
      rollout content or clearing previous values.
- [x] The full Python test suite, plan freshness check, and hooks JSON check pass.
- [x] `PLAN_web.md` reflects the final Phase 3 status and evidence.

## Out Of Scope

- New widgets, backend APIs, databases, frameworks, build systems, or account
  systems.
- Automatic collection of focus, todo, calendar, or raw AI session content.
- Layout changes based only on desktop screenshots or aesthetic preference.
- Replacing the accepted three-column layout only to eliminate expected text
  ellipses.
- Declaring Phase 4 complete without restart, refresh-cycle, and certificate
  behavior observed on the physical device.

## Notes

- Source of truth: `PLAN_web.md`, especially Phase 3 remaining gates and the
  no-speculative-layout rule.
- Execution order is local diagnostic/quota validation, one coherent live
  candidate publication, physical-device evidence, one layout decision, any
  necessary minimal layout change, then final local/live verification.
- This complex task has `design.md` and `implement.md`; implementation still
  requires explicit review and `task.py start`.
