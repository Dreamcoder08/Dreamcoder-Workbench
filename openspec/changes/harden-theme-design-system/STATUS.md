# Status: harden-theme-design-system (mostly delivered)

Status: **open — mostly delivered** (updated 2026-09-11).

## Delivered (13/21)

- `DreamcoderThemes/dreamcoder/design-system.json` — six-target terminal-first inventory.
- `DreamcoderThemes/dreamcoder/design-system.schema.json` plus the `tokens.schema.json` update.
- `src/dreamcoder_theme/design_system.py` — role, target, parity, matrix, and finding models.
- Adapter coverage for Kitty, Ghostty, Warp, Starship, tmux, and OpenCode.
- RED/GREEN tests for canonical role traceability and complete three-mode parity.
- `scripts/generate-palette-tokens.py` refactored into write-free load/enrich/render functions.
- `scripts/verify-theme-health.py` extended with schema, canonical synchronization, and six-target rendering checks.
- OpenCode discovery replaced with the declared `.opencode/themes` contract, plus focused tests.

## Remaining (8)

- Remove `continue-on-error: true` from the theme-health step in `.github/workflows/theme-validation.yml`.
- Correct `.pre-commit-config.yaml` path filters to cover `DreamcoderThemes/dreamcoder/`, the schemas,
  the generator, and the six-target files.
- Document the inventory, layered provenance rules, state/contrast matrix, regeneration command, and
  OpenCode lifecycle.
- Integration assertions for CI wiring and pre-commit path coverage.
- Full closing gates (`pytest`, coverage 40%, `ruff`, `mypy`).
- Textual review of generated terminal-first diffs.
- The two parent-owned bounded native review rows.

No later change re-attempted the remaining items.
