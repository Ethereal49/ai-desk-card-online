# Frontend Directory Structure

## Current Layout

The frontend is a static application owned entirely by `web/`:

```text
web/
  index.html             # fixed semantic shell and widget mount points
  styles.css             # all layout and e-ink presentation rules
  app.js                 # data loading, formatting, and rendering
  widgets.json           # runtime data
  widgets.example.json   # documented example contract
  favicon.svg
  README.md
```

## Rules

- Keep the MVP HTML/CSS/vanilla JavaScript with no build step.
- Do not add React, Vite, Astro, TypeScript tooling, npm dependencies, or a
  component directory unless `PLAN_web.md` changes first.
- Keep fixed widget mount points in `index.html`; add rendering behavior to
  `app.js` and presentation to `styles.css`.
- Keep generated screenshots and Browser QA artifacts under `output/`, never
  under `web/`.
- Future server code belongs in `web-server/`, not in the static frontend.

## Naming

- Widget element IDs use `widget-<type>`.
- Renderer functions use `render<Type>`.
- CSS classes describe stable roles such as `glance-row`, `focus-widget`, and
  `item-row`, not transient visual experiments.

## Examples

- `web/index.html`: the six fixed semantic widget regions.
- `web/app.js`: one renderer per widget type.
- `web/styles.css`: the exact `758x1024` grid and overflow constraints.
