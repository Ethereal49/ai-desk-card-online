# Phase 6 Configurable Focus And Visual Alignment Design

## Design Summary

Phase 6 keeps `widgets.json` as the sole browser contract. It adds one bounded
local Focus configuration and one pure resolver between source merging and
document validation. The browser continues to receive ordinary Focus data; it
does not know which source was selected. Long content remains complete in JSON
and the DOM, while reusable CSS line-clamp classes control the fixed display.

## Data Flow

```text
Linear -> todo -----------------------+
Calendar -> calendar ----------------+|
Codex -> ai-status / ai-tasks -------||
live baseline -> weather ------------||
                                      vv
                         merge source/LKG widgets
                                      |
local focus.json -> validate -> resolve allowlisted Focus projection
                                      |
                         validate complete widgets.json
                                      |
                   preview or locked atomic publish
                                      |
                         static browser presentation
                                      |
                      two-line visual clamping only
```

There is no second runtime format and no browser-side source routing.

## Focus Configuration Contract

Default path:

```text
~/.config/ai-desk-card-online/focus.json
```

The refresh CLI accepts `--focus-config` so tests can use temporary files. A
missing default file means:

```json
{"source": "todo.first"}
```

A present file must be a regular, bounded UTF-8 JSON object. The allowed shape
is:

```json
{
  "source": "todo.first | calendar.next | ai-status.task | weather.current | manual",
  "task": "required only for manual",
  "subtitle": "optional override",
  "big_text": "optional override"
}
```

Unknown keys and selectors are rejected. The implementation uses the existing
Focus field length bounds and privacy-key rejection. The example is tracked at
`deploy/focus.example.json`; the live file stays outside the repository and is
never transferred to the server. Documentation installs it with mode `0600`.

## Resolver Contract

The resolver consumes only the already projected widget map:

| Source | Task | Default big text | Default subtitle |
| --- | --- | --- | --- |
| `todo.first` | first todo text or explicit empty state | `NOW` / `CLEAR` | `Todo priority` |
| `calendar.next` | first event title or explicit empty state | event start / `CLEAR` | `Next event` |
| `ai-status.task` | projected AI task | `AI` | projected model |
| `weather.current` | projected condition | formatted temperature | projected location |
| `manual` | configured task | configured value or `FOCUS` | configured value or `Manual` |

Optional overrides replace only `big_text` and `subtitle`. Linked values are
copied, never referenced by an arbitrary path. The result contains only the
existing Focus fields plus the common source/freshness fields.

Focus resolution happens after `merge_source_results` and quota merge, so a
recoverable source failure first restores the source widget's last-known-good
data and marks it stale. The resolver then propagates that stale state and the
source timestamp into Focus. A configuration error is different: it aborts
before baseline SSH, candidate creation, or publication.

The Linear adapter stops owning Focus. This removes two competing definitions
of the headline and makes the resolver the only owner of source selection.

## Presentation Contract

A shared two-line class uses the browser's line clamp support with a bounded
height and overflow fallback. It is applied only to source/user prose:

- Focus task;
- AI session/task prose;
- weather condition and forecast condition;
- calendar and todo row content.

The renderer keeps the original escaped text nodes and supplies full accessible
labels where a composite row includes secondary text. It does not slice strings
or mutate loaded data. Known-short metadata stays one line.

The list row clamp covers the combined main text and tag so a row occupies at
most two lines. Five normal todo rows must fit without the existing removal
fallback. If malformed or future content still overflows the fixed widget after
compact spacing, the existing whole-row removal remains the final safety net
and selected/total remains visible.

## Alignment System

- Replace top-bar floats with a two-column grid and center both blocks
  vertically.
- Give every widget header one shared fixed height, centered cross-axis, and
  consistent divider/padding.
- Center Focus and AI-status primary regions without centering list prose.
- Center weather's primary temperature/condition group as one balanced unit.
- Keep forecast, calendar, and todo in stable grid columns with consistent row
  height and baseline.
- Render AI task counts as a flat 2x2 metric grid with shared separators rather
  than four rounded nested cards.
- Replace fixed footer label widths with a three-column grid: source left,
  refresh center, status right.
- Preserve the fixed card rows and automatic scale transform. Font sizes remain
  fixed design tokens rather than viewport-based values.

## Failure And Compatibility Matrix

| Condition | Behavior |
| --- | --- |
| Focus config absent | Use `todo.first`; no warning or publish failure. |
| Focus config malformed/unknown | Redacted fatal configuration status before SSH. |
| Linked source stale | Resolve from its LKG data and mark Focus stale. |
| Linked list empty | Render explicit empty Focus state. |
| Manual text invalid | Redacted fatal configuration status before SSH. |
| CSS line clamp unsupported | Bounded height and hidden overflow prevent geometry break; compatibility test records whether visible ellipsis is supported on the target browser. |
| Text still causes widget overflow | Apply compact class, then remove only lowest-priority list rows as final guard. |
| Browser fetch fails | Existing last-rendered/fallback data and offline state remain unchanged. |

## Rollout And Rollback

1. Validate locally with missing/default and temporary custom configurations.
2. Deploy the static bundle and publisher modules without installing a custom
   local Focus file; production therefore keeps `todo.first` by default.
3. Run one preview, publish, live geometry check, and subsequent natural
   LaunchAgent tick.
4. To roll back behavior, remove the optional local Focus file and restore the
   previous static bundle/publisher commit. Server JSON backups and the shared
   weather lock remain valid because the external widget schema is unchanged.

