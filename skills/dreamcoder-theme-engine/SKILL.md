# Dreamcoder Theme Engine

## Purpose

Python theme engine that reads `tokens.json` and generates color configs for 28+ targets.

## Architecture

```
tokens.json → palette_tokens.py (static tokens)
           → palette.py (adaptive from wallpaper)
           → renderers*.py (28+ target formats)
           → writers.py (write_if_changed)
```

## Key Files

- `src/dreamcoder_theme/palette_tokens.py` — Canonical token definitions (dark/light)
- `src/dreamcoder_theme/palette.py` — `guard()` for WCAG contrast validation, `adaptive_palette()` for wallpaper colors
- `src/dreamcoder_theme/renderers.py` — Hub that imports all `renderers_*.py` leaf modules
- `src/dreamcoder_theme/renderers_kitty.py` — Kitty terminal colors
- `src/dreamcoder_theme/renderers_ghostty_warp.py` — Ghostty + Warp
- `src/dreamcoder_theme/renderers_starship.py` — Starship prompt (23 modules)
- `src/dreamcoder_theme/renderers_tmux.py` — Tmux theme
- `src/dreamcoder_theme/writers.py` — `write_if_changed()`, `update_ghostty_theme()`, `ensure_kitty_ui_include()`
- `src/dreamcoder_theme/sync.py` — Orchestrator: loads variants, renders, writes

## Adding a New Renderer

1. Create `renderers_<target>.py` with a function `def <target>_content(palette: dict) -> str`
2. Import it in `renderers.py` `__all__` list
3. Add it to `sync_active_targets()` or `sync_repo_snippets()` in `sync.py`
4. Add path to `ThemePaths` dataclass in `settings.py`

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=dreamcoder_theme --cov-fail-under=40
```

## Token Guardrails

All colors must pass WCAG 4.5:1 minimum contrast and APCA body minimums.
Use `guard(color, background, mode)` from `palette.py` to validate.
