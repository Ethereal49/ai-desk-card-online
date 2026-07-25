# Correct Certificate Deployment Documentation

## Goal

Make certificate operations documentation describe the durable renewal
mechanism and verification boundary rather than an obsolete fixed expiry date,
using current read-only server evidence without changing live configuration.

## Background

- `deploy/README.md` says the current certificate expires on `2026-06-07`,
  which is already false and conflicts with `PLAN_web.md`'s rule that expiry is
  a runtime fact.
- A read-only check on `2026-07-25` showed a newly issued short-lived IP
  certificate with the expected SAN and a later expiry.
- The generic `certbot.timer` is inactive because this host uses the Snap
  package. `snap.certbot.renew.timer` is enabled, ran successfully, and had a
  next scheduled execution.
- A deploy hook copies renewed files into Caddy's explicit certificate path and
  reloads Caddy; its current path and permissions must be re-read live before
  documentation is finalized.

## Requirements

- Remove every documentation claim that treats a certificate expiry timestamp
  as durable configuration. Use commands and expected invariants instead.
- Document the actual Snap unit name and explain why `certbot.timer` is not the
  authoritative health check on this installation.
- Re-verify read-only: certificate issuer/SAN/date, Snap renewal timer enabled
  and scheduled state, recent renewal service result, Certbot renewal config,
  deploy-hook presence, Caddy explicit cert/key references, and public
  HTTP-redirect/unauthenticated-HTTPS status.
- Describe the renewal chain precisely:
  Certbot/Snap timer -> HTTP-01 challenge path -> renewed lineage -> deploy hook
  -> Caddy certificate directory -> Caddy reload.
- Keep all passwords, hashes, private keys, ACME account details, tokens, and
  certificate private material out of command output and repository files.
- Change documentation/examples only. Do not run `certbot renew`, edit live
  Caddy/Certbot/systemd state, reload services, or alter certificates in this
  task.
- Update `PLAN_web.md` only with durable mechanism/current task state; the final
  plan-compression child will remove historical duplication.

## Acceptance Criteria

- [ ] `deploy/README.md` contains no fixed current certificate expiry and names
  `snap.certbot.renew.timer` as the operative renewal scheduler.
- [ ] Documentation distinguishes durable configuration from runtime checks and
  includes bounded commands for SAN/date, timer/service, deploy hook, and HTTP
  status verification.
- [ ] The documented renewal chain matches read-only live Caddy, Certbot, Snap,
  and hook state; any uncertainty is explicit rather than guessed.
- [ ] No live configuration or runtime file is modified and no secret/private
  certificate material is captured in evidence.
- [ ] Existing deployment examples remain syntactically valid and do not expose
  non-runtime repository files.
- [ ] Documentation, plan freshness, Trellis validation, privacy search, and
  `git diff --check` pass before archive.

## Out Of Scope

- Renewing or replacing the current certificate.
- Changing ACME provider/profile, Caddy routing, Basic Auth, firewall, DNS, or
  systemd/Snap configuration.
- Re-running the password-bearing authenticated HTTPS gate unless the user
  separately supplies the password in the existing environment boundary.
