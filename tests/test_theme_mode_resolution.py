"""theme_mode() must follow the persisted active mode when no env override exists.

A bare ``dreamcoder sync`` (from a hook, a listener, or a shell that never
exported DREAMCODER_THEME_MODE) used to render Dreamcoder Dark while the system
was in Light, because the only fallback was the repo default.
"""

from __future__ import annotations

import pytest

from dreamcoder_theme.settings import theme_mode


@pytest.fixture
def cache_home(tmp_path, monkeypatch):
    monkeypatch.delenv("DREAMCODER_THEME_MODE", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    return tmp_path


def write_mode_cache(cache_home, body: str) -> None:
    target = cache_home / "dreamcoder" / "cursor-cli.env"
    target.parent.mkdir(parents=True)
    target.write_text(body)


def test_env_override_wins_over_persisted_mode(cache_home, monkeypatch):
    write_mode_cache(cache_home, 'export DREAMCODER_THEME_MODE="light"\n')
    monkeypatch.setenv("DREAMCODER_THEME_MODE", "dark")
    assert theme_mode() == "dark"


def test_persisted_mode_is_used_without_env(cache_home):
    write_mode_cache(
        cache_home,
        'export COLORFGBG="0;15"\nexport DREAMCODER_THEME_MODE="light"\n',
    )
    assert theme_mode() == "light"


def test_defaults_to_dark_without_env_or_cache(cache_home):
    assert theme_mode() == "dark"


def test_invalid_persisted_mode_falls_back_to_dark(cache_home):
    write_mode_cache(cache_home, 'export DREAMCODER_THEME_MODE="sepia"\n')
    assert theme_mode() == "dark"
