# Dreamcoder Theme Preview

Generated from `DreamcoderThemes/dreamcoder/tokens.json`.

## Design rationale

Dreamcoder light themes follow a **cocoa/lúcuma** identity: warm parchment backgrounds, graphite-brown text, and restrained accents. Unlike generic light themes that jump from white to mid-gray surfaces, Dreamcoder uses a **flat surface ladder** (~10 luminance points between steps) so panels feel layered without looking muddy.

**Dreamcoder Dark** reserves a pure-black canvas through `surface_policy`, with scroll-safe near-black functional surfaces, indigo brand accents, icy diagnostics, and pastel syntax colors. Surfaces ladder from the canvas to lighter panels and modal layers. The opencode theme keeps the main background as `none` so the terminal's semi-transparent background remains visible while panels and selections carry the layered surface system.

Semantic tokens are intentionally distinct:

- `comment` is a desaturated pastel syntax color, while `subtle` remains reserved for low-emphasis UI chrome.
- Dark `accent` (pastel indigo), `accent_2` (soft violet), `error` (soft rose), and `warning` (pale gold) form the Dreamcoder Dark signature.
- `accent` carries runtime CTAs and active chrome; the explicit `brand` alias preserves the requested indigo identity while `focus` remains a blue keyboard/input affordance.
- `on_accent`, `on_error`, and `selection_bg`/`selection_fg` are explicit pairs validated in CI.
## Palette

### Dreamcoder Dark

| Role | Color |
| --- | --- |
| `bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#000000'></span> `#000000` |
| `bg_soft` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#090909'></span> `#090909` |
| `surface0` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#090909'></span> `#090909` |
| `surface1` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#121212'></span> `#121212` |
| `surface2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1c1c1c'></span> `#1c1c1c` |
| `surface3` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#262626'></span> `#262626` |
| `text` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#ebebeb'></span> `#ebebeb` |
| `text_heading` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fafafa'></span> `#fafafa` |
| `muted` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#dcdcdc'></span> `#dcdcdc` |
| `subtle` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a4a4a4'></span> `#a4a4a4` |
| `comment` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#cecece'></span> `#cecece` |
| `accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a7b5fd'></span> `#a7b5fd` |
| `accent_2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#c6d0fd'></span> `#c6d0fd` |
| `diagnostic` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#76c4f6'></span> `#76c4f6` |
| `sage` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#86cf90'></span> `#86cf90` |
| `success` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#86cf90'></span> `#86cf90` |
| `info` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#76c4f6'></span> `#76c4f6` |
| `lavender` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#d6a2f6'></span> `#d6a2f6` |
| `mauve` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f59ac5'></span> `#f59ac5` |
| `error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fc9d95'></span> `#fc9d95` |
| `warning` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#dcb55e'></span> `#dcb55e` |
| `on_accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#000000'></span> `#000000` |
| `on_error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#000000'></span> `#000000` |
| `link` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a7b5fd'></span> `#a7b5fd` |
| `link_hover` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#c6d0fd'></span> `#c6d0fd` |
| `selection_bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#303030'></span> `#303030` |
| `selection_fg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#ebebeb'></span> `#ebebeb` |
| `border` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#636363'></span> `#636363` |
| `border_ui` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#777777'></span> `#777777` |
| `border_hi` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a4a4a4'></span> `#a4a4a4` |
| `focus` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#6eccd1'></span> `#6eccd1` |

### Dreamcoder Light

| Role | Color |
| --- | --- |
| `bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f9f6f2'></span> `#f9f6f2` |
| `bg_soft` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f2eee9'></span> `#f2eee9` |
| `surface0` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fefdfa'></span> `#fefdfa` |
| `surface1` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#ede9e3'></span> `#ede9e3` |
| `surface2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#e3ddd5'></span> `#e3ddd5` |
| `surface3` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#d4ccc1'></span> `#d4ccc1` |
| `text` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1e1813'></span> `#1e1813` |
| `text_heading` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#110c08'></span> `#110c08` |
| `muted` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#2b241e'></span> `#2b241e` |
| `subtle` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#4f463e'></span> `#4f463e` |
| `comment` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#5f544c'></span> `#5f544c` |
| `accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#874004'></span> `#874004` |
| `accent_2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#753100'></span> `#753100` |
| `diagnostic` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0a5b8f'></span> `#0a5b8f` |
| `sage` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1b672f'></span> `#1b672f` |
| `success` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1b672f'></span> `#1b672f` |
| `info` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0a5b8f'></span> `#0a5b8f` |
| `lavender` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#574894'></span> `#574894` |
| `mauve` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#81386b'></span> `#81386b` |
| `error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#9c2024'></span> `#9c2024` |
| `warning` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#6e5201'></span> `#6e5201` |
| `on_accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fefdfa'></span> `#fefdfa` |
| `on_error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fefdfa'></span> `#fefdfa` |
| `link` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#874004'></span> `#874004` |
| `link_hover` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#753100'></span> `#753100` |
| `selection_bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f1d7c1'></span> `#f1d7c1` |
| `selection_fg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1e1813'></span> `#1e1813` |
| `border` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#908379'></span> `#908379` |
| `border_ui` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#5f544c'></span> `#5f544c` |
| `border_hi` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#2b241e'></span> `#2b241e` |
| `focus` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#016367'></span> `#016367` |

