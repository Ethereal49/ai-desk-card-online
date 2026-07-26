# Focus Configuration CLI Design

## Command Contract

```text
scripts/configure_focus.py [--config PATH] get
scripts/configure_focus.py [--config PATH] set --source SOURCE
  [--task TEXT] [--subtitle TEXT] [--big-text TEXT]
scripts/configure_focus.py [--config PATH] reset
```

Expected outcomes:

| Condition | Exit | Output |
| --- | --- | --- |
| Valid `get`/`set`/`reset` | `0` | Bounded status, source, and presence flags only |
| Validation/configuration error | `3` | `focus-config=fatal reason=configuration` |
| Local filesystem/atomic-write error | `1` | `focus-config=fatal reason=local-io` |

Argparse usage errors retain exit `2`. Error output never includes the rejected
value or file content.

## Data Flow

```text
CLI args
  -> bounded candidate dict
  -> focus_config.parse_focus_config
  -> serialize canonical public config shape
  -> private temporary file in target directory
  -> chmod 0600
  -> atomic os.replace
  -> fsync directory when supported
```

`get` calls `load_focus_config` and reports only:

```text
focus-config=ok source=<allowlisted-value> task=<present|absent>
subtitle=<present|absent> big_text=<present|absent>
```

The exact line may be compacted, but configured values other than the public
selector are never printed.

## Reuse Boundary

- `focus_config.py` remains the single selector/text validation authority.
- A narrow write helper may live in `configure_focus.py`; do not expand
  `focus_config.py` into a CLI or source/publish orchestrator.
- Do not call or modify the legacy `update_focus.py` data path.

## Atomicity And Permissions

Write only after full candidate validation. Use a temporary file in the target
directory so `os.replace` is atomic. On any pre-replace failure, remove the
temporary file and preserve the prior config. Explicitly set directory/file
modes because umask alone is not a contract.

## Security And Privacy

The user intentionally supplies the text, but it is still local private
configuration. Help/error/status output is structure-only. Tests inject unique
secret markers and assert they never appear in stdout/stderr.

## Compatibility

Missing config behavior is unchanged. `reset` writes an explicit default rather
than deleting arbitrary paths. The scheduler reads the file on its next normal
tick; no new daemon, launchd configuration, or live schema is introduced.
