# Phase 7 Parent Implementation Plan

Status: planning handoff. The user authorized all four deliverables, but this
session intentionally does not start implementation.

## Ordered Execution

1. [x] Create the parent/child Trellis tree and converge all planning artifacts.
2. [ ] Start and complete `07-25-phase7-codex-quota-freshness`.
3. [ ] Start and complete `07-25-phase7-focus-config-cli`.
4. [ ] Start and complete `07-25-phase7-certificate-docs`.
5. [ ] Start and complete `07-25-phase7-plan-current-state` after steps 2-4.
6. [ ] Run the parent integration gate:
   - full Python tests and static/privacy contracts;
   - Python/JavaScript/plist/shell syntax checks;
   - plan freshness, Trellis validation, and `git diff --check`;
   - credential-free source/publish/runtime checks required by completed
     children, without exposing configured content.
7. [ ] Update shared specs only for executable contracts learned during child
   implementation.
8. [ ] Commit work in coherent child batches, update the draft PR evidence,
   archive completed children and parent, and record the Trellis journal.

## New-Session Entry Point

```bash
cd /Users/ethereal/Documents/Code/ai-desk-card-online
git switch agent/phase7-planning-handoff
git pull --ff-only
python3 ./.trellis/scripts/get_context.py
python3 ./.trellis/scripts/task.py start 07-25-phase7-codex-quota-freshness
```

Then load `trellis-before-dev`, read the quota child's artifacts and relevant
backend specs, and execute only that child until its evidence is durable.

## Parent Completion Gate

Do not start or archive the parent merely because the planning tree exists.
The parent is complete only after every child is completed or has an explicit
user-approved no-go, integrated checks pass, the PR accurately reports the
result, and the final plan contains no stale next-step claim.
