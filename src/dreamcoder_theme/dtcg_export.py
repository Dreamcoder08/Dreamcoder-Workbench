"""Export ``tokens.json`` as a Design Tokens Community Group (DTCG) 2025.10 document.

The export is a pure function of the tokens: it reuses the tier resolvers
(``token_tiers``, ``elevation``, ``rhythm``) and the OKLCH helpers, so no colour
or shadow arithmetic is repeated here. Layout:

* ``primitive.light.<family>.<step>``: OKLCH colours with an exact sRGB hex fallback;
* ``semantic.light.<role>``: aliases of the primitive each role is bound to
  (translucent roles are sRGB colours with alpha);
* ``semantic.dark.<role>``: sRGB colours, because Dark has no primitives yet;
* ``component.*``: spacing, radius, motion, elevation, hairline and font families.

Figma, Penpot and Style Dictionary 5 read this format.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .color_space import hex_to_unit_rgb, oklch_to_hex, parse_oklch
from .elevation import resolve_components
from .rhythm import resolve_rhythm
from .token_tiers import TierError, drift

SCHEMA_URL = "https://www.designtokens.org/schemas/2025.10/format.json"
SOURCE = "DreamcoderThemes/dreamcoder/tokens.json"
PRIMITIVE_MODE = "light"
SEMANTIC_MODES = ("light", "dark")

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_RGBA = re.compile(r"^rgba\((\d+), (\d+), (\d+), ([0-9.]+)\)$")
_SHADOW_LAYER = re.compile(
    r"(-?[0-9.]+)(?:px)? (-?[0-9.]+)(?:px)? ([0-9.]+)(?:px)? rgba\((\d+), (\d+), (\d+), ([0-9.]+)\)"
)
_BEZIER = re.compile(r"^cubic-bezier\((.+)\)$")

Doc = dict[str, Any]


class ExportError(ValueError):
    """The tokens cannot be expressed as a valid DTCG document."""


def _number(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value


def _token(type_: str, value: Any) -> Doc:
    return {"$type": type_, "$value": value}


def _srgb(hex_color: str, alpha: float | None = None) -> Doc:
    value: Doc = {
        "colorSpace": "srgb",
        "components": [round(c, 6) for c in hex_to_unit_rgb(hex_color)],
    }
    if alpha is not None:
        value["alpha"] = alpha
    value["hex"] = hex_color.lower()
    return value


def _rgba_value(raw: str) -> Doc:
    match = _RGBA.match(raw)
    if match is None:
        raise ExportError(f"not an rgba(r, g, b, a) value: {raw!r}")
    red, green, blue = (int(match[i]) for i in (1, 2, 3))
    return _srgb(f"#{red:02x}{green:02x}{blue:02x}", float(match[4]))


def _colour_role(raw: Any) -> Doc | None:
    """sRGB colour of a semantic role, or None when the value is not a colour."""
    if isinstance(raw, str) and _HEX.match(raw):
        return _srgb(raw)
    if isinstance(raw, str) and raw.startswith("rgba("):
        return _rgba_value(raw)
    return None


def _alias(mode: str, primitive: str) -> str:
    """Reference to the primitive named ``family.step`` (the dot is the path separator)."""
    return f"{{primitive.{mode}.{primitive}}}"


def _px(text: str) -> Doc:
    return {"value": _number(float(text.removesuffix("px"))), "unit": "px"}


def _group(description: str, children: Doc) -> Doc:
    return {"$description": description, **children}


def _primitives(tokens: Doc) -> Doc:
    families: Doc = {}
    for name, text in tokens["primitives"][PRIMITIVE_MODE].items():
        family, _, step = name.partition(".")
        try:
            lightness, chroma, hue = parse_oklch(text)
        except ValueError as error:
            raise ExportError(f"primitive {name}: {error}") from error
        value = {
            "colorSpace": "oklch",
            "components": [lightness, chroma, hue],
            "hex": oklch_to_hex(lightness, chroma, hue),
        }
        families.setdefault(family, {})[step] = _token("color", value)
    light = _group(f"Dreamcoder Light OKLCH primitives from {SOURCE} (primitives.light).", families)
    return _group(f"Tier 1: raw colours, generated from {SOURCE}.", {PRIMITIVE_MODE: light})


def _semantic_mode(tokens: Doc, mode: str) -> Doc:
    bindings: dict[str, str] = tokens.get("bindings", {}).get(mode, {})
    roles: Doc = {}
    for role, raw in tokens["modes"][mode].items():
        if role in bindings:
            roles[role] = _token("color", _alias(mode, bindings[role]))
            continue
        value = _colour_role(raw)
        if value is not None:
            roles[role] = _token("color", value)
    origin = f"{SOURCE} (modes.{mode})"
    note = "aliases of the primitive each role is bound to" if bindings else "sRGB colours"
    return _group(f"Dreamcoder {mode.title()} semantic roles from {origin}: {note}.", roles)


def _semantic(tokens: Doc) -> Doc:
    modes = {mode: _semantic_mode(tokens, mode) for mode in SEMANTIC_MODES}
    return _group(f"Tier 2: roles per mode, generated from {SOURCE}.", modes)


def _shadow(css: str) -> list[Doc]:
    layers = []
    for match in _SHADOW_LAYER.finditer(css):
        x, y, blur = (_number(float(match[i])) for i in (1, 2, 3))
        base = f"#{int(match[4]):02x}{int(match[5]):02x}{int(match[6]):02x}"
        layers.append(
            {
                "color": _srgb(base, float(match[7])),
                "offsetX": {"value": x, "unit": "px"},
                "offsetY": {"value": y, "unit": "px"},
                "blur": {"value": blur, "unit": "px"},
                "spread": {"value": 0, "unit": "px"},
            }
        )
    if not layers:
        raise ExportError(f"no shadow layer in {css!r}")
    return layers


def _curve(css: str) -> list[float]:
    match = _BEZIER.match(css)
    if match is None:
        raise ExportError(f"not a cubic-bezier() value: {css!r}")
    return [_number(float(part)) for part in match[1].split(",")]


def _scale(values: dict[str, str]) -> Doc:
    return {step: _token("dimension", _px(text)) for step, text in values.items()}


def _components(tokens: Doc) -> Doc:
    try:
        rhythm = resolve_rhythm(tokens, PRIMITIVE_MODE)
        resolved = resolve_components(tokens, PRIMITIVE_MODE)
    except TierError as error:
        raise ExportError(str(error)) from error
    motion = rhythm["motion"]
    hairline = tokens["components"]["border"]["hairline"]["color"][PRIMITIVE_MODE]
    groups: Doc = {
        "spacing": _group("4 px base grid.", _scale(rhythm["spacing"])),
        "radius": _group("Corner radius scale.", _scale(resolved["radius"])),
        "elevation": _group(
            "Light elevation: one overhead key light plus sky ambient, warm-ink shadows.",
            {level: _token("shadow", _shadow(css)) for level, css in resolved["elevation"].items()},
        ),
        "border": _group(
            "Light hairline border.",
            {
                "hairline-width": _token("dimension", _px(resolved["border"]["hairline"])),
                "hairline-color": _token("color", _alias(PRIMITIVE_MODE, hairline)),
            },
        ),
        "motion": _group(
            "Durations step by about 1.6x; curves approximate a critically damped spring.",
            {
                "duration": {
                    name: _token("duration", {"value": int(text.removesuffix("ms")), "unit": "ms"})
                    for name, text in motion["duration"].items()
                },
                "curve": {
                    name: _token("cubicBezier", _curve(css))
                    for name, css in motion["curve"].items()
                },
            },
        ),
        "typography": _group(
            "Font families shared by every mode.",
            {
                "font-family": {
                    role: _token("fontFamily", name)
                    for role, name in rhythm["typography"]["font_family"].items()
                }
            },
        ),
    }
    return _group(f"Tier 3: mode-independent geometry and rhythm, generated from {SOURCE}.", groups)


def build_dtcg(tokens: Doc) -> Doc:
    """DTCG 2025.10 document for ``tokens``; raises ``ExportError`` on inconsistent tiers."""
    problems = drift(tokens)
    if problems:
        raise ExportError("; ".join(problems))
    try:
        return {
            "$schema": SCHEMA_URL,
            "$description": (
                "Dreamcoder Workbench design tokens in DTCG 2025.10 (Format and Color modules). "
                f"Generated from {SOURCE} by scripts/export-dtcg.py; never edit by hand."
            ),
            "primitive": _primitives(tokens),
            "semantic": _semantic(tokens),
            "component": _components(tokens),
        }
    except KeyError as error:
        raise ExportError(f"tokens are missing {error}") from error


def render_dtcg(tokens: Doc) -> str:
    """Deterministic text of the export: fixed key order, two-space indent, final newline."""
    return json.dumps(build_dtcg(tokens), indent=2, ensure_ascii=False) + "\n"
