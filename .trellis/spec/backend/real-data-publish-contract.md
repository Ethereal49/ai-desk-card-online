# Real-Data Publish Contract

## Scenario: Local Sources To Authenticated Static Runtime

### 1. Scope / Trigger

Use this contract when changing a real-data adapter, the shared widget
projection, the preview/publish orchestrator, the remote installer, or the
macOS scheduler. The Mac owns `ai-status`, `focus`, `ai-tasks`, `calendar`, and
`todo`; the server owns `weather`. A publish must merge those ownership domains
without exposing source records or replacing a newer weather value.

### 2. Signatures

```text
scripts/refresh_dashboard.py [--source-check | --preview | --publish]
  [--baseline PATH] [--host HOST] [--remote-path PATH]
  [--remote-lock PATH] [--remote-backups PATH] [--local-lock PATH]
  [--focus-config PATH]
  [--state-db PATH] [--goals-db PATH] [--sessions PATH]

scripts/configure_focus.py [--config PATH] get
scripts/configure_focus.py [--config PATH] set --source SOURCE
  [--task TEXT] [--subtitle TEXT] [--big-text TEXT]
scripts/configure_focus.py [--config PATH] reset

scripts/run_scheduled_refresh.py [--status PATH] [--timeout SECONDS]

deploy/scripts/install_widgets.py --payload PATH
  [--live PATH] [--lock PATH] [--backup-dir PATH] [--keep-backups COUNT]
```

Each source returns a `widget_contract.SourceResult` containing only its source
name, owned widget types, health, observation time, projected widget data, and
an optional low-sensitivity error label.

### 3. Contracts

- `LINEAR_API_KEY` is required. A non-empty process environment value wins;
  otherwise repository-root `.env.local`, then `.env`, may provide it.
- `AI_DESK_CARD_CALENDARS` is required and must be a non-empty JSON array of
  exact Apple Calendar names. The names are filter inputs and never public data.
- Missing Focus configuration defaults to `todo.first`. A present configuration
  is a bounded JSON object that allows only `todo.first`, `calendar.next`,
  `ai-status.task`, `weather.current`, or `manual`, plus documented overrides.
  Invalid configuration exits before baseline SSH and never prints its content.
- `configure_focus.py` reuses `parse_focus_config` as the single selector/text
  validator. `get` reports only source and field-presence flags; `set` validates
  the complete candidate and existing file before replacement; `reset` writes
  the explicit `{"source":"todo.first"}` default. It creates a missing parent
  as mode `0700` and atomically replaces the file as mode `0600`.
- The Focus configuration command never reads sources, writes `widgets.json`,
  invokes SSH, previews, publishes, or restarts the scheduler. A successful
  change is read by the next normal scheduler tick; an explicit preview or
  publish remains a separate operator action.
- Source access is read-only. Linear projects at most five `text`/`tag` todo rows;
  Calendar projects at most four `start`/`title`/`end` rows; Codex projects only
  title/model/timing/state counts and bounded quota percentages/reset times.
- Focus is resolved exactly once from the merged projected widgets. It is not a
  second Linear-owned source result. Linked source freshness/LKG state is
  propagated and weather remains server-owned.
- Current limitation: `weather.current` Focus is resolved from the local
  baseline before publish. The remote installer then re-reads the live document
  under the shared lock and preserves its current server-owned weather. If
  weather changes between those steps, the installed weather is current while
  Focus can reflect the previous weather until the next local scheduler tick.
- `widget_contract.validate_document` is the final public boundary. It rejects
  unknown fields, duplicate types/slots, excessive list counts, invalid text,
  and private keys such as IDs, paths, links, notes, attendees, prompts,
  responses, previews, transcripts, tokens, and API keys.
- Source failure preserves that widget's last-known-good data and adds only
  `stale`, `last_attempt_at`, and a low-sensitivity `error`. A configuration
  failure is fatal and cannot be merged or published.
- Routine output is limited to source health, changed widget types, publish
  result, or a bounded failure reason. Never print raw source records or titles.
- The IP HTTPS verifier uses a five-second connect timeout, a fifteen-second
  per-attempt limit, and at most two connection-error retries with a one-second
  delay. Retries only address transport flakiness; every expected HTTP status
  is still checked exactly.
- Local runs use `/tmp/ai-desk-card-refresh.lock`. Remote publish and weather
  update use `/run/lock/ai-desk-card-widgets.lock`.
- The remote installer re-reads live JSON under the lock, preserves weather,
  creates a changed-only `0600` backup, atomically installs mode `0644`, verifies
  exact content and mode, and restores the backup after a failed install check.
- The LaunchAgent contains no credentials. It runs every 300 seconds while the
  user session is available; `run_scheduled_refresh.py` bounds execution to 150
  seconds and atomically replaces a maximum 8192-byte `0600` latest-status file.

