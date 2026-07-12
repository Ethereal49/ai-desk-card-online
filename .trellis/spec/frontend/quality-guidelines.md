# Frontend Quality Guidelines

## Non-Negotiable Acceptance Criteria

- The target viewport is exactly `758x1024`.
- `scrollHeight <= clientHeight` and `scrollWidth <= clientWidth`.
- All six widget regions render without internal overflow or overlap.
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
server and use the Codex built-in Browser at `758x1024`.

## Review Checklist

- Does every new data string pass through `escapeHtml`?
- Are list counts bounded in both producer and renderer where applicable?
- Can the longest expected text fit or truncate coherently?
- Did the fixed row or column values change? If so, was the static contract
  test updated intentionally?
- Was the failed-fetch path checked after the normal path?
- Was real device behavior kept as the final authority over simulated layout?

## Accessibility And E-Ink

- Maintain semantic regions and labels.
- Keep contrast high and text large enough for 30-50 cm viewing.
- Avoid large rapidly changing dark regions and layout movement.
- Treat the page as an ambient display, not an interactive dashboard.
