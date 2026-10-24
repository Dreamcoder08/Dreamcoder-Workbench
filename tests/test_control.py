"""Dual-agent transaction regression tests; desktop reload is always mocked."""

import json
from unittest import mock

import pytest
from test_cli_theme_activation import _run, theme_home  # noqa: F401

from dreamcoder_theme import cli_handlers, sync
from dreamcoder_theme.settings import theme_paths


@pytest.fixture
def agent_home(theme_home, monkeypatch):  # noqa: F811 - imported pytest fixture
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(theme_home / "pi"))
    monkeypatch.setenv("GENTLE_SHELL_HOME", str(theme_home / "gentle"))
    monkeypatch.setenv("DREAMCODER_ADAPTIVE", "0")
    return theme_home


@pytest.mark.parametrize("failure", ["reload", "write"])
def test_agent_paths_restore_exact_state_after_failed_activation(agent_home, capsys, failure):
    assert _run("light", capsys)[0] == 0
    paths = theme_paths()
    source = agent_home / "variant.json"
    source.write_text("untouched repository variant\n")
    snapshots = {}
    for theme, settings in (
        (paths.pi_theme, paths.pi_settings),
        (paths.gentle_shell_theme, paths.gentle_shell_settings),
    ):
        assert theme is not None and settings is not None
        # Replace the generated test fixture with a legacy link.
        theme.unlink()
        theme.symlink_to(source)
        settings.write_text('{"theme":"custom","packages":["keep"]}\n')
        for path in (theme, settings):
            snapshots[path] = cli_handlers._capture_path(path)
    if failure == "reload":
        rc, payload = _run("dark", capsys, reload_failure=True)
    else:
        writer = sync.ensure_pi_theme_settings

        def fail_gentle(path):
            if path == paths.gentle_shell_settings:
                raise OSError("injected Gentle Shell settings write failure")
            return writer(path)

        with mock.patch.object(sync, "ensure_pi_theme_settings", side_effect=fail_gentle):
            rc, payload = _run("dark", capsys)
    assert rc != 0
    assert payload["rollback_state"] == "restored"
    for path, state in snapshots.items():
        assert cli_handlers._capture_path(path) == state
    assert source.read_text() == "untouched repository variant\n"


def test_preparation_includes_gentle_shell_without_mutation(agent_home):
    paths = theme_paths()
    prepared = sync.prepare("dark")
    assert prepared.render_plan["gentle_shell_theme"] == prepared.render_plan["pi_theme"]
    assert paths.gentle_shell_theme in cli_handlers._mutable_paths(paths)
    assert paths.gentle_shell_settings in cli_handlers._mutable_paths(paths)
    assert paths.gentle_shell_theme is not None
    assert not paths.gentle_shell_theme.exists()
    theme = json.loads(prepared.render_plan["gentle_shell_theme"])
    assert theme["name"] == "dreamcoder"
