"""Tests for the sync orchestrator module."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from dreamcoder_theme import sync
from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS as V
from dreamcoder_theme.settings import ThemePaths

ROOT = Path(__file__).resolve().parents[1]


def _canonical_guardrails() -> dict[str, float]:
    tokens_file = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"
    tokens = json.loads(tokens_file.read_text())
    return {k: v for k, v in tokens["guardrails"].items() if isinstance(v, (int, float))}


_CONTENT_FUNCS = [
    "kitty_content",
    "kitty_ui_content",
    "ghostty_content",
    "warp_content",
    "opencode_content",
    "codex_tmtheme_content",
    "pi_theme_content",
    "starship_content",
    "tmux_content",
    "lazygit_content",
    "nvim_dispatcher_content",
    "zsh_syntax_content",
    "ls_colors_content",
    "bat_content",
    "delta_content",
    "fzf_content",
    "btop_content",
    "dunst_content",
    "firefox_content",
    "obsidian_content",
    "cava_content",
    "hypr_content",
    "hypr_colors_lua_content",
    "hypr_colors_conf_content",
    "waybar_content",
    "waybar_matugen_content",
    "rofi_content",
    "rofi_matugen_content",
    "readme_content",
    "antigravity_content",
]


def _patch_renderers(return_value: str = "") -> list[mock._patch]:
    return [
        mock.patch(f"dreamcoder_theme.sync.{name}", return_value=return_value)
        for name in _CONTENT_FUNCS
    ]


_WRITER_DEFAULTS: dict[str, Any] = {
    "write_if_changed": False,
    "ensure_kitty_ui_include": False,
    "update_ghostty_theme": False,
    "update_warp_settings": False,
    "write_opencode_tui": False,
    "cleanup_opencode_themes": False,
    "ensure_codex_theme_config": False,
    "ensure_pi_theme_settings": False,
    "update_zellij_config": False,
    "write_variant_files": [False],
}


def _writer_patches(**overrides: Any) -> list[mock._patch]:
    vals = {**_WRITER_DEFAULTS, **overrides}
    return [
        mock.patch(f"dreamcoder_theme.sync.{name}", return_value=vals[name])
        for name in _WRITER_DEFAULTS
    ]


@pytest.fixture
def mock_paths() -> Any:
    return ThemePaths(
        kitty=Path("/fake/kitty/colors.conf"),
        kitty_config=Path("/fake/kitty/kitty.conf"),
        kitty_ui=Path("/fake/kitty/ui.conf"),
        ghostty=Path("/fake/ghostty/theme"),
        ghostty_config=Path("/fake/ghostty/config"),
        starship=Path("/fake/starship.toml"),
        tmux=Path("/fake/tmux/tmux.conf"),
        lazygit=Path("/fake/lazygit/config.yml"),
        zellij_config=Path("/fake/zellij/config.kdl"),
        warp=Path("/fake/warp/theme.yaml"),
        warp_settings=Path("/fake/warp/settings.toml"),
        opencode=Path("/fake/opencode/theme.json"),
        opencode_tui=Path("/fake/opencode/tui.json"),
        codex_theme=Path("/fake/codex/themes/Dreamcoder.tmTheme"),
        codex_config=Path("/fake/codex/config.toml"),
        pi_theme=Path("/fake/pi/themes/dreamcoder.json"),
        pi_settings=Path("/fake/pi/settings.json"),
        wallpaper=Path("/fake/wallpaper.jpg"),
        tokens_file=Path("/fake/tokens.json"),
        bat_theme_dir=Path("/fake/bat/themes"),
        nvim=Path("/fake/nvim/colors/dreamcoder.lua"),
        zsh_syntax=Path("/fake/themes/zsh-syntax.zsh"),
        ls_colors=Path("/fake/themes/ls-colors.sh"),
        bat=Path("/fake/themes/bat.sh"),
        delta=Path("/fake/themes/delta.gitconfig"),
        fzf=Path("/fake/themes/fzf.sh"),
        btop=Path("/fake/themes/btop.theme"),
        dunst=Path("/fake/themes/dunst.conf"),
        firefox=Path("/fake/themes/firefox.css"),
        obsidian=Path("/fake/themes/obsidian.css"),
        cava=Path("/fake/themes/cava.config"),
        hyprland=Path("/fake/themes/hyprland.conf"),
        hypr_colors_lua=Path("/fake/hypr/colors.lua"),
        hypr_colors_conf=Path("/fake/hypr/colors.conf"),
        waybar=Path("/fake/themes/waybar.css"),
        waybar_matugen=Path("/fake/waybar/colors.css"),
        rofi=Path("/fake/themes/rofi.rasi"),
        rofi_matugen=Path("/fake/rofi/colors.rasi"),
    )


@pytest.fixture
def active() -> dict[str, str]:
    return dict(V["dark"])


@pytest.fixture
def variants() -> dict[str, dict[str, str]]:
    return {
        "dark": dict(V["dark"]),
        "light": dict(V["light"]),
    }


def test_sync_active_targets_returns_dict(mock_paths, active):
    patches = [*_writer_patches(), *_patch_renderers()]
    for p in patches:
        p.start()
    try:
        result = sync.sync_active_targets(mock_paths, active, "dark")
    finally:
        for p in patches:
            p.stop()
    assert isinstance(result, dict)
    assert result["kitty"] is False
    assert "hyprland" in result
    assert result["bat_theme"] is False


def test_sync_active_targets_detects_changes(mock_paths, active):
    def side_effect(path, content):
        return path.name in ("colors.conf", "starship.toml", "tmux.conf")

    patches = [
        mock.patch("dreamcoder_theme.sync.write_if_changed", side_effect=side_effect),
        *(
            mock.patch(f"dreamcoder_theme.sync.{name}", return_value=val)
            for name, val in _WRITER_DEFAULTS.items()
            if name != "write_if_changed"
        ),
        *_patch_renderers(),
    ]
    for p in patches:
        p.start()
    try:
        result = sync.sync_active_targets(mock_paths, active, "dark")
    finally:
        for p in patches:
            p.stop()
    assert result["kitty"] is True
    assert result["starship"] is True
    assert result["tmux"] is True
    assert result["ghostty"] is False


def test_sync_bat_theme_variants_delegates(mock_paths):
    v = {"dark": {"bg": "#111"}, "light": {"bg": "#fff"}}
    with mock.patch(
        "dreamcoder_theme.sync.write_variant_files", return_value=[True, False]
    ) as mock_wvf:
        result = sync.sync_bat_theme_variants(mock_paths, v)
    mock_wvf.assert_called_once()
    assert result == [True, False]


def test_print_summary_output(mock_paths, capsys):
    changed = {"kitty": True, "starship": False}
    sync.print_summary("dark", mock_paths, changed, [True, False])
    captured = capsys.readouterr()
    assert "Synced Dreamcoder dark identity" in captured.out
    assert "kitty=True" in captured.out
    assert "Repo variant/snippet changes: 1" in captured.out


def _main_patches(mock_paths, active, variants, **overrides):
    vals = dict(
        theme_paths=mock_paths,
        theme_mode="dark",
        load_variants=variants,
        adaptive_palette=active,
        adaptive_enabled=False,
        write_repo_enabled=True,
        valid_starship=True,
        load_guardrails=_canonical_guardrails(),
        batch_theme_variants=[False],
    )
    vals.update(overrides)
    result = []
    for name in (
        "theme_paths",
        "theme_mode",
        "load_variants",
        "adaptive_palette",
        "adaptive_enabled",
        "write_repo_enabled",
        "valid_starship",
        "load_guardrails",
    ):
        if name in vals:
            result.append(mock.patch(f"dreamcoder_theme.sync.{name}", return_value=vals[name]))
    result += [*_writer_patches(), *_patch_renderers()]
    return result


def test_main_happy_path(mock_paths, active, variants):
    patches = _main_patches(mock_paths, active, variants)
    for p in patches:
        p.start()
    try:
        sync.main([])
    finally:
        for p in patches:
            p.stop()


def test_main_fails_on_invalid_starship(mock_paths, active, variants):
    patches = _main_patches(mock_paths, active, variants, valid_starship=False)
    for p in patches:
        p.start()
    try:
        with pytest.raises(SystemExit) as exc:
            sync.main([])
    finally:
        for p in patches:
            p.stop()
    assert "Starship" in str(exc.value)


def test_main_gate_failure_blocks_all_writes(mock_paths, active, variants):
    """R4: a failed dual gate performs zero writes and exits non-zero.

    No writer, selector, variant, or repo writer may run when validation
    fails, and no settings mutation occurs (main() performs none — here the
    fail-closed contract is: non-zero exit, zero writes, prior state untouched
    by construction).
    """
    patches = [
        mock.patch("dreamcoder_theme.sync.theme_paths", return_value=mock_paths),
        mock.patch("dreamcoder_theme.sync.theme_mode", return_value="dark"),
        mock.patch("dreamcoder_theme.sync.load_variants", return_value=variants),
        mock.patch("dreamcoder_theme.sync.adaptive_palette", return_value=active),
        mock.patch("dreamcoder_theme.sync.adaptive_enabled", return_value=False),
        mock.patch("dreamcoder_theme.sync.write_repo_enabled", return_value=True),
        mock.patch("dreamcoder_theme.sync.load_guardrails", return_value=_canonical_guardrails()),
        mock.patch("dreamcoder_theme.sync.validate_palette", return_value=["forced gate failure"]),
    ]
    # Every write path must be untouched when the gate fails.
    for name in (
        "sync_active_targets",
        "sync_bat_theme_variants",
        "sync_repo_snippets",
        "valid_starship",
        "write_if_changed",
        "ensure_kitty_ui_include",
        "update_ghostty_theme",
        "update_warp_settings",
        "write_opencode_tui",
        "cleanup_opencode_themes",
        "ensure_codex_theme_config",
        "ensure_pi_theme_settings",
        "update_zellij_config",
        "write_variant_files",
    ):
        patches.append(
            mock.patch(
                f"dreamcoder_theme.sync.{name}",
                side_effect=RuntimeError(f"{name} must not run when the gate fails"),
            )
        )
    for p in patches:
        p.start()
    try:
        with pytest.raises(SystemExit) as exc:
            sync.main([])
    finally:
        for p in patches:
            p.stop()
    assert "Theme gate failed" in str(exc.value)
    assert "no writes performed" in str(exc.value)
    assert "forced gate failure" in str(exc.value)


def test_main_skips_sync_repo_when_disabled(mock_paths, active, variants):
    patches = _main_patches(mock_paths, active, variants, write_repo_enabled=False)
    patches.append(
        mock.patch(
            "dreamcoder_theme.sync.sync_repo_snippets",
            side_effect=RuntimeError("should not be called"),
        )
    )
    for p in patches:
        p.start()
    try:
        sync.main([])
    finally:
        for p in patches:
            p.stop()


def test_main_calls_sync_repo_when_enabled(mock_paths, active, variants):
    patches = _main_patches(mock_paths, active, variants)
    patches.append(mock.patch("dreamcoder_theme.sync.sync_repo_snippets", return_value=[True]))
    for p in patches:
        p.start()
    try:
        sync.main([])
    finally:
        for p in patches:
            p.stop()


def test_main_light_mode(mock_paths):
    active_light = dict(V["light"])
    v = {"dark": dict(V["dark"]), "light": active_light}
    patches = _main_patches(mock_paths, active_light, v, theme_mode="light")
    for p in patches:
        p.start()
    try:
        sync.main([])
    finally:
        for p in patches:
            p.stop()


def test_load_variants_fallback_when_missing(tmp_path):
    tokens_file = tmp_path / "nonexistent.json"
    result = load_variants(V, tokens_file)
    assert result == V
    assert "dark" in result


def test_load_variants_merges_tokens(tmp_path):
    tokens = {"modes": {"dark": {"bg": "#000001"}}}
    tokens_file = tmp_path / "tokens.json"
    tokens_file.write_text(__import__("json").dumps(tokens))

    # The sentinel differs from the default on purpose, so the override is
    # observable. load_variants warns by contract whenever a tokens-file
    # value overrides a default, so assert that warning rather than leak it
    # into every suite summary as unhandled noise.
    with pytest.warns(UserWarning, match="palette divergence"):
        result = load_variants(V, tokens_file)
    assert result["dark"]["bg"] == "#000001"
    assert result["light"]["bg"] == V["light"]["bg"]
    assert "prompt_bg" in result["dark"]


# ---------------------------------------------------------------------------
# VARIANT_REGISTRY structure tests (T3.1)
# ---------------------------------------------------------------------------


def test_variant_registry_has_minimum_entries() -> None:
    """Registry must have >=18 entries."""
    assert len(sync.VARIANT_REGISTRY) >= 18, f"Expected >=18, got {len(sync.VARIANT_REGISTRY)}"


def test_variant_registry_all_four_tuples() -> None:
    """Every registry entry must be a 4-tuple."""
    for i, entry in enumerate(sync.VARIANT_REGISTRY):
        assert isinstance(entry, tuple), f"Entry {i} is not a tuple"
        assert len(entry) == 4, f"Entry {i} has {len(entry)} elements, expected 4"


def test_variant_registry_content_fns_callable() -> None:
    """Every registry entry's builder must be callable."""
    for i, (_base, _names, builder, _active_path) in enumerate(sync.VARIANT_REGISTRY):
        assert callable(builder), f"Entry {i} builder is not callable: {builder}"


