# Phase 7 Reliability And Operator Ergonomics

## Goal

Close the remaining operational quality gap and make routine Focus operation
safer without changing the static dashboard architecture: restore fresh Codex
quota data when an authoritative source exists or preserve an explicit no-go,
add a deterministic local Focus configuration CLI, correct certificate-renewal
documentation, and reduce `PLAN_web.md` to an accurate current-state source of
truth.

## Background

- Phase 6 is complete and archived; the branch baseline contains the verified
  static six-widget UI, real-data publisher, scheduler, weather ownership,
  Basic Auth boundary, and physical-device acceptance.
- A read-only check on `2026-07-25` found Linear, Apple Calendar, Codex
  metadata, weather, and publishing healthy. Codex quota alone remained stale,
  so the otherwise successful five-minute LaunchAgent run exited `2`.
- The live certificate renewed successfully on `2026-07-25`. The operative
  renewal unit is `snap.certbot.renew.timer`, while the deployment README still
  contains an obsolete fixed expiry date.
- Focus is configurable through a strict local JSON file, but there is no
  ergonomic command for creating or inspecting that file safely.
- `PLAN_web.md` still contains repeated historical checkpoints that belong in
  archived Trellis evidence rather than the current plan.

## Child Task Map

| Order | Child | Priority | Deliverable |
| --- | --- | --- | --- |
| 1 | `07-25-phase7-codex-quota-freshness` | P1 | Restore an authoritative fresh quota path or fail loudly if no such source exists. |
| 2 | `07-25-phase7-focus-config-cli` | P2 | Add a local atomic, redacted CLI for the existing Focus config contract. |
| 3 | `07-25-phase7-certificate-docs` | P2 | Correct renewal/runtime documentation using read-only live evidence. |
| 4 | `07-25-phase7-plan-current-state` | P2 | Compress the plan after the other children establish final current facts. |

## Requirements

- Keep every child independently testable and archiveable. The parent owns
  ordering, shared constraints, final integration review, and GitHub handoff;
  it has no direct product implementation.
- Execute children in the listed order. In particular, plan compression runs
  last so earlier children cannot reintroduce stale checkpoints.
- Preserve the static HTML/CSS/vanilla-JavaScript architecture, six-widget JSON
  contract, privacy allowlist, `758x1024` fit, server-owned weather, local
  source ownership, locked atomic publish, LaunchAgent cadence, and Caddy Basic
  Auth boundary.
- Do not solve quota freshness by increasing the stale threshold, fabricating
  values, screen scraping, or copying raw session/account records.
- Do not add a browser editor, backend API, arbitrary Focus field selector, or
  direct source-system write.
- During the original planning handoff, keep all tasks in `planning`; later
  implementation starts only after reading the artifacts and activating the
  owning child.
- Publish this planning tree and the complete local baseline to a GitHub branch
  with a draft PR targeting `main`.

## Acceptance Criteria

- [x] All four child tasks are linked to this parent and contain converged
  `prd.md`, `design.md`, and `implement.md` artifacts.
- [x] The quota child is completed with fresh authoritative quota evidence or
  an explicit evidence-backed no-go; stale data is never relabeled fresh.
- [x] The Focus CLI child is completed with atomic private config writes,
  redacted output, contract reuse, tests, and operator documentation.
- [x] The certificate documentation child is completed without changing live
  Caddy, Certbot, certificate, or server state.
- [x] The plan hygiene child runs last and leaves one coherent current-state
  plan with durable archive links and no stale runtime claims.
- [x] Every child passes its focused checks; the integrated branch passes the
  full Python/static/privacy/Trellis/plan gates and any required read-only live
  checks.
- [ ] Completed children and this parent are archived, the Trellis journal is
  recorded, and the draft PR is updated with implementation evidence before it
  is marked ready or merged.

## Out Of Scope

- New dashboard widgets or source integrations.
- UI redesign, firmware, daemon, database, backend service, or framework work.
- Replacing Caddy, Basic Auth, the server host, scheduler cadence, or weather
  provider.
- Merging the draft PR; it remains draft for review after implementation.
