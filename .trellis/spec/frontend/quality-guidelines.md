# Frontend Quality Guidelines

## Non-Negotiable Acceptance Criteria

- The target viewport is exactly `758x1024`.
- `scrollHeight <= clientHeight` and `scrollWidth <= clientWidth`.
- All six widget regions render without internal overflow or overlap.
- Source/user prose keeps its complete JSON/DOM value and renders at no more
  than two visual lines with a visible ellipsis when it exceeds that bound.
- Normal data renders up to five todo rows and four calendar rows. Whole-row
  removal is only a final widget-overflow guard and must report the truthful
  `selected/total` count.
- Missing fields and failed `widgets.json` requests do not blank the page.
- The failed-fetch state retains content and visibly reports `offline`.
- There are no animations, transitions, gradients, hover-only controls, or
  decorative shadows.

## Verification

Run:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

`scripts/test_web_static_contract.py` protects the schema-to-DOM-to-CSS
contract. After any layout or rendering change, serve `web/` with a static
server and use the Codex built-in Browser at `758x1024`. Long English, Chinese,
and unbroken-token fixtures must verify the two-line computed clamp, visible
ellipsis, complete DOM value, row counts, and page/widget geometry at
`758x1024`, `740x951`, and `467x600`; the physical device remains the final
authority.

## Review Checklist

- Does every new data string pass through `escapeHtml`?
- Are list counts bounded in both producer and renderer where applicable?
- Does long prose retain its complete DOM value while using the shared two-line
  clamp, including Chinese and unbroken tokens?
- Are centered primary regions visually balanced while list prose remains
  left-aligned and column-comparable?
- Did the fixed row or column values change? If so, was the static contract
  test updated intentionally?
- Was the failed-fetch path checked after the normal path?
- Was real device behavior kept as the final authority over simulated layout?

## Accessibility And E-Ink

- Maintain semantic regions and labels.
- Keep contrast high and text large enough for 30-50 cm viewing.
- Avoid large rapidly changing dark regions and layout movement.
- Treat the page as an ambient display, not an interactive dashboard.
