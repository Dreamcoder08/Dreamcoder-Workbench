# Changelog

## Unreleased

### Added

- Conservative setup integration for the ML4W network launcher, preserving custom scripts, existing backups, and write-free dry runs.
- Process-local `dreamcoder-nmtui` launcher with terminal-native inverse selection, Fish/Zsh routing, and a Waybar default entry point; explicit Newt style overrides remain supported.
- PEP 621 packaging: `pyproject.toml` with setuptools build backend, `__version__` in package.
- `dreamcoder-theme` CLI entry point (`dreamcoder-theme sync|doctor|paths`).
- `Makefile` with targets: install, test, coverage, build, clean, lint.
- `CONTRIBUTING.md` with dev setup guide, test runner, and PR workflow.
- PyPI trusted publisher CI workflow — auto-publishes on `v*` tag pushes.
- CI test matrix: Python 3.11 + 3.12, coverage reporting, lint.
- Automated terminal readability guardrails for ANSI colors, cursor contrast, and selection contrast.
- Design system governance documentation for Dreamcoder Workbench's product definition, token contract, component model, accessibility policy, and release readiness checklist.
- Global design-system regression tests covering APCA dark diagnostic contrast, governance docs, README discoverability, and changelog discipline.
- RGBA token validation in `verify-theme-health.py` with structured format checking.
- Multi-target validation in `verify-theme-health.py` (Kitty, Ghostty, Waybar, Hyprland, Rofi, Btop, Dunst, Fzf).
- GitHub Actions workflow (`.github/workflows/theme-validation.yml`) for CI theme checks.
- Pre-commit hooks (`.pre-commit-config.yaml`) for local validation.
- Flexible systemd service path resolution via `dreamcoder-run.sh` helper.
- `rgba_color` definition added to `tokens.schema.json`.

### Changed

- Refreshed the active generated theme snapshot to Dreamcoder Light while retaining the named Dark variants.
- **Prefix restructure**: 22 directories renamed with the `Dreamcoder*` prefix (Gentleman.Dots style). Config tools (Alacritty → DreamcoderAlacritty, Kitty → DreamcoderKitty, etc.), AI configs (Pi → DreamcoderPi, Codex-*→ DreamcoderCodex*, Antigravity → DreamcoderAntigravity), and assets (themes → DreamcoderThemes, Wallpapers → DreamcoderWallpapers, profiles → DreamcoderProfiles). Infra (src, tests, installer, scripts, docs) keeps standard names.
- Updated all internal references: Go installer, Python theme engine, scripts, tests, docs, CI workflows, .gitignore, CODEOWNERS.
- Symlink `unknown` converted from absolute to relative.
- **Default dark**: `theme_mode()` of the engine and `DREAMCODER_THEME_MODE` in fish now default to `dark` (Anthracite Steel) — a clean environment (CI, new shell) no longer regenerates or sources the legacy light palette.
- **Untrack `colors-matugen.conf`**: the matugen palette (derived from the wallpaper) is no longer tracked; the `.gitignore` now works as intended.
- **`cat`/`gl` in fish**: `cat` aligned to `bat --paging=never`; the dead `gl` alias removed (redundant with `glg` and shadowed by the abbr `--oneline -20`).
- **Theme preview regenerated** for the Anthracite Steel migration (unblocks the CI uncommitted-changes gate).
- README restructured: PyPI package section added above the dotfiles installation guide.
- APCA thresholds aligned to 2025-2026 research (Lc 75/30/45, no dark-mode special case).
- Updated the `visual health policy` section in README with the APCA advisory status.
- `check_apca_or_warn()` now logs advisory warnings instead of failing (WCAG stays authoritative).
- Visual regression test now skips missing plugin dependencies gracefully.
- Hyprland renderer converts RGBA to ARGB compact format automatically.

### Fixed

- Repository sync regression tests derive the current upstream pin instead of relying on a historical hash.
- Zsh sources Bun completions only from nonempty regular files, preserving support for symlinks to regular files.
- Pi and Gentle Shell Light use cream chrome surfaces and brown focus roles, including the medium-thinking editor border, without changing Dark.
- Zsh checks the optional Starship transience function with native syntax instead of Fish's unsupported `functions -q` option.
- **Hyprland rgba converter**: `_rgba_to_argb` used `zfill(2)`, which only pads and never truncates, generating invalid 10-char `rgba()` values (e.g. `rgba(13811588ed)`). Now clamps with `int():02x` + conversion guard + regression tests.
- **Anthracite Steel migration**: the dark palette propagated to the 24 tracked consumers (opencode, firefox, waybar, dunst, rofi, btop, obsidian, hyprland, zsh-syntax, etc.), regenerated with the engine and verified by idempotency.
- **Engine writers**: `write_if_changed` normalizes to exactly one final newline (POSIX), removing the `end-of-file-fixer` hook churn on every commit.
- **opencode health gate**: the `.opencode/themes/dreamcoder.json` check is now mode-aware (accepts dark/light/night per the declared contract) instead of hardcoding light — the clean checkout kept failing after the migration.
- **`ls` icons in fish**: the abbrs shadowed the aliases; listings are now abbrs with `--icons=always` and an eza guard, and `16-dreamcoder-icons.fish` stays only as a fallback without eza.
- **Symlink `unknown` (root cause)**: the repair planner copied the detected-mode string (`detail`) as the symlink target; now an explicit absolute target (kitty colors) + a guard that rejects non-absolute targets. The bug should not reappear.
- **Hermetic test suite**: `test_pi_theme_generation` spawned sync without isolating the `DREAMCODER_*_THEME` env vars, writing repo assets (a light run left the files in light). Isolated with env vars → `pytest` no longer dirties the working tree.
- **Repo-only generation**: `sync_repo_snippets` now also writes the repo-root assets (two consumer sets: apps that copy vs desktop with symlinks), eliminating drift between them.
- **CI pipeline unblocked**: the 3 workflows (CI, Integration Test, Repository Sync Enforcement) pass again. The sync module gained the `__main__` guard (the documented `python -m dreamcoder_theme.sync` command did nothing); shellcheck in CI uses `--severity=warning` (SC1091 info); the integration test completes the install mock (symlinks of themes dir + kitty variants, fish/starship installed) and the bat contract test aligns with the canonical format.
- **Toolchain up to date (Aug 2026)**: pre-commit-hooks v6.0.0, ruff-pre-commit v0.16.2 (PLR0917 added to ignore, consistent with PLR0913), mirrors-mypy v2.3.0, shellcheck-py v0.11.0.1. GitHub Actions pinned by commit SHA at current majors (checkout v7.0.1, setup-node/python/go v7, upload-artifact v7.0.1); commitlint on Node 24; Python matrix +3.14. uv and ruff updated locally (uv 0.12.3, ruff 0.16.2).
- Fixed 5 malformed `inactive_border` RGBA values in `tokens.json` and `palette_tokens.py`.
- Corrected the APCA implementation to spec (polarity-aware exponents, black soft-clamp, hysteresis offset).
- Fixed opencode `textSelected` in light mode — selection text now inverts to the background color instead of using the main text color.

### Known Tradeoffs

- Dark `diagnostic` color (#5f95ca) scores APCA Lc 42.7 (below 75 advisory) but WCAG 6.00:1 (AA pass).
- Dark `border_ui` scores APCA Lc 25.1 (below 30 advisory) but WCAG 3.60:1 (passes UI requirement).
