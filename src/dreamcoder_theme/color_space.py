"""OKLCH <-> sRGB conversion and the canonical ``oklch(L C H)`` text form.

OKLab (Ottosson 2020) is perceptually uniform enough that equal lightness
steps look equal, which is why Dreamcoder primitives are authored in OKLCH and
only rendered to sRGB hex at the edges.
"""

from __future__ import annotations

import math
import re

_SRGB_BREAK = 0.04045
_SRGB_LINEAR_BREAK = 0.0031308
_OKLCH_TEXT = re.compile(r"^oklch\((?P<l>[0-9.]+) (?P<c>[0-9.]+) (?P<h>[0-9.]+)\)$")


def hex_to_unit_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return (int(value[0:2], 16) / 255, int(value[2:4], 16) / 255, int(value[4:6], 16) / 255)


def unit_rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb)


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= _SRGB_BREAK else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= _SRGB_LINEAR_BREAK else 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    lr, lg, lb = (srgb_to_linear(c) for c in hex_to_unit_rgb(value))
    lms_l = (0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb) ** (1 / 3)
    lms_m = (0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb) ** (1 / 3)
    lms_s = (0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb) ** (1 / 3)
    lightness = 0.2104542553 * lms_l + 0.7936177850 * lms_m - 0.0040720468 * lms_s
    a = 1.9779984951 * lms_l - 2.4285922050 * lms_m + 0.4505937099 * lms_s
    b = 0.0259040371 * lms_l + 0.7827717662 * lms_m - 0.8086757660 * lms_s
    return lightness, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def oklch_to_hex(lightness: float, chroma: float, hue: float) -> str:
    a = chroma * math.cos(math.radians(hue))
    b = chroma * math.sin(math.radians(hue))
    l_c = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_c = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_c = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lr = +4.0767416621 * l_c - 3.3077115913 * m_c + 0.2309699292 * s_c
    lg = -1.2684380046 * l_c + 2.6097574011 * m_c - 0.3413193965 * s_c
    lb = -0.0041960863 * l_c - 0.7034186147 * m_c + 1.7076147010 * s_c
    return unit_rgb_to_hex(tuple(linear_to_srgb(max(0.0, min(1.0, c))) for c in (lr, lg, lb)))  # type: ignore[arg-type]


def format_oklch(lightness: float, chroma: float, hue: float) -> str:
    """Canonical text. Four decimals round-trip nearly every 8-bit colour (not
    all: ~0.08% land one code value off), so tokens are checked per value."""
    hue = 0.0 if chroma < 5e-5 else round(hue, 2) % 360
    return f"oklch({lightness:.4f} {chroma:.4f} {hue:.2f})"


def parse_oklch(text: str) -> tuple[float, float, float]:
    match = _OKLCH_TEXT.match(text)
    if match is None:
        raise ValueError(f"not an oklch(L C H) value: {text!r}")
    lightness, chroma, hue = (float(match[g]) for g in ("l", "c", "h"))
    if not 0 <= lightness <= 1 or chroma > 0.4 or hue >= 360:
        raise ValueError(f"oklch value out of range: {text!r}")
    return lightness, chroma, hue
