# Deployment Security

Phase 1.5 is not complete until the live server passes these checks.

The user currently wants direct public-IP access instead of a domain. Private
runtime data is allowed only on the current HTTPS + Basic Auth path. Plain HTTP
must remain redirect-only and unauthenticated HTTPS must return `401`.

## Deployment Evidence History

The following observations were checked against `myecs` / `112.74.73.134` on
the dates shown. They are evidence history, not a substitute for rerunning the
live gates below:

- SSH alias `myecs` works with `ecs-user`, port `2222`, and passwordless sudo.
- Caddy is installed as `v2.11.3`, active, and enabled.
- Live `/etc/caddy/Caddyfile` uses the shape in `deploy/caddy/Caddyfile.ip-https.example`: `:80` only serves ACME challenge files and redirects to HTTPS; `:443` serves `/srv/ai-desk-card-online` behind Basic Auth.
- Backup before applying IP-only hardening: `/etc/caddy/Caddyfile.ai-desk-card-online.20260531004653.bak`.
- Live Caddy currently has `Cache-Control: no-store`, CSP, `Referrer-Policy`, `X-Content-Type-Options`, and file blocking for non-runtime files.
- Public `http://112.74.73.134/` redirects to HTTPS.
- Unauthenticated `https://112.74.73.134/` and `/widgets.json` return `401`.
- Authenticated `https://112.74.73.134/` and `/widgets.json` return `200` with a Let's Encrypt shortlived IP certificate.
- Authenticated `/README.md`, `/widgets.example.json`, and path traversal probes return `404`.
- Public browser check at `758x1024` on 2026-05-31: `scrollHeight=1024`, `clientHeight=1024`, and all four Phase 1 widgets render.
- 2026-06-01 update: role-based runtime files have been synced to `/srv/ai-desk-card-online/` with `weather`, `ai-status`, `focus`, `ai-tasks`, `calendar`, and `todo` in `widgets.json`. Backup before this sync: `/srv/ai-desk-card-online.backups/web-before-role-20260601220821.tgz`.
- 2026-06-01 update: HTTPS Basic Auth gate passed after sync with `deploy/scripts/verify_ip_https.sh`: unauthenticated runtime and non-runtime paths return `401`, authenticated `/` and `/widgets.json` return `200`, authenticated non-runtime files and path traversal probes return `404`, required security headers are present, and TLS SAN contains `IP Address:112.74.73.134`.
- 2026-06-01 update: authenticated live Browser layout gate passed through a local temporary Basic Auth proxy to live HTTPS assets at `758x1024`: `scrollHeight=1024`, `clientHeight=1024`, and `weather`, `ai-status`, `focus`, `ai-tasks`, `calendar`, and `todo` render without detected internal overflow.
- 2026-06-01 update: low-sensitivity focus/todo/calendar smoke data was published to live `widgets.json` only after checking the local JSON field boundary. Backup before this JSON-only sync: `/srv/ai-desk-card-online.backups/widgets-before-smoke-20260601224034.json`.
- 2026-06-01 update: the post-smoke live gate passed: remote `widgets.json` contains only the six cropped display widgets, `deploy/scripts/verify_ip_https.sh` passed, and authenticated live Browser validation at `758x1024` reported `scrollHeight=1024`, `clientHeight=1024`, `scrollWidth=758`, `clientWidth=758`, all six widget labels present, and no detected internal overflow.
- `/srv/ai-desk-card-online` currently contains `README.md`, `widgets.example.json`, and runtime web files.
- 2026-07-23 Phase 5 UI cutover: the long-text/five-todo static bundle was
  backed up and installed with matching local/live hashes and mode `0644`.
  The weather service now uses `/run/lock/ai-desk-card-widgets.lock`; a manual
  oneshot returned `Result=success`, the timer stayed active, and weather stayed
  fresh. Real owned-widget publication remains gated on Calendar allowlist.
- Non-project ports are intentionally out of scope for this phase.

The template in `deploy/caddy/Caddyfile.example` dry-run validates on the live Caddy version when supplied with placeholder environment variables and `--adapter caddyfile`.

For the current IP-only deployment, use `deploy/caddy/Caddyfile.ip-only.example`
to reduce accidental file exposure. This does not satisfy the private-data gate.