## Contrast audit

### Dreamcoder Dark contrast (WCAG 2)

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `text` | 17.62:1 | AAA |
| `muted` | 15.31:1 | AA |
| `comment` | 13.34:1 | AA |
| `accent` | 10.67:1 | AA |
| `accent_2` | 13.84:1 | AA |
| `diagnostic` | 11.00:1 | AA |
| `sage` | 11.34:1 | AA |
| `error` | 10.40:1 | AA |
| `warning` | 10.81:1 | AA |

### Dreamcoder Dark APCA

| Token | Lc vs bg | Target |
| --- | ---: | --- |
| `text` | 94.8 | ≥75 (body) |
| `muted` | 85.4 | ≥75 (body) |
| `comment` | 76.9 | ≥75 (body) |
| `accent` | 64.5 | ≥75 (FAIL) |
| `accent_2` | 79.1 | ≥75 (body) |
| `diagnostic` | 66.2 | ≥75 (FAIL) |
| `sage` | 67.8 | ≥75 (FAIL) |
| `error` | 63.4 | ≥75 (FAIL) |
| `warning` | 65.3 | ≥75 (FAIL) |
| `border_ui` | 30.6 | ≥60 (FAIL) |
| `focus` | 67.3 | ≥60 (UI) |

### Dreamcoder Dark UI affordance contrast

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `border_ui` | 4.69:1 | PASS |
| `border_hi` | 8.42:1 | PASS |
| `focus` | 11.22:1 | PASS |

### Dreamcoder Light contrast (WCAG 2)

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `text` | 16.31:1 | AAA |
| `muted` | 14.19:1 | AA |
| `comment` | 6.82:1 | AA |
| `accent` | 7.05:1 | AA |
| `accent_2` | 8.88:1 | AA |
| `diagnostic` | 6.71:1 | AA |
| `sage` | 6.44:1 | AA |
| `error` | 7.37:1 | AA |
| `warning` | 6.79:1 | AA |

### Dreamcoder Light APCA

| Token | Lc vs bg | Target |
| --- | ---: | --- |
| `text` | 99.2 | ≥75 (body) |
| `muted` | 97.0 | ≥75 (body) |
| `comment` | 80.4 | ≥75 (body) |
| `accent` | 80.7 | ≥75 (body) |
| `accent_2` | 86.3 | ≥75 (body) |
| `diagnostic` | 79.4 | ≥75 (body) |
| `sage` | 78.5 | ≥75 (body) |
| `error` | 80.9 | ≥75 (body) |
| `warning` | 80.0 | ≥75 (body) |
| `border_ui` | 80.4 | ≥60 (UI) |
| `focus` | 78.7 | ≥60 (UI) |

### Dreamcoder Light UI affordance contrast

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `border_ui` | 6.82:1 | PASS |
| `border_hi` | 14.19:1 | PASS |
| `focus` | 6.54:1 | PASS |

## Usage

```bash
./scripts/dreamcoder auto
./scripts/dreamcoder light
./scripts/dreamcoder dark
./scripts/dreamcoder verify
./scripts/dreamcoder preview
```

## Design notes

- Dark mode uses a pure black canvas reserved by `surface_policy`; light mode avoids pure black and pure white.
- Main text targets AAA (WCAG 2) and APCA Lc ≥ 75 for long coding sessions.
- Cocoa/Lúcuma accents are identity colors in light; Dreamcoder Dark uses indigo, violet, icy blue, soft rose, and pale gold for dark-mode personality.
- UI affordance tokens (`border_ui`, `border_hi`, `focus`) target at least 3:1 against the main background.
- opencode uses one canonical theme: `dreamcoder`; its main `background` is generated as `none` for terminal transparency.
