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
| `bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f3eadc'></span> `#f3eadc` |
| `bg_soft` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#e6d7c4'></span> `#e6d7c4` |
| `surface0` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fff7ea'></span> `#fff7ea` |
| `surface1` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#decbb1'></span> `#decbb1` |
| `surface2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#c8ad89'></span> `#c8ad89` |
| `surface3` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#b89d7a'></span> `#b89d7a` |
| `text` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#17120d'></span> `#17120d` |
| `text_heading` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#100c07'></span> `#100c07` |
| `muted` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#352e22'></span> `#352e22` |
| `subtle` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#554638'></span> `#554638` |
| `comment` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#725e4c'></span> `#725e4c` |
| `accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#824f16'></span> `#824f16` |
| `accent_2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a7471c'></span> `#a7471c` |
| `diagnostic` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0d4a68'></span> `#0d4a68` |
| `sage` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#315b31'></span> `#315b31` |
| `success` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#315b31'></span> `#315b31` |
| `info` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0d4a68'></span> `#0d4a68` |
| `lavender` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#57478b'></span> `#57478b` |
| `mauve` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#7d3e64'></span> `#7d3e64` |
| `error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#842f24'></span> `#842f24` |
| `warning` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#654300'></span> `#654300` |
| `on_accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fff7ea'></span> `#fff7ea` |
| `on_error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#fff7ea'></span> `#fff7ea` |
| `link` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#824f16'></span> `#824f16` |
| `link_hover` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a7471c'></span> `#a7471c` |
| `selection_bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#decbb1'></span> `#decbb1` |
| `selection_fg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#17120d'></span> `#17120d` |
| `border` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#8a7358'></span> `#8a7358` |
| `border_ui` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#66513b'></span> `#66513b` |
| `border_hi` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#3e2f20'></span> `#3e2f20` |
| `focus` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#0f6570'></span> `#0f6570` |

### Dreamcoder Dusk

| Role | Color |
| --- | --- |
| `bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#ebe4d6'></span> `#ebe4d6` |
| `bg_soft` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#dfd5c4'></span> `#dfd5c4` |
| `surface0` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f1eadf'></span> `#f1eadf` |
| `surface1` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#d8cbb8'></span> `#d8cbb8` |
| `surface2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#c6b6a0'></span> `#c6b6a0` |
| `surface3` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#b6a691'></span> `#b6a691` |
| `text` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1a1713'></span> `#1a1713` |
| `text_heading` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#13100c'></span> `#13100c` |
| `muted` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#4c443a'></span> `#4c443a` |
| `subtle` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#5a4f43'></span> `#5a4f43` |
| `comment` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#615548'></span> `#615548` |
| `accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#8a5520'></span> `#8a5520` |
| `accent_2` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#96411e'></span> `#96411e` |
| `diagnostic` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#104b67'></span> `#104b67` |
| `sage` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#344f30'></span> `#344f30` |
| `success` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#344f30'></span> `#344f30` |
| `info` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#104b67'></span> `#104b67` |
| `lavender` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#5b4e86'></span> `#5b4e86` |
| `mauve` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#784762'></span> `#784762` |
| `error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#773126'></span> `#773126` |
| `warning` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#604000'></span> `#604000` |
| `on_accent` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f1eadf'></span> `#f1eadf` |
| `on_error` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#f1eadf'></span> `#f1eadf` |
| `link` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#8a5520'></span> `#8a5520` |
| `link_hover` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#96411e'></span> `#96411e` |
| `selection_bg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#d8cbb8'></span> `#d8cbb8` |
| `selection_fg` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#1a1713'></span> `#1a1713` |
| `border` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#a7947a'></span> `#a7947a` |
| `border_ui` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#665845'></span> `#665845` |
| `border_hi` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#4a3f32'></span> `#4a3f32` |
| `focus` | <span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:#216a73'></span> `#216a73` |

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
| `text` | 15.60:1 | AAA |
| `muted` | 11.25:1 | AA |
| `comment` | 5.15:1 | AA |
| `accent` | 5.72:1 | AA |
| `accent_2` | 4.95:1 | AA |
| `diagnostic` | 8.02:1 | AA |
| `sage` | 6.59:1 | AA |
| `error` | 7.30:1 | AA |
| `warning` | 7.48:1 | AA |

### Dreamcoder Light APCA

| Token | Lc vs bg | Target |
| --- | ---: | --- |
| `text` | 93.3 | ≥75 (body) |
| `muted` | 88.0 | ≥75 (body) |
| `comment` | 68.8 | ≥75 (FAIL) |
| `accent` | 71.4 | ≥75 (FAIL) |
| `accent_2` | 66.9 | ≥75 (FAIL) |
| `diagnostic` | 79.9 | ≥75 (body) |
| `sage` | 75.3 | ≥75 (body) |
| `error` | 77.2 | ≥75 (body) |
| `warning` | 78.3 | ≥75 (body) |
| `border_ui` | 74.1 | ≥60 (UI) |
| `focus` | 71.0 | ≥60 (UI) |

### Dreamcoder Light UI affordance contrast

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `border_ui` | 6.28:1 | PASS |
| `border_hi` | 10.79:1 | PASS |
| `focus` | 5.65:1 | PASS |

### Dreamcoder Dusk contrast (WCAG 2)

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `text` | 14.12:1 | AAA |
| `muted` | 7.56:1 | AA |
| `comment` | 5.72:1 | AA |
| `accent` | 4.88:1 | AA |
| `accent_2` | 5.40:1 | AA |
| `diagnostic` | 7.46:1 | AA |
| `sage` | 7.20:1 | AA |
| `error` | 7.37:1 | AA |
| `warning` | 7.44:1 | AA |

### Dreamcoder Dusk APCA

| Token | Lc vs bg | Target |
| --- | ---: | --- |
| `text` | 89.0 | ≥75 (body) |
| `muted` | 76.6 | ≥75 (body) |
| `comment` | 69.5 | ≥75 (FAIL) |
| `accent` | 64.9 | ≥75 (FAIL) |
| `accent_2` | 67.4 | ≥75 (FAIL) |
| `diagnostic` | 75.9 | ≥75 (body) |
| `sage` | 75.3 | ≥75 (body) |
| `error` | 75.4 | ≥75 (body) |
| `warning` | 75.9 | ≥75 (body) |
| `border_ui` | 68.2 | ≥60 (UI) |
| `focus` | 65.2 | ≥60 (UI) |

### Dreamcoder Dusk UI affordance contrast

| Token | Ratio vs bg | Target |
| --- | ---: | --- |
| `border_ui` | 5.45:1 | PASS |
| `border_hi` | 8.10:1 | PASS |
| `focus` | 4.92:1 | PASS |

## Usage

```bash
./scripts/dreamcoder auto
./scripts/dreamcoder light
./scripts/dreamcoder dark
./scripts/dreamcoder verify
./scripts/dreamcoder preview
```

## Design notes

- Dark mode uses a pure black canvas reserved by `surface_policy`; light and dusk modes avoid pure black and pure white.
- Main text targets AAA (WCAG 2) and APCA Lc ≥ 75 for long coding sessions.
- Cocoa/Lúcuma accents are identity colors in light; Dreamcoder Dark uses indigo, violet, icy blue, soft rose, and pale gold for dark-mode personality.
- UI affordance tokens (`border_ui`, `border_hi`, `focus`) target at least 3:1 against the main background.
- opencode uses one canonical theme: `dreamcoder`; its main `background` is generated as `none` for terminal transparency.