For IP HTTPS without a domain, use `deploy/caddy/Caddyfile.ip-https.example`.
The live server uses a Let's Encrypt IP address certificate with Certbot's
`shortlived` profile. Because some clients do not send SNI for IP addresses,
the HTTPS Caddy server listens on `:443` with an explicit certificate instead
of using `https://112.74.73.134` as the site label. Caddy automatic HTTPS is
disabled for these explicit `:80` and `:443` listeners so the HTTP-01 route and
manually installed certificate remain unambiguous.

### IP Certificate Renewal

Certbot is installed through Snap on this host. The authoritative scheduler is
`snap.certbot.renew.timer`; a missing or inactive generic `certbot.timer` is not
a renewal failure for this installation. The durable renewal chain is:

```text
snap.certbot.renew.timer
  -> Certbot webroot HTTP-01 under /.well-known/acme-challenge/
  -> renewed Let's Encrypt lineage
  -> /etc/letsencrypt/renewal-hooks/deploy/ai-desk-card-online-ip-cert.sh
  -> /etc/caddy/certs/ai-desk-card-online/
  -> Caddy reload
```

Certificate dates, the Certbot version, timer timestamps, and service results
are runtime facts. Verify them instead of copying them into durable prose.
These public checks expose no credentials or private key material:

```bash
openssl s_client \
  -connect 112.74.73.134:443 \
  -servername 112.74.73.134 </dev/null 2>/dev/null \
  | openssl x509 -noout -issuer -dates -ext subjectAltName

curl -sS --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'http_root=%{http_code}\n' http://112.74.73.134/
curl -sS --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'http_missing_acme=%{http_code}\n' \
  http://112.74.73.134/.well-known/acme-challenge/read-only-missing-probe
curl -sS --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'https_root_unauthenticated=%{http_code}\n' https://112.74.73.134/
```

Expected invariants: the certificate issuer is Let's Encrypt, SAN contains
`IP Address:112.74.73.134`, the current time is within the reported validity
interval, HTTP `/` redirects, a nonexistent challenge file returns `404`
without redirecting, and unauthenticated HTTPS returns `401`.

Use bounded remote checks for the scheduler and renewal profile:

```bash
ssh myecs 'systemctl is-enabled snap.certbot.renew.timer'
ssh myecs 'systemctl is-active snap.certbot.renew.timer'
ssh myecs 'systemctl show snap.certbot.renew.timer \
  --property=LastTriggerUSec --property=NextElapseUSecRealtime --no-pager'
ssh myecs 'systemctl show snap.certbot.renew.service \
  --property=Result --property=ExecMainStatus --no-pager'
ssh myecs 'certbot --version'
ssh myecs "sudo awk -F ' *= *' \
  '/^(authenticator|preferred_profile|webroot_path) *=/ {print}' \
  /etc/letsencrypt/renewal/112.74.73.134.conf"
```

Expected invariants: the Snap timer is enabled and active, a future execution
is scheduled, the most recent renewal service has `Result=success` and
`ExecMainStatus=0`, and the renewal config uses `shortlived` plus `webroot` at
`/srv/ai-desk-card-online`.

Inspect the deploy boundary without printing either file's contents:

```bash
ssh myecs 'sudo stat -c "%U:%G %a %n" \
  /etc/letsencrypt/renewal-hooks/deploy/ai-desk-card-online-ip-cert.sh; \
  sudo bash -n \
  /etc/letsencrypt/renewal-hooks/deploy/ai-desk-card-online-ip-cert.sh'
ssh myecs 'hook=/etc/letsencrypt/renewal-hooks/deploy/ai-desk-card-online-ip-cert.sh; \
  sudo grep -Eq "install .*0644.*fullchain" "$hook" \
    && echo hook_fullchain_mode=0644; \
  sudo grep -Eq "install .*0600.*privkey" "$hook" \
    && echo hook_private_key_mode=0600; \
  sudo grep -Eq "systemctl +reload +caddy" "$hook" \
    && echo hook_reload_caddy=present'
ssh myecs 'sudo stat -c "%U:%G %a %n" \
  /etc/caddy/certs/ai-desk-card-online/fullchain.pem \
  /etc/caddy/certs/ai-desk-card-online/privkey.pem'
ssh myecs 'sudo grep -Eq "^[[:space:]]*auto_https +off[[:space:]]*$" \
  /etc/caddy/Caddyfile && echo caddy_auto_https=off; \
  sudo grep -Fq \
  "tls /etc/caddy/certs/ai-desk-card-online/fullchain.pem /etc/caddy/certs/ai-desk-card-online/privkey.pem" \
  /etc/caddy/Caddyfile && echo caddy_explicit_tls_paths=present; \
  sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null \
    && echo caddy_config=valid'
```

