"""Deterministic renderer registry assembly and validation.

Hexagonal-architecture-v2 design §1-§2 / ADR-001 / ADR-002:

- registrations live adjacent to their leaf renderer modules as immutable
  ``REGISTRATIONS`` tuples; this module imports them through an explicit,
  reviewable tuple and sorts by ``consumer_id`` (no dynamic discovery, no
  decorator/import side effects, no unordered assembly);
- ``EXPECTED_CONSUMER_IDS`` is the explicit frozen 33-ID set; its cardinality is
  never used as policy — diagnostics compare registered vs expected sets;
- ``validate_registry()`` implements the design §1 checks: unique non-empty
  IDs, contract version, closed mode set, output-ownership validity, port
  conformance (callable + ``str`` result for every declared mode), strategy
  compatibility, and the exact expected-ID bijection. Path-template/env-name
  validation becomes binding in Phase 2 when path resolvers introduce path
  fields; the PR 1 model carries no path fields.
- discovery and conformance are pure: no file creation, no selectors, no
  subprocesses, no installer or settings behavior.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .renderer_contract import (
    ALL_MODES,
    SUPPORTED_CONTRACT_VERSION,
    ActiveStrategy,
    MutationStrategy,
    OutputKind,
    Palette,
    RendererRegistration,
    RendererStrategy,
    RenderMode,
    RepositoryStrategy,
    SyncDefinition,
)

# --- Explicit leaf registration imports (reviewable; never dynamic) -----------
from .renderers_antigravity import REGISTRATIONS as ANTIGRAVITY_REGISTRATIONS
from .renderers_codex import REGISTRATIONS as CODEX_REGISTRATIONS
from .renderers_extra_bat_delta import REGISTRATIONS as BAT_DELTA_REGISTRATIONS
from .renderers_extra_btop import REGISTRATIONS as BTOP_REGISTRATIONS
from .renderers_extra_firefox import REGISTRATIONS as FIREFOX_REGISTRATIONS
from .renderers_extra_notify import REGISTRATIONS as NOTIFY_REGISTRATIONS
from .renderers_extra_nvim import REGISTRATIONS as NVIM_REGISTRATIONS
from .renderers_extra_obsidian import REGISTRATIONS as OBSIDIAN_REGISTRATIONS
from .renderers_extra_shell import REGISTRATIONS as SHELL_REGISTRATIONS
from .renderers_ghostty_warp import REGISTRATIONS as GHOSTTY_WARP_REGISTRATIONS
from .renderers_herdr import REGISTRATIONS as HERDR_REGISTRATIONS
from .renderers_hypr_waybar_rofi import REGISTRATIONS as HYPR_WAYBAR_ROFI_REGISTRATIONS
from .renderers_kitty import REGISTRATIONS as KITTY_REGISTRATIONS
from .renderers_lazygit import REGISTRATIONS as LAZYGIT_REGISTRATIONS
from .renderers_opencode import REGISTRATIONS as OPENCODE_REGISTRATIONS
from .renderers_pi import REGISTRATIONS as PI_REGISTRATIONS
from .renderers_starship import REGISTRATIONS as STARSHIP_REGISTRATIONS
from .renderers_tmux import REGISTRATIONS as TMUX_REGISTRATIONS
from .renderers_zellij import REGISTRATIONS as ZELLIJ_REGISTRATIONS

# --- Deterministic assembly ----------------------------------------------------
# Explicit group tuple (no globals/dynamic discovery); final order is sorted by
# consumer_id, so assembly is identical regardless of import order.
_REGISTRATION_GROUPS: tuple[tuple[RendererRegistration, ...], ...] = (
    ANTIGRAVITY_REGISTRATIONS,
    BAT_DELTA_REGISTRATIONS,
    BTOP_REGISTRATIONS,
    CODEX_REGISTRATIONS,
    FIREFOX_REGISTRATIONS,
    GHOSTTY_WARP_REGISTRATIONS,
    HERDR_REGISTRATIONS,
    HYPR_WAYBAR_ROFI_REGISTRATIONS,
    KITTY_REGISTRATIONS,
    LAZYGIT_REGISTRATIONS,
    NOTIFY_REGISTRATIONS,
    NVIM_REGISTRATIONS,
    OBSIDIAN_REGISTRATIONS,
    OPENCODE_REGISTRATIONS,
    PI_REGISTRATIONS,
    SHELL_REGISTRATIONS,
    STARSHIP_REGISTRATIONS,
    TMUX_REGISTRATIONS,
    ZELLIJ_REGISTRATIONS,
)

REGISTRATIONS: tuple[RendererRegistration, ...] = tuple(
    sorted((r for group in _REGISTRATION_GROUPS for r in group), key=lambda r: r.consumer_id)
)

# --- Explicit expected 33-consumer set (design §5.1, tasks 0.1/1.6) -----------
EXPECTED_CONSUMER_IDS: frozenset[str] = frozenset(
    {
        "kitty",
        "kitty_ui",
        "ghostty",
        "warp",
        "starship",
        "codex_app",
        "codex_theme",
        "bat_theme",
        "pi_theme",
        "antigravity",
        "tmux",
        "lazygit",
        "zsh_syntax",
        "ls_colors",
        "bat",
        "delta",
        "fzf",
        "btop",
        "dunst",
        "firefox",
        "obsidian",
        "cava",
        "opencode",
        "zellij",
        "nvim",
        "hyprland",
        "hypr_colors_lua",
        "hypr_colors_conf",
        "waybar",
        "waybar_matugen",
        "rofi",
        "rofi_matugen",
        "herdr",
    }
)

# --- Ownership rules (check 4): output_kind -> (allowed active, allowed repository)
_OWNERSHIP_RULES: dict[str, tuple[frozenset[ActiveStrategy], frozenset[RepositoryStrategy]]] = {
    "active": (
        frozenset({ActiveStrategy.RESOLVED_ACTIVE_PATH, ActiveStrategy.PINNED_ACTIVE_PATH}),
        frozenset({RepositoryStrategy.NO_VARIANTS}),
    ),
    "repository": (
        frozenset({ActiveStrategy.REPOSITORY_ONLY, ActiveStrategy.NO_ACTIVE_OUTPUT}),
        frozenset({RepositoryStrategy.MODE_VARIANTS, RepositoryStrategy.VERSIONED_VARIANTS}),
    ),
    "active-and-repository": (
        frozenset({ActiveStrategy.RESOLVED_ACTIVE_PATH, ActiveStrategy.PINNED_ACTIVE_PATH}),
        frozenset({RepositoryStrategy.MODE_VARIANTS, RepositoryStrategy.VERSIONED_VARIANTS}),
    ),
}


def representative_palette() -> Palette:
    """Side-effect-free representative palette for conformance rendering.

    Uses the canonical in-memory dark token constants; no file, selector,
    subprocess, installer, or settings access.
    """
    from .palette_tokens import VARIANTS  # noqa: PLC0415

    return dict(VARIANTS["dark"])


def _check_contract_version(reg: RendererRegistration, problems: list[str]) -> None:
    version: int = reg.contract_version  # widen: runtime values may be invalid
    if version != SUPPORTED_CONTRACT_VERSION:
        problems.append(
            f"consumer '{reg.consumer_id}' declares unsupported contract version "
            f"{version!r}; expected {SUPPORTED_CONTRACT_VERSION}"
        )


def _check_modes(reg: RendererRegistration, problems: list[str]) -> None:
    if not reg.modes:
        problems.append(f"consumer '{reg.consumer_id}' declares an empty mode set")
        return
    unsupported = sorted(reg.modes - ALL_MODES)
    if unsupported:
        problems.append(f"consumer '{reg.consumer_id}' declares unsupported modes: {unsupported}")


def _check_ownership(reg: RendererRegistration, problems: list[str]) -> None:
    rules = _OWNERSHIP_RULES.get(reg.output_kind)
    if rules is None:
        problems.append(
            f"consumer '{reg.consumer_id}' declares invalid output kind {reg.output_kind!r}"
        )
        return
    allowed_active, allowed_repository = rules
    if reg.sync.active not in allowed_active:
        problems.append(
            f"consumer '{reg.consumer_id}' output ownership invalid: active strategy "
            f"{reg.sync.active.value!r} incompatible with output kind {reg.output_kind!r}"
        )
    if reg.sync.repository not in allowed_repository:
        problems.append(
            f"consumer '{reg.consumer_id}' output ownership invalid: repository strategy "
            f"{reg.sync.repository.value!r} incompatible with output kind {reg.output_kind!r}"
        )


def _check_strategy_compatibility(reg: RendererRegistration, problems: list[str]) -> None:
    if reg.sync.mutation == MutationStrategy.PROFILE_AWARE_SELECTOR and reg.output_kind not in {
        "active",
        "active-and-repository",
    }:
        problems.append(
            f"consumer '{reg.consumer_id}' strategy conflict: profile-aware selector "
            f"requires active output, got {reg.output_kind!r}"
        )
    if (
        reg.sync.mutation == MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE
        and reg.output_kind == "repository"
    ):
        problems.append(
            f"consumer '{reg.consumer_id}' strategy conflict: symlink-safe active write "
            "requires an active output, got 'repository'"
        )
    if reg.sync.mutation == MutationStrategy.ACTIVE_ONLY_BRIDGE:
        if reg.output_kind != "active":
            problems.append(
                f"consumer '{reg.consumer_id}' strategy conflict: active-only bridge "
                f"requires output kind 'active', got {reg.output_kind!r}"
            )
        if reg.sync.repository != RepositoryStrategy.NO_VARIANTS:
            problems.append(
                f"consumer '{reg.consumer_id}' strategy conflict: active-only bridge "
                f"must not declare repository variants"
            )
    if (
        reg.sync.mutation == MutationStrategy.REPOSITORY_VARIANT_WRITER
        and reg.output_kind != "repository"
    ):
        problems.append(
            f"consumer '{reg.consumer_id}' strategy conflict: repository variant writer "
            f"requires output kind 'repository', got {reg.output_kind!r}"
        )


def _check_renderer(reg: RendererRegistration, palette: Palette, problems: list[str]) -> None:
    # Runtime guards: registrations are declared data and may violate the
    # declared Protocol, so bind to Any before the callable/str checks.
    renderer: Any = reg.renderer
    if not callable(renderer):
        problems.append(f"consumer '{reg.consumer_id}' renderer is not callable")
        return
    for mode in sorted(reg.modes):
        try:
            result: Any = renderer(palette)
        except Exception as exc:
            problems.append(
                f"consumer '{reg.consumer_id}' renderer failed for mode {mode!r}: {exc}"
            )
            continue
        if not isinstance(result, str):
            problems.append(
                f"consumer '{reg.consumer_id}' returned non-string result for mode "
                f"{mode!r}: {type(result).__name__}"
            )


def _check_expected_ids(regs: Sequence[RendererRegistration], problems: list[str]) -> None:
    registered = {r.consumer_id for r in regs}
    missing = sorted(EXPECTED_CONSUMER_IDS - registered)
    extra = sorted(registered - EXPECTED_CONSUMER_IDS)
    if missing:
        problems.append(f"missing consumer ids: {missing}")
    if extra:
        problems.append(f"extra consumer ids: {extra}")


def validate_registry(
    registrations: Sequence[RendererRegistration] | None = None,
) -> list[str]:
    """Validate the full registry; returns a list of problems (empty = valid).

    Runs all design §1 checks before any render/write: unique non-empty IDs,
    contract version, closed mode set, output-ownership validity, port
    conformance (callable + ``str`` for every declared mode), mutation-strategy
    compatibility, and the exact expected-ID bijection. Pure: no files, no
    selectors, no subprocesses, no installer/settings behavior.
    """
    regs: Sequence[RendererRegistration] = (
        tuple(registrations) if registrations is not None else REGISTRATIONS
    )
    problems: list[str] = []

    seen: set[str] = set()
    for reg in regs:
        if not reg.consumer_id:
            problems.append("consumer registration with an empty consumer id")
        if reg.consumer_id in seen:
            problems.append(f"duplicate consumer id '{reg.consumer_id}'")
        seen.add(reg.consumer_id)

    for reg in regs:
        _check_contract_version(reg, problems)
        _check_modes(reg, problems)
        _check_ownership(reg, problems)
        _check_strategy_compatibility(reg, problems)

    palette = representative_palette()
    for reg in regs:
        _check_renderer(reg, palette, problems)

    _check_expected_ids(regs, problems)
    return problems


__all__ = [
    "ALL_MODES",
    "EXPECTED_CONSUMER_IDS",
    "REGISTRATIONS",
    "SUPPORTED_CONTRACT_VERSION",
    "ActiveStrategy",
    "MutationStrategy",
    "OutputKind",
    "Palette",
    "RenderMode",
    "RendererRegistration",
    "RendererStrategy",
    "RepositoryStrategy",
    "SyncDefinition",
    "representative_palette",
    "validate_registry",
]
