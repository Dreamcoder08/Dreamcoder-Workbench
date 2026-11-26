"""OKLCH <-> sRGB conversion and the canonical ``oklch(L C H)`` text form.

OKLab (Ottosson 2020) is perceptually uniform enough that equal lightness
steps look equal, which is why Dreamcoder primitives are authored in OKLCH and
only rendered to sRGB hex at the edges.
"""

from __future__ import annotations

import math
import re

Lab = tuple[float, float, float]

_SRGB_BREAK = 0.04045
_SRGB_LINEAR_BREAK = 0.0031308
_D65_WHITE = (0.95047, 1.0, 1.08883)
_LAB_EPSILON = 216 / 24389
_LAB_KAPPA = 24389 / 27
_POW7_25 = 25.0**7
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


def unit_rgb_to_oklab(rgb: tuple[float, float, float]) -> Lab:
    """OKLab (L, a, b) of an sRGB colour given as 0..1 channels."""
    lr, lg, lb = (srgb_to_linear(c) for c in rgb)
    lms_l = (0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb) ** (1 / 3)
    lms_m = (0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb) ** (1 / 3)
    lms_s = (0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb) ** (1 / 3)
    lightness = 0.2104542553 * lms_l + 0.7936177850 * lms_m - 0.0040720468 * lms_s
    a = 1.9779984951 * lms_l - 2.4285922050 * lms_m + 0.4505937099 * lms_s
    b = 0.0259040371 * lms_l + 0.7827717662 * lms_m - 0.8086757660 * lms_s
    return lightness, a, b


def rgb_to_oklab(red: int, green: int, blue: int) -> Lab:
    """OKLab (L, a, b) of an 8-bit sRGB colour."""
    return unit_rgb_to_oklab((red / 255, green / 255, blue / 255))


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    lightness, a, b = unit_rgb_to_oklab(hex_to_unit_rgb(value))
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


def hex_to_lab(value: str) -> Lab:
    """CIE L*a*b* (D65) of an sRGB hex colour."""
    r, g, b = (srgb_to_linear(c) for c in hex_to_unit_rgb(value))
    xyz = (
        0.4124564 * r + 0.3575761 * g + 0.1804375 * b,
        0.2126729 * r + 0.7151522 * g + 0.0721750 * b,
        0.0193339 * r + 0.1191920 * g + 0.9503041 * b,
    )
    fx, fy, fz = (
        t ** (1 / 3) if t > _LAB_EPSILON else (_LAB_KAPPA * t + 16) / 116
        for t in (c / w for c, w in zip(xyz, _D65_WHITE, strict=True))
    )
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def _hue_degrees(a: float, b: float) -> float:
    return math.degrees(math.atan2(b, a)) % 360 if a or b else 0.0


def delta_e2000(first: str | Lab, second: str | Lab) -> float:
    """CIEDE2000 colour difference (Sharma, Wu & Dalal 2005).

    Each argument is an sRGB hex string or a CIE Lab tuple.
    """
    lab1 = hex_to_lab(first) if isinstance(first, str) else first
    lab2 = hex_to_lab(second) if isinstance(second, str) else second
    (l1, a1, b1), (l2, a2, b2) = lab1, lab2
    c_mean = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(c_mean**7 / (c_mean**7 + _POW7_25)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1, c2 = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1, h2 = _hue_degrees(a1p, b1), _hue_degrees(a2p, b2)

    chromatic = c1 * c2 != 0
    dh = 0.0
    if chromatic:
        dh = h2 - h1
        if dh > 180:
            dh -= 360
        elif dh < -180:
            dh += 360
    d_l, d_c = l2 - l1, c2 - c1
    d_h = 2 * math.sqrt(c1 * c2) * math.sin(math.radians(dh / 2))

    l_mean, c_bar = (l1 + l2) / 2, (c1 + c2) / 2
    h_bar = h1 + h2
    if chromatic:
        h_bar /= 2
        if abs(h1 - h2) > 180:
            h_bar += 180 if h1 + h2 < 360 else -180
    t = (
        1
        - 0.17 * math.cos(math.radians(h_bar - 30))
        + 0.24 * math.cos(math.radians(2 * h_bar))
        + 0.32 * math.cos(math.radians(3 * h_bar + 6))
        - 0.20 * math.cos(math.radians(4 * h_bar - 63))
    )
    d_theta = 30 * math.exp(-(((h_bar - 275) / 25) ** 2))
    r_c = 2 * math.sqrt(c_bar**7 / (c_bar**7 + _POW7_25))
    s_l = 1 + 0.015 * (l_mean - 50) ** 2 / math.sqrt(20 + (l_mean - 50) ** 2)
    s_c = 1 + 0.045 * c_bar
    s_h = 1 + 0.015 * c_bar * t
    r_t = -math.sin(math.radians(2 * d_theta)) * r_c
    term_c, term_h = d_c / s_c, d_h / s_h
    return math.sqrt((d_l / s_l) ** 2 + term_c**2 + term_h**2 + r_t * term_c * term_h)
