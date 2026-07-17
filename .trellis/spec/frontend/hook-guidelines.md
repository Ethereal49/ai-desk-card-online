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

## Viewport Fit Contract

### 1. Scope / Trigger

This contract applies when the fixed `758x1024` card must fit an e-ink browser
whose layout viewport and visible CSS viewport differ.

### 2. Signature

`applyViewportScale()` is the single sizing entry point. It runs at startup,
from `window.onresize`, and from `window.visualViewport.onresize` when the API
exists.

### 3. Contract

- Use `window.visualViewport.width/height` for fit calculations when available;
  fall back to `window.innerWidth/innerHeight` and then document client sizes.
- Reserve a 4px inset on viewports smaller than `758x1024`.
- Prefer CSS `zoom` so layout participates before an `overflow: hidden` clip;
  retain the existing transform fallback for browsers without `style.zoom`.
- The opt-in `?viewport=1` footer diagnostic displays the visual dimensions
  used by the fit algorithm. A device may report a larger layout viewport, such
  as `740x951`, and a smaller visual viewport, such as `467x600`.
- The normal URL must retain `source: widgets.json`.

### 4. Validation / Error Matrix

| Condition | Required behavior |
| --- | --- |
| `758x1024` viewport | `zoom=1`, no page scroll, full card visible |
| smaller visual viewport | scale down, keep 4px lower-edge inset |
| no `visualViewport` API | use inner/document fallback and transform |
| query flag absent | leave normal footer source label unchanged |
| resize or browser chrome change | recompute scale and diagnostic |

### 5. Good / Base / Bad Cases

- Good: use visual viewport + CSS zoom, then verify bottom border on device.
- Base: use inner viewport with transform fallback when visual viewport is
  unavailable.
- Bad: scale only from `innerWidth/innerHeight` and assume transformed content
  is clipped after transform in every browser.

### 6. Tests Required

- Static contract test asserts query gating, visual viewport path, zoom fallback,
  and the 4px inset.
- Browser gate checks normal and `?viewport=1` URLs at `758x1024`, `740x951`,
  and a smaller viewport, including page dimensions and footer output.
- Physical-device check confirms first-load fit and a visible lower border.

### 7. Wrong vs Correct

```javascript
// Wrong: device browser can clip the unscaled layout before transform.
var scale = Math.min(window.innerWidth / 758, window.innerHeight / 1024);
card.style.transform = "scale(" + scale + ")";

// Correct: size against the visible viewport and let layout-aware zoom run first.
var viewport = window.visualViewport;
var width = viewport ? viewport.width : window.innerWidth;
var height = viewport ? viewport.height : window.innerHeight;
var scale = Math.min((width - 4) / 758, (height - 4) / 1024);
if ("zoom" in card.style) card.style.zoom = scale;
```

**Why**: The physical device exposed `740x951` as its layout viewport but
`467x600` as its visual viewport. The old transform-only path required manual
pinch-out and clipped the lower border; the contract above fits the actual
visible area automatically.
