# Gentle Shell and Pi theme pair

## Objective

Give Pi and Gentle Shell a real dark variant so the generated Dreamcoder Dark is
selected as the dark theme of a light/dark pair, instead of a single theme that
ignores the terminal appearance.

## Problem

`settings.json` selects `"theme": "dreamcoder"` in both agent homes. Pi only
switches with the terminal appearance when the setting is a pair
(`"light/dark"`), and a theme must declare a unique `name` that equals its
filename. Today the repo writes `dreamcoder-dark.json` and
`dreamcoder-light.json` whose inner name is `dreamcoder`, so a pair could not
resolve and hot reload would never match the file.

## Scope

- Renderer: emit `appearance` and a mode-suffixed `name`, with an explicit
  override for the legacy stable file.
- Writers: persist the pair in each agent home and select the pair in settings.
- Sync wiring: pass variants through `sync_pi_targets` and the Pi helper script.
- Repository assets: regenerate the two variant files with matching names.
- Tests and the user-facing theme documentation.

Out of scope: live activation, restarting a Pi session, the macOS and Linux
launchers, and any change to the stable `dreamcoder.json` selection path.

## Tasks

- [x] T1 (RED): Extend `tests/test_pi_theme_generation.py` and the shell test
      with the contract below and observe them fail.
- [x] T2: `pi_theme_content(c, *, name=None)` emits `appearance` and defaults the
      name to `dreamcoder-<mode>`.
- [x] T3: `ensure_pi_theme_settings` writes
      `"dreamcoder-light/dreamcoder-dark"`; `sync_pi_targets` writes both
      variant files next to the stable theme in each agent home and keeps
      `dreamcoder.json` named `dreamcoder`.
- [x] T4: Thread `variants` through `sync_active_targets` and
      `DreamcoderPi/.pi/agent/scripts/pi-theme.sh`; regenerate the repository
      variant assets.
- [x] T5: Document the pair, the appearance field and the legacy stable file in
      `docs/configuration/theme-system.md`.

## Acceptance criteria

- Both agent homes contain `dreamcoder-light.json` and `dreamcoder-dark.json`
  whose `name` equals the filename and whose `appearance` matches the mode.
- Both settings files contain `"theme": "dreamcoder-light/dreamcoder-dark"`.
- The three theme files in an agent home declare three distinct names.
- The legacy `dreamcoder.json` keeps `"name": "dreamcoder"` and the active
  palette.
- No duplicate resource names are produced.

## Checks

```bash
.venv/bin/pytest -q tests/test_pi_theme_generation.py tests/test_dreamcoder_writers.py \
  tests/test_dreamcoder_sync.py tests/test_control.py tests/test_registry_purity.py
.venv/bin/pytest -q tests/
bats tests/shell/test_pi_theme.bats
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests
.venv/bin/mypy --config-file=pyproject.toml src
scripts/verify-theme-health.py
scripts/validate-markdown-links.py
```

Tests must never touch the real `~/.pi` or `~/.gentle-shell`; use `tmp_path` and
environment overrides.

## Delivery

Single work unit committed on `feat/dark-design-benchmark`; it joins the pending
chained PR slice. No PR or merge is created from this task.

## Delivery record (2026-10-23)

Commit `c8485c2` (now `d3f4489` after the commitlint subject rewrite) delivered the pair: 14 files, +120/-32. Hooks passed on the commit, and the clean-worktree closure run at the same tree reported full pytest, ruff, mypy, health, markdown links and 88 bats assertions green.

Live application to `/home/dreamcoder08/.gentle-shell/agent` and `/home/dreamcoder08/.pi/agent` (backup at `/home/dreamcoder08/.tmp/opencode/gentle-shell-backup-20261023-234906`):
- `themes/dreamcoder.json` name `dreamcoder`, appearance `dark`, regular file.
- `themes/dreamcoder-dark.json` name `dreamcoder-dark`, appearance `dark`.
- `themes/dreamcoder-light.json` name `dreamcoder-light`, appearance `light`.
- `settings.json` theme `dreamcoder-light/dreamcoder-dark` in both homes.
The three repository assets are now byte-identical to their live counterparts. A running session needs a restart to load the new pair.

Chained delivery: slice A branch `fix/dark-ansi-cyan` (PR #28 to `main`) and slice B branch `feat/dark-design-benchmark` (PR #29 to `fix/dark-ansi-cyan`). PR #28 CI is fully green, including commitlint, after rewriting the eight subject lines to lower-case; slice B reports no checks because `commitlint.yml` only runs for pull requests to `main`.

Correction found during closure: the working-tree copy of `DreamcoderPi/.pi/agent/themes/dreamcoder.json` had been overwritten with the dark variant name (`dreamcoder-dark`), which would collide with the dark file. It was restored from `c8485c2` and re-checked byte-for-byte against the live file.
