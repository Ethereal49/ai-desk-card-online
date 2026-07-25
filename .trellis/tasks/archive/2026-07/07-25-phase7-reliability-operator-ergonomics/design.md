# Phase 7 Parent Design

## Responsibility Boundary

The parent is an integration and sequencing boundary, not an implementation
bucket. Each child owns one deliverable and its evidence. The parent owns the
shared invariants, the order in which children are executed, final regression
coverage, archive/journal closeout, and the GitHub PR narrative.

## Task Graph

```text
quota freshness (P1) -----------------------------+
                                                    |
Focus config CLI (P2) -----------------------------+--> integrated check
                                                    |         |
certificate docs (P2, read-only live evidence) ----+         v
                                              PLAN_web cleanup (last)
                                                        |
                                                        v
                                             parent closeout / PR ready
```

The first three children do not depend on each other's code, but they must not
run in parallel in one worktree because all turns synchronize `PLAN_web.md`.
The plan cleanup child explicitly depends on the other three being completed or
having durable evidence-backed outcomes.

## Shared Contracts

- Runtime remains static `web/` plus `widgets.json`.
- The existing public widget schema and privacy validator remain authoritative.
- Local configuration remains outside the repository and is never copied to
  the server.
- Source and deployment failures retain last-known-good state and remain
  visible through bounded health/exit codes.
- Live verification is read-only unless a child PRD explicitly requires the
  existing publisher to install a validated candidate.

## Branch And PR Strategy

- Handoff branch: `agent/phase7-planning-handoff`.
- PR base: `main`.
- The planning handoff opens as a draft PR. The next session continues the same
  branch sequentially, or creates child branches only after updating task
  metadata and documenting the integration strategy.
- Do not merge while any child or parent acceptance criterion is open.

## Integration Risks

- A quota fix can accidentally publish private account/session data. The public
  contract and redacted output tests remain mandatory.
- A Focus CLI can conflict with the legacy `update_focus.py` manual updater.
  The new command owns only the production config file; it must not write live
  `widgets.json` or silently invoke publish.
- Certificate documentation can become stale if it records a fixed expiry.
  Document the mechanism and verification commands, not a dated runtime value.
- Plan cleanup can delete important constraints. Preserve architecture,
  security boundaries, active behavior, archive paths, and unresolved risks
  before removing historical prose.

## Rollback

Each child must be independently revertible. If integrated checks regress,
revert only the owning child commit and keep the remaining completed child
evidence intact. The parent is not archived until the integrated branch is
green.
