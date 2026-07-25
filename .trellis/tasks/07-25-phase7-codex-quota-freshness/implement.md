# Codex Quota Freshness Implementation Plan

## Ordered Work

1. [x] Reproduce the current stale result and record bounded baseline evidence.
2. [x] Inventory recent authoritative quota structures without emitting raw
   records or sensitive values; decide adapter extension versus no-go.
3. [x] Confirm research does not change the reviewed source boundary.
4. [x] Confirm no new source shape exists that requires a failing fixture.
5. [x] Retain the existing parser/discovery adapter because current events
   contain no authoritative window; no executable change is justified.
6. [x] Verify last-known-good, old/missing/malformed, ordering, bounds, and
   redacted-output paths.
7. [x] Keep the unchanged executable contract in the backend spec; update
   operator docs and the Phase 7 `PLAN_web.md` checkpoint with the no-go.
8. [x] Run local gates:

```bash
PYTHONPATH=scripts python3 -m unittest test_update_codex_usage test_refresh_dashboard
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m compileall -q scripts deploy/scripts
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-25-phase7-codex-quota-freshness
git diff --check
```

9. [x] Run redacted source-check. Stop before preview/publish because no fresh
   authoritative quota exists; publishing cannot prove the no-go fresh.
10. [ ] Record live JSON/weather preservation and one natural LaunchAgent tick;
    for the fresh-source branch only. Complete no-go evidence, review specs,
    commit, archive, and journal.

## Stop Conditions

- Stop with an evidence-backed no-go rather than broadening privacy access if
  current authoritative quota is unavailable.
- Stop before publish if any output includes raw rollout content, paths,
  account identifiers, prompts, responses, tokens, or config text.
- Do not proceed from focused tests to live publish if the full contract suite
  fails.
