"""Tests for the Orca theme integration (best-effort, outside the
consumer coverage contract)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_orca import (
    orca_data_path,
    orca_main_window_running,
    orca_terminal_theme,
    orca_theme_settings,
    sync_orca_theme,
)


def _sync(
    active: dict[str, str], mode: str, variants: dict[str, dict[str, str]] | None = None
) -> str:
    return sync_orca_theme(active, variants or VARIANTS, mode)


def test_orca_terminal_theme_dark_shape() -> None:
    theme = orca_terminal_theme(VARIANTS["dark"])
    assert theme["name"] == "Dreamcoder Dark"
    assert theme["background"] == VARIANTS["dark"]["bg"]
    assert theme["foreground"] == VARIANTS["dark"]["text"]
    for key in (
        "cursor",
        "cursorAccent",
        "selectionBackground",
        "selectionForeground",
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "brightBlack",
        "brightRed",
        "brightGreen",
        "brightYellow",
        "brightBlue",
        "brightMagenta",
        "brightCyan",
        "brightWhite",
    ):
        assert theme[key].startswith("#"), f"{key} must be a hex color, got {theme[key]!r}"


def test_orca_terminal_theme_light_differs_from_dark() -> None:
    dark = orca_terminal_theme(VARIANTS["dark"])
    light = orca_terminal_theme(VARIANTS["light"])
    assert light["name"] == "Dreamcoder Light"
    assert light["background"] != dark["background"]


def test_orca_data_path_uses_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    override = tmp_path / "custom" / "orca-data.json"
    monkeypatch.setenv("ORCA_DATA_PATH", str(override))
    assert orca_data_path() == override


def test_orca_main_window_running_detects_bare_orca_ide_cmdline(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    running = proc_root / "1234"
    running.mkdir(parents=True)
    (running / "cmdline").write_bytes(b"/opt/orca/orca-ide\x00")

    helper = proc_root / "5678"
    helper.mkdir(parents=True)
    (helper / "cmdline").write_bytes(b"/opt/orca/orca-ide\x00--type=renderer\x00")

    assert orca_main_window_running(proc_root) is True


def test_orca_main_window_not_running_when_only_helpers_present(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    helper = proc_root / "5678"
    helper.mkdir(parents=True)
    (helper / "cmdline").write_bytes(b"/opt/orca/orca-ide\x00--type=renderer\x00")

    assert orca_main_window_running(proc_root) is False


def test_orca_theme_settings_carry_both_variants_and_chrome_mode() -> None:
    settings = orca_theme_settings(VARIANTS["dark"], VARIANTS, "dark")
    names = [t["name"] for t in settings["terminalCustomThemes"]]
    assert names == ["Dreamcoder Dark", "Dreamcoder Light"]
    assert settings["terminalThemeDark"] == "Dreamcoder Dark"
    assert settings["terminalThemeLight"] == "Dreamcoder Light"
    assert settings["terminalUseSeparateLightTheme"] is True
    assert settings["theme"] == "dark"
    assert settings["terminalDividerColorDark"] == VARIANTS["dark"]["border_ui"]
    assert settings["terminalDividerColorLight"] == VARIANTS["light"]["border_ui"]


def test_orca_theme_settings_prefer_adaptive_active_palette() -> None:
    adaptive_dark = dict(VARIANTS["dark"], bg="#010203")
    settings = orca_theme_settings(adaptive_dark, VARIANTS, "dark")
    dark_entry = next(t for t in settings["terminalCustomThemes"] if t["name"] == "Dreamcoder Dark")
    light_entry = next(
        t for t in settings["terminalCustomThemes"] if t["name"] == "Dreamcoder Light"
    )
    assert dark_entry["background"] == "#010203"
    assert light_entry["background"] == VARIANTS["light"]["bg"]


def test_sync_orca_theme_skips_when_main_window_running(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(json.dumps({"settings": {}}))
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=True):
        status = _sync(VARIANTS["dark"], "dark")
    assert status == "skipped-running"
    assert json.loads(data_path.read_text()) == {"settings": {}}


def test_sync_orca_theme_skips_when_file_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "missing.json"))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        assert _sync(VARIANTS["dark"], "dark") == "skipped-missing"


def test_sync_orca_theme_skips_when_malformed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text("not json")
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        assert _sync(VARIANTS["dark"], "dark") == "skipped-malformed"


def test_sync_orca_theme_applies_and_is_idempotent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(
        json.dumps(
            {
                "settings": {
                    "terminalThemeDark": "Ghostty Default Style Dark",
                    "terminalCustomThemes": [{"name": "Unrelated", "background": "#111111"}],
                    "terminalFontSize": 14,
                }
            }
        )
    )
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        first = _sync(VARIANTS["dark"], "dark")
        second = _sync(VARIANTS["dark"], "dark")

    assert first == "applied"
    assert second == "unchanged"
    data = json.loads(data_path.read_text())
    settings = data["settings"]
    assert settings["terminalThemeDark"] == "Dreamcoder Dark"
    assert settings["terminalThemeLight"] == "Dreamcoder Light"
    assert settings["terminalUseSeparateLightTheme"] is True
    assert settings["theme"] == "dark"
    assert settings["terminalFontSize"] == 14, "unrelated settings must be preserved"
    names = [t["name"] for t in settings["terminalCustomThemes"]]
    assert names.count("Dreamcoder Dark") == 1
    assert "Unrelated" in names, "unrelated pre-existing themes must be preserved"


def test_sync_orca_theme_keeps_both_entries_on_mode_switch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(json.dumps({"settings": {}}))
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        _sync(VARIANTS["dark"], "dark")
        status = _sync(VARIANTS["light"], "light")

    assert status == "applied"
    settings = json.loads(data_path.read_text())["settings"]
    assert settings["theme"] == "light"
    assert settings["terminalThemeLight"] == "Dreamcoder Light"
    names = [t["name"] for t in settings["terminalCustomThemes"]]
    assert sorted(names) == ["Dreamcoder Dark", "Dreamcoder Light"]
    light_entry = next(
        t for t in settings["terminalCustomThemes"] if t["name"] == "Dreamcoder Light"
    )
    assert light_entry["background"] == VARIANTS["light"]["bg"]


def test_sync_orca_theme_repairs_dangling_theme_references(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(
        json.dumps(
            {
                "settings": {
                    "terminalThemeDark": "Dreamcoder Dark",
                    "terminalThemeLight": "Dreamcoder Light",
                    "terminalUseSeparateLightTheme": True,
                    "terminalCustomThemes": [],
                }
            }
        )
    )
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        status = _sync(VARIANTS["dark"], "dark")

    assert status == "applied"
    settings = json.loads(data_path.read_text())["settings"]
    names = [t["name"] for t in settings["terminalCustomThemes"]]
    assert sorted(names) == ["Dreamcoder Dark", "Dreamcoder Light"]


def test_sync_orca_theme_replaces_stale_dreamcoder_definitions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(
        json.dumps(
            {
                "settings": {
                    "terminalCustomThemes": [
                        {"name": "Dreamcoder Dark", "background": "#DEADBE"},
                        {"name": "Dreamcoder Light", "background": "#DEADBF"},
                    ]
                }
            }
        )
    )
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        assert _sync(VARIANTS["dark"], "dark") == "applied"

    settings = json.loads(data_path.read_text())["settings"]
    entries = {t["name"]: t for t in settings["terminalCustomThemes"]}
    assert entries["Dreamcoder Dark"]["background"] == VARIANTS["dark"]["bg"]
    assert entries["Dreamcoder Light"]["background"] == VARIANTS["light"]["bg"]
    assert len(entries) == 2
