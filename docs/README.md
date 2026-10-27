# Dreamcoder Workbench documentation

Find the next guide for your task, then use the technical references when you
need implementation details. For the project overview and ownership of the
upstream environments, start with the [main README](../README.md).

## Get started

1. Read the [installation guide](../INSTALL.md) for the full desktop journey,
   verification and troubleshooting.
2. Choose the component guides below for the tools you actually use.
3. Read the [source manifest](sources.md) to understand what Dreamcoder
   Workbench owns and what comes from Gentleman.Dots and ML4W.

The full desktop path targets Arch Linux or a derivative with ML4W. The other
platform guides describe component-specific approaches, not a guarantee of a
complete desktop or compatibility for every component.

| Platform guide | Use it for |
| --- | --- |
| [Linux](installation/linux.md) | Linux setup and distribution-specific notes |
| [macOS](installation/macos.md) | macOS components |
| [WSL](installation/wsl.md) | Components in Windows Subsystem for Linux |
| [Termux](installation/termux.md) | Components on Android through Termux |

## Configure your workspace

| Task | Guide |
| --- | --- |
| Configure a terminal | [Terminal configuration](configuration/terminal-config.md) |
| Configure an editor | [Editor configuration](configuration/editor-config.md) |
| Configure a shell or prompt | [Shell configuration](configuration/shell-config.md) |
| Configure a multiplexer | [Tmux and Zellij](configuration/multiplexer-config.md) |
| Set up ML4W profiles and keybindings | [ML4W integration](configuration/ml4w.md) |
| Understand or regenerate themes | [Theme system](configuration/theme-system.md) and [theme preview](generated/dreamcoder-theme-preview.md) |
| Configure the review model | [gga model pin](configuration/gga.md) |
| Explore AI tool integrations | [AI integration](ai-integration.md) and [Herdr integration](herdr.md) |
| Move from an upstream setup | [Gentleman.Dots migration](migration/from-gentleman.md) or [ML4W migration](migration/from-ml4w.md) |

## Develop and maintain

- [Contributing](../CONTRIBUTING.md) covers development setup, tests and pull requests.
- [Design system](DREAMCODER_DESIGN_SYSTEM.md) describes visual identity and
  color guidelines; [dark theme validation](configuration/dark-theme-validation.md)
  records validation details.
- [Control Center](DREAMCODER_CONTROL_CENTER.md) describes the control dashboard.
- [PyPI publishing](pypi-publishing.md) covers package release maintenance.
- [Operator report](generated/DREAMCODER_OPERATOR_REPORT.md) is a generated
  technical report, not an installation guide.

## Architecture and reference

These resources explain implementation and decisions rather than the onboarding path.

- [Theme pipeline](architecture/theme-pipeline.mmd), [data flow](architecture/data-flow.mmd)
  and [monorepo structure](architecture/monorepo-structure.mmd) are Mermaid diagrams.
- [Source manifest](sources.md) describes upstream pins and ownership;
  its [machine-readable manifest](upstream-manifest.json) and
  [schema](upstream-manifest.schema.json) support maintenance.
- Architecture decision records: [project structure](adr/0001-project-structure.md),
  [toolchain selection](adr/0002-toolchain-selection.md),
  [Python quality](adr/0003-python-quality-strategy.md),
  [shell testing](adr/0004-shell-test-strategy.md) and
  [CI/CD quality gates](adr/0005-ci-cd-quality-gates.md).

## Historical designs and plans

[Design specifications](superpowers/specs/) and [implementation plans](superpowers/plans/)
record project proposals and past work. They are context, not necessarily current
setup instructions. The [prefix restructure proposal](architecture/sdd-prefix-restructure/01-proposal.md)
is also architectural history; use the current guides above for onboarding.