### 4. Validation & Error Matrix

| Condition | Required result |
| --- | --- |
| All sources fresh | Exit `0`; preview or publish may proceed |
| Recoverable source or quota stale | Exit `2`; preserve last-known-good and report partial health |
| Missing/rejected Linear key, invalid/unmatched Calendar allowlist, or invalid Focus config | Exit `3`; do not read the live baseline or contact the publish host |
| Valid Focus config `get`, `set`, or `reset` | Exit `0`; print only source and field-presence flags |
| Focus config argument usage error | Exit `2`; print bounded argparse usage |
| Focus config validation or malformed existing file | Exit `3`; preserve the previous path and print `reason=configuration` |
| Focus config local filesystem read/write failure | Exit `1`; preserve previous bytes, remove any temporary file, and print `reason=local-io` |
| Local lock already held | Exit `4`; print `refresh=skipped reason=already-running` |
| SSH, transfer, JSON, contract, or installer failure | Exit `1`; fail loudly without a broken live file |
| Scheduled run exceeds its bound | Exit `124`; write `refresh=fatal reason=scheduled-timeout` |
| Remote owned widgets are unchanged | Exit `0`; print `publish=no-change`; create no backup |
| Post-install content or mode differs | Non-zero; restore the verified backup under the shared lock |

Basic Auth is not stored in this workflow. The authenticated acceptance gate
receives `AI_DESK_CARD_AUTH_PASSWORD` only through the caller's environment.

### 5. Good/Base/Bad Cases

- Good: all sources are fresh, preview reports only health and changed types,
  publish preserves the live weather hash, and the installer returns `updated`.
- Good: `configure_focus.py set` writes a parser-valid mode-`0600` config and a
  subsequent `get` reports presence flags without revealing configured text.
- Base: quota is stale but other sources are usable; the publish succeeds with
  exit `2`, keeps the prior quota values marked stale, and updates other widgets.
- Base: `configure_focus.py reset` replaces a valid config with the explicit
  default; no live file changes until a separate normal refresh runs.
- Base: a concurrent server weather update wins under the remote lock while a
  `weather.current` Focus derived before publish may lag for one local tick.
- Bad: Calendar configuration is absent or matches no calendar; exit `3` occurs
  before SSH and the live document is unchanged.
- Bad: invalid Focus text, a malformed existing file, or a failed atomic
  replacement leaves the previous config byte-for-byte unchanged and emits no
  configured value.
- Bad: two timer invocations overlap; one owns the local lock and the other exits
  `4` without creating remote staging data.

### 6. Tests Required

- `test_source_linear.py`: environment precedence, auth rejection, pagination,
  parent/child selection, all ranking keys, field projection, and redacted errors.
- `test_source_apple_calendar.py`: allowlist failures, permission/timeout/malformed
  output, local-time overlap, cancellation, ordering, list cap, and privacy crop.
- `test_source_codex_tasks.py`: bounded lifecycle reads, schema drift, state
  precedence, distinct daily completion, and forbidden metadata exclusion.
- `test_widget_contract.py`: owned fields, private-key rejection, list limits,
  isolated stale merge, quota merge, and changed-type reporting.
- `test_refresh_dashboard.py`: no-write preview, no-host configuration failure,
  Focus ordering, local non-overlap, unique staging, redacted output, and
  publish response checks.
- `test_focus_config.py`: missing/default configuration, every allowlisted
  source, overrides, empty/stale projection, strict shape/size validation, and
  redacted failure boundaries.
- `test_configure_focus.py`: help/exit contract, every selector round-trip,
  manual/linked rules, redacted output, atomic preservation and cleanup,
  directory/file modes, explicit reset, and no widget/publish side effects.
- `test_install_widgets.py`: weather preservation, changed-only backup, `0644`
  atomic install, no-change behavior, validation failure, and rollback.
- `test_run_scheduled_refresh.py`: bounded status content, mode `0600`, timeout,
  and exit-code preservation.

### 7. Wrong vs Correct

#### Wrong

```text
Build widgets.json locally from an old copy, copy all six widgets to the server,
then overwrite the live file without sharing the weather lock.
```

This can regress a concurrent weather update and publishes before the server's
current document has been validated.

#### Correct

```text
Collect and privacy-project five local widgets -> validate -> transfer only the
owned payload -> acquire the shared remote lock -> re-read live JSON -> preserve
weather -> validate -> backup if changed -> atomic install -> verify or restore.
```

#### Wrong: Focus Configuration

```text
Hand-edit Focus JSON, overwrite widgets.json, and publish in the same command.
```

This duplicates validation, can expose private configured text, and creates a
second owner for live Focus state.

#### Correct: Focus Configuration

```text
CLI args -> shared Focus parser -> private atomic config replacement -> next
normal scheduler read, with preview/publish remaining separate explicit steps.
```
