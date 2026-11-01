# Dreamcoder Dots SDD Project Context

- **Project:** dreamcoder-dots
- **Workspace:** `/home/dreamcoder08/Documents/PROYECTOS/dreamcoder08/dreamcoder-workbench`
- **Artifact store:** OpenSpec
- **Execution mode:** Interactive
- **Delivery strategy:** Auto-forecast chained PRs
- **Review budget:** 400 changed lines

## Stack

- Python 3.11+ package using setuptools, with Jinja2 runtime dependency
- Theme engine under `src/dreamcoder_theme/`
- Canonical theme tokens in `themes/dreamcoder/tokens.json`
- Renderers and writers generate configurations for terminal, shell, desktop, editor, and tool targets
- Shell automation under `scripts/`; Go 1.26 installer under `installer/`
- Installer uses Cobra/Bubble Tea-style CLI components and has Go unit/e2e test areas

## Testing and quality

- Strict TDD: disabled in existing OpenSpec configuration
- Primary test runner: `python -m pytest tests/ -v` (pytest 9.0.3 detected)
- Coverage: `python -m pytest tests/ --cov=dreamcoder_theme --cov-report=term-missing` (threshold: 40%)
- Lint and format: `ruff check src/ tests/` and `ruff format --check src/ tests/`
- Type checking: `mypy src/` (not available in the current PATH)
- Shell linting: `find scripts/ -name '*.sh' -exec shellcheck --shell=bash {} +`
- Shell tests: `bats shell-tests/` (available)
- Go tests: `go test ./...` from `installer/`
- Full development setup: `pip install -e ".[dev]"`

## Architecture conventions

- `palette_tokens.py` contains generated/static token definitions.
- `palette.py` validates contrast with WCAG/APCA guardrails and supports adaptive palettes.
- `renderers.py` is the renderer hub; target-specific behavior belongs in `renderers_<target>.py`.
- `sync.py` orchestrates variant loading, rendering, and writes.
- `writers.py` uses change-aware writes and manages target-specific includes/updates.
- Theme changes must preserve WCAG 4.5:1 minimum contrast, APCA body minimums, and the canonical token workflow.
- Technical artifacts are written in English.

## Initialization notes

- Existing `openspec/config.yaml` was preserved and remains authoritative for SDD rules and testing commands; it already defines the OpenSpec `spec-driven` schema and `strict_tdd: false`.
- `.atl/skill-registry.md` exists and is available for phase skill resolution.
- This refresh made no source-code or configuration changes.
- The working tree is heavily dirty (93 reported paths, including pre-existing deletions, generated files, and modifications); later phases MUST isolate their scope and avoid unrelated cleanup.
- Native review authority is currently locked by unrelated correction-required lineages; do not alter or reconcile those review artifacts during initialization.
- Existing OpenSpec artifacts and changes were preserved, including Phase 1 delivery material and GGA/theme-repair work.
- Any unresolved target naming (including existing `herdr` renderer references) must be clarified during proposal planning before implementation.
