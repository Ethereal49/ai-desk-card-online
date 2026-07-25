# Compress PLAN_web To Current State

## Goal

Turn `PLAN_web.md` back into a compact, internally consistent current product
and architecture source of truth, while preserving durable constraints,
evidence boundaries, and links to archived Trellis detail.

## Background

- `PLAN_web.md` currently mixes current architecture with long Phase 3-6
  checkpoints, obsolete dated certificate facts, superseded no-ellipsis text,
  repeated test counts, and completed next-step lists.
- Detailed historical evidence already lives under
  `.trellis/tasks/archive/2026-07/`; duplicating it in the plan creates drift.
- The plan freshness hook makes `PLAN_web.md` mandatory, so stale prose directly
  harms future development decisions rather than being harmless history.
- This child runs after the other Phase 7 implementation/docs children so it
  can represent their final outcomes once.

## Requirements

- Do not begin until quota freshness, Focus CLI, and certificate documentation
  children are completed or have explicit durable no-go outcomes.
- Preserve only current, decision-relevant sections:
  - product intent and deployed architecture;
  - fixed constraints and privacy/security boundaries;
  - six-widget data/ownership contract;
  - current local publisher/scheduler and server runtime topology;
  - UI/layout/text behavior and validation commands;
  - current known limitations/residual risks;
  - active/next work and archive index.
- Move historical narrative to archive links rather than rewriting or deleting
  its evidence. Preserve every archive path needed to find Phase 3-7 decisions.
- Remove fixed certificate expiry dates, obsolete test counts, completed
  implementation checklists, repeated live snapshots, and superseded behavior
  presented as current.
- Resolve contradictions explicitly. The most recent verified behavior wins;
  older behavior is represented only through its archive link.
- Keep commands only when they are current operator/validation contracts. Do
  not embed secrets, private paths beyond already documented safe defaults, or
  transient live values.
- Do not change code, runtime configuration, schemas, or product behavior.

## Acceptance Criteria

- [ ] `PLAN_web.md` has one current-status narrative and one next-work section;
  completed phase detail is represented by concise archive links.
- [ ] No current statement claims no ellipsis, a fixed Linear-owned Focus, an
  obsolete certificate expiry, old test count, incomplete Phase 6, or another
  behavior contradicted by the implemented repository/runtime.
- [ ] Current static architecture, six widget/slot mapping, source ownership,
  privacy boundary, Focus allowlist/CLI, quota outcome, automatic scaling,
  two-line clamp, scheduler, weather ownership, Caddy Basic Auth, and locked
  publish are all retained.
- [ ] Unresolved risks and explicit historical waivers remain discoverable and
  are not converted into false passes.
- [ ] Every referenced active/archive task path exists and the Phase 7 task tree
  is represented accurately.
- [ ] `ensure_plan_updated.py`, plan guard tests, Trellis validation, link/path
  checks, and `git diff --check` pass.
- [ ] A before/after review confirms no executable implementation or deployment
  file changed in this child.

## Out Of Scope

- Rewriting archived task artifacts or git history.
- Changing AGENTS/spec requirements, runtime code, UI, server configuration, or
  deployment state.
- Adding new product features under the guise of documentation cleanup.
