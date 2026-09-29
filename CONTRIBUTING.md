# Contributing

Thanks for your interest in Dreamcoder Workbench! This project is a personal dotfiles
repository with an open-source theme engine. Contributions, ideas, and bug
reports are welcome.

## How to contribute — quick path

1. **Report a bug** or request a feature: open an issue on the [GitHub repository](https://github.com/Dreamcoder08/Dreamcoder-Workbench).
2. **Propose a change**: fork the repo, create a branch, and commit focused changes (see [Pull Request Guidelines](#pull-request-guidelines)).
3. **Open a PR**: push your branch and open a pull request against `main`. CI runs lint, type checks, and tests automatically; pre-commit hooks run locally on every commit.

Need a smaller first step? Pick an open issue, fix a docs typo, or add a renderer test.

## Project Structure

```text
src/dreamcoder_theme/     # Python theme engine (pip-installable package)
  ├── palette.py              # Color math, adaptive palette derivation
  ├── palette_tokens.py       # Static design tokens (dark/light/dusk)
  ├── renderers.py            # Public renderer import hub
  ├── renderers_kitty.py      # Kitty format renderer
  ├── renderers_ghostty_warp.py
  ├── renderers_codex.py
  ├── renderers_opencode.py
  ├── renderers_pi.py
  ├── renderers_starship.py
  ├── renderers_tmux.py
  ├── renderers_antigravity.py
  ├── renderers_readme.py
  ├── renderers_hypr_waybar_rofi.py
  ├── renderers_extra_nvim.py      # Nvim + LSP + plugins + syntax + UI
  ├── renderers_extra_obsidian.py
  ├── renderers_extra_bat_delta.py
  ├── renderers_extra_btop.py
  ├── renderers_extra_firefox.py
  ├── renderers_extra_notify.py    # Dunst, Cava
  ├── renderers_extra_shell.py     # Zsh, LS_COLORS, fzf
  ├── sync.py                  # Theme file orchestration
  ├── control.py               # CLI entry point
  ├── writers.py               # Filesystem writers & config updaters
  ├── settings.py              # Paths, mode, adaptive configuration
  ├── core.py                  # Core path utilities
  ├── doctor.py                # Health checks
  ├── dashboard.py             # Control center dashboard
  ├── cli_parser.py            # CLI argument parser
  ├── cli_handlers.py          # CLI command handlers
  ├── installer.py             # Dotfiles installer
  ├── repair_engine.py         # Repair after updates
  ├── profiles.py              # ML4W profile management
  ├── backups.py               # Theme backup/restore
  ├── audit.py                 # Theme audit & validation
  ├── docs_report.py           # Documentation health report
  ├── motion.py                # Motion preset scheduler
  ├── tui.py                   # Terminal UI
  ├── visual_regression.py     # Visual regression testing
  └── settings_store.py        # Settings persistence
tests/                        # pytest test suite
shell-tests/                  # bats tests for shell scripts
docs/                         # Documentation hub
scripts/                      # Shell automation scripts
DreamcoderThemes/dreamcoder/    # Generated theme files (output)
```

Each tool lives in a Dreamcoder-prefixed top-level directory
(`DreamcoderKitty/`, `DreamcoderGhostty/`, `DreamcoderNvim/`, etc.)
and is installed via GNU Stow.

## Development Setup

```bash
# Clone and enter
git clone git@github.com:Dreamcoder08/Dreamcoder-Workbench.git
cd Dreamcoder-Workbench

# Install with dev dependencies (using pip)
pip install -e ".[dev]"

# Or using uv (recommended)
uv pip install -e ".[dev]"
```

## Quality Commands

The project provides a `Makefile` with common quality commands:

```bash
make lint          # ruff check + ruff format --check + shellcheck + mypy
make test          # pytest tests/ -v
make coverage      # pytest --cov=dreamcoder_theme --cov-report=term-missing
make format        # auto-format all Python files with ruff
make type-check    # mypy src/ (strict mode)
make python-lint   # ruff only
make shell-lint    # shellcheck on scripts/*.sh
make clean         # remove build artifacts
make build         # build wheel + source tarball
```

Or run tools individually:

```bash
# Full test suite
pytest

# With coverage
pytest --cov=dreamcoder_theme --cov-report=term-missing

# Specific test file
pytest tests/test_palette.py -v
```

## Linting

```bash
# ruff for Python
ruff check src/dreamcoder_theme/

# auto-fix
ruff check --fix src/dreamcoder_theme/

# shellcheck for shell scripts
shellcheck --shell=bash scripts/*.sh
```

## Pre-commit Hooks

The project uses pre-commit to enforce quality on every commit. Install it:

```bash
pip install pre-commit
pre-commit install
```

After installation, the following checks run automatically before each commit:

| Hook                          | Tool             | Description                       |
| ----------------------------- | ---------------- | --------------------------------- |
| trailing-whitespace           | pre-commit-hooks | Remove trailing whitespace        |
| end-of-file-fixer             | pre-commit-hooks | Ensure files end with newline     |
| check-yaml                    | pre-commit-hooks | Validate YAML syntax              |
| check-json                    | pre-commit-hooks | Validate JSON syntax              |
| ruff                          | ruff-pre-commit  | Lint + auto-fix Python            |
| ruff-format                   | ruff-pre-commit  | Format Python with ruff           |
| mypy                          | mypy             | Type check (strict mode)          |
| shellcheck                    | shellcheck-py    | Static analysis for shell scripts |
| dreamcoder-theme-validate     | custom           | Validate theme token health       |
| dreamcoder-preview-regenerate | custom           | Regenerate theme preview          |

Run all hooks manually at any time:

```bash
pre-commit run --all-files
```

To skip hooks for a WIP commit (use sparingly):

```bash
git commit --no-verify -m "wip: ..."
```

## Building

```bash
# Build wheel + source tarball
python -m build

# Or via Makefile
make build
```

## How to Add a New Renderer

Renderers follow a pure-function architecture. Adding a new target follows this flow:

```mermaid
flowchart LR
    A["1. Create renderer_<target>.py<br/>Define content(target_colors) → str"] --> B
    B["2. Export from renderers.py<br/>Add import + __all__ entry"] --> C
    C["3. Add write call to sync.py<br/>write_if_changed(path, content(active))"] --> D
    D["4. Add path to settings.py<br/>theme_paths() namedtuple"] --> E
    E["5. Add paths to control.py<br/>path generation if needed"] --> F
    F["6. Add print to sync_summary()<br/>Show path + changed status"] --> G
    G["7. Write tests<br/>tests/test_renderer_<target>.py"] --> H
    H["8. Add variant files if needed<br/>sync_repo_snippets() write_variant_files()"]
```

### Checklist

- [ ] `renderers_<target>.py` — pure function that takes `dict[str, str]` and returns `str`
- [ ] Registered in `renderers.py` (import + `__all__`)
- [ ] Called in `sync.py` → `sync_active_targets()` or `sync_repo_snippets()`
- [ ] Path defined in `settings.py` → `theme_paths()`
- [ ] Path generated in `control.py` if applicable
- [ ] `print_summary()` shows the new target
- [ ] Tests in `tests/`

## Documentation changes

Documentation changes are reviewed like code changes.

- [ ] Run `python scripts/validate-markdown-links.py` and fix any broken links.
- [ ] Update the smallest relevant page; do not duplicate content that already lives in another doc — link to it instead.
- [ ] The changed page is reachable from the [docs index](docs/README.md) or the README documentation table; add it there if it is a new page.
- [ ] Keep the identity string "Dreamcoder Workbench" and mode names `dark/light` consistent with the rest of the docs.
- [ ] Commit with the `docs:` conventional commit type.

Do not duplicate references: link to the source page for detailed behavior.

## Pull Request Guidelines

- Keep changes focused — one feature/fix per PR.
- Add tests for new functionality.
- Ensure `make lint && make test && make coverage` passes before opening the PR.
- Follow existing code style (ruff defaults, 100 chars line length).
- Keep the CHANGELOG updated under `## Unreleased`.
- Pre-commit hooks must pass before committing.

## Design Principles

- **Health first**: colors must pass WCAG AA contrast ratios.
- **Single source of truth**: edit tokens in `palette_tokens.py`, not in
  individual theme files.
- **Renderers are pure**: each renderer takes a color dict and returns a
  string — no side effects.
- **Stow-compatible**: file paths in the repo mirror `$HOME` layout so GNU
  Stow can link them directly.
