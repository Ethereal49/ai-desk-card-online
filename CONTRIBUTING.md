# Contributing

Contributions are welcome when they preserve the project's e-ink, privacy, and
static-architecture boundaries.

## Before You Start

Read [AGENTS.md](AGENTS.md) and [PLAN_web.md](PLAN_web.md). The plan is the
product and architecture source of truth.

This repository intentionally uses HTML, CSS, vanilla JavaScript, JSON, and
standard-library Python. Do not add a frontend framework, backend service,
build system, package runtime, firmware transport, or live write integration
without first changing the plan and explaining which product requirement needs
that complexity.

For a larger change, open an issue before implementation. Describe the user
problem, privacy boundary, expected behavior, and how completion can be
verified.

## Local Setup

```bash
git clone https://github.com/Ethereal49/ai-desk-card-online.git
cd ai-desk-card-online
python3 -m http.server 4173 --directory web
```

No dependency installation is required for the deterministic test suite.

## Development Rules

- Make the smallest change that solves the stated problem.
- Keep frontend files in `web/`, deployment assets in `deploy/`, and
  deterministic Python tooling in `scripts/`.
- Preserve the stable `widgets.json` contract and unrelated widgets.
- Keep real credentials and private runtime data out of the repository.
- Treat source access as read-only unless a separately reviewed plan changes
  that boundary.
- Update tests to express why the behavior matters.
- Update `PLAN_web.md` after the implementation state changes.

## Required Checks

Run:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m compileall -q scripts .codex/hooks .trellis/scripts deploy/scripts
node --check web/app.js
bash -n deploy/scripts/*.sh
python3 .codex/hooks/ensure_plan_updated.py
git diff --check
```

Report skipped checks explicitly. A skipped check is not a pass.

For frontend changes, also serve `web/` and inspect the built-in Browser at
`758x1024`. Verify:

- the page has no horizontal or vertical scrolling;
- all six widget regions render;
- missing or failed `widgets.json` does not blank the page;
- long English, Chinese, and unbroken text stays bounded;
- no private data appears in screenshots or fixtures.

Store intermediate QA artifacts in ignored `output/`. Commit a screenshot
under `docs/assets/` only when it is sanitized, reviewed, and part of public
documentation.

## Pull Requests

Keep pull requests focused. Complete the repository PR template and include:

- the problem and scope;
- affected contracts and privacy boundaries;
- exact tests and Browser/device checks run;
- known limitations or skipped gates;
- screenshots only when the visual output changed.

Do not publish live data, mutate a deployment, or include credentials merely to
make a pull request check pass.

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE) and that you will follow the
[Code of Conduct](CODE_OF_CONDUCT.md).
