# Installing Dreamcoder Workbench on Termux (Android)

## Prerequisites

- Termux app (from F-Droid, NOT Play Store)
- Android 7+

## Install

```bash
pkg update && pkg upgrade
pkg install stow git python nodejs

git clone https://github.com/Dreamcoder08/Dreamcoder-Workbench.git ~/Dreamcoder-Workbench
cd ~/Dreamcoder-Workbench

# Install the Python theme engine
pip install -e .
# or, with uv:
uv sync

# Run the installer
./scripts/dreamcoder install
```

## Verify

```bash
./scripts/dreamcoder doctor    # Health check
./scripts/dreamcoder status    # System status
```

If the installer was skipped, you can still use the theme engine directly:

```bash
dreamcoder-theme sync
```

## Limitations

- No systemd (light/dark automation unavailable)
- No GUI apps (Kitty/Ghostty unavailable)
- Limited shader support

## Rollback

The installer writes a backup manifest under `~/.local/share/dreamcoder/backups/` before changing configs. To restore, run `./scripts/dreamcoder backup restore <backup_id> --json` with the backup id shown during install. Remove the `~/Dreamcoder-Workbench` directory to uninstall the environment.
