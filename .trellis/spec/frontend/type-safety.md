# Data And Type Safety

## Current Language Boundary

The browser code is plain JavaScript and has no TypeScript build step. Type
safety comes from a small JSON contract, defensive normalization, escaping,
and tests. Do not add TypeScript tooling without changing `PLAN_web.md`.

## Defensive Rules

- Normalize nullable objects with `value || {}` and arrays with `value || []`.
- Convert numeric display values with `Number` and validate with `isFinite`.
- Treat invalid timestamps as infinitely old.
- Provide visible fallback strings for missing fields.
- Escape all data-derived HTML.
- Limit loops to the supported display count.

Examples in `web/app.js` include `widgetByType`, `minutesSince`,
`formatContext`, `formatQuotaWindow`, and `formatCount`.

## Contract Synchronization

When a field changes, inspect and update all relevant surfaces:

- `web/widgets.example.json`;
- fallback data and renderer in `web/app.js`;
- producer in `scripts/update_*.py`;
- contract or updater tests in `scripts/test_*.py`;
- `PLAN_web.md` if the stable contract or product boundary changes.

## Forbidden Patterns

- Directly interpolating untrusted strings into HTML.
- Assuming a widget or nested field always exists.
- Treating numeric-looking strings as valid without conversion checks.
- Adding a second incompatible schema alongside the existing contract.
