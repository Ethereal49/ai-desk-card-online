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

## Update Demo Data

Generate a complete public-demo `widgets.json`:

```bash
../scripts/web_update.py --focus "Review the AI desk card" --todo "Keep data public"
```

This script is for resetting the full demo payload.

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
  --event "09:30|Deep work|11:00" \
  --event "14:00|Project checkpoint|"
```

This script writes only `calendar.now_iso` and up to four calendar events with
`start`, `title`, and optional `end`. Do not pass raw Calendar or Google
Calendar records, locations, attendees, meeting links, notes, calendar IDs,
event IDs, transcripts, tokens, or raw logs into `widgets.json`.

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
- Text remains readable on an e-ink display.
- No animations or firmware/daemon dependencies are required.

## Deployment

The live deployment uses HTTPS Basic Auth. Keep source tokens and raw private
data out of `widgets.json`; only write the fields needed for rendering.