The hook should be root-owned, executable, and syntactically valid. It installs
the full chain as `0644`, installs the private key as `0600`, and reloads Caddy.
The installed copies should be owned by `caddy`, with modes `0644` and `0600`
respectively. Never print the private key, the full Caddyfile, or authentication
configuration into logs.

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

## Phase 5 Real-Data Publication

The production publisher runs on the Mac because Linear credentials, Apple
Calendar permission, and Codex metadata are local. It does not write real
source records to the Git worktree:

```bash
scripts/refresh_dashboard.py --source-check
scripts/refresh_dashboard.py --preview
scripts/refresh_dashboard.py --publish
```

Configuration is loaded from exported environment values first, then the
ignored mode-`0600` `.env.local`. Required fields are `LINEAR_API_KEY` and a
non-empty JSON-array `AI_DESK_CARD_CALENDARS`. The LaunchAgent contains neither.

Focus selection is optional and lives outside the repository at
`~/.config/ai-desk-card-online/focus.json`. A missing file uses `todo.first`.
Use the configuration CLI instead of hand-editing the file:

```bash
scripts/configure_focus.py get
scripts/configure_focus.py set --source calendar.next
scripts/configure_focus.py set --source manual --task "Private local focus"
scripts/configure_focus.py reset
```

Allowed `source` values are `todo.first`, `calendar.next`, `ai-status.task`,
`weather.current`, and `manual`. `manual` requires `task`; `subtitle` and
`big_text` are optional overrides. Unknown fields, arbitrary paths, malformed
JSON, and invalid text fail before baseline SSH. The file is read on every
scheduled refresh and is never transferred to the server or printed in logs.
The CLI creates a missing config directory as `0700`, atomically installs the
file as `0600`, and reports only source plus field-presence flags. A valid
change is applied by the next normal scheduler tick; the CLI does not preview,
publish, or restart it. Use CLI `--config PATH` and refresh
`--focus-config PATH` only for the same deliberate temporary alternate config.
`deploy/focus.example.json` remains the public contract example.

The preview reads `/srv/ai-desk-card-online/widgets.json` over SSH and reports
only source health and changed widget types. Publish transfers one sanitized
owned-widget payload plus the portable installer to a unique remote temporary
directory. `deploy/scripts/install_widgets.py` then:

1. acquires `/run/lock/ai-desk-card-widgets.lock`;
2. validates and re-reads the current live document;
3. preserves the server-owned weather widget;
4. creates a mode-`0600` backup only when widget content changes;
5. atomically installs and verifies mode `0644`;
6. restores the backup if post-install verification fails;
7. keeps only the newest bounded backup set.

The weather service uses the same Linux lock through `/usr/bin/flock`, so a
weather update and a local publish cannot overwrite each other.

The manual `scp` recipes below are retained only for diagnosis and rollback;
they are not the production Phase 5 update path.

## macOS LaunchAgent

Enable scheduling only after source-check, preview, one manual publish, live
HTTPS, Browser, and physical-device checks pass:

```bash
mkdir -p "$HOME/Library/LaunchAgents"
plutil -lint deploy/launchd/com.ethereal.ai-desk-card-refresh.plist.example
cp deploy/launchd/com.ethereal.ai-desk-card-refresh.plist.example \
  "$HOME/Library/LaunchAgents/com.ethereal.ai-desk-card-refresh.plist"
launchctl bootstrap "gui/$UID" \
  "$HOME/Library/LaunchAgents/com.ethereal.ai-desk-card-refresh.plist"
launchctl kickstart -k "gui/$UID/com.ethereal.ai-desk-card-refresh"
launchctl print "gui/$UID/com.ethereal.ai-desk-card-refresh"
```

The user agent runs every 300 seconds while the login session is available.
Local and remote locks prevent overlap. Sleep pauses execution and a later tick
resumes it. `scripts/run_scheduled_refresh.py` applies a 150-second bound and
replaces, rather than appends to, this mode-`0600` status file:

```text
~/Library/Logs/ai-desk-card-online/latest.log
```

Disable it before rollback or maintenance:

```bash
launchctl bootout "gui/$UID/com.ethereal.ai-desk-card-refresh"
```

