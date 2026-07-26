# Open-Source Readiness Implementation Plan

## Completion Contract

This plan is complete only when all PRD acceptance criteria are backed by
repeatable local output or GitHub read-back evidence. Passing tests alone is
not enough: the replacement branch, draft PR, approved repository setting,
exact branch cleanup, Trellis archive, journal, and clean final state are
separate gates.

## 1. Establish The Replacement Branch

- [x] Capture current status, task path, `origin/main`, old branch commit,
  ancestry, PR state, protection state, and recovery commands.
- [x] Fetch without tags and verify the planning task is the only uncommitted
  scope.
- [x] Switch to local `main`, fast-forward it to the fetched `origin/main`, and
  create `agent/open-source-readiness` from that commit.
- [x] Confirm the untracked planning task moved with the worktree and no old
  branch-only tracked changes were carried.
- [x] Update the task metadata to record the real base/implementation branch.

Rollback point: before any old branch deletion, recreate or switch back to
`agent/phase7-planning-handoff` from the recorded full commit ID.

## 2. Update Rules Before Structure

- [x] Patch the project-specific section of `AGENTS.md` first:
  - add root governance files, `.github/`, and `docs/assets/`;
  - rename the launchd example;
  - replace the absolute sibling source-repository path with an optional,
    relative historical-reference convention.
- [x] Keep the user-authored global working and sub-agent rules unchanged.
- [x] Add Phase 8/open-source task ownership to `PLAN_web.md` without claiming
  implementation completion.

Checkpoint: inspect the diff and confirm the new paths are governed before
creating them.

## 3. Make Configuration Generic And Fail Loud

- [x] Add failing tests for:
  - `AI_DESK_CARD_SSH_HOST` default resolution;
  - host-free source checks and local-baseline previews;
  - remote baseline/publish paths failing with exit `3` before SSH when host is
    absent;
  - verification scripts rejecting missing URL/IP configuration before
    invoking `curl`;
  - required open-source files and current-facing owner-specific anchor
    exclusions.
- [x] Update `scripts/refresh_dashboard.py` and its direct tests.
- [x] Update verification scripts, Caddy examples, launchd example, and
  operator docs.
- [x] Genericize current-facing `web/README.md`, `deploy/README.md`, and
  applicable `PLAN_web.md` content while leaving archive/history unchanged.
- [x] Run the focused tests and syntax checks before continuing.

Primary commands:

```bash
python3 -m unittest scripts.test_refresh_dashboard scripts.test_open_source_contract
bash -n deploy/scripts/*.sh
python3 -m plistlib deploy/launchd/*.plist.example
```

If `python3 -m plistlib` is unavailable as a CLI, parse the file through a
short read-only `python3 -c` command using stdlib `plistlib`.

## 4. Add The Open-Source Project Surface

- [x] Add the exact MIT license text with
  `Copyright (c) 2026 Ethereal49`.
- [x] Add root `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and
  `CODE_OF_CONDUCT.md`.
- [x] Add structured issue forms, chooser config, PR template, and the
  read-only CI workflow.
- [x] Resolve official action release tags to full commit SHAs immediately
  before writing CI and retain tag comments for reviewability.
- [x] Ensure all governance paths are executable and no placeholder or support
  promise is left unresolved.
- [x] Add/extend deterministic repository contract tests for required files,
  local links, workflow security anchors, plist validity, and current-facing
  genericization.

Checkpoint: render/inspect the root README text and run link/contract checks.

## 5. Generate And Inspect The Public Screenshot

- [x] Load the project-required built-in Browser skill.
- [x] Serve a temporary copy of `web/` with
  `widgets.example.json` exposed as `widgets.json`.
- [x] Open at exactly `758x1024` and verify:
  - `window.innerWidth === 758`;
  - `window.innerHeight === 1024`;
  - `scrollHeight <= innerHeight`;
  - all six supported widget types are represented;
  - no private live data is present.
- [x] Capture and visually inspect the screenshot.
- [x] Save the approved sanitized image to
  `docs/assets/dashboard-preview.png` and confirm the README renders it.
- [x] Stop the temporary server and remove only temporary artifacts.

## 6. Run The Full Local Quality Gate

- [x] Run all Python tests with skip counts reported.
- [x] Compile Python and check JavaScript and shell syntax.
- [x] Parse every tracked JSON and plist example.
- [x] Run repository privacy/current-facing anchor scans while explicitly
  excluding Git history and archived Trellis evidence.
- [x] Validate `PLAN_web.md` freshness and the active Trellis task.
- [x] Run `git diff --check` and unstaged scope review. Staged-diff review
  remains part of the work-commit gate.
- [x] Re-run README links and screenshot no-scroll/browser evidence.

Expected deterministic suite:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m compileall -q scripts .codex/hooks .trellis/scripts
node --check web/app.js
bash -n deploy/scripts/*.sh
python3 .codex/hooks/ensure_plan_updated.py
git diff --check
```

Any skipped or unavailable check is recorded as incomplete, not passed.

## 7. Update Specs And Create The Work Commit

- [x] Load `trellis-update-spec` and update every executable contract affected
  by host resolution, deployment examples, CI, and public-surface validation.
- [x] Update `PLAN_web.md` last with only verified current state and the
  remaining publish/cleanup gates.
- [x] Run the final full quality gate again.
- [ ] Stage only task-owned files and create the implementation commit.

Rollback point: the implementation remains isolated on
`agent/open-source-readiness`; revert the work commit or close the draft PR.

## 8. Push And Verify GitHub Surfaces

- [ ] Load the GitHub publish skill and push
  `agent/open-source-readiness`.
- [ ] Create a draft PR targeting `main` with scope, evidence, limitations,
  security-setting boundary, and branch-cleanup plan.
- [ ] Read back PR base/head/title/body/draft state and checks.
- [ ] Update the repository description to the verified product summary and
  read it back.
- [ ] Enable GitHub private vulnerability reporting and read it back.
- [ ] Snapshot all other security/protection settings and prove they did not
  change.
- [ ] Record successful GitHub read-back evidence in the Trellis task.

Do not merge the PR.

## 9. Delete Only The Approved Old Branch

- [ ] Re-fetch `origin/main` and the exact old remote branch.
- [ ] Re-prove old commit ancestry, no open PR, and unprotected state.
- [ ] Confirm current branch is `agent/open-source-readiness` and its draft PR
  exists.
- [ ] Record the exact recovery commands using
  `46700de3e3ea92491981ba9c29dffe0d58a84708`.
- [ ] Delete local `agent/phase7-planning-handoff` with safe
  `git branch -d`.
- [ ] Delete remote `agent/phase7-planning-handoff` by exact name.
- [ ] Read back local and remote inventories; preserve `main` and
  `agent/open-source-readiness`.

Stop before deletion if any proof changes.

## 10. Trellis Closeout

- [ ] Add final evidence, including commands, outcomes, skipped count, PR URL,
  setting read-back, branch inventories, and recovery commit.
- [ ] Update `PLAN_web.md` last for final freshness and commit any resulting
  evidence/plan changes as a second work commit.
- [ ] Re-run final local gates and confirm the draft PR includes the latest
  commit.
- [ ] Archive the Trellis task with `task.py archive`.
- [ ] Record the journal using only work commit hashes, then push archive and
  journal commits.
- [ ] Verify:
  - clean worktree;
  - task exists under `.trellis/tasks/archive/`;
  - all README/local/archive links resolve;
  - draft PR remains open and draft;
  - private vulnerability reporting remains enabled;
  - no unapproved security setting changed;
  - local/remote branch inventories match the approved final state.

Only after every item above passes may the `/goal` be marked complete.
