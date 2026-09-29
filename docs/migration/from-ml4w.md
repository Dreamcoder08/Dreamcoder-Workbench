# Migrating from ML4W

## What Changes

- Theme system: Material You → Token-based (Dreamcoder Workbench)
- Installer: QML app → Go binary TUI
- Config location: `~/.config/ml4w/` → `~/.config/dreamcoder/`

## Migration Steps

1. Backup ML4W config:

   ```bash
   cp -r ~/.config/ml4w ~/.config/ml4w-backup
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

4. Select components to migrate

5. Verify the migration:

   ```bash
   ./scripts/dreamcoder doctor
   ```

6. Remove ML4W when satisfied:

   ```bash
   rm -rf ~/.config/ml4w
   ```

## Preserved Settings

- Shell aliases and functions
- Neovim keymaps (mostly compatible)
- Git config (stays in `~/.gitconfig`)

## Rollback

The installer writes a backup manifest under `~/.local/share/dreamcoder/backups/` before changing configs. To restore, run `./scripts/dreamcoder backup restore <backup_id> --json` with the backup id shown during install. Your `~/.config/ml4w-backup` copy remains untouched until you remove it.

## Differences

| Feature | ML4W | Dreamcoder Workbench |
| --- | --- | --- |
| Theme source | Wallpaper (Material You) | tokens.json |
| Light/Dark schedule | Manual | Systemd timer |
| Health checks | None | WCAG/APCA |
