#!/usr/bin/env python3
"""Generate a Dreamcoder specimen board (`--mode light|dark`, default light) as one deterministic SVG.

Four panels, all computed from `DreamcoderThemes/dreamcoder/tokens.json`:

1. primitive ramps: every `primitives.<mode>` colour, grouped by family (Dark: the graphite
   text ramp and surface ladder, then the pigments around the hue wheel);
2. roles on every surface, with the WCAG ratio and APCA Lc of each pair (magnitude, so
   Dark's negative polarity reads like Light's);
3. elevation e0-e4: Light is the key + ambient shadow model on the paper canvas; Dark is
   tonal surfaces with top-edge hairlines, no shadow is drawn on black;
4. pigment distinctness: the CIEDE2000 matrix between the accent roles.

Pure Python, no timestamps and no randomness: the same tokens always produce the
same bytes, so the checked-in board is a regression artefact (`git diff` shows
any perceptual change). Writes only the file given with `--output`.

Exit codes: 0 written, 2 unreadable or incomplete tokens.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme._math import apca_lc, contrast  # noqa: E402
from dreamcoder_theme.color_space import (  # noqa: E402
    delta_e2000,
    hex_to_oklch,
    oklch_to_hex,
    parse_oklch,
)

TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
MODES = ("light", "dark")
DEFAULT_MODE = "light"

SURFACES = ("bg", "surface0", "surface1", "surface2", "surface3")
DARK_SURFACES = (*SURFACES, "selection")
TEXT_ROLES = ("text_heading", "text", "muted", "subtle", "comment")
DARK_TEXT_ROLES = ("text_heading", "text", "muted", "comment", "subtle")
PIGMENT_ROLES = (
    "accent",
    "accent_2",
    "link",
    "error",
    "warning",
    "success",
    "sage",
    "focus",
    "diagnostic",
    "info",
    "lavender",
    "mauve",
)
MATRIX_ROLES = tuple(r for r in PIGMENT_ROLES if r != "link")
ELEVATION_SURFACE = {
    "e0": "bg",
    "e1": "surface1",
    "e2": "surface0",
    "e3": "surface0",
    "e4": "surface0",
}


def default_output(mode: str) -> Path:
    return ROOT / f"docs/generated/dreamcoder-{mode}-specimen.svg"


WIDTH = 1200
MARGIN = 40
FONT = "Inter, 'DejaVu Sans', sans-serif"
MONO = "'JetBrains Mono', 'DejaVu Sans Mono', monospace"
CLOSE_DELTA_E = 10.0


class TokenError(Exception):
    """tokens.json lacks something the specimen needs."""


class Board:
    """Accumulates SVG elements with a vertical cursor."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.defs: list[str] = []
        self.y = MARGIN

    def rect(self, x: int, y: int, w: int, h: int, fill: str, extra: str = "") -> None:
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>')

    def text(
        self,
        x: int,
        y: int,
        value: str,
        fill: str,
        size: int = 12,
        family: str = FONT,
        weight: int = 400,
        anchor: str = "start",
    ) -> None:
        self.parts.append(
            f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
        )

    def render(self, background: str) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{self.y}" '
            f'viewBox="0 0 {WIDTH} {self.y}">'
        )
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        base = f'<rect width="{WIDTH}" height="{self.y}" fill="{background}"/>'
        return "\n".join([head, defs, base, *self.parts, "</svg>", ""])


def load_tokens(path: Path) -> dict[str, Any]:
    try:
        tokens = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TokenError(f"{path}: {error}") from error
    if not isinstance(tokens, dict):
        raise TokenError(f"{path}: not a JSON object")
    return tokens


def _mode_colors(tokens: dict[str, Any], mode: str) -> dict[str, str]:
    colors: dict[str, str] = tokens.get("modes", {}).get(mode, {})
    surfaces = DARK_SURFACES if mode == "dark" else SURFACES
    missing = [r for r in (*surfaces, *TEXT_ROLES, *PIGMENT_ROLES) if r not in colors]
    if missing:
        raise TokenError(f"modes.{mode} lacks roles: {', '.join(missing)}")
    return colors


