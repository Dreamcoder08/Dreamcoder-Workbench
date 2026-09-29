"""Legacy ``theme.render_profile`` tolerance after the Night profile removal.

Dreamcoder ships only Light and Dark. Settings files written by older
versions may still carry ``theme.render_profile`` (``standard``/``night``);
loading them must never crash, and the stale key is treated like any other
unknown setting: reported as a warning and preserved untouched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dreamcoder_theme import settings as settings_mod
from dreamcoder_theme import settings_store


@pytest.fixture
def settings_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate persisted settings and the mode cache under a temp home."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / ".cache"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / ".local" / "share"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("DREAMCODER_THEME_MODE", raising=False)
    return tmp_path


def _write_settings(settings_home: Path, data: dict) -> Path:
    path = settings_home / ".config" / "dreamcoder" / "settings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return path


def test_schema_no_longer_declares_render_profile() -> None:
    assert "theme.render_profile" not in settings_store.SETTINGS_SCHEMA
    assert not hasattr(settings_mod, "render_profile")


@pytest.mark.parametrize("legacy_value", ["standard", "night"])
def test_persisted_legacy_render_profile_loads_as_unknown_setting(
    settings_home: Path, legacy_value: str
) -> None:
    """A stale key validates (warning only) and is preserved byte-for-byte."""
    path = _write_settings(
        settings_home,
        {"terminal": {"default_mode": "dark"}, "theme": {"render_profile": legacy_value}},
    )
    before = path.read_bytes()

    report = settings_store.validate_settings()

    assert report["valid"] is True
    assert report["errors"] == []
    assert [w["key"] for w in report["warnings"]] == ["theme.render_profile"]
    assert settings_store.settings_get("terminal.default_mode") == "dark"
    assert settings_store.settings_get("theme.render_profile") == legacy_value
    assert path.read_bytes() == before


def test_legacy_render_profile_does_not_affect_theme_mode(
    settings_home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A persisted legacy ``night`` value never selects a mode."""
    _write_settings(settings_home, {"theme": {"render_profile": "night"}})
    assert settings_mod.theme_mode() == "dark"
    monkeypatch.setenv("DREAMCODER_THEME_MODE", "light")
    assert settings_mod.theme_mode() == "light"


def test_writing_another_setting_keeps_legacy_key(settings_home: Path) -> None:
    """Updating a known key never crashes on, or drops, the stale key."""
    _write_settings(settings_home, {"theme": {"render_profile": "night"}})
    settings_store.settings_set("terminal.default_mode", "light")
    assert settings_store.settings_get() == {
        "terminal": {"default_mode": "light"},
        "theme": {"render_profile": "night"},
    }


def test_unknown_settings_preserved_with_warnings(settings_home: Path) -> None:
    """Unknown settings produce warnings and remain preserved (forward compat)."""
    path = _write_settings(settings_home, {"future": {"option": 42}})
    report = settings_store.validate_settings()
    assert report["valid"] is True
    keys = [warning["key"] for warning in report["warnings"]]
    assert "future.option" in keys
    assert json.loads(path.read_text()) == {"future": {"option": 42}}
