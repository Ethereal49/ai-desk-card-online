# Plan guard Trellis closeout exemption

## Goal

Make the `PLAN_web.md` freshness gate compatible with the mandatory Trellis
closeout order. Archiving a completed task and recording its journal must not
make an otherwise current product plan stale.

## Background

The Phase 8 final gate passed before Trellis closeout. `task.py archive` and
`add_session.py` then correctly generated their auto-commits, but
`.codex/hooks/ensure_plan_updated.py` reported the new archived `task.json` and
workspace journal/index as newer project changes. Rewriting the plan after
every journal would violate the Trellis commit order and create a non-terminating
plan/journal freshness loop.

## Requirements

- Ignore only Trellis-managed closeout records under:
  - `.trellis/tasks/archive/`;
  - `.trellis/workspace/`.
- Continue treating active task files under `.trellis/tasks/<active-task>/`,
  code-specs under `.trellis/spec/`, and ordinary project files as
  plan-relevant.
- Preserve all existing ignored-directory and ignored-file behavior.
- Add regression tests for both closeout exemptions and the active-task
  counterexample.
- Record the boundary in the owning backend quality guideline and update
  `PLAN_web.md`.
- Do not change dashboard runtime behavior, deployment behavior, GitHub
  settings, branches, or PR state.

## Acceptance Criteria

- [x] A journal or archived task written after `PLAN_web.md` does not appear in
  `stale_files`.
- [x] A newer active task artifact still appears in `stale_files`.
- [x] A newer ordinary project file still appears in `stale_files`.
- [ ] The full Python suite passes with zero skipped tests, and plan freshness,
  static syntax, Trellis validation, archive links, and `git diff --check`
  pass.
- [ ] After this task's own archive and journal auto-commits, the live plan
  hook prints `{}` without an extra product/work commit.
- [ ] The fix is committed, pushed to draft PR #2, its latest CI succeeds, the
  task is archived, the journal records only its work commit, and the final
  worktree is clean.

## Out Of Scope

- Ignoring all of `.trellis/`.
- Replacing modification-time freshness with a different plan model.
- Changing Trellis scripts or their required archive/journal commit order.
- Modifying product or live deployment behavior.

## Notes

- This is a lightweight workflow-contract repair with one hook, its direct
  tests, the owning guideline, and the product plan in scope.
