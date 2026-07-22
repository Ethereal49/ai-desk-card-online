# Phase 4 Stability Evidence

## Preflight Baseline

Timestamp: `2026-07-19T23:47:35+08:00` to `2026-07-19T23:48:58+08:00`

This note contains operational metadata only. No Basic Auth password, token,
rollout content, or private widget payload is recorded.

- Certificate issuer: Let's Encrypt `YE1`
- Certificate validity: `2026-07-18 00:09:44 GMT` through `2026-07-24 16:09:43 GMT`
- Certificate SAN: `IP Address:112.74.73.134`
- HTTP `/`: `301`
- Unauthenticated HTTPS `/`: `401`
- Security headers observed: `Cache-Control: no-store`, CSP, HSTS,
  `Referrer-Policy`, `X-Content-Type-Options`
- `caddy`: `active`
- `ai-desk-card-weather.timer`: `active`
- Last weather service execution: `2026-07-19 23:21:28` to `23:21:30 CST`,
  exit status `0`, result `success`
- Last service log: `updated weather for Shenzhen (fresh)`
- Live runtime snapshot at `2026-07-19T23:21:30+08:00`:
  - `refresh_seconds=300`
  - weather `stale=false`, source `wttr.in`, error `null`
  - quota source `codex-rollout`, `stale=true`, weekly window present,
    5-hour window unavailable
- Local/live hashes match for `index.html`, `app.js`, and `styles.css`:
  - `index.html`: `591febcda83b64390616f68210110e9b2363a82651bca457aa51e6148ca6247c`
  - `app.js`: `44f5c58699103fa14d45ed48801158dabb4a3a88bf1659fe347db3c8a33c685a`
  - `styles.css`: `788b216b0e980ff6af3e6b879244b115e961ae5e82e28f3c8e530f20ec201008`

## Unverified Closeout Evidence

- User-authenticated HTTPS script against the latest certificate: not run.
- Final timed physical-device checkpoint at or after `T+24h`: not collected.
- Physical reload against the certificate renewed during the observation
  window: not collected.

## Physical-Device Preflight

Report recorded: `2026-07-21T14:01:39+08:00`

- The renewed certificate was accepted and the authenticated page rendered.
- The user reported all requested page checks normal except that the viewport
  diagnostic was not visible. This confirms six widgets, a visible lower
  border, and no reported scrolling, overlap, blank page, or unacceptable
  ghosting at preflight.
- The upper-right freshness label showed `stale 28m` at observation time.
  This is the top-level document age classification, not the weather widget's
  source-stale flag. The live host subsequently recorded `updated_at` and
  weather `updated_at` as `2026-07-21T13:59:08+08:00`, with
  `weather.stale=false`.
- Weather service executions at `12:58:36`, `13:28:51`, and `13:59:08` all
  succeeded with fresh data.
- The diagnostic should replace `source: widgets.json` in the bottom-left
  footer when `viewport=1` reaches `web/app.js`. The user confirmed that the
  bottom-left footer instead displays `source: widgets.json`.
- A manual page refresh changed the upper-right freshness label from
  `stale 28m` to `updated 8m ago`. At `2026-07-21T14:10:07+08:00`, the live
  document timestamp was `2026-07-21T13:59:08+08:00`, so the refreshed device
  state is consistent with the current live document. This proves manual reload
  recovery, not yet the scheduled 5-minute client refresh.
- Caddy preserves the diagnostic query across HTTP to HTTPS:
  `Location: https://112.74.73.134/?viewport=1&v=role3`. The remaining question
  is whether the device browser is executing the current `app.js` after
  authentication.
- The user confirmed the authenticated address bar still contains
  `?viewport=1&v=role3`, while the footer remains `source: widgets.json`.
  This is consistent with an old cached script or a device-specific script
  execution difference; no runtime fix is authorized before the browser restart
  gate isolates it.

## Browser Restart Recovery

- The user closed and restarted only the device browser, reopened the
  authenticated page, and confirmed all production page checks remained normal:
  six widgets, automatic fit, visible lower border, and no reported scrolling,
  overlap, blank page, or unacceptable ghosting.
- The footer still displayed `source: widgets.json` despite the retained query.
  The live bundle contains the query-gated diagnostic and the server preserves
  the query, so this is recorded as a device-specific diagnostic limitation.
  It does not block the production recovery gate and does not justify a runtime
  code change during this observation-only task.
- The previously confirmed physical visual viewport remains `467x600`; current
  fit and lower-edge behavior match that baseline even though the opt-in readout
  is unavailable in this browser session.

## Full Device Reboot And T0

- The user completed a full device reboot and reported that the fixed
  production URL recovered normally after startup.
