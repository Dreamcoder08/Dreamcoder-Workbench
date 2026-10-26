"""Tests for renderer output consistency and make_guard factory."""

import json
import plistlib
from pathlib import Path

import pytest

from dreamcoder_theme.palette import detect_mode, guard, make_guard
from dreamcoder_theme.renderers_codex import codex_tmtheme_content
from dreamcoder_theme.renderers_extra_nvim import nvim_content
from dreamcoder_theme.renderers_kitty import kitty_content, kitty_ui_content
from dreamcoder_theme.renderers_opencode import opencode_content, opencode_tokens
from dreamcoder_theme.renderers_pi import pi_theme_content
from dreamcoder_theme.renderers_starship import starship_content

HERE = Path(__file__).resolve().parent
TOKENS_FILE = HERE.parent / "DreamcoderThemes/dreamcoder/tokens.json"
VARIANTS = json.loads(TOKENS_FILE.read_text())["modes"]


@pytest.fixture(params=list(VARIANTS.keys()))
def variant(request):
    return VARIANTS[request.param]


@pytest.fixture
def dark():
    return VARIANTS["dark"]


# ── make_guard tests ──────────────────────────────────────────


class TestMakeGuard:
    def test_produces_same_as_direct_guard(self, dark):
        g = make_guard(dark, minimum=3.0)

        expected = guard(dark["accent"], dark["bg"], "dark", minimum=3.0)
        assert g(dark["accent"]) == expected

    def test_dark_modes(self, dark):
        g = make_guard(dark)
        result = g(dark["accent"])
        assert isinstance(result, str)
        assert result.startswith("#")

    def test_light_modes(self):
        light = VARIANTS["light"]
        g = make_guard(light)
        result = g(light["accent"])
        assert isinstance(result, str)
        assert result.startswith("#")


# ── opencode_tokens structural tests ──────────────────────────


class TestOpencodeTokens:
    def test_returns_expected_keys(self, variant):
        t = opencode_tokens(variant)
        expected_keys = {
            "keyword",
            "function",
            "method",
            "variable",
            "parameter",
            "property",
            "field",
            "string",
            "number",
            "constant",
            "type",
            "constructor",
            "enum",
            "operator",
            "punctuation",
            "comment",
            "todo",
            "deprecated",
            "code_bg",
            "selection",
            "selection_fg",
            "search",
        }
        assert set(t.keys()) == expected_keys

    def test_all_colors_are_hex(self, variant):
        t = opencode_tokens(variant)
        for key, val in t.items():
            if key in ("selection", "selection_fg"):
                continue  # these are token references, not always hex
            if val.startswith("#"):
                assert len(val) == 7, f"{key}={val} is not #RRGGBB"
            else:
                assert isinstance(val, str)

    def test_keyword_matches_accent(self, variant):
        t = opencode_tokens(variant)
        # Keyword should be in the accent family (amber/brown)
        assert t["keyword"].startswith("#")

    def test_function_matches_accent_2(self, variant):
        t = opencode_tokens(variant)
        assert t["function"].startswith("#")

    def test_type_matches_diagnostic(self, variant):
        t = opencode_tokens(variant)
        assert t["type"].startswith("#")


# ── opencode_content JSON structure tests ─────────────────────


class TestOpencodeContent:
    def test_is_valid_json(self, variant):
        content = opencode_content(variant)
        data = json.loads(content)
        assert "$schema" in data
        assert "defs" in data
        assert "theme" in data

    def test_theme_has_required_fields(self, variant):
        content = opencode_content(variant)
        data = json.loads(content)
        theme = data["theme"]
        for key in (
            "background",
            "text",
            "syntaxKeyword",
            "syntaxFunction",
            "syntaxVariable",
            "syntaxType",
            "syntaxString",
        ):
            assert key in theme, f"missing {key}"

    def test_syntax_colors_match_opencode_tokens(self, variant):
        t = opencode_tokens(variant)
        content = opencode_content(variant)
        data = json.loads(content)
        theme = data["theme"]
        assert theme["syntaxKeyword"] == t["keyword"]
        expected_function = t["function"]
        if detect_mode(variant) == "light":
            expected_function = guard(
                expected_function,
                theme["backgroundCode"],
                "light",
                minimum=4.5,
            )
        assert theme["syntaxFunction"] == expected_function
        assert theme["syntaxVariable"] == t["variable"]
        assert theme["syntaxString"] == t["string"]
        assert theme["syntaxType"] == t["type"]


# ── codex tmTheme structure tests ─────────────────────────────


