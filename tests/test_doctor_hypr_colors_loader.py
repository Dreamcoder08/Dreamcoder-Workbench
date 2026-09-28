"""Doctor: where Hyprland loads dreamcoder-colors from.

ML4W upgrades rewrite hyprland.lua, so the loader lives in the Dreamcoder-owned
custom.lua. A legacy require injected into hyprland.lua is still accepted.
"""

from pathlib import Path

from dreamcoder_theme.doctor import _check_hypr_colors_loader

LOADER = 'require("dreamcoder-colors")\n'


def _hypr(tmp_path: Path) -> Path:
    hypr = tmp_path / "hypr"
    hypr.mkdir()
    (hypr / "hyprland.lua").write_text('require("colors")\nrequire("custom")\n')
    return hypr


def test_loader_in_custom_lua_is_ok(tmp_path: Path) -> None:
    hypr = _hypr(tmp_path)
    (hypr / "custom.lua").write_text(LOADER)

    check = _check_hypr_colors_loader(tmp_path)

    assert check.status == "ok"
    assert check.detail == str(hypr / "custom.lua")


def test_legacy_loader_in_hyprland_lua_is_still_ok(tmp_path: Path) -> None:
    hypr = _hypr(tmp_path)
    (hypr / "hyprland.lua").write_text('require("colors")\n' + LOADER)

    check = _check_hypr_colors_loader(tmp_path)

    assert check.status == "ok"
    assert check.detail == str(hypr / "hyprland.lua")


def test_missing_loader_warns_and_points_at_the_generator(tmp_path: Path) -> None:
    hypr = _hypr(tmp_path)
    (hypr / "custom.lua").write_text("-- keybindings only\n")

    check = _check_hypr_colors_loader(tmp_path)

    assert check.status == "warn"
    assert "generate-custom-lua.sh" in check.repair


def test_missing_hypr_dir_warns(tmp_path: Path) -> None:
    check = _check_hypr_colors_loader(tmp_path)

    assert check.status == "warn"
    check.to_dict()
