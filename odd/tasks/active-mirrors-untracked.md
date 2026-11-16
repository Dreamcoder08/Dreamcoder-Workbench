# Active-mode mirrors out of git

Objective: switching Light/Dark must leave `git status` clean, so the Herdr budget chip and `git status` show only real work; generated active-mode files stop being tracked while CI, tests, stow and a fresh clone keep working.
Branch: `chore/untrack-active-mirrors` from `main`. Delivery: ask-on-risk, work-unit commits, one PR to `main` (size:exception only for the `git rm --cached` list if needed). Test runner: `python3 -m pytest -q`, `scripts/verify-theme-health.py`, `PYTHONPATH=src scripts/verify-repo-sync.py`, a mode flip (`./scripts/dreamcoder sync` in Light and in Dark) followed by `git status --short`.

## Specs

- **S1 — Status limpio al cambiar de modo.** User: "yes haslo todo debe estar 10/10 y actualizado", accepting the proposal "dejar de trackear esos espejos activos para que `git status` y el chip reflejen solo trabajo real". Acceptance: after a sync in Light and again in Dark, `git status --short` lists no tracked file changed by the mode (only pre-existing user edits remain).
- **S2 — Pure mirrors are generated, not tracked.** Every file whose content is fully determined by tokens + active mode is gitignored and removed from the index; the sync still writes it at the same path, so every consumer (stow links, sourced snippets, app configs, copy-style apps) keeps working.
- **S3 — Stow-routed mirrors get a repo write.** Files that today reach the repo only through a live symlink (`DreamcoderShell/.config/starship.toml`, `DreamcoderGhostty/.config/ghostty/themes/dreamcoder`, `DreamcoderTmux/.config/tmux/tmux-dreamcoder.conf`, `DreamcoderBat/.config/bat/themes/Dreamcoder.tmTheme`, `DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder.yaml`) are also written by the sync's repo pass, so a repo-only sync produces them on a fresh clone before stow needs them.
- **S4 — Hybrids keep a stable selector.** Tracked hand-maintained configs point at a mode-independent alias (`theme = dreamcoder` in Ghostty, a stable theme name in Zellij), and the mode lives only in generated, untracked files. The Fastfetch `default_mode` and the Kitty `colors-dreamcoder.conf` symlink stop changing tracked state on a mode flip (move mode state to an untracked location with a compatible read fallback; untrack the generated symlink).
- **S5 — CI and install keep passing from a fresh clone.** `theme-validation.yml` runs a repo-only sync before `pytest` and `verify-theme-health.py`; the install flow generates the mirrors before stow (shell and Go installer paths). Live `~/.config` targets are not touched by the CI sync.
- **S6 — Docs and guards.** Docs that call these files "checked-in mirrors" are updated (`docs/configuration/theme-system.md`, `docs/DREAMCODER_DESIGN_SYSTEM.md`, the renderer-registry gap note); a test asserts every active mirror path is ignored and untracked and that the hybrids contain the stable alias.

## Tasks

| ID | Specs | Route | Status | Evidence |
|----|-------|-------|--------|----------|
| T1 | S3, S4 | delegated (context backstop) | pending | sync repo writes for stow-routed mirrors; stable selectors; mode state untracked |
| T2 | S2, S5 | delegated (context backstop) | pending | `.gitignore`, CI repo-only sync, install order; parent runs `git rm --cached` |
| T3 | S1, S6 | delegated (context backstop) | pending | guard test, docs, mode-flip proof |
| T4 | S1-S6 | independent verifier | pending | Risk items 5 (CI, install) and 3 (consumed file paths) |

Route declaration: one bounded writer runs T1-T3 in order (they share `sync.py` and `.gitignore`, so no parallel writers); parent owns git; independent verifier for T4 because the change names high-risk items 5 and 3.

## Log

- **L1 (2026-11-16, user):** "yes haslo todo debe estar 10/10 y actualizado" — reply to: "Lo que más impacto tiene es el punto 1: dejar de trackear esos espejos activos para que `git status` y el chip reflejen solo trabajo real. [...] ¿Lo encaro?"
- **L2 (map, explorer):** pure repo writes via `write_active_repo_file` (sync.py:862-878): kitty `dreamcoder-ui.conf`, `.opencode/themes/dreamcoder.json`, Pi `dreamcoder.json`, `DreamcoderThemes/dreamcoder/{hyprland.conf,waybar.css,rofi.rasi}`, `DreamcoderThemes/{zsh-syntax-highlighting-dreamcoder.zsh,ls-colors-dreamcoder.sh,bat-dreamcoder.sh,delta-dreamcoder.gitconfig,fzf-dreamcoder.sh,btop-dreamcoder.theme,dunst-dreamcoder.conf,firefox-dreamcoder.css,obsidian-dreamcoder.css,cava-dreamcoder.config,hyprland.conf,waybar.css,rofi.rasi}`, lazygit `config.yml`, registry active paths (Codex app/CLI, bat). Stow-routed without repo write: starship, ghostty `themes/dreamcoder`, tmux, bat active, warp active. Hybrids: ghostty `config` (`theme =` line), zellij `config.kdl` (`theme` line), fastfetch `settings.json` (`terminal.default_mode`), kitty `colors-dreamcoder.conf` (tracked symlink re-pointed by `apply-theme-mode.sh`). Readers without a prior sync: `theme-validation.yml` (pytest + verify-theme-health), `tests/test_active_mirror_identity_consistency.py`, `test_lazygit_renderer.py`, `test_bat_visual_coherence.py`, `test_terminal_icon_contract.py`, `verify-theme-health.py` (`.opencode` artifact). Install: `dreamcoder-maintenance.sh install` stows before `theme-auto.sh` syncs.
- **L3 (observed):** each hybrid flips exactly one selector line (`theme = dreamcoder-dark` → `dreamcoder`, `theme "dreamcoder-dark"` → `"dreamcoder-light"`, `"default_mode": "dark"` → `"light"`); the tracked Warp active file still holds a pre-Lúcuma Light palette (`#f3eadc`), evidence the tracked copies drift.
