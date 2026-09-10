"""Explicit, transactional activation for exact-version Herdr 0.7.3 configs.

This module never runs automatically. A caller explicitly selects ``dark`` or
``light`` and opts into a documented reload attempt. Activation is refused
unless the installed runtime reports exactly ``herdr 0.7.3``. A failed write
or attempted reload restores the prior active configuration from a retained
backup; a previously absent target is removed instead. No other Herdr
version, mode, or target is supported by this module.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import subprocess
import sys
import tomllib
import uuid
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .settings import ROOT

_HERDR_VERSION = "herdr 0.7.3"
_VERSION_TIMEOUT_SECONDS = 5
_RELOAD_TIMEOUT_SECONDS = 5
_VALID_MODES = ("dark", "light")
_SOURCE_ROOT = ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3"

_CANONICAL_UI = {"accent": "#6FA0AF"}
_CANONICAL_KEYS = {
    "prefix": "ctrl+a",
    "previous_agent": "prefix+alt+k",
    "next_agent": "prefix+alt+j",
    "focus_agent": "prefix+ctrl+1..9",
}

Run = Callable[..., subprocess.CompletedProcess[str]]
Mode = Literal["dark", "light"]
Status = Literal[
    "applied",
    "precondition-failed",
    "backup-failed",
    "write-failed",
    "reload-failed-restored",
    "restore-failed",
]
Stage = Literal[
    "mode",
    "version",
    "source",
    "path",
    "backup",
    "stage-write",
    "replace",
    "reload",
    "restore",
    "complete",
]
ReloadState = Literal["not-requested", "succeeded", "failed"]
RestorationState = Literal["not-required", "succeeded", "failed"]


class TargetResolutionError(Exception):
    """Raised when the Herdr active-config target cannot be resolved safely."""


@dataclass(frozen=True)
class ActivationResult:
    """Outcome of one explicit Herdr activation transaction."""

    status: Status
    stage: Stage
    mode: str | None
    reload: ReloadState
    restoration: RestorationState
    backup_path: str | None
    target: str | None
    message: str

    @property
    def succeeded(self) -> bool:
        return self.status == "applied"


# ---------------------------------------------------------------------------
# Path resolution and safety
# ---------------------------------------------------------------------------


def _check_path_safety(path: Path) -> str | None:
    if "\x00" in str(path):
        return "resolved Herdr path contains a NUL byte"
    if not path.is_absolute():
        return "resolved Herdr path must be absolute"
    if path.parent == path:
        return "resolved Herdr path must not be the filesystem root"
    if path.is_dir():
        return "resolved Herdr path is an existing directory"
    if path.is_symlink():
        return "resolved Herdr path must not be a symlink"
    parent = path.parent
    while True:
        if parent.exists() and parent.is_symlink():
            return f"resolved Herdr path has a symlinked parent: {parent}"
        if parent.parent == parent:
            return None
        parent = parent.parent


def is_override_target(env: Mapping[str, str]) -> bool:
    """Report whether the active target came from the explicit override variable."""
    return bool(env.get("HERDR_CONFIG_PATH"))


def resolve_herdr_target(env: Mapping[str, str]) -> Path:
    """Resolve the managed Herdr active-config path with documented precedence."""
    override = env.get("HERDR_CONFIG_PATH")
    if override is not None:
        if not override:
            raise TargetResolutionError("HERDR_CONFIG_PATH is set but empty")
        candidate = Path(override)
    else:
        xdg = env.get("XDG_CONFIG_HOME")
        if xdg is not None:
            if not xdg:
                raise TargetResolutionError("XDG_CONFIG_HOME is set but empty")
            candidate = Path(xdg) / "herdr" / "config.toml"
        else:
            home = env.get("HOME")
            if not home:
                raise TargetResolutionError("HOME is required when XDG_CONFIG_HOME is unset")
            candidate = Path(home) / ".config" / "herdr" / "config.toml"

    error = _check_path_safety(candidate)
    if error is not None:
        raise TargetResolutionError(error)
    return candidate


# ---------------------------------------------------------------------------
# Version gate
# ---------------------------------------------------------------------------


def _herdr_version_matches(run: Run) -> bool:
    try:
        process = run(
            ["herdr", "--version"],
            capture_output=True,
            text=True,
            timeout=_VERSION_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if process.returncode != 0:
        return False
    output = process.stdout
    if output.endswith("\r\n"):
        output = output[:-2]
    elif output.endswith("\n"):
        output = output[:-1]
    return output == _HERDR_VERSION


# ---------------------------------------------------------------------------
# Source validation
# ---------------------------------------------------------------------------


def _source_path(source_root: Path, mode: Mode) -> Path:
    return source_root / f"config.{mode}.toml"


def _validate_source(path: Path) -> bytes | None:
    try:
        if path.is_symlink() or not path.is_file():
            return None
        raw = path.read_bytes()
        parsed = tomllib.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    theme = parsed.get("theme")
    if not isinstance(theme, dict) or not isinstance(theme.get("custom"), dict):
        return None
    if parsed.get("ui") != _CANONICAL_UI:
        return None
    if parsed.get("keys") != _CANONICAL_KEYS:
        return None
    return raw


# ---------------------------------------------------------------------------
# Filesystem transaction primitives (monkeypatch seams for fault injection)
# ---------------------------------------------------------------------------


def _open_exclusive(path: Path) -> int:
    return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)


def _fsync_fd(fd: int) -> None:
    os.fsync(fd)


def _fsync_directory(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_replace(source: Path, destination: Path) -> None:
    os.replace(source, destination)


def _current_identity(path: Path) -> tuple[int, int] | None:
    try:
        stat_result = os.lstat(path)
    except OSError:
        return None
    return (stat_result.st_dev, stat_result.st_ino)


def _sibling_path(target: Path, kind: str) -> Path:
    return target.with_name(f".{target.name}.dreamcoder-{kind}-{os.getpid()}-{uuid.uuid4().hex}")


def _write_exclusive(path: Path, data: bytes) -> None:
    fd = _open_exclusive(path)
    try:
        os.write(fd, data)
        _fsync_fd(fd)
    finally:
        os.close(fd)


def _write_exclusive_or_cleanup(path: Path, data: bytes) -> None:
    try:
        _write_exclusive(path, data)
    except OSError:
        path.unlink(missing_ok=True)
        raise


def _attempt_reload(run: Run) -> bool:
    try:
        process = run(
            ["herdr", "server", "reload-config"],
            capture_output=True,
            text=True,
            timeout=_RELOAD_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return process.returncode == 0


def _attempt_restore(
    target: Path, backup_path: Path | None, installed_identity: tuple[int, int] | None
) -> bool:
    if backup_path is not None:
        try:
            data = backup_path.read_bytes()
            restore_stage = _sibling_path(target, "restore")
            _write_exclusive_or_cleanup(restore_stage, data)
            _atomic_replace(restore_stage, target)
            _fsync_directory(target.parent)
        except OSError:
            return False
        return True

    current = _current_identity(target)
    if current is None:
        return True
    if current != installed_identity:
        return False
    try:
        target.unlink()
    except OSError:
        return False
    return True


# ---------------------------------------------------------------------------
# Activation transaction
# ---------------------------------------------------------------------------


def activate_herdr(
    mode: Mode,
    *,
    reload_requested: bool,
    env: Mapping[str, str] | None = None,
    run: Run = subprocess.run,
    source_root: Path = _SOURCE_ROOT,
) -> ActivationResult:
    """Explicitly activate one checked-in Dreamcoder Herdr 0.7.3 configuration."""
    environment = os.environ if env is None else env

    def failure(
        status: Status,
        stage: Stage,
        message: str,
        *,
        target: Path | None = None,
        backup_path: Path | None = None,
        reload: ReloadState = "not-requested",
        restoration: RestorationState = "not-required",
    ) -> ActivationResult:
        return ActivationResult(
            status=status,
            stage=stage,
            mode=mode if mode in _VALID_MODES else None,
            reload=reload,
            restoration=restoration,
            backup_path=str(backup_path) if backup_path is not None else None,
            target=str(target) if target is not None else None,
            message=message,
        )

    if mode not in _VALID_MODES:
        return failure("precondition-failed", "mode", f"unsupported Herdr mode: {mode!r}")

    if not _herdr_version_matches(run):
        return failure(
            "precondition-failed",
            "version",
            "herdr --version did not report exactly 'herdr 0.7.3'",
        )

    source_bytes = _validate_source(_source_path(source_root, mode))
    if source_bytes is None:
        return failure(
            "precondition-failed",
            "source",
            f"checked-in Herdr {mode} source is missing or does not match the canonical shape",
        )

    try:
        target = resolve_herdr_target(environment)
    except TargetResolutionError as error:
        return failure("precondition-failed", "path", str(error))

    created_parent = False
    if not target.parent.exists():
        if is_override_target(environment):
            return failure(
                "precondition-failed",
                "path",
                f"override parent directory does not exist: {target.parent}",
                target=target,
            )
        try:
            target.parent.mkdir(parents=True)
            created_parent = True
        except OSError as error:
            return failure(
                "precondition-failed",
                "path",
                f"failed to create Herdr config directory: {error}",
                target=target,
            )

    result = _run_transaction(mode, target, source_bytes, reload_requested, run, failure)
    if created_parent and result.status != "applied":
        with contextlib.suppress(OSError):
            target.parent.rmdir()  # only removes it when it is empty
    return result


Failure = Callable[..., ActivationResult]


def _run_transaction(
    mode: Mode,
    target: Path,
    source_bytes: bytes,
    reload_requested: bool,
    run: Run,
    failure: Failure,
) -> ActivationResult:
    had_previous = target.exists()
    backup_path: Path | None = None

    if had_previous:
        backup_path = _sibling_path(target, "backup")
        try:
            _write_exclusive_or_cleanup(backup_path, target.read_bytes())
        except OSError as error:
            return failure(
                "backup-failed", "backup", f"failed to create backup: {error}", target=target
            )

    staging_path = _sibling_path(target, "stage")
    try:
        _write_exclusive_or_cleanup(staging_path, source_bytes)
    except OSError as error:
        return failure(
            "write-failed",
            "stage-write",
            f"failed to write staging file: {error}",
            target=target,
            backup_path=backup_path,
        )

    initial_identity = _current_identity(target) if had_previous else None
    recheck_identity = _current_identity(target) if had_previous else None
    if had_previous and initial_identity != recheck_identity:
        staging_path.unlink(missing_ok=True)
        return failure(
            "write-failed",
            "replace",
            "target changed externally before activation could replace it",
            target=target,
            backup_path=backup_path,
        )

    try:
        _atomic_replace(staging_path, target)
    except OSError as error:
        staging_path.unlink(missing_ok=True)
        return failure(
            "write-failed",
            "replace",
            f"failed to replace target: {error}",
            target=target,
            backup_path=backup_path,
        )

    installed_identity = _current_identity(target)

    try:
        _fsync_directory(target.parent)
    except OSError as error:
        restored = _attempt_restore(target, backup_path, installed_identity)
        return failure(
            "write-failed" if restored else "restore-failed",
            "replace",
            f"failed to fsync parent directory after replace: {error}",
            target=target,
            backup_path=backup_path,
            restoration="succeeded" if restored else "failed",
        )

    if not reload_requested:
        return failure(
            "applied",
            "complete",
            f"Herdr {mode} configuration updated; reload was not requested",
            target=target,
            backup_path=backup_path,
        )

    if _attempt_reload(run):
        return failure(
            "applied",
            "complete",
            f"Herdr {mode} configuration updated and reloaded",
            target=target,
            backup_path=backup_path,
            reload="succeeded",
        )

    restored = _attempt_restore(target, backup_path, installed_identity)
    return failure(
        "reload-failed-restored" if restored else "restore-failed",
        "reload",
        "Herdr reload failed; previous configuration was "
        + ("restored" if restored else "NOT restored"),
        target=target,
        backup_path=backup_path,
        reload="failed",
        restoration="succeeded" if restored else "failed",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explicitly activate a Dreamcoder Herdr theme")
    parser.add_argument("mode", choices=_VALID_MODES)
    parser.add_argument("--reload", action="store_true", dest="reload_requested")
    args = parser.parse_args(argv)
    result = activate_herdr(args.mode, reload_requested=args.reload_requested)
    print(asdict(result))
    if not result.succeeded:
        print(result.message, file=sys.stderr)
    if result.succeeded or result.status == "precondition-failed":
        # precondition-failed means no mutation was attempted (wrong Herdr
        # version, missing binary, invalid source) — there is nothing to
        # roll back and nothing broke. Exit 0 so callers under `set -e`
        # (scripts/apply-theme-mode.sh) don't abort mode-switching for
        # every other target just because this optional integration
        # doesn't apply in the current environment. A real mutation
        # failure (backup/write/reload/restore) still exits 1.
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
