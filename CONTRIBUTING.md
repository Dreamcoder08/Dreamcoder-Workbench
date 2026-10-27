# Contributing

Thanks for helping improve Dreamcoder Workbench. Report bugs and propose changes on the [GitHub repository](https://github.com/Dreamcoder08/Dreamcoder-Workbench); keep pull requests focused and include tests for behavior changes.

## Prepare a local development environment

Python 3.11 or newer is required. Clone the repository, then from its root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pip install pre-commit
pre-commit install
```

Reactivate `.venv` in each new shell. `pre-commit` is separate from the project's dev extras. Some checks also need external tools, including ShellCheck; see the [Makefile](Makefile) and [hook configuration](.pre-commit-config.yaml). For desktop installation rather than development, use [INSTALL.md](INSTALL.md).

## Check your change

Run the checks relevant to your work before opening a pull request:

```bash
make python-lint   # Ruff lint and format check
make shell-lint    # ShellCheck on shell scripts recursively under scripts/
make type-check    # mypy src/
make lint          # all three above
make test          # pytest tests/ -v
make coverage      # pytest with coverage report
python scripts/validate-markdown-links.py
pre-commit run --all-files
```

`make format` rewrites Python files, and `make build` creates distribution artifacts. Review their output before committing. Hooks can also modify files: inspect the diff and rerun checks after fixes. The hook configuration includes whitespace, YAML/JSON and large-file checks, Ruff, mypy, ShellCheck, Markdown links, and path-triggered tests, theme validation, preview drift and profile validation. Running all hooks may regenerate the theme preview.

For documentation, update the smallest relevant page, link rather than duplicate guidance, and keep pages reachable from the [docs index](docs/README.md). Use English, the name Dreamcoder Workbench, and `dark`/`light` for user-facing modes. Use a `docs:` commit for documentation changes.

## Add or change a theme renderer

The source of truth for palette data is [tokens.json](DreamcoderThemes/dreamcoder/tokens.json); `src/dreamcoder_theme/palette_tokens.py` is generated from it, not the file to edit by hand. See the [theme system guide](docs/configuration/theme-system.md) for regeneration and its write boundaries.

1. Follow an existing renderer in `src/dreamcoder_theme/renderers_*.py`; render content from palette values rather than writing files in the renderer. Export public functions through `renderers.py` where appropriate.
2. Trace a comparable target through `sync.py`: its registry, coverage declaration, preparation and render plan, active writes and repository variants. Decide whether the new target needs a selector or specialized integration; not every target uses the same path. Keep registry and coverage invariants aligned.
3. If needed, define paths in `settings.py` and reuse the appropriate writer in `writers.py` or the existing specialized writer. Preserve validation and ownership rules rather than adding an independent write path.
4. Add focused renderer and synchronization tests, including the target's selection and failure boundaries. Update documentation when behavior or commands change.

Generated output alone does not install an application or prove that it consumes a theme. Review generated changes and application-specific behavior separately.

## Submit

Create a branch, make focused commits, and open a pull request against `main`. Describe the change, its validation and any platform limitations; update the changelog when appropriate. For the broader layout and component guides, start at the [documentation hub](docs/README.md).
