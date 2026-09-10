"""Focused fault-injection tests for the exact-version Herdr activation transaction.

All tests use temporary directories and a fake ``herdr`` executable. No test
reads or writes the real user Herdr directory.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from dreamcoder_theme import herdr_activation as activation
from dreamcoder_theme.herdr_activation import activate_herdr, resolve_herdr_target

_CANONICAL_UI = '[ui]\naccent = "#6FA0AF"\n'
_CANONICAL_KEYS = (
    "[keys]\n"
    'prefix = "ctrl+a"\n'
    'previous_agent = "prefix+alt+k"\n'
    'next_agent = "prefix+alt+j"\n'
    'focus_agent = "prefix+ctrl+1..9"\n'
)


def _source(mode: str, accent: str) -> str:
    return (
        "[theme]\n"
        'name = "catppuccin"\n\n'
        "[theme.custom]\n"
        f'accent = "{accent}"\n\n'
        f"{_CANONICAL_UI}\n{_CANONICAL_KEYS}"
    )


def _source_root(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    root.mkdir()
    (root / "config.dark.toml").write_text(_source("dark", "#A5B4FC"))
    (root / "config.light.toml").write_text(_source("light", "#824f16"))
    return root


class FakeRun:
    """Callable stand-in for ``subprocess.run`` with scripted outcomes."""

    def __init__(self, version: str = "herdr 0.7.3\n", reload_returncode: int = 0) -> None:
        self.version = version
        self.reload_returncode = reload_returncode
        self.calls: list[list[str]] = []
        self.version_side_effect: Exception | None = None
        self.reload_side_effect: Exception | None = None

    def __call__(self, command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        if command[-1] == "--version":
            if self.version_side_effect is not None:
                raise self.version_side_effect
            return subprocess.CompletedProcess(command, 0, self.version, "")
        if self.reload_side_effect is not None:
            raise self.reload_side_effect
        return subprocess.CompletedProcess(command, self.reload_returncode, "", "")


# ---------------------------------------------------------------------------
# Target resolution
# ---------------------------------------------------------------------------


def test_target_resolution_prefers_explicit_override(tmp_path: Path) -> None:
    override = tmp_path / "custom" / "config.toml"
    target = resolve_herdr_target({"HERDR_CONFIG_PATH": str(override)})
    assert target == override


def test_target_resolution_uses_xdg_then_home_fallback(tmp_path: Path) -> None:
    xdg = tmp_path / "xdg"
    assert resolve_herdr_target({"XDG_CONFIG_HOME": str(xdg)}) == xdg / "herdr/config.toml"

    home = tmp_path / "home"
    assert resolve_herdr_target({"HOME": str(home)}) == home / ".config/herdr/config.toml"


@pytest.mark.parametrize(
    "env",
    (
        {"HERDR_CONFIG_PATH": ""},
        {"XDG_CONFIG_HOME": ""},
        {},
        {"HERDR_CONFIG_PATH": "relative/config.toml"},
        {"HERDR_CONFIG_PATH": "/"},
    ),
)
def test_target_resolution_rejects_unsafe_or_missing_inputs(env: dict[str, str]) -> None:
    with pytest.raises(activation.TargetResolutionError):
        resolve_herdr_target(env)


def test_target_resolution_rejects_nul_byte(tmp_path: Path) -> None:
    with pytest.raises(activation.TargetResolutionError):
        resolve_herdr_target({"HERDR_CONFIG_PATH": str(tmp_path / "bad\x00name")})


def test_target_resolution_rejects_existing_directory(tmp_path: Path) -> None:
    target = tmp_path / "config.toml"
    target.mkdir()
    with pytest.raises(activation.TargetResolutionError):
        resolve_herdr_target({"HERDR_CONFIG_PATH": str(target)})


def test_target_resolution_rejects_target_symlink(tmp_path: Path) -> None:
    real = tmp_path / "real.toml"
    real.write_text("x")
    link = tmp_path / "config.toml"
    link.symlink_to(real)
    with pytest.raises(activation.TargetResolutionError):
        resolve_herdr_target({"HERDR_CONFIG_PATH": str(link)})


def test_target_resolution_rejects_symlinked_parent(tmp_path: Path) -> None:
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    linked_dir = tmp_path / "linked_dir"
    linked_dir.symlink_to(real_dir)
    with pytest.raises(activation.TargetResolutionError):
        resolve_herdr_target({"HERDR_CONFIG_PATH": str(linked_dir / "config.toml")})


# ---------------------------------------------------------------------------
# Version gate — must precede any backup/staging/target mutation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version",
    ("herdr 0.7.2\n", "herdr 0.7.4\n", "not-herdr\n", "herdr 0.7.3 extra\n", ""),
)
def test_version_mismatch_fails_before_any_mutation(tmp_path: Path, version: str) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    fake = FakeRun(version=version)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "version"
    assert not target.exists()
    assert fake.calls == [["herdr", "--version"]]


def test_missing_executable_fails_before_mutation(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    fake = FakeRun()
    fake.version_side_effect = FileNotFoundError("herdr not found")

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "version"
    assert not target.exists()


def test_version_timeout_fails_before_mutation(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    fake = FakeRun()
    fake.version_side_effect = subprocess.TimeoutExpired(cmd=["herdr", "--version"], timeout=5)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "version"
    assert not target.exists()


# ---------------------------------------------------------------------------
# Mode and source validation
# ---------------------------------------------------------------------------


def test_unsupported_mode_fails_before_version_check(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    fake = FakeRun()

    result = activate_herdr(
        "dusk",  # type: ignore[arg-type]
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "mode"
    assert fake.calls == []


@pytest.mark.parametrize(
    "corrupt",
    (
        None,  # missing file
        "not even toml {{{",
        '[theme]\nname = "catppuccin"\n',  # missing custom/ui/keys
        '[theme]\nname = "catppuccin"\n[theme.custom]\naccent="#A5B4FC"\n'
        '[ui]\naccent = "#000000"\n\n[keys]\nprefix = "ctrl+a"\n'
        'previous_agent = "prefix+alt+k"\nnext_agent = "prefix+alt+j"\n'
        'focus_agent = "prefix+ctrl+1..9"\n',  # wrong canonical ui value
    ),
)
def test_invalid_source_fails_before_mutation(tmp_path: Path, corrupt: str | None) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "config.light.toml").write_text(_source("light", "#824f16"))
    if corrupt is not None:
        (source_root / "config.dark.toml").write_text(corrupt)
    target = tmp_path / "target" / "config.toml"
    fake = FakeRun()

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "source"
    assert not target.exists()


def test_source_symlink_is_rejected(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    real = source_root / "config.dark.toml"
    real.rename(source_root / "real-dark.toml")
    (source_root / "config.dark.toml").symlink_to(source_root / "real-dark.toml")
    target = tmp_path / "target" / "config.toml"

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "source"


# ---------------------------------------------------------------------------
# Absent-target and existing-target success paths
# ---------------------------------------------------------------------------


def test_absent_target_is_created_atomically_without_claiming_backup(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "applied"
    assert result.backup_path is None
    assert result.restoration == "not-required"
    assert result.reload == "not-requested"
    assert target.read_text() == (source_root / "config.dark.toml").read_text()
    remaining = list(target.parent.iterdir())
    assert remaining == [target]


def test_existing_target_is_backed_up_before_atomic_replace(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# personalized existing config\n"
    target.write_text(original)

    result = activate_herdr(
        "light",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "applied"
    assert result.backup_path is not None
    backup = Path(result.backup_path)
    assert backup.read_text() == original
    assert target.read_text() == (source_root / "config.light.toml").read_text()
    remaining = set(target.parent.iterdir())
    assert remaining == {target, backup}


def test_override_with_missing_parent_directory_fails_closed(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "missing-dir" / "config.toml"

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "precondition-failed"
    assert result.stage == "path"
    assert not target.parent.exists()


def test_xdg_derived_missing_parent_directory_is_created_and_activation_succeeds(
    tmp_path: Path,
) -> None:
    source_root = _source_root(tmp_path)
    xdg = tmp_path / "xdg-config"

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"XDG_CONFIG_HOME": str(xdg)},
        run=FakeRun(),
        source_root=source_root,
    )

    target = xdg / "herdr" / "config.toml"
    assert result.status == "applied"
    assert target.read_text() == (source_root / "config.dark.toml").read_text()


def test_xdg_derived_created_directory_is_removed_when_activation_fails_and_dir_stays_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    xdg = tmp_path / "xdg-config"
    monkeypatch.setattr(activation, "_open_exclusive", _raise_oserror)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"XDG_CONFIG_HOME": str(xdg)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "write-failed"
    assert not (xdg / "herdr").exists()


def test_xdg_derived_created_directory_is_kept_when_activation_succeeds(
    tmp_path: Path,
) -> None:
    source_root = _source_root(tmp_path)
    xdg = tmp_path / "xdg-config"

    result = activate_herdr(
        "light",
        reload_requested=False,
        env={"XDG_CONFIG_HOME": str(xdg)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "applied"
    assert (xdg / "herdr").is_dir()


# ---------------------------------------------------------------------------
# Backup / staging fault injection
# ---------------------------------------------------------------------------


def test_backup_create_failure_leaves_target_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    monkeypatch.setattr(activation, "_open_exclusive", _raise_oserror)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "backup-failed"
    assert result.stage == "backup"
    assert target.read_text() == original
    assert list(target.parent.iterdir()) == [target]


def test_backup_fsync_failure_leaves_target_unchanged_and_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    monkeypatch.setattr(activation, "_fsync_fd", _raise_oserror)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "backup-failed"
    assert result.stage == "backup"
    assert target.read_text() == original
    assert list(target.parent.iterdir()) == [target]


def test_staging_write_failure_leaves_target_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)

    calls = {"n": 0}
    real_open = activation._open_exclusive

    def flaky(path: Path) -> int:
        calls["n"] += 1
        if calls["n"] == 1:  # first exclusive create is the staging file
            raise OSError("disk full")
        return real_open(path)

    monkeypatch.setattr(activation, "_open_exclusive", flaky)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "write-failed"
    assert result.stage == "stage-write"
    assert not target.exists()


def test_replace_failure_leaves_target_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    monkeypatch.setattr(activation, "_atomic_replace", _raise_oserror2)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "write-failed"
    assert result.stage == "replace"
    assert target.read_text() == original
    assert result.backup_path is not None


def test_parent_fsync_failure_after_replace_restores_previous_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    monkeypatch.setattr(activation, "_fsync_directory", _raise_oserror)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status in {"write-failed", "restore-failed"}
    assert result.restoration in {"succeeded", "failed"}
    if result.restoration == "succeeded":
        assert target.read_text() == original


def test_identity_conflict_before_replace_is_reported_as_write_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_text("# original\n")

    calls = {"n": 0}

    def shifting_identity(_path: Path) -> tuple[int, int]:
        calls["n"] += 1
        return (1, calls["n"])

    monkeypatch.setattr(activation, "_current_identity", shifting_identity)

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert result.status == "write-failed"
    assert result.stage == "replace"
    assert target.read_text() == "# original\n"


# ---------------------------------------------------------------------------
# Reload behavior
# ---------------------------------------------------------------------------


def test_reload_not_requested_reports_applied_without_reload_claim(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    fake = FakeRun()

    result = activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "applied"
    assert result.reload == "not-requested"
    assert fake.calls == [["herdr", "--version"]]


def test_reload_requested_and_successful_runs_exact_argv(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    fake = FakeRun()

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "applied"
    assert result.reload == "succeeded"
    assert fake.calls == [["herdr", "--version"], ["herdr", "server", "reload-config"]]


@pytest.mark.parametrize("returncode", (1, 2))
def test_reload_nonzero_exit_restores_existing_target(tmp_path: Path, returncode: int) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    fake = FakeRun(reload_returncode=returncode)

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "reload-failed-restored"
    assert result.reload == "failed"
    assert result.restoration == "succeeded"
    assert target.read_text() == original


def test_reload_launch_failure_restores_existing_target(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    fake = FakeRun()
    fake.reload_side_effect = OSError("cannot exec")

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "reload-failed-restored"
    assert target.read_text() == original


def test_reload_timeout_restores_existing_target(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    fake = FakeRun()
    fake.reload_side_effect = subprocess.TimeoutExpired(cmd=["herdr", "server"], timeout=5)

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "reload-failed-restored"
    assert target.read_text() == original


def test_reload_failure_removes_newly_created_target_when_absent_before(
    tmp_path: Path,
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    fake = FakeRun(reload_returncode=1)

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "reload-failed-restored"
    assert not target.exists()


# ---------------------------------------------------------------------------
# Restore failure
# ---------------------------------------------------------------------------


def test_restore_failure_after_reload_failure_reports_backup_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    original = "# original\n"
    target.write_text(original)
    fake = FakeRun(reload_returncode=1)
    monkeypatch.setattr(activation, "_atomic_replace", _raise_after_first_call())

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "restore-failed"
    assert result.restoration == "failed"
    assert result.backup_path is not None


def test_restore_failure_for_absent_target_reports_restore_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    fake = FakeRun(reload_returncode=1)
    calls = {"n": 0}

    def shifting_identity(_path: Path) -> tuple[int, int]:
        calls["n"] += 1
        return (1, calls["n"])

    monkeypatch.setattr(activation, "_current_identity", shifting_identity)

    result = activate_herdr(
        "dark",
        reload_requested=True,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=fake,
        source_root=source_root,
    )

    assert result.status == "restore-failed"
    assert result.restoration == "failed"


# ---------------------------------------------------------------------------
# Scope confinement
# ---------------------------------------------------------------------------


def test_writes_are_confined_to_target_directory(tmp_path: Path) -> None:
    source_root = _source_root(tmp_path)
    target = tmp_path / "target" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_text("# original\n")

    activate_herdr(
        "dark",
        reload_requested=False,
        env={"HERDR_CONFIG_PATH": str(target)},
        run=FakeRun(),
        source_root=source_root,
    )

    assert set(tmp_path.iterdir()) == {source_root, target.parent}


def _raise_oserror(*_args: object, **_kwargs: object) -> int:
    raise OSError("injected failure")


def _raise_oserror2(*_args: object, **_kwargs: object) -> None:
    raise OSError("injected failure")


def _raise_after_first_call():
    calls = {"n": 0}
    real_replace = activation._atomic_replace

    def wrapper(source: Path, destination: Path) -> None:
        calls["n"] += 1
        if calls["n"] == 1:
            real_replace(source, destination)
            return
        raise OSError("injected restore failure")

    return wrapper


# ---------------------------------------------------------------------------
# CLI exit code: precondition-failed must not abort the caller's `set -e`
# theme-mode script (scripts/apply-theme-mode.sh) just because Herdr isn't
# the one pinned-supported version.
# ---------------------------------------------------------------------------


def _result(status: str, message: str = "") -> activation.ActivationResult:
    return activation.ActivationResult(
        status=status,  # type: ignore[arg-type]
        stage="version",  # type: ignore[arg-type]
        mode="dark",
        reload="not-requested",  # type: ignore[arg-type]
        restoration="not-required",  # type: ignore[arg-type]
        backup_path=None,
        target=None,
        message=message or f"status={status}",
    )


def test_main_exits_zero_on_precondition_failed(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        activation, "activate_herdr", lambda *a, **k: _result("precondition-failed")
    )
    assert activation.main(["dark"]) == 0
    assert "status=precondition-failed" in capsys.readouterr().err


def test_main_exits_zero_on_applied(monkeypatch, capsys) -> None:
    monkeypatch.setattr(activation, "activate_herdr", lambda *a, **k: _result("applied"))
    assert activation.main(["dark"]) == 0


@pytest.mark.parametrize(
    "status", ["backup-failed", "write-failed", "reload-failed-restored", "restore-failed"]
)
def test_main_exits_one_on_real_mutation_failures(monkeypatch, capsys, status: str) -> None:
    monkeypatch.setattr(activation, "activate_herdr", lambda *a, **k: _result(status))
    assert activation.main(["dark"]) == 1
    assert f"status={status}" in capsys.readouterr().err
