"""Tests for the Orca theme integration (best-effort, outside the
consumer coverage contract)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_orca import (
    orca_data_path,
    orca_main_window_running,
    orca_state_db_path,
    orca_store,
    orca_terminal_theme,
    orca_theme_settings,
    sync_orca_theme,
)

_TERMINAL_KEYS = (
    "foreground",
    "background",
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
)


def _sync(
    active: dict[str, str], mode: str, variants: dict[str, dict[str, str]] | None = None
) -> str:
    return sync_orca_theme(active, variants or VARIANTS, mode)


def _not_running() -> Any:
    return mock.patch(
        "dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=False
    )


def _make_sqlite_profile(directory: Path, settings: dict[str, object] | None = None) -> Path:
    """Create a profile-state database shaped like Orca's own."""
    db_path = directory / "profile-state.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE profile_state_meta (
          key TEXT NOT NULL PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE TABLE profile_state_documents (
          domain TEXT NOT NULL PRIMARY KEY,
          payload TEXT NOT NULL,
          domain_version INTEGER NOT NULL,
          revision INTEGER NOT NULL,
          updated_at INTEGER NOT NULL,
          content_hash TEXT NOT NULL
        );
        """
    )
    payload = json.dumps(settings or {}, separators=(",", ":"))
    conn.execute(
        "INSERT INTO profile_state_documents VALUES ('settings', ?, 1, 1, 1000, ?)",
        (payload, hashlib.sha256(payload.encode()).hexdigest()),
    )
    other = json.dumps({"open": 1}, separators=(",", ":"))
    conn.execute(
        "INSERT INTO profile_state_documents VALUES ('ui', ?, 1, 37, 2000, ?)",
        (other, hashlib.sha256(other.encode()).hexdigest()),
    )
    conn.execute("INSERT INTO profile_state_meta VALUES ('profile_id', 'local-default')")
    conn.execute("INSERT INTO profile_state_meta VALUES ('revision', '37')")
    conn.commit()
    conn.close()
    (directory / "profile-state.db.authority").write_text("sqlite\n", encoding="utf-8")
    return db_path


def _read_sqlite(db_path: Path) -> tuple[dict[str, object], int, str, str]:
    conn = sqlite3.connect(db_path)
    try:
        payload, revision, content_hash = conn.execute(
            "SELECT payload, revision, content_hash FROM profile_state_documents"
            " WHERE domain = 'settings'"
        ).fetchone()
        meta = conn.execute(
            "SELECT value FROM profile_state_meta WHERE key = 'revision'"
        ).fetchone()[0]
        ui_revision = conn.execute(
            "SELECT revision FROM profile_state_documents WHERE domain = 'ui'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert ui_revision == 37, "unrelated domains must keep their revision"
    return json.loads(payload), revision, content_hash, meta


def test_orca_terminal_theme_uses_the_id_addressed_entry_shape() -> None:
    theme = orca_terminal_theme(VARIANTS["dark"], "dark")
    assert theme["id"] == "manual:dreamcoder-dark"
    assert theme["name"] == "Dreamcoder Dark"
    assert theme["source"] == "manual"
    assert theme["mode"] == "dark"
    assert isinstance(theme["importedAt"], str) and theme["importedAt"].endswith("Z")
    terminal = theme["terminal"]
    assert terminal["background"] == VARIANTS["dark"]["bg"]
    assert terminal["foreground"] == VARIANTS["dark"]["text"]
    for key in _TERMINAL_KEYS:
        assert terminal[key].startswith("#"), f"{key} must be a hex color, got {terminal[key]!r}"


def test_orca_terminal_theme_light_differs_from_dark() -> None:
    dark = orca_terminal_theme(VARIANTS["dark"], "dark")
    light = orca_terminal_theme(VARIANTS["light"], "light")
    assert light["id"] == "manual:dreamcoder-light"
    assert light["name"] == "Dreamcoder Light"
    assert light["mode"] == "light"
    assert light["terminal"]["background"] != dark["terminal"]["background"]


def test_orca_terminal_theme_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError):
        orca_terminal_theme(VARIANTS["dark"], "sepia")


def test_orca_paths_use_env_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = tmp_path / "custom" / "orca-data.json"
    db = tmp_path / "custom" / "profile-state.db"
    monkeypatch.setenv("ORCA_DATA_PATH", str(data))
    assert orca_data_path() == data
    assert orca_state_db_path() == db
    monkeypatch.setenv("ORCA_STATE_DB_PATH", str(tmp_path / "other.db"))
    assert orca_state_db_path() == tmp_path / "other.db"


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


def test_orca_main_window_running_detects_appimage_cmdline(tmp_path: Path) -> None:
    """The AppImage build runs its main process from the image path itself."""
    proc_root = tmp_path / "proc"
    running = proc_root / "1234"
    running.mkdir(parents=True)
    (running / "cmdline").write_bytes(b"/home/u/Downloads/orca-linux.AppImage\x00")

    daemon = proc_root / "5678"
    daemon.mkdir(parents=True)
    (daemon / "cmdline").write_bytes(
        b"/home/u/.cache/orca/node\x00--spawner-exec-path\x00/tmp/.mount_orca/orca-ide\x00"
    )

    assert orca_main_window_running(proc_root) is True


def test_orca_main_window_not_running_for_unrelated_appimage(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    other = proc_root / "1234"
    other.mkdir(parents=True)
    (other / "cmdline").write_bytes(b"/home/u/Apps/other.AppImage\x00")

    assert orca_main_window_running(proc_root) is False


def test_orca_theme_settings_select_by_custom_id_and_keep_both_variants() -> None:
    settings = orca_theme_settings(VARIANTS["dark"], VARIANTS, "dark")
    ids = [t["id"] for t in settings["terminalCustomThemes"]]
    assert ids == ["manual:dreamcoder-dark", "manual:dreamcoder-light"]
    assert settings["terminalThemeDark"] == "custom:manual:dreamcoder-dark"
    assert settings["terminalThemeLight"] == "custom:manual:dreamcoder-light"
    assert settings["terminalUseSeparateLightTheme"] is True
    assert settings["theme"] == "dark"
    assert settings["terminalDividerColorDark"] == VARIANTS["dark"]["border_ui"]
    assert settings["terminalDividerColorLight"] == VARIANTS["light"]["border_ui"]


def test_orca_theme_settings_prefer_adaptive_active_palette() -> None:
    adaptive_dark = dict(VARIANTS["dark"], bg="#010203")
    settings = orca_theme_settings(adaptive_dark, VARIANTS, "dark")
    dark_entry = next(t for t in settings["terminalCustomThemes"] if t["mode"] == "dark")
    light_entry = next(t for t in settings["terminalCustomThemes"] if t["mode"] == "light")
    assert dark_entry["terminal"]["background"] == "#010203"
    assert light_entry["terminal"]["background"] == VARIANTS["light"]["bg"]


def test_orca_theme_settings_preserve_previous_import_stamp() -> None:
    existing = [
        {
            "id": "manual:dreamcoder-dark",
            "name": "Dreamcoder Dark",
            "source": "manual",
            "mode": "dark",
            "terminal": {"background": "#000000", "foreground": "#ffffff", "black": "#000000"},
            "importedAt": "2026-01-02T03:04:05Z",
        }
    ]
    settings = orca_theme_settings(VARIANTS["dark"], VARIANTS, "dark", existing)
    dark_entry = next(t for t in settings["terminalCustomThemes"] if t["mode"] == "dark")
    assert dark_entry["importedAt"] == "2026-01-02T03:04:05Z"


def test_orca_store_prefers_sqlite_when_authority_says_so(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = _make_sqlite_profile(tmp_path)
    (tmp_path / "orca-data.json").write_text(json.dumps({"settings": {}}), encoding="utf-8")
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    assert orca_store() == ("sqlite", db_path)


def test_orca_store_falls_back_to_json_without_sqlite_authority(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(json.dumps({"settings": {}}), encoding="utf-8")
    (tmp_path / "profile-state.db").write_bytes(b"")
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    assert orca_store() == ("json", data_path)


def test_sync_orca_theme_skips_when_main_window_running(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = _make_sqlite_profile(tmp_path)
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    with mock.patch("dreamcoder_theme.renderers_orca.orca_main_window_running", return_value=True):
        status = _sync(VARIANTS["dark"], "dark")
    assert status == "skipped-running"
    _, revision, _, meta = _read_sqlite(db_path)
    assert (revision, meta) == (1, "37"), "a running window must never be written"


def test_sync_orca_theme_skips_when_profile_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "missing.json"))
    with _not_running():
        assert _sync(VARIANTS["dark"], "dark") == "skipped-missing"


def test_sync_orca_theme_skips_when_sqlite_settings_are_malformed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = _make_sqlite_profile(tmp_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE profile_state_documents SET payload = 'not json' WHERE domain = 'settings'"
    )
    conn.commit()
    conn.close()
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    with _not_running():
        assert _sync(VARIANTS["dark"], "dark") == "skipped-malformed"


def test_sync_orca_theme_applies_to_sqlite_with_a_consistent_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = _make_sqlite_profile(tmp_path, {"terminalFontSize": 14, "theme": "system"})
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    with _not_running():
        status = _sync(VARIANTS["dark"], "dark")

    assert status == "applied"
    settings, revision, content_hash, meta = _read_sqlite(db_path)
    assert revision == 38 and meta == "38", "the document row and profile revision move together"
    conn = sqlite3.connect(db_path)
    payload = conn.execute(
        "SELECT payload FROM profile_state_documents WHERE domain = 'settings'"
    ).fetchone()[0]
    conn.close()
    assert content_hash == hashlib.sha256(payload.encode()).hexdigest()
    assert settings["theme"] == "dark"
    assert settings["terminalThemeDark"] == "custom:manual:dreamcoder-dark"
    assert settings["terminalThemeLight"] == "custom:manual:dreamcoder-light"
    assert settings["terminalUseSeparateLightTheme"] is True
    assert settings["terminalFontSize"] == 14, "unrelated settings must be preserved"
    backups = list(tmp_path.glob("profile-state.db.dreamcoder-backup.*"))
    assert len(backups) == 1, "the previous database must be backed up before the write"


def test_sync_orca_theme_is_idempotent_on_sqlite(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = _make_sqlite_profile(tmp_path)
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    with _not_running():
        first = _sync(VARIANTS["dark"], "dark")
        second = _sync(VARIANTS["dark"], "dark")

    assert (first, second) == ("applied", "unchanged")
    _, revision, _, meta = _read_sqlite(db_path)
    assert (revision, meta) == (38, "38"), "a no-op run must not bump the revision again"


def test_sync_orca_theme_json_store_still_works(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_path = tmp_path / "orca-data.json"
    data_path.write_text(
        json.dumps(
            {
                "settings": {
                    "terminalThemeDark": "Ghostty Default Style Dark",
                    "terminalCustomThemes": [
                        {
                            "id": "warp:unrelated",
                            "name": "Unrelated",
                            "source": "warp",
                            "mode": "dark",
                            "terminal": {"background": "#111111"},
                        }
                    ],
                    "terminalFontSize": 14,
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ORCA_DATA_PATH", str(data_path))
    with _not_running():
        first = _sync(VARIANTS["dark"], "dark")
        second = _sync(VARIANTS["dark"], "dark")

    assert (first, second) == ("applied", "unchanged")
    settings = json.loads(data_path.read_text(encoding="utf-8"))["settings"]
    assert settings["terminalFontSize"] == 14
    ids = [t["id"] for t in settings["terminalCustomThemes"]]
    assert ids.count("manual:dreamcoder-dark") == 1
    assert "warp:unrelated" in ids, "unrelated pre-existing themes must be preserved"


def test_sync_orca_theme_keeps_both_entries_on_mode_switch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = _make_sqlite_profile(tmp_path)
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    with _not_running():
        _sync(VARIANTS["dark"], "dark")
        status = _sync(VARIANTS["light"], "light")

    assert status == "applied"
    settings, _, _, _ = _read_sqlite(db_path)
    assert settings["theme"] == "light"
    assert settings["terminalThemeLight"] == "custom:manual:dreamcoder-light"
    ids = [t["id"] for t in settings["terminalCustomThemes"]]
    assert sorted(ids) == ["manual:dreamcoder-dark", "manual:dreamcoder-light"]
    light_entry = next(t for t in settings["terminalCustomThemes"] if t["mode"] == "light")
    assert light_entry["terminal"]["background"] == VARIANTS["light"]["bg"]


def test_sync_orca_theme_repairs_the_broken_flat_shape(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The previous Dreamcoder version wrote name-only flat entries Orca drops."""
    db_path = _make_sqlite_profile(
        tmp_path,
        {
            "terminalThemeDark": "Dreamcoder Dark",
            "terminalThemeLight": "Dreamcoder Light",
            "terminalUseSeparateLightTheme": True,
            "terminalCustomThemes": [
                {"name": "Dreamcoder Dark", "background": "#DEADBE"},
                {"name": "Dreamcoder Light", "background": "#DEADBF"},
            ],
        },
    )
    monkeypatch.setenv("ORCA_DATA_PATH", str(tmp_path / "orca-data.json"))
    with _not_running():
        assert _sync(VARIANTS["dark"], "dark") == "applied"

    settings, _, _, _ = _read_sqlite(db_path)
    entries = settings["terminalCustomThemes"]
    assert [t["id"] for t in entries] == ["manual:dreamcoder-dark", "manual:dreamcoder-light"]
    assert entries[0]["terminal"]["background"] == VARIANTS["dark"]["bg"]
    assert len(entries) == 2, "the flat duplicates must be dropped, not kept"
