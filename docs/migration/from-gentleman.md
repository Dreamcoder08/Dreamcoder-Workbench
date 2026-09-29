# Migrating from Gentleman.Dots

## What Changes

- AI layer: Separate (gentle-ai) → Integrated (gentle-ai + per-agent themes and AI session state)
- Installer: Go binary → Go binary (different TUI)
- Shell: Same (Fish/Zsh) + Nushell added

## Migration Steps

1. Backup Gentleman config:

   ```bash
   cp -r ~/.config/gentleman ~/.config/gentleman-backup
   ```

2. Install Dreamcoder Workbench:

   ```bash
   git clone git@github.com:Dreamcoder08/Dreamcoder-Workbench.git
   cd Dreamcoder-Workbench
   pip install -e .
   # or, with uv:
   uv sync
   ```

3. Run the installer:

   ```bash
   ./scripts/dreamcoder install
   ```

4. Set up the AI layer:
   Dreamcoder Workbench keeps the upstream `gentle-ai` stack and adds dedicated
   themes for the coding agents you already use (Claude Code, OpenCode, Codex CLI,
   and Pi) plus a live AI session state in the Starship prompt. There is no separate
   "dreamcoder-ai" product to install — the integration ships with this repository.
   See [AI Integration](../ai-integration.md) for setup and per-agent details.

5. Verify the migration:

   ```bash
   ./scripts/dreamcoder doctor
   ```

6. Remove Gentleman when satisfied:

   ```bash
   rm -rf ~/.config/gentleman
   ```

## Preserved Settings

- Fish shell config (compatible)
- Neovim LazyVim (compatible)
- Tmux config (compatible)
- Ghostty config (similar structure)

## Rollback

The installer writes a backup manifest under `~/.local/share/dreamcoder/backups/` before changing configs. To restore, run `./scripts/dreamcoder backup restore <backup_id> --json` with the backup id shown during install. Your `~/.config/gentleman-backup` copy remains untouched until you remove it.

## Differences

| Feature | Gentleman | Dreamcoder Workbench |
| --- | --- | --- |
| Theme | Hardcoded | Token-based |
| AI layer | gentle-ai | gentle-ai + agent themes (see [AI Integration](../ai-integration.md)) |
| Vim trainer | ✓ | ✓ (improved) |
| Light/Dark schedule | — | ✓ Systemd timer |
| Health checks | — | ✓ WCAG/APCA |
