# Component Guidelines

## Component Model

There is no component framework. A frontend component consists of:

- a semantic mount element in `web/index.html`;
- a focused `render<Type>(widget)` function in `web/app.js`;
- role-specific selectors in `web/styles.css`;
- an example payload in `web/widgets.example.json`.

Keep this four-part contract synchronized when a widget changes.

## Rendering

- Read missing objects with defensive defaults such as `widget.data || {}`.
- Render explicit fallback text rather than leaving a region blank.
- Escape every data-derived string with `escapeHtml` before assigning
  `innerHTML`.
- Cap lists in the renderer even when the producer also enforces limits.
- Keep renderer functions deterministic and free of data fetching.

`renderWeather`, `renderAiStatus`, `renderCalendar`, and `renderTodo` are the
reference implementations.

## Styling

- Preserve the fixed `758x1024` card and stable grid dimensions.
- Use high contrast, large text, fixed bounds, and explicit overflow behavior.
- No animation, transitions, gradients, hover-only behavior, or decorative
  shadows.
- Cards are only the actual widgets; do not nest decorative cards.

## Accessibility

- Use semantic `header`, `section`, `article`, `footer`, `time`, and headings.
- Give widget regions `aria-label` values.
- Keep decorative checkbox marks `aria-hidden="true"`.
- Do not depend on color alone; freshness also has visible text.

## Common Mistakes

- Writing unescaped JSON fields into `innerHTML`.
- Adding content that forces scrolling at `758x1024`.
- Changing CSS without updating the static contract test and Browser gate.
