# Codex Quota Freshness Implementation Plan

## Ordered Work

1. [ ] Reproduce the current stale result and record bounded baseline evidence.
2. [ ] Inventory recent authoritative quota structures without emitting raw
   records or sensitive values; decide adapter extension versus no-go.
3. [ ] Update `prd.md`/`design.md` if research changes the source boundary.
4. [ ] Add failing fixtures for the discovered structure and privacy risks.
5. [ ] Implement the smallest parser/discovery adapter that normalizes into the
   existing quota contract; do not change unrelated Codex metadata behavior.
6. [ ] Verify last-known-good, old/missing/malformed, ordering, bounds, and
   redacted-output paths.
7. [ ] Update `.trellis/spec/backend/real-data-publish-contract.md`, operator
   docs, and the Phase 7 `PLAN_web.md` checkpoint if the executable contract
   changed.
8. [ ] Run local gates:

```bash
python3 -m unittest scripts.test_update_codex_usage scripts.test_refresh_dashboard
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m compileall -q scripts deploy/scripts
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-25-phase7-codex-quota-freshness
git diff --check
```

9. [ ] Run redacted source-check/preview, then publish through the existing
   locked path only after local checks pass.
10. [ ] Record live JSON/weather preservation and one natural LaunchAgent tick;
    complete evidence, review specs, commit, archive, and journal.

## Stop Conditions

- Stop with an evidence-backed no-go rather than broadening privacy access if
  current authoritative quota is unavailable.
- Stop before publish if any output includes raw rollout content, paths,
  account identifiers, prompts, responses, tokens, or config text.
- Do not proceed from focused tests to live publish if the full contract suite
  fails.