def _primitives(tokens: dict[str, Any], mode: str) -> dict[str, tuple[float, str]]:
    """name -> (OKLCH lightness, hex)."""
    raw: dict[str, str] = tokens.get("primitives", {}).get(mode, {})
    if not raw:
        raise TokenError(f"primitives.{mode} is missing")
    out: dict[str, tuple[float, str]] = {}
    for name, value in raw.items():
        try:
            lightness, chroma, hue = parse_oklch(value)
        except ValueError as error:
            raise TokenError(f"primitive {name}: {error}") from error
        out[name] = (lightness, oklch_to_hex(lightness, chroma, hue))
    return out


def _heading(board: Board, colors: dict[str, str], title: str, note: str) -> None:
    board.y += 28
    board.text(MARGIN, board.y, title, colors["text_heading"], 18, weight=600)
    board.y += 20
    board.text(MARGIN, board.y, note, colors["comment"], 12)
    board.y += 20


NEUTRAL_FAMILIES = {"light": ("paper", "ink", "clay"), "dark": ("graphite",)}
GRAPHITE_SPLIT = 0.5  # OKLab L: at or above it a graphite step is text, below it a surface
GRAPHITE_CAPTIONS = (
    "graphite text ramp (strictly ordered, brightest first)",
    "graphite surface ladder (tonal elevation, even OKLab steps up from the OLED canvas)",
)


def panel_primitives(
    board: Board, colors: dict[str, str], tokens: dict[str, Any], mode: str
) -> None:
    _heading(board, colors, "1 · Primitive ramps", f"primitives.{mode}, OKLCH rendered to sRGB hex")
    # Material story, one row per family: Light is paper, ink, clay; Dark is the graphite ramp and
    # ladder. Pigments follow, around the hue wheel.
    families: dict[str, list[tuple[str, float, str]]] = {}
    for name, (lightness, value) in _primitives(tokens, mode).items():
        families.setdefault(name.split(".")[0], []).append((name, lightness, value))
    neutrals = [f for f in NEUTRAL_FAMILIES[mode] if f in families]
    pigments = sorted(
        (f for f in families if f not in neutrals),
        key=lambda f: hex_to_oklch(max(families[f], key=lambda m: m[1])[2])[2],
    )
    rows = [sorted(families[f], key=lambda m: -m[1]) for f in neutrals]
    captions: list[str | None] = [None] * len(rows)
    if mode == "dark":
        graphite = rows.pop(0)
        rows = [
            [m for m in graphite if m[1] >= GRAPHITE_SPLIT],
            [m for m in graphite if m[1] < GRAPHITE_SPLIT],
            *rows,
        ]
        captions = [*GRAPHITE_CAPTIONS, *[None] * (len(rows) - 2)]
    flat = [m for f in pigments for m in sorted(families[f], key=lambda m: -m[1])]
    pigment_rows = [flat[i : i + 9] for i in range(0, len(flat), 9)]
    rows += pigment_rows
    pigment_caption = "pigments around the hue wheel, one OKLab L" if mode == "dark" else None
    captions += [pigment_caption] * len(pigment_rows)
    step, width = 126, 116
    for row, caption in zip(rows, captions, strict=True):
        if caption:
            board.text(MARGIN, board.y + 8, caption, colors["comment"], 11)
            board.y += 18
        for column, (name, _, value) in enumerate(row):
            x = MARGIN + column * step
            board.rect(x, board.y, width, 36, value, f' stroke="{colors["border"]}"')
            board.text(x, board.y + 52, name, colors["text"], 11, MONO)
            board.text(x, board.y + 64, value, colors["muted"], 10, MONO)
        board.y += 80
    board.y += 10


def panel_roles(board: Board, colors: dict[str, str], mode: str) -> None:
    dark = mode == "dark"
    _heading(
        board,
        colors,
        "2 · Roles on every surface",
        "WCAG 2 ratio and APCA Lc magnitude of each role on each surface; light text on black is "
        "negative polarity (higher is easier to read)"
        if dark
        else "WCAG 2 ratio and APCA Lc of each role on each surface (higher is easier to read)",
    )
    # Dark adds the selection surface, so its six columns are narrower than Light's five.
    surfaces = DARK_SURFACES if dark else SURFACES
    label_w, cell_w, cell_h, text_dx = (110, 172, 40, 40) if dark else (130, 200, 40, 52)
    for column, surface in enumerate(surfaces):
        # Light surface3 carries borders and pressed fills, never body text (no 4.5:1 floor there).
        label = f"{surface} · non-text" if surface == "surface3" and not dark else surface
        board.text(MARGIN + label_w + column * cell_w, board.y, label, colors["muted"], 11, MONO)
    board.y += 10
    for role in (*(DARK_TEXT_ROLES if dark else TEXT_ROLES), *PIGMENT_ROLES, "link_hover"):
        if role not in colors:
            continue
        board.text(MARGIN, board.y + 25, role, colors["text"], 12, MONO)
        for column, surface in enumerate(surfaces):
            x = MARGIN + label_w + column * cell_w
            ratio = contrast(colors[role], colors[surface])
            lc = abs(apca_lc(colors[role], colors[surface]))
            board.rect(
                x, board.y, cell_w - 8, cell_h, colors[surface], f' stroke="{colors["border"]}"'
            )
            board.text(x + 10, board.y + 26, "Aa", colors[role], 18, weight=600)
            board.text(
                x + text_dx, board.y + 25, f"{ratio:.2f}:1  Lc {lc:.0f}", colors[role], 12, MONO
            )
        board.y += cell_h + 6
    board.y += 14


