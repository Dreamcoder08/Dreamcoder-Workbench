"""Dreamcoder colours for the vendored Gentle Shell Desktop herdr-app mods.

The ``gentle-*`` mods under ``DreamcoderHerdr/.config/herdr-app/mods`` are
copied from Gentle Shell (MIT). Every colour they draw comes from two hex
tables in their ``tokens.js`` (``TOKENS``/``LIGHT`` in gentle-chat,
``HEX``/``HEX_LIGHT`` in the shared copy) plus the theme the
``gentle-shell`` layout selects. This module derives both from the canonical
Dreamcoder palette so the mods follow ``tokens.json`` like every other app.
"""

from __future__ import annotations

import json
import re

from ._math import mix
from .palette import ansi

GENTLE_TOKEN_NAMES = (
    "canvas",
    "background",
    "chrome",
    "surface",
    "raised",
    "user",
    "selected",
    "hover",
    "line",
    "lineStrong",
    "text",
    "muted",
    "faint",
    "accent",
    "accentSoft",
    "ok",
    "warn",
    "err",
    "info",
    "onAccent",
    "btnLine",
)


def gentle_shell_tokens(palette: dict[str, str], mode: str) -> dict[str, str]:
    """Map one Dreamcoder variant onto the Gentle Shell Desktop token names."""
    dark = mode == "dark"
    bg = palette["bg"]
    accent = palette["accent"]
    # Light uses the canonical selection tint so every app marks rows alike.
    selected = mix(bg, accent, 0.18) if dark else palette["selection"]
    tokens = {
        "canvas": bg,
        "background": bg,
        "chrome": palette["bg_soft"],
        "surface": palette["surface2"] if dark else palette["surface0"],
        "raised": palette["surface3"] if dark else palette["surface1"],
        "user": mix(bg, accent, 0.12 if dark else 0.08),
        "selected": selected,
        "hover": selected if dark else palette["surface1"],
        "line": palette["surface3"] if dark else palette["surface2"],
        "lineStrong": palette["border"],
        "text": palette["text"],
        # Light UI secondary text uses subtle; Light muted is an editor tone.
        "muted": palette["muted"] if dark else palette["subtle"],
        # Dark border_ui is only 3.6:1 on the raised surfaces; subtle keeps AA.
        "faint": palette["subtle"] if dark else palette["border_ui"],
        "accent": accent,
        "accentSoft": palette["accent_2"],
        "ok": palette["success"],
        "warn": palette["warning"],
        "err": palette["error"],
        "info": palette["info"],
        "onAccent": palette["on_accent"],
        "btnLine": palette["text"] + ("17" if dark else "1f"),
    }
    return {name: value.upper() for name, value in tokens.items()}


def _theme_extras(tokens: dict[str, str], mode: str) -> dict[str, str]:
    """Roles the layout theme sets that have no token of their own."""
    dark = mode == "dark"
    extras = {
        "popover": tokens["raised"] if dark else tokens["surface"],
        "accent_foreground": tokens["onAccent"],
        "solid": tokens["accent"],
        "solid_foreground": tokens["onAccent"],
    }
    if not dark:
        extras["idle"] = tokens["muted"]
        extras["selection"] = tokens["accent"] + "33"
    return extras


def gentle_shell_theme_content(palette: dict[str, str], mode: str) -> str:
    """Render ``themes/dreamcoder-shell-<mode>.json`` for the gentle-shell layout."""
    t = gentle_shell_tokens(palette, mode)
    extras = _theme_extras(t, mode)
    colors = {
        "background": t["background"],
        "canvas": t["canvas"],
        "chrome": t["chrome"],
        "surface": t["surface"],
        "raised": t["raised"],
        "popover": extras["popover"],
        "selected": t["selected"],
        "hover": t["hover"],
        "border": t["line"],
        "input": t["lineStrong"],
        "foreground": t["text"],
        "muted": t["muted"],
        "dim": t["faint"],
        "accent": t["accent"],
        "accent_foreground": extras["accent_foreground"],
        "solid": extras["solid"],
        "solid_foreground": extras["solid_foreground"],
        "done": t["ok"],
        "blocked": t["warn"],
        "working": t["info"],
        "idle": t["muted"],
        "selection": t["accent"] + ("4D" if mode == "dark" else "33"),
    }
    slots = [color.upper() for color in ansi(palette)]
    lines = ["{"]
    lines.append(f'  "background": {json.dumps(palette["bg"].upper())},')
    lines.append(f'  "foreground": {json.dumps(palette["text"].upper())},')
    lines.append(f'  "selection": {json.dumps(palette["selection"].upper())},')
    lines.append(f'  "cursor": {json.dumps(palette["accent"].upper())},')
    lines.append('  "ansi": [')
    lines.append("    " + ", ".join(json.dumps(c) for c in slots[:8]) + ",")
    lines.append("    " + ", ".join(json.dumps(c) for c in slots[8:]))
    lines.append("  ],")
    lines.append('  "colors": {')
    lines.append(",\n".join(f"    {json.dumps(k)}: {json.dumps(v)}" for k, v in colors.items()))
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


# tokens.js tables: name -> (mode, whether it holds layout extras)
_TABLES = {
    "TOKENS": ("dark", False),
    "HEX": ("dark", False),
    "LIGHT": ("light", False),
    "HEX_LIGHT": ("light", False),
    "LAYOUT_COLORS": ("dark", True),
    "LIGHT_COLORS": ("light", True),
}
_TABLE_START = re.compile(r"^(?:export )?const ([A-Z_]+) = \{")
_ENTRY = re.compile(r'^(  [A-Za-z_]+: \[?")(#[0-9a-fA-F]{6,8})(")')


def gentle_tokens_js_content(source: str, dark: dict[str, str], light: dict[str, str]) -> str:
    """Rewrite the colour tables of a vendored gentle ``tokens.js``.

    Only hex values inside the known tables change; code, comments and
    layout stay byte-identical. An entry the mapping does not know raises,
    so an upstream token added later is noticed instead of staying pink.
    """
    values = {
        ("dark", False): gentle_shell_tokens(dark, "dark"),
        ("light", False): gentle_shell_tokens(light, "light"),
    }
    values[("dark", True)] = _theme_extras(values[("dark", False)], "dark")
    values[("light", True)] = _theme_extras(values[("light", False)], "light")

    seen: set[str] = set()
    table: tuple[str, bool] | None = None
    out: list[str] = []
    for line in source.splitlines(keepends=True):
        start = _TABLE_START.match(line)
        if start:
            table = _TABLES.get(start.group(1))
            if table:
                seen.add(table[0])
        elif line.startswith("};"):
            table = None
        elif table:
            entry = _ENTRY.match(line)
            if entry:
                name = entry.group(1).strip().split(":", 1)[0]
                mapping = values[table]
                if name not in mapping:
                    raise ValueError(f"gentle tokens.js: no Dreamcoder value for {name!r}")
                out.append(entry.group(1) + mapping[name] + line[entry.end(2) :])
                continue
        out.append(line)
    if seen != {"dark", "light"}:
        raise ValueError("gentle tokens.js: dark and light colour tables not found")
    return "".join(out)
