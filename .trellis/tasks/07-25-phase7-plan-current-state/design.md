# PLAN_web Current-State Design

## Target Information Architecture

```text
1. Product intent and current status
2. Non-negotiable product/technical/privacy constraints
3. Six-widget information architecture and ownership
4. Data contract and source projection rules
5. Frontend layout, scaling, text, and failure behavior
6. Publisher, scheduler, server, auth, certificate, and weather topology
7. Verification and operational commands
8. Current limitations and next work
9. Archive index
```

Exact numbering may follow the existing plan, but each fact has one canonical
location.

## Retention Matrix

| Content | Action |
| --- | --- |
| Current architecture/constraints/contracts | Keep and deduplicate |
| Current Phase 7 outcome | Keep once |
| Archived implementation narrative | Replace with task link and one-line result |
| Dated live snapshot/test count/cert expiry | Remove from durable plan |
| Explicit residual risk or waiver | Keep concise with evidence link |
| Superseded behavior | Remove from current prose; preserve archive link |
| Validation/operator command still used | Keep in owning section |

## Consistency Checks

Search for known drift anchors before and after editing: `no ellipsis`, Linear
owning Focus, fixed certificate dates, old unittest counts, `implementation in
progress`, and completed task paths under the active directory.

All remaining phase/task paths must exist. Current source ownership must agree
with code specs and `AGENTS.md`.

## Editing Boundary

Only `PLAN_web.md` and this task's evidence/artifacts may change. If review
finds an implementation/doc error elsewhere, create or reopen the owning child
instead of silently fixing it here.
