# Deployment Security

Phase 1.5 is not complete until the live server passes these checks.

The user currently wants direct public-IP access instead of a domain. That means
the IP-only path is for public demo data only. Do not enable Basic Auth over
plain HTTP, and do not put private data in `widgets.json`.

## Current Live Snapshot

Checked against `myecs` / `112.74.73.134` on 2026-05-31:

- SSH alias `myecs` works with `ecs-user`, port `2222`, and passwordless sudo.
- Caddy is installed as `v2.11.3`, active, and enabled.
- Live `/etc/caddy/Caddyfile` uses the shape in `deploy/caddy/Caddyfile.ip-https.example`: `:80` only serves ACME challenge files and redirects to HTTPS; `:443` serves `/srv/ai-desk-card-online` behind Basic Auth.
- Backup before applying IP-only hardening: `/etc/caddy/Caddyfile.ai-desk-card-online.20260531004653.bak`.
- Live Caddy currently has `Cache-Control: no-store`, CSP, `Referrer-Policy`, `X-Content-Type-Options`, and file blocking for non-runtime files.
- Public `http://112.74.73.134/` redirects to HTTPS.
- Unauthenticated `https://112.74.73.134/` and `/widgets.json` return `401`.
- Authenticated `https://112.74.73.134/` and `/widgets.json` return `200` with a Let's Encrypt shortlived IP certificate.
- Authenticated `/README.md`, `/widgets.example.json`, and path traversal probes return `404`.
- Public browser check at `758x1024`: `scrollHeight=1024`, `clientHeight=1024`, and all four Phase 1 widgets render.
- `/srv/ai-desk-card-online` currently contains `README.md`, `widgets.example.json`, and runtime web files.
- Non-project ports are intentionally out of scope for this phase.

The template in `deploy/caddy/Caddyfile.example` dry-run validates on the live Caddy version when supplied with placeholder environment variables and `--adapter caddyfile`.

For the current IP-only deployment, use `deploy/caddy/Caddyfile.ip-only.example`
to reduce accidental file exposure. This does not satisfy the private-data gate.

For IP HTTPS without a domain, use `deploy/caddy/Caddyfile.ip-https.example`.
The live server uses a Let's Encrypt IP address certificate issued with
Certbot `5.6.0` and `--preferred-profile shortlived`. The current certificate
expires on `2026-06-07`; Certbot renewal is configured and a deploy hook copies
renewed certs into `/etc/caddy/certs/ai-desk-card-online/` before reloading Caddy.
Because some clients do not send SNI for IP addresses, the HTTPS Caddy server
listens on `:443` with an explicit certificate instead of using
`https://112.74.73.134` as the site label.

The live HTTPS site is protected with Caddy Basic Auth. The username is `desk`;
the generated password is not committed to this repository.

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

To dry-run this repository template before installing it:

```bash
HASH=$(caddy hash-password --plaintext 'dry-run-password')
ACME_EMAIL=you@example.com \
AI_DESK_CARD_DOMAIN=card.example.com \
AI_DESK_CARD_WEB_ROOT=/srv/ai-desk-card-online \
AI_DESK_CARD_AUTH_USER=desk \
AI_DESK_CARD_AUTH_HASH="$HASH" \
caddy validate --adapter caddyfile --config deploy/caddy/Caddyfile.example
```

For the current IP HTTPS + Basic Auth deployment:

```bash
HASH=$(caddy hash-password --plaintext 'replace-with-live-password')
AI_DESK_CARD_AUTH_USER=desk \
AI_DESK_CARD_AUTH_HASH="$HASH" \
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
```

Expected after reload:

```bash
curl -I http://112.74.73.134/
curl -I http://112.74.73.134/widgets.json
curl -I https://112.74.73.134/
curl -I https://112.74.73.134/widgets.json
curl -I -u desk:'replace-with-the-password' https://112.74.73.134/
curl -I -u desk:'replace-with-the-password' https://112.74.73.134/widgets.json
```

Expected: HTTP returns redirect; unauthenticated HTTPS returns `401`;
authenticated `/` and `/widgets.json` return `200`; security headers are present.

You can re-run the HTTP redirect gate from this repo:

```bash
deploy/scripts/verify_ip_only.sh
```

You can re-run the IP HTTPS Basic Auth gate from this repo after exporting the
live password:

```bash
export AI_DESK_CARD_AUTH_USER=desk
export AI_DESK_CARD_AUTH_PASSWORD='replace-with-live-password'
deploy/scripts/verify_ip_https.sh
```

To update the live public demo data without restarting Caddy:

```bash
scripts/web_update.py --focus "Phase 2 public demo update"
scp web/widgets.json myecs:/tmp/ai-desk-card-widgets.json
ssh myecs 'sudo install -o root -g root -m 0644 /tmp/ai-desk-card-widgets.json /srv/ai-desk-card-online/widgets.json'
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
