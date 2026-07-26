# Configurable Focus And Visual Alignment

## Goal

Make the fixed e-ink dashboard easier to scan by limiting long display text to
two readable lines with a visible ellipsis, allowing the headline Focus widget
to project one explicitly configured source, and applying one consistent
alignment system across the existing six-widget layout.

## Background

- Phase 5 completed the real-data adapters, privacy projection, locked publish
  workflow, five-minute LaunchAgent, automatic viewport scaling, and the
  `758x1024`, `740x951`, and `467x600` browser gates.
- The current Focus value is produced inside the Linear adapter and always
  duplicates the first selected todo item.
- The current text policy preserves complete rendered titles and can remove a
  lower-ranked row when wrapped content does not fit. The user now prefers a
  two-line visual limit with an ellipsis so the dashboard remains easy to scan.
- The current layout mixes floats, right alignment, center alignment, fixed
  footer widths, and list columns. The user wants a coherent visual rhythm, but
  centered list prose would make calendar and todo rows harder to compare.

## Requirements

### R1. Two-Line Display Policy

- Long user/source content in Focus, AI status, weather conditions, forecast,
  calendar, and todo surfaces must render at no more than two visual lines.
- Content that exceeds two lines must show a visible ellipsis. Content that
  fits within two lines must not show an ellipsis.
- The complete privacy-projected string must remain in `widgets.json` and in
  the rendered DOM. Truncation is a presentation concern, not a source or
  publisher transformation.
- Chinese, normal English, and a long token without break opportunities must
  all remain bounded. The page must not rely on hover, scrolling, animation,
  viewport-dependent font sizing, or arbitrary character-count truncation.
- Known-short metadata such as time, count, freshness, quota, and source labels
  may remain one line. The normal five-item todo fixture must continue to show
  all five rows; row removal remains only a final whole-widget overflow guard.

### R2. Configurable Focus Projection

- Focus becomes a deterministic presentation projection instead of a second
  output owned by the Linear adapter.
- Missing local configuration preserves the current default behavior:
  `todo.first` supplies the headline task.
- The allowlisted sources are exactly `todo.first`, `calendar.next`,
  `ai-status.task`, `weather.current`, and `manual`.
- A local JSON file at
  `~/.config/ai-desk-card-online/focus.json` stores the selection. A CLI path
  override is allowed for tests and migration. The repository contains only a
  public example, never the user's live manual text.
- Configuration is bounded and strict: only documented keys are accepted,
  arbitrary JSON paths or executable selectors are forbidden, and a present
  malformed configuration fails before baseline SSH or live mutation.
- Optional `subtitle` and `big_text` overrides may customize any linked source.
  `manual` additionally requires `task`. Values use the existing Focus string
  bounds and privacy validation.
- A linked source propagates its freshness. A recoverable source failure uses
  the source's last-known-good widget before Focus is resolved. Empty valid
  sources produce explicit empty-state text rather than a guessed value.
- The existing publisher, remote installer, weather ownership, scheduler, and
  browser JSON contract remain deterministic and model-free.

### R3. Alignment And Visual Rhythm

- Primary headline and metric content is horizontally and vertically centered
  within its available region.
- Calendar, todo, and forecast rows remain left-aligned and share explicit,
  stable columns because scanability takes precedence over blanket centering.
- Widget headers in the same row use consistent height, vertical alignment,
  title baseline, metadata placement, divider position, and spacing.
- The AI task counts use equal cells and centered values without nested
  decorative cards. The footer uses balanced left/center/right grid columns.
- Top bar, widget padding, line heights, row gaps, and secondary text color use
  a small shared token set. No palette redesign, animation, gradient, shadow,
  new widget, or framework is introduced.
- The fixed `758x1024` card, automatic fit behavior, bottom border, and no-page-
  scroll contract remain unchanged at all three validation viewports.

### R4. Compatibility, Documentation, And Rollout

- Keep static HTML, CSS, vanilla JavaScript, and `widgets.json`; do not add a
  web editor, backend API, database, or source-system write.
- Preserve six widget types, slot names, top-level fields, five todo items,
  four calendar items, offline fallback, shared remote lock, and atomic publish.
- Update the example data, focused tests, frontend/backend specs where the
  executable contract changes, `web/README.md`, `deploy/README.md`,
  `AGENTS.md` only if structure changes, and `PLAN_web.md`.
- Deploy the changed static bundle and deterministic publisher code through the
  existing authenticated/static boundary when no unavailable credential is
  required. Do not place live Focus configuration on the server.

## Acceptance Criteria

- [x] AC1: Browser fixtures prove long Chinese, English, and unbroken-token
  content is visually limited to two lines with an ellipsis, while short text
  is not ellipsized and the DOM/JSON retain the full projected strings.
- [x] AC2: The normal fixture renders five todo rows; no widget or page reports
  horizontal or vertical overflow at `758x1024`, `740x951`, or `467x600`.
- [x] AC3: Missing Focus configuration resolves to `todo.first`, and unit tests
  cover every allowlisted source, optional overrides, valid empty states, stale
  propagation, and stable projected fields.
- [x] AC4: Unknown sources/keys, malformed or oversized JSON, invalid field
  types/lengths, and an incomplete `manual` configuration fail before baseline
  SSH or publish, without printing configured text.
- [x] AC5: Linear owns only todo in the production refresh path; Focus is
  resolved once after successful/stale source results have been merged, and
  weather remains server-owned.
- [x] AC6: Browser screenshots and geometry checks show centered primary
  content, left-aligned list columns, equal AI count cells, aligned header
  dividers, balanced footer columns, no overlap, and a complete bottom border.
- [x] AC7: Full Python tests, Python compile, JavaScript syntax, static/privacy
  checks, Trellis validation, plan freshness, and `git diff --check` pass.
- [x] AC8: Preview/source health output remains bounded and redacted; a live
  publish preserves weather, returns a valid installed document, and the
  installed LaunchAgent completes a subsequent scheduled refresh without
  configuration or contract failure.
- [x] AC9: The user confirms the deployed physical device remains readable, or
  explicitly waives that physical-only evidence; no unverified physical claim
  is recorded as passed.

## Out Of Scope

- Browser-side configuration or editing controls.
- Arbitrary field paths, scripts, plugins, model-selected routing, or dynamic
  widget creation.
- Changing source-system records, the Linear ranking policy, Calendar scope,
  Codex classification, refresh cadence, authentication, or server topology.
- Reopening Phase 4 or Phase 5 evidence already archived.
