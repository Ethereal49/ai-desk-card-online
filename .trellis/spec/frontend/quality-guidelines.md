# Frontend Quality Guidelines

## Non-Negotiable Acceptance Criteria

- The target viewport is exactly `758x1024`.
- `scrollHeight <= clientHeight` and `scrollWidth <= clientWidth`.
- All six widget regions render without internal overflow or overlap.
- Source/user text renders completely without ellipsis or silent clipping.
- Normal data renders up to five todo rows and four calendar rows. At the
  physical readability floor, remove only lowest-ranked whole rows and report
  the truthful `selected/total` count.
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
and unbroken-token fixtures must also compare each supported text element's
`scrollWidth`/`scrollHeight` with its client dimensions at `758x1024`,
`740x951`, and `467x600`; the physical device remains the final authority.

## Review Checklist

- Does every new data string pass through `escapeHtml`?
- Are list counts bounded in both producer and renderer where applicable?
- Does expected text wrap completely, including unbroken tokens, without using
  `text-overflow: ellipsis`, `-webkit-line-clamp`, or hidden clipping?
- Did the fixed row or column values change? If so, was the static contract
  test updated intentionally?
- Was the failed-fetch path checked after the normal path?
- Was real device behavior kept as the final authority over simulated layout?

## Accessibility And E-Ink

- Maintain semantic regions and labels.
- Keep contrast high and text large enough for 30-50 cm viewing.
- Avoid large rapidly changing dark regions and layout movement.
- Treat the page as an ambient display, not an interactive dashboard.
