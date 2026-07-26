# Connect real data and publish it safely

## Goal

Replace the current smoke/manual widget content with fresh data from the user's
actual systems, while preserving the static architecture and strict privacy
projection. Publishing convenience is part of this task, but it is downstream
of the real-data adapters: efficiently publishing simulated values does not
make the desk card useful.

## Background

- Weather is the only fully automatic real source: `myecs` fetches wttr.in
  every 30 minutes and isolates failures with last-known-good data.
- Codex quota has a real bounded local rollout parser, but refresh and live
  publication are manual; the checked-in value is stale.
- `ai-status` and `ai-tasks` contain explicit local smoke values. Their updater
  accepts caller-supplied values and does not observe real Codex task state.
- `focus`, `todo`, and `calendar` also contain manual smoke/demo content. Their
  updaters crop caller-supplied values but do not connect to a source system.
- The documented and producer-side todo limit is five, but `web/app.js`
  currently reports and renders at most four rows. Phase 5 must reconcile this
  existing contract defect before a five-item Linear result can be accepted.
- All local updaters edit only a local `widgets.json`. Live publication remains
  a separate manual `scp` plus `sudo install -m 0644` sequence.
- The runtime remains a static authenticated site. No backend API, database,
  browser-side editor, or framework is required unless the selected real source
  cannot be accessed safely from the local machine.
- Phase 4 was closed by user direction with three explicitly unverified gates.
  This task does not reopen those operational checks or claim they passed.

## Confirmed Product Direction

- Data authenticity takes priority over reducing the number of publish commands.
- Linear is the source of truth for both `todo` and `focus`.
- `focus` is derived automatically from the highest-priority issue in the final
  `todo` list. It has no separate Linear label, query, or manually maintained
  state.
- The Linear todo candidate pool is assigned to the current user across both
  `CODE` and `LIFE`, limited to `started` and `unstarted` status types. Backlog,
  completed, and canceled issues are excluded; issues without a due date remain
  eligible.
- Parent/container issues are excluded when another fetched issue references
  them as `parentId`. Child issues are not excluded and remain normal todo
  candidates.
- Final todo ordering is Linear priority first, then due date (earliest
  overdue, today, future, no date), then `started` before `unstarted`, then
  `updatedAt` descending, then a stable issue identifier.
- Linear authentication uses `LINEAR_API_KEY`. The current local credential is
  in repository-root `.env.local`, which is untracked, ignored by Git, and mode
  `0600`. The key value must never be printed or copied into tracked artifacts.
- Apple Calendar is the source of truth for the `calendar` widget.
- Apple Calendar access uses a required explicit calendar-name allowlist from
  local configuration. Missing or empty configuration fails loudly; the adapter
  never falls back to reading every visible calendar.
- Calendar displays events overlapping the local-time window from now through
  tomorrow at `23:59`. Ended and canceled events are excluded. Ongoing events
  sort before future events; all-day and timed events share the four-item cap.
- `ai-status` and `ai-tasks` cover all local Codex tasks across workspaces, not
  only this repository. `ai-status` selects the most recently active unfinished
  task; `ai-tasks` summarizes the global local-task state.
- The deterministic Codex state policy is approved: a running task needs an
  unmatched start plus activity within 30 minutes; explicit blocked/limited goal
  states map to blocked; active/paused goals and no-goal terminal tasks from the
  last 24 hours map to waiting; and daily completion counts distinct threads.
- Complete readable text takes priority over a fixed visible row count. After
  wrapping and content-based fitting reach the physical readability floor, omit
  only the lowest-ranked overflow row and report selected/total counts. For a
  single primary title, release lower-priority auxiliary blocks before clipping
  the title.
- After the manual source and publish gates pass, a user LaunchAgent runs every
  five minutes continuously while the macOS user session is available. There is
  no work-hours filter; sleep naturally pauses execution and a later tick resumes
  it.
- Each real source must have an explicit projection from source fields to the
  existing widget contract. Raw source objects must never be mirrored.
- Keep Basic Auth passwords, SSH credentials, tokens, raw rollout content,
  source IDs, meeting links, notes, and third-party records out of the repo,
  command output, durable staging files, and live JSON.
- Reuse the existing widget field contracts and list limits. Source adapters
  should call shared deterministic projection/update functions rather than
  introduce a parallel document format.
