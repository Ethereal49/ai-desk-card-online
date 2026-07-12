# Lifecycle And Data Loading Guidelines

## No Framework Hooks

This project does not use React or custom hooks. Do not introduce hook
abstractions. Page lifecycle is explicit at the bottom of `web/app.js`.

## Initialization Order

1. Format the clock.
2. Scale and center the fixed card for the available viewport.
3. Render `fallbackData` immediately.
4. Load `widgets.json`.
5. Start refresh and clock intervals.
6. Recompute scale on resize.

## Data Loading

- Use a cache-busting timestamp on `widgets.json` requests.
- Keep `lastData` as the last successfully parsed document.
- On HTTP, parse, or send failure, render `lastData` with offline state.
- Never blank the page while loading or after a failed refresh.
- Clamp refresh intervals to at least 30 seconds.

The current implementation uses `XMLHttpRequest` for compatibility with the
target device browser. Do not replace it with `fetch` without a real device
compatibility reason and an updated plan.

## Timing Rules

- Dashboard data uses `refresh_seconds`, defaulting to 300 seconds.
- The clock updates every 30 seconds.
- No animation frames, polling loops, or event streams are allowed.
