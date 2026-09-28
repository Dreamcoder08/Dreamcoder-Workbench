# Dreamcoder Palette Tokens

## Token Schema

Defined in `DreamcoderThemes/dreamcoder/tokens.json` with validation schema at `tokens.schema.json`.

## Modes

| Mode    | Name             | BG        | Accent    | Use Case    |
| ------- | ---------------- | --------- | --------- | ----------- |
| `dark`  | Dreamcoder Dark  | `#000000` | `#A5B4FC` | 18:00-07:00 |
| `light` | Dreamcoder Light | `#f3eadc` | `#824f16` | 07:00-16:00 |
| `dusk`  | Dreamcoder Dusk  | `#ebe4d6` | `#8a5520` | 16:00-18:00 |

These are the only canonical modes; Dark and Light are the user-facing ones. OLED behavior belongs to `modes.dark.surface_policy`.

## Token Categories

- **Background**: `bg`, `bg_soft`, `surface{0,1,2,3}`
- **Text**: `text`, `text_heading`, `muted`, `subtle`, `comment`
- **Accent**: `accent`, `accent_2`, `focus`
- **Semantic**: `error`, `warning`, `success`, `info`, `diagnostic`
- **UI**: `border`, `border_ui`, `border_hi`, `selection`
- **Prompt**: `prompt_bg`, `prompt_surface{0,1,2}`, `prompt_text`, `prompt_muted`, `prompt_accent`

## Guardrails (WCAG + APCA)

```json
{
  "minimum_text_contrast": 4.5,
  "preferred_main_text_contrast": 7.0,
  "minimum_apca_body": 75,
  "minimum_apca_body_dark": 50
}
```

## Color Tokens to Update

When updating a color in `tokens.json`, also update:

1. `src/dreamcoder_theme/palette_tokens.py` (regenerated from tokens.json)
2. `scripts/apply-theme-mode.sh` (kanagawa tmux colors)
3. `src/dreamcoder_theme/renderers_starship.py` (palette section)

## Validation

```bash
python scripts/verify-theme-health.py  # Validates all tokens
python scripts/generate-theme-preview.py  # Generates docs preview
```
