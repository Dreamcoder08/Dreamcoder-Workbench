"""Resolve the component tier: elevation, radius and border for one mode.

One key light, overhead and slightly in front of the screen, so every shadow
falls straight down. Each level is two terms: a Lambert key
(``0 {z/2}px {z}px``) and a sky ambient (``0 0 {2z}px``). The shadow colour is
the mode's ink primitive: warm ink on Light, because interreflection off warm
paper keeps the umbra warm, and graphite.000 on Dark, where the black canvas
swallows it and only a window floating over the lit wallpaper shows it.

A mode may also name tonal elevation: on an emissive OLED canvas each level
rises to a lighter neutral surface (``surface``), and the top two levels catch
the overhead key on a lighter top edge (``edge``). A mode without a component
colour resolves to nothing, so its output stays untouched.
"""

from __future__ import annotations

from typing import Any

from .color_space import oklch_to_hex, parse_oklch
from .token_tiers import TierError


def _number(value: float) -> str:
    return f"{value:g}"


def _hex(primitives: dict[str, str], mode: str, name: str) -> str:
    if name not in primitives:
        raise TierError(f"{mode}: component colour {name} is not a primitive")
    try:
        return oklch_to_hex(*parse_oklch(primitives[name]))
    except ValueError as error:
        raise TierError(f"{mode}: primitive {name}: {error}") from error


def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {_number(alpha)})"


def _shadow(ink: str, z: float, key_alpha: float, ambient_alpha: float) -> str:
    key = f"0 {_number(z / 2)}px {_number(z)}px {_rgba(ink, key_alpha)}"
    ambient = f"0 0 {_number(2 * z)}px {_rgba(ink, ambient_alpha)}"
    return f"{key}, {ambient}"


def _tonal(group: dict[str, Any], primitives: dict[str, str], mode: str) -> dict[str, str] | None:
    names: dict[str, str] | None = group.get(mode)
    if names is None:
        return None
    return {level: _hex(primitives, mode, name) for level, name in names.items()}


def adopts_components(tokens: dict[str, Any], mode: str) -> bool:
    """A mode adopts the component tier when it names a shadow ink; others are untouched."""
    ink: dict[str, Any] = tokens.get("components", {}).get("elevation", {}).get("ink", {})
    return mode in ink


def resolve_components(tokens: dict[str, Any], mode: str) -> dict[str, Any]:
    components: dict[str, Any] = tokens.get("components", {})
    elevation: dict[str, Any] = components.get("elevation", {})
    if not adopts_components(tokens, mode):
        return {}
    ink_name = elevation["ink"][mode]
    primitives: dict[str, str] = tokens.get("primitives", {}).get(mode, {})
    ink = _hex(primitives, mode, ink_name)

    shadows: dict[str, str] = {}
    previous = 0.0
    for level, spec in elevation.get("levels", {}).items():
        z = float(spec["z"])
        if z <= previous:
            raise TierError(f"{mode}: elevation {level} z={z:g} does not exceed {previous:g}")
        previous = z
        shadows[level] = _shadow(ink, z, float(spec["key_alpha"]), float(spec["ambient_alpha"]))

    hairline = components.get("border", {}).get("hairline", {})
    border: dict[str, str] = {"hairline": f"{_number(hairline.get('width', 1))}px"}
    border_name = hairline.get("color", {}).get(mode)
    if border_name is not None:
        border["hairline_color"] = _hex(primitives, mode, border_name)

    resolved: dict[str, Any] = {
        "shadow_ink": ink,
        "elevation": shadows,
        "radius": {k: f"{_number(v)}px" for k, v in components.get("radius", {}).items()},
        "border": border,
    }
    for key in ("surface", "edge"):
        tonal = _tonal(elevation.get(key, {}), primitives, mode)
        if tonal is not None:
            resolved[key] = tonal
    return resolved


def palette_keys(tokens: dict[str, Any], mode: str) -> dict[str, str]:
    """Flatten the resolved component tier into string palette keys for renderers."""
    resolved = resolve_components(tokens, mode)
    if not resolved:
        return {}
    keys = {"shadow_ink": resolved["shadow_ink"]}
    keys.update({f"elevation_{k}": v for k, v in resolved["elevation"].items()})
    keys.update({f"radius_{k}": v for k, v in resolved["radius"].items()})
    keys.update({f"border_{k}": v for k, v in resolved["border"].items()})
    for tonal in ("surface", "edge"):
        keys.update({f"elevation_{tonal}_{k}": v for k, v in resolved.get(tonal, {}).items()})
    return keys
