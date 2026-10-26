"""Agent hex compatibility for OpenCode 2.1.4; no live configuration access.

Known managed IDs cannot distinguish a manually chosen canonical accent hex
from a previous sync result. Only those IDs accept that ambiguity; every other
agent's explicit hex remains custom, even when identical to a canonical color.
"""

from __future__ import annotations

import json
from dataclasses import fields, replace
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from dreamcoder_theme import sync
from dreamcoder_theme.opencode_colors import update_opencode_agent_colors
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_opencode import opencode_content
from dreamcoder_theme.settings import ThemePaths


@pytest.fixture
def config_path():
    with TemporaryDirectory(prefix="dreamcoder-agent-colors-") as directory:
        yield Path(directory) / "opencode.json"


def update(path, mode="dark"):
    return update_opencode_agent_colors(path, VARIANTS[mode], VARIANTS)


@pytest.mark.parametrize(
    "agent,role",
    [
        ("gentle-orchestrator", "primary"),
        ("dangerous-gentleman", "accent"),
    ],
)
def test_managed_primary_follows_repeated_mode_changes(config_path, agent, role):
    config_path.write_text(json.dumps({"agent": {agent: {"color": role}}}))
    for mode in ("dark", "light", "dusk", "dark"):
        assert update(config_path, mode) is True
        assert json.loads(config_path.read_text()) == {
            "agent": {agent: {"color": VARIANTS[mode]["accent"]}}
        }
        assert update(config_path, mode) is False


@pytest.mark.parametrize(
    "role",
    [
        "primary",
        "secondary",
        "accent",
        "error",
        "warning",
        "success",
        "info",
        "textMuted",
        "textSubtle",
        "textPlaceholder",
        "borderFocus",
        "syntaxFunction",
    ],
)
def test_explicit_symbolic_roles_match_transparent_renderer(config_path, role):
    config_path.write_text(json.dumps({"agent": {"other": {"color": role}}}))
    assert update(config_path) is True
    expected = json.loads(opencode_content(VARIANTS["dark"], True))["theme"][role]
    assert json.loads(config_path.read_text())["agent"]["other"]["color"] == expected


@pytest.mark.parametrize("value", ["unknown", "#123456", "#abc", "none", 42, None])
def test_unknown_custom_or_noncolor_values_are_unchanged(config_path, value):
    original = json.dumps({"agent": {"gentle-orchestrator": {"color": value}}})
    config_path.write_text(original)
    assert update(config_path) is False
    assert config_path.read_text() == original


@pytest.mark.parametrize("mode", list(VARIANTS))
def test_other_agents_canonical_hex_is_always_custom(config_path, mode):
    original = json.dumps({"agent": {"other": {"color": VARIANTS[mode]["accent"]}}})
    config_path.write_text(original)
    assert update(config_path, "light" if mode == "dark" else "dark") is False
    assert config_path.read_text() == original


def test_known_ids_canonical_hex_has_documented_managed_ambiguity(config_path):
    # A manual hex equal to the established primary/accent role is intentionally
    # indistinguishable from managed output, but unrelated token hex is not.
    config_path.write_text(
        json.dumps(
            {
                "agent": {
                    "gentle-orchestrator": {"color": VARIANTS["dark"]["accent"]},
                    "dangerous-gentleman": {"color": VARIANTS["dark"]["error"]},
                }
            }
        )
    )
    assert update(config_path, "light") is True
    assert json.loads(config_path.read_text())["agent"] == {
        "gentle-orchestrator": {"color": VARIANTS["light"]["accent"]},
        "dangerous-gentleman": {"color": VARIANTS["dark"]["error"]},
    }


@pytest.mark.parametrize(
    "original",
    [
        "{",
        "[]",
        "null",
        '{"agent": []}',
        '{"agent": null}',
        '{"agent": {"bad": null, "good": {"color": "primary"}}}',
        '{"agent": {"bad": "primary"}}',
        '{"agent": {}, "agent": {"good": {"color": "primary"}}}',
    ],
)
def test_malformed_or_wrong_shape_is_unchanged(config_path, original):
    config_path.write_text(original)
    assert update(config_path) is False
    assert config_path.read_text() == original


def test_missing_file_is_not_created(config_path):
    assert update(config_path) is False
    assert not config_path.exists()


@pytest.mark.parametrize("original", ["{}", '{"agent": {"no-color": {"model": "test"}}}'])
def test_no_agent_color_is_invented(config_path, original):
    config_path.write_text(original)
    assert update(config_path) is False
    assert config_path.read_text() == original


def test_preserves_unrelated_fields_and_unique_value_formatting(config_path):
    original = (
        '{\n "model": "keep", "permission": {"edit": "ask"},\n'
        ' "agent": {"gentle-orchestrator": {"color" : "primary",'
        ' "prompt": "color: primary", "model": "other", "tools": {}}}\n}\n'
    )
    config_path.write_text(original)
    assert update(config_path) is True
    assert config_path.read_text() == original.replace(
        '"primary"', '"' + VARIANTS["dark"]["accent"] + '"'
    )


def test_ambiguous_text_patch_preserves_semantics(config_path):
    data = {
        "color": "primary",
        "agent": {
            "one": {"color": "primary"},
            "two": {"color": "primary"},
            "no-color": {"prompt": '"color": "primary"'},
        },
    }
    config_path.write_text(json.dumps(data))
    assert update(config_path) is True
    for agent in ("one", "two"):
        data["agent"][agent]["color"] = VARIANTS["dark"]["accent"]
    assert json.loads(config_path.read_text()) == data


def test_public_sync_uses_tui_config_directory_and_preserves_theme(config_path, monkeypatch):
    # All output paths are isolated; neither home paths nor repository artifacts
    # can be reached by the public orchestrator in this fixture.
    root = config_path.parent
    optional = {field.name: None for field in fields(ThemePaths) if field.default is None}
    paths = ThemePaths(
        **{
            field.name: root / field.name
            for field in fields(ThemePaths)
            if field.name not in optional
        },
        **optional,
    )
    paths = replace(
        paths,
        opencode=root / "elsewhere/themes/dreamcoder.json",
        opencode_tui=root / "config/tui.json",
    )
    target = paths.opencode_tui.parent / "opencode.json"
    target.parent.mkdir()
    target.write_text('{"agent":{"gentle-orchestrator":{"color":"primary"}},"model":"keep"}')
    monkeypatch.setenv("DREAMCODER_CLEAN_OPENCODE_THEMES", "0")
    for mode in ("dark", "light", "dusk"):
        # Public modes stay dark/light; also exercise the legacy dusk palette
        # as active input without adding a new public mode to the orchestrator.
        base = "dark" if mode == "dark" else "light"
        result = sync.sync_active_targets(paths, VARIANTS[mode], base, VARIANTS)
        assert result["opencode_agent_colors"] is True
        assert json.loads(target.read_text()) == {
            "agent": {"gentle-orchestrator": {"color": VARIANTS[mode]["accent"]}},
            "model": "keep",
        }
        assert paths.opencode.read_text() == opencode_content(VARIANTS[mode], True)
        assert json.loads(paths.opencode_tui.read_text())["theme"] == "dreamcoder"
        assert not (paths.opencode.parent / "opencode.json").exists()
