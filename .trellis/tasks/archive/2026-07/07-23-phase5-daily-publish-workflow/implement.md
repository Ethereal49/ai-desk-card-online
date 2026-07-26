# Phase 5 Implementation Plan

Status: implementation in progress. Planning review passed and `task.py start`
has been run.

## Success Gate

Phase 5 is complete only when real Linear, Apple Calendar, Codex task metadata,
and Codex quota data reach the authenticated live page through the deterministic
workflow; weather remains current; failures preserve last-known-good values;
and no raw/private source fields enter repository artifacts, live JSON, or
routine logs.

## Ordered Work

1. Converge the contracts.
   - Record the approved Codex state, text-fit, and continuous five-minute
     scheduling definitions.
   - Define exact widget allowlists, freshness fields, due tags, string bounds,
     exit codes, backup retention, and local/remote lock paths.
   - Reconcile the approved five-item todo contract with the current four-row
     browser render cap and update the task acceptance mapping.

2. Add shared deterministic contract helpers.
   - Implement full-document and owned-widget validation.
   - Implement source-result merge, last-known-good stale marking, privacy-key
     rejection, and changed-widget reporting.
   - Test malformed documents, duplicate types/slots, list limits, permissions,
     privacy bans, unchanged results, and isolated source failures.

3. Implement the Linear adapter.
   - Add environment-first and `.env.local` credential loading without logging
     values.
   - Add paginated read-only GraphQL access with timeout and auth-error typing.
   - Add pure parent exclusion, filtering, ordering, due-tag, todo, and focus
     projection helpers.
   - Test all ordering keys, parent/child behavior, no-date items, empty focus,
     pagination, unauthorized responses, redaction, and fixture-only projection.

4. Implement the Apple Calendar adapter.
   - Add strict JSON-array calendar allowlist parsing.
   - Add one bounded read-only `osascript` call that filters calendar names
     before output and emits only approved fields.
   - Add pure local-time overlap, all-day, cancellation, ordering, and cropping
     projection.
   - Test missing/empty/unmatched allowlists, permission denial, timeout,
     malformed output, late-night boundaries, ongoing/multi-day events, and
     privacy removal.

5. Implement the Codex task adapter.
   - Add schema-checked read-only queries for thread and goal metadata.
   - Add bounded lifecycle-tail parsing without message-content access.
   - Implement the approved state precedence, dormant cutoff, distinct daily
     completion counting, and most-recent unfinished selection.
   - Test running, terminal, aborted, blocked/limited, paused, completed,
     missing-goal, archived, stale, contradictory, and schema-drift fixtures.

6. Integrate Codex quota.
   - Reuse the existing quota parser through imported pure functions.
   - Merge quota independently from Codex task state and preserve it on failure.
   - Add integration tests proving no rollout text/path/token details escape.

7. Build the local orchestrator and preview.
   - Validate configuration before SSH and acquire a local run lock.
   - Run adapters independently with bounded timeouts.
   - Read the live baseline, compose and validate in memory, and report only
     source health plus changed widget types.
   - Test no-write preview, partial stale results, fatal config/auth failures,
     concurrent invocation, and redacted output.

8. Build locked remote publication.
   - Implement transfer to a unique remote temporary path.
   - Implement remote lock, re-read/merge, final validation, changed-only
     timestamped backup, bounded retention, atomic `0644` install, verification,
     rollback, and temporary-file cleanup.
   - Update the weather systemd unit to use the same lock.
   - Test against temporary local directories and stubbed SSH commands before
     any live server mutation.

9. Align todo count and long-text render contracts.
   - Remove blanket ellipsis/silent clipping from source content and add
     wrapping, long-token breaking, and bounded content-fit classes.
   - Implement the approved extreme-text policy without hover, page scroll,
     overlap, or font sizes below the physical readability floor.
   - Make the smallest renderer/style adjustment required to display five todo
     rows under the normal bounded-title contract.
   - Update example/fallback/static contract and rendered-geometry tests with
     long English, Chinese, and unbroken-token fixtures.
   - Re-run Browser checks at `758x1024`, `740x951`, and `467x600`; require no
     page scroll, internal overflow, clipping, or text overlap.

10. Perform real-source preflight and manual cutover.
    - Run the Calendar permission/allowlist preflight interactively.
    - Run source-only and preview modes and confirm redacted health output.
    - Run one manual publish, verify remote JSON/mode/weather preservation, then
      run authenticated HTTPS and live Browser/device checks.
    - Do not enable scheduling if any source is still smoke/manual or stale from
      configuration failure.

11. Add and enable the LaunchAgent after manual gates pass.
    - Install an example-backed user LaunchAgent without credentials.
    - Verify inspectability, five-minute invocation, non-overlap, sleep/wake
      recovery, bounded logs, and at least two consecutive successful runs.
    - Confirm the physical page reflects a subsequent scheduled data change.

12. Document and close.
    - Update `web/README.md`, `deploy/README.md`, `AGENTS.md` structure if new
      directories are added, and `PLAN_web.md` after each artifact group.
    - Run the PRD convergence pass, Trellis validation, full tests, diff checks,
      live gates, and privacy scan.
    - Record evidence, then finish/archive only after every accepted criterion
      is checked or explicitly waived by the user.

## Validation Commands

Expected commands will be finalized with the implementation, but the minimum
gate is:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-23-phase5-daily-publish-workflow
git diff --check
```

Source and publish CLIs must also support fixture/temporary-host validation so
tests never require live Linear, Calendar, Codex, or SSH access.

The live gate must include:

```bash
python3 scripts/refresh_dashboard.py --preview
python3 scripts/refresh_dashboard.py --publish
deploy/scripts/verify_ip_https.sh
```

The Basic Auth password is supplied only through the existing environment
boundary for the final HTTPS gate and is never written to files or logs.

## Risk And Rollback Points

- Linear and Calendar access are read-only; any attempted source write is a
  release blocker.
- Codex schema drift must produce stale state, not guessed counts.
- The first remote mutation requires a verified backup and shared weather lock.
- The LaunchAgent remains disabled until the manual publish is accepted.
- Rollback order: unload LaunchAgent, restore verified remote backup under lock,
  confirm weather timer and authenticated page, then diagnose locally.
- Do not use `web_update.py` during cutover because it regenerates the complete
  smoke document and can overwrite real/server-owned values.

## Before `task.py start`

- [x] User approves Codex status semantics.
- [x] User approves the extreme-text overflow priority.
- [x] User approves the scheduler boundary and cadence.
- [x] User reviews the final converged planning artifacts and authorizes
      implementation without routine confirmation prompts.
- [x] `prd.md` passes the lossless convergence pass.
- [x] `design.md` and this implementation plan match `PLAN_web.md`.
- [x] Trellis task validation, plan freshness, 43 existing tests, and diff checks
      pass at final planning review.
