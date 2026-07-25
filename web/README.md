# AI Desk Card Web

Static MVP for a `758x1024` e-ink browser dashboard.

## Run

```bash
cd web
python3 -m http.server 4173
```

Open:

```text
http://127.0.0.1:4173/
```

Append `?viewport=1` to show the visual viewport used for automatic fitting in
the footer:

```text
http://127.0.0.1:4173/?viewport=1
```

The diagnostic is opt-in and leaves the normal URL unchanged. It is retained
for repeat measurements on the physical e-ink device. Some device browsers
report a larger layout viewport (for example `740x951`) and a smaller visual
viewport (for example `467x600`) because of their page-scale behavior; the
visual value is the one that determines fit.

The card automatically fits the available visual viewport. Browsers that
support layout-aware CSS zoom use it before clipping; other browsers keep the
transform fallback. Viewports smaller than `758x1024` reserve a 4px safe inset
so the lower border does not sit directly on the clipping boundary.

## Data

- Runtime data: `widgets.json`
- Example data: `widgets.example.json`
- Refresh interval defaults to `300` seconds.

The default layout is role-based: weather and `ai-status` in the glance row,
focus in the headline row, `ai-tasks`, calendar, and todo in the detail row,
and status in the footer.

The page keeps the last rendered data if refresh fails and marks the footer as offline.

Long source text keeps its complete JSON and DOM value but is visually limited
to two lines with an ellipsis. Chinese, normal English, and unbroken tokens use
the same presentation rule. The renderer removes lowest-ranked whole list rows
only if the complete fixed widget still overflows after clamping; Calendar and
todo headers keep truthful `selected/total` counts. A normal five-item todo
remains visible at the target viewport.

## Refresh Real Data

Production refresh is one deterministic local command:

```bash
cd /Users/ethereal/Documents/Code/ai-desk-card-online
scripts/refresh_dashboard.py --source-check
scripts/refresh_dashboard.py --preview
scripts/refresh_dashboard.py --publish
```

`--source-check` never contacts the publish host. `--preview` reads the live
JSON over SSH, validates the merged candidate, and prints only source health
plus changed widget types. `--publish` sends only the five locally owned,
privacy-projected widgets to the locked remote installer. The installer
re-reads live JSON under the shared weather lock, preserves weather, writes a
changed-only backup, installs atomically as mode `0644`, verifies, and rolls
back on failure.

Local untracked configuration lives in repository-root `.env.local` with mode
`0600`:

```text
LINEAR_API_KEY=<read-only CODE/LIFE key>
AI_DESK_CARD_CALENDARS=["Work","Personal"]
```

The calendar value must be a non-empty JSON array of exact Apple Calendar
names. Missing, malformed, or unmatched configuration stops before SSH and
never falls back to reading every calendar. Routine output never includes task
titles, event titles, calendar names, source IDs, paths, tokens, or raw JSON.

The source mapping is deterministic:

- Linear assigned `CODE`/`LIFE` issues -> up to five `todo` rows;
- allowlisted Apple Calendar events -> up to four `calendar` rows;
- local Codex thread/goal/lifecycle metadata -> `ai-status` and `ai-tasks`;
- bounded Codex rollout rate-limit events -> `ai-status.data.quota`;
- server timer -> `weather`.

Focus is resolved after those projected widgets and their last-known-good
states have been merged. Its optional local configuration is
`~/.config/ai-desk-card-online/focus.json`; a missing file keeps the default
`todo.first` behavior. Allowed sources are `todo.first`, `calendar.next`,
`ai-status.task`, `weather.current`, and `manual`. See
`deploy/focus.example.json`. A present malformed file stops before SSH, and no
configuration content is printed in routine output.

Manage that private configuration without hand-editing JSON:

```bash
scripts/configure_focus.py get
scripts/configure_focus.py set --source ai-status.task --big-text AI
scripts/configure_focus.py set --source manual --task "Private local focus"
scripts/configure_focus.py reset
```

The command reuses the production parser, creates private `0700`/`0600`
storage, replaces the config atomically, and prints only source plus
field-presence flags. It never writes `widgets.json` or invokes preview,
publish, SSH, or the scheduler. The next normal scheduler tick reads a valid
change; explicit `refresh_dashboard.py --preview/--publish` remains separate.

