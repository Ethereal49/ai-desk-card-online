# Design: Phase 4 Device Stability

## Scope And Boundary

Keep the deployed static architecture unchanged:

```text
weather timer / existing updater
        |
        v
web/widgets.json
        |
        v
authenticated Caddy static site
        |
        v
physical e-ink browser
```

This task collects operational evidence against the already-published bundle.
It does not add endpoints, logging services, browser automation, widgets,
backend code, or configuration changes. A failure may authorize a later fix only
after its root cause is identified and documented.

## Observation Protocol

The preflight load, browser restart, and full device reboot are recovery tests,
not part of the timed stability window. The clock starts at the first
successful stable physical-device load after the full reboot (`T0`). The run is
complete only after `T0 + 24 hours`; a late checkpoint is valid, an early
checkpoint is not. Record each checkpoint in a durable task evidence note with:

- local timestamp and elapsed time;
- fixed URL/query used and whether the page required authentication again;
- displayed `updated_at`, weather freshness/stale state, quota state, and six
  widget presence;
- viewport diagnostic, lower border, scrolling/clipping, readability, ghosting,
  and blank-screen result;
- action taken since the previous checkpoint and any failure symptom.

Required checkpoints are `T0`, approximately `T+15m`, `T+65m`, and `T+24h`.
The operator may add checks at any timer boundary. The preflight load, browser
restart, and device reboot must each be timestamped separately before `T0`.

## Recovery And Data Contracts

The recovery contract is identical for the initial load, browser restart, and
full device reboot: renewed IP certificate accepted, Basic Auth succeeds, the
page renders six widgets, the visual-viewport fit remains automatic, and the
lower border remains visible. A stale or unavailable quota value is acceptable
when its state is shown honestly and unrelated widgets remain intact.

Client refresh evidence uses the page's existing `refresh_seconds` contract
(currently 300 seconds). Weather evidence uses the existing 30-minute timer and
compares `updated_at` plus weather content before and after at least two timer
executions. A screenshot without timestamp/data comparison is insufficient.

## Failure And Rollback Boundary

If any gate fails, stop declaring stability, preserve the evidence, and capture
the relevant browser/server/service state. Do not change UI, Caddy, systemd,
updaters, or device settings during the run. Only after the failure has a
reproducible root cause may a separate fix task or implementation scope be
approved. There is no rollback action for an observation-only pass; the current
known-good deployment remains the baseline.

## Verification Layers

Physical-device evidence is authoritative for TLS acceptance, restart recovery,
viewport fit, e-ink readability, ghosting, and clipping. Live host checks are
authoritative for Caddy, the weather timer/service, certificate dates/SAN, and
authenticated runtime boundaries. Local tests and plan guards verify repository
integrity but cannot substitute for either live layer.
