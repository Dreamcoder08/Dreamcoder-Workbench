"""Night naming/selection tests (Phase 4, task 4.6).

Covers R5/R9: every Night registry entry resolves to a distinct ``*-night``
artifact name, the Ghostty/Zellij/Warp/Neovim/Pi selectors are profile-aware,
and standard-dark substitution is detected and forbidden.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dreamcoder_theme import sync
from dreamcoder_theme.renderers_extra_nvim import nvim_dispatcher_content
from dreamcoder_theme.writers import (
    update_ghostty_theme,
    update_warp_settings,
    update_zellij_config,
    write_variant_files,
)

# ---------------------------------------------------------------------------
# Every Night registry entry has a distinct *-night name (R5)
# ---------------------------------------------------------------------------


def test_every_registry_entry_declares_a_night_name() -> None:
    """Each VARIANT_REGISTRY entry must carry a ``night`` key (D = dark/light/night)."""
    for base, names, _builder, _active in sync.VARIANT_REGISTRY:
        assert "night" in names, f"registry entry {base} has no night name"


def test_night_names_never_equal_dark_names() -> None:
    """Standard-dark substitution is forbidden: night must not reuse the dark name."""
    for base, names, _builder, _active in sync.VARIANT_REGISTRY:
        assert names["night"] != names["dark"], f"night alias for {base} equals dark"
        assert names["night"] != names["light"], f"night alias for {base} equals light"


def test_night_names_carry_a_night_marker() -> None:
    """Every registry night name is visually distinct via -night/-Night or .night.

    Hyphen markers (``*-night``/``*-Night``) are the majority convention; the
    dotted marker (``config.night.yml``) follows the established Herdr
    ``config.night.toml`` naming for config files whose base name must stay
    ``config`` (Lazygit consumes ``config.yml``).
    """
    for base, names, _builder, _active in sync.VARIANT_REGISTRY:
        name = names["night"]
        assert re.search(r"-night\b|-Night\b|\.night\b", name), f"{name} lacks a night marker"


def test_registry_coverage_rows_use_the_same_night_names() -> None:
    """COVERAGE night_artifact rows match the registry names byte-for-byte."""
    registry_night = {
        (base / names["night"]).relative_to(sync.ROOT).as_posix()
        for base, names, _builder, _active in sync.VARIANT_REGISTRY
    }
    declared = {row.night_artifact for row in sync.COVERAGE if row.source == "registry"}
    assert declared == registry_night
    problems = sync.validate_coverage_declaration()
    assert problems == [], problems


def test_write_variant_files_writes_night_artifact(tmp_path: Path) -> None:
    """write_variant_files produces the night artifact from the night palette."""

    def builder(variant: dict[str, str]) -> str:
        return f"bg={variant['bg']}\n"

    base = tmp_path / "themes"
    names = {"dark": "x-dark.conf", "light": "x-light.conf", "night": "x-night.conf"}
    variants = {
        "dark": {"bg": "#000000"},
        "light": {"bg": "#ffffff"},
        "night": {"bg": "#0d1015"},
    }
    write_variant_files(base, names, builder, variants)
    assert (base / "x-night.conf").read_text() == "bg=#0d1015\n"


def test_write_variant_files_missing_night_fails_closed(tmp_path: Path) -> None:
    """A missing night variant aborts before any write (no silent fallback)."""

    def builder(variant: dict[str, str]) -> str:
        return f"bg={variant['bg']}\n"

    base = tmp_path / "themes"
    names = {"dark": "x-dark.conf", "night": "x-night.conf"}
    variants = {"dark": {"bg": "#000000"}}  # night missing
    with pytest.raises(ValueError, match="night"):
        write_variant_files(base, names, builder, variants)
    assert not (base / "x-dark.conf").exists()
    assert not (base / "x-night.conf").exists()


# ---------------------------------------------------------------------------
# Profile-aware selectors (design §6)
# ---------------------------------------------------------------------------


class TestGhosttySelector:
    def test_night_selects_dreamcoder_night(self, tmp_path: Path) -> None:
        path = tmp_path / "config"
        path.write_text("[theme]\n")
        assert update_ghostty_theme(path, "dark", "night") is True
        assert "theme = dreamcoder-night" in path.read_text()

    def test_night_wins_over_light(self, tmp_path: Path) -> None:
        path = tmp_path / "config"
        path.write_text("[theme]\n")
        assert update_ghostty_theme(path, "light", "night") is True
        assert "theme = dreamcoder-night" in path.read_text()
        assert "theme = dreamcoder\n" not in path.read_text()

    def test_standard_dark_keeps_legacy_name(self, tmp_path: Path) -> None:
        path = tmp_path / "config"
        path.write_text("[theme]\n")
        assert update_ghostty_theme(path, "dark") is True
        assert "theme = dreamcoder-dark" in path.read_text()

    def test_standard_light_keeps_legacy_name(self, tmp_path: Path) -> None:
        path = tmp_path / "config"
        path.write_text("[theme]\n")
        assert update_ghostty_theme(path, "light") is True
        assert "theme = dreamcoder" in path.read_text()

    def test_night_never_selects_standard_dark(self, tmp_path: Path) -> None:
        path = tmp_path / "config"
        path.write_text("theme = dreamcoder-dark\n")
        assert update_ghostty_theme(path, "dark", "night") is True
        content = path.read_text()
        assert "theme = dreamcoder-night" in content
        assert "theme = dreamcoder-dark" not in content


class TestZellijSelector:
    def test_night_selects_night_kdl(self, tmp_path: Path) -> None:
        path = tmp_path / "config.kdl"
        path.write_text("some_setting true\n")
        assert update_zellij_config(path, "dark", "night") is True
        assert 'theme "dreamcoder-night"' in path.read_text()

    def test_night_fails_closed_when_kdl_not_ready(self, tmp_path: Path) -> None:
        path = tmp_path / "config.kdl"
        path.write_text("some_setting true\n")
        with pytest.raises(ValueError, match="dreamcoder-night"):
            update_zellij_config(path, "dark", "night", kdl_ready=False)
        # No selector mutation happened.
        assert 'theme "dreamcoder-night"' not in path.read_text()

    def test_standard_mode_selector_unchanged(self, tmp_path: Path) -> None:
        path = tmp_path / "config.kdl"
        path.write_text("some_setting true\n")
        assert update_zellij_config(path, "light") is True
        assert 'theme "dreamcoder-light"' in path.read_text()


class TestWarpSelector:
    def test_night_keeps_dark_appearance(self, tmp_path: Path) -> None:
        path = tmp_path / "settings.toml"
        assert update_warp_settings(path, "dark", "night") is True
        content = path.read_text()
        assert "override_opacity = 76" in content
        assert "override_blur = 20" in content
        assert "override_blur_texture = true" in content

    def test_night_never_enters_light_branch(self, tmp_path: Path) -> None:
        """Even with a light base, night keeps dark appearance (conflict is caught upstream)."""
        path = tmp_path / "settings.toml"
        assert update_warp_settings(path, "light", "night") is True
        content = path.read_text()
        assert "override_opacity = 76" in content
        assert "override_opacity = 96" not in content

    def test_standard_light_keeps_light_appearance(self, tmp_path: Path) -> None:
        path = tmp_path / "settings.toml"
        assert update_warp_settings(path, "light") is True
        assert "override_opacity = 96" in path.read_text()


class TestNvimSelector:
    def test_dispatcher_resolves_profile_before_base_mode(self) -> None:
        content = nvim_dispatcher_content()
        profile_pos = content.index("DREAMCODER_THEME_PROFILE")
        mode_pos = content.index("DREAMCODER_THEME_MODE")
        assert profile_pos < mode_pos, "profile must be resolved before base mode"
        assert "dreamcoder-night.lua" in content
        assert 'profile == "night"' in content

    def test_background_alone_still_selects_standard_dark(self) -> None:
        content = nvim_dispatcher_content()
        # The dispatcher must never fall back to night when only the base mode
        # is known; background=dark resolves to dreamcoder-dark.lua.
        assert "dreamcoder-dark.lua" in content


class TestPiSelector:
    def test_pi_theme_script_is_profile_aware(self) -> None:
        script = (
            Path(__file__).resolve().parents[1] / "DreamcoderPi/.pi/agent/scripts/pi-theme.sh"
        ).read_text()
        assert "DREAMCODER_THEME_PROFILE" in script
        assert 'variant="night"' in script or 'variant="${profile}"' in script
        assert "dreamcoder-night.json" in script or "dreamcoder-$variant.json" in script

    def test_pi_theme_script_fails_closed_on_invalid_profile(self) -> None:
        script = (
            Path(__file__).resolve().parents[1] / "DreamcoderPi/.pi/agent/scripts/pi-theme.sh"
        ).read_text()
        assert "invalid render profile" in script


# ---------------------------------------------------------------------------
# Standard-dark-substitution detection (R5)
# ---------------------------------------------------------------------------


def test_apply_theme_script_has_no_standard_dark_night_leak() -> None:
    """The shell selector must not substitute standard dark while reporting night.

    The night branch of the Kanagawa bridge and the VARIANT-based artifact
    selection must differ from the standard dark values.
    """
    script = (Path(__file__).resolve().parents[1] / "scripts/apply-theme-mode.sh").read_text()
    # Night selectors are driven by VARIANT, never hardcoded to the dark name.
    assert 'VARIANT="${MODE}"' in script
    assert '[[ "${PROFILE}" == "night" ]] && VARIANT="night"' in script
    # The night Kanagawa palette is distinct from the standard dark palette.
    assert '@ukiyo-color-text "#c6c6c6"' in script
    assert '@ukiyo-color-text "#E6E6E6"' in script


def test_coverage_night_artifacts_all_distinct_from_dark() -> None:
    """Every declared Night artifact carries a night marker (no dark reuse).

    The ``opencode`` row is the documented stable-ID exception (design §5 row
    5): the active ``dreamcoder.json`` is overwritten with Night bytes and no
    ``dreamcoder-night.json`` sibling exists — its selection strategy carries
    the Night identity instead of the artifact name.
    """
    for row in sync.COVERAGE:
        artifact = row.night_artifact
        if row.consumer_id == "opencode" or artifact.startswith("active:"):
            assert "night" in row.selection_strategy.lower()
            continue
        assert re.search(r"-night\b|-Night\b|night", artifact), artifact
        assert "dark" not in artifact.split("/")[-1] or "night" in artifact
