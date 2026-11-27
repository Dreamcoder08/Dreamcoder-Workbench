"""Resolve the rhythm tier: spacing, motion and typography for one mode.

Spacing is a 4 px base grid, so every gap is a multiple of the one below it.
Motion durations step by ~1.6x (perceptual just-noticeable difference) and the
curves approximate a critically damped spring: no overshoot, so every bezier
control value stays within [0, 1]. Typography is one contract shared by every
mode, with the font families recorded once. A mode that has not adopted the
component tier resolves to nothing, so its output stays untouched.
"""

from __future__ import annotations

from typing import Any

from .elevation import adopts_components
from .token_tiers import TierError

GRID = 4
DURATIONS = ("quick", "base", "slow")
CURVES = ("enter", "exit", "move")


def _number(value: float) -> str:
    return f"{value:g}"


def _spacing(raw: dict[str, Any]) -> dict[str, str]:
    for step, value in raw.items():
        if not isinstance(value, int) or value < GRID or value % GRID:
            raise TierError(f"spacing {step}={value!r} is not a multiple of {GRID}px")
    return {step: f"{value}px" for step, value in raw.items()}


def _durations(raw: dict[str, Any]) -> dict[str, str]:
    previous = 0
    out: dict[str, str] = {}
    for name in DURATIONS:
        value = raw[name]
        if value <= previous:
            raise TierError(f"motion duration {name}={value} does not exceed {previous}")
        previous = value
        out[name] = f"{value}ms"
    return out


def _curves(raw: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in CURVES:
        points = raw[name]
        if len(points) != 4 or any(not 0 <= p <= 1 for p in points):
            raise TierError(f"motion curve {name}={points!r} overshoots [0, 1]")
        out[name] = f"cubic-bezier({', '.join(_number(p) for p in points)})"
    return out


def resolve_rhythm(tokens: dict[str, Any], mode: str) -> dict[str, Any]:
    if not adopts_components(tokens, mode):
        return {}
    components: dict[str, Any] = tokens["components"]
    motion: dict[str, Any] = components["motion"]
    typography: dict[str, Any] = dict(tokens["modes"][mode]["typography"])
    typography["font_family"] = dict(components["typography"]["font_family"])
    return {
        "spacing": _spacing(components["spacing"]),
        "motion": {
            "duration": _durations(motion["duration"]),
            "curve": _curves(motion["curve"]),
        },
        "typography": typography,
    }


def palette_keys(tokens: dict[str, Any], mode: str) -> dict[str, str]:
    """Flatten the resolved rhythm tier into string palette keys for renderers."""
    resolved = resolve_rhythm(tokens, mode)
    if not resolved:
        return {}
    keys = {f"space_{k}": v for k, v in resolved["spacing"].items()}
    keys.update({f"motion_duration_{k}": v for k, v in resolved["motion"]["duration"].items()})
    keys.update({f"motion_curve_{k}": v for k, v in resolved["motion"]["curve"].items()})
    typography = resolved["typography"]
    keys.update({f"type_{k}": str(v) for k, v in typography.items() if k != "font_family"})
    keys.update({f"font_{k}": v for k, v in typography["font_family"].items()})
    return keys
