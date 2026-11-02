"""Doctor: Waybar/Rofi colors files and Firefox theme discovery.

The sync writes the active mode straight into colors.css / colors.rasi when
they are regular files, so a regular file is healthy. Firefox stores profiles
under the XDG path (~/.config/mozilla/firefox) as well as the legacy
~/.mozilla/firefox, and the doctor must find the theme in either place.
"""

from pathlib import Path

from dreamcoder_theme.doctor import _check_colors_file, _check_firefox_theme


def test_regular_colors_file_written_by_sync_is_ok(tmp_path: Path) -> None:
    colors = tmp_path / "colors.css"
    colors.write_text("@define-color background #f3eadc;\n")

    check = _check_colors_file("waybar", colors, "colors-{mode}.css")

    assert check.status == "ok"
    assert check.name == "waybar colors"
    assert "written by sync" in check.detail


def test_colors_symlink_is_still_ok(tmp_path: Path) -> None:
    (tmp_path / "colors-light.rasi").write_text("* {}\n")
    colors = tmp_path / "colors.rasi"
    colors.symlink_to("colors-light.rasi")

    check = _check_colors_file("rofi", colors, "colors-{mode}.rasi")

    assert check.status == "ok"
    assert check.detail == f"{colors} -> colors-light.rasi"


def test_missing_colors_file_fails(tmp_path: Path) -> None:
    check = _check_colors_file("waybar", tmp_path / "colors.css", "colors-{mode}.css")

    assert check.status == "fail"
    assert check.detail.endswith("missing")


def test_dangling_colors_symlink_fails(tmp_path: Path) -> None:
    colors = tmp_path / "colors.css"
    colors.symlink_to("colors-light.css")

    check = _check_colors_file("waybar", colors, "colors-{mode}.css")

    assert check.status == "fail"


def _profile(root: Path, name: str) -> Path:
    chrome = root / name / "chrome"
    chrome.mkdir(parents=True)
    return chrome


def test_firefox_theme_found_in_xdg_profile(tmp_path: Path) -> None:
    chrome = _profile(tmp_path / ".config/mozilla/firefox", "abc.default-release")
    (chrome / "dreamcoder.css").write_text("/* theme */\n")

    check = _check_firefox_theme(tmp_path)

    assert check.status == "ok"
    assert check.detail == "1 file(s)"


def test_firefox_theme_found_in_legacy_profile(tmp_path: Path) -> None:
    chrome = _profile(tmp_path / ".mozilla/firefox", "abc.default")
    (chrome / "dreamcoder.css").write_text("/* theme */\n")

    assert _check_firefox_theme(tmp_path).status == "ok"


def test_firefox_theme_missing_warns_with_xdg_repair(tmp_path: Path) -> None:
    check = _check_firefox_theme(tmp_path)

    assert check.status == "warn"
    assert check.detail == "not found"
    assert ".config/mozilla/firefox" in check.repair
