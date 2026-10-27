# Dreamcoder Workbench on WSL

Use this component-only path inside a WSL distribution, not as a full desktop
setup. WSL distributions, Windows versions and individual integrations have not
been established as compatible. The full installer applies Linux desktop hooks
and attempts a systemd user timer; do not run it as a general WSL host setup.

## Install the Python package only

Make Git and Python 3.11 or newer, including virtual environment and pip
support, available in the distribution. Then run inside WSL:

```bash
git clone https://github.com/Dreamcoder08/Dreamcoder-Workbench.git
cd Dreamcoder-Workbench
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
dreamcoder-theme --help
```

If `python3` is older, create the environment with an available Python 3.11+
interpreter. Pip installs the declared Jinja2 dependency in that environment.
The help output lists the control CLI commands; the package CLI has no `sync`
subcommand. Reactivate the environment when returning: the repository wrapper
calls `python3` and needs its dependencies available.

## Before generating configuration

The repository's `./scripts/dreamcoder sync` writes generated configuration and
may write repository files. Back up affected configuration and review the
[theme system guide](../configuration/theme-system.md) before running it.
Generated files do not automatically configure Windows Terminal or ensure an
application loads a theme. User systemd availability depends on the WSL setup;
do not assume the timer or desktop integrations work. Installing the package
alone does not apply the full overlay.

For the intended Linux desktop, see the [full installation guide](../../INSTALL.md);
return to the [documentation hub](../README.md) for other guides.
