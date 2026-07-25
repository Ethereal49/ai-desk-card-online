# Phase 7 Handoff

## State

- Branch: `agent/phase7-planning-handoff`
- Base: `main`
- Parent: `07-25-phase7-reliability-operator-ergonomics`
- All tasks are intentionally `planning`; no Phase 7 implementation has begun.
- The user authorized all four deliverables and requested implementation in a
  new Codex session.

## Start Here

1. Read `AGENTS.md`, `PLAN_web.md`, this file, and the parent artifacts.
2. Run `python3 ./.trellis/scripts/get_context.py` and confirm the worktree and
   GitHub branch are current.
3. Read the quota child artifacts, then run:

```bash
python3 ./.trellis/scripts/task.py start 07-25-phase7-codex-quota-freshness
```

4. Complete and archive children sequentially in the parent order. Do not run
   the final plan-cleanup child before quota, Focus CLI, and certificate docs
   have durable outcomes.

## Current Live Facts At Handoff

- `2026-07-25` source check: Linear, Apple Calendar, and Codex metadata `ok`;
  Codex quota `stale`.
- Latest scheduled refresh: `publish=updated`, exit `2` only because quota is
  stale; status file mode `0600`, interval `300s`.
- Live weather is fresh and its timer/service are healthy.
- The live IP certificate renewed on `2026-07-25`; SAN is the server IP and the
  operative renewal unit is `snap.certbot.renew.timer`.

These are handoff observations, not permanent constants. Re-verify drift-prone
runtime facts in the owning child before claiming completion.
