# Certificate Documentation Evidence

## Boundary

Read-only checks ran at `2026-07-25T16:37:32Z`
(`2026-07-26T00:37:32+08:00`) against SSH alias `myecs` and public IP
`112.74.73.134`. No renewal, service reload, configuration edit, certificate
replacement, or repository-to-server copy was performed.

The checks did not read or record Basic Auth values, ACME account details,
private key contents, environment files, or private certificate material.

## Public Certificate And Transport

Bounded status-only `curl` checks and
`openssl s_client | openssl x509 -noout` reported:

- HTTP `/`: `301`;
- a nonexistent `/.well-known/acme-challenge/` path over HTTP: `404`, not a
  redirect or authentication response;
- unauthenticated HTTPS `/`: `401`, with normal certificate verification also
  succeeding;
- issuer: Let's Encrypt `YE2`;
- SAN: `IP Address:112.74.73.134`;
- validity: `Jul 25 01:21:47 2026 GMT` through
  `Jul 31 17:21:46 2026 GMT`.

The validity dates are observation evidence only. They are not copied into
durable deployment prose.

## Renewal Scheduler And Lineage

Targeted `systemctl show`, `certbot --version`, and allowlisted renewal-config
fields reported:

- Certbot `5.7.0`;
- `snap.certbot.renew.timer`: `enabled` and `active`;
- last trigger: `Sat 2026-07-25 21:36:04 CST`;
- next execution: `Sun 2026-07-26 10:15:00 CST`;
- last `snap.certbot.renew.service`: `Result=success`, `ExecMainStatus=0`;
- renewal config: `/etc/letsencrypt/renewal/112.74.73.134.conf`;
- `preferred_profile=shortlived`;
- `authenticator=webroot`;
- `webroot_path=/srv/ai-desk-card-online`.

The generic `certbot.timer` is not the package-owned scheduler on this Snap
installation. Renewal health must be evaluated from the Snap timer and service.

## Deploy Hook And Caddy

The deploy hook
`/etc/letsencrypt/renewal-hooks/deploy/ai-desk-card-online-ip-cert.sh` is
`root:root`, mode `0755`, and passes `bash -n`. Bounded pattern checks confirmed
that it:

- installs the renewed full chain with mode `0644`;
- installs the private key with mode `0600` without printing its contents;
- reloads Caddy after installation.

Targeted live Caddy checks reported:

- service: `enabled` and `active`;
- global option: `auto_https off`;
- explicit `:80` listener with the HTTP-01 challenge route;
- explicit `:443` listener with
  `/etc/caddy/certs/ai-desk-card-online/fullchain.pem` and `privkey.pem`;
- `caddy validate`: valid;
- installed full chain: `caddy:caddy`, mode `0644`;
- installed private key: `caddy:caddy`, mode `0600`;
- the installed full chain has the same issuer, SAN, and validity interval as
  the public certificate.

The checked-in `deploy/caddy/Caddyfile.ip-https.example` was streamed to the
live Caddy binary on standard input with a generated disposable password hash.
`caddy validate --adapter caddyfile --config -` exited `0`; the example was not
installed and no service was reloaded.

The verified renewal chain is therefore:

```text
Snap renewal timer
  -> Certbot webroot HTTP-01 challenge
  -> renewed Let's Encrypt lineage
  -> deploy hook
  -> Caddy certificate directory
  -> Caddy reload
```

## Safe Verification Shape

The documentation exposes only status, certificate public metadata, allowlisted
renewal fields, file metadata, and boolean configuration invariants. It avoids
commands that print the whole renewal config, deploy hook, Caddyfile, private
key, environment, or authentication configuration.

## Repository Checkpoint

- `python3 -m unittest discover -s scripts -p 'test_*.py'`: `98 passed`;
- `bash -n deploy/scripts/verify_ip_https.sh deploy/scripts/verify_ip_only.sh`:
  passed;
- stale-claim scan for the obsolete expiry, Certbot version, and
  `auto_https disable_redirects`: passed;
- private-key/credential-pattern scan: passed; reviewed sensitive-word matches
  are placeholders, variable names, or prohibitions only;
- `task.py validate 07-25-phase7-certificate-docs`: passed;
- `git diff --check`: passed.

The backend IP certificate renewal code-spec now owns the executable Snap,
HTTP-01, hook, Caddy, read-only verification, and failure-escalation contract.

Plan freshness is rerun after this evidence checkpoint so `PLAN_web.md` remains
the final project-state write.
