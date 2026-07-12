# Logging Guidelines

## Current Practice

The project has no logging framework. CLI scripts emit short human-readable
status lines with `print`, and shell verification gates use `printf`.

## What To Log

- The action completed and the local target path.
- Fresh/stale state when it changes the meaning of the result.
- The failed gate, expected value, and observed value before exiting non-zero.
- External fetch exceptions for local diagnosis.

Examples:

- `scripts/update_codex_usage.py` prints the quota freshness and destination.
- `scripts/update_weather.py` prints the location and fresh/stale result.
- `deploy/scripts/verify_ip_https.sh` prints each checked path and status.

## What Not To Log

- Authentication passwords or hashes.
- Tokens, transcripts, rollout content, private task text, or raw third-party
  records.
- Full JSON payloads when a concise status is sufficient.

## Conventions

- Keep output deterministic enough for an operator to scan.
- Use stderr for fatal shell-gate explanations.
- Do not introduce structured logging, log files, or telemetry until a long
  running backend process actually exists.