def _shadow_filter(name: str, ink: str, dy: float, blur: float, alpha: float) -> str:
    return (
        f'<filter id="{name}" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feDropShadow dx="0" dy="{dy:g}" stdDeviation="{blur / 2:g}" '
        f'flood-color="{ink}" flood-opacity="{alpha:g}"/></filter>'
    )


def _dark_elevation_surfaces(
    elevation: dict[str, Any], primitives: dict[str, tuple[float, str]]
) -> tuple[dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    """Level -> (primitive name, hex) for the tonal surfaces and their top-edge hairlines."""
    out: list[dict[str, tuple[str, str]]] = []
    for key in ("surface", "edge"):
        named: dict[str, str] = elevation.get(key, {}).get("dark", {})
        missing = [n for n in named.values() if n not in primitives]
        if missing:
            raise TokenError(f"components.elevation.{key}.dark names unknown primitives: {missing}")
        out.append({level: (name, primitives[name][1]) for level, name in named.items()})
    return out[0], out[1]


def panel_elevation_dark(board: Board, colors: dict[str, str], tokens: dict[str, Any]) -> None:
    _heading(
        board,
        colors,
        "3 · Elevation e0-e4",
        "tonal: each level is a lighter graphite surface (emission); no shadow is drawn, black ink is "
        "invisible on the OLED canvas",
    )
    elevation = tokens.get("components", {}).get("elevation", {})
    surfaces, edges = _dark_elevation_surfaces(elevation, _primitives(tokens, "dark"))
    top = board.y
    board.rect(MARGIN, top, WIDTH - 2 * MARGIN, 190, colors["bg"], f' stroke="{colors["border"]}"')
    step = (WIDTH - 2 * MARGIN) // 5
    for column, level in enumerate(("e0", *elevation.get("levels", {}))):
        x = MARGIN + 24 + column * step
        name, fill = surfaces.get(level, ("bg", colors["bg"]))
        board.rect(x, top + 30, 140, 90, fill, ' rx="8"')
        if level in edges:
            # The overhead key light catching the top edge, one ladder step lighter.
            board.rect(x + 8, top + 30, 124, 2, edges[level][1])
        board.text(x + 70, top + 80, level, colors["text"], 16, MONO, 600, "middle")
        board.text(x + 70, top + 142, f"{name}  {fill}", colors["muted"], 11, MONO, anchor="middle")
        detail = f"top edge {edges[level][0]}" if level in edges else "no edge"
        board.text(x + 70, top + 158, detail, colors["muted"], 11, MONO, anchor="middle")
    board.y = top + 190 + 24


def panel_elevation(
    board: Board, colors: dict[str, str], tokens: dict[str, Any], mode: str
) -> None:
    if mode == "dark":
        panel_elevation_dark(board, colors, tokens)
        return
    _heading(
        board,
        colors,
        "3 · Elevation e0-e4",
        "one key light (0 z/2 z) plus sky ambient (0 0 2z), warm-ink shadow on the paper canvas",
    )
    elevation = tokens.get("components", {}).get("elevation", {})
    ink_name = elevation.get("ink", {}).get(mode)
    primitives = _primitives(tokens, mode)
    if ink_name not in primitives:
        raise TokenError(f"components.elevation.ink.{mode} is not a primitive")
    ink = primitives[ink_name][1]
    levels: dict[str, Any] = elevation.get("levels", {})
    top = board.y
    board.rect(MARGIN, top, WIDTH - 2 * MARGIN, 190, colors["bg"], f' stroke="{colors["border"]}"')
    step = (WIDTH - 2 * MARGIN) // 5
    for column, level in enumerate(("e0", *levels)):
        x = MARGIN + 24 + column * step
        fill = colors[ELEVATION_SURFACE.get(level, "surface0")]
        spec = levels.get(level)
        if spec is not None:
            z = float(spec["z"])
            ambient, key = f"{level}-ambient", f"{level}-key"
            board.defs.append(_shadow_filter(ambient, ink, 0, 2 * z, float(spec["ambient_alpha"])))
            board.defs.append(_shadow_filter(key, ink, z / 2, z, float(spec["key_alpha"])))
            for filter_id in (ambient, key):
                board.rect(x, top + 30, 140, 90, fill, f' rx="8" filter="url(#{filter_id})"')
        board.rect(x, top + 30, 140, 90, fill, f' rx="8" stroke="{colors["border"]}"')
        board.text(x + 70, top + 80, level, colors["text"], 16, MONO, 600, "middle")
        detail = (
            "canvas"
            if spec is None
            else f"z {z:g}  key {spec['key_alpha']:g}  amb {spec['ambient_alpha']:g}"
        )
        board.text(x + 70, top + 150, detail, colors["muted"], 11, MONO, anchor="middle")
    board.y = top + 190 + 24


def panel_pigments(board: Board, colors: dict[str, str]) -> None:
    _heading(
        board,
        colors,
        "4 · Pigment distinctness (ΔE2000)",
        f"between accent roles; a shaded cell is below ΔE {CLOSE_DELTA_E:g} (hard to tell apart, 0.0 = alias)",
    )
    label_w, cell = 100, 84
    for column, role in enumerate(MATRIX_ROLES):
        board.text(
            MARGIN + label_w + column * cell + cell // 2,
            board.y,
            role,
            colors["muted"],
            10,
            MONO,
            anchor="middle",
        )
    board.y += 10
    for row, name in enumerate(MATRIX_ROLES):
        y = board.y + row * 30
        board.text(MARGIN, y + 19, name, colors["text"], 11, MONO)
        for column, other in enumerate(MATRIX_ROLES):
            x = MARGIN + label_w + column * cell
            if name == other:
                board.rect(x, y, cell - 4, 26, colors[name], ' rx="4"')
                continue
            delta = delta_e2000(colors[name], colors[other])
            fill = colors["surface3"] if delta < CLOSE_DELTA_E else colors["surface0"]
            board.rect(x, y, cell - 4, 26, fill, f' rx="4" stroke="{colors["border"]}"')
            board.text(
                x + (cell - 4) // 2,
                y + 18,
                f"{delta:.1f}",
                colors["text"],
                11,
                MONO,
                anchor="middle",
            )
    board.y += len(MATRIX_ROLES) * 30 + 20


def build_specimen(tokens: dict[str, Any], mode: str = DEFAULT_MODE) -> str:
    colors = _mode_colors(tokens, mode)
    board = Board()
    board.text(
        MARGIN,
        board.y + 14,
        f"Dreamcoder {mode.capitalize()} specimen",
        colors["text_heading"],
        26,
        weight=600,
    )
    board.y += 34
    board.text(
        MARGIN,
        board.y,
        "Generated by scripts/generate-specimen.py from DreamcoderThemes/dreamcoder/tokens.json. Do not edit.",
        colors["comment"],
        12,
    )
    panels: tuple[Callable[[], None], ...] = (
        lambda: panel_primitives(board, colors, tokens, mode),
        lambda: panel_roles(board, colors, mode),
        lambda: panel_elevation(board, colors, tokens, mode),
        lambda: panel_pigments(board, colors),
    )
    for panel in panels:
        panel()
    board.y += MARGIN - 10
    return board.render(colors["bg"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a Dreamcoder specimen board (SVG).")
    parser.add_argument("--mode", choices=MODES, default=DEFAULT_MODE, help="colour mode (light)")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="SVG file to write (default docs/generated/dreamcoder-<mode>-specimen.svg)",
    )
    parser.add_argument("--tokens", type=Path, default=TOKENS, help="tokens.json to read")
    args = parser.parse_args(argv)
    try:
        svg = build_specimen(load_tokens(args.tokens), args.mode)
    except TokenError as error:
        print(f"generate-specimen: {error}", file=sys.stderr)
        return 2
    output: Path = args.output or default_output(args.mode)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(svg.encode("utf-8"))
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
