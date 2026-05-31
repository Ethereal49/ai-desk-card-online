# AI Desk Card Web

Static MVP for a `758x1024` e-ink browser dashboard.

## Run

```bash
cd web
python3 -m http.server 4173
```

Open:

```text
http://127.0.0.1:4173/
```

## Data

- Runtime data: `widgets.json`
- Example data: `widgets.example.json`
- Refresh interval defaults to `300` seconds.

The page keeps the last rendered data if refresh fails and marks the footer as offline.

## Update Demo Data

Generate a complete public-demo `widgets.json`:

```bash
../scripts/web_update.py --focus "Review the AI desk card" --todo "Keep data public"
```

This script is for resetting the full demo payload.

Update the Phase 3 weather widget from the public wttr.in flow:

```bash
../scripts/update_weather.py --location Shenzhen
```

The weather updater preserves the other widgets. If the public weather source
fails, it keeps the previous weather values and marks only the weather widget
as stale.

## Phase 1 Checks

- `758x1024` viewport has no scrolling.
- `focus`, `weather`, `calendar`, and `todo` widgets render.
- Text remains readable on an e-ink display.
- No animations or firmware/daemon dependencies are required.

## Deployment

The live deployment uses HTTPS Basic Auth. Keep source tokens and raw private
data out of `widgets.json`; only write the fields needed for rendering.
