# Install Dreamcoder Workbench on Linux

For an Arch Linux or derivative desktop with Gentleman.Dots and ML4W, follow the
[canonical full installation guide](../../INSTALL.md). It covers prerequisites,
configuration changes, verification, upstream relinking and recovery. Other
Linux distributions and individual integrations are not automatically guaranteed
compatible.

## Component-only exploration

If you do not want the desktop overlay, clone the repository and install only
its Python package in a virtual environment as described in the
[full installation guide](../../INSTALL.md). Do not run
`./scripts/dreamcoder install` unless you intend to apply its home-directory
changes and Linux desktop hooks.

With the environment active, inspect the package CLI:

```bash
dreamcoder-theme --help
dreamcoder-theme installer plan --json
```

The package command is the control CLI; it does not provide a `sync` subcommand.
The plan describes installer targets, not a promise of compatibility. To generate
themes separately, the repository wrapper offers `./scripts/dreamcoder sync`;
this writes generated configuration and potentially repository files, so review
the [theme system guide](../configuration/theme-system.md) and back up affected
configuration before using it. Generated files alone do not ensure that an
application loads them.

Return to the [documentation hub](../README.md) for configuration and other
platform guides.
