# Install Dreamcoder Workbench on an ML4W desktop

This is the canonical full desktop path: install the Gentleman.Dots base and
ML4W first, then apply the Dreamcoder Workbench overlay. It is intended for an
Arch Linux desktop or derivative; it is not a guarantee for every distribution,
release, application or hardware combination. For component-only use, see the
[Linux](docs/installation/linux.md), [macOS](docs/installation/macos.md),
[WSL](docs/installation/wsl.md) and [Termux](docs/installation/termux.md) guides.

## Before you start

- Review the upstream installation requirements and make an independent backup
  of your home configuration and any data you cannot lose. Keep the backup
  outside paths the installer will change.
- You need Git, GNU Stow, Python 3.11 or newer, a Python virtual environment
  with pip, and an internet connection for dependencies. The theme package
  declares Jinja2 as a dependency.
- Run the commands below as your normal user, not as root. The installer changes
  files and links in your home directory, applies hooks, attempts to enable a
  user systemd timer and runs automatic theme selection. Review the plan before
  deciding to proceed. A working user systemd session is needed for the timer.

## 1. Set up the upstream environments

1. Follow the current [Gentleman.Dots instructions](https://github.com/Gentleman-Programming/Gentleman.Dots)
   for its shell, editor and terminal base. Select the components you need.
2. Follow the official [ML4W instructions](https://ml4w.com/os/) for the
   Hyprland desktop. Complete upstream setup before applying this overlay.

These projects own their installers and prerequisites; consult their current
instructions rather than assuming an old command or release applies.

## 2. Get the overlay and prepare Python

Choose a location you intend to keep: Stow links can point into the clone.

```bash
git clone https://github.com/Dreamcoder08/Dreamcoder-Workbench.git
cd Dreamcoder-Workbench
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Check that the displayed Python version is at least 3.11 before creating the
virtual environment. If your default `python3` is older, create the environment
with an available Python 3.11+ interpreter instead. Installing the package in
that environment also installs its declared Jinja2 dependency. Reactivate the
same environment in each new shell before running the wrapper: it invokes
`python3`, and exposing the source tree alone does not install dependencies.

## 3. Inspect, then install

From the clone, with the environment active:

```bash
./scripts/dreamcoder installer plan --json
```

The plan reports managed targets and potential conflicts. It is an inspection,
not a substitute for reviewing your existing configuration or a complete list
of every hook and generated file. If the changes are acceptable, run:

```bash
./scripts/dreamcoder install
```

The installer creates a backup manifest for selected targets and prints its ID;
record that ID. It stows shell, terminal, fastfetch, bat, Warp and systemd
modules into the home directory, applies ML4W and CLI hooks, attempts to enable
the user timer, and runs automatic theme selection. These operations can change
existing configuration and generated files; the manifest is not a complete
snapshot of every side effect. Timer enablement can fail without failing the
installation, so verify it separately.

Stow conflicts are a separate preservation mechanism: the installer moves
blocking files or foreign symlinks to
`~/.local/share/dreamcoder/install-conflicts/<backup-id>/`, preserving their
home-relative paths. A symlink is moved as a link, not followed. This location
uses `$XDG_DATA_HOME` when set. Inspect and retain both the manifest backup and
conflict directory; neither replaces an independent backup.

## 4. Verify and choose a mode

```bash
./scripts/dreamcoder doctor
./scripts/dreamcoder status
systemctl --user status dreamcoder-theme-auto.timer
```

Doctor reports health findings rather than promising every optional component
is present. Status compares several generated configurations with the scheduled
mode and can report mismatches, including after a manual mode change. The timer
status may be inactive if user systemd or timer enablement is unavailable.
Investigate reported findings for the components you actually use.

To apply a mode manually, knowing that this writes configuration and may reload
integrations:

```bash
./scripts/dreamcoder dark
# Or: ./scripts/dreamcoder light
```

Automatic selection defaults to light from 07:00 until 18:00 and dark otherwise;
local settings can change the window. Applications may require their own reload
or may not consume the generated theme automatically.

## Recovery and troubleshooting

- **Missing Python module or Jinja2:** activate the environment and repeat the
  package installation in step 2. Confirm `python3 --version` in that shell.
- **Missing Stow:** install GNU Stow using your distribution's package manager,
  then review the plan again. Do not run pip with sudo.
- **Upstream upgrade changed links:** ML4W may re-point shell or terminal targets
  to its own tree. Inspect the plan and your backups before running
  `./scripts/dreamcoder repair`. Repair also backs up, relinks where Stow is
  available, applies hooks, attempts the timer and runs theme selection. Conflicts
  are moved to a new conflict directory; copy any still-needed upstream data, such
  as fish universal variables, back by hand after inspecting both locations.
- **Theme or timer mismatch:** check doctor, status and the user timer output above;
  confirm that the affected application is installed and reads its configuration.
  Avoid assuming every integration is supported on your machine.

To inspect available manifests and preview a restore, use the ID printed during
installation (replace `BACKUP_ID` with that ID):

```bash
./scripts/dreamcoder backup list --json
./scripts/dreamcoder backup restore BACKUP_ID --dry-run --json
```

After inspecting the paths and independently preserving newer changes, omit
`--dry-run` to restore that manifest. Restore replaces or removes the selected
paths according to their pre-install state; it does not necessarily undo all
hooks, generated files, timer state or Stow links. Inspect the separate conflict
directory as well. Do not delete the clone as an uninstall shortcut: remaining
links may depend on it. Review and remove or restore individual changes only
when you understand their ownership.

## Next steps

See the [documentation hub](docs/README.md) for configuration guides, the
[theme system](docs/configuration/theme-system.md) for synchronization, and the
[source manifest](docs/sources.md) for upstream ownership.
