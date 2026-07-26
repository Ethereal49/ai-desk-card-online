# Certificate Documentation Design

## Source Of Truth Split

Documentation records mechanisms and invariants:

- certificate profile is Let's Encrypt short-lived IP;
- SAN must include the target IP;
- Snap owns renewal scheduling;
- the deploy hook synchronizes renewed lineage files to Caddy;
- Caddy serves an explicit certificate on `:443` behind Basic Auth.

Runtime commands provide dates and current status. No date is copied into prose
as a durable "current certificate" fact.

## Read-Only Evidence Set

Use commands that cannot expose private key contents:

```text
openssl s_client | openssl x509 -noout -issuer -dates -ext subjectAltName
systemctl list-timers --all | filter snap.certbot.renew
systemctl status/show snap.certbot.renew.timer/service
stat and bounded text inspection of renewal config/deploy hook/Caddy paths
curl status-only checks for HTTP redirect and unauthenticated HTTPS
```

Do not print environment files, Basic Auth hashes, private key contents, ACME
account files, or full Caddy configuration if a targeted field/path check is
sufficient.

## Documentation Layout

Update the existing IP HTTPS section in `deploy/README.md` with:

1. durable topology;
2. renewal scheduler and hook chain;
3. safe live verification commands;
4. expected status invariants and failure interpretation.

Keep Caddy examples generic. Change an example only if read-only evidence proves
the checked-in shape is wrong.

## Failure Boundary

If the live mechanism contradicts checked-in docs in a way that requires server
changes, stop this documentation child and create a separate implementation
task. Do not repair live infrastructure under a docs-only scope.
