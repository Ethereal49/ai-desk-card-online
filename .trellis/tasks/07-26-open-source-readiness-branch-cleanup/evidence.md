# Open-Source Readiness Evidence

## Replacement Branch

- Fetched `origin/main` commit:
  `a47db94933f6bc7e48497ec11e4181b2ae97cda0`.
- Fast-forwarded local `main` to that commit and created
  `agent/open-source-readiness` from the same commit.
- Task metadata reads `branch=agent/open-source-readiness`,
  `base_branch=main`, and `status=in_progress`.
- The active task directory was the only uncommitted scope carried from the
  merged Phase 7 branch.

## Approved Old-Branch Proof Before Implementation

- Local and remote `agent/phase7-planning-handoff` both resolved to
  `46700de3e3ea92491981ba9c29dffe0d58a84708`.
- `git merge-base --is-ancestor 46700de3e3ea92491981ba9c29dffe0d58a84708 origin/main`
  returned `0`.
- GitHub returned no open PR for that head and reported the branch
  unprotected; repository rulesets were empty.
- Recovery commands:

```bash
git branch agent/phase7-planning-handoff 46700de3e3ea92491981ba9c29dffe0d58a84708
git push origin agent/phase7-planning-handoff
```

These observations are not deletion authorization by themselves. They must be
re-read after the replacement branch is pushed and has a draft PR.

## Public Project Surface

- Added root README, exact MIT license, contributing guide, security policy,
  Contributor Covenant 2.1 adaptation, Issue Forms, chooser configuration, PR
  template, read-only CI, and a sanitized screenshot.
- CI official action pins were resolved immediately before authoring:
  - `actions/checkout` v7.0.1:
    `3d3c42e5aac5ba805825da76410c181273ba90b1`
  - `actions/setup-python` v7.0.0:
    `5fda3b95a4ea91299a34e894583c3862153e4b97`
  - `actions/setup-node` v7.0.0:
    `820762786026740c76f36085b0efc47a31fe5020`
- Ruby parsed the workflow and all three issue-template YAML files.
- `scripts/test_open_source_contract.py` proves the required file set, local
  Markdown links, MIT holder/text anchors, real PNG header/size, neutral plist,
  owner-anchor exclusion, least-privilege/full-SHA CI, and pre-network shell
  input failures.

## Generic Configuration

- `AI_DESK_CARD_SSH_HOST` or `--host` is required only for remote baseline
  reads and every publish.
- `--source-check` and `--preview --baseline PATH` remain host-free.
- Missing remote host returns redacted exit `3` before source collection or
  SSH.
- HTTP/HTTPS verification scripts require explicit URL/IP input and tests prove
  a fake `curl` is not invoked when it is absent.
- Launchd uses a neutral label, path placeholders, minimal PATH, and explicit
  host placeholder. Systemd weather location comes from
  `/etc/default/ai-desk-card-online`.
- Current docs/spec/examples contain no owner host alias, live IP, owner home
  path, or historical backup identifier. Archived Trellis evidence and Git
  history were unchanged.

## Browser And Screenshot

- Served a temporary copy of `web/` with `widgets.example.json` exposed as
  `widgets.json`.
- Normalized only the temporary top-level `updated_at` to the capture time so
  a historical fixture timestamp did not appear as current project health.
  Repository fixtures were unchanged.
- Built-in Browser evidence at exactly `758x1024`:
  - `innerWidth=758`, `innerHeight=1024`;
  - `scrollWidth=758`, `scrollHeight=1024`;
  - all six widget elements present and visible;
  - no widget horizontal or vertical overflow;
  - no match for the owner host/IP/home-path, `token`, or `password` anchors;
  - footer: `source: widgets.json refresh: 300s status: normal`.
- Final asset:
  `docs/assets/dashboard-preview.png`, real PNG `758x1024`,
  SHA-256
  `72c15ee11920a6e65231c06a9561552c7fb9fe2ecde1b8183b06b3a210e908bc`.
- The browser viewport override was reset, the local tab finalized, the server
  stopped, and the temporary fixture directory moved to Trash.

## Local Verification

- Full deterministic suite before independent review: `111` tests passed,
  zero skipped.
- Python compile, JavaScript syntax, shell syntax, tracked JSON, launchd plist,
  issue/workflow YAML, `git diff --check`, local links, and current-facing
  privacy scans passed.
- `scripts/test_open_source_contract.py`: `9` tests passed.
- Three independent read-only agents audited:
  - open-source/governance surfaces: no actionable finding;
  - task/diff/branch scope: no archive/history drift; deletion correctly still
    blocked pending replacement push/draft PR;
  - config/CI: found one P2 remote-cleanup observability gap.
