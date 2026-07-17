# Implementation Plan: Complete Phase 3 Real-Use Gates

## 1. Preflight

- [x] Load `trellis-before-dev` and the frontend/backend specs relevant to
      `web/`, JSON updaters, tests, and deployment.
- [x] Confirm the working tree and current task state before editing.
- [x] Recheck the live host, Caddy, weather timer, certificate, and current
      runtime file hashes; treat `PLAN_web.md` snapshots as historical only.
- [x] Confirm the HTTPS Basic Auth credentials are available without writing
      them to the repository or command output.
- [x] Run `scripts/update_codex_usage.py` against local Codex sessions and
      inspect the quota allowlist before any upload.
- [x] Verify current-event and stale/unavailable preservation paths with tests
      or controlled fixtures.

## 2. Add The Opt-In Viewport Readout

- [x] Add compatible query-flag detection to `web/app.js`.
- [x] Reuse the viewport calculation from `applyViewportScale` and show the
      dimensions in `source-label` only for `?viewport=1`.
- [x] Update the existing resize path so the readout stays current.
- [x] Add static-contract coverage for enabled and normal presentation paths.
- [x] Update `web/README.md` with the diagnostic URL contract.

Validation checkpoint:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Use the Codex built-in Browser at `758x1024` to verify the normal URL is
unchanged and `?viewport=1` reports `758x1024` without overflow.

## 3. Publish One Live Candidate And Collect Device Evidence

- [x] Create a timestamped backup of the current live runtime assets.
- [x] Publish the diagnostic, quota-aware `app.js`/`styles.css`, and cropped
      `widgets.json` together so live assets share one contract version.
- [x] Verify the uploaded quota contains only remaining percentages, reset
      timestamps, source, freshness, update time, and documented
      low-sensitivity error/attempt fields.
- [x] Run `deploy/scripts/verify_ip_https.sh`; the user-provided run passed all
      redirect, auth, non-runtime, header, and TLS SAN checks.
- [x] Ask the user to open the authenticated live URL with `?viewport=1` on the
      physical device and report dimensions, quota visibility, and the PRD
      readability checklist.
- [x] Record the dated evidence in `PLAN_web.md` before choosing a layout.

This is a hard user-interaction gate. Do not continue to layout implementation
without the physical-device observations.

## 4. Select And Implement One Layout Outcome

- [x] Choose exactly one outcome: keep three columns, compact mode, or detail
      rotation, using the recorded evidence.
- [x] For keep-three-columns, make no CSS change and record the no-change
      decision.
- [x] Change automatic fitting to use the visual viewport, layout-aware zoom
      when available, transform fallback, and a 4px small-viewport safe inset.
- [x] Verify a fresh simulated `740x951` load fits the lower border without
      manual zoom, then confirm on the device that the visual `467x600` area
      fits without manual zoom.
- [x] Compact/rotation branch is not applicable: evidence selected the current
      three-column layout, so no detail CSS or rotation change was made.
- [x] Update `scripts/test_web_static_contract.py` only for the chosen contract.
- [x] Re-run the full test suite and built-in Browser gate, including failed
      `widgets.json` behavior and widget-level overflow checks.
- [x] Back up live assets and publish the selected fit behavior. The authenticated
      HTTPS and live Browser gates remain pending credentials.
      HTTPS and authenticated live Browser gates.

Rollback point: restore the pre-layout backup if any live or physical-device
gate regresses.

## 5. Final Live Verification

- [x] If Step 4 changed layout assets, create a new timestamped backup and
      publish only the selected coherent runtime bundle.
- [x] Run the HTTPS gate and authenticated live Browser gate; verify both 5h and
      7d states render without exposing raw source data.
- [x] Recheck the physical device after the fit behavior change; the user
      confirmed first-load fit and a visible lower border without pinch zoom.

Rollback point: restore the pre-candidate runtime backup if authentication, static
file boundaries, rendering, or data privacy checks fail.

## 6. Final Quality Gate

- [x] Run:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 .codex/hooks/ensure_plan_updated.py
python3 -m json.tool .codex/hooks.json
git diff --check
```

- [x] Confirm the built-in Browser and physical device evidence satisfy every
      PRD acceptance criterion.
- [x] Update `PLAN_web.md` with the final layout decision, live verification
      snapshot, quota state, and remaining Phase 4 work.
- [x] Run `trellis-check` and review the final diff. Complete Trellis Phase 3
      commit/archive steps only after all gates pass.
