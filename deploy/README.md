# Deployment Security

Phase 1.5 is not complete until the live server passes these checks.

## Server Boundary

- Only expose confirmed public ports. The desk card site normally needs `80` and `443`.
- Keep one SSH management port only, and restrict it by source IP when possible.
- Close or internalize unrelated Docker, 1Panel, database, and temporary service ports.
- Do not put real calendar, todo, message, token, or focus data in `web/widgets.json` before HTTPS and access control pass.

## Caddy Setup

Use `deploy/caddy/Caddyfile.example` as the template. It requires Caddy `2.8+` because the current directive name is `basic_auth`.

Generate the Basic Auth hash on the server:

```bash
caddy hash-password --plaintext 'replace-with-a-long-password'
```

Set environment variables for the Caddy service:

```text
ACME_EMAIL=you@example.com
AI_DESK_CARD_DOMAIN=card.example.com
AI_DESK_CARD_WEB_ROOT=/var/www/ai-desk-card-online/web
AI_DESK_CARD_AUTH_USER=desk
AI_DESK_CARD_AUTH_HASH=<hash-from-caddy-hash-password>
```

Validate before reload:

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
```

## Acceptance Checks

Unauthenticated requests must not reveal content:

```bash
curl -I https://card.example.com/
curl -I https://card.example.com/widgets.json
```

Expected: `401 Unauthorized`.

Authenticated runtime files must load:

```bash
curl -I -u desk:'replace-with-the-password' https://card.example.com/
curl -I -u desk:'replace-with-the-password' https://card.example.com/widgets.json
```

Expected: `200 OK`, `Cache-Control: no-store`, and the configured security headers.

Non-runtime files must not be public:

```bash
curl -I -u desk:'replace-with-the-password' https://card.example.com/README.md
curl -I -u desk:'replace-with-the-password' https://card.example.com/widgets.example.json
```

Expected: `404 Not Found`.

Path traversal probes must not reveal files:

```bash
curl -I -u desk:'replace-with-the-password' https://card.example.com/../PLAN_web.md
curl -I -u desk:'replace-with-the-password' https://card.example.com/%2e%2e/PLAN_web.md
```

Expected: no file content returned.

After deployment, verify the browser page again at `758x1024` and confirm no scroll.
