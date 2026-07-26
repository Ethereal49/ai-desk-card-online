# Deployment And Operator Guide

This guide deploys the static dashboard without changing its HTML/CSS/vanilla
JavaScript architecture. Commands that install files, reload services, or
publish widgets mutate a live system; inspect them and substitute your own
host, address, paths, and credentials before running them.

## Security Boundary

Choose one exposure model:

1. **Domain HTTPS + Basic Auth** — recommended for private widgets. Use
   `caddy/Caddyfile.example`.
2. **Public-IP HTTPS + Basic Auth** — advanced path for a client-compatible IP
   certificate. Use `caddy/Caddyfile.ip-https.example`.
3. **Plain HTTP public demo** — synthetic or intentionally public data only.
   Use `caddy/Caddyfile.ip-only.example`. Basic Auth is deliberately absent
   because HTTP would expose the password.

The browser is not an authorization boundary. Do not place real calendar,
todo, focus, task, or quota text on an unauthenticated deployment.

All Caddy examples expose only runtime web assets and block repository files.
They require `Cache-Control: no-store`, a restrictive CSP, referrer protection,
and content-type protection. HTTPS examples also require server-side Basic
Auth.

## Reference Paths And Inputs

The checked-in deployment contracts use these canonical Linux paths:

```text
static runtime root: /srv/ai-desk-card-online
portable scripts:    /opt/ai-desk-card-online
shared widget lock:  /run/lock/ai-desk-card-widgets.lock
widget backups:      /srv/ai-desk-card-online.backups
```

Use environment variables for machine-specific values:

```bash
export AI_DESK_CARD_SSH_HOST=card-host
export AI_DESK_CARD_WEB_ROOT=/srv/ai-desk-card-online
export AI_DESK_CARD_DOMAIN=card.example.com
export AI_DESK_CARD_PUBLIC_IP=203.0.113.10
```

`203.0.113.10` is a documentation-only TEST-NET address. Replace it with your
real public IP; do not copy it into a live certificate request.

## Install Static Files

Install only the contents needed by the browser:

```text
index.html
styles.css
app.js
favicon.svg
widgets.json
```

Keep the Git repository, `README.md`, `widgets.example.json`, credentials,
certificate material, and source configuration outside the public runtime
root. Make the runtime files readable by Caddy and keep `widgets.json` at mode
`0644` after atomic updates.

## Domain HTTPS With Caddy

`caddy/Caddyfile.example` requires Caddy 2.8 or newer because it uses
`basic_auth`.

Generate a password hash on the server:

```bash
caddy hash-password --plaintext 'replace-with-a-long-password'
```

Provide the Caddy service with:

```text
ACME_EMAIL=operator@example.com
AI_DESK_CARD_DOMAIN=card.example.com
AI_DESK_CARD_WEB_ROOT=/srv/ai-desk-card-online
AI_DESK_CARD_AUTH_USER=desk
AI_DESK_CARD_AUTH_HASH=<caddy-password-hash>
```

Validate a candidate before installing or reloading it:

```bash
AI_DESK_CARD_AUTH_HASH="$(caddy hash-password --plaintext 'dry-run-only')" \
ACME_EMAIL=operator@example.com \
AI_DESK_CARD_DOMAIN=card.example.com \
AI_DESK_CARD_WEB_ROOT=/srv/ai-desk-card-online \
AI_DESK_CARD_AUTH_USER=desk \
caddy validate --adapter caddyfile --config deploy/caddy/Caddyfile.example
```

Installing the candidate and reloading Caddy are explicit operator actions and
are not performed by repository tests.

## Public-IP HTTPS

`caddy/Caddyfile.ip-https.example` assumes an externally provisioned
certificate pair at:

```text
/etc/caddy/certs/ai-desk-card-online/fullchain.pem
/etc/caddy/certs/ai-desk-card-online/privkey.pem
```

The template requires:

