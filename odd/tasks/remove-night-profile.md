# Remove the Night render profile

## Objective

The Dreamcoder design system has exactly two modes: Dreamcoder Light and
Dreamcoder Dark. Remove the Night render profile (derived from Dark) end to end.

## Problem

Night survives as an opt-in profile (`dreamcoder night`, `theme.render_profile`,
`night_palette()`, 33 generated `*-night*` artifacts, Herdr night variants, docs).
The scheduler never activates it, and the 16:00 timer trigger only re-applies Light.

## Why

User decision (2026-09-28): "solo debe tener dreamcoder light y dreamcoder dark".

## Scope

- In: runtime code (palette, settings, settings_store, sync, cli_handlers,
  cli_parser, herdr_switch, renderer_contract, targets, renderers, writers, doctor,
  repair_engine), scripts (apply-theme-mode.sh, dreamcoder dispatcher, theme-auto.sh,
  verify-theme-health.py, generate-theme-preview.py), data files (tokens.json,
  tokens.schema.json, design-system.json, targets.json, targets.schema.json),
  generated `*-night*` artifacts, tests, live docs, systemd timer (drop 16:00),
  live-machine cleanup (settings key, dangling night symlinks).
- Out: the legacy Dusk token set (still used; separate decision); archived openspec,
  CHANGELOG history and docs/superpowers history are not rewritten.

## Constraints

- Light and Dark output must stay byte-identical except where Night logic lived.
- Keep the Light/Dark contrast gate (`validate_palette`) intact.
- `targets.json`, `targets.schema.json` and `renderer_contract` change in the same
  commit (`targets.py` requires modes to match `ALL_RENDER_VARIANTS`).
- Unrelated working-tree edits (timer-rewritten theme files, user's fish prompt,
  warp, apply-system-mode.sh) are never staged.
- TDD: off (no project/session TDD configuration). Runners: `python -m pytest tests/`,
  `bats tests/shell/ tests/ml4w/`.
- Delivery: work-unit commits on `refactor/remove-night-profile` (stacked on
  `chore/ml4w-2.16-gentleman-sync`); forecast ~1,200–1,500 authored lines, mostly
  deletions. Push/PR slicing is the user's decision.

## Tasks

- [x] N1 — Core model: remove Night from palette/settings/settings_store, renderer
  contract, targets manifest + schema, tokens + schema, design-system mode_policy,
  every renderer's `modes` and Night name-sniffing; update affected tests. Route:
  delegated writer. Scope widened to keep the commit green: `sync.py` and the CLI
  activation (`cli_handlers`, `cli_parser`, `herdr_switch`) plus the Python scripts
  that imported `night_palette` (`verify-theme-health.py`, `generate-theme-preview.py`)
  moved here from N2 because they import the removed palette/settings API. COVERAGE
  stays as the 33-consumer declaration keyed by the Dark artifact; Codex app and
  Antigravity coverage now render exactly what `sync_repo_snippets()` writes (active
  palette / Dark-pinned). A persisted legacy `theme.render_profile` is ignored as an
  unknown setting (warning, preserved). Repo-only regeneration: every Light/Dark
  artifact byte-identical; only the generated README, nvim dispatcher and preview
  docs lost their Night lines. Commit: 319ffdd.
- [x] N2 — Scripts + shell tests: `apply-theme-mode.sh` drops the profile argument,
  the Night artifact gate, the kanagawa Night case and `DREAMCODER_THEME_PROFILE`
  (cursor-cli.env no longer writes it; tmux unsets the stale variable); the
  `dreamcoder` dispatcher rejects `night` as an unknown command; `theme-auto.sh`
  stops passing `standard`; `pi-theme.sh` selects by mode only. Bats: Night tests
  (including the failing kanagawa one) deleted and replaced with Light/Dark and
  `night`-rejection coverage. Route: delegated writer. Python parts of the original
  N2 landed in N1 (see above). Commit: 72c173b.
- [x] N3 — Artifacts: deleted the 33 tracked `*-night*` generated artifacts (Herdr
  `config.night.toml` for 0.7.3/0.8.0/0.8.2/0.9.1 included) and the CI workflow's
  Kitty night symlink. Repo-only regeneration afterwards reports 0 changes, so sync
  no longer recreates them. Light/Dark byte-identity vs the pre-N1 baseline: every
  tracked `*dark*`/`*light*` artifact unchanged. The characterization fixtures
  (`tests/fixtures/legacy_*.json`) were intentionally NOT regenerated: they are frozen
  Phase-0 evidence of the legacy 32-consumer sync (no test reads them), a rerun would
  replace the legacy hashes with today's palette and bake machine-specific live
  paths; the harness itself was updated in N1 so it still runs. Route: delegated
  writer. Commit: e9b75fd.
- [x] N4 — Docs + timer: live docs (CLAUDE.md, README, INSTALL, AGENTS, CONTRIBUTING,
  COMPARISON, design system, theme-system/ml4w/editor/terminal/termux, migration,
  herdr + Herdr evidence, palette-token skill), live openspec specs (eye-comfort
  rewritten around Light/Dark + legacy-key tolerance, ml4w-keybindings-waybar,
  renderer-registry), `desktop-arch.json` wording, repo `settings.json` drops
  `theme.render_profile`, and the timer drops the 16:00 trigger ("light/dark"
  wording; schedule is 07:00 light, 18:00 dark). Not touched: archived and
  in-flight `openspec/changes/*`, CHANGELOG, docs/superpowers, the Dusk
  `light_hours_default`/`dusk_hours_default` token metadata. Route: delegated
  writer. Commit: ad41d7b.
- [ ] N5 — Live cleanup: drop `theme.render_profile` from live settings, remove
  dangling `~/.config/starship-night.toml` and Warp `Dreamcoder-Night.yaml` links,
  `systemctl --user daemon-reload`, apply current mode, verify. Route: inline.

## Acceptance criteria

- `git ls-files | grep -i night` returns nothing outside history docs.
- `dreamcoder night` is an unknown command; `dreamcoder light|dark` work.
- pytest and bats green (the kanagawa Night bats test is removed with Night).
- `verify-ml4w-setup.sh` and `dreamcoder doctor` pass after N5.

## Progress

- Verification after N4: `python -m pytest tests/ -q` exit 0; `bats tests/shell/
  tests/ml4w/` 143/143 ok; `verify-theme-health.py` and `verify-repo-sync.py` OK;
  shellcheck/bash -n clean on modified scripts; `git ls-files | grep -i night`
  lists only this feature document.
- Branch created from `chore/ml4w-2.16-gentleman-sync`; shell readability fixes
  (c9cf723, 32f9f6f, ffc5359, 754d352) landed here before the Night work started.

## Next step

N5 (live cleanup, parent-owned).
