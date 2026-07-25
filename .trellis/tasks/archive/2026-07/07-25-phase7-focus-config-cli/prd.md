# Add Safe Focus Configuration CLI

## Goal

Provide a deterministic operator command for creating, inspecting, and
resetting the existing local Focus configuration without hand-editing JSON,
printing configured text, mutating live `widgets.json`, or weakening the
allowlisted projection contract.

## Background

- Production Focus configuration lives at
  `~/.config/ai-desk-card-online/focus.json`; a missing file defaults to
  `todo.first`.
- `scripts/focus_config.py` already owns strict parsing and projection for
  `todo.first`, `calendar.next`, `ai-status.task`, `weather.current`, and
  `manual` plus bounded `task`, `subtitle`, and `big_text` fields.
- `scripts/update_focus.py` is a legacy diagnostic updater that writes a local
  `widgets.json`. It is not the production configuration path and must not be
  repurposed in a way that creates two Focus owners.

## Requirements

- Add a standard-library CLI at `scripts/configure_focus.py` that reuses
  `focus_config.parse_focus_config`/`load_focus_config` rather than duplicating
  selectors, limits, or validation.
- Support three deterministic commands:
  - `get`: validate the current file and print only source plus field-presence
    flags, never configured text;
  - `set`: accept one allowlisted source and documented overrides, validate the
    complete candidate before replacing the file;
  - `reset`: atomically write the explicit default `{"source":"todo.first"}`.
- The default path remains the existing config path. `--config PATH` is allowed
  for tests and deliberate alternate local configuration only.
- Create the parent directory with mode `0700` when needed. Every successful
  config replacement must be atomic and mode `0600`, including replacement of
  an existing file with broader permissions.
- Invalid source/field combinations, missing manual task, overlong/empty text,
  malformed existing config, filesystem errors, or directories in place of a
  file must fail loudly with a bounded redacted reason and leave the previous
  file byte-for-byte unchanged.
- The command must not read source systems, resolve the selected widget, invoke
  SSH, publish, restart the LaunchAgent, edit `widgets.json`, or print manual
  task/subtitle/big-text values.
- Document that the next normal scheduler tick applies a valid config. Keep a
  separate explicit `refresh_dashboard.py --preview/--publish` operator flow;
  the CLI itself never chains it.
- Update `AGENTS.md` structure, deploy/web operator docs, tests, and the Phase 7
  plan checkpoint.

## Acceptance Criteria

- [ ] `get`, `set`, and `reset` have stable help text, exit codes, and redacted
  output; no command prints configured content.
- [ ] Every allowlisted source can be written and reloaded through the shared
  parser; `manual` requires `task`, and linked sources reject `task`.
- [ ] Successful writes are atomic with directory mode `0700` and file mode
  `0600` on first write and replacement.
- [ ] Invalid input or I/O failure preserves the previous config exactly and
  does not contact sources, SSH, publisher, or live runtime.
- [ ] `reset` produces the explicit default and the production resolver still
  projects `todo.first` on the next preview.
- [ ] Tests prove the CLI never writes `web/widgets.json` or invokes publish.
- [ ] Focused/full Python, privacy, Trellis, plan, and diff gates pass; operator
  docs explain usage and the legacy diagnostic updater boundary.

## Out Of Scope

- Browser-side settings, arbitrary JSON paths, plugins, scripts, model routing,
  dynamic widget creation, or source-system writes.
- Automatic publish or LaunchAgent restart.
- Removing `scripts/update_focus.py`; its diagnostic role may be clarified but
  not silently changed in this task.