def test_variant_registry_no_wm_nvim_entries() -> None:
    """Registry must not contain hyprland, waybar, rofi, or nvim."""
    excluded = {"hypr", "waybar", "rofi", "nvim"}
    for i, (base, _names, _builder, _active_path) in enumerate(sync.VARIANT_REGISTRY):
        base_str = str(base).lower()
        found = excluded & set(base_str.split("/"))
        assert not found, f"Entry {i} base {base} contains excluded name: {found}"


# ---------------------------------------------------------------------------
# Write-order determinism test (T3.2)
# ---------------------------------------------------------------------------


def test_variant_registry_write_order_deterministic(variants, active) -> None:
    """Mock write_variant_files; assert call sequence matches registry order."""
    with (
        mock.patch("dreamcoder_theme.sync.write_variant_files", return_value=[]) as m_wvf,
        mock.patch("dreamcoder_theme.sync.write_if_changed", return_value=False),
    ):
        sync.sync_repo_snippets(variants, active)

    called_bases = [call[0][0] for call in m_wvf.call_args_list]
    registry_bases = [entry[0] for entry in sync.VARIANT_REGISTRY]
    reg_idx = 0
    for called_base in called_bases:
        if reg_idx < len(registry_bases) and called_base == registry_bases[reg_idx]:
            reg_idx += 1
    assert reg_idx == len(registry_bases), (
        f"Only {reg_idx}/{len(registry_bases)} registry entries called in order"
    )


