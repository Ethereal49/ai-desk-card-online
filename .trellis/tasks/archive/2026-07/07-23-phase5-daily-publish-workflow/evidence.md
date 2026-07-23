# Phase 5 Evidence

## Local Implementation Checkpoint

Recorded on 2026-07-23.

- `python3 -m unittest discover -s scripts -p 'test_*.py'`: 77 passed.
- All new Python modules compile; `node --check web/app.js` passed.
- LaunchAgent example passed `plutil -lint`.
- `web/widgets.example.json` passed the shared full-document validator.
- Fixture tests cover Linear hierarchy/ranking/auth/pagination/privacy, Calendar
  allowlist/window/cancellation/permission/privacy, Codex state precedence and
  schema drift, shared last-known-good/privacy validation, remote weather
  preservation/backup/mode/no-change behavior, local orchestration redaction,
  and bounded scheduled status output.

## Browser Checkpoint

- At `758x1024`, example data rendered all five todo rows and two forecast rows.
- Page dimensions were exactly `758x1024`; all six widget scroll dimensions
  matched their client dimensions.
- At `740x951`, the fixed card rendered as `701x947` with a 4px lower inset;
  page scroll dimensions were `740x951`; all widgets had zero internal overflow.
- At `467x600`, the card rendered as approximately `441x596`; page scroll
  dimensions were `467x600`; all widgets had zero internal overflow.
- Normal URLs retained `source: widgets.json`; screenshots are generated under
  `output/playwright/` and are not committed.
- A 288-character unbroken token plus long Chinese title fixture produced zero
  page/widget overflow and no `...`; primary widgets hid lower-priority headers
  and metrics before fitting the complete title.
- A five-row long-title todo fixture retained exactly the highest-priority two
  complete rows, removed only the trailing rows, reported `2/8`, and had zero
  widget overflow or ellipsis.

## Real Source Checkpoint

- Linear read-only API: `ok`; projected five todo rows without logging titles.
- Codex metadata: `ok`; projected only state/count/title/model/timing metadata.
- Codex quota: real weekly value found, but approximately 15 hours old and
  therefore correctly marked `stale`.
- Apple Calendar: the explicit two-calendar allowlist is configured locally,
  EventKit Full Access was granted to the Codex app identity through a
  temporary permission probe, and the bounded preflight now returns
  `apple-calendar=ok`. The accepted local window currently contains `0/0`
  events; no event text is recorded here.

## Manual Cutover Checkpoint

- Redacted `--preview` reported `linear=ok`, `apple-calendar=ok`,
  `codex-metadata=ok`, and `codex-quota=stale`; it listed only changed widget
  types and performed no write.
- One real `--publish` returned `publish=updated` with partial exit `2` solely
  for the stale quota sample. Remote validation passed: all six widget types,
  mode `0644`, one changed-only backup, five todo rows, and the shared strict
  contract. The pre/post weather widget hash matched exactly.
- The Codex in-app Browser could not open the IP HTTPS URL (`ERR_BLOCKED_BY_CLIENT`);
  this is not counted as an authenticated live Browser pass. The shell-level
  unauthenticated transport checks remain `301/401`; the password-gated HTTPS
  check and physical-device confirmation are still required.

## Live Infrastructure Checkpoint

- Backed up and installed the Phase 5 `index.html`, `styles.css`, `app.js`, and
  `favicon.svg`; local and live SHA-256 hashes matched and modes are `0644`.
- Backed up and installed the weather service with the shared
  `/run/lock/ai-desk-card-widgets.lock`; `daemon-reload` and a manual oneshot run
  completed with `Result=success`, the timer remained active, weather remained
  fresh, and live JSON remained mode `0644`.
- Public transport remained healthy after UI deployment: HTTP returned `301`
  and unauthenticated HTTPS returned `401`.
- The live certificate SAN contains `IP Address:112.74.73.134` and is valid from
  `2026-07-21T11:57:27Z` through `2026-07-28T03:57:26Z`.
- The portable remote installer ran under the server's Python 3.8 against a
  temporary copy of live JSON: it preserved weather, created one backup,
  installed mode `0644`, and reported `publish=updated`.

## Code-Spec Checkpoint

- Added the executable backend real-data publish contract covering adapter
  inputs, public projection, source health, exit codes, local/remote locks,
  weather ownership, backup/install/rollback, scheduler bounds, and required
  tests.
- Updated backend structure and frontend quality/component specs for the new
  source/orchestrator files, five-row todo contract, complete text wrapping,
  geometry assertions, and whole-row `selected/total` overflow behavior.
- This checkpoint does not satisfy the remaining authenticated HTTPS, physical
  device, or installed LaunchAgent gates.

## Follow-Up Read-Only Checkpoint

- Local full-suite rerun remained green: `77 passed`; task validation,
  `ensure_plan_updated.py`, syntax checks, contracts, and `git diff --check`
  also passed.
- Live read-only checks remained healthy: HTTP `301`, unauthenticated HTTPS
  `401`, Caddy and weather timer `active`, live JSON mode `0644`, all six widget
  types present, and no widget currently marked stale. The certificate still
  contains SAN `IP Address:112.74.73.134` and is valid through
  `2026-07-28T03:57:26Z`.
- A corrected repository privacy scan found no credential/private-key patterns;
  the only two password assignments are documented placeholders in
  `deploy/README.md` and `PLAN_web.md`.
