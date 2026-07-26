# Open-Source Readiness And Branch Cleanup

## Goal

Turn the existing public repository into a credible, reusable open-source
project without changing the dashboard product architecture, then remove only
branches proven redundant after merged work is preserved on `main`.

## Background

- The repository is public and its GitHub community profile is currently 14%.
- The repository root has no `README.md`, license, contribution guide, security
  policy, code of conduct, issue templates, pull-request template, or CI.
- The existing `web/README.md` and `deploy/README.md` are operator references,
  not a newcomer-oriented project entry point.
- Several deployment examples contain machine-specific paths or live host/IP
  defaults, which makes a public clone look owner-specific and can encourage
  unsafe copy-paste deployment.
- GitHub `main` is the default branch. PR #1 is merged. The only other live
  local/remote branch observed is `agent/phase7-planning-handoff`; it has no
  open PR and is a cleanup candidate only after ancestry is reverified against
  the fetched `origin/main` and work moves to a new owning branch.
- `main` currently has no branch protection or repository ruleset. Private
  vulnerability reporting is the only approved security-setting change;
  documentation cleanup does not imply any other repository-setting change.

## Requirements

### Public Project Entry Point

- Add an English root `README.md` that explains the product, target e-ink
  display, actual architecture, six widgets, quick start, configuration model,
  privacy boundary, validation, deployment entry points, limitations,
  contribution path, and license.
- Use a real screenshot generated from the public example/dashboard fixture;
  do not expose private runtime data or credentials.
- Keep detailed operator procedures in `web/README.md` and `deploy/README.md`;
  the root README links to them rather than duplicating their full content.

### Open-Source Governance

- Add only useful governance files: an MIT license with
  `Copyright (c) 2026 Ethereal49`, `CONTRIBUTING.md`,
  `SECURITY.md`, and `CODE_OF_CONDUCT.md`.
- Add issue templates, an issue-template chooser config, and a pull-request
  template with checks that reflect this repository's privacy, plan, test, and
  e-ink validation boundaries.
- Enable GitHub private vulnerability reporting and make it the primary path
  in `SECURITY.md`; sensitive reports must not be filed as public issues.
- Add a minimal dependency-free GitHub Actions CI workflow for Python tests,
  Python/JavaScript/shell/plist/JSON syntax, plan freshness, and diff safety.
- Do not fabricate releases, maintainers, support SLAs, public deployment URLs,
  package-manager installation, or a roadmap that the repository does not have.

### Public Reusability

- Genericize every current-facing surface, including root/web/deployment docs,
  `PLAN_web.md`, script defaults, and plist examples. Replace `myecs`, the live
  IP, owner home paths, and historical backup paths with explicit placeholders
  or required environment inputs while preserving fail-loud validation.
- Leave `.trellis/tasks/archive/` and Git history unchanged. The removed values
  are not credentials, and rewriting evidence/history would destroy useful
  provenance without removing already-public objects from existing commits.
- Do not publish credentials, Basic Auth hashes, private keys, calendar names,
  local Focus content, private source records, or server-generated artifacts.
- Keep the static HTML/CSS/vanilla-JavaScript and `widgets.json` architecture.
  This task does not add a backend, framework, build system, or package runtime.

### Branch Cleanup

- Create the implementation branch from the fetched `origin/main`; do not
  continue public-readiness work on the already merged Phase 7 branch.
- Never delete `main`, the current implementation branch, a protected branch,
  an unmerged branch, or a branch referenced by an open PR.
- Before any deletion, record the exact local and remote branch names, fetched
  commit IDs, merged/ancestor proof, PR state, and rollback/recovery command.
- The final exact cleanup candidate list has explicit approval. Local deletion
  still uses safe `git branch -d`; remote deletion occurs only after local
  verification and can be recovered from the recorded commit ID.

## Acceptance Criteria

- [ ] A newcomer can understand the project and run the static dashboard from
  the root README without owner-specific knowledge.
- [ ] The README uses an actual sanitized dashboard screenshot and all local
  links/commands resolve from a clean clone.
- [ ] The pull-request head contains the useful README/license/contributing/
  conduct/security/template surfaces without placeholder claims. Because
  GitHub calculates the community profile from the default branch, no
  default-branch score increase is claimed before the draft PR is merged.
- [ ] CI runs the repository's real deterministic checks on pull requests and
  pushes to `main` without adding a build dependency.
- [ ] Public deployment examples contain no hardcoded owner home path or live
  host/IP default, and current tests/docs agree with the new inputs.
- [ ] Full Python/static/privacy/Trellis/plan/link checks pass; the rendered
  README and dashboard screenshot are inspected.
- [ ] The implementation is committed on a new branch based on current
  `origin/main`, pushed, and represented by a draft PR without merging it.
- [ ] Only explicitly approved redundant branches are deleted; post-delete
  local and remote inventories prove `main` and the implementation branch are
  preserved.
- [ ] The task is archived and the Trellis journal records only work commits.

## Out Of Scope

- Product features, UI redesign, runtime source changes, live dashboard
  publication, server mutation, certificate renewal, or scheduler changes.
- Package registry publication, container images, release automation,
  CHANGELOG/CITATION files without real releases or citation requirements.
- Enabling branch protection, repository rulesets, Discussions, Pages, or
  other GitHub settings. Private vulnerability reporting is the sole approved
  repository-security setting change in this task.

## Decisions

- License: MIT, copyright `2026 Ethereal49`.
- Current-facing docs/examples are generic and reusable; archived Trellis
  evidence and existing Git history retain their historical content.
- Approved cleanup candidate after replacement-branch push and final proof:
  local `agent/phase7-planning-handoff` and remote
  `origin/agent/phase7-planning-handoff`, both anchored at
  `46700de3e3ea92491981ba9c29dffe0d58a84708`. Recovery may recreate the branch
  from that full commit ID.
- GitHub private vulnerability reporting may be enabled and used as the
  executable private reporting path in `SECURITY.md`; other security settings
  remain unchanged.