- Treat the remote weather widget as server-owned and preserve its latest live
  value when publishing locally generated widget changes.
- Scheduling and publication must remain observable and reversible; silent
  failure is not acceptable for an ambient display.

## Linear Source Evidence

- The connected Linear OAuth app can currently read the user's workspace and
  assigned issues. The account belongs to the `CODE` and `LIFE` teams.
- Issue results expose enough metadata for deterministic selection: title,
  status/status type, priority, due date, labels, project, team, parent, and
  update/completion timestamps.
- The display projection does not need descriptions, URLs, issue IDs, branch
  names, creator/assignee IDs, or raw API objects. These fields must not be
  copied into `widgets.json` or routine logs.
- The Codex Linear connector proves account access for interactive planning but
  is not a runtime API for a standalone repository script. Periodic unattended
  refresh requires a separate local Linear API/OAuth credential boundary.
- Linear's current API documentation states that a personal API key can be
  restricted to `Read` permission and to specific teams. This makes a
  `CODE`/`LIFE` read-only key stored outside the repository a smaller MVP
  boundary than implementing a local OAuth client and refresh flow.
- Local inspection on 2026-07-23 confirmed `.env.local` exists, is ignored by
  `.gitignore`, is not tracked, has mode `0600`, and contains a non-empty
  `LINEAR_API_KEY` assignment. The value was not displayed or recorded.

## Apple Calendar Source Evidence

- This macOS host provides `/usr/bin/osascript` and the system Calendar app.
- Calendar's scripting dictionary exposes read access to calendars and events,
  including calendar name plus event summary, start date, end date, all-day
  state, status, location, notes, and UID.
- The adapter needs only calendar name for source filtering and event summary,
  start/end, and all-day state for projection. Location, notes, UID, attendees,
  URLs, alarms, and raw event objects are forbidden from widget data and logs.
- Calendar access is protected by macOS privacy controls. Missing or denied
  permission must be reported as a source failure and must not trigger retries
  that repeatedly prompt the user.

## Codex Task Source Evidence

- `~/.codex/state_5.sqlite` has a `threads` table with title, cwd, model,
  created/updated/recency timestamps, archive state, and rollout path. It has no
  authoritative running/waiting/blocked task-status column.
- A 2026-07-23 metadata-only aggregate found 283 non-archived threads. Treating
  every non-archived thread as currently waiting would make the dashboard count
  meaningless, so dormant no-goal threads need an explicit recency boundary.
- `~/.codex/goals_1.sqlite` has explicit per-thread goal states including
  `active`, `paused`, `blocked`, `usage_limited`, `budget_limited`, and
  `complete`, but not every thread has a goal row.
- Rollout JSONL lifecycle event types include `task_started`, `task_complete`,
  `turn_aborted`, `user_message`, and `agent_message`. Bounded tail inspection
  can distinguish an in-flight turn from a completed/aborted turn without
  copying message content.
- The Codex app can report runtime thread states such as `active` and
  `notLoaded`, but that app tool is not a standalone repository-script API.
  Phase 5 therefore does not depend on an app-server protocol and uses only the
  local SQLite/rollout evidence described above.
- `logs_2.sqlite`, prompt/response fields, previews, first-user-message fields,
  and full rollout content are outside the adapter boundary.

## Reference Repository Research

The source repository at `/Users/ethereal/Documents/Code/ai-desk-card` was
inspected before selecting this implementation boundary.

- Reusable mechanisms: explicit per-widget schemas, bounded list projection,
  read-current-state-before-writing, persistent last-known-good cache, visible
  scheduler configuration, per-widget TTL/freshness, and a pure-Python fallback.
- The reference `card-refresh` flow is an agent workflow: cron launches a
  headless AI CLI, the model chooses fetchers, and `push_widget.py` POSTs one
  widget at a time. Its deterministic fallback only handles weather, system,
  and git status.
- The reference repository has a Reminders adapter, but no equivalent
  Calendar adapter or deterministic Codex task-state collector. Its
  `ai-status` and `ai-tasks` schemas describe payloads; the refresh skill
  explicitly skips those widgets because they are conversation-driven.
- The reference daemon's cache/TTL and Pillow/BLE/USB/raw-frame transport are
  hardware concerns. They do not belong in this browser/static JSON project.