## Diagnostic Updaters

Generate a complete public-demo `widgets.json`:

```bash
../scripts/web_update.py --focus "Review the AI desk card" --todo "Keep data public"
```

This script is only for resetting a local demo payload. The manual
`update_*.py` commands below remain diagnostic tools and are not production
sources after Phase 5 cutover.

Update the Phase 3 weather widget from the public wttr.in flow:

```bash
../scripts/update_weather.py --location Shenzhen
```

The weather updater preserves the other widgets. If the public weather source
fails, it keeps the previous weather values and marks only the weather widget
as stale.

Update only the low-sensitivity AI session widgets:

```bash
../scripts/update_ai_session.py \
  --session-name "Codex work turn" \
  --task "Advance the AI desk card" \
  --context-used 2000 \
  --context-limit 30000 \
  --running 1 \
  --waiting 0 \
  --blocked 0 \
  --completed-today 2
```

This script writes only `ai-status` and `ai-tasks`. Do not pass transcripts,
message previews, tokens, private task text, or raw logs into `widgets.json`.
Calling convention: run it manually at the end of a meaningful Codex work turn
or milestone. It writes only the selected `widgets.json` file and does not
publish to live or auto-collect session state.

Update only the low-sensitivity Codex quota summary from local rollout files:

```bash
../scripts/update_codex_usage.py
```

The updater scans recent `~/.codex/sessions/**/rollout-*.jsonl` files backwards
in bounded chunks, identifies 5-hour and weekly windows by duration, and writes only
remaining percentages, reset timestamps, source, freshness, and update time to
`ai-status.data.quota`. It does not copy rollout text, prompts, transcripts,
account identifiers, paths, or token details, and it does not publish to live.
If current `token_count.rate_limits` records contain no quota windows, that is
an unavailable source rather than a successful refresh: the updater preserves
the last-known-good values, marks them stale, and the production refresh exits
`2` after continuing with other healthy sources. Do not increase the stale
threshold or use file modification time to relabel an old observation fresh.

Update only the low-sensitivity focus widget:

```bash
../scripts/update_focus.py \
  --task "Define the next useful boundary" \
  --big-text "NOW" \
  --subtitle "manual focus"
```

This script writes only `focus.task`, `focus.big_text`, and `focus.subtitle`.
Do not pass notes, source URLs, transcripts, tokens, or raw task-manager
records into `widgets.json`.

Update only the low-sensitivity todo widget:

```bash
../scripts/update_todo.py \
  --title "Todo" \
  --item "Define todo crop contract" --tag "manual" \
  --item "Keep raw sources out" --tag "privacy"
```

This script writes only `todo.title` and up to five `todo.items[]` entries with
`text` and optional `tag`. Do not pass raw Reminders, Notion rows, source IDs,
URLs, completion history, transcripts, tokens, or raw logs into `widgets.json`.

Update only the low-sensitivity calendar widget:

```bash
../scripts/update_calendar.py \
  --event "09:30|Calendar crop contract|10:00" \
  --event "14:00|Keep raw events out|"
```

Each event is `START|TITLE|END`; `END` may be empty. The script writes only
`calendar.now_iso` and up to four events with `start`, `title`, and optional
`end`. Do not pass raw Calendar or Google Calendar records, locations,
attendees, meeting links, notes, calendar IDs, event IDs, transcripts, tokens,
or raw logs into `widgets.json`.

## Layout Checks

- `758x1024` viewport has no scrolling.
- `weather`, `ai-status`, `focus`, `ai-tasks`, `calendar`, and `todo` widgets render.
- Long content shows at most two lines with a visible ellipsis while full DOM
  text remains available.
- Primary content is centered; forecast, calendar, and todo rows remain
  left-aligned in stable columns.
- Text remains readable on an e-ink display.
- No animations or firmware/daemon dependencies are required.

## Deployment

The live deployment uses HTTPS Basic Auth. Keep source tokens and raw private
data out of `widgets.json`; only write the fields needed for rendering.
