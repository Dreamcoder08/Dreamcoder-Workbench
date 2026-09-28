"""Pure, profile-gated renderer for repository-owned Herdr variants."""

from __future__ import annotations

import re

from .herdr_contract import SUPPORTED_PROFILES, HerdrProfile

_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")
_PALETTE_UI_FIELDS: dict[str, str] = {}
_UI_FIELD_RHS = {"pane_scrollbars": "false", "accent": '"#6FA0AF"'}
_KEYS_LINES = (
    'prefix = "ctrl+a"',
    'previous_agent = "prefix+alt+k"',
    'next_agent = "prefix+alt+j"',
    'focus_agent = "prefix+ctrl+1..9"',
)
_TOKEN_MAPPING = (
    ("accent", "accent"),
    ("panel_bg", "bg"),
    ("surface0", "surface0"),
    ("surface1", "surface1"),
    ("surface_dim", "bg_soft"),
    ("overlay0", "border_ui"),
    ("overlay1", "subtle"),
    ("text", "text"),
    ("subtext0", "muted"),
    ("mauve", "mauve"),
    ("green", "success"),
    ("yellow", "warning"),
    ("red", "error"),
    ("blue", "info"),
    ("teal", "focus"),
    ("peach", "accent_2"),
)
_OPTIONAL_TOKEN_MAPPING = (
    ("sidebar_bg", "bg"),
    ("active_row_bg", "surface0"),
    ("selection_bg", "selection"),
)


class HerdrContractUnavailableError(RuntimeError):
    """Raised when code attempts Herdr rendering without verified evidence."""


class HerdrModeError(Exception):
    """Raised when a Herdr variant mode is not the supported dark or light set."""


def herdr_content(profile: HerdrProfile, mode: str, palette: dict[str, str]) -> str:
    """Render one static Light or Dark variant without touching active configuration."""
    if not profile.is_complete:
        raise HerdrContractUnavailableError("Herdr color rendering requires a complete profile")
    if mode not in {"dark", "light"}:
        raise HerdrModeError("Herdr supports only dark and light variants")

    evidence = profile.evidence
    if "name" not in evidence.allowed_theme_fields:
        raise HerdrContractUnavailableError("Herdr profile does not allow theme.name")

    custom_lines: list[str] = []
    mappings = _TOKEN_MAPPING + tuple(
        mapping
        for mapping in _OPTIONAL_TOKEN_MAPPING
        if mapping[0] in evidence.allowed_custom_fields
    )
    if {field for field, _token in mappings} != set(evidence.allowed_custom_fields):
        raise HerdrContractUnavailableError("Herdr profile requests unsupported custom fields")
    for field, token in mappings:
        color = palette.get(token)
        if not isinstance(color, str) or _HEX_COLOR.fullmatch(color) is None:
            raise HerdrContractUnavailableError(
                f"Herdr palette token {token!r} must be a #RRGGBB color"
            )
        custom_lines.append(f'{field} = "{color}"')

    base_theme = (
        evidence.light_base_theme_name
        if mode == "light" and evidence.light_base_theme_name
        else evidence.base_theme_name
    )

    ui_lines: list[str] = []
    for field in evidence.allowed_ui_fields:
        mapped_token = _PALETTE_UI_FIELDS.get(field)
        rhs = f'"{palette[mapped_token]}"' if mapped_token is not None else _UI_FIELD_RHS.get(field)
        if rhs is None:
            raise HerdrContractUnavailableError(
                f"Herdr profile requests unsupported [ui] field {field!r}"
            )
        ui_lines.append(f"{field} = {rhs}")

    return "\n".join(
        (
            "# Managed by Dreamcoder; repository variant only.",
            "[theme]",
            f'name = "{base_theme}"',
            "",
            "[theme.custom]",
            *custom_lines,
            "",
            "[ui]",
            *ui_lines,
            "",
            "[keys]",
            *_KEYS_LINES,
            "",
        )
    )


def herdr_token_mapping() -> tuple[tuple[str, str], ...]:
    """Expose the fixed documented-field to canonical-token mapping for tests."""
    return _TOKEN_MAPPING


def herdr_ui_field_rhs() -> dict[str, str]:
    """Expose static RHS values and palette token references for tests."""
    return {**_UI_FIELD_RHS, **_PALETTE_UI_FIELDS}


from .renderer_adapters import VersionedHerdrAdapter  # noqa: E402
from .renderer_contract import (  # noqa: E402
    ActiveStrategy,
    MutationStrategy,
    RendererRegistration,
    RendererStrategy,
    RepositoryStrategy,
    SyncDefinition,
)

# The registry intentionally retains one entry per consumer even though
# sync_herdr_repo_variants() generates every complete supported profile. It is
# a conformance layer, so bind one live representative and describe the full
# profile set instead of hardcoding one historical version.
_REPRESENTATIVE_PROFILE = next(
    profile for profile in SUPPORTED_PROFILES if profile and profile.is_complete
)
_SUPPORTED_PROFILE_VERSIONS = ", ".join(
    profile.evidence.version for profile in SUPPORTED_PROFILES if profile and profile.is_complete
)

REGISTRATIONS: tuple[RendererRegistration, ...] = (
    RendererRegistration(
        consumer_id="herdr",
        renderer=VersionedHerdrAdapter(_REPRESENTATIVE_PROFILE, "dark"),
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.VERSIONED_HERDR,
            active=ActiveStrategy.REPOSITORY_ONLY,
            repository=RepositoryStrategy.VERSIONED_VARIANTS,
            mutation=MutationStrategy.REPOSITORY_VARIANT_WRITER,
        ),
        summary_label=f"Herdr repository profiles ({_SUPPORTED_PROFILE_VERSIONS})",
    ),
)
