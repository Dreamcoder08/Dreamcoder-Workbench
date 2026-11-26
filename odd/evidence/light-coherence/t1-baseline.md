# T1 Baseline — Dreamcoder Light (2026-11-26)

Base: `origin/main` 7e399ce, light mode, repo-only sync (`DREAMCODER_WRITE_LIVE=0`).

## Gates

- `pytest tests/`: exit 0 (all passed). Needs the repo-only sync first: active mirrors are untracked since PR #80, so a fresh worktree fails 33 mirror tests until synced.
- `scripts/verify-theme-health.py`: exit 0.

## Live desktop (`t1-desktop-before.png`)

- Wallpaper paper is more saturated/orange than the UI paper.
- Waybar: saturated red `102` badge and teal `ml.` tile break the palette.
- Hyprland active border is a gradient `#8b440c → #fefdfa` (90°): reads as a heavy orange frame.
- Gentle Shell renders a dark violet "Delegating" block inside the light UI: a dark surface leaking into Light.
- Elevation cues mix borders, flat cards and left rules; no single light model.

## Hex literals

130 tracked files carry hex literals (tests/docs/odd/openspec excluded). A light-accent probe (`#8b440c → #8a450d` in a scratch copy) regenerated 47 files; `palette_tokens.py` and the Neovim colorscheme are generated, not hand-copied.

Files with hex that the probe did not touch (candidates for hand-authored colors; a generated file that never uses the accent also lands here):

- `DreamcoderAlacritty/.config/alacritty/dreamcoder-light.toml`
- `DreamcoderAntigravity/Dreamcoder.json`
- `DreamcoderClaudeCode/.claude/themes/dreamcoder-light.json`
- `DreamcoderGhostty/.config/ghostty/shaders/dreamcoder-cursor-pulse.glsl`
- `DreamcoderHerdr/.config/herdr-app/programs.json`
- `DreamcoderNushell/.config/nushell/dreamcoder-light.nu`
- `DreamcoderNushell/.config/nushell/dreamcoder-theme.nu`
- `DreamcoderNushell/env.nu`
- `DreamcoderShell/.nanorc`
- `DreamcoderShell/.p10k.zsh`
- `DreamcoderThemes/dreamcoder/btop-dreamcoder.theme`
- `DreamcoderThemes/dreamcoder/cava-dreamcoder.config`
- `DreamcoderThemes/dreamcoder/delta-dreamcoder.gitconfig`
- `DreamcoderThemes/dreamcoder/dunst-dreamcoder.conf`
- `DreamcoderThemes/dreamcoder/firefox-dreamcoder.css`
- `DreamcoderThemes/dreamcoder/fzf-dreamcoder.sh`
- `DreamcoderThemes/dreamcoder/ls-colors-dreamcoder.sh`
- `DreamcoderThemes/dreamcoder/obsidian-dreamcoder.css`
- `DreamcoderThemes/dreamcoder/tmux-dreamcoder.conf`
- `DreamcoderThemes/dreamcoder/zsh-syntax-highlighting-dreamcoder.zsh`
- `DreamcoderTmux/.config/tmux/dreamcoder-light.conf`
- `DreamcoderTmux/.config/tmux/tmux-dreamcoder-base.conf`
- `DreamcoderWezTerm/.config/wezterm/dreamcoder-light.lua`
- `DreamcoderYazi/.config/yazi/theme.toml`
- `DreamcoderZellij/.config/zellij/config.kdl.bak.1782968040`
- `DreamcoderZellij/.config/zellij/config.kdl.bak.1782969521`
- `DreamcoderZellij/.config/zellij/config-light.kdl`
- `DreamcoderZellij/.config/zellij/config-light.kdl.bak.1782968040`
- `DreamcoderZellij/.config/zellij/layouts/dreamcoder.kdl`
- `DreamcoderZellij/.config/zellij/layouts/work_everforest.kdl`
- `DreamcoderZellij/.config/zellij/layouts/work_kanagawa.kdl`
- `DreamcoderZellij/.config/zellij/layouts/work.kdl`
- `DreamcoderZellij/.config/zellij/layouts/work_oldWorld.kdl`
- `DreamcoderZellij/.config/zellij/layouts/work_sakura.kdl`
- `scripts/apply-theme-mode.sh`
- `scripts/generate-palette-tokens.py`
- `scripts/status.sh`
- `scripts/verify-theme-health.py`
- `src/dreamcoder_theme/_math.py`
- `src/dreamcoder_theme/renderers_herdr.py`
- `src/dreamcoder_theme/renderers_hypr_waybar_rofi.py`
- `src/dreamcoder_theme/renderers_opencode.py`

## Legacy spotted

- `DreamcoderZellij/.config/zellij/*.bak.*` backup files are tracked.
- Zellij layouts for foreign themes: `work_everforest`, `work_kanagawa`, `work_oldWorld`, `work_sakura`.
- `DreamcoderShell/.p10k.zsh` (Powerlevel10k) next to the Starship prompt.
- `dusk` mode in tokens, engine, schema, installer, docs.
- `scripts/WALLPAPER_SETUP.md` describes a fixed palette that contradicts adaptive matugen.
- `tokens.json` still names "Dreamcoder OS".
