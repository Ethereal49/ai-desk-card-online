# Verify Phase 4 device stability

## Goal

Prove over a continuous 24-hour observation window that the deployed desk card
remains usable through renewed TLS, browser/device restarts, repeated refresh
cycles, and weather updates. Phase 4 is an operational evidence task, not a
feature-development task.

## Background

- Phase 3 is complete and archived. The physical e-ink device fits the visual
  viewport automatically, keeps the three-column layout, and renders the live
  quota-aware page without pinch zoom or a clipped lower border.
- Caddy and `ai-desk-card-weather.timer` are active.
- The page reloads `widgets.json` every 300 seconds; weather updates every 30
  minutes on the server.
- The IP certificate renewed on 2026-07-18 after the previous physical-device
  test. The current certificate is valid through 2026-07-24 and includes
  `IP Address:112.74.73.134`; post-renewal device compatibility is not yet
  proven.
- `PLAN_web.md` contained stale Phase 3 status and next-step text; planning has
  corrected it so Phase 4 now owns the active gates.

## Requirements

- Before starting the timed run, reopen the fixed live URL after certificate
  renewal, restart only the device browser, and reboot the physical device;
  verify the same recovery contract after each action.
- Define `T0` as the first successful stable page after the full device reboot.
  Keep that page in service for at least 24 continuous hours. Check and record
  evidence at `T0`, approximately `T+15m`, `T+65m`, and `T+24h` (or later),
  including timestamps and before/after `updated_at` values.
- During the window, observe repeated 5-minute page refreshes and at least two
  successful 30-minute weather update cycles without white screens, scrolling,
  clipped borders, unacceptable ghosting, or loss of unrelated widget/quota
  data.
- Re-run the authenticated HTTPS gate and read-only service/certificate checks
  at the end of the 24-hour window.
- Correct `PLAN_web.md` so Phase 3 is complete, Phase 4 owns the active gates,
  and the archived Phase 3 task is no longer described as current.
- Do not change UI, updater, Caddy, systemd, or device configuration unless a
  gate fails and the root cause is established first.

## Acceptance Criteria

- [x] The renewed certificate is accepted by the physical device and the live
      page renders after authentication.
- [x] Closing/restarting the device browser recovers the page, authentication
      flow, automatic fit, and all six widgets.
- [x] A full device reboot recovers the same behavior from the fixed URL.
- [ ] The device remains in service for at least 24 continuous hours from the
      post-reboot `T0` to final closeout, with evidence at the defined
      checkpoints. The server-side window elapsed, but no final physical-device
      confirmation was collected.
- [x] At least three 5-minute client refresh intervals complete without blanking
      the page or losing last-known-good content, and the recorded
      `updated_at` values distinguish refresh evidence from a static screenshot.
- [x] At least two consecutive weather timer executions update live weather,
      keep `stale=false`, and preserve quota and unrelated widgets.
- [ ] No unacceptable scroll, clipping, overlap, flicker, or ghosting appears
      during the observation window. The device was normal through the
      `T+65m` report; the final physical state is unverified.
- [ ] The authenticated HTTPS script, Caddy/weather service checks, certificate
      SAN/date check, and repository quality gates pass at closeout. All parts
      except the authenticated HTTPS script were recorded at `T+26h55m`.
- [x] `PLAN_web.md` contains no stale active Phase 3 task or incomplete Phase 3
      gate list and records the dated Phase 4 evidence.

## Out Of Scope

- New widgets, visual redesign, compact/rotation layouts, backend APIs, or
  databases.
- Automating focus, todo, calendar, or AI-session collection.
- Treating fresh Codex quota availability as a Phase 4 stability requirement;
  stale/unavailable rendering remains valid if it preserves prior values.
- Fixing an unobserved failure speculatively.

## Technical Notes

- This is a complex task because it includes ordered physical-device actions,
  time-based observation, live infrastructure checks, and an explicit no-fix
  boundary. Add `design.md` and `implement.md` before `task.py start`.
- The observation window is fixed at 24 hours. The `T+65m` checkpoint is a
  minimum weather-cycle checkpoint inside that window, not an alternative
  completion window.

## Closeout Decision

On 2026-07-23 the user directed the project to stop checking Phase 4 and move
on to later work. The observation task is therefore closed with a documented
partial result, not a full acceptance pass:

- Passed evidence: certificate acceptance at preflight, browser restart,
  device reboot, repeated refresh opportunities through `T+65m`, two or more
  weather updates, and the 26h55m server/repository observation.
- Unverified evidence: the final physical-device state after 24 hours, a
  physical reload against the certificate renewed during the window, and the
  final authenticated HTTPS `200/404` boundary.
- Residual risk: a device-specific problem with the latest certificate or the
  authenticated route could exist despite the healthy server-side evidence.

Archiving this task records that the requested observation work ended. It must
not be cited as proof that every acceptance criterion passed.
