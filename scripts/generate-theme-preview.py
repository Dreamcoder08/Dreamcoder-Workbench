#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme._math import apca_lc  # noqa: E402

TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
OUT = ROOT / "docs/generated/dreamcoder-theme-preview.md"
TEXT_KEYS = [
    "text",
    "muted",
    "comment",
    "accent",
    "accent_2",
    "diagnostic",
    "sage",
    "error",
    "warning",
]
ROLES = [
    "bg",
    "bg_soft",
    "surface0",
    "surface1",
    "surface2",
    "surface3",
    "text",
    "text_heading",
    "muted",
    "subtle",
    "comment",
    "accent",
    "accent_2",
    "diagnostic",
    "sage",
    "success",
    "info",
    "lavender",
    "mauve",
    "error",
    "warning",
    "on_accent",
    "on_error",
    "link",
    "link_hover",
    "selection_bg",
    "selection_fg",
    "border",
    "border_ui",
    "border_hi",
    "focus",
]


def rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lum(value):
    def channel(part):
        part /= 255
        return part / 12.92 if part <= 0.03928 else ((part + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(part) for part in rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(left, right):
    high, low = sorted((lum(left), lum(right)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def badge(value):
    return f"<span style='display:inline-block;width:0.9em;height:0.9em;border:1px solid #888;background:{value}'></span> `{value}`"


def palette_table(name, palette):
    rows = [f"### {name}\n", "| Role | Color |", "| --- | --- |"]
    for role in ROLES:
        if role in palette:
            rows.append(f"| `{role}` | {badge(palette[role])} |")
    return "\n".join(rows)


def contrast_table(name, palette):
    rows = [
        f"### {name} contrast (WCAG 2)\n",
        "| Token | Ratio vs bg | Target |",
        "| --- | ---: | --- |",
    ]
    bg = palette["bg"]
    for key in TEXT_KEYS:
        ratio = contrast(bg, palette[key])
        target = "AAA" if key == "text" and ratio >= 7 else "AA" if ratio >= 4.5 else "FAIL"
        rows.append(f"| `{key}` | {ratio:.2f}:1 | {target} |")
    return "\n".join(rows)


def apca_table(name, palette, body_min, ui_min):
    rows = [
        f"### {name} APCA\n",
        "| Token | Lc vs bg | Target |",
        "| --- | ---: | --- |",
    ]
    bg = palette["bg"]
    for key in TEXT_KEYS:
        lc = abs(apca_lc(palette[key], bg))
        target = "body" if lc >= body_min else "FAIL"
        rows.append(f"| `{key}` | {lc:.1f} | ≥{body_min} ({target}) |")
    for key in ["border_ui", "focus"]:
        lc = abs(apca_lc(palette[key], bg))
        target = "UI" if lc >= ui_min else "FAIL"
        rows.append(f"| `{key}` | {lc:.1f} | ≥{ui_min} ({target}) |")
    return "\n".join(rows)


def ui_contrast_table(name, palette):
    rows = [
        f"### {name} UI affordance contrast\n",
        "| Token | Ratio vs bg | Target |",
        "| --- | ---: | --- |",
    ]
    bg = palette["bg"]
    for key in ["border_ui", "border_hi", "focus"]:
        ratio = contrast(bg, palette[key])
        target = "PASS" if ratio >= 3 else "FAIL"
        rows.append(f"| `{key}` | {ratio:.2f}:1 | {target} |")
    return "\n".join(rows)


def main():
    try:
        tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"unable to load theme tokens from {TOKENS}: {error}") from error

    guardrails = tokens["guardrails"]
    body_min = guardrails.get("minimum_apca_body", 75)
    ui_min = guardrails.get("minimum_apca_ui", 60)
    parts = [
        "# Dreamcoder Theme Preview",
        "",
        "Generated from `DreamcoderThemes/dreamcoder/tokens.json`.",
        "",
    ]
    parts += [
        "## Design rationale",
        "",
        "Dreamcoder light themes follow a **cocoa/lúcuma** identity: warm parchment backgrounds, graphite-brown text, and restrained accents. Unlike generic light themes that jump from white to mid-gray surfaces, Dreamcoder uses a **flat surface ladder** (~10 luminance points between steps) so panels feel layered without looking muddy.",
        "",
        "**Dreamcoder Dark** reserves a pure-black canvas through `surface_policy`, with scroll-safe near-black functional surfaces, indigo brand accents, icy diagnostics, and pastel syntax colors. Surfaces ladder from the canvas to lighter panels and modal layers. The opencode theme keeps the main background as `none` so the terminal's semi-transparent background remains visible while panels and selections carry the layered surface system.",
        "",
        "Semantic tokens are intentionally distinct:",
        "",
        "- `comment` is a desaturated pastel syntax color, while `subtle` remains reserved for low-emphasis UI chrome.",
        "- Dark `accent` (pastel indigo), `accent_2` (soft violet), `error` (soft rose), and `warning` (pale gold) form the Dreamcoder Dark signature.",
        "- `accent` carries runtime CTAs and active chrome; the explicit `brand` alias preserves the requested indigo identity while `focus` remains a blue keyboard/input affordance.",
        "- `on_accent`, `on_error`, and `selection_bg`/`selection_fg` are explicit pairs validated in CI.",
    ]
    parts += ["## Palette", ""]
    for mode, palette in tokens["modes"].items():
        parts.append(palette_table(palette.get("name", mode), palette))
        parts.append("")
    parts += ["## Contrast audit", ""]
    for mode, palette in tokens["modes"].items():
        label = palette.get("name", mode)
        parts.append(contrast_table(label, palette))
        parts.append("")
        parts.append(apca_table(label, palette, body_min, ui_min))
        parts.append("")
        parts.append(ui_contrast_table(label, palette))
        parts.append("")
    parts += [
        "## Usage",
        "",
        "```bash",
        "./scripts/dreamcoder auto",
        "./scripts/dreamcoder light",
        "./scripts/dreamcoder dark",
        "./scripts/dreamcoder verify",
        "./scripts/dreamcoder preview",
        "```",
        "",
    ]
    parts += [
        "## Design notes",
        "",
        "- Dark mode uses a pure black canvas reserved by `surface_policy`; light and dusk modes avoid pure black and pure white.",
        "- Main text targets AAA (WCAG 2) and APCA Lc ≥ 75 for long coding sessions.",
        "- Cocoa/Lúcuma accents are identity colors in light; Dreamcoder Dark uses indigo, violet, icy blue, soft rose, and pale gold for dark-mode personality.",
        "- UI affordance tokens (`border_ui`, `border_hi`, `focus`) target at least 3:1 against the main background.",
        "- opencode uses one canonical theme: `dreamcoder`; its main `background` is generated as `none` for terminal transparency.",
        "",
    ]
    output = OUT.resolve()
    expected_output = (ROOT / "docs/generated/dreamcoder-theme-preview.md").resolve()
    if output != expected_output or ROOT not in output.parents:
        raise SystemExit(f"refusing to write outside the repository preview path: {output}")
    output.write_text("\n".join(parts), encoding="utf-8")
    print(f"Generated {output}")


if __name__ == "__main__":
    main()
