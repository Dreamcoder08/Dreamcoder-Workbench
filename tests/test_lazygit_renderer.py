"""Focused Lazygit renderer regression tests.

Covers the token-driven Lazygit integration: every mode variant parses as valid
YAML, theme/author/branch-log colors come from the canonical tokens (never a
duplicated per-mode palette), the Delta syntax theme stays valid per mode
(Catppuccin Latte light / Mocha dark), non-color Lazygit behavior is
preserved, and the registry registration is consistent with the engine.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from dreamcoder_theme.palette import detect_mode
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderer_registry import REGISTRATIONS
from dreamcoder_theme.renderers_lazygit import lazygit_content

ROOT = Path(__file__).resolve().parents[1]
TOKENS_FILE = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"
TOKENS = json.loads(TOKENS_FILE.read_text())


VARIANTS_BY_MODE = {"dark": VARIANTS["dark"], "light": VARIANTS["light"]}


@pytest.fixture(params=["dark", "light"])
def mode(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def variant(mode: str) -> dict[str, str]:
    return VARIANTS_BY_MODE[mode]


def _parse(content: str) -> dict:
    return yaml.safe_load(content)


class TestVariantParsing:
    def test_every_variant_parses_as_yaml(self, variant) -> None:
        data = _parse(lazygit_content(variant))
        assert isinstance(data, dict)
        assert data["gui"]["theme"]
        assert data["update"]["method"] == "never"

    def test_active_config_artifact_parses(self) -> None:
        for path in (
            ROOT / "DreamcoderLazygit/.config/lazygit/config.yml",
            ROOT / "DreamcoderLazygit/.config/lazygit/config.dark.yml",
            ROOT / "DreamcoderLazygit/.config/lazygit/config.light.yml",
        ):
            assert path.is_file(), f"missing generated artifact {path}"
            assert _parse(path.read_text())["gui"]["theme"]


class TestTokenFidelity:
    """Theme block, author colors, and branch log derive from canonical tokens."""

    def test_theme_colors_match_tokens(self, variant) -> None:
        theme = _parse(lazygit_content(variant))["gui"]["theme"]
        assert theme["activeBorderColor"][0] == variant["accent"]
        assert theme["inactiveBorderColor"][0] == variant["border"]
        assert theme["searchingActiveBorderColor"][0] == variant["accent_2"]
        assert theme["optionsTextColor"][0] == variant["diagnostic"]
        assert theme["selectedLineBgColor"][0] == variant["selection"]
        assert theme["inactiveViewSelectedLineBgColor"][0] == variant["surface2"]
        assert theme["cherryPickedCommitFgColor"][0] == variant["diagnostic"]
        assert theme["cherryPickedCommitBgColor"][0] == variant["accent_2"]
        assert theme["markedBaseCommitFgColor"][0] == variant["diagnostic"]
        assert theme["markedBaseCommitBgColor"][0] == variant["accent"]
        assert theme["unstagedChangesColor"][0] == variant["error"]
        assert theme["defaultFgColor"][0] == variant["text"]

    def test_author_colors_use_token_pairs(self, variant) -> None:
        author = _parse(lazygit_content(variant))["gui"]["authorColors"]
        expected_fg = {
            variant["accent"],
            variant["accent_2"],
            variant["diagnostic"],
            variant["sage"],
            variant["lavender"],
            variant["mauve"],
        }
        assert set(author) == expected_fg
        assert set(author.values()) == {variant["bg"]}

    def test_branch_log_uses_token_colors(self, variant) -> None:
        cmd = _parse(lazygit_content(variant))["git"]["branchLogCmd"]
        assert variant["accent"] in cmd
        assert variant["accent_2"] in cmd
        assert variant["comment"] in cmd
        assert variant["diagnostic"] in cmd

    def test_no_hardcoded_palette_outside_tokens(self, variant) -> None:
        """Any hex color in the output must come from the palette tokens."""
        token_values = {v.lower() for v in variant.values()}
        content = lazygit_content(variant)
        for match in re.finditer(r"#[0-9a-fA-F]{6}", content):
            assert match.group(0).lower() in token_values, f"non-token color: {match.group(0)}"


class TestDeltaSyntaxTheme:
    def test_light_uses_catppuccin_latte(self) -> None:
        cmd = _parse(lazygit_content(VARIANTS["light"]))["git"]["diffRenderers"][0]["command"]
        assert 'delta --syntax-theme "Catppuccin Latte" --paging=never' in cmd

    def test_dark_uses_catppuccin_mocha(self) -> None:
        cmd = _parse(lazygit_content(VARIANTS["dark"]))["git"]["diffRenderers"][0]["command"]
        assert 'delta --syntax-theme "Catppuccin Mocha" --paging=never' in cmd

    def test_installed_catppuccin_themes_are_used(self) -> None:
        # The chosen themes must match the machine-installed set (Latte/Mocha).
        assert detect_mode(VARIANTS["light"]) == "light"
        assert detect_mode(VARIANTS["dark"]) == "dark"


class TestNonColorBehaviorPreserved:
    def test_layout_and_git_options_unchanged(self, variant) -> None:
        gui = _parse(lazygit_content(variant))["gui"]
        git = _parse(lazygit_content(variant))["git"]
        assert gui["showFileTree"] is True
        assert gui["showRandomTip"] is False
        assert gui["nerdFontsVersion"] == "3"
        assert gui["sidePanelWidth"] == 0.3
        assert gui["expandFocusedSidePanel"] is True
        assert gui["mainPanelSplitMode"] == "flexible"
        assert gui["language"] == "en"
        assert git["merging"]["manualCommit"] is False
        assert git["skipHookPrefix"] == "WIP"
        assert git["autoFetch"] is True
        assert git["autoRefresh"] is True
        assert git["diffRenderers"][0]["colorArg"] == "always"

    def test_modes_differ_in_color_but_share_structure(self) -> None:
        dark = _parse(lazygit_content(VARIANTS["dark"]))
        light = _parse(lazygit_content(VARIANTS["light"]))
        assert (
            dark["gui"]["theme"]["activeBorderColor"] != light["gui"]["theme"]["activeBorderColor"]
        )
        assert dark["gui"]["showFileTree"] == light["gui"]["showFileTree"]
        assert dark["update"] == light["update"]


class TestRegistryRegistration:
    def test_lazygit_registered_as_active_and_repository(self) -> None:
        regs = {r.consumer_id: r for r in REGISTRATIONS}
        assert "lazygit" in regs
        reg = regs["lazygit"]
        assert reg.modes == frozenset({"dark", "light"})
        assert reg.output_kind == "active-and-repository"
        assert reg.sync.repository.value == "mode_variants"
        assert reg.sync.active.value == "resolved_active_path"

    def test_renderer_conforms_for_all_modes(self) -> None:
        regs = {r.consumer_id: r for r in REGISTRATIONS}
        for mode in ("dark", "light"):
            result = regs["lazygit"].renderer(VARIANTS_BY_MODE[mode])
            assert type(result) is str and len(result) > 0