# ---------------------------------------------------------------------------
# Symlink active-file corruption regression
# ---------------------------------------------------------------------------


def test_zellij_repository_dark_and_light_match_canonical_tokens(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variants, active
) -> None:
    """Repository Zellij variants must match the canonical dark/light renderings."""
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    monkeypatch.setattr(sync, "VARIANT_REGISTRY", [])

    sync.sync_repo_snippets(variants, active)

    zellij_dir = tmp_path / "DreamcoderZellij/.config/zellij"
    for mode in ("dark", "light"):
        path = zellij_dir / f"dreamcoder-{mode}.kdl"
        assert path.read_text() == sync.zellij_content(V[mode], f"dreamcoder-{mode}")


def test_kitty_ui_active_write_does_not_corrupt_symlinked_sibling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variants, active
) -> None:
    """An external mode selector can leave dreamcoder-ui.conf as a symlink to
    one of the -dark/-light siblings. Writing the active (dark) file
    through that symlink must never overwrite the sibling's own content."""
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    kitty_dir = tmp_path / "DreamcoderKitty/.config/kitty"
    # VARIANT_REGISTRY bakes absolute repo paths in at import time, so the
    # declarative loop would write the real checked-in active mirrors even
    # with ROOT redirected; empty it so this test only exercises the
    # explicit kitty_ui write under the temporary root.
    monkeypatch.setattr(sync, "VARIANT_REGISTRY", [])
    kitty_dir.mkdir(parents=True)

    light_path = kitty_dir / "dreamcoder-ui-light.conf"
    light_content = sync.kitty_ui_content(V["light"])
    light_path.write_text(light_content)
    active_path = kitty_dir / "dreamcoder-ui.conf"
    active_path.symlink_to("dreamcoder-ui-light.conf")

    sync.sync_repo_snippets(variants, active)

    assert not active_path.is_symlink(), "active file must become its own regular file"
    assert active_path.read_text().rstrip("\n") == sync.kitty_ui_content(V["dark"]).rstrip("\n")
    assert light_path.read_text() == light_content, (
        "writing the active (dark) file must not corrupt the light sibling "
        "it used to be symlinked to"
    )


