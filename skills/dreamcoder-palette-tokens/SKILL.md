# Dreamcoder Palette Tokens

Single source: `DreamcoderThemes/dreamcoder/tokens.json` (schema: `tokens.schema.json`).
Rationale and laws: [design-system page](../../docs/DREAMCODER_DESIGN_SYSTEM.md). Do not restate them here.

## Modes

Only `dark` and `light` exist. OLED behavior is `modes.dark.surface_policy`.

| Mode    | Name             | BG        | Use Case    |
| ------- | ---------------- | --------- | ----------- |
| `dark`  | Dreamcoder Dark  | `#000000` | 18:00-07:00 |
| `light` | Dreamcoder Light | `#f9f6f2` | 07:00-18:00 |

## Tiers

| Tier | Key | Holds |
| --- | --- | --- |
| 1 primitives | `primitives.light` | Named OKLCH colours: `paper.*`, `ink.*`, `clay.*`, one pigment each (`madder`, `umber`, `ochre`, `malachite`, `verdigris`, `indigo`, `violet`, `cochineal`) |
| 2 semantic | `bindings.light` → `modes.<mode>` | Role → primitive name. `modes.*` stays flat hex for every consumer |
| 3 components | `components` | `elevation`, `radius`, `border`, `spacing`, `motion`, `typography`, `wallpaper` limits |

Dark has no bindings yet: its `modes.dark` hex is authored directly.

## Roles

- **Background**: `bg`, `bg_soft`, `surface{0,1,2,3}` (`surface3` is non-text)
- **Text**: `text`, `text_heading`, `muted`, `subtle`, `comment`
- **Accent**: `accent`, `accent_2` (hover), `link`, `link_hover`, `focus`
- **Semantic**: `error`, `warning`, `success`, `info`, `diagnostic` (`info` and `diagnostic` share one primitive)
- **UI**: `border`, `border_ui`, `border_hi`, `selection`
- **Prompt**: `prompt_bg`, `prompt_surface{0,1,2}`, `prompt_text`, `prompt_muted`, `prompt_accent`
- ANSI-16 is derived in `palette.py`; never add it to tokens.

## Guardrails

Read thresholds from `guardrails` in `tokens.json`; never hard-code them. WCAG 2.2 and APCA are both blocking.

| Check | Where |
| --- | --- |
| WCAG ≥ 4.5 text (7.0 main text), APCA body Lc 75 light / 50 dark | `guardrails`, `verify-theme-health.py` |
| Pigments mutually ΔE2000 ≥ 12, one density (L within 0.01) | `tests/test_light_material.py` |
| Paper hue 70–84° and chroma rising as L falls; ink and clay one hue axis | `tests/test_light_material.py` |
| Shadow ink is warm, never black; depth grows with level | `tests/test_light_elevation.py` |
| Spacing on the 4 px grid; motion curves without overshoot | `tests/test_light_rhythm.py` |
| Chip/badge fills are washes (alpha ≤ 0.16), no saturated solid fills | `tests/test_light_semantic_chrome.py` |
| Tiers consistent: `TIER_DRIFT`, `TIER_UNBOUND` | `verify-theme-health.py` |

## Changing a colour

Edit only `tokens.json`, then regenerate. Never edit generated outputs.

1. Change the primitive in `primitives.light` (or a binding in `bindings.light`).
2. Update the matching flat hex in `modes.light` (`TIER_DRIFT` fails otherwise).
3. Regenerate and verify:

```bash
python scripts/generate-palette-tokens.py   # writes palette_tokens.py
./scripts/dreamcoder sync                   # writes every renderer output
make theme-check                            # sync, drift, health, tests, wallpaper contract
make theme-diff                             # ΔE2000 / contrast impact vs origin/main
```

Hand-copied hex outside generated files fails `tests/test_light_color_files.py`.
