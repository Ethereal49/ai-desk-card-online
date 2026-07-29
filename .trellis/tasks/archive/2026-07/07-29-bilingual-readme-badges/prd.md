# Add bilingual README and project badges

## Goal

Make the repository easier to evaluate and adopt for Chinese-speaking users
without weakening the existing English-first open-source entry point or making
unverified project claims.

## Background

- `README.md` is the canonical English project entry point.
- The repository already has a real `CI` workflow, an MIT license, a Python
  3.11+ requirement, a vanilla JavaScript frontend, and a contribution guide.
- The current backend and frontend Trellis indexes say that all documentation
  must be English. That conflicts with an explicitly requested localized
  README, so the convention must be revised before adding the translation.
- `scripts/test_open_source_contract.py` owns the public-file, local-link, and
  owner-specific-anchor checks.

## Requirements

- Keep `README.md` as the canonical English README.
- Add `README.zh-CN.md` as a complete Simplified Chinese translation of the
  root README. Preserve commands, paths, schema names, URLs, verified
  limitations, and privacy boundaries exactly where translation would change
  their technical meaning.
- Add reciprocal `English | 简体中文` navigation near the top of both README
  files.
- Add these verified open-source badges near the top of both README files:
  GitHub Actions CI, MIT License, Python 3.11+, Vanilla JavaScript, and PRs
  Welcome. CI and contribution badges must link to their relevant repository
  surfaces; local license and contribution links must remain valid.
- Revise the duplicated backend/frontend documentation-language convention to
  keep English canonical while permitting explicitly localized entry-point
  documents that link back to the canonical source and remain synchronized.
- Extend the open-source contract so `README.zh-CN.md` is a required,
  current-facing public file, and so its local links and forbidden
  owner-specific anchors are checked.
- Update `PLAN_web.md` with the resulting current public-entry state without
  adding implementation history or changing product architecture.

## Out Of Scope

- Adding or changing dashboard widget types, data sources, frontend behavior,
  publication, deployment, certificates, schedulers, or live state.
- Translating `web/README.md`, `deploy/README.md`, governance files, or Trellis
  specifications beyond the minimum language-convention change.
- Adding package, coverage, release, download, support, or deployment badges
  whose claims are not backed by current repository evidence.
- Changing GitHub repository settings, branches, pull requests, or releases.

## Acceptance Criteria

- [x] `README.md` links to `README.zh-CN.md`, remains the canonical English
  entry point, and displays only the five verified badges listed above.
- [x] `README.zh-CN.md` links back to `README.md` and is a complete,
  technically faithful Simplified Chinese version of the current root README.
- [x] Both README files use the same screenshot, section coverage, commands,
  project links, privacy boundary, and known limitations.
- [x] Backend and frontend spec indexes consistently document the
  English-canonical/localized-entry exception before the localized README is
  added.
- [x] `scripts/test_open_source_contract.py` fails if the localized README is
  missing, contains a broken local link, or includes a forbidden
  owner-specific anchor.
- [x] `PLAN_web.md` records bilingual public entry and verified badges as
  current state without claiming runtime changes.
- [x] Focused open-source contract tests, the full unittest suite, Python/JS/
  shell/JSON/plist syntax gates, the plan freshness gate, and
  `git diff --check` pass with no skipped required check.

## Key Decisions

- Use a separate `README.zh-CN.md` instead of mixing two full languages into
  one file.
- Treat "common open-source widgets" as README badges, not product dashboard
  widgets.
- Use current repository facts as the badge source of truth; do not add
  aspirational metrics.
- Include the concurrently completed Trellis upgrade files in the final commit
  as explicitly approved existing changes; do not revert or rewrite them as
  part of this README task.

## Risks And Deferred Items

- The two README files can drift later. This task makes the canonical/localized
  relationship explicit and adds contract coverage, but it does not introduce
  translation-generation tooling.
- Badge image availability is an external rendering concern; repository tests
  validate badge claims and local destinations without depending on live badge
  network responses.
