"""Every coloured LS_COLORS entry must be readable in Dreamcoder Light and Dark.

Broken symlinks (``or``) and sticky directories (``st``) used colour pairs below
WCAG AA, which made them unreadable in the terminal listing.
"""

from __future__ import annotations

import re

import pytest

from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS as DEFAULT_VARIANTS
from dreamcoder_theme.renderers_extra_shell import ls_colors_content
from dreamcoder_theme.settings import theme_paths

AA = 4.5


def _luminance(hex_rgb: str) -> float:
    channels = [int(hex_rgb[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _truecolor(params: list[str], selector: str) -> str | None:
    for i in range(len(params) - 4):
        if params[i] == selector and params[i + 1] == "2":
            return "".join(f"{int(v):02x}" for v in params[i + 2 : i + 5])
    return None


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_ls_colors_entries_meet_aa(mode):
    palette = load_variants(DEFAULT_VARIANTS, theme_paths().tokens_file)[mode]
    snippet = ls_colors_content(palette)
    ls_colors = re.search(r"export LS_COLORS='([^']+)'", snippet).group(1)
    base_bg = palette["bg"].lstrip("#").lower()
    failures = []
    for entry in ls_colors.split(":"):
        key, _, value = entry.partition("=")
        params = value.split(";")
        fg = _truecolor(params, "38")
        if fg is None:
            continue
        ratio = _contrast(fg, _truecolor(params, "48") or base_bg)
        if ratio < AA:
            failures.append(f"{key}={ratio:.2f}")
    assert not failures, f"{mode}: entries below {AA}:1 -> {failures}"
