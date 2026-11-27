# Dreamcoder Theme Engine

## Purpose

Python theme engine that reads `tokens.json` and generates colour configs for the targets in `sync.py`.
Design rules live in the [design-system page](../../docs/DREAMCODER_DESIGN_SYSTEM.md); this file is a map of the code.

## Architecture

```
tokens.json → token_tiers.py (primitives + bindings → hex)
           → palette_tokens.py (generated static tokens)
           → palette.py (load_variants, adaptive palette from wallpaper, ANSI)
           → elevation.py / rhythm.py / effects.py (components → palette keys, both modes)
           → renderers*.py (target formats)
           → renderers_mode_files.py (MODE_FILES: per-mode generated files)
           → writers.py (write_if_changed)
```

## Key Files

- `src/dreamcoder_theme/palette_tokens.py` — GENERATED from `tokens.json` (`scripts/generate-palette-tokens.py`); do not edit
- `src/dreamcoder_theme/color_space.py` — OKLCH/OKLab/sRGB conversion, `delta_e2000`
- `src/dreamcoder_theme/token_tiers.py` — resolves `bindings` against `primitives`; `TierError`
- `src/dreamcoder_theme/elevation.py` — `components.elevation/radius/border` → shadow, radius, border keys; Dark also resolves the tonal surfaces (`surface.dark`) and top-edge hairlines (`edge.dark`)
- `src/dreamcoder_theme/rhythm.py` — `components.spacing/motion/typography` → rhythm keys (mode-independent geometry, shared by Dark and Light)
- `src/dreamcoder_theme/effects.py` — `components.glow` geometry + the semantic token each glow decorates → `effects.glow_*`; `drift()` backs the `EFFECTS_DRIFT` health check
- `src/dreamcoder_theme/wallpaper_contract.py` — pure wallpaper limits (`components.wallpaper`); I/O is in `scripts/check-wallpaper.py`
- `src/dreamcoder_theme/renderers_mode_files.py` — per-mode generated files (`MODE_FILES`: Alacritty, WezTerm, Nushell, Tmux for both modes, Yazi for Light) and the Zellij theme block; guarded by `tests/test_light_color_files.py` and `tests/test_dark_color_files.py`
- `src/dreamcoder_theme/palette.py` — `validate_palette()` (WCAG/APCA), `make_guard()`, `adaptive_palette()` for wallpaper colours, `ansi()`
- `src/dreamcoder_theme/renderers.py` — hub importing every `renderers_*.py`
- `src/dreamcoder_theme/writers.py` — `write_if_changed()`, `update_ghostty_theme()`, `ensure_kitty_ui_include()`
- `src/dreamcoder_theme/sync.py` — orchestrator: loads variants, renders, writes; `sync_mode_files(mode, palette)` writes the per-mode files

## Adding a New Renderer

1. Create `renderers_<target>.py` with `def <target>_content(palette: dict) -> str`; take every colour from `palette`, never a literal
2. Import it in `renderers.py` `__all__`
3. Add it to `sync_active_targets()` or `sync_repo_snippets()` in `sync.py`
4. Add the path to the `ThemePaths` dataclass in `settings.py`
5. A file that exists once per mode goes in `MODE_FILES` instead of the registry; its renderer takes the palette of the mode being written and no colour literal

## Validation

```bash
make theme-check                 # regenerate, drift check, health, theme tests, wallpaper contract
make theme-diff                  # perceptual diff vs origin/main
make specimen                    # regenerate docs/generated/dreamcoder-{light,dark}-specimen.svg (--mode light|dark)
uv run --quiet --extra dev python -m pytest tests/ -q -p no:cacheprovider -o addopts=""
```

`make theme-check` fails on `git diff`: stage intentional output changes first.

## Token Guardrails

All colours must pass WCAG 4.5:1 and the APCA body minimums; `validate_palette()` in `palette.py` enforces the `guardrails` from `tokens.json`.
