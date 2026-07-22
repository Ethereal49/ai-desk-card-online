# Implementation Plan: Phase 4 Device Stability

## 1. Planning And Preflight

- [x] Review the approved `prd.md`, this design, and the current `PLAN_web.md`.
- [x] Load `trellis-before-dev` and the relevant frontend/backend/deployment
      specs before any execution action.
- [x] Confirm the working tree, active task, fixed URL, and current live bundle
      are unchanged since Phase 3.
- [x] Prepare a timestamped evidence note under this task directory; never
      store the Basic Auth password or other secrets in it.

## 2. Start The 24-Hour Run

- [x] Re-run the renewed certificate/SAN/date check and open the fixed URL on
      the physical device with the existing viewport diagnostic if needed.
- [x] Record the preflight load: authentication, six widgets, quota state,
      `updated_at`, viewport dimensions, lower border, no-scroll, readability,
      and ghosting.
- [x] Restart only the device browser and record the recovery result.
- [x] Reboot the physical device and record the recovery result. The first
      stable page after this reboot is `T0` for the 24-hour clock; record the
      same data contract again.

## 3. Timed Observation

- [x] The dedicated `T+15m` physical response was not captured. Record the
      catch-up `T+65m` interval report explicitly; it covers more than three
      5-minute refresh opportunities but is not represented as a time-exact
      `T+15m` observation.
- [x] At approximately `T+65m`, verify from the live host that at least two
      consecutive 30-minute weather timer executions succeeded, compare their
      resulting `updated_at` changes on the device, and confirm
      quota/unrelated widgets remain present.
- [x] Keep the observation window open until at least `T+24h`; record the
      server-side final checkpoint. The recorded checkpoint was at `T+26h55m`.
- [ ] Obtain the matching final physical-device confirmation. Skipped on
      2026-07-23 at the user's direction; do not infer it from server evidence.
- [ ] If a checkpoint fails, stop the stability claim and preserve evidence;
      do not apply speculative fixes.

## 4. Closeout Gates

- [ ] Run the user-authenticated HTTPS gate without echoing credentials.
      Skipped on 2026-07-23 at the user's direction; the Phase 3 pass does not
      verify the certificate renewed during this observation window:

```bash
read -s "AI_DESK_CARD_AUTH_PASSWORD?Basic Auth password: "
export AI_DESK_CARD_AUTH_PASSWORD
AI_DESK_CARD_AUTH_USER=desk deploy/scripts/verify_ip_https.sh
unset AI_DESK_CARD_AUTH_PASSWORD
```

- [x] Run read-only Caddy, weather service/timer, and certificate checks on the
      live `myecs` host:

```bash
ssh myecs 'sudo systemctl status caddy --no-pager'
ssh myecs 'sudo systemctl status ai-desk-card-weather.timer --no-pager'
ssh myecs 'sudo systemctl status ai-desk-card-weather.service --no-pager'
ssh myecs 'sudo journalctl -u ai-desk-card-weather.service --since "24 hours ago" --no-pager'
openssl s_client -connect 112.74.73.134:443 -servername 112.74.73.134
```

- [x] Run repository gates:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 .codex/hooks/ensure_plan_updated.py
python3 -m json.tool .codex/hooks.json
git diff --check
```

- [x] Update `PLAN_web.md` with the dated 24-hour result, then run the plan
      freshness check again.
- [x] Close and archive the observation task at the user's direction with the
      incomplete acceptance criteria and residual risk stated explicitly. Do
      not describe the archive status as a full Phase 4 acceptance pass.

## Rollback Points

This task should not modify the runtime bundle. If an accidental deployment or
configuration change is made, stop and restore the last known-good Phase 3
backup before continuing. A product or infrastructure fix belongs in a separate
task after root-cause review.
