# Dreamcoder Dots — AI Agent Skills

## Code Review Rules

### Shell Scripts

- Executable scripts (`scripts/*.sh`) start with `set -euo pipefail`
- Sourced files must NOT set shell options: `lib/*.sh` and everything under
  `DreamcoderShell/.config/shell/` run inside the caller's shell, and `errexit`/`nounset`
  there closes an interactive terminal on the first failing command
- Shell fragments loaded by interactive shells (aliases, small functions) stay short;
  scripts and libraries have one purpose per file and functions that fit on a screen
- Quote all variables: `"${var}"`
- Use `[[ ]]` instead of `[ ]` for tests
- Pass values to inline Python or other interpreters through arguments, never by
  interpolating them into source text

### Modularity

- One file = one purpose
- No duplicate code (DRY)
- Conditional loading: `command -v x && ...`

### Safety

- Safe sourcing: `[[ -f "$file" ]] && source "$file"`
- No hardcoded paths
- Fallback chains for optional tools

### Naming

- Aliases: lowercase, short (`gs`, `pacupd`)
- Functions: snake_case (`smart_cd`, `mkcd`)
- Env vars: UPPER_CASE (`PROJECTS_DIR`)

## Available Skills

| Skill                       | Description                                     | Path                                                  |
| --------------------------- | ----------------------------------------------- | ----------------------------------------------------- |
| `dreamcoder-theme-engine`   | Python theme engine: tokens, renderers, writers | [SKILL.md](skills/dreamcoder-theme-engine/SKILL.md)   |
| `dreamcoder-palette-tokens` | Token schema, WCAG/APCA guardrails, modes       | [SKILL.md](skills/dreamcoder-palette-tokens/SKILL.md) |

## Documentation

When editing documentation, follow these maintenance rules:

- Run `python scripts/validate-markdown-links.py` after doc changes (pre-commit does this automatically for staged files).
- Docs are English, user-facing guides in neutral professional English.
- Identity is always "Dreamcoder Workbench" (never "Dreamcoder OS" / "DreamcoderDots" / bare "dreamcoder-dots").
- Color modes are `dark/light` (never "dusk" as a user-facing mode).
- One file = one purpose: do not duplicate content across docs — link to the source page.
- Update the smallest relevant page for a change; keep every doc reachable from [docs/README.md](docs/README.md).
- Commit doc changes with the `docs:` conventional commit type.

## Auto-invoke

When working on these areas, load the corresponding skill first:

- Theme engine / renderers → `dreamcoder-theme-engine`
- Colors / tokens → `dreamcoder-palette-tokens`
- Shell scripts → use code review rules above
- Documentation / README edits → follow the Documentation rules above
