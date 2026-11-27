"""Pure color math functions — zero I/O, zero side effects.

Domain layer of the Dreamcoder theme engine. Imports only stdlib math types.
"""

from __future__ import annotations

import math


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string."""
    return "#" + "".join(f"{max(0, min(255, part)):02x}" for part in rgb)


def mix(left: str, right: str, amount: float) -> str:
    """Linear interpolation between two hex colors."""
    a = hex_to_rgb(left)
    b = hex_to_rgb(right)
    return rgb_to_hex(tuple(round(x + (y - x) * amount) for x, y in zip(a, b)))  # type: ignore[arg-type]


def rel_luminance(value: str) -> float:
    """WCAG 2.2 relative luminance of a hex color."""
    r, g, b = hex_to_rgb(value)
    sr, sg, sb = r / 255, g / 255, b / 255
    lr = sr / 12.92 if sr <= 0.03928 else ((sr + 0.055) / 1.055) ** 2.4
    lg = sg / 12.92 if sg <= 0.03928 else ((sg + 0.055) / 1.055) ** 2.4
    lb = sb / 12.92 if sb <= 0.03928 else ((sb + 0.055) / 1.055) ** 2.4
    return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb


def contrast(fg: str, bg: str) -> float:
    """WCAG 2.2 contrast ratio between two hex colors."""
    a, b = sorted((rel_luminance(fg), rel_luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def guard(color: str, background: str, mode_name: str, minimum: float = 4.5) -> str:
    """Adjust color toward white (dark mode) or black (light mode) until
    it meets the minimum contrast ratio against the background."""
    target = "#ffffff" if mode_name == "dark" else "#000000"
    safe = color
    for _ in range(12):
        if contrast(safe, background) >= minimum:
            return safe
        safe = mix(safe, target, 0.18)
    return safe


def compute_on_color(
    background: str,
    mode_name: str,
    *,
    light_candidate: str | None = None,
    dark_candidate: str | None = None,
    canvas: str = "#000000",
    minimum: float = 4.5,
) -> str:
    """Pick readable foreground (text) on a filled surface.

    Dark falls back to ``canvas``, the OLED canvas the filled surface sits on.
    """
    candidates: list[str]
    if mode_name == "dark":
        candidates = [c for c in (dark_candidate, canvas) if c]
    else:
        candidates = [c for c in (light_candidate, "#fff7ea", "#ffffff") if c]
    for candidate in candidates:
        if contrast(candidate, background) >= minimum:
            return candidate
    return guard(candidates[-1], background, mode_name, minimum=minimum)


def surface_guard(
    color: str,
    background: str,
    mode_name: str,
    minimum: float = 1.05,
    maximum: float = 2.4,
) -> str:
    """Keep color within a contrast range against background for UI surfaces."""
    if contrast(color, background) < minimum:
        target = "#ffffff" if mode_name == "dark" else "#000000"
        safe = color
        for _ in range(12):
            safe = mix(safe, target, 0.08)
            if contrast(safe, background) >= minimum:
                return safe
        return safe
    if contrast(color, background) > maximum:
        safe = color
        for _ in range(12):
            safe = mix(safe, background, 0.12)
            if contrast(safe, background) <= maximum:
                return safe
        return safe
    return color


# ------------------------------------------------------------------
# SAPC/APCA 0.0.98G-4g constants (canonical, ADR-001)
#
# Values cross-validated against the former duplicated implementations
# in scripts/verify-theme-health.py, scripts/generate-theme-preview.py,
# and tests/test_dreamcoder_global_design_system.py, which now import
# this module. Do not change these without updating the known-vector
# evidence in tests/test_apca_implementation.py.
# ------------------------------------------------------------------
_APCA_COEFF_R = 0.2126729
_APCA_COEFF_G = 0.7151522
_APCA_COEFF_B = 0.0721750
_APCA_NORM_TXT = 0.57  # normal polarity: text exponent
_APCA_NORM_BG = 0.56  # normal polarity: background exponent
_APCA_REV_TXT = 0.62  # reverse polarity: text exponent
_APCA_REV_BG = 0.65  # reverse polarity: background exponent
_APCA_BLACK_THRESHOLD = 0.022
_APCA_BLACK_CLAMP = 1.414
_APCA_SCALE = 1.14
_APCA_LOW_THRESHOLD = 0.035991
_APCA_LOW_FACTOR = 27.7847239587675
_APCA_OFFSET = 0.027


def apca_luminance(value: str) -> float:
    """APCA luminance Y for a color (no polarity exponent applied).

    Internal helper of the canonical SAPC/APCA implementation. APCA uses
    the simple 2.4 exponent, not WCAG piecewise linearization.
    """
    r, g, b = hex_to_rgb(value)
    lin_r = math.pow(r / 255, 2.4)
    lin_g = math.pow(g / 255, 2.4)
    lin_b = math.pow(b / 255, 2.4)
    return _APCA_COEFF_R * lin_r + _APCA_COEFF_G * lin_g + _APCA_COEFF_B * lin_b


def apca_lc(foreground: str, background: str) -> float:
    """SAPC/APCA 0.0.98G-4g contrast (Lc) for text on a background.

    Returns a SIGNED, polarity-aware value: positive when the background
    is lighter than the foreground (dark text on light background), and
    negative when the foreground is lighter than the background (light
    text on dark background). Threshold comparisons MUST use ``abs(lc)``;
    diagnostics retain the signed value and polarity.
    """
    y_fg = apca_luminance(foreground)
    y_bg = apca_luminance(background)

    # Determine polarity: higher Y = lighter.
    if y_bg >= y_fg:  # normal polarity (dark text on light bg)
        exp_bg = _APCA_NORM_BG
        exp_txt = _APCA_NORM_TXT
        is_reverse = False
    else:  # reverse polarity (light text on dark bg)
        exp_bg = _APCA_REV_BG
        exp_txt = _APCA_REV_TXT
        is_reverse = True

    # Black soft-clamp: only colors below the threshold are clamped.
    def soft_clamp(y: float, exponent: float) -> float:
        if y < _APCA_BLACK_THRESHOLD:
            return math.pow(y + math.pow(_APCA_BLACK_THRESHOLD - y, _APCA_BLACK_CLAMP), exponent)
        return math.pow(y, exponent)

    y_bg_pow = soft_clamp(y_bg, exp_bg)
    y_fg_pow = soft_clamp(y_fg, exp_txt)

    # SAPC with the polarity-aware exponents.
    sapc = (y_bg_pow - y_fg_pow) * _APCA_SCALE

    # Low-contrast offset (hysteresis).
    if abs(sapc) >= _APCA_LOW_THRESHOLD:
        out = ((sapc + _APCA_OFFSET) if is_reverse else (sapc - _APCA_OFFSET)) * 100
    else:
        out = sapc * _APCA_LOW_FACTOR * 100

    return out
