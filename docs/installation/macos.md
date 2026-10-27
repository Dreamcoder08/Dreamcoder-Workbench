# Dreamcoder Workbench on macOS

This is a component-only path, not the full ML4W desktop installation. macOS
versions and individual integrations have not been established as compatible.
The full installer applies Linux desktop hooks and attempts a systemd user timer;
do not run it on the host as a general macOS setup.

## Install the Python package only

Install Git and Python 3.11 or newer using your preferred trusted source. Then:

```bash
git clone https://github.com/Dreamcoder08/Dreamcoder-Workbench.git
cd Dreamcoder-Workbench
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
dreamcoder-theme --help
```

Use a Python 3.11+ interpreter to create the environment if `python3` is older.
The package declares Jinja2; pip installs it in the virtual environment. The
help output lists the control CLI commands, not a package `sync` subcommand.
Reactivate the environment when returning to the clone; the repository wrapper
calls `python3` and needs its dependencies available.

## Before generating configuration

The repository's `./scripts/dreamcoder sync` writes generated configuration and
may write repository files. Back up affected configuration and review the
[theme system guide](../configuration/theme-system.md) before running it. A
generated theme does not mean an installed application will load it, and Linux
hooks, desktop integration and timer behavior should not be assumed to work on
macOS. Package installation alone does not apply the full overlay.

For the intended Linux desktop, see the [full installation guide](../../INSTALL.md);
for other topics, return to the [documentation hub](../README.md).
