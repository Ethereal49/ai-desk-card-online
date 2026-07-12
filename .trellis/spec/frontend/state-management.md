# State Management

## Current State Model

State is intentionally small and module-global in `web/app.js`:

- `fallbackData`: complete renderable startup data.
- `lastData`: last successfully parsed runtime document.
- `refreshTimer`: active refresh interval handle.
- `elements`: cached DOM mount points.

Do not add a state library, local storage, IndexedDB, or client-side data model
for the static MVP.

## Source Of Truth

- `web/widgets.json` is runtime truth.
- The UI derives widget state by `type`, not array position.
- Missing widgets resolve to `{ type, data: {} }` and render fallbacks.
- Freshness derives from top-level `updated_at`; fetch failure overrides it to
  offline.
- Widget-specific stale state remains inside that widget's data.

## Update Rules

- A successful load replaces `lastData` only after JSON parsing succeeds.
- A failed load keeps prior content and changes status presentation only.
- Renderer functions must not mutate the loaded document.
- Producers, not the browser, own cropping and privacy filtering.

## Forbidden Patterns

- Clearing `lastData` before a request completes.
- Coupling rendering to widget array order.
- Persisting private runtime data in browser storage.
- Adding interactive state that conflicts with the ambient-display product.
