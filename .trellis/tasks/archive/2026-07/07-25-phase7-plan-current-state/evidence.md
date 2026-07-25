# PLAN_web Current-State Evidence

## Before Snapshot

- `PLAN_web.md`: 552 lines, 20 headings.
- Phase/status narrative appeared in three large regions: lines `1-117`,
  `298-418`, and `464-552`.
- Repeated history included dated live snapshots, fixed certificate validity,
  old test counts, completed checklists, commit hashes, and three copies of the
  Phase 7 execution state.
- Known stale claims included Focus owned by Linear, certificate docs still in
  progress, certificate expiry as current fact, pre-Phase-6 no-ellipsis
  behavior, and certificate work as the next task.

## Sources Reviewed

- `AGENTS.md`, both Trellis spec indexes, backend real-data/certificate
  contracts, and frontend component/lifecycle/state/quality/type contracts;
- current `web/index.html`, `web/styles.css`, `web/app.js`, source adapters,
  Focus resolver/CLI, refresh orchestrator, installer, scheduler, and deployment
  assets;
- archived Phase 3, 4, 5, 6, quota, Focus CLI, and certificate task artifacts;
- current Phase 7 parent and plan-cleanup artifacts.

Three independent read-only agent goals audited frontend behavior,
backend/deployment behavior, and task/archive path consistency. All three
reported no file changes; the only pre-rewrite dirty path was this task's
Trellis status transition.

## Retention Decisions

Keep once:

- static architecture and fixed product/technical/privacy boundaries;
- six slots, ownership, limits, and strict public JSON projection;
- Focus allowlist/CLI, quota no-go, last-known-good/error semantics;
- fixed layout, visual-viewport fit, two-line clamp, overflow fallback, and
  offline behavior;
- locked publisher, LaunchAgent, server weather, Caddy Basic Auth, and Snap
  certificate-renewal topology;
- current operator/validation commands, limitations, residual evidence
  boundaries, one next-work section, and archive links.

Remove from the durable plan:

- phase-by-phase implementation diaries and completed checklists;
- test counts, observation timestamps, runtime hashes, commit/journal lists,
  fixed quota samples, and certificate dates/versions;
- manual updater/`scp` flow presented as production;
- superseded no-ellipsis behavior and already completed Phase 7 sequencing.

## New Drift Found

- `web/app.js` schedules polling from fallback data before the asynchronous
  first load and does not reschedule after success. The current effective
  interval is 300 seconds; a non-300 runtime `refresh_seconds` changes the
  label but not the timer. This task records the mismatch and does not change
  code.
- `weather.current` Focus is composed from the pre-publish baseline. If weather
  changes before the shared remote lock, the installer preserves the newer
  weather while Focus can lag until the next local tick.
- Field allowlisting cannot determine whether permitted title text is
  semantically sensitive; source cropping and Caddy Basic Auth remain required.

## Path Audit Baseline

The current Phase 7 parent exists and resolves four unique children: three
completed archive tasks and this active final child. The seven Phase 3-7
archive paths retained by the rewritten plan all existed before editing.

The plan-cleanup and parent archive paths do not exist yet and are not claimed
as current links. Parent closeout must replace the active parent path with its
final archive path after both moves exist.

## After Snapshot

- `PLAN_web.md`: 292 lines, one H1, nine numbered current-state sections, and
  one explicit next-work statement.
- Historical status prose was replaced by seven existing Phase 3-7 archive
  links; every referenced active/archive task path resolves.
- Current Focus ownership, quota no-go, certificate renewal, two-line clamp,
  visual-viewport fit, publisher/scheduler topology, and residual boundaries
  agree with current source and code-specs.
- Stale-claim search found no fixed runtime date, old test count, incomplete
  certificate/Focus status, Linear-owned Focus, or superseded text behavior.
- Scope check confirmed that no executable, deployment, schema, AGENTS, or spec
  file changed in this child.

## Validation

- `python3 -m unittest scripts.test_plan_guard`: 5 passed;
- full Python suite: 98 passed;
- plan freshness guard: passed;
- Trellis task validation: passed;
- active/archive path resolver: passed;
- stale-claim and credential/private-key scans: passed;
- nine-section/one-next-work/line-count shape check: passed;
- `git diff --check`: passed.

## Spec Convergence

No `.trellis/spec/` edit belongs in this child. Current specs already state the
intended configurable refresh and projection contracts; changing them would
either duplicate the new plan or bless the newly exposed polling mismatch.
The mismatch is recorded as an implementation gap for a separate code task,
while this task preserves its explicit plan/artifact-only scope.
