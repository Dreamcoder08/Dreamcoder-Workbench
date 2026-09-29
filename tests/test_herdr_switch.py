"""Focused tests for the version-aware Herdr selector switcher.

All tests use temporary directories and a fake ``herdr`` executable. No test
reads or writes the real user Herdr directory or contacts a live server.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from dreamcoder_theme import herdr_switch as switch_module
from dreamcoder_theme.herdr_switch import (
    SelectorResolutionError,
    choose_variant,
    resolve_selector,
    switch_herdr,
)

APPLIED = json.dumps(
    {"id": "cli:server:reload-config", "result": {"status": "applied", "type": "config_reload"}}
)
SERVER_NOT_RUNNING = json.dumps(
    {
        "id": "cli:server:reload-config",
        "error": {"code": "server_not_running", "message": "no herdr server"},
    }
)
RELOAD_FAILED = json.dumps(
    {"id": "cli:server:reload-config", "result": {"status": "failed", "type": "config_reload"}}
)


def _variant_root(
    tmp_path: Path,
    *,
    versions: tuple[str, ...] = ("0.7.3", "0.8.0", "0.8.2", "0.9.1"),
    modes: tuple[str, ...] = ("dark", "light"),
) -> Path:
    root = tmp_path / "variants"
    for version in versions:
        directory = root / version
        directory.mkdir(parents=True)
        for mode in modes:
            (directory / f"config.{mode}.toml").write_text(
                f'[theme]\nname = "catppuccin"\n\n[theme.custom]\naccent = "#{mode}"\n'
            )
    return root


class FakeRun:
    """Callable stand-in for ``subprocess.run`` with scripted outcomes."""

    def __init__(
        self,
        *,
        version: str = "herdr 0.9.2\n",
        config_check_returncode: int = 0,
        reload_stdout: str = APPLIED,
        reload_stderr: str = "",
        reload_returncode: int = 0,
        version_error: Exception | None = None,
        config_check_error: Exception | None = None,
        reload_error: Exception | None = None,
    ) -> None:
        self.version = version
        self.config_check_returncode = config_check_returncode
        self.reload_stdout = reload_stdout
        self.reload_stderr = reload_stderr
        self.reload_returncode = reload_returncode
        self.version_error = version_error
        self.config_check_error = config_check_error
        self.reload_error = reload_error
        self.calls: list[list[str]] = []

    def __call__(self, command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        if command[-1] == "--version":
            if self.version_error is not None:
                raise self.version_error
            return subprocess.CompletedProcess(command, 0, self.version, "")
        if command[1:] == ["config", "check"]:
            if self.config_check_error is not None:
                raise self.config_check_error
            output = "config: ok\n" if self.config_check_returncode == 0 else "config: error\n"
            return subprocess.CompletedProcess(command, self.config_check_returncode, output, "")
        if command[1:] == ["server", "reload-config"]:
            if self.reload_error is not None:
                raise self.reload_error
            return subprocess.CompletedProcess(
                command, self.reload_returncode, self.reload_stdout, self.reload_stderr
            )
        raise AssertionError(f"unexpected command: {command}")  # pragma: no cover


# ---------------------------------------------------------------------------
# Selector resolution
# ---------------------------------------------------------------------------


def test_resolve_selector_prefers_explicit_override(tmp_path: Path) -> None:
    env = {"HERDR_CONFIG_PATH": str(tmp_path / "override.toml"), "XDG_CONFIG_HOME": "/x"}
    assert resolve_selector(env) == tmp_path / "override.toml"


def test_resolve_selector_uses_xdg_then_home(tmp_path: Path) -> None:
    xdg = tmp_path / "xdg"
    assert resolve_selector({"XDG_CONFIG_HOME": str(xdg)}) == xdg / "herdr" / "config.toml"
    home = tmp_path / "home"
    assert resolve_selector({"HOME": str(home)}) == home / ".config" / "herdr" / "config.toml"


@pytest.mark.parametrize(
    "env",
    [
        {"HERDR_CONFIG_PATH": "", "HOME": "/home/u"},
        {"XDG_CONFIG_HOME": ""},
        {"HOME": ""},
        {},
    ],
)
def test_resolve_selector_rejects_empty_inputs(env: dict[str, str]) -> None:
    with pytest.raises(SelectorResolutionError):
        resolve_selector(env)


# ---------------------------------------------------------------------------
# Variant selection
# ---------------------------------------------------------------------------


def test_exact_profile_selects_its_own_variant(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    choice = choose_variant("herdr 0.8.0\n", "light", root)
    assert choice.path == root / "0.8.0/config.light.toml"
    assert choice.profile_version == "0.8.0"
    assert choice.fallback is False


def test_newer_unprofiled_version_falls_back_to_newest_variant(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    choice = choose_variant("herdr 0.9.2\n", "dark", root)
    assert choice.path == root / "0.9.1/config.dark.toml"
    assert choice.profile_version == "0.9.1"
    assert choice.fallback is True
    assert "no checked-in profile" in choice.reason


def test_installed_091_selects_its_own_variant(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    choice = choose_variant("herdr 0.9.1\n", "light", root)
    assert choice.path == root / "0.9.1/config.light.toml"
    assert choice.profile_version == "0.9.1"
    assert choice.fallback is False


def test_version_between_profiles_is_rejected(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    choice = choose_variant("herdr 0.9.0\n", "dark", root)
    assert choice.path is None
    assert "unsupported" in choice.reason


def test_older_unprofiled_version_is_rejected(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    choice = choose_variant("herdr 0.7.2\n", "dark", root)
    assert choice.path is None
    assert "unsupported" in choice.reason


@pytest.mark.parametrize("version", ["not-herdr\n", "", "herdr 0.9\n"])
def test_malformed_or_missing_version_is_rejected(tmp_path: Path, version: str) -> None:
    root = _variant_root(tmp_path)
    assert choose_variant(version, "dark", root).path is None
    assert choose_variant(None, "dark", root).path is None


# ---------------------------------------------------------------------------
# Switching preconditions
# ---------------------------------------------------------------------------


def test_missing_executable_fails_before_selector_touch(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    run = FakeRun(version_error=FileNotFoundError("herdr"))
    outcome = switch_herdr("dark", run=run, selector=selector, variant_root=root)
    assert outcome.status == "precondition-failed"
    assert not selector.exists()
    assert [call for call in run.calls] == [["herdr", "--version"]]


def test_missing_variant_fails_before_selector_touch(tmp_path: Path) -> None:
    root = _variant_root(tmp_path, modes=("dark",))
    selector = tmp_path / "config.toml"
    outcome = switch_herdr("light", run=FakeRun(), selector=selector, variant_root=root)
    assert outcome.status == "precondition-failed"
    assert not selector.exists()


def test_config_check_rejection_fails_before_selector_touch(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    run = FakeRun(config_check_returncode=1)
    outcome = switch_herdr("light", run=run, selector=selector, variant_root=root)
    assert outcome.status == "precondition-failed"
    assert "config check rejected" in outcome.message
    assert not selector.exists()
    assert ["herdr", "server", "reload-config"] not in run.calls


def test_invalid_mode_is_rejected_before_any_call(tmp_path: Path) -> None:
    run = FakeRun()
    outcome = switch_herdr(
        "dusk", run=run, selector=tmp_path / "config.toml", variant_root=tmp_path
    )
    assert outcome.status == "precondition-failed"
    assert run.calls == []


# ---------------------------------------------------------------------------
# Selector management
# ---------------------------------------------------------------------------


def test_absent_selector_is_created(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "herdr" / "config.toml"
    selector.parent.mkdir()
    outcome = switch_herdr("light", run=FakeRun(), selector=selector, variant_root=root)
    assert outcome.status == "applied"
    assert outcome.reload == "applied"
    assert selector.is_symlink()
    assert selector.readlink() == Path("config.light.toml")
    deployed = selector.parent / "config.light.toml"
    assert deployed.read_text() == (root / "0.9.1/config.light.toml").read_text()


def test_existing_symlink_selector_is_repointed(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    selector.symlink_to(root / "0.9.1/config.dark.toml")
    outcome = switch_herdr("light", run=FakeRun(), selector=selector, variant_root=root)
    assert outcome.status == "applied"
    assert selector.readlink() == Path("config.light.toml")
    assert outcome.previous_target == str(root / "0.9.1/config.dark.toml")


def test_repo_variant_is_never_modified(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    variant = root / "0.9.1/config.light.toml"
    before = variant.read_text()
    switch_herdr("light", run=FakeRun(), selector=tmp_path / "config.toml", variant_root=root)
    assert variant.read_text() == before
    assert not variant.is_symlink()


def test_deployed_copy_preserves_top_level_keys(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    deployed = tmp_path / "config.light.toml"
    deployed.write_text('onboarding = false\n\n[theme]\nname = "old"\n')
    outcome = switch_herdr(
        "light", run=FakeRun(), selector=tmp_path / "config.toml", variant_root=root
    )
    assert outcome.status == "applied"
    content = deployed.read_text()
    assert content.startswith("onboarding = false\n")
    assert content.count("onboarding = false") == 1
    assert content.count("[theme]") == 1


def test_regular_file_selector_is_refused_and_unchanged(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    selector.write_text("user owned\n")
    run = FakeRun()
    outcome = switch_herdr("light", run=run, selector=selector, variant_root=root)
    assert outcome.status == "selector-conflict"
    assert not selector.is_symlink()
    assert selector.read_text() == "user owned\n"
    assert ["herdr", "server", "reload-config"] not in run.calls


def test_override_with_missing_parent_fails_closed(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    env = {"HERDR_CONFIG_PATH": str(tmp_path / "missing" / "config.toml")}
    outcome = switch_herdr("light", env=env, run=FakeRun(), variant_root=root)
    assert outcome.status == "precondition-failed"
    assert not (tmp_path / "missing").exists()


def test_xdg_parent_directory_is_created(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    env = {"XDG_CONFIG_HOME": str(tmp_path / "xdg")}
    outcome = switch_herdr("light", env=env, run=FakeRun(), variant_root=root)
    assert outcome.status == "applied"
    assert (tmp_path / "xdg" / "herdr" / "config.toml").is_symlink()


def test_no_reload_requested_skips_the_reload_call(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    run = FakeRun()
    outcome = switch_herdr(
        "dark", reload_requested=False, run=run, selector=selector, variant_root=root
    )
    assert outcome.status == "applied"
    assert outcome.reload == "not-requested"
    assert ["herdr", "server", "reload-config"] not in run.calls


# ---------------------------------------------------------------------------
# Reload outcomes
# ---------------------------------------------------------------------------


def test_reload_server_not_running_keeps_the_selector(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    run = FakeRun(reload_stdout="", reload_stderr=SERVER_NOT_RUNNING, reload_returncode=1)
    outcome = switch_herdr("light", run=run, selector=selector, variant_root=root)
    assert outcome.status == "server_not_running"
    assert outcome.succeeded is True
    assert selector.readlink() == Path("config.light.toml")


def test_reload_failure_restores_the_previous_selector(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    original = root / "0.9.1/config.dark.toml"
    selector.symlink_to(original)
    run = FakeRun(reload_stdout=RELOAD_FAILED, reload_returncode=1)
    outcome = switch_herdr("light", run=run, selector=selector, variant_root=root)
    assert outcome.status == "reload-failed-restored"
    assert outcome.restoration == "succeeded"
    assert Path(selector.readlink()) == original


def test_reload_failure_removes_a_newly_created_selector(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    run = FakeRun(reload_stdout="", reload_stderr="boom", reload_returncode=1)
    outcome = switch_herdr("light", run=run, selector=selector, variant_root=root)
    assert outcome.status == "reload-failed-restored"
    assert not selector.is_symlink()
    assert not selector.exists()


def test_reload_launch_failure_restores_the_previous_selector(tmp_path: Path) -> None:
    root = _variant_root(tmp_path)
    selector = tmp_path / "config.toml"
    original = root / "0.9.1/config.dark.toml"
    selector.symlink_to(original)
    run = FakeRun(reload_error=FileNotFoundError("herdr"))
    outcome = switch_herdr("light", run=run, selector=selector, variant_root=root)
    assert outcome.status == "reload-failed-restored"
    assert Path(selector.readlink()) == original


# ---------------------------------------------------------------------------
# CLI exit codes
# ---------------------------------------------------------------------------


def test_main_exits_zero_for_success(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(
        switch_module,
        "switch_herdr",
        lambda *_a, **_k: switch_module.SwitchResult(
            "applied", "light", "0.8.2", True, "/s", None, "applied", "not-required", "ok"
        ),
    )
    assert switch_module.main(["light"]) == 0
    assert json.loads(capsys.readouterr().out.strip())["status"] == "applied"


@pytest.mark.parametrize("status", ["precondition-failed", "selector-conflict"])
def test_main_exits_zero_without_mutation(
    monkeypatch: pytest.MonkeyPatch, capsys, status: str
) -> None:
    monkeypatch.setattr(
        switch_module,
        "switch_herdr",
        lambda *_a, **_k: switch_module.SwitchResult(
            status, "light", None, False, "/s", None, "not-requested", "not-required", "no mutation"
        ),
    )
    assert switch_module.main(["light"]) == 0
    assert "no mutation" in capsys.readouterr().err


@pytest.mark.parametrize("status", ["reload-failed-restored", "restore-failed", "write-failed"])
def test_main_exits_one_on_real_failures(
    monkeypatch: pytest.MonkeyPatch, capsys, status: str
) -> None:
    monkeypatch.setattr(
        switch_module,
        "switch_herdr",
        lambda *_a, **_k: switch_module.SwitchResult(
            status, "light", "0.8.2", False, "/s", None, "failed", "succeeded", "boom"
        ),
    )
    assert switch_module.main(["light"]) == 1
    assert "boom" in capsys.readouterr().err
