"""Tests for the Orca terminal theme integration (best-effort, outside the
33-consumer coverage contract)."""

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
    sync_orca_theme,
)


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


def test_sync_orca_theme_skips_when_main_window_running(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(json.dumps({"settings": {}}))
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=True):
        status = sync_orca_theme(VARIANTS["dark"])
    assert status == "skipped-running"
    assert json.loads(data_path.read_text()) == {"settings": {}}


def test_sync_orca_theme_skips_when_file_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "missing.json"))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        assert sync_orca_theme(VARIANTS["dark"]) == "skipped-missing"


def test_sync_orca_theme_skips_when_malformed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text("not json")
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        assert sync_orca_theme(VARIANTS["dark"]) == "skipped-malformed"


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
                }
            }
        )
    )
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        first = sync_orca_theme(VARIANTS["dark"])
        second = sync_orca_theme(VARIANTS["dark"])

    assert first == "applied"
    assert second == "unchanged"
    data = json.loads(data_path.read_text())
    settings = data["settings"]
    assert settings["terminalThemeDark"] == "Dreamcoder Dark"
    names = [t["name"] for t in settings["terminalCustomThemes"]]
    assert names.count("Dreamcoder Dark") == 1
    assert "Unrelated" in names, "unrelated pre-existing themes must be preserved"


def test_sync_orca_theme_replaces_prior_dreamcoder_entry_on_mode_switch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(json.dumps({"settings": {}}))
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False):
        sync_orca_theme(VARIANTS["dark"])
        status = sync_orca_theme(VARIANTS["light"])

    assert status == "applied"
    settings = json.loads(data_path.read_text())["settings"]
    assert settings["terminalThemeLight"] == "Dreamcoder Light"
    names = [t["name"] for t in settings["terminalCustomThemes"]]
    assert sorted(names) == ["Dreamcoder Dark", "Dreamcoder Light"]