- Closed the P2 by making a successful install followed by remote staging
  cleanup failure fatal, preserving a primary publish error when both fail,
  emitting only a bounded cleanup warning in that case, and updating tests plus
  the owning code-specs.
- Focused publisher suite after that fix: `15` tests passed.
- Final full-scope suite after the fix: `113` tests passed, zero skipped.
- Final Python compile, JavaScript syntax, shell syntax, `18` JSON files,
  launchd plist, four workflow/issue YAML files, task JSONL validation, plan
  freshness, archive no-diff, current-facing privacy scan, and
  `git diff --check` passed.

## Work Commit, Draft PR, And CI

- Work commit:
  `dcca6b1c2d8e77891570a89253fa257598ada581`
  (`docs: establish open-source project readiness`).
- Pushed branch: `agent/open-source-readiness`.
- Draft PR:
  `https://github.com/Ethereal49/ai-desk-card-online/pull/2`.
- Read-back confirmed:
  - state `OPEN`;
  - `isDraft=true`;
  - base `main`;
  - head `agent/open-source-readiness`;
  - head OID
    `dcca6b1c2d8e77891570a89253fa257598ada581`;
  - merge state `CLEAN`;
  - `validate` check completed with conclusion `SUCCESS`.
- The PR remains draft and was not merged.

## Approved Repository Settings

- Before the approved mutation:
  - description:
    `Web dashboard plan for ai-desk-card on e-ink browser devices`;
  - private vulnerability reporting: `enabled=false`;
  - repository rulesets: `[]`;
  - `main` protection endpoint: `404 Branch not protected`;
  - Dependabot security updates and every returned secret-scanning setting:
    `disabled`.
- Updated and read back the description as:
  `Static, privacy-conscious AI desk card dashboard for 758x1024 e-ink browsers.`
- Enabled and read back private vulnerability reporting:
  `{"enabled":true}`.
- After the approved mutation:
  - repository remains public with default branch `main`;
  - issues, projects, and wiki remain enabled;
  - repository rulesets remain `[]`;
  - `main` remains unprotected;
  - Dependabot security updates and every returned secret-scanning setting
    remain `disabled`.
- No other repository security or protection setting was changed.

## Approved Old-Branch Cleanup

- Immediately before deletion, a fresh fetch and GitHub read-back proved:
  - local and remote `agent/phase7-planning-handoff` both resolved to
    `46700de3e3ea92491981ba9c29dffe0d58a84708`;
  - that exact commit remained an ancestor of
    `origin/main@a47db94933f6bc7e48497ec11e4181b2ae97cda0`;
  - the old head had no open PR;
  - GitHub reported `protected=false`;
  - replacement PR #2 remained open/draft and its first CI run was successful.
- Deleted the local branch with safe
  `git branch -d agent/phase7-planning-handoff`.
- Deleted only the exact remote branch with
  `git push origin --delete agent/phase7-planning-handoff`.
- Fresh local inventory:
  - `agent/open-source-readiness` at
    `dcca6b1c2d8e77891570a89253fa257598ada581`;
  - `main` at
    `a47db94933f6bc7e48497ec11e4181b2ae97cda0`.
- Fresh live remote inventory contains only:
  - `refs/heads/agent/open-source-readiness` at
    `dcca6b1c2d8e77891570a89253fa257598ada581`;
  - `refs/heads/main` at
    `a47db94933f6bc7e48497ec11e4181b2ae97cda0`.
- Both local and remote-tracking exact-ref absence checks for the old branch
  returned non-zero.
- Recovery remains possible from the immutable commit:

```bash
git branch agent/phase7-planning-handoff 46700de3e3ea92491981ba9c29dffe0d58a84708
git push origin agent/phase7-planning-handoff
```

## Pending Closeout Gates

- Final post-settings/cleanup local gate passed:
  - `113` Python tests passed, zero skipped;
  - Python compile, JavaScript syntax, and all deployment shell syntax passed;
  - all `17` tracked JSON files, the tracked launchd plist, and all four
    workflow/Issue Form YAML files parsed;
  - task JSONL validation, plan freshness, current-facing contract/privacy/link
    checks, archive no-diff, and `git diff --check` passed.
- The installed Ruby/Psych version does not expose `safe_load_file`; the first
  YAML parser invocation failed loudly, was replaced with the compatible
  `YAML.safe_load(File.read(...))` API, and all four files then passed.
- Commit and push this second work commit, then read back its PR head/check
  before archiving.
- Archive the Trellis task, record the journal, push closeout commits, and
  verify the final clean state.