- No Basic Auth password is present in the process environment, no Codex app
  terminal session is attached, and the LaunchAgent plist/job is not installed
  or loaded. These are explicit pending gates, not passes.

## Remaining Gates

- Calendar allowlist, macOS Calendar Full Access, preview, and the first real
  locked publication are complete.
- Authenticated HTTPS and runtime allowlist checks are complete. The Codex
  in-app Browser remains blocked by client policy, so the physical device is
  the final visual authority for this static page.
- The user reports readable text; obtain explicit bottom-border visibility and
  no-overlap/no-ellipsis confirmation.
- Install LaunchAgent only after manual cutover; verify two consecutive runs and
  the physical device.

## Authenticated Gate Attempt

- User-run `deploy/scripts/verify_ip_https.sh` reached authenticated `200` for
  `/` and `/widgets.json`, and authenticated `404` for `/README.md`.
- The next authenticated request, `/widgets.example.json`, timed out after 15
  seconds, so the script stopped and the authenticated HTTPS gate is **not** a
  pass. A credential-free loopback check on `myecs` returns promptly, which is
  consistent with a transient public request timeout rather than a Caddy route
  failure.
- The user reports that device text is readable. Bottom-border visibility and
  the complete no-overlap/no-ellipsis checklist still need explicit confirmation.
- After this attempt, the verifier was hardened with bounded connection retries;
  this change has passed shell syntax validation and does not weaken status
  assertions. The authenticated gate must be rerun against the updated script.

## Authenticated Gate Pass

- The user reran the updated `deploy/scripts/verify_ip_https.sh` through the
  `read -s` environment boundary. HTTP redirected with `301`; every unauthenticated
  runtime and non-runtime probe returned `401`.
- Authenticated `/` and `/widgets.json` returned `200`; authenticated
  `/README.md`, `/widgets.example.json`, `/../PLAN_web.md`, and
  `/%2e%2e/PLAN_web.md` returned `404`.
- Header, TLS verification, and IP SAN checks completed, and the script printed
  `IP HTTPS Basic Auth gate passed for https://112.74.73.134`.
- No password value was sent to or persisted by the repository workflow.

## LaunchAgent Checkpoint

- Installed `com.ethereal.ai-desk-card-refresh` as a mode-`0600` user
  LaunchAgent from the checked-in template. The loaded plist has
  `StartInterval=300`, `RunAtLoad=true`, and contains no credential/token/key.
- The bootstrap/kickstart run wrote status at `2026-07-23T18:17:24+08:00`.
  Two subsequent natural status-file updates were observed at
  `18:22:32+08:00` and `18:27:39+08:00`, 307 seconds apart. This satisfies the
  two consecutive five-minute run gate without substituting manual `kickstart`
  for either scheduled tick.
- Each status reported Linear, Apple Calendar, and Codex metadata `ok`, Codex
  quota `stale`, and `publish=updated`. LaunchAgent `last exit code=2` therefore
  represents the designed partial-freshness result rather than scheduler or
  publish failure.
- `latest.log` is mode `0600`, three lines, bounded to 135 bytes in the latest
  run, and passed a forbidden-field/privacy scan. No refresh process remained
  after completion, and the local lock tests cover overlapping invocation.
- Post-run live JSON remains mode `0644`, contains all six widget types and five
  todo rows. The publish backup created at `18:27:38` retained the then-current
  weather; the server weather service subsequently logged a fresh update at
  `18:27:40`, demonstrating that the shared-lock ownership paths serialized
  without regressing the server-owned widget.
- A later scheduled tick reported `linear=stale` and still completed the
  last-known-good publish. An immediate source-only recheck recovered to
  `linear=ok`, with Calendar and Codex metadata also `ok`; only the known old
  quota sample remained stale. This is recorded as successful source-failure
  isolation, not as an all-sources-fresh run.
- A subsequent natural tick at `2026-07-23T18:38:07+08:00` also reported
  `linear=ok`, Calendar/Codex metadata `ok`, quota `stale`, and
  `publish=updated`, confirming unattended recovery after the transient source
  failure. No refresh process remained afterward.
- The current `pmset` log tail contains no post-install system sleep/wake event
  that can be correlated with a later tick. Long-lived `caffeinate` and
  `UURemote` assertions also prevent treating display sleep as system sleep.
- On 2026-07-23 the user explicitly waived the direct system sleep/wake
  observation gate. This waiver does not alter the implementation contract:
  LaunchAgent scheduling semantics, bounded execution, and later natural-tick
  recovery remain verified above.

## Acceptance Audit

- The user explicitly confirms the physical device bottom border and readable
  no-overlap/no-ellipsis state. The live-device criterion is now checked.
- All `24/24` PRD acceptance criteria are checked in `prd.md`. The final
  LaunchAgent criterion is satisfied by implementation, cadence, privacy,
  non-overlap, and later natural-tick evidence; its direct system sleep/wake
  observation sub-gate is explicitly waived by the user.

## Final Closeout Checkpoint

- Final full-suite rerun: `78 passed`. The added regression proves that a
  failure reported after atomic replacement still restores the changed-only
  backup, closing the post-replace/directory-sync rollback gap.
- Python compile, JavaScript syntax, shell syntax, LaunchAgent plist lint,
  Trellis task validation, plan freshness, privacy scan, and
  `git diff --check` pass at closeout.