```text
AI_DESK_CARD_WEB_ROOT=/srv/ai-desk-card-online
AI_DESK_CARD_AUTH_USER=desk
AI_DESK_CARD_AUTH_HASH=<caddy-password-hash>
```

It listens explicitly on `:80` and `:443`, disables Caddy automatic HTTPS,
serves `/.well-known/acme-challenge/*` before redirecting HTTP, and uses the
explicit certificate pair on HTTPS.

If Certbot manages a short-lived IP certificate, the durable renewal chain is:

```text
Snap renewal timer
  -> webroot HTTP-01 challenge
  -> renewed lineage
  -> root-owned deploy hook
  -> Caddy certificate directory
  -> Caddy reload
```

Certificate issuer, SAN, validity, client support, Certbot version, scheduler
timestamps, and last service result are runtime facts. Recheck them; do not
copy an observed value into durable configuration.

Read-only public checks:

```bash
openssl s_client \
  -connect "${AI_DESK_CARD_PUBLIC_IP}:443" \
  -servername "${AI_DESK_CARD_PUBLIC_IP}" </dev/null 2>/dev/null \
  | openssl x509 -noout -issuer -dates -ext subjectAltName

curl -sS --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'http_root=%{http_code}\n' \
  "http://${AI_DESK_CARD_PUBLIC_IP}/"
curl -sS --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'http_missing_acme=%{http_code}\n' \
  "http://${AI_DESK_CARD_PUBLIC_IP}/.well-known/acme-challenge/read-only-missing-probe"
curl -sS --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'https_root_unauthenticated=%{http_code}\n' \
  "https://${AI_DESK_CARD_PUBLIC_IP}/"
```

Expected: an in-validity certificate whose SAN contains the public IP, an HTTP
redirect for `/`, `404` for a missing unauthenticated challenge file, and `401`
for unauthenticated HTTPS.

For a Snap installation, inspect the scheduler without invoking renewal:

```bash
ssh "$AI_DESK_CARD_SSH_HOST" \
  'systemctl is-enabled snap.certbot.renew.timer &&
   systemctl is-active snap.certbot.renew.timer &&
   systemctl show snap.certbot.renew.timer \
     --property=LastTriggerUSec \
     --property=NextElapseUSecRealtime --no-pager &&
   systemctl show snap.certbot.renew.service \
     --property=Result --property=ExecMainStatus --no-pager'
```

Do not print the private key, ACME account data, Basic Auth hash/password, full
live Caddyfile, or complete renewal environment. A documentation audit must not
run `certbot renew`, a deploy hook, or a service reload.

## Executable HTTP/HTTPS Gates

The repository verification scripts have no live address defaults and fail
before `curl` when required inputs are missing.

Public HTTP redirect gate:

```bash
AI_DESK_CARD_URL="http://${AI_DESK_CARD_PUBLIC_IP}" \
  deploy/scripts/verify_ip_only.sh
```

Authenticated public-IP HTTPS gate:

```bash
export AI_DESK_CARD_BASE_URL="https://${AI_DESK_CARD_PUBLIC_IP}"
export AI_DESK_CARD_IP="$AI_DESK_CARD_PUBLIC_IP"
export AI_DESK_CARD_AUTH_USER=desk
export AI_DESK_CARD_AUTH_PASSWORD='<live-password>'
deploy/scripts/verify_ip_https.sh
```

The HTTPS gate checks redirects, unauthenticated `401`, authenticated runtime
`200`, authenticated non-runtime/path-probe `404`, security headers, TLS
verification, and IP SAN. The password is accepted only through the caller's
environment and must not be committed or logged.

## Real-Data Publisher

The Mac-side publisher owns `ai-status`, `focus`, `ai-tasks`, `calendar`, and
`todo`; the server weather timer owns `weather`.

Required local configuration:

```text
LINEAR_API_KEY=<read-only key>
AI_DESK_CARD_CALENDARS=["Work","Personal"]
AI_DESK_CARD_SSH_HOST=card-host
```

