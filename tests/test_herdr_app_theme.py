"""herdr-app desktop themes are generated from the canonical tokens."""

from __future__ import annotations

import json
from pathlib import Path

from dreamcoder_theme.palette import ansi
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_herdr import herdr_app_theme_content

ROOT = Path(__file__).resolve().parent.parent
THEMES = ROOT / "DreamcoderHerdr/.config/herdr-app/themes"


def test_dark_theme_keeps_the_shipped_bytes() -> None:
    shipped = (THEMES / "dreamcoder-dark.json").read_text()
    assert herdr_app_theme_content(VARIANTS["dark"]) == shipped


def test_light_theme_maps_canonical_light_tokens() -> None:
    light = VARIANTS["light"]
    theme = json.loads(herdr_app_theme_content(light))

    assert theme["background"] == light["bg"].upper()
    assert theme["foreground"] == light["text"].upper()
    assert theme["selection"] == light["selection"].upper()
    assert theme["cursor"] == light["accent"].upper()
    assert theme["ansi"] == [color.upper() for color in ansi(light)]
    assert theme["colors"] == {
        "canvas": light["bg"].upper(),
        "chrome": light["bg"].upper(),
        "surface": light["surface0"].upper(),
        "raised": light["surface1"].upper(),
        "selected": light["surface0"].upper(),
        "selection": light["selection"].upper(),
        "foreground": light["text"].upper(),
        "muted": light["muted"].upper(),
        "dim": light["border_ui"].upper(),
        "accent": light["accent"].upper(),
        "blocked": light["error"].upper(),
        "done": light["success"].upper(),
        "working": light["warning"].upper(),
    }


def test_shipped_light_theme_matches_the_renderer() -> None:
    shipped = (THEMES / "dreamcoder-light.json").read_text()
    assert shipped == herdr_app_theme_content(VARIANTS["light"])
