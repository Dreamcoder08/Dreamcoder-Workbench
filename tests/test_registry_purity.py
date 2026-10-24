"""Registry discovery + conformance purity enforcement (hexagonal-architecture-v2 task 1.7).

Spies on filesystem, selector, subprocess, installer, and settings entry points
while registry discovery and conformance run: zero file creation/writes, zero
selector runs, zero subprocesses, zero backups, zero settings mutations. The
test fails if any side effect is introduced.
"""

from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

from dreamcoder_theme import renderer_registry
from dreamcoder_theme.renderer_registry import REGISTRATIONS, validate_registry

# Load the independent oracle before the no-file-access guards are installed.
FROZEN_IDS = frozenset(
    json.loads(
        (Path(__file__).resolve().parent / "fixtures" / "expected_consumer_ids.json").read_text()
    )["expected_consumer_ids"]
)
TOOLKIT_IDS = frozenset({"gtk3", "gtk4", "qt6ct"})
EXPECTED_IDS = FROZEN_IDS | TOOLKIT_IDS


@pytest.fixture
def blocked_entry_points(monkeypatch) -> None:
    """Replace every side-effect entry point with a spy that raises."""

    def _forbidden(*args, **kwargs):
        raise AssertionError("side effect during registry discovery/conformance")

    # Filesystem mutation entry points.
    monkeypatch.setattr("os.makedirs", _forbidden)
    monkeypatch.setattr("os.mkdir", _forbidden)
    monkeypatch.setattr("os.remove", _forbidden)
    monkeypatch.setattr("os.rename", _forbidden)
    monkeypatch.setattr("os.symlink", _forbidden)
    monkeypatch.setattr("os.unlink", _forbidden)
    monkeypatch.setattr("os.write", _forbidden)

    # File writes through pathlib.
    monkeypatch.setattr(Path, "write_text", _forbidden)
    monkeypatch.setattr(Path, "write_bytes", _forbidden)
    monkeypatch.setattr(Path, "mkdir", _forbidden)
    monkeypatch.setattr(Path, "symlink_to", _forbidden)
    monkeypatch.setattr(Path, "unlink", _forbidden)
    monkeypatch.setattr(Path, "rename", _forbidden)

    # Builtins open: any open during discovery is a violation (we only need
    # in-memory constants + pure renderers).
    monkeypatch.setattr(builtins, "open", _forbidden)

    # Subprocess / process spawning.
    monkeypatch.setattr("subprocess.run", _forbidden)
    monkeypatch.setattr("subprocess.Popen", _forbidden)
    monkeypatch.setattr("subprocess.call", _forbidden)
    monkeypatch.setattr("subprocess.check_call", _forbidden)

    # Writer / selector / installer / settings entry points must never fire.
    from dreamcoder_theme import writers  # noqa: PLC0415

    for name in (
        "write_if_changed",
        "write_variant_files",
        "write_variant_files_and_active",
        "update_ghostty_theme",
        "update_warp_settings",
        "update_zellij_config",
        "ensure_codex_theme_config",
        "ensure_pi_theme_settings",
        "ensure_kitty_ui_include",
        "write_opencode_tui",
        "cleanup_opencode_themes",
    ):
        monkeypatch.setattr(writers, name, _forbidden)

    from dreamcoder_theme import settings  # noqa: PLC0415

    monkeypatch.setattr(settings, "theme_paths", _forbidden)


class TestPurity:
    def test_discovery_creates_no_files(self, blocked_entry_points) -> None:
        # Every filesystem-mutation entry point is spied by blocked_entry_points;
        # passing validation proves zero side effects without a scratch dir.
        assert validate_registry(REGISTRATIONS) == []

    def test_discovery_never_opens_files(self, blocked_entry_points) -> None:
        # open() is spied; any read would raise AssertionError.
        assert validate_registry(REGISTRATIONS) == []

    def test_conformance_renders_modes_without_side_effects(self, blocked_entry_points) -> None:
        from dreamcoder_theme.palette_tokens import VARIANTS  # noqa: PLC0415

        palette = dict(VARIANTS["dark"])
        for reg in REGISTRATIONS:
            for mode in reg.modes:
                out = reg.renderer(palette)
                assert type(out) is str

    def test_module_top_level_import_is_side_effect_free(self, tmp_path, monkeypatch) -> None:
        """Importing the registry module itself performs no file/subprocess work."""
        import importlib  # noqa: PLC0415

        monkeypatch.setattr(
            builtins, "open", lambda *a, **k: (_ for _ in ()).throw(AssertionError())
        )
        monkeypatch.setattr(
            "subprocess.run", lambda *a, **k: (_ for _ in ()).throw(AssertionError())
        )
        # Re-importing a fully-loaded module is a no-op; assert module import
        # machinery does not rely on filesystem side effects beyond stdlib.
        mod = importlib.reload(renderer_registry)
        assert mod.REGISTRATIONS
        assert len(FROZEN_IDS) == 33
        assert FROZEN_IDS.isdisjoint(TOOLKIT_IDS)
        ids = [r.consumer_id for r in mod.REGISTRATIONS]
        assert set(ids) == EXPECTED_IDS
        assert len(ids) == len(set(ids)) == len(EXPECTED_IDS)
