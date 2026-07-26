# IP Certificate Renewal Contract

## Scenario: Short-Lived IP Certificate Renewal

### 1. Scope / Trigger

Use this contract when changing the public-IP HTTPS Caddy example, Certbot/Snap
renewal documentation, HTTP-01 routing, the deploy hook, certificate install
paths, or certificate health checks for a configured public-IP deployment.

Documentation-only audits are read-only. If a live invariant fails, stop and
open a separate infrastructure repair task rather than mutating the server
under a documentation scope.

### 2. Signatures

```text
Snap scheduler: snap.certbot.renew.timer
Renewal service: snap.certbot.renew.service
Renewal config: /etc/letsencrypt/renewal/<lineage-name>.conf
Deploy hook:
  /etc/letsencrypt/renewal-hooks/deploy/ai-desk-card-online-ip-cert.sh
Caddy certificate directory: /etc/caddy/certs/ai-desk-card-online/
Repository example: deploy/caddy/Caddyfile.ip-https.example
```

Safe live checks use `systemctl is-enabled/is-active/show`,
`openssl x509 -noout`, status-only `curl`, `stat`, `bash -n`, targeted
`grep -q`, and `caddy validate`. They must not invoke renewal or reload.

### 3. Contracts

- The Snap-owned timer, not generic `certbot.timer`, is the authoritative
  scheduler for this installation.
- Certbot uses the `shortlived` profile, the `webroot` authenticator, and
  `/srv/ai-desk-card-online` for HTTP-01 challenge files.
- Caddy uses `auto_https off`, an explicit `:80` route that serves
  `/.well-known/acme-challenge/*` before redirecting, and an explicit `:443`
  certificate pair. Both listeners obtain the static root from
  `AI_DESK_CARD_WEB_ROOT`; checked-in examples contain no live address or
  owner-specific host alias.
- The root-owned executable deploy hook installs the full chain as `0644` and
  private key as `0600`, owned by `caddy`, then reloads Caddy.
- Certificate issuer, SAN, validity dates, Certbot version, timer timestamps,
  and service results are runtime facts. Durable docs state invariants and
  commands, not a fixed current value.
- Checks may expose public certificate metadata, paths, modes, ownership,
  service state, and boolean config matches. They must not print a private key,
  Basic Auth hash/password, ACME account data, environment file, or complete
  live Caddyfile.

The renewal flow is:

```text
Snap timer -> webroot HTTP-01 -> renewed lineage -> deploy hook
  -> Caddy certificate directory -> Caddy reload
```

### 4. Validation & Error Matrix

| Condition | Required result |
| --- | --- |
| Generic `certbot.timer` is absent/inactive, Snap timer is healthy | Neutral; use the Snap units |
| Snap timer is disabled/inactive or has no next execution | Fail the audit; open an infra repair task |
| Last renewal service has non-success result or nonzero status | Fail the audit; do not relabel it healthy |
| Public certificate lacks the IP SAN or is outside its validity interval | Fail the public TLS gate |
| Missing HTTP challenge path redirects or requires auth | Fail HTTP-01 route validation |
| Deploy hook is missing, unsafe, or has wrong install/reload actions | Fail the audit; do not run it during docs work |
| Caddy certificate modes/owners or explicit paths differ | Fail the audit and reconcile in a separate task |
| `caddy validate` fails | Do not install or reload the candidate config |
| HTTP `/` is not a redirect or unauthenticated HTTPS `/` is not `401` | Fail the transport/access-control gate |

### 5. Good/Base/Bad Cases

- Good: the Snap timer is enabled/active with a future execution, the last
  service succeeded, the public and installed certificates match, hook and
  Caddy invariants pass, and public status is `301/404/401`.
- Base: generic `certbot.timer` is inactive while the Snap timer and renewal
  service are healthy. This is expected packaging behavior, not a failure.
- Bad: copy the observed expiry or Certbot version into durable prose, print a
  full config/private file, or run `certbot renew`/`systemctl reload` to make a
  documentation check pass.

### 6. Tests Required

- Stream `Caddyfile.ip-https.example` to a compatible Caddy binary with a
  disposable generated password hash and static-root environment value, then
  assert `caddy validate` exits `0`; do not install the candidate or reload
  Caddy.
- Run `bash -n` on the checked-in deployment verification scripts.
- Search durable docs for obsolete fixed expiry/version claims and
  `auto_https disable_redirects`.
- Run the bounded live checks for SAN/date, `301/404/401`, Snap timer/service,
  allowlisted renewal fields, hook syntax/actions, certificate modes, and Caddy
  validation.
- Run the repository privacy scan, Trellis validation, plan freshness guard,
  full Python suite, and `git diff --check` before archive.

### 7. Wrong vs Correct

#### Wrong

```text
The certificate expires on a copied date, so renewal is healthy.
Run certbot renew and reload Caddy to confirm it.
```

This converts a stale observation into configuration and crosses the live
mutation boundary during an audit.

#### Correct

```text
Read public certificate metadata -> inspect Snap timer/service -> verify
allowlisted renewal/hook/Caddy invariants -> record timestamped evidence.
```

This proves the complete mechanism without exposing secrets or changing state.
