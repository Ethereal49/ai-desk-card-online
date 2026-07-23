# Phase 6 Implementation Plan

Status: planning approved by the user; implementation starts only after the
artifacts pass the Trellis planning gate and `task.py start` is run.

## Success Gate

Phase 6 is complete only when configurable Focus projection, two-line visual
ellipsis, and the alignment system work together without changing the public
six-widget schema, privacy boundary, real-data refresh behavior, viewport fit,
or weather ownership, and every PRD criterion has durable evidence.

## Ordered Work

1. [x] Converge planning and executable contracts.
   - Update `PLAN_web.md` from the Phase 5 no-ellipsis/fixed-Linear decisions.
   - Validate the task artifacts and plan freshness before activation.

2. [x] Add pure Focus configuration and projection helpers.
   - Add strict bounded JSON loading, default behavior, source enum, field
     validation, redacted errors, and pure source-specific projection.
   - Reuse the shared widget contract for final Focus validation.
   - Add a public deployment example without user content.

3. [x] Integrate one Focus owner into the publisher.
   - Make Linear own only todo.
   - Load/validate Focus configuration before baseline SSH.
   - Resolve Focus after source/LKG and quota merge, propagate freshness, and
     include Focus in changed-widget reporting and owned publication.
   - Keep source-check/preview/scheduled output bounded and title-free.

4. [x] Replace the complete-text display policy with two-line presentation clamps.
   - Add one reusable clamp class and apply it to the approved content fields.
   - Preserve full escaped DOM text and accessible composite row labels.
   - Adjust row height/spacing so the normal five-todo fixture remains visible.
   - Retain compact and whole-row fallback only for residual widget overflow.

5. [x] Normalize alignment and visual rhythm.
   - Convert top bar and footer to explicit grids.
   - Align widget headers, primary regions, list columns, and divider positions.
   - Flatten and equalize AI task metric cells.
   - Keep list prose left-aligned and primary metrics centered.

6. [x] Update examples, documentation, and code specs.
   - Update `web/widgets.example.json`, `web/README.md`, `deploy/README.md`,
     frontend/backend specs, static contract tests, and `PLAN_web.md`.
   - Update `AGENTS.md` only if a tracked directory is added.

7. [x] Run focused and full local validation.
   - Unit-test config parsing, every source mode, overrides, empty/stale states,
     redacted failures, Linear ownership, and orchestrator ordering.
   - Run Python compile/tests, JavaScript syntax, plist/shell checks, widget
     contract, privacy scans, Trellis validation, plan freshness, and diff check.

8. [x] Run browser validation.
   - Use the built-in Browser at `758x1024`, `740x951`, and `467x600`.
   - Validate short text plus long Chinese, English, and unbroken tokens.
   - Record screenshot/geometry evidence for two-line ellipsis, five todo rows,
     header alignment, equal metrics, footer alignment, no overlap/overflow,
     automatic scaling, and complete bottom border.

9. [x] Deploy and observe one scheduler cycle.
   - Deploy only the required static/publisher files through the existing path.
   - Run redacted source-check/preview/publish and read-only server checks.
   - Verify live hashes/modes/weather preservation and one later LaunchAgent
     status update. Run authenticated HTTPS only if the password is available
     through the existing environment boundary.
   - Ask only for the physical-device visual result that cannot be observed
     locally; accept an explicit waiver without claiming a pass.

10. [ ] Close the task.
    - Complete the evidence checklist, run the final full-scope quality gate,
      update specs and plan, commit Phase 3.4 work, archive the task, and record
      the Trellis journal.

## Minimum Validation Commands

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m compileall -q scripts deploy/scripts
node --check web/app.js
plutil -lint deploy/launchd/com.ethereal.ai-desk-card-refresh.plist.example
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-23-phase6-configurable-focus-visual-alignment
git diff --check
```

## Risk And Rollback Points

- Configuration content can become live Focus text; never print it in errors,
  tests, evidence, or routine health output.
- Focus must have exactly one production owner. Do not retain a second Linear
  projection after the resolver is integrated.
- CSS truncation must not become producer-side string truncation; validate full
  JSON and DOM text independently from rendered geometry.
- Do not center list prose or shrink fonts below the current readable floor to
  force visual symmetry.
- Deploy without a custom Focus file first so missing configuration proves the
  backward-compatible default before any optional user customization.
- If live behavior regresses, remove the optional config, restore the prior
  bundle/publisher commit, and verify weather plus authenticated static access.

## Before `task.py start`

- [x] User approved the two-line ellipsis policy.
- [x] User approved configurable allowlisted Focus sources with `todo.first`
  as the default.
- [x] User approved centered primary content with scan-friendly left-aligned
  lists.
- [x] User authorized autonomous Trellis execution except for complex or
  security decisions.
- [x] PRD convergence, task validation, plan freshness, baseline tests, and
  diff checks pass.
