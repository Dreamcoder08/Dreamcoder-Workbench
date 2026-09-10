"""Regression tests for repository-only Herdr variant generation."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from dreamcoder_theme import sync
from dreamcoder_theme.herdr_contract import (
    HERDR_073_PROFILE,
    HERDR_080_PROFILE,
    HERDR_082_PROFILE,
)
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_herdr import (
    HerdrContractUnavailableError,
    HerdrModeError,
    herdr_content,
    herdr_token_mapping,
)

EXPECTED_CUSTOM_FIELDS = {
    "accent",
    "panel_bg",
    "surface0",
    "surface1",
    "surface_dim",
    "overlay0",
    "overlay1",
    "text",
    "subtext0",
    "mauve",
    "green",
    "yellow",
    "red",
    "blue",
    "teal",
    "peach",
}


@pytest.mark.parametrize("mode", ("dark", "light"))
def test_herdr_output_uses_exact_allow_list_and_canonical_tokens(mode: str) -> None:
    content = herdr_content(HERDR_073_PROFILE, mode, VARIANTS[mode])
    parsed = tomllib.loads(content)

    assert parsed["theme"]["name"] == "catppuccin"
    assert set(parsed["theme"]) == {"name", "custom"}
    assert set(parsed["theme"]["custom"]) == EXPECTED_CUSTOM_FIELDS
    for field, token in herdr_token_mapping():
        assert parsed["theme"]["custom"][field] == VARIANTS[mode][token]
    assert parsed["ui"] == {"accent": "#6FA0AF"}
    assert parsed["keys"] == {
        "prefix": "ctrl+a",
        "previous_agent": "prefix+alt+k",
        "next_agent": "prefix+alt+j",
        "focus_agent": "prefix+ctrl+1..9",
    }
    assert "window-title" not in content
    assert "tab-title" not in content
    assert content.endswith("\n") and not content.endswith("\n\n")
    assert "\r" not in content


@pytest.mark.parametrize("mode", ("dark", "light"))
def test_herdr_080_renders_pane_scrollbars_false_for_every_mode(mode: str) -> None:
    content = herdr_content(HERDR_080_PROFILE, mode, VARIANTS[mode])
    parsed = tomllib.loads(content)

    assert parsed["theme"]["name"] == "catppuccin"
    assert set(parsed["theme"]) == {"name", "custom"}
    assert set(parsed["theme"]["custom"]) == EXPECTED_CUSTOM_FIELDS
    for field, token in herdr_token_mapping():
        assert parsed["theme"]["custom"][field] == VARIANTS[mode][token]
    assert parsed["ui"] == {
        "accent": "#6FA0AF",
        "pane_scrollbars": False,
    }
    assert parsed["ui"]["pane_scrollbars"] is False
    assert parsed["keys"] == {
        "prefix": "ctrl+a",
        "previous_agent": "prefix+alt+k",
        "next_agent": "prefix+alt+j",
        "focus_agent": "prefix+ctrl+1..9",
    }
    assert "pane_scrollbars = false" in content
    assert content.endswith("\n") and not content.endswith("\n\n")


def test_herdr_080_light_renders_dreamcoder_light() -> None:
    content = herdr_content(HERDR_080_PROFILE, "light", VARIANTS["light"])
    parsed = tomllib.loads(content)

    assert parsed["theme"]["custom"]["panel_bg"] == VARIANTS["light"]["bg"] == "#f3eadc"
    assert parsed["theme"]["custom"]["text"] == VARIANTS["light"]["text"]
    assert parsed["theme"]["custom"]["surface1"] == VARIANTS["light"]["surface1"]
    assert parsed["ui"]["accent"] == "#6FA0AF"


@pytest.mark.parametrize("mode", ("dark", "light", "night"))
def test_herdr_082_uses_mode_aware_base_and_sidebar_tokens(mode: str) -> None:
    palette = VARIANTS["dark"] if mode == "night" else VARIANTS[mode]
    parsed = tomllib.loads(herdr_content(HERDR_082_PROFILE, mode, palette))

    expected_base = "catppuccin-latte" if mode == "light" else "catppuccin"
    assert parsed["theme"]["name"] == expected_base
    assert parsed["theme"]["custom"]["sidebar_bg"] == palette["bg"]
    assert parsed["theme"]["custom"]["active_row_bg"] == palette["surface0"]
    assert parsed["theme"]["custom"]["selection_bg"] == palette["selection"]


def test_herdr_080_variants_are_byte_stable_and_matching_in_structure() -> None:
    dark = herdr_content(HERDR_080_PROFILE, "dark", VARIANTS["dark"])
    light = herdr_content(HERDR_080_PROFILE, "light", VARIANTS["light"])

    assert dark == herdr_content(HERDR_080_PROFILE, "dark", VARIANTS["dark"])
    assert light == herdr_content(HERDR_080_PROFILE, "light", VARIANTS["light"])
    dark_toml, light_toml = tomllib.loads(dark), tomllib.loads(light)
    assert set(dark_toml["theme"]["custom"]) == set(light_toml["theme"]["custom"])
    assert dark_toml["ui"]["pane_scrollbars"] is False
    assert light_toml["ui"]["pane_scrollbars"] is False
    assert dark_toml["ui"]["accent"] == "#6FA0AF"
    assert light_toml["ui"]["accent"] == "#6FA0AF"
    assert dark_toml["keys"] == light_toml["keys"]
    assert dark != light


def test_herdr_variants_are_byte_stable_and_have_matching_structure() -> None:
    dark = herdr_content(HERDR_073_PROFILE, "dark", VARIANTS["dark"])
    light = herdr_content(HERDR_073_PROFILE, "light", VARIANTS["light"])

    assert dark == herdr_content(HERDR_073_PROFILE, "dark", VARIANTS["dark"])
    assert light == herdr_content(HERDR_073_PROFILE, "light", VARIANTS["light"])
    dark_toml, light_toml = tomllib.loads(dark), tomllib.loads(light)
    assert set(dark_toml["theme"]["custom"]) == set(light_toml["theme"]["custom"])
    assert dark_toml["ui"]["accent"] == "#6FA0AF"
    assert light_toml["ui"]["accent"] == "#6FA0AF"
    assert dark_toml["keys"] == light_toml["keys"]
    assert dark != light


@pytest.mark.parametrize("mode", ("dusk", "invalid"))
def test_herdr_rejects_non_static_modes(mode: str) -> None:
    with pytest.raises(HerdrModeError, match="only dark, light, and night"):
        herdr_content(HERDR_073_PROFILE, mode, VARIANTS["dark"])


def test_repository_sync_writes_only_versioned_variants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    selector = tmp_path / "user-herdr" / "config.toml"
    selector.parent.mkdir()
    selector.write_text("onboarding = false\n")
    monkeypatch.setattr(sync, "ROOT", tmp_path)

    changes = sync.sync_herdr_repo_variants({"dark": VARIANTS["dark"], "light": VARIANTS["light"]})
    base_073 = tmp_path / "DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3"
    base_080 = tmp_path / "DreamcoderHerdr/.config/herdr/dreamcoder/0.8.0"
    base_082 = tmp_path / "DreamcoderHerdr/.config/herdr/dreamcoder/0.8.2"

    assert changes == [True, True, True, True, True, True]
    assert (base_073 / "config.dark.toml").is_file()
    assert (base_073 / "config.light.toml").is_file()
    assert (base_080 / "config.dark.toml").is_file()
    assert (base_080 / "config.light.toml").is_file()
    assert (base_082 / "config.dark.toml").is_file()
    assert (base_082 / "config.light.toml").is_file()
    assert selector.read_text() == "onboarding = false\n"
    assert sync.sync_herdr_repo_variants(
        {"dark": VARIANTS["dark"], "light": VARIANTS["light"]}
    ) == [
        False,
        False,
        False,
        False,
        False,
        False,
    ]


def test_checked_in_repository_variants_match_the_renderer() -> None:
    repo = Path(__file__).parents[1]
    night = sync.prepare("dark", "standard").variants["night"]
    for profile in (HERDR_073_PROFILE, HERDR_080_PROFILE, HERDR_082_PROFILE):
        base = repo / "DreamcoderHerdr/.config/herdr/dreamcoder" / profile.evidence.version

        assert (base / "config.dark.toml").read_text() == herdr_content(
            profile, "dark", VARIANTS["dark"]
        )
        assert (base / "config.light.toml").read_text() == herdr_content(
            profile, "light", VARIANTS["light"]
        )
        assert (base / "config.night.toml").read_text() == herdr_content(profile, "night", night)


def test_unsupported_profile_produces_no_repository_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync, "ROOT", tmp_path)

    assert sync.sync_herdr_repo_variants(VARIANTS, profiles=()) == []
    assert not (tmp_path / "DreamcoderHerdr").exists()


def test_incomplete_profile_cannot_generate_output() -> None:
    incomplete = HERDR_073_PROFILE.__class__(
        evidence=HERDR_073_PROFILE.evidence.__class__(
            **{**HERDR_073_PROFILE.evidence.__dict__, "base_theme_name": ""}
        )
    )

    with pytest.raises(HerdrContractUnavailableError):
        herdr_content(incomplete, "dark", VARIANTS["dark"])
