# Restore Codex Quota Freshness

## Goal

Restore a truthful, low-sensitivity fresh Codex quota projection so the normal
five-minute refresh can return healthy status instead of permanent partial
success, while retaining explicit stale/last-known-good behavior whenever no
authoritative current quota is available.

## Background

- On `2026-07-25`, `scripts/refresh_dashboard.py --source-check` returned `2`:
  Linear, Apple Calendar, and Codex metadata were `ok`; `codex-quota=stale`.
- The published quota sample was last updated on `2026-07-22`, while all other
  live widgets were current. Scheduled refreshes still published successfully
  but ended with exit `2` every 300 seconds.
- `scripts/update_codex_usage.py` currently accepts only rollout
  `event_msg` records whose payload is `token_count` and contains a
  `rate_limits` object. It marks records older than 600 seconds stale.
- Stale behavior is intentional and correct. The unresolved issue is whether
  the current Codex runtime changed event shape/location or stopped emitting an
  authoritative quota event.

## Requirements

- Diagnose the root cause before changing code. Record only structural facts
  such as file/event kind, field names, timestamps, and availability; do not
  copy prompts, responses, transcripts, account identifiers, auth values, or
  raw rollout lines into task evidence.
- Use the simplest authoritative local source available:
  1. support a current rollout event shape if it exists;
  2. otherwise use an existing stable local Codex metadata/API surface only if
     it can be read without copying credentials or private records;
  3. if no authoritative current source exists, produce an evidence-backed
     no-go and keep quota stale.
- Do not increase the stale threshold to hide missing updates, fabricate quota,
  screen scrape UI, invoke an AI model, or query/write external accounts.
- Preserve the public quota schema: bounded `source`, `updated_at`, `stale`,
  optional `last_attempt_at`/`error`, and only the 5h/7d remaining percentage,
  window length, and reset time fields.
- Preserve backwards compatibility with known rollout shapes, reverse bounded
  scanning, last-known-good merge, privacy rejection, and partial exit `2`
  when current quota is genuinely unavailable.
- A fresh authoritative quota must make `--source-check`, preview, publish, and
  the next natural LaunchAgent run return `0` when every other source is fresh.
- Update backend code-spec, tests, operator documentation, evidence, and the
  Phase 7 checkpoint in `PLAN_web.md` for the chosen source contract.

## Acceptance Criteria

- [ ] Research evidence identifies why no quota event newer than `2026-07-22`
  reached the current parser and records the selected source or an explicit
  no-go without private content.
- [ ] Focused tests cover every newly accepted structural variant, event/source
  ordering, freshness timing, malformed data, bounded reads, privacy crop, and
  backwards compatibility with the existing rollout fixture.
- [ ] Missing or old authoritative data remains stale, preserves last-known-good
  quota, and returns partial exit `2`; it is never silently relabeled fresh.
- [ ] With current authoritative data, `--source-check` reports
  `codex-quota=ok` and exits `0` when other sources are healthy.
- [ ] Preview/publish output remains bounded and contains no raw quota event,
  path, account field, token, title, prompt, response, or configured text.
- [ ] A validated publish preserves server-owned weather and the installed JSON
  passes the shared contract with fresh quota.
- [ ] A subsequent natural LaunchAgent tick exits `0`, writes a bounded `0600`
  status file, and leaves no refresh process running.
- [ ] Full unit/static/privacy/Trellis/plan/diff gates pass and the child has
  durable `evidence.md` before archive.

## Out Of Scope

- Changing Codex account limits or authentication.
- Adding a remote quota proxy, browser automation, backend service, or model
  call.
- Treating an unavailable fresh source as a successful implementation.
