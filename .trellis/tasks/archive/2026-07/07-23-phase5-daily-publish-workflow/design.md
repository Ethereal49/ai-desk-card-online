# Phase 5 Real-Data And Publish Design

Status: ready for final user review. Codex state, text-overflow, and continuous
five-minute scheduling policies are approved. No implementation starts before
that review.

## Problem

The page and authenticated static hosting work, but five widgets still show
caller-supplied smoke data and Codex quota publication is manual. The minimum
useful system is therefore not a richer UI or a backend. It is a deterministic
local process that reads the approved real sources, projects only display-safe
fields, and safely merges them into the live static JSON without overwriting
server-owned weather.

## Design Principles

- Keep `widgets.json` as the only browser runtime contract.
- Read sources locally because Linear credentials, Apple Calendar, and Codex
  metadata live on the Mac.
- Use code, not a model, for selection, projection, validation, retries, and
  publication.
- Preserve last-known-good values per source and expose stale state instead of
  clearing a widget.
- Treat the live server file as the publication baseline; do not persist real
  private source payloads in the Git worktree.
- Keep weather owned by the existing server timer.
- Make every scheduled action inspectable, bounded, and reversible.

## Reference Repository Synthesis

| Reference mechanism | Phase 5 decision | Reason |
| --- | --- | --- |
| `interests.yaml` source/schedule config | Adapt | Keep explicit local source configuration, but the six slots are fixed and do not need configurable routing. |
| Per-widget JSON schema and validation | Reuse concept | Validate the current browser contract before mutation; do not import the old 540x960 schemas verbatim. |
| Read current cache before refresh | Reuse | Read live `widgets.json` before composing replacements so last-known-good data is available. |
| TTL and stale markers | Adapt | Preserve content and mark it stale; never delete an expired widget from the static page. |
| Cron launching a headless AI CLI | Reject | It spends tokens and makes deterministic source selection depend on a model. |
| Pure-Python fallback | Extend | Deterministic Python becomes the primary path for all approved sources, not a three-widget fallback. |
| Loopback daemon and single-widget POST | Reject | The browser pulls one static JSON document from Caddy. |
| Pillow, firmware, BLE, USB, raw frames | Reject | These are outside the browser architecture and repository reuse boundary. |
| Conversation-driven `ai-status` | Replace | The old repository has schemas only; Phase 5 derives status from bounded local metadata and lifecycle events. |

## Architecture

```text
macOS LaunchAgent or manual command
                |
                v
scripts/refresh_dashboard.py
  |-- Linear GraphQL adapter ----------> focus + todo
  |-- Apple Calendar adapter ----------> calendar
  |-- Codex metadata adapter ----------> ai-status + ai-tasks
  |-- existing quota parser -----------> ai-status.quota
                |
                v
sanitized in-memory adapter results
                |
                v
read current live widgets.json over SSH
                |
                v
compose + validate locally
                |
                v
remote installer under flock
  |-- re-read current live document
  |-- preserve current weather/unowned widgets
  |-- backup changed document
  |-- atomic replace mode 0644
  `-- validate and verify
                |
                v
Caddy static file -> e-ink browser

server weather timer -- same flock --> weather-only atomic updater
```

No new HTTP service, database, queue, or resident application daemon is added.

## Proposed Files

```text
scripts/
  refresh_dashboard.py          # one manual/scheduled orchestration CLI
  source_linear.py              # GraphQL access plus pure projection helpers
  source_apple_calendar.py      # osascript access plus event projection
  source_codex_tasks.py         # SQLite/goal/lifecycle metadata aggregation
  widget_contract.py            # shared allowlist, merge, freshness, validation
  test_refresh_dashboard.py
  test_source_linear.py
  test_source_apple_calendar.py
  test_source_codex_tasks.py
  test_widget_contract.py
deploy/
  scripts/
    install_widgets.py          # locked remote merge/backup/atomic install
  launchd/
    com.ethereal.ai-desk-card-refresh.plist.example
