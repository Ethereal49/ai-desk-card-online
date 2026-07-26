# Plan Guard Closeout Evidence

## Root Cause

Trellis requires the final order:

```text
work commit -> task archive auto-commit -> journal auto-commit
```

The plan guard previously scanned every file under `.trellis/`. The archive
and journal auto-commits therefore made a current plan appear stale after the
only valid place to update it, creating a non-terminating closeout loop.

## Boundary

- Ignored:
  - `.trellis/tasks/archive/`;
  - `.trellis/workspace/`.
- Still plan-relevant:
  - active `.trellis/tasks/<task>/` artifacts;
  - `.trellis/spec/`;
  - ordinary project files.
- Existing ignored cache/artifact directories are unchanged.

## Red/Green Proof

- Before the hook change,
  `test_ignores_trellis_closeout_records` failed with both the archived
  `task.json` and journal in `stale_files`.
- The active-task counterexample already passed before the hook change.
- After the hook change, all eight direct plan-guard tests passed, including
  the active-task and code-spec counterexamples.

## Full Pre-Commit Gate

- `116` Python tests passed, zero skipped.
- Python compile, JavaScript syntax, and deployment shell syntax passed.
- Active Trellis task JSONL validation and `git diff --check` passed.
- The archived Phase 8 task is a legitimate branch addition relative to
  `origin/main`; archive integrity is checked by exact completed-task path and
  plan archive-link resolution, not by requiring the entire archive tree to be
  identical to `origin/main`.

## Final Closeout Gate

After this task's own archive and journal auto-commits, rerun the live plan
hook. Completion requires `{}` without any additional plan/work commit.
