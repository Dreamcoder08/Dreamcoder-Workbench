# Dreamcoder Workbench — Documentation

Welcome to the Dreamcoder Workbench documentation hub. This index centralizes
all the technical documentation for the project.

## New here? Quick path

New to Dreamcoder Workbench? Here is the shortest path:

1. Start with the [main README](../README.md): overview, badges, and the 3-step install.
2. Read the [Source Manifest](sources.md) to understand what is upstream and what the repo owns.
3. Go deeper into the [Theme System](configuration/theme-system.md) if you work with colors or tokens.
4. Review the [Design System](DREAMCODER_DESIGN_SYSTEM.md) for the identity and contrast guidelines.

---

## Architecture

High-level documentation on how the system is built and how it works.

| Document | Description |
|-----------|-------------|
| [Theme Pipeline](architecture/theme-pipeline.mmd) | How tokens from `tokens.json` flow through the renderers to the final theme files |
| [AI Integration](ai-integration.md) | How Dreamcoder Workbench integrates with Claude Code, OpenCode, Pi, and other AI tools |
| [Monorepo Structure](architecture/monorepo-structure.mmd) | Visual map of the repository: `src/`, `scripts/`, `tests/`, and every top-level directory |
| [Data Flow](architecture/data-flow.mmd) | Full flow of `dreamcoder-theme sync`: palette → tokens → renderers → writers → disk |
| [Source Manifest](sources.md) | Upstream inputs (ML4W, Gentleman.Dots), ownership boundaries, and prohibitions on secrets/runtime state |
| [Herdr Integration](herdr.md) | Herdr 0.7.3/0.8.0/0.8.2/0.9.1 contracts, versioned generated variants, and deployment profiles |
| [Design System](DREAMCODER_DESIGN_SYSTEM.md) | Design principles, color philosophy, and visual identity guidelines |
| [Control Center](DREAMCODER_CONTROL_CENTER.md) | Central control dashboard for the Dreamcoder Workbench ecosystem |

### Architecture Decision Records (ADRs)

| ADR | Title | Status |
|-----|--------|--------|
| [ADR-001](adr/0001-project-structure.md) | Monorepo Project Structure Layout | Accepted |
| [ADR-002](adr/0002-toolchain-selection.md) | Python and Shell Quality Toolchain | Accepted |
| [ADR-003](adr/0003-python-quality-strategy.md) | Python Quality Strategy | Accepted |
| [ADR-004](adr/0004-shell-test-strategy.md) | Shell Test Strategy | Accepted |
| [ADR-005](adr/0005-ci-cd-quality-gates.md) | CI/CD Quality Gates | Accepted |

---

## Installation

Step-by-step guides to install Dreamcoder Workbench on different platforms.

| Guide | Platform |
|------|-----------|
| [Linux](installation/linux.md) | Arch Linux (recommended), Fedora, Debian-based |
| [macOS](installation/macos.md) | macOS Sonoma+ |
| [WSL](installation/wsl.md) | Windows Subsystem for Linux |
| [Termux](installation/termux.md) | Android via Termux |

---

## Configuration

Configuration guides for individual components.

| Guide | Component |
|------|-----------|
| [Terminal](configuration/terminal-config.md) | Kitty, Ghostty, WezTerm, Alacritty |
| [Editor](configuration/editor-config.md) | Neovim, VS Code / Antigravity |
| [Shell](configuration/shell-config.md) | Zsh, Bash, Starship, Fish, Nushell |
| [Multiplexer](configuration/multiplexer-config.md) | Tmux, Zellij |
| [ML4W Integration](configuration/ml4w.md) | Profile-driven keybindings, native dispatchers, file layout |
| [Theme System](configuration/theme-system.md) | Theme engine architecture, tokens, variants |

---

## Development

Guides for contributors and developers.

| Resource | Description |
|---------|-------------|
| [CONTRIBUTING](../CONTRIBUTING.md) | How to contribute: setup, tests, PR guidelines |
| [Design Docs](superpowers/specs/) | Design specs and implementation plans (SDD) |
| [Theme Preview](generated/dreamcoder-theme-preview.md) | Automatically generated preview of all themes |
| [PyPI Publishing](pypi-publishing.md) | Publishing `dreamcoder-theme` to PyPI with Trusted Publisher |
| [Migration Guides](migration/) | Migrating from ML4W and Gentleman.Dots |

---

## Root Links

- [Main README](../README.md) — overview, badges, quick start
- [GitHub Repository](https://github.com/Dreamcoder08/Dreamcoder-Workbench)
- [PyPI Package](https://pypi.org/project/dreamcoder-theme/)