# ---------------------------------------------------------------------------
# Systematic symlink-safety guard for every active_path repo write
# ---------------------------------------------------------------------------


def test_write_active_repo_file_unlinks_a_stale_symlink(tmp_path: Path) -> None:
    """The shared guard every VARIANT_REGISTRY active_path write goes
    through: a pre-existing symlink at the target must never let the write
    land on a sibling file instead of its own path."""
    sibling = tmp_path / "dreamcoder-light.json"
    sibling.write_text("light content\n")
    target = tmp_path / "dreamcoder.json"
    target.symlink_to("dreamcoder-light.json")

    changed = sync.write_active_repo_file(target, "dark content\n")

    assert changed is True
    assert not target.is_symlink()
    assert target.read_text() == "dark content\n"
    assert sibling.read_text() == "light content\n", (
        "writing the active file must not corrupt the sibling it used to be symlinked to"
    )


def test_write_active_repo_file_matches_write_if_changed_for_regular_files(
    tmp_path: Path,
) -> None:
    """No symlink involved: behavior is identical to write_if_changed."""
    target = tmp_path / "plain.json"
    assert sync.write_active_repo_file(target, "content\n") is True
    assert sync.write_active_repo_file(target, "content\n") is False
    assert sync.write_active_repo_file(target, "new content\n") is True
    assert target.read_text() == "new content\n"


def test_variant_registry_active_paths_use_the_symlink_safe_writer() -> None:
    """Every VARIANT_REGISTRY entry with a real active_path (pi_theme,
    codex_app, codex_theme, bat_theme as of this writing) must go through
    write_active_repo_file, not the raw write_if_changed a stale symlink
    at that path would silently write through. A source-level check
    instead of exercising sync_repo_snippets against real ROOT-relative
    paths, since VARIANT_REGISTRY bakes in absolute paths from the actual
    repository at import time and cannot be safely redirected to a
    tmp_path in-process."""
    source = inspect.getsource(sync.sync_repo_snippets)
    assert "write_active_repo_file(active_path" in source
    assert sum(1 for _, _, _, ap in sync.VARIANT_REGISTRY if ap is not None) >= 1
