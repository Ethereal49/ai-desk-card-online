# Codex Quota Freshness Evidence

## Decision

Evidence-backed no-go on `2026-07-26`: the current local Codex runtime does not
expose an authoritative current quota window through a stable local surface.
Keep the last-known-good quota explicitly stale and retain partial exit `2`.
Do not change the parser or the 600-second freshness threshold.

## Bounded Baseline

- `scripts/refresh_dashboard.py --source-check` reported Linear, Apple
  Calendar, and Codex metadata `ok`, with `codex-quota=stale` and exit `2`.
- The existing parser selected the last valid local observation at
  `2026-07-22T03:56:42.625Z`; it contained only a weekly window and was
  correctly marked stale.
- The inventory read at most the newest 80 `rollout-*.jsonl` files and at most
  1 MiB from each file tail. It emitted structural summaries only.

## Structural Findings

- The bounded sample contained 7,249 `event_msg/token_count` records. The
  newest record was observed at `2026-07-25T16:05:40.341Z`, so event emission
  and file discovery are active.
- Current payload keys remain `info`, `rate_limits`, and `type`.
- Current `rate_limits` keys include `primary`, `secondary`,
  `individual_limit`, and `credits`, but all four values are `null` in current
  observations. The latest record with a non-null recognized quota window was
  the same `2026-07-22T03:56:42.625Z` observation selected by the parser.
- All 80 bounded files matched the current `rollout-*.jsonl` discovery rule.
  The stale result is therefore not caused by a filename or directory miss.
- Older non-null windows still use recognized `used_percent`,
  `window_minutes`, and `resets_at` fields. There is no unsupported current
  envelope for a parser adapter to normalize.

## Alternative Local Surfaces

- The installed Codex CLI exposes login status, diagnostics, model-catalog,
  and app-server commands, but no stable local quota/status command.
- Key-only inspection of local Codex JSON metadata found auth, model-cache,
  version, hook, and browser-host configuration surfaces. No quota cache is
  present; authentication values were not read or printed.
- Schema-only inspection of the local Codex SQLite stores found thread, goal,
  log, memory, and migration state, with no quota or rate-limit table/view.
- No remote account API, UI scraping, model call, or raw session/account record
  was used.

## Rationale And Runtime Contract

An empty current `rate_limits` object is an explicit absence of authoritative
quota data, not a schema variant. Accepting file modification time, token
counts, credits metadata, or an older observation as current quota would
fabricate freshness. The existing behavior is therefore the correct outcome:

- preserve the last-known-good bounded quota values;
- mark the quota stale with a low-sensitivity error;
- report `codex-quota=stale` and partial exit `2`;
- continue refreshing and publishing the other healthy owned widgets.

## Validation

- Corrected focused command: 19 quota/orchestrator tests passed.
- Full suite: 86 tests passed.
- Python compile, Trellis validation, and `git diff --check` passed.
- Redacted source check returned partial exit `2` with Linear, Apple Calendar,
  and Codex metadata `ok` and Codex quota `stale`, matching the no-go contract.
- The backend executable contract did not change, so no backend spec edit is
  required. Operator docs and `PLAN_web.md` record the durable stale behavior.
- Preview, publish, live JSON/weather, and natural LaunchAgent exit `0` gates
  are conditional on a fresh authoritative source and were not run. Reporting
  them as passed would violate the no-go boundary.