```

The exact names may be adjusted during implementation to match surrounding
imports, but ownership remains `scripts/` for local data logic and `deploy/`
for host/scheduler operations. A shared helper is justified here because four
sources need the same validation, freshness, merge, and privacy rules.

## Configuration

- `LINEAR_API_KEY`: exported environment value first, then repository-root
  `.env.local`. The value is never logged.
- `AI_DESK_CARD_CALENDARS`: a required JSON-array environment setting loaded
  through the same local configuration boundary, for example
  `["Calendar", "Work"]`. Empty, malformed, or unmatched names fail before any
  live mutation; there is no all-calendars fallback.
- SSH host and remote path use safe defaults `myecs` and
  `/srv/ai-desk-card-online/widgets.json`, with explicit CLI overrides for
  testing or migration.
- Basic Auth credentials are not used by the publisher. SSH remains the write
  boundary; Basic Auth is used only for the final external read gate.
- The LaunchAgent contains paths and cadence only. It contains no API key,
  password, or private source data.

## Adapter Contract

Each adapter separates source access from pure projection and returns an
in-memory result with:

- source name;
- `ok`, `stale`, or `configuration_error` health;
- source observation timestamp;
- owned widget types;
- sanitized replacement data on success;
- a stable low-sensitivity error code on failure.

Raw source records are discarded after projection and are never printed or
serialized to a durable staging file. `configuration_error` stops before SSH.
Recoverable source failures allow unrelated successful adapters to continue;
the failed source's live value is retained and marked stale.

## Source Designs

### Linear

- Call Linear GraphQL directly with the read-only personal API key.
- Page through all assigned `CODE` and `LIFE` issues needed for parent
  classification before cropping.
- Keep only `started` and `unstarted` issues, excluding any issue identifier
  referenced as another fetched issue's parent.
- Sort by the approved priority, due bucket/date, state, update time, and stable
  identifier keys.
- Project at most five `{text, tag}` rows. The first row also becomes
  `focus.task`; an empty result produces an explicit empty focus state.
- Normalize priority as urgent, high, normal, low, then no priority; Linear's
  numeric zero must not accidentally sort ahead of urgent.
- Derive due tags as `overdue`, `today`, `tomorrow`, `this-week`, `later`, or an
  empty tag when no due date exists. IDs are used only as the final in-memory
  sort key and never leave the adapter.

### Apple Calendar

- Invoke `/usr/bin/osascript` once per refresh with a hard timeout.
- Apply the configured calendar-name allowlist inside AppleScript before event
  records are emitted to Python.
- Return a machine-readable bounded payload containing only title, start, end,
  all-day, and cancellation state.
- In Python, select events overlapping now through tomorrow 23:59 local time,
  exclude ended/canceled events, put ongoing events first, then sort by start,
  and crop the combined all-day/timed list to four.
- Run an interactive permission preflight before enabling the LaunchAgent. A
  denied permission is one source failure, not an in-run retry loop.

### Codex Tasks

- Query only allowed metadata columns from `~/.codex/state_5.sqlite` and goal
  state/timestamps from `~/.codex/goals_1.sqlite`.
- Inspect only bounded rollout tails for lifecycle event type and timestamp.
- Do not select `cwd`, rollout path, preview, first-user-message, prompt,
  response, or transcript content into output.
- Apply the proposed deterministic classification in `prd.md`. Old no-goal
  threads outside the accepted waiting window are dormant and excluded from
  active counts; an unmatched `task_started` older than the accepted 30-minute
  activity guard is not allowed to remain running forever.
- Choose the most recently updated unfinished task for `ai-status`; project a
  complete privacy-projected title, model, state label, and metadata-derived
  timing only.
- Count distinct threads for `completed_today` to prevent multi-turn inflation.

### Codex Quota

- Reuse the existing bounded `update_codex_usage.py` parsing functions instead
  of implementing a second rollout-rate-limit parser.
- Merge quota independently inside `ai-status.data.quota`. A quota failure
  preserves the prior quota and marks only that nested source stale.

## Document And Freshness Contract

- `weather`: remains server-owned.
- `focus` and `todo`: one Linear source result and timestamp.
- `calendar`: one Apple Calendar source result and timestamp.
- `ai-tasks` and the non-quota portion of `ai-status`: one Codex metadata source
  result and timestamp.
- `ai-status.data.quota`: independent Codex rollout source freshness.
- Every owned widget has `source`, `updated_at`, and `stale`. Failed attempts add
  only a stable public error label and `last_attempt_at`; raw exceptions stay in
  local diagnostic output.
- Top-level `updated_at` changes only after a successful remote install.

The existing plan/updater contract permits five todo items, while the current
browser renderer displays only four. Phase 5 treats this as a contract defect:
the renderer and its static/no-overflow tests must be aligned to the approved
five-item limit without redesigning the layout.

## Text Fit And Readability

The current UI uses ellipsis on nearly every narrow text surface and hidden
overflow on the remaining long-text surfaces. Phase 5 replaces that blanket
behavior with content-specific fitting:

- Main content (`focus.task`, Codex task title/state, weather condition,
  calendar title, todo text) wraps on normal boundaries and uses
  `overflow-wrap` for a single long token.
- Font and spacing adjustments are selected from a small deterministic class
  set based on measured content fit after render. They are not functions of
  viewport width, so the fixed card continues to scale as one unit.
- Generated metadata stays deliberately short. Quota, counts, time, source,
  and freshness formatters must produce values that fit their known cells
  without depending on ellipsis.
- The implementation must test both CSS declarations and rendered geometry.
  Removing `text-overflow: ellipsis` is not sufficient if `overflow: hidden`
  still clips glyphs.
- The physical device establishes the minimum readable class. Content must not
  shrink below that floor.

For source values that still exceed the available fixed-height region after
wrapping and readable compaction, the approved policy preserves complete
higher-ranked rows and omits the lowest-ranked overflow row. The widget header
reports selected/total counts so omission is visible. A single primary title
cannot be dropped; its widget first collapses lower-priority auxiliary metrics
or decorative space. Source adapters perform field-level privacy projection but
must not shorten selected titles or append ellipsis.

## Preview And Publish Flow

1. Validate configuration and credential shape. Authentication rejection stops
   before contacting the publish host.
2. Acquire a non-blocking local run lock so scheduled and manual runs cannot
   overlap.
3. Run every source adapter with independent timeouts and collect health.
4. Read the current live JSON over SSH. Preview may read but never write it.
5. Merge successful projections and stale markers into an in-memory candidate.
6. Validate structure, slots, widget/data allowlists, list limits, string/number
   bounds, and banned privacy keys.
7. In `--preview`, print only source health, candidate freshness, and changed
   widget types, then exit without local or remote writes.
8. In `--publish`, transfer the validated owned-widget replacements to a unique
   remote temporary file.
9. The remote installer takes the shared lock, re-reads live JSON, preserves the
   latest weather and unowned widgets, validates the final document, creates a
   timestamped backup only when content changes, atomically installs mode
   `0644`, and verifies the result.
10. Retain a bounded newest set of backups so a five-minute schedule cannot
    create unbounded files. A no-change run creates no backup.
11. Return `0` for full success/no change, a distinct non-zero partial status
    for safely published stale source state, and non-zero fatal status for any
    mutation or verification failure.

The weather systemd service and remote installer must use the same Linux
`flock` path. This closes the read/replace race that a simple `scp` plus
`install` sequence would leave open.

## Scheduler

The confirmed scheduler is a user LaunchAgent with `StartInterval=300` and a
bounded command timeout. It runs continuously while the macOS user session is
available, has no work-hours filter, and resumes on a later tick after sleep.
This is preferable to the old repository's cron-plus-model loop because Apple
Calendar is a user-session source and no model is needed.

The scheduler is installed only after a manual preview and manual authenticated
publish pass. Its stdout/stderr contain one-line source-health and publish
results, never task titles, calendar titles, tokens, or raw JSON.

## Failure Matrix

| Failure | Required behavior |
| --- | --- |
| Missing/malformed config or rejected Linear key | Stop before SSH or any file mutation. |
| Linear network failure | Preserve focus/todo last-known-good values, mark both stale, continue other sources. |
| Calendar denial/timeout/malformed output | Preserve calendar, mark it stale, do not retry inside the run. |
| Codex DB/schema/rollout drift | Preserve AI task fields/counts, mark that source stale, keep quota independent. |
| Quota event unavailable | Preserve prior quota and mark nested quota stale. |
| SSH/read failure | Do not create a candidate install or alter local runtime files. |
| Candidate validation failure | Do not transfer or mutate live data. |
| Concurrent local refresh | Second process exits with a visible already-running status. |
| Concurrent server weather update | Shared remote lock serializes both writers; current weather is preserved. |
| Transfer/install/verify failure | Keep or restore previous live file and exit non-zero. |
| No data changes | Verify health and exit without backup/install churn. |

## Compatibility And Migration

- Existing manual `update_*.py` commands remain available as diagnostic tools
  during Phase 5; they are no longer the production source after live cutover.
- The static browser continues loading `widgets.json` every 300 seconds.
- New freshness fields are additive and must be tolerated by existing renderers
  before scheduler activation.
- Deployment starts with preview, then one manual publish, then scheduler
  installation. Rollback disables the LaunchAgent and restores the latest
  verified remote backup; weather continues independently.
