# Phase 7 Parent Implementation Plan

Status: implementation complete; parent integration and PR closeout are in
progress.

## Ordered Execution

1. [x] Create the parent/child Trellis tree and converge all planning artifacts.
2. [x] Start and complete `07-25-phase7-codex-quota-freshness`.
3. [x] Start and complete `07-25-phase7-focus-config-cli`.
4. [x] Start and complete `07-25-phase7-certificate-docs`.
5. [x] Start and complete `07-25-phase7-plan-current-state` after steps 2-4.
6. [x] Run the parent integration gate:
   - full Python tests and static/privacy contracts;
   - Python/JavaScript/plist/shell syntax checks;
   - plan freshness, Trellis validation, and `git diff --check`;
   - credential-free source/publish/runtime checks required by completed
     children, without exposing configured content.
7. [x] Update shared specs for executable contracts and current limitations
   learned during child implementation and parent integration.
8. [ ] Commit and push parent integration, update and read back the draft PR,
   record PR evidence, and create the final parent work commit.
9. [ ] Archive the parent after all work commits, then record the Trellis
   journal using only parent work commit hashes.

## Closeout Sequence

```bash
git push origin agent/phase7-planning-handoff
# Update and read back draft PR #1 without merging it.
python3 ./.trellis/scripts/task.py archive 07-25-phase7-reliability-operator-ergonomics
# Record the parent journal after archive.
```

## Parent Completion Gate

Do not start or archive the parent merely because the planning tree exists.
The parent is complete only after every child is completed or has the approved
evidence-backed no-go outcome, integrated checks pass, the PR accurately
reports the result, and the final plan contains no stale next-step claim.
