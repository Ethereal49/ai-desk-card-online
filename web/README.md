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

This script is for public demo data only while the deployment uses plain HTTP.

## Phase 1 Checks

- `758x1024` viewport has no scrolling.
- `focus`, `weather`, `calendar`, and `todo` widgets render.
- Text remains readable on an e-ink display.
- No animations or firmware/daemon dependencies are required.

## Deployment

Before putting private data in `widgets.json`, finish Phase 1.5 in
`../deploy/README.md`: HTTPS, Basic Auth, blocked non-runtime files, security
headers, and public port cleanup.
