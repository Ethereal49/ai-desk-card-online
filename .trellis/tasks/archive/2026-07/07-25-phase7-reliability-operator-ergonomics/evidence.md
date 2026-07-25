# Phase 7 Integration Evidence

## Child Outcomes

All four children completed and archived in the required order:

| Child | Durable outcome | Work commit | Archive commit |
| --- | --- | --- | --- |
| Quota freshness | Evidence-backed no-go; preserve stale LKG and partial exit `2` | `053a181` | `3c18112` |
| Focus config CLI | Atomic private redacted `get/set/reset` command | `44692ab` | `5c48e99` |
| Certificate docs | Snap/webroot/hook/Caddy mechanism and read-only evidence | `a9d33e5` | `e10adce` |
| PLAN current state | 552-to-292-line current-state plan with verified archive links | `d1da341` | `3849025` |

Each child has its own `evidence.md`, work commit, archive commit, and journal
entry. No child silently relabeled an open or waived gate as passed.

## Integrated Repository Gate

- Full Python suite: 98 passed.
- Python compile, JavaScript syntax, deployment shell syntax, LaunchAgent plist
  lint, tracked JSON parse, and repository credential/private-key scan passed.
- Parent Trellis validation and the four-child completed/archive tree check
  passed.
- Final plan freshness, stale-claim/path/shape/scope checks, and
  `git diff --check` passed again after the parent artifact and spec writes.
  Every plan archive path resolves except the intentionally transient parent
  path, which is verified again after archive.

## Redacted Source And Preview Gate

`scripts/refresh_dashboard.py --source-check` reported:

```text
linear=ok apple-calendar=ok codex-metadata=ok codex-quota=stale
```

`scripts/refresh_dashboard.py --preview` reported the same source health,
listed only the five changed owned widget types, and ended with
`publish=preview`. Both returned expected partial exit `2` solely because of
the accepted quota no-go. No title, configured Focus text, source record,
credential, or raw JSON was printed.

Neither command published. No server runtime file, local production Focus
config, scheduler, or live service state was changed.

## Read-Only Live Gate

Checked at `2026-07-25T17:03:50Z`:

- HTTP `/`: `301`;
- nonexistent HTTP ACME path: `404`;
- unauthenticated HTTPS `/`: `401`;
- certificate issuer: Let's Encrypt `YE2`;
- SAN: `IP Address:112.74.73.134`;
- observed validity: `Jul 25 01:21:47 2026 GMT` through
  `Jul 31 17:21:46 2026 GMT`;
- Caddy, weather timer, and `snap.certbot.renew.timer`: active;
- latest Snap renewal service: `Result=success`, `ExecMainStatus=0`.

The dates and service state are timestamped evidence only, not durable plan
claims. No authenticated password gate, renewal, reload, or live mutation was
performed during this parent check.

## Preserved Boundaries

- Quota stays explicitly stale until a stable authoritative source exists.
- The browser `refresh_seconds` scheduling mismatch, one-tick
  `weather.current` Focus lag, line-clamp fallback, device diagnostic limit,
  Phase 4 incomplete closeout, Phase 5 sleep/wake waiver, and authenticated
  in-app Browser limitation remain visible in `PLAN_web.md`.
- No new product feature or live mutation was added under parent integration.

## Spec Convergence

Parent integration corrected two current-state code-spec gaps without changing
runtime behavior:

- frontend lifecycle guidance now distinguishes the intended configurable
  interval from the current fallback-300-second scheduling limitation;
- the real-data publish contract now records the bounded one-local-tick lag
  possible for `weather.current` Focus during a concurrent server weather
  update.

Both remain explicit future implementation gaps rather than newly blessed
behavior.

## PR Update Verification

Parent integration commit `e44f6f2` was pushed to
`agent/phase7-planning-handoff`. Draft PR #1 was rewritten from the obsolete
planning handoff to the four child outcomes, integrated checks, operator impact,
and remaining boundaries, then read back through GitHub:

- title: `Implement Phase 7 reliability and operator ergonomics`;
- base/head: `main` <- `agent/phase7-planning-handoff`;
- integration head OID at PR read-back, before evidence/bookkeeping commits:
  `e44f6f2a0eb21b65a912df0798f72d4c2812939a`;
- state: open, draft, merge state clean.

The PR was not marked ready and was not merged. Parent archive and journal occur
only after the final parent work commit.
