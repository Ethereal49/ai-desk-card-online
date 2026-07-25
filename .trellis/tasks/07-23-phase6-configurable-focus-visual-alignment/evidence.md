# Phase 6 Evidence

## Planning And Local Contract

- User approved the two-line ellipsis policy, allowlisted Focus sources with
  `todo.first` default, centered primary regions with left-aligned lists, and
  autonomous Trellis execution except for complex/security decisions.
- `task.py validate 07-23-phase6-configurable-focus-visual-alignment` passed
  during planning and after implementation. `PLAN_web.md` was updated with the
  Phase 6 contract and current checkpoint.
- Focus configuration is absent on this Mac, so production behavior is the
  backward-compatible `todo.first` default. No user Focus file was created or
  copied into the repository/server.

## Implementation

- Added `scripts/focus_config.py` with bounded JSON loading, the five-source
  allowlist, optional overrides, empty/stale propagation, and pure projection.
- Linear now owns only `todo`; Focus is resolved after source/LKG and quota
  merge. The public six-widget JSON schema and server-owned weather remain
  unchanged.
- Added `deploy/focus.example.json`; it contains no user data.
- Added two-line presentation clamping for source/user prose while retaining
  complete escaped DOM text and accessible composite row labels.
- Replaced top-bar floats and fixed footer widths with grid alignment; detail
  headers share a top line, primary content is centered, list prose remains
  column-aligned, and AI metric cells are flat/equal.

## Local Quality

- `python3 -m unittest discover -s scripts -p 'test_*.py'`: **86 passed**.
- Python compile, `node --check web/app.js`, plist lint, shell syntax,
  widget-contract validation, `ensure_plan_updated.py`, Trellis validation, and
  `git diff --check`: passed.
- Focus tests cover missing/default config, each allowlisted source, overrides,
  empty/stale state, invalid shape/type/length/size/directory, and redacted
  publisher failure before source collection/baseline SSH.

## Browser Gate

The Codex built-in Browser used a public isolated long-text fixture, not live
user/source data. Screenshots are generated under `output/browser/phase6/` and
are ignored QA artifacts.

- `758x1024`: page `758x1024`; five todo rows; two forecast rows; all widget
  overflow flags false; detail header tops all `665`; AI count cells all
  `71x98`; footer bottom `1000`; long source nodes computed
  `-webkit-line-clamp: 2`, displayed two lines, and showed visible `...` in the
  screenshot.
- The short-text fixture at `758x1024` kept ordinary todo titles and Calendar
  end times fully visible without an ellipsis; the long fixture independently
  showed ellipsis only after the second visual line. The corresponding JSON and
  DOM text lengths remained unchanged.
- `740x951`: card `701x947` at x `18`; page `740x951`; five todo rows; no
  widget overflow; footer bottom `925`.
- `467x600`: card `441x596` at x `12`; page `467x600`; five todo rows; no
  widget overflow; every clamp node reported line clamp `2`; footer bottom
  `582`; bottom border visible in the screenshot.
- Long Chinese, English, and unbroken-token strings remained present in the DOM
  with their full lengths; only the visual boxes were clamped.
- The normal fixture also retained no page/widget overflow and five-row
  rendering. The local server was stopped after the gate.

## Real Source And Publish Gate

- `scripts/refresh_dashboard.py --source-check`: exit `2` with
  `linear=ok apple-calendar=ok codex-metadata=ok codex-quota=stale`; the stale
  quota is the known bounded old local sample.
- `--preview`: exit `2`, redacted health plus `changed=ai-status,focus,ai-tasks,calendar,todo`
  and `publish=preview`; no write occurred.
- One real `--publish`: exit `2` solely for stale quota; `publish=updated`.
  Live JSON remained mode `0644`, contained all six widget types, five todo
  rows, `focus_source=focus-config:todo.first`, and no stale widgets.
- Weather widget SHA-256 before and after publish matched:
  `aacf676cfd5f08a03b1b6f7024bbd1b9b6f8e8cd29c905372d6b42653da7c997`.
- Static `index.html`, `styles.css`, `app.js`, and `favicon.svg` were backed up
  and installed with mode `0644`; all four local/live SHA-256 values matched.
- Credential-free transport checks after deployment remained HTTP `301` and
  unauthenticated HTTPS `401`. The authenticated password gate was not rerun in
  this turn because the password was not available to the repository process;
  the prior Phase 5 authenticated gate remains historical evidence, not a new
  Phase 6 claim.

## Scheduler Gate

- The installed LaunchAgent naturally completed a post-deploy tick at
  `2026-07-23T23:41:48+08:00` with the same redacted source health and
  `publish=updated`.
- `StartInterval=300`, latest status mode `0600`, status size bounded, and no
  residual refresh process were observed.
- On `2026-07-25`, after being asked to check the deployed physical device for
  readable two-line ellipsis, normal Focus/module alignment, and a complete
  bottom border, the user replied `正常`. This is the direct physical evidence
  for AC9; it is not inferred from an earlier phase or browser simulation.

## Final Closeout Gate

- Final local gate rerun: `86 passed`; Python compile, JavaScript syntax,
  LaunchAgent plist lint, shell syntax, widget contract, privacy assertions,
  plan freshness, Trellis validation, and `git diff --check` all passed.
- The three temporary Browser fixture servers were stopped after validation;
  no local `http.server` process remains.
- Final credential-free live read-only check at `2026-07-24T00:18+08:00`:
  remote `widgets.json` and static bundle files are `0644`; all six widget
  types are present; todo count is `5`; Focus source is
  `focus-config:todo.first`; weather is fresh at
  `2026-07-23T23:58:59+08:00`; weather timer is enabled/active and the latest
  service result is `success`.
- Public transport remains HTTP `301` to HTTPS and unauthenticated HTTPS
  returns `401`. The live certificate is issued by Let's Encrypt, contains
  `IP Address:112.74.73.134`, and is valid through `2026-07-28T03:57:26Z`.
- The installed LaunchAgent has `StartInterval=300`, latest status mode
  `0600`, and a bounded status line ending in `publish=updated`; the exit code
  `2` is the known stale-quota partial result, not a publish failure.
- AC1-AC9 are evidenced above. The physical result is a direct user report;
  every other criterion is backed by the local, Browser, publish, scheduler,
  or live read-only evidence recorded in this document.
