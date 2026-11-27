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
| `bg_soft` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0B0B0B'></span> `#0B0B0B` |
| `surface0` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0B0B0B'></span> `#0B0B0B` |
| `surface1` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0D0D0F'></span> `#0D0D0F` |
| `surface2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1F1F1F'></span> `#1F1F1F` |
| `surface3` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#2E2E2E'></span> `#2E2E2E` |
| `text` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#E6E6E6'></span> `#E6E6E6` |
| `text_heading` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#F5F5F5'></span> `#F5F5F5` |
| `muted` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#C7C7C7'></span> `#C7C7C7` |
| `subtle` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#A7A7A7'></span> `#A7A7A7` |
| `comment` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#D0D0D0'></span> `#D0D0D0` |
| `accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#A5B4FC'></span> `#A5B4FC` |
| `accent_2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#D4B5FD'></span> `#D4B5FD` |
| `diagnostic` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#7DD3FC'></span> `#7DD3FC` |
| `sage` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#34D399'></span> `#34D399` |
| `success` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#34D399'></span> `#34D399` |
| `info` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#7DD3FC'></span> `#7DD3FC` |
| `lavender` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#D4B5FD'></span> `#D4B5FD` |
| `mauve` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#D8B4FE'></span> `#D8B4FE` |
| `error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#FB8585'></span> `#FB8585` |
| `warning` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#FBBF24'></span> `#FBBF24` |
| `on_accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#000000'></span> `#000000` |
| `on_error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#000000'></span> `#000000` |
| `link` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#A5B4FC'></span> `#A5B4FC` |
| `link_hover` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#D4B5FD'></span> `#D4B5FD` |
| `selection_bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#3A3A3A'></span> `#3A3A3A` |
| `selection_fg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#E6E6E6'></span> `#E6E6E6` |
| `border` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#6B6B6B'></span> `#6B6B6B` |
| `border_ui` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#767676'></span> `#767676` |
| `border_hi` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#A7A7A7'></span> `#A7A7A7` |
| `focus` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#3B82F6'></span> `#3B82F6` |

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
| `text` | 16.83:1 | AAA |
| `muted` | 12.42:1 | AA |
| `comment` | 13.62:1 | AA |
| `accent` | 10.53:1 | AA |
| `accent_2` | 11.83:1 | AA |
| `diagnostic` | 12.60:1 | AA |
| `sage` | 10.92:1 | AA |
| `error` | 8.80:1 | AA |
| `warning` | 12.58:1 | AA |

### Dreamcoder Dark APCA

| Token | Lc vs bg | Target |
| --- | ---: | --- |
| `text` | 91.7 | ≥75 (body) |
| `muted` | 72.7 | ≥75 (FAIL) |
| `comment` | 78.1 | ≥75 (body) |
| `accent` | 63.8 | ≥75 (FAIL) |
| `accent_2` | 70.0 | ≥75 (FAIL) |
| `diagnostic` | 73.7 | ≥75 (FAIL) |
| `sage` | 66.2 | ≥75 (FAIL) |
| `error` | 55.4 | ≥75 (FAIL) |
| `warning` | 73.7 | ≥75 (FAIL) |
| `border_ui` | 30.1 | ≥60 (FAIL) |
| `focus` | 37.8 | ≥60 (FAIL) |

### Dreamcoder Dark UI affordance contrast

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `border_ui` | 4.62:1 | PASS |
| `border_hi` | 8.73:1 | PASS |
| `focus` | 5.71:1 | PASS |

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