- Recovery includes the previously requested contract: authenticated page,
  six widgets, automatic fit, visible lower border, and no reported scrolling,
  overlap, blank page, or unacceptable ghosting.
- Conservative `T0`: `2026-07-21T15:01:39+08:00`, captured when the normal
  recovery report was received. The physical page recovered no later than this
  timestamp, so measuring 24 hours from it cannot shorten the observation.
- Live baseline at `T0`: document `updated_at=2026-07-21T14:59:22+08:00`,
  `weather.stale=false`, Caddy active, and weather timer active.
- Earliest valid final checkpoint: `2026-07-22T15:01:39+08:00`.

## T+65m Server Checkpoint

Timestamp: `2026-07-21T16:07:47+08:00` (`T+66m08s`)

- Caddy and `ai-desk-card-weather.timer` remained active.
- Weather service execution 1: `15:29:19` to `15:29:21`, result `Succeeded`,
  output `updated weather for Shenzhen (fresh)`.
- Weather service execution 2: `15:59:34` to `15:59:35`, result `Succeeded`,
  output `updated weather for Shenzhen (fresh)`.
- Live document and weather `updated_at`: `2026-07-21T15:59:35+08:00`.
- Live weather remained `stale=false`, source `wttr.in`, error `null`.
- Quota contract remained present with weekly stale data and no 5-hour window;
  this matches the accepted last-known-good state.
- Certificate still contained `IP Address:112.74.73.134` and remained within
  its validity interval.
- The separate `T+15m` physical response was not captured. A current
  physical-device report is required to prove that the page remained usable
  across the elapsed client-refresh and weather-update opportunities.

### T+65m Physical Confirmation

Report recorded: `2026-07-21T16:11:38+08:00`

- The user answered that all requested physical-device checks had no problem.
  This response covered the current freshness state, all six widgets, quota
  presence, and the absence since `T0` of blank page, scrolling, clipping,
  overlap, or unacceptable ghosting.
- The user did not provide the exact freshness string. The corresponding live
  document timestamp was `2026-07-21T15:59:35+08:00`, and the server evidence
  proves two distinct post-`T0` weather updates.
- The elapsed interval covers more than thirteen 5-minute client refresh
  opportunities. Combined with the normal current physical page and changed
  live timestamps, this satisfies the repeated-refresh intent. It is recorded
  transparently as a `T+65m` catch-up rather than a time-exact `T+15m` report.

## T+24h Server And Repository Closeout

Timestamp: `2026-07-22T17:56:54+08:00` to `2026-07-22T17:59:24+08:00`
(`T+26h55m`)

- Caddy remained active and enabled.
- `ai-desk-card-weather.timer` remained active and enabled.
- Since `T0`, the weather timer started 57 service executions: 52 published
  fresh data, 5 encountered upstream timeout/handshake errors and preserved
  stale last-known-good data, and 0 unit executions failed.
- Each stale fallback recovered to fresh on a later timer cycle. The final
  service execution at `17:34:49` to `17:34:51` exited `0` with result
  `success` and published fresh weather.
- Live document and weather `updated_at`: `2026-07-22T17:34:51+08:00`.
- Final weather state: `stale=false`, source `wttr.in`, error `null`.
- All six widget types remained present: weather, ai-status, focus, ai-tasks,
  calendar, and todo. The accepted weekly-stale / 5-hour-unavailable quota
  contract remained present.
- Runtime `index.html`, `app.js`, and `styles.css` hashes still matched the
  local known-good bundle.
- The certificate renewed again during the observation window. Current validity
  is `2026-07-21 11:57:27 GMT` through `2026-07-28 03:57:26 GMT`, with
  `IP Address:112.74.73.134` in SAN.
- HTTP `/` returned `301`; unauthenticated HTTPS `/` returned `401` with the
  required security headers.
- Repository gates passed: 43 Python tests, `.codex/hooks.json` parse,
  Trellis task validation, and `git diff --check`.
- The authenticated HTTPS `200/404` boundary remains pending because the Basic
  Auth password is not stored in the Codex environment.
- Final physical-device confirmation must reload the page so it exercises the
  certificate renewed during this observation window; server evidence cannot
  replace that device TLS check.

## User-Directed Closeout

Date: `2026-07-23`

The user directed the project to stop further Phase 4 checks and plan later
work. No additional physical-device, authenticated HTTPS, certificate, server,
or runtime check was performed after that instruction.

The accepted result is therefore partial:

- The preflight recovery gates, `T+65m` physical/server checkpoint, and
  `T+26h55m` server/repository observation remain valid evidence.
- The final physical-device state, device acceptance of the latest renewed
  certificate, and final authenticated HTTPS boundary remain unverified.
- No failure was observed, but absence of the final evidence is not converted
  into a pass.