- The reference flow's AI-driven routing, optional schema validation, and
  direct per-widget push are insufficient for this task's privacy, repeatability,
  and server-owned-weather requirements. Phase 5 therefore reuses the
  configuration and cache ideas but implements deterministic local adapters and
  one validated atomic publish transaction.

## Confirmed Codex State Policy

The following approved policy is the deterministic interpretation of
`ai-status` / `ai-tasks`. Codex has no single authoritative thread-status
field, so every state is derived only from the allowed metadata and lifecycle
evidence below.

- Scope active-state classification to non-archived local Codex threads across
  workspaces; do not filter by this repository's `cwd`. A thread completed and
  archived today may still contribute to `completed_today`.
- `running`: the latest bounded lifecycle event is an unfinished
  `task_started` turn and its thread/rollout metadata has changed within the
  last 30 minutes. An older unmatched start is stale evidence, not permanent
  proof that work is still running.
- `blocked`: the thread has an explicit goal status of `blocked`,
  `usage_limited`, or `budget_limited`, provided it is not currently running.
- `waiting`: an explicit `active` or `paused` goal with no running turn, or a
  no-goal non-archived thread whose latest terminal event is `task_complete` or
  `turn_aborted` within the last 24 hours. Older no-goal threads are dormant,
  not waiting.
- `completed_today`: distinct threads with a `task_complete` lifecycle event
  on the current local date, plus goals that entered `complete` today; count a
  thread once even if it produced multiple turns.
- `ai-status` chooses the most recently updated unfinished candidate after the
  above classification. It projects only the complete selected title, model,
  state label, and elapsed/context values available from metadata; it never uses
  prompt, response, preview, path, thread ID, or rollout text.

## Confirmed Refresh Policy

- A visible user LaunchAgent runs one bounded deterministic refresh every five
  minutes continuously while the macOS user session is available.
- The LaunchAgent is enabled only after source preflight, preview, and one
  authenticated manual publication pass.
- The five-minute cadence matches the browser polling interval and spends no
  model tokens. macOS sleep pauses execution; refresh resumes on a later tick
  after wake without replaying missed runs.
- The existing server weather timer remains independent and server-owned.

## Text-Fit Evidence

- `web/styles.css:131-138`, `169-180`, `182-190`, `208-217`, `226-238`,
  `256-276`, `298-306`, and `345-351` explicitly apply single-line overflow
  hiding and `text-overflow: ellipsis` to metadata, weather, AI status, list
  rows, task counts, and footer text.
- Calendar titles, todo titles, and forecast conditions inherit the shared
  single-line `.row-main` rule. A longer source value is therefore replaced by
  `...` even when wrapping could make it readable.
- `web/styles.css:140-148` and `192-199` hide overflow for focus and AI task
  text without an ellipsis, so some long values can be silently clipped.
- Hover tooltips or interaction are not a valid recovery mechanism for an
  ambient e-ink display. Supported text must be readable directly on screen.
- The page has fixed `758x1024` geometry and no-scroll requirements. Arbitrary
  source length, a fixed five/four row count, and a fixed large font cannot all
  be guaranteed simultaneously; an explicit overflow priority is required.

## Requirements

- Define the source of truth and refresh contract for `focus`, `todo`,
  `calendar`, `ai-status`, `ai-tasks`, and Codex quota before implementation.
- Implement the Linear adapter as read-only. It may use issue metadata for
  filtering and ordering, but its output is limited to the existing focus task
  text and up to five todo text/tag pairs.
- Make Linear selection policy explicit and testable: `CODE`/`LIFE` team scope
  with no project filter, current-user assignee, allowed status types, due-date
  treatment, label semantics, ordering, and behavior when no candidate exists.
- Fetch enough assigned issues to classify parent containers before applying the
  five-item display limit. Do not infer that an issue is a parent merely because
  it has its own `parentId`; that field identifies an eligible child issue.
- Rank the selected todo candidates deterministically by Linear priority first.
  The first ranked todo supplies `focus.task`; lower-priority items remain only
  in the todo widget. The accepted tie-breakers are due date, started status,
  update time, and stable identifier in that order.
- Normalize Linear priority so `urgent`, `high`, `normal`, `low`, and no
  priority sort in that order even if the API encodes no priority as zero.
- Derive display tags from local due date: `overdue`, `today`, `tomorrow`,
  `this-week`, `later`, or empty for no due date. Do not expose team, project,
  label, identifier, or raw status as a tag.
