"""Wallpaper <-> UI contract: measurable limits a wallpaper must meet.

Pure functions over a list of 8-bit sRGB pixels (a downsample of the image) and
the limits in ``components.wallpaper.<mode>`` of tokens.json. Colour statistics
are measured in OKLab, so lightness, chroma and hue match how the palette is
authored. Readability composites the palette's translucent bar and panel over
the worst wallpaper pixels and checks WCAG contrast of the palette text.

No I/O: reading images is the caller's job (``scripts/check-wallpaper.py``).
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any, NamedTuple

from ._math import contrast, rgb_to_hex
from .color_space import rgb_to_oklab

Pixel = tuple[int, int, int]
Contract = Mapping[str, Any]

_RGBA = re.compile(r"^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)$")


class Finding(NamedTuple):
    """One violated rule: a stable ``WALLPAPER_*`` code and a readable message."""

    code: str
    message: str


def load_contract(tokens: Mapping[str, Any], mode: str) -> dict[str, Any]:
    """The wallpaper limits of one mode; ``KeyError`` for an unknown mode."""
    contract: dict[str, Any] = tokens["components"]["wallpaper"][mode]
    return contract


def _percentile(sorted_values: Sequence[float], fraction: float) -> float:
    return sorted_values[max(0, math.ceil(fraction * len(sorted_values)) - 1)]


def _std(values: Sequence[float]) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def _check_size(width: int, height: int, contract: Contract) -> Finding | None:
    rule = contract["size"]
    problems = []
    if width < rule["min_width"] or height < rule["min_height"]:
        problems.append(f"{width}x{height} is below {rule['min_width']}x{rule['min_height']}")
    aspect = rule["aspect"]
    wanted = aspect["width"] / aspect["height"]
    if abs(width / height / wanted - 1) > aspect["tolerance"]:
        problems.append(
            f"aspect {width / height:.3f} is not {aspect['width']}:{aspect['height']}"
            f" within {aspect['tolerance']:.0%}"
        )
    return Finding("WALLPAPER_SIZE", "; ".join(problems)) if problems else None


def _check_lightness(mean_l: float, contract: Contract) -> Finding | None:
    low, high = contract["lightness"]["min"], contract["lightness"]["max"]
    if low <= mean_l <= high:
        return None
    return Finding("WALLPAPER_LIGHTNESS", f"mean L {mean_l:.3f} is outside [{low}, {high}]")


def _check_chroma(chromas: Sequence[float], contract: Contract) -> Finding | None:
    rule = contract["chroma"]
    p95 = _percentile(sorted(chromas), 0.95)
    mean = sum(chromas) / len(chromas)
    problems = []
    if p95 > rule["p95_max"]:
        problems.append(f"p95 C {p95:.4f} exceeds {rule['p95_max']}")
    if mean > rule["mean_max"]:
        problems.append(f"mean C {mean:.4f} exceeds {rule['mean_max']}")
    return Finding("WALLPAPER_CHROMA", "; ".join(problems)) if problems else None


def _check_hue(mean_a: float, mean_b: float, contract: Contract) -> Finding | None:
    """Chroma-weighted circular mean hue is atan2 of the mean (a, b)."""
    rule = contract["hue"]
    if math.hypot(mean_a, mean_b) < rule["min_mean_chroma"]:
        return None
    hue = math.degrees(math.atan2(mean_b, mean_a)) % 360
    distance = abs((hue - rule["center"] + 180) % 360 - 180)
    if distance <= rule["tolerance"]:
        return None
    return Finding(
        "WALLPAPER_HUE",
        f"mean hue {hue:.0f} deg is {distance:.0f} deg from {rule['center']},"
        f" beyond +/-{rule['tolerance']}",
    )


def _band_pixels(grid_width: int, rows: int, contract: Contract) -> int:
    """Pixels in one bar band (the top or the bottom share of the rows)."""
    return max(1, round(rows * float(contract["safe_zone"]["fraction"]))) * grid_width


def _check_safe_zone(
    lightness: Sequence[float], grid_width: int, rows: int, contract: Contract
) -> Finding | None:
    rule = contract["safe_zone"]
    size = _band_pixels(grid_width, rows, contract)
    floor = rule.get("min_mean_lightness")
    problems = []
    for name, band in (("top", lightness[:size]), ("bottom", lightness[-size:])):
        spread = _std(band)
        if spread > rule["max_std_lightness"]:
            problems.append(f"{name} band std L {spread:.3f} exceeds {rule['max_std_lightness']}")
        mean = sum(band) / len(band)
        if floor is not None and mean < floor:
            problems.append(f"{name} band mean L {mean:.3f} is below {floor}")
    return Finding("WALLPAPER_SAFE_ZONE", "; ".join(problems)) if problems else None


def _worst_colour(
    pixels: Sequence[Pixel], lightness: Sequence[float], fraction: float, lightest: bool
) -> Pixel:
    """Mean colour of the worst ``fraction`` of pixels (darkest, or lightest)."""
    count = max(1, math.ceil(fraction * len(pixels)))
    order = sorted(range(len(pixels)), key=lambda i: lightness[i], reverse=lightest)[:count]
    red, green, blue = (round(sum(pixels[i][c] for i in order) / count) for c in range(3))
    return red, green, blue


def _composite(overlay: str, under: Pixel) -> str:
    """Hex of an ``rgba(r, g, b, a)`` overlay composited over an opaque pixel."""
    match = _RGBA.match(overlay)
    if match is None:
        raise ValueError(f"not an rgba(r, g, b, a) value: {overlay!r}")
    alpha = float(match[4])
    red, green, blue = (
        round(alpha * int(match[index]) + (1 - alpha) * under[index - 1]) for index in (1, 2, 3)
    )
    return rgb_to_hex((red, green, blue))


def _check_readability(
    pixels: Sequence[Pixel],
    lightness: Sequence[float],
    grid_width: int,
    rows: int,
    mode: str,
    contract: Contract,
    palette: Mapping[str, str],
) -> Finding | None:
    """Text on dark UI reads worst over light pixels, and the reverse for light UI."""
    rule = contract["readability"]
    lightest = mode == "dark"
    top = _band_pixels(grid_width, rows, contract)
    under_bar = _worst_colour(pixels[:top], lightness[:top], rule["worst_fraction"], lightest)
    under_panel = _worst_colour(pixels, lightness, rule["worst_fraction"], lightest)
    checks = (
        ("text over module_rgba", palette["text"], "module_rgba", under_bar, rule["text_min"]),
        ("muted over module_rgba", palette["muted"], "module_rgba", under_bar, rule["muted_min"]),
        (
            "text over panel_rgba",
            palette["text"],
            "panel_rgba",
            under_panel,
            rule["panel_text_min"],
        ),
    )
    worst = "lightest" if lightest else "darkest"
    problems = []
    for label, foreground, overlay, under, minimum in checks:
        ratio = contrast(foreground, _composite(palette[overlay], under))
        if ratio < minimum:
            problems.append(f"{label} on the {worst} pixels is {ratio:.2f}:1, below {minimum}:1")
    return Finding("WALLPAPER_READABILITY", "; ".join(problems)) if problems else None


def evaluate(
    pixels: Sequence[Pixel],
    *,
    grid_width: int,
    source_size: tuple[int, int],
    mode: str,
    contract: Contract,
    palette: Mapping[str, str],
) -> list[Finding]:
    """Check one wallpaper against the contract; at most one finding per rule.

    ``pixels`` is the row-major downsample (``grid_width`` columns); ``source_size``
    is the original (width, height). ``palette`` is the resolved mode palette.
    """
    rows, remainder = divmod(len(pixels), grid_width)
    if not pixels or remainder:
        raise ValueError(f"{len(pixels)} pixels do not fill rows of {grid_width}")
    labs: dict[Pixel, tuple[float, float, float]] = {}
    for pixel in pixels:
        if pixel not in labs:
            labs[pixel] = rgb_to_oklab(*pixel)
    measured = [labs[pixel] for pixel in pixels]
    lightness = [lab[0] for lab in measured]
    chromas = [math.hypot(lab[1], lab[2]) for lab in measured]
    count = len(pixels)
    mean_a = sum(lab[1] for lab in measured) / count
    mean_b = sum(lab[2] for lab in measured) / count

    findings = (
        _check_size(*source_size, contract),
        _check_lightness(sum(lightness) / count, contract),
        _check_chroma(chromas, contract),
        _check_hue(mean_a, mean_b, contract),
        _check_safe_zone(lightness, grid_width, rows, contract),
        _check_readability(pixels, lightness, grid_width, rows, mode, contract, palette),
    )
    return [finding for finding in findings if finding is not None]