To update the live public demo data without restarting Caddy:

```bash
scripts/web_update.py --focus "Phase 2 public demo update"
scp web/widgets.json myecs:/tmp/ai-desk-card-widgets.json
ssh myecs 'sudo install -o root -g root -m 0644 /tmp/ai-desk-card-widgets.json /srv/ai-desk-card-online/widgets.json'
```

To update the low-sensitivity AI session widgets without restarting Caddy:

```bash
scripts/update_ai_session.py \
  --widgets web/widgets.json \
  --session-name "Codex work turn" \
  --task "Advance the AI desk card" \
  --context-used 2000 \
  --context-limit 30000 \
  --running 1 \
  --waiting 0 \
  --blocked 0 \
  --completed-today 2
scp web/widgets.json myecs:/tmp/ai-desk-card-widgets.json
ssh myecs 'sudo install -o root -g root -m 0644 /tmp/ai-desk-card-widgets.json /srv/ai-desk-card-online/widgets.json'
```

Only write low-sensitivity display fields. Do not pass transcripts, message
previews, tokens, private task text, or raw logs into `widgets.json`.
This is a manual-only convention for the end of a meaningful Codex work turn or
milestone. The script does not publish by itself; the `scp` + `sudo install`
steps are the explicit live update boundary.

To update the low-sensitivity focus widget without restarting Caddy:

```bash
scripts/update_focus.py \
  --widgets web/widgets.json \
  --task "Define the next useful boundary" \
  --big-text "NOW" \
  --subtitle "manual focus"
scp web/widgets.json myecs:/tmp/ai-desk-card-widgets.json
ssh myecs 'sudo install -o root -g root -m 0644 /tmp/ai-desk-card-widgets.json /srv/ai-desk-card-online/widgets.json'
```

Only write `focus.task`, `focus.big_text`, and `focus.subtitle`. Do not pass
notes, source URLs, transcripts, tokens, or raw task-manager records into
`widgets.json`.

To update the low-sensitivity todo widget without restarting Caddy:

```bash
scripts/update_todo.py \
  --widgets web/widgets.json \
  --title "Todo" \
  --item "Define todo crop contract" --tag "manual" \
  --item "Keep raw sources out" --tag "privacy"
scp web/widgets.json myecs:/tmp/ai-desk-card-widgets.json
ssh myecs 'sudo install -o root -g root -m 0644 /tmp/ai-desk-card-widgets.json /srv/ai-desk-card-online/widgets.json'
```

Only write `todo.title` and up to five `todo.items[]` entries with `text` and
optional `tag`. Do not pass raw Reminders, Notion rows, source IDs, URLs,
completion history, transcripts, tokens, or raw logs into `widgets.json`.

To update the low-sensitivity calendar widget without restarting Caddy:

```bash
scripts/update_calendar.py \
  --widgets web/widgets.json \
  --event "09:30|Calendar crop contract|10:00" \
  --event "14:00|Keep raw events out|"
scp web/widgets.json myecs:/tmp/ai-desk-card-widgets.json
ssh myecs 'sudo install -o root -g root -m 0644 /tmp/ai-desk-card-widgets.json /srv/ai-desk-card-online/widgets.json'
```

Each event is `START|TITLE|END`; `END` may be empty. Only write
`calendar.now_iso` and up to four events with `start`, `title`, and optional
`end`. Do not pass raw Calendar or Google Calendar records, locations,
attendees, meeting links, notes, calendar IDs, event IDs, transcripts, tokens,
or raw logs into `widgets.json`.

## Phase 3 Weather Refresh

The first Phase 3 data source is Shenzhen weather from the public `wttr.in`
JSON endpoint. It does not use an API key.

The live server runs:

```bash
systemctl status ai-desk-card-weather.timer
systemctl status ai-desk-card-weather.service
```

The timer runs every 30 minutes and updates only the weather widget under the
shared publication lock:

```bash
/usr/bin/flock -x /run/lock/ai-desk-card-widgets.lock \
  /usr/bin/python3 /opt/ai-desk-card-online/scripts/update_weather.py \
  --widgets /srv/ai-desk-card-online/widgets.json \
  --location Shenzhen
```

If the public source fails, the script preserves the previous weather values
and marks only the weather widget as stale.

The updater writes `widgets.json` atomically and keeps the file mode at `0644`.
Do not remove that permission step: Caddy must be able to read the runtime JSON.

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