- Implement one deterministic local adapter per approved source. Separate source
  access from privacy projection so fixture-based tests do not require live
  accounts or mutate source data.
- Implement Apple Calendar access as a read-only `osascript` adapter that emits
  a bounded machine-readable payload for Python projection. Do not add, modify,
  delete, accept, or decline calendar events.
- Apply the calendar-name allowlist inside the source adapter before emitting
  event records. Calendar names are filter inputs only and must not be written
  to `widgets.json` or routine logs.
- Select events that overlap the accepted now-through-tomorrow window, including
  ongoing all-day events. Normalize all comparisons in the local timezone,
  exclude ended/canceled events, order ongoing before future and then
  chronologically, and crop the combined list to four.
- Project only the fields already required by the UI: focus text; up to five
  todo text/tag pairs; up to four calendar start/title/end rows;
  privacy-projected AI status/task counts; and normalized quota windows. Field
  projection must not shorten selected source titles or append ellipsis.
- Align the todo renderer with the approved five-item producer/plan contract
  using the smallest layout-safe change, then rerun fixed-viewport and physical
  no-overflow checks. This contract correction does not authorize a redesign.
- Remove ellipsis and silent clipping from user/source content in focus,
  AI status, weather, calendar, and todo. Prefer normal multi-line wrapping,
  `overflow-wrap` for long tokens, and deterministic content-based font/spacing
  classes; do not scale font size from viewport width and do not require hover.
- Keep a physically validated readability floor. When content still cannot fit
  at that floor, apply the approved extreme-text policy instead of reintroducing
  ellipsis, clipping, page scroll, overlap, or an unreadably small font.
- Apply the approved extreme-text policy deterministically: remove
  lowest-ranked list rows until all remaining rows fit and show
  `selected/total`; for a single primary title, collapse lower-priority
  auxiliary blocks before reducing the title below the readability floor.
- Keep auxiliary generated labels short through deterministic formatting. Do
  not copy verbose source metadata into the page merely because wrapping exists.
- Build Codex task state from read-only metadata and bounded lifecycle-event
  inspection. Do not infer blocked state from natural-language message content
  and do not read `logs_2.sqlite`.
- Do not depend on the Codex app-server in Phase 5 because it has no supported
  standalone script API. Keep SQLite metadata queries, goal-state queries, and
  rollout lifecycle parsing behind separate source functions so schema drift or
  an unavailable source produces an explicit stale result rather than invented
  counts.
- Give every derived widget a source timestamp and freshness state. A source
  failure must preserve that widget's last-known-good value, mark only that
  widget stale/unavailable, and leave unrelated widgets intact.
- Compose adapters through one local orchestration entry point. A preview mode
  must show source health and changed widget types without printing raw records.
- Merge against the current live `widgets.json` before publication so the
  server-owned weather value and unrelated widgets are not regressed by an old
  local copy.
- Validate JSON structure, widget types, field allowlists, list limits, and
  banned privacy fields before any live mutation.
- Create a timestamped remote backup, atomically install the candidate with mode
  `0644`, and verify the expected contract after publication. Any failure must
  preserve or restore the previous live file and fail loudly.
- Serialize local publication with a visible run lock, and serialize the
  remote install with the same lock used by the weather updater so a local
  publish cannot regress a concurrent server-owned weather update.
- Use the approved continuous user LaunchAgent with bounded execution and logs;
  do not introduce a work-hours filter or an opaque resident daemon.
- Use source-native local authorization or environment-managed credentials.
  Do not add credentials, passwords, host keys, or private server state to
  tracked files.
- Prefer an already-exported `LINEAR_API_KEY`; otherwise the local entry point
  may load repository-root `.env.local` without logging its contents. Missing,
  empty, malformed, or rejected credentials must fail before changing JSON or
  contacting the publish host.
- Keep the workflow deterministic. Model calls are not permitted for routing,
  validation, field mapping, retry behavior, or publication decisions.
- Update `web/README.md`, `deploy/README.md`, and `PLAN_web.md` with the final
  command contract and failure boundary.

## Acceptance Criteria

- [x] The selected real systems and refresh policy are recorded for every
      non-weather widget; no production widget depends on typed smoke values.
- [x] When todo contains at least one item, `focus.task` exactly matches the
      first, highest-priority todo item. When todo is empty, focus renders an
      explicit empty state rather than retaining an unrelated old task.
