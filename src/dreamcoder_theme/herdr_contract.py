"""Version-bound runtime contract selection for Herdr integrations."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

_VERSION_OUTPUT = re.compile(r"herdr[ \t]+(\d+\.\d+\.\d+)", re.IGNORECASE)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class ContractStatus(StrEnum):
    """Outcome of matching runtime output to compatibility evidence."""

    SKIPPED_NOT_INSTALLED = "skipped-not-installed"
    SUPPORTED = "supported"
    UNSUPPORTED_CONTRACT = "unsupported-contract"


@dataclass(frozen=True)
class ProcedureEvidence:
    """Evidence that an operational procedure exists and is unambiguous."""

    available: bool
    unambiguous: bool
    observable: bool = True

    @classmethod
    def from_mapping(cls, mapping: object) -> ProcedureEvidence:
        if not isinstance(mapping, Mapping):
            return cls(available=False, unambiguous=False, observable=False)
        available = mapping.get("available")
        unambiguous = mapping.get("unambiguous")
        observable = mapping.get("observable", True)
        return cls(
            available=available if isinstance(available, bool) else False,
            unambiguous=unambiguous if isinstance(unambiguous, bool) else False,
            observable=observable if isinstance(observable, bool) else False,
        )

    @property
    def is_complete(self) -> bool:
        return self.available and self.unambiguous and self.observable


@dataclass(frozen=True)
class ContractEvidence:
    """Sanitized version-bound evidence required before Herdr can be enabled."""

    profile_id: str
    executable: str
    version: str
    source_identity: str
    source_sha256: str
    default_config_path: str
    config_path_environment: str
    color_representation: str | None
    base_theme_name: str
    allowed_theme_fields: tuple[str, ...]
    allowed_custom_fields: tuple[str, ...]
    allowed_ui_fields: tuple[str, ...]
    candidate_validation: ProcedureEvidence
    server_applicability: ProcedureEvidence
    reload: ProcedureEvidence
    restoration: ProcedureEvidence
    light_base_theme_name: str | None = None

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> ContractEvidence:
        def text(name: str) -> str:
            candidate = mapping.get(name)
            return candidate if isinstance(candidate, str) else ""

        def strings(name: str) -> tuple[str, ...]:
            candidate = mapping.get(name)
            if not isinstance(candidate, list) or not all(
                isinstance(item, str) for item in candidate
            ):
                return ()
            return tuple(candidate)

        color_representation = mapping.get("color_representation")
        return cls(
            profile_id=text("profile_id"),
            executable=text("executable"),
            version=text("version"),
            source_identity=text("source_identity"),
            source_sha256=text("source_sha256"),
            default_config_path=text("default_config_path"),
            config_path_environment=text("config_path_environment"),
            color_representation=(
                color_representation if isinstance(color_representation, str) else None
            ),
            base_theme_name=text("base_theme_name"),
            allowed_theme_fields=strings("allowed_theme_fields"),
            allowed_custom_fields=strings("allowed_custom_fields"),
            allowed_ui_fields=strings("allowed_ui_fields"),
            candidate_validation=ProcedureEvidence.from_mapping(
                mapping.get("candidate_validation")
            ),
            server_applicability=ProcedureEvidence.from_mapping(
                mapping.get("server_applicability")
            ),
            reload=ProcedureEvidence.from_mapping(mapping.get("reload")),
            restoration=ProcedureEvidence.from_mapping(mapping.get("restoration")),
            light_base_theme_name=(
                mapping.get("light_base_theme_name")
                if isinstance(mapping.get("light_base_theme_name"), str)
                else None
            ),
        )

    @property
    def is_complete(self) -> bool:
        """Require every asserted behavior before any profile can be enabled."""
        return all(
            (
                bool(self.profile_id),
                self.executable == "herdr",
                bool(_VERSION_OUTPUT.fullmatch(f"herdr {self.version}")),
                bool(self.source_identity),
                bool(_SHA256.fullmatch(self.source_sha256)),
                bool(self.default_config_path),
                bool(self.config_path_environment),
                bool(self.color_representation),
                bool(self.base_theme_name),
                bool(self.allowed_theme_fields),
                bool(self.allowed_custom_fields),
                bool(self.allowed_ui_fields),
                self.candidate_validation.is_complete,
                self.server_applicability.is_complete,
                self.reload.is_complete,
                self.restoration.is_complete,
            )
        )


@dataclass(frozen=True)
class HerdrProfile:
    """A profile is usable only when all evidence is complete."""

    evidence: ContractEvidence

    @property
    def is_complete(self) -> bool:
        return self.evidence.is_complete


@dataclass(frozen=True)
class ProfileSelection:
    """A non-mutating contract-selection result."""

    status: ContractStatus
    profile: HerdrProfile | None = None


def profile_from_evidence(evidence: ContractEvidence) -> HerdrProfile:
    """Create a profile without allowing callers to override completeness."""
    return HerdrProfile(evidence=evidence)


HERDR_073_EVIDENCE = ContractEvidence(
    profile_id="herdr-0.7.3",
    executable="herdr",
    version="0.7.3",
    source_identity=(
        "Herdr v0.7.3 official configuration reference; source commit "
        "299dd4163a96381ec2d8e5bde13d7ba6d6432373"
    ),
    source_sha256="043ef43ecbabda28465dcff1eec3184518150d567b8b8f20cda9c6c88770641d",
    default_config_path="<HOME>/.config/herdr/config.toml",
    config_path_environment="HERDR_CONFIG_PATH",
    color_representation="hex (#RRGGBB)",
    base_theme_name="catppuccin",
    allowed_theme_fields=("name", "auto_switch", "dark_name", "light_name"),
    allowed_custom_fields=(
        "accent",
        "panel_bg",
        "surface0",
        "surface1",
        "surface_dim",
        "overlay0",
        "overlay1",
        "text",
        "subtext0",
        "mauve",
        "green",
        "yellow",
        "red",
        "blue",
        "teal",
        "peach",
    ),
    allowed_ui_fields=("accent",),
    candidate_validation=ProcedureEvidence(available=True, unambiguous=True),
    server_applicability=ProcedureEvidence(available=True, unambiguous=True),
    reload=ProcedureEvidence(available=True, unambiguous=True, observable=True),
    restoration=ProcedureEvidence(available=True, unambiguous=True),
)
HERDR_073_PROFILE = HerdrProfile(evidence=HERDR_073_EVIDENCE)

# Herdr v0.8.0 installed-binary evidence. Observed exactly: executable `herdr`,
# version `0.8.0`, binary SHA-256
# b872ea7e40fa2cb17e857ac9b62b1bf26db7b403c622f5d2f3f5b35f6e9acd28; default
# config confirms `[ui] pane_scrollbars = false`; config validation is
# `herdr config check`; reload command is `herdr server reload-config`; config
# path `~/.config/herdr/config.toml` overridable by `HERDR_CONFIG_PATH`. No
# fields beyond that evidence are asserted.
HERDR_080_EVIDENCE = ContractEvidence(
    profile_id="herdr-0.8.0",
    executable="herdr",
    version="0.8.0",
    source_identity=(
        "Herdr v0.8.0 installed-binary evidence: default config confirms "
        "[ui] pane_scrollbars = false; validation `herdr config check`; "
        "reload `herdr server reload-config`; HERDR_CONFIG_PATH override"
    ),
    source_sha256="b872ea7e40fa2cb17e857ac9b62b1bf26db7b403c622f5d2f3f5b35f6e9acd28",
    default_config_path="<HOME>/.config/herdr/config.toml",
    config_path_environment="HERDR_CONFIG_PATH",
    color_representation="hex (#RRGGBB)",
    base_theme_name="catppuccin",
    allowed_theme_fields=("name",),
    allowed_custom_fields=(
        "accent",
        "panel_bg",
        "surface0",
        "surface1",
        "surface_dim",
        "overlay0",
        "overlay1",
        "text",
        "subtext0",
        "mauve",
        "green",
        "yellow",
        "red",
        "blue",
        "teal",
        "peach",
    ),
    allowed_ui_fields=("accent", "pane_scrollbars"),
    candidate_validation=ProcedureEvidence(available=True, unambiguous=True),
    server_applicability=ProcedureEvidence(available=True, unambiguous=True),
    reload=ProcedureEvidence(available=True, unambiguous=True, observable=True),
    restoration=ProcedureEvidence(available=True, unambiguous=True),
)
HERDR_080_PROFILE = HerdrProfile(evidence=HERDR_080_EVIDENCE)

# Herdr v0.8.2 source-derived evidence. The official v0.8.2 tag peels to
# 9eb521456ac0d19d3ab3d9d7cea3cca10baa8a4c. source_sha256 is the SHA-256 of
# src/config/theme.rs at that commit; see herdr-contract-evidence.md.
HERDR_082_EVIDENCE = ContractEvidence(
    profile_id="herdr-0.8.2",
    executable="herdr",
    version="0.8.2",
    source_identity=(
        "Herdr v0.8.2 official source commit "
        "9eb521456ac0d19d3ab3d9d7cea3cca10baa8a4c; src/config/theme.rs"
    ),
    source_sha256="9d7bdfdb391d12112e7d4eb1bd3895e50bdb6556255ef75e634094a969684e2d",
    default_config_path="<XDG_CONFIG_HOME>/herdr/config.toml",
    config_path_environment="HERDR_CONFIG_PATH",
    color_representation="hex (#RRGGBB)",
    base_theme_name="catppuccin",
    light_base_theme_name="catppuccin-latte",
    allowed_theme_fields=("name",),
    allowed_custom_fields=(
        "accent",
        "panel_bg",
        "sidebar_bg",
        "active_row_bg",
        "selection_bg",
        "surface0",
        "surface1",
        "surface_dim",
        "overlay0",
        "overlay1",
        "text",
        "subtext0",
        "mauve",
        "green",
        "yellow",
        "red",
        "blue",
        "teal",
        "peach",
    ),
    allowed_ui_fields=("accent", "pane_scrollbars"),
    candidate_validation=ProcedureEvidence(available=True, unambiguous=True),
    server_applicability=ProcedureEvidence(available=True, unambiguous=True),
    reload=ProcedureEvidence(available=True, unambiguous=True, observable=True),
    restoration=ProcedureEvidence(available=True, unambiguous=True),
)
HERDR_082_PROFILE = HerdrProfile(evidence=HERDR_082_EVIDENCE)

# Herdr v0.9.1 installed-binary evidence (`herdr update` from 0.9.0). Observed
# exactly: executable `herdr` at ~/.cargo/bin/herdr, version `0.9.1`, binary
# SHA-256 2a02fed16beb651ef006e1d43f048f652ca4dc58ad053cd2d44450563d5c54b7.
# `herdr config check` rejects unknown keys and theme names in 0.9.1, so the
# field set below is the 0.8.2 set proven accepted by running `config check`
# against each generated variant through HERDR_CONFIG_PATH. Reload command is
# `herdr server reload-config`; see herdr-contract-evidence.md.
HERDR_091_EVIDENCE = ContractEvidence(
    profile_id="herdr-0.9.1",
    executable="herdr",
    version="0.9.1",
    source_identity=(
        "Herdr v0.9.1 installed-binary evidence: `herdr config check` (strict on "
        "unknown keys) accepts every generated field; reload "
        "`herdr server reload-config`; HERDR_CONFIG_PATH override"
    ),
    source_sha256="2a02fed16beb651ef006e1d43f048f652ca4dc58ad053cd2d44450563d5c54b7",
    default_config_path="<HOME>/.config/herdr/config.toml",
    config_path_environment="HERDR_CONFIG_PATH",
    color_representation="hex (#RRGGBB)",
    base_theme_name="catppuccin",
    light_base_theme_name="catppuccin-latte",
    allowed_theme_fields=HERDR_082_EVIDENCE.allowed_theme_fields,
    allowed_custom_fields=HERDR_082_EVIDENCE.allowed_custom_fields,
    allowed_ui_fields=HERDR_082_EVIDENCE.allowed_ui_fields,
    candidate_validation=ProcedureEvidence(available=True, unambiguous=True),
    server_applicability=ProcedureEvidence(available=True, unambiguous=True),
    reload=ProcedureEvidence(available=True, unambiguous=True, observable=True),
    restoration=ProcedureEvidence(available=True, unambiguous=True),
)
HERDR_091_PROFILE = HerdrProfile(evidence=HERDR_091_EVIDENCE)
SUPPORTED_PROFILES = (HERDR_073_PROFILE, HERDR_080_PROFILE, HERDR_082_PROFILE, HERDR_091_PROFILE)


def detect_profile(
    version_output: str | None, *, profiles: tuple[HerdrProfile, ...] = SUPPORTED_PROFILES
) -> ProfileSelection:
    """Match exact version output without guessing malformed runtime output."""
    if version_output is None:
        return ProfileSelection(status=ContractStatus.SKIPPED_NOT_INSTALLED)

    match = _VERSION_OUTPUT.fullmatch(version_output.strip())
    if match is None:
        return ProfileSelection(status=ContractStatus.UNSUPPORTED_CONTRACT)

    version = match.group(1)
    for profile in profiles:
        if profile.is_complete and profile.evidence.version == version:
            return ProfileSelection(status=ContractStatus.SUPPORTED, profile=profile)
    return ProfileSelection(status=ContractStatus.UNSUPPORTED_CONTRACT)