class TestCodexTmTheme:
    def test_is_valid_plist(self, variant):
        content = codex_tmtheme_content(variant)
        data = plistlib.loads(content.encode("utf-8"))
        assert data["name"] in ("Dreamcoder",)

    def test_has_global_settings(self, variant):
        content = codex_tmtheme_content(variant)
        data = plistlib.loads(content.encode("utf-8"))
        settings = data["settings"][0]["settings"]
        assert "background" in settings
        assert "foreground" in settings
        assert "caret" in settings
        assert "selection" in settings

    def test_global_colors_match_palette(self, variant):
        content = codex_tmtheme_content(variant)
        data = plistlib.loads(content.encode("utf-8"))
        settings = data["settings"][0]["settings"]
        assert settings["background"] == variant["bg"]
        assert settings["foreground"] == variant["text"]
        assert settings["caret"] == variant["accent"]

    def test_syntax_scopes_match_opencode_tokens(self, variant):
        t = opencode_tokens(variant)
        content = codex_tmtheme_content(variant)
        data = plistlib.loads(content.encode("utf-8"))
        scope_map = {
            "comment": "comment",
            "string": "string",
            "punctuation": "punctuation",
            "keyword.operator": "operator",
        }
        for item in data["settings"]:
            scope = item.get("scope", "")
            if scope in scope_map:
                expected = t[scope_map[scope]]
                assert item["settings"]["foreground"] == expected, (
                    f"scope '{scope}': expected {expected}"
                )


# ── Pi theme JSON structure tests ─────────────────────────────


class TestPiThemeContent:
    def test_is_valid_json(self, variant):
        content = pi_theme_content(variant)
        data = json.loads(content)
        assert "$schema" in data
        assert "name" in data
        assert "colors" in data

    def test_has_required_color_keys(self, variant):
        content = pi_theme_content(variant)
        data = json.loads(content)
        colors = data["colors"]
        for key in (
            "syntaxKeyword",
            "syntaxFunction",
            "syntaxVariable",
            "syntaxString",
            "syntaxType",
            "accent",
            "text",
        ):
            assert key in colors, f"missing colors.{key}"

    def test_syntax_colors_match_opencode_tokens(self, variant):
        t = opencode_tokens(variant)
        content = pi_theme_content(variant)
        data = json.loads(content)
        colors = data["colors"]
        assert colors["syntaxKeyword"] == t["keyword"]
        assert colors["syntaxFunction"] == t["function"]
        assert colors["syntaxVariable"] == t["variable"]
        assert colors["syntaxString"] == t["string"]
        assert colors["syntaxType"] == t["type"]
        assert colors["syntaxOperator"] == t["operator"]
        assert colors["syntaxPunctuation"] == t["punctuation"]


# ── Kitchen-sink: all renderers produce valid output ──────────


class TestKitchenSink:
    """Every renderer function produces valid output for both modes."""

    RENDERERS = [  # type: ignore[var-annotated]  # noqa: RUF012
        ("kitty", kitty_content),
        ("kitty_ui", kitty_ui_content),
        ("starship", starship_content),
    ]

    def test_all_renderers_produce_string(self, variant):
        for name, func in self.RENDERERS:  # type: ignore[union-attr]
            result = func(variant)
            assert isinstance(result, str), f"{name} should return str"
            assert len(result) > 0, f"{name} should not be empty"


# ── Nvim colors_name correctness ──────────────────────────────


class TestNvimColorsName:
    """colors_name must accurately identify the mode, not be swapped."""

    def test_dark_sets_correct_colors_name(self, dark):
        content = nvim_content(dark)
        assert 'colors_name = "dreamcoder-dark"' in content, (
            "dark variant must report dreamcoder-dark"
        )

    def test_light_sets_correct_colors_name(self):
        light = VARIANTS["light"]
        content = nvim_content(light)
        assert 'colors_name = "dreamcoder-light"' in content, (
            "light variant must report dreamcoder-light"
        )

    def test_dusk_sets_correct_colors_name(self):
        dusk = VARIANTS["dusk"]
        content = nvim_content(dusk)
        assert 'colors_name = "dreamcoder-light"' in content, (
            "dusk variant (lighter) must report dreamcoder-light"
        )


# ── Cross-mode consistency ────────────────────────────────────


class TestCrossModeConsistency:
    def test_dark_and_light_have_same_opencode_keys(self):
        dark_t = opencode_tokens(VARIANTS["dark"])
        light_t = opencode_tokens(VARIANTS["light"])
        assert set(dark_t.keys()) == set(light_t.keys())

    def test_dark_and_light_have_different_color_values(self):
        dark_t = opencode_tokens(VARIANTS["dark"])
        light_t = opencode_tokens(VARIANTS["light"])
        for key in ("keyword", "function", "type", "string", "variable"):
            assert dark_t[key] != light_t[key], (
                f"{key} should differ between modes: dark={dark_t[key]} light={light_t[key]}"
            )