The first two values may live in ignored mode-`0600` `.env.local`.
`AI_DESK_CARD_SSH_HOST` must be exported or provided with `--host` for remote
preview/publish.

Run each boundary explicitly:

```bash
scripts/refresh_dashboard.py --source-check
scripts/refresh_dashboard.py --preview
scripts/refresh_dashboard.py --publish
```

- `--source-check` never contacts the publish host.
- `--preview` reads the live baseline, merges projected data, resolves Focus,
  validates the full document, and performs no write.
- `--publish` transfers only the five locally owned widgets to a unique
  temporary directory.
- `scripts/install_widgets.py` acquires the shared lock, re-reads the live
  document, preserves weather, creates a changed-only mode-`0600` backup,
  installs mode `0644` atomically, verifies, and restores after a failed
  post-install check.

Routine output contains only source health, changed widget types, bounded
reasons, and publish status. It must not contain source titles, calendar names,
paths, raw JSON, or credentials.

## Focus Configuration

The optional private Focus config defaults to:

```text
~/.config/ai-desk-card-online/focus.json
```

Use the shared validation CLI:

```bash
scripts/configure_focus.py get
scripts/configure_focus.py set --source calendar.next
scripts/configure_focus.py set --source manual --task "Private local focus"
scripts/configure_focus.py reset
```

Allowed sources are `todo.first`, `calendar.next`, `ai-status.task`,
`weather.current`, and `manual`. The CLI keeps the directory at `0700`, writes
the file atomically at `0600`, reports only source/field-presence flags, and
does not preview, publish, use SSH, or restart a scheduler.

## macOS LaunchAgent

The credential-free example runs a bounded publish every 300 seconds. Create
the local file from the neutral template:

```bash
repo_root="$(pwd -P)"
launch_agent="$HOME/Library/LaunchAgents/com.example.ai-desk-card-refresh.plist"
mkdir -p "$(dirname "$launch_agent")"
sed \
  -e "s|/ABSOLUTE/PATH/TO/ai-desk-card-online|$repo_root|g" \
  -e "s|REPLACE_WITH_SSH_HOST|$AI_DESK_CARD_SSH_HOST|g" \
  deploy/launchd/com.example.ai-desk-card-refresh.plist.example \
  >"$launch_agent"
plutil -lint "$launch_agent"
```

Inspect the rendered file before loading it. It must contain no credentials.
Then use `launchctl bootstrap`, `kickstart`, `print`, or `bootout` according to
your macOS version and desired lifecycle. `scripts/run_scheduled_refresh.py`
bounds execution to 150 seconds and replaces a maximum 8192-byte mode-`0600`
status file at:

```text
~/Library/Logs/ai-desk-card-online/latest.log
```

## Server Weather Timer

Install `scripts/update_weather.py` and the shared contract under
`/opt/ai-desk-card-online/scripts/`, then configure:

```text
# /etc/default/ai-desk-card-online
AI_DESK_CARD_WEATHER_LOCATION="Your City"
```

The checked-in systemd service uses the same
`/run/lock/ai-desk-card-widgets.lock` as publication and updates only weather.
The timer runs every 30 minutes. A source failure preserves the previous
weather values and marks only the weather widget stale.

Validate unit content before enabling it. Enabling, starting, or running the
service is a live mutation and remains an explicit operator action.

## Acceptance And Rollback

Before declaring a private deployment usable:

- unauthenticated runtime paths return `401`;
- authenticated `/` and `/widgets.json` return `200`;
- authenticated repository/non-runtime/path-probe requests return `404`;
- required security headers are present;
- the certificate is valid for the requested hostname or IP;
- the `758x1024` browser page has no scroll and renders all six widgets;
- no credential or forbidden private field appears in `widgets.json`;
- publisher and weather updates share the same lock.

Stop the scheduler before maintenance. Restore the newest verified widget
backup under the shared lock if publication validation fails. Validate a Caddy
rollback candidate before reload. Never make a live system change solely to
turn a documentation or repository check green.
