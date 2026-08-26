# Dreamcoder Workbench Theme System

## Architecture

Three-layer design system:

```txt
primitives (OKLCH ramps) → semantic tokens (tokens.json) → component themes (renderers)
```

Pipeline:

```txt
tokens.json → generate-palette-tokens.py → palette_tokens.py
           → dreamcoder sync → generated theme files for every configured renderer
```

## Canonical tokens

Single source of truth: [`DreamcoderThemes/dreamcoder/tokens.json`](../../DreamcoderThemes/dreamcoder/tokens.json)

The canonical modes are exactly **Dreamcoder Dark**, **Dreamcoder Light**, and
**Dreamcoder Dusk**. Night is a render profile derived from Dark, not a fourth
mode. Dark's `surface_policy` permits pure black only for the canvas; functional
and scrollable surfaces use the near-black ladder (`surface0`–`surface3`) to
reduce OLED smear.

| Layer       | Examples                                                       |
| ----------- | -------------------------------------------------------------- |
| Surfaces    | `bg`, `bg_soft`, `surface0`–`surface3`                         |
| Text        | `text`, `text_heading`, `muted`, `subtle`, `comment`           |
| Brand       | `accent`, `accent_2`, `link`, `link_hover`                     |
| Feedback    | `error`, `warning`, `success`, `info`, `diagnostic`            |
| On-colors   | `on_surface`, `on_accent`, `on_error`, `on_focus`              |
| Interaction | `selection_bg`, `selection_fg`, `hover`, `pressed`, `disabled` |
| Chrome      | `border`, `border_ui`, `border_hi`, `focus`, `panel_rgba`      |

## Regenerating themes

After editing `tokens.json`:

```bash
./scripts/generate-palette-tokens.py       # sync palette_tokens.py + derived tokens
python scripts/generate-dark-css.py        # sync dreamcoder-dark.css variables
./scripts/dreamcoder sync                  # propagate to all targets
./scripts/verify-theme-health.py           # WCAG + APCA gates (light and dark)
```

CI or local drift checks can use:

```bash
python scripts/generate-palette-tokens.py --check
python scripts/generate-dark-css.py --check
```

## Quality gates

- WCAG 2.2: body text ≥ 4.5:1 (main text ≥ 7:1)
- APCA: body Lc ≥ 75 light / ≥ 50 dark; `on_accent` Lc ≥ 54 on filled accent
- CI validates **both** light and dark Kitty, Starship, Ghostty, Waybar, Hypr, Rofi, Btop, Dunst, Fzf

## Design decisions

- **brand alias** = indigo `#6366F1`; the runtime `accent` is a lighter accessible role where filled controls must pass the existing WCAG/APCA gates
- **focus** = blue `#3B82F6`, kept distinct from brand and diagnostic colors
- **border aliases** = `#12121A` (subtle) and `#1F1F2B` (medium); significant runtime borders remain brighter because the non-text contrast gate is not weakened
- **generated CSS** = [`dreamcoder-dark.css`](../../DreamcoderThemes/dreamcoder/dreamcoder-dark.css), sourced only from `tokens.json`
- **stable Dark identifiers** = `dreamcoder-dark.css` and `:root[data-theme="dark"]`; OLED compatibility naming is retired, and OLED behavior remains a surface policy of Dreamcoder Dark rather than a separate mode
- **adaptive/matugen** may tint surfaces but identity tokens win per `CLAUDE.md`

## Adding new targets

1. Create renderer in `src/dreamcoder_theme/renderers_<target>.py`
2. Map semantic tokens (never raw hex in renderers)
3. Register in `src/dreamcoder_theme/sync.py`
4. Run `./scripts/dreamcoder sync`
