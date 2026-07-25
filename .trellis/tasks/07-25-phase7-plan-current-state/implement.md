# PLAN_web Current-State Implementation Plan

## Preconditions

- [ ] Quota freshness child has a completed or explicit no-go outcome.
- [ ] Focus config CLI child is completed.
- [ ] Certificate documentation child is completed.

## Ordered Work

1. [ ] Snapshot headings, current line count, archive links, commands, residual
   risks, and known drift anchors.
2. [ ] Draft the target current-state outline and map every retained fact before
   deleting historical prose.
3. [ ] Rewrite section by section, preserving architecture, contracts, security,
   verification, current Phase 7 outcomes, and archive paths.
4. [ ] Search for contradictions, stale dates/counts/statuses, duplicate facts,
   missing archive paths, and statements unsupported by code/spec/live evidence.
5. [ ] Confirm this child changed no executable or deployment file.
6. [ ] Run:

```bash
python3 -m unittest scripts.test_plan_guard
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-25-phase7-plan-current-state
git diff --check
```

7. [ ] Complete evidence with a retention/removal audit, commit, archive, and
   journal. Return to the parent for final integrated checks.

## Rollback

If important constraints or evidence links are lost, restore the pre-cleanup
plan and repeat from the retention matrix. Do not accept a shorter plan merely
because it is shorter; it must remain sufficient to implement safely.
