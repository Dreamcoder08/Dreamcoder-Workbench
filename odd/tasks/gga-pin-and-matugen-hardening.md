# GGA model pin and Matugen ownership hardening

## Objective

Every gga review runs on OpenAI `gpt-6.1-sol` at `medium` reasoning in every project, and
that survives `gentle-ai sync`; Dreamcoder-owned colour files are never overwritten by
Matugen. Record written retroactively (2026-09-30): the work started as small fixes and
grew, so the tasks and evidence below are reconstructed from the merged PRs.

## Problem

- gga's codex provider runs `codex exec "<prompt>"` with no model flag, and ~50 project
  `.gga` files pick other providers.
- `gentle-ai sync` (default scope includes GGA) rewrites the whole `~/.config/gga/config`
  unconditionally (gentle-ai 3.7.0 `internal/components/gga/config.go`,
  `internal/cli/sync.go:1158-1170`), so a pin kept only in that file is lost.
- Matugen rewrote `hypr/colors.conf`, `hypr/colors.lua`, `waybar/colors.css`,
  `rofi/colors.rasi` and, through a symlink into Waybar, `swaync/colors.css`. Restoring the
  colours afterwards was a race that could be lost.
- The Codex quota is account-wide and shared across models (`gpt-6-sol` hit the same limit),
  and `STRICT_MODE=true` turns a provider failure into a blocked commit.

## Constraints

- Never edit other repositories' `.gga`; never fabricate a `PASSED` verdict.
- Interactive `codex` and `~/.codex/config.toml` stay untouched.
- Hooks live in Dreamcoder-owned files or in marked, idempotent, reversible blocks.
- TDD: off (no project configuration); every behaviour change got a test that fails without
  it. Runners: `bats tests/shell/ tests/ml4w/`, `python -m pytest tests/`.
- Delivery: one PR per work unit, merge commits, CI green on each.

## Tasks

- [x] G1 — Point the repo `.gga` at codex and document the pin. PR #18.
- [x] G2 — Shim (`scripts/gga-codex-shim.sh`) that pins model/effort only for `codex exec`
  under a `gga` ancestor, installer (`scripts/install-gga-pin.sh`), `pin.env`, marked config
  block, `environment.d`, shell wiring, `dreamcoder repair` hook, docs. 16 tests. PR #21.
- [x] G3 — Found by simulating a `gentle-ai` rewrite: in fish the shim sat behind the real
  codex (`fish_user_paths` outranks PATH). Add it to `fish_user_paths` from `config.fish`
  with `--move`. PR #22.
- [x] G4 — Codex quota exhausted: `STRICT_MODE="false"` in the marked block so an unavailable
  provider does not block commits while a real `STATUS: FAILED` still does. PR #23.
- [x] G5 — Backfill review of the files skipped during the outage found real defects:
  indented TOML headers swallowed the next template; membership-only PATH checks; adjacent
  duplicates; PATH rule centralised in `lib/gga-shim-path.sh`. PR #24.
- [x] M1 — Disable the five Matugen templates that write Dreamcoder-owned files (marked,
  idempotent, validated as TOML), plus hardening of `apply-ml4w-hooks.sh` (escaped generated
  shell, `timeout(1)` guard, hostile-path test). PR #20.
- [x] M2 — `verify-ml4w-setup.sh`: `path_is_ml4w_managed`, paths passed to Python via argv,
  jq/jsonschema absence reported instead of misreported. PR #19.

## Acceptance criteria

- A gentle-ai-style config rewrite followed by the installer restores codex; with the shell
  environment alone `GGA_PROVIDER=codex` survives the rewrite. Verified by simulation.
- A fresh fish resolves `codex` to the shim first; the real codex stays reachable.
- A real dark to light and the 18:00 timer switch leave the four colour files as Dreamcoder
  colours; `verify-ml4w-setup.sh` 23 passed / 0 failed.

## Progress

- Live on 2026-09-30: installer applied, `verify-ml4w-setup.sh` 23/0, bats 192 ok, pytest
  exit 0, CI green on every merged PR.
- Lessons: run GGA-gated commits in the background (1–3 min); export every isolation variable
  in suites that run with the real HOME (a leak once broke the live wallpaper runner); a
  test that cannot fail is worse than none (a vacuous injection test was removed).

## Decision (2026-09-30)

An earlier count of "~31" project `.gga` files with `STRICT_MODE="true"` was wrong: a full scan
finds 72 checkouts of 15 repositories (50 of them worktrees of one `arkelythex` organisation
repository), all tracked by git, so the value is committed project policy rather than a personal
preference. The user chose **not to touch them**: during a Codex outage those repositories keep
blocking commits, and `git commit --no-verify` is the escape hatch (documented in
`docs/configuration/gga.md`). Changing them would mean editing tracked files in other
repositories, so it needs a per-repository decision by their owners.

## Next step

Feature complete; nothing pending.
