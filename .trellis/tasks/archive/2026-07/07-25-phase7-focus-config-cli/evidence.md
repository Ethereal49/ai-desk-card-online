# Focus Configuration CLI Evidence

## Implemented Contract

- `scripts/configure_focus.py [--config PATH] get|set|reset` is a standalone
  standard-library command.
- `set` and `reset` reuse `focus_config.parse_focus_config`; the resolver remains
  the single selector/text validation authority.
- A missing parent is created as mode `0700`. A validated candidate is written
  to a same-directory temporary file, flushed, set to mode `0600`, and installed
  with `os.replace`; failed replacement removes the temporary file and preserves
  previous bytes.
- Success output contains only the allowlisted source and task/subtitle/big-text
  presence flags. Configuration and local-I/O failures use bounded reason labels
  and never print configured values or exception text.
- The command imports no source, widget updater, publisher, remote, or scheduler
  path. It writes only the selected config; refresh remains a separate action.

## Focused Evidence

- The initial focused run failed because `configure_focus` did not exist.
- After implementation, one help-text correction, and explicit wrapped-I/O
  mapping, 26 Focus/resolver/refresh tests passed.
- Tests cover all five selectors, shared-parser reuse, manual/linked field rules,
  argparse exit `2`, configuration exit `3`, local-I/O exit `1`, redaction,
  first/replacement modes, byte preservation, temporary cleanup, explicit reset,
  and no `widgets.json` or process invocation.

## Isolated Operator Smoke

- An isolated `set --source manual -> get -> reset` sequence returned `0` for
  every command. Output contained only source and field-presence flags; neither
  private smoke value appeared.
- The created directory was mode `0700`, the replaced file was mode `0600`, and
  reset produced exactly `{"source":"todo.first"}`.
- A preview using the reset config and repository baseline reported
  `publish=preview`. It returned the expected partial exit `2` because of the
  separately documented quota no-go; all other sources were `ok`.
- The baseline SHA-256 was identical before and after preview. The isolated
  config, lock, and temporary directory were removed with individual bounded
  cleanup operations.

## Quality Gates

- 26 focused Focus/resolver/refresh tests passed.
- 98 full Python tests passed.
- Python compile, JavaScript syntax, plist lint, shell syntax, Trellis
  validation, plan freshness, and `git diff --check` passed.
- Direct CLI help lists `get`, `set`, and `reset`, documents the no-publish
  boundary, and states that configured text is never printed.
