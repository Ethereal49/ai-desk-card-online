# Focus Configuration CLI Implementation Plan

## Ordered Work

1. [x] Read `focus_config.py`, its direct caller, existing focus tests, manual
   updater, backend specs, and operator docs.
2. [x] Add focused failing tests for command parsing, every selector, manual
   requirements, redaction, atomic preservation, modes, and no-publish behavior.
3. [x] Implement `scripts/configure_focus.py` with `get`, `set`, and `reset`,
   reusing the shared parser and writing only the selected config path.
4. [x] Verify invalid input never changes an existing config and temporary
   files are cleaned after failures.
5. [x] Update `AGENTS.md`, `deploy/README.md`, `web/README.md`, backend code-spec
   if the executable CLI contract warrants it, and `PLAN_web.md`.
6. [x] Run:

```bash
PYTHONPATH=scripts python3 -m unittest test_focus_config test_configure_focus test_refresh_dashboard
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m compileall -q scripts deploy/scripts
python3 .codex/hooks/ensure_plan_updated.py
python3 ./.trellis/scripts/task.py validate 07-25-phase7-focus-config-cli
git diff --check
```

7. [x] Use a temporary config to prove `set -> get -> reset`, then run a
   redacted local preview that resolves the explicit default without writing
   live state.
8. [x] Complete evidence and spec review, create work commit `44692ab`, then
   archive and journal through finish-work.

## Rollback

Removing the new CLI leaves the Phase 6 config/resolver unchanged. If a config
written during local validation is not an isolated temporary file, restore the
pre-test bytes and mode before closing the task.
