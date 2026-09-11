"""Select the generated Herdr variant for the installed version and reload.

Implements the live-switching contract documented in ``docs/herdr.md``: resolve
the active selector, choose the generated variant for the installed Herdr
version, manage only an absent selector or an existing symlink, request a live
reload, and restore the previous selector when the reload does not report
``applied``.

When the installed version is newer than every complete checked-in profile, the
newest generated variant is used as a compatibility fallback. ``herdr config
check`` under ``HERDR_CONFIG_PATH`` must accept that variant before the selector
is touched, so an incompatible schema fails closed instead of being selected.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .herdr_contract import SUPPORTED_PROFILES, ContractStatus, detect_profile
from .settings import ROOT

_VERSION_TIMEOUT_SECONDS = 5
_RELOAD_TIMEOUT_SECONDS = 10
_VALID_MODES = ("dark", "light", "night")
_VARIANT_ROOT = ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder"
_VERSION_OUTPUT = re.compile(r"herdr[ \t]+(\d+)\.(\d+)\.(\d+)", re.IGNORECASE)

Run = Callable[..., subprocess.CompletedProcess[str]]
Mode = Literal["dark", "light", "night"]

Status = Literal[
    "applied",
    "server_not_running",
    "precondition-failed",
    "selector-conflict",
    "write-failed",
    "reload-failed-restored",
    "restore-failed",
]
ReloadState = Literal["not-requested", "applied", "server-not-running", "failed"]
RestorationState = Literal["not-required", "succeeded", "failed"]


class SelectorResolutionError(Exception):
    """Raised when the active Herdr selector cannot be resolved safely."""


class SwitchPreconditionError(Exception):
    """A precondition that must leave the selector untouched did not hold."""

    def __init__(self, status: Status, message: str, selector: Path | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.selector = selector


@dataclass(frozen=True)
class SwitchResult:
    """Outcome of one variant selection and reload attempt."""

    status: Status
    mode: str | None
    profile_version: str | None
    fallback: bool
    selector: str | None
    previous_target: str | None
    reload: ReloadState
    restoration: RestorationState
    message: str

    @property
    def succeeded(self) -> bool:
        return self.status in {"applied", "server_not_running"}


@dataclass(frozen=True)
class VariantChoice:
    """Selected generated variant, or the reason none can be selected."""

    path: Path | None
    profile_version: str | None = None
    fallback: bool = False
    reason: str = ""


@dataclass(frozen=True)
class _Prepared:
    """Every precondition satisfied; only the selector write and reload remain."""

    mode: str
    variant: Path
    profile_version: str | None
    fallback: bool
    note: str
    selector: Path
    previous: str | None


# ---------------------------------------------------------------------------
# Selector resolution and Symlink management
# ---------------------------------------------------------------------------


def resolve_selector(env: Mapping[str, str]) -> Path:
    """Resolve the active selector with documented precedence."""
    override = env.get("HERDR_CONFIG_PATH")
    if override is not None:
        if not override:
            raise SelectorResolutionError("HERDR_CONFIG_PATH is set but empty")
        return Path(override)
    xdg = env.get("XDG_CONFIG_HOME")
    if xdg is not None:
        if not xdg:
            raise SelectorResolutionError("XDG_CONFIG_HOME is set but empty")
        return Path(xdg) / "herdr" / "config.toml"
    home = env.get("HOME")
    if not home:
        raise SelectorResolutionError("HOME is required when XDG_CONFIG_HOME is unset")
    return Path(home) / ".config" / "herdr" / "config.toml"


def _selector_state(selector: Path) -> tuple[str, str | None]:
    """Return ``(state, previous_link_target)`` without following symlinks."""
    if selector.is_symlink():
        return "symlink", os.readlink(selector)
    if selector.exists():
        return "regular", None
    return "absent", None


def _sibling_path(selector: Path) -> Path:
    return selector.with_name(f".{selector.name}.dreamcoder-{os.getpid()}-{uuid.uuid4().hex}")


def _point_selector(selector: Path, target: Path) -> None:
    staging = _sibling_path(selector)
    os.symlink(str(target), staging)
    try:
        os.replace(staging, selector)
    except OSError:
        staging.unlink(missing_ok=True)
        raise


def _restore_selector(selector: Path, previous_target: str | None) -> bool:
    try:
        if previous_target is None:
            if selector.is_symlink():
                selector.unlink()
            return True
        staging = _sibling_path(selector)
        os.symlink(previous_target, staging)
        os.replace(staging, selector)
    except OSError:
        return False
    return True


def _preamble(text: str) -> str:
    """Top-level scalar keys (for example Herdr's ``onboarding``) before any section."""
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            break
        if re.match(r"^[A-Za-z_][A-Za-z0-9_.-]*\s*=", stripped):
            lines.append(line.rstrip())
    return "".join(f"{line}\n" for line in lines)


def _deploy_variant(variant: Path, selector: Path, mode: str) -> Path:
    """Copy the generated variant next to the selector so Herdr never writes the repo.

    User-owned top-level keys already present in the deployed copy (Herdr's own
    ``onboarding``, for instance) are preserved so a mode switch does not drop
    them.
    """
    deployed = selector.parent / f"config.{mode}.toml"
    preserved = ""
    if deployed.is_file() and not deployed.is_symlink():
        preserved = _preamble(deployed.read_text(encoding="utf-8"))
    staging = _sibling_path(deployed)
    staging.write_text(preserved + variant.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        os.replace(staging, deployed)
    except OSError:
        staging.unlink(missing_ok=True)
        raise
    return deployed


# ---------------------------------------------------------------------------
# Version detection and variant selection
# ---------------------------------------------------------------------------


def _parse_version(version_output: str) -> tuple[int, int, int] | None:
    match = _VERSION_OUTPUT.fullmatch(version_output.strip())
    if match is None:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _profile_version(profile_version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", profile_version)
    if match is None:  # pragma: no cover - SUPPORTED_PROFILES versions are validated
        raise ValueError(f"malformed profile version: {profile_version!r}")
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def choose_variant(version_output: str | None, mode: str, variant_root: Path) -> VariantChoice:
    """Select the generated ``config.<mode>.toml`` variant for the runtime."""
    selection = detect_profile(version_output)
    if selection.status is ContractStatus.SKIPPED_NOT_INSTALLED:
        return VariantChoice(None, reason="herdr executable is unavailable")

    if selection.status is ContractStatus.SUPPORTED and selection.profile is not None:
        version = selection.profile.evidence.version
        return VariantChoice(variant_root / version / f"config.{mode}.toml", version, False)

    parsed = _parse_version(version_output or "")
    if parsed is None:
        return VariantChoice(None, reason=f"unrecognised herdr version output: {version_output!r}")

    newest = max(SUPPORTED_PROFILES, key=lambda profile: _profile_version(profile.evidence.version))
    if parsed > _profile_version(newest.evidence.version):
        version = newest.evidence.version
        return VariantChoice(
            variant_root / version / f"config.{mode}.toml",
            version,
            True,
            reason=(
                f"herdr {'.'.join(str(part) for part in parsed)} has no checked-in profile; "
                f"using the newest generated variant ({version})"
            ),
        )
    return VariantChoice(
        None, reason=f"unsupported herdr version: {'.'.join(str(part) for part in parsed)}"
    )


# ---------------------------------------------------------------------------
# Runtime interactions
# ---------------------------------------------------------------------------


def _read_version(run: Run) -> str | None:
    try:
        process = run(
            ["herdr", "--version"],
            capture_output=True,
            text=True,
            timeout=_VERSION_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if process.returncode != 0:
        return None
    output = (process.stdout or "").strip()
    return output or None


def _config_check(run: Run, variant: Path, env: Mapping[str, str]) -> bool:
    probe_env = dict(env)
    probe_env["HERDR_CONFIG_PATH"] = str(variant)
    try:
        process = run(
            ["herdr", "config", "check"],
            capture_output=True,
            text=True,
            timeout=_VERSION_TIMEOUT_SECONDS,
            check=False,
            env=probe_env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return process.returncode == 0


def _reload(run: Run, env: Mapping[str, str]) -> ReloadState:
    try:
        process = run(
            ["herdr", "server", "reload-config"],
            capture_output=True,
            text=True,
            timeout=_RELOAD_TIMEOUT_SECONDS,
            check=False,
            env=dict(env),
        )
    except (OSError, subprocess.TimeoutExpired):
        return "failed"
    payload = _parse_payload(process.stdout) or _parse_payload(process.stderr)
    if payload is None:
        return "failed"
    result = payload.get("result")
    if isinstance(result, dict) and result.get("status") == "applied":
        return "applied"
    error = payload.get("error")
    if isinstance(error, dict) and error.get("code") == "server_not_running":
        return "server-not-running"
    return "failed"


def _parse_payload(stream: str | None) -> dict[str, object] | None:
    if not stream or not stream.strip():
        return None
    for line in reversed(stream.strip().splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


# ---------------------------------------------------------------------------
# Switching transaction
# ---------------------------------------------------------------------------


def _result(
    status: Status,
    message: str,
    *,
    mode: str | None,
    choice: VariantChoice | None = None,
    selector: Path | None = None,
    previous: str | None = None,
    reload: ReloadState = "not-requested",
    restoration: RestorationState = "not-required",
) -> SwitchResult:
    return SwitchResult(
        status=status,
        mode=mode if mode in _VALID_MODES else None,
        profile_version=choice.profile_version if choice is not None else None,
        fallback=choice.fallback if choice is not None else False,
        selector=str(selector) if selector is not None else None,
        previous_target=previous,
        reload=reload,
        restoration=restoration,
        message=message,
    )


def _prepare_selector(
    environment: Mapping[str, str], selector: Path | None
) -> tuple[Path, str | None]:
    """Resolve the selector and prove it is safe to manage, or raise."""
    if selector is None:
        try:
            selector = resolve_selector(environment)
        except SelectorResolutionError as error:
            raise SwitchPreconditionError("precondition-failed", str(error)) from error

    state, previous = _selector_state(selector)
    if state == "regular":
        raise SwitchPreconditionError(
            "selector-conflict",
            f"refusing to replace a regular Herdr config file: {selector}. "
            "Replace it with a symlink to opt in.",
            selector,
        )

    if not selector.parent.exists():
        if environment.get("HERDR_CONFIG_PATH"):
            raise SwitchPreconditionError(
                "precondition-failed",
                f"override selector parent directory does not exist: {selector.parent}",
                selector,
            )
        try:
            selector.parent.mkdir(parents=True)
        except OSError as error:
            raise SwitchPreconditionError(
                "precondition-failed",
                f"failed to create Herdr config directory: {error}",
                selector,
            ) from error
    return selector, previous


def _prepare(
    mode: str,
    environment: Mapping[str, str],
    run: Run,
    selector: Path | None,
    variant_root: Path,
) -> SwitchResult | _Prepared:
    choice = choose_variant(_read_version(run), mode, variant_root)
    if choice.path is None:
        return _result("precondition-failed", choice.reason, mode=mode)

    variant = choice.path
    if not variant.is_file() or variant.is_symlink():
        return _result(
            "precondition-failed",
            f"generated Herdr {mode} variant is missing: {variant}",
            mode=mode,
            choice=choice,
        )

    if not _config_check(run, variant, environment):
        return _result(
            "precondition-failed",
            f"herdr config check rejected the generated {mode} variant: {variant}",
            mode=mode,
            choice=choice,
        )

    try:
        selector_path, previous = _prepare_selector(environment, selector)
    except SwitchPreconditionError as error:
        return _result(
            error.status,
            error.message,
            mode=mode,
            choice=choice,
            selector=error.selector,
        )
    return _Prepared(
        mode,
        variant,
        choice.profile_version,
        choice.fallback,
        choice.reason,
        selector_path,
        previous,
    )


def _finish(prepared: _Prepared, environment: Mapping[str, str], run: Run) -> SwitchResult:
    prefix = prepared.note + "; " if prepared.note else ""
    reload_state = _reload(run, environment)
    if reload_state == "applied":
        return _result(
            "applied",
            f"{prefix}selected {prepared.variant} and reloaded the server",
            mode=prepared.mode,
            choice=_choice_of(prepared),
            selector=prepared.selector,
            previous=prepared.previous,
            reload="applied",
        )
    if reload_state == "server-not-running":
        return _result(
            "server_not_running",
            f"{prefix}selected {prepared.variant}; reload is deferred until the server starts",
            mode=prepared.mode,
            choice=_choice_of(prepared),
            selector=prepared.selector,
            previous=prepared.previous,
            reload="server-not-running",
        )
    restored = _restore_selector(prepared.selector, prepared.previous)
    return _result(
        "reload-failed-restored" if restored else "restore-failed",
        f"{prefix}Herdr reload failed; previous selector was "
        + ("restored" if restored else "NOT restored"),
        mode=prepared.mode,
        choice=_choice_of(prepared),
        selector=prepared.selector,
        previous=prepared.previous,
        reload="failed",
        restoration="succeeded" if restored else "failed",
    )


def _choice_of(prepared: _Prepared) -> VariantChoice:
    return VariantChoice(
        prepared.variant, prepared.profile_version, prepared.fallback, prepared.note
    )


def switch_herdr(
    mode: str,
    *,
    reload_requested: bool = True,
    env: Mapping[str, str] | None = None,
    run: Run = subprocess.run,
    selector: Path | None = None,
    variant_root: Path = _VARIANT_ROOT,
) -> SwitchResult:
    """Select the installed runtime's generated variant and reload Herdr."""
    environment = os.environ if env is None else dict(env)

    if mode not in _VALID_MODES:
        return _result("precondition-failed", f"unsupported Herdr mode: {mode!r}", mode=mode)

    prepared = _prepare(mode, environment, run, selector, variant_root)
    if isinstance(prepared, SwitchResult):
        return prepared

    try:
        deployed = _deploy_variant(prepared.variant, prepared.selector, prepared.mode)
        _point_selector(prepared.selector, Path(deployed.name))
    except OSError as error:
        return _result(
            "write-failed",
            f"failed to deploy the Herdr variant: {error}",
            mode=mode,
            choice=_choice_of(prepared),
            selector=prepared.selector,
            previous=prepared.previous,
        )

    if not reload_requested:
        prefix = prepared.note + "; " if prepared.note else ""
        return _result(
            "applied",
            f"{prefix}selected {prepared.variant}; reload was not requested",
            mode=mode,
            choice=_choice_of(prepared),
            selector=prepared.selector,
            previous=prepared.previous,
        )
    return _finish(prepared, environment, run)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select the Dreamcoder Herdr variant for the installed version"
    )
    parser.add_argument("mode", choices=_VALID_MODES)
    parser.add_argument("--no-reload", action="store_false", dest="reload_requested", default=True)
    args = parser.parse_args(argv)
    outcome = switch_herdr(args.mode, reload_requested=args.reload_requested)
    print(json.dumps(asdict(outcome), sort_keys=True))
    if not outcome.succeeded:
        print(outcome.message, file=sys.stderr)
    if outcome.succeeded or outcome.status in {"precondition-failed", "selector-conflict"}:
        # No mutation was attempted or the selector is user-owned: do not abort
        # the enclosing theme switch for an optional, environment-dependent
        # integration. A real mutation or reload failure still exits 1.
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
