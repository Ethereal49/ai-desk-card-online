# Certificate Documentation Implementation Plan

## Ordered Work

1. [ ] Capture bounded read-only live evidence for certificate SAN/date, Snap
   timer/service, renewal lineage, deploy hook, Caddy references, and public
   transport status.
2. [ ] Compare evidence with `deploy/README.md`, Caddy examples, `PLAN_web.md`,
   and archived deployment evidence; classify each claim as durable or runtime.
3. [ ] Update only the necessary docs/examples. Remove fixed expiry prose and
   document `snap.certbot.renew.timer` plus the hook chain.
4. [ ] Run documentation/privacy checks:

```bash
bash -n deploy/scripts/verify_ip_https.sh deploy/scripts/verify_ip_only.sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-25-phase7-certificate-docs
git diff --check
```

5. [ ] Re-run only status/SAN/timer checks needed to prove the documented
   invariants; do not invoke renewal or service mutation.
6. [ ] Record exact evidence boundaries, commit, archive, and journal.

## Escalation

Open a separate fix task if the timer is disabled, the deploy hook is absent or
unsafe, Caddy points at different files, or status-only checks reveal a live
failure. A docs task must not hide or repair those conditions.