- [x] Linear candidate tests cover both sides of the hierarchy rule: a parent
      referenced by a child's `parentId` is excluded, while that child remains
      eligible.
- [x] Linear ordering tests prove priority, overdue/today/future/no-date due
      buckets, `started` precedence, update time, and stable final ordering.
- [x] A five-item Linear result with representative bounded titles renders all
      five items at the target viewport; producer, example, renderer count, and
      static contract tests share the same normal limit and do not introduce
      scroll, clipping, or overlap.
- [x] Representative long English and Chinese focus/task/event titles render
      without `...`, hidden text, overlap, page scroll, or internal overflow at
      `758x1024`, `740x951`, and `467x600` viewport measurements.
- [x] Long unbroken tokens wrap without widening the card, and content-based
      font fitting never crosses the physically accepted readability floor.
- [x] Browser assertions compare each supported text element's rendered
      dimensions with its scroll dimensions so removing the ellipsis declaration
      cannot mask a new `overflow: hidden` failure.
- [x] An extreme fixture proves that only lowest-ranked whole rows are omitted,
      the remaining titles are complete, and the header truthfully reports
      selected/total; a single-title fixture preserves the title before
      auxiliary metrics.
- [x] Linear credential tests cover environment precedence, `.env.local`
      fallback, missing/empty values, unauthorized responses, redacted output,
      and no local/live mutation after authentication failure.
- [x] Apple Calendar adapter tests cover allowed calendar filtering, timed and
      all-day projection, canceled/past event exclusion, four-event cropping,
      permission denial, malformed adapter output, and privacy-field removal.
- [x] Missing, empty, and unmatched Calendar allowlists fail without falling
      back to all calendars or replacing the last-known-good calendar widget.
- [x] Calendar window tests cover late-night execution, tomorrow's boundary,
      ongoing timed events, multi-day/all-day overlap, ended/canceled exclusion,
      deterministic ordering, and the shared four-event cap.
- [x] Fixture-backed adapter tests prove exact source-to-widget field mappings
      and prove that IDs, notes, links, attendees, transcripts, and tokens are
      excluded.
- [x] A local run reads real source state and produces focus, todo, calendar,
      AI status/task counts, and quota values that can be traced to their source
      timestamps without exposing raw records.
- [x] A source failure preserves last-known-good data and marks only the owning
      widget stale/unavailable.
- [x] Preview reports source health and changed widget types without modifying
      local/live files or revealing private source content.
- [x] Publication preserves latest server-owned weather and unrelated widgets,
      creates a backup, installs an atomic `0644` file, and verifies the result.
- [x] Validation, source, transfer, backup, install, and verification failures
      have tested fail-loud behavior and do not leave a broken live JSON file.
- [x] The live device displays current real values for all approved sources;
      smoke/demo labels and dated placeholder content are absent.
- [x] Codex aggregation covers tasks across workspaces while proving that
      prompts, responses, previews, paths, thread IDs, and raw rollout records
      never enter widget data or routine output.
- [x] Codex source tests cover in-flight, completed-turn, aborted, explicit goal
      blocked/complete, missing-goal, archived, stale-source, and schema-drift
      cases using metadata-only fixtures.
- [x] Repository quality gates and one authenticated end-to-end real-data
      publication smoke pass before the task is closed.
- [x] The continuous five-minute LaunchAgent is inspectable from the local user
      session, contains no credentials, records source health plus publish result
      without raw source data, pauses during sleep, and resumes on a later tick.
      Direct system sleep/wake observation is explicitly waived by the user;
      LaunchAgent cadence, bounded execution, and later natural-tick recovery
      remain verified.

## Out Of Scope

- Web editing, user accounts, backend APIs, databases, queues, or a build step.
- An opaque resident local daemon or unbounded background process.
- Mirroring complete Reminders, Calendar, Notion, Linear, or AI session records.
- Writing back to the source systems; Phase 5 reads and projects data only.
- UI redesign, new widgets, or reopening the skipped Phase 4 evidence gates.

## Notes

- This complex task has complete `prd.md`, `design.md`, and `implement.md`
  planning artifacts. Implementation still requires explicit final user review
  before `task.py start`.
- Inline Trellis mode is active; `implement.jsonl` and `check.jsonl` remain
  empty unless the dispatch mode changes.
