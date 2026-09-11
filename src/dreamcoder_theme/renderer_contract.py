"""Formal renderer port and immutable registration model.

Hexagonal-architecture-v2 ADR-001: the primary and ONLY renderer contract is a
typed callable ``Protocol`` compatible with ``dict[str, str] -> str``. Existing
function-based leaf renderers conform structurally without a class hierarchy;
special consumers are exposed through small context-binding adapters that
present the same one-palette/one-string port. ``Mapping[str, str]`` may be used
internally for immutability and type safety, but every public caller and leaf
renderer stays compatible with the established ``dict[str, str] -> str`` shape.

This module holds the model types only. ``renderer_registry.py`` owns the
deterministic assembly, validation, and the expected consumer-ID set; leaf
renderer modules import the model from here to declare adjacent registrations
without circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal, Protocol, runtime_checkable

# Semantic palette mapping accepted by every renderer. ``dict`` keeps existing
# leaf renderers and callers compatible; adapters may accept Mapping internally.
Palette = dict[str, str]

# Canonical authored themes are distinct from runtime render variants. Night is
# derived from Dark by a render profile; it is never a fourth canonical mode.
CanonicalMode = Literal["light", "dusk", "dark"]
CANONICAL_MODES: frozenset[CanonicalMode] = frozenset({"light", "dusk", "dark"})

RenderVariant = Literal["dark", "light", "night"]
# Backward-compatible registration type name: registrations describe generated
# runtime variants, not the canonical token schema.
RenderMode = RenderVariant

# Declared renderer contract versions. Only version 1 exists today; validation
# rejects any other value.
SupportedContractVersion = Literal[1]
SUPPORTED_CONTRACT_VERSION: SupportedContractVersion = 1

# Output ownership: where the consumer's rendered content is delivered.
OutputKind = Literal["active", "repository", "active-and-repository"]

# Closed set of generated runtime variants accepted by registrations.
ALL_RENDER_VARIANTS: frozenset[RenderVariant] = frozenset({"dark", "light", "night"})
ALL_MODES = ALL_RENDER_VARIANTS


@runtime_checkable
class Renderer(Protocol):
    """The single renderer port: one palette mapping in, one string out.

    ``palette`` is positional-only so the port shape stays exactly
    ``render(palette) -> str``; no keyword context leaks through the port.
    """

    def __call__(self, palette: Palette, /) -> str: ...


# ---------------------------------------------------------------------------
# Closed strategy types (ADR-002). Each is a closed enum variant, not an open
# callback bag: specialized behavior is bound through declared strategies, and
# validation checks strategy/ownership compatibility before any render/write.
# ---------------------------------------------------------------------------


class RendererStrategy(StrEnum):
    """How the consumer's content is produced from the palette."""

    DIRECT_CONTENT = "direct_content"
    TRANSPARENT_OPENCODE = "transparent_opencode"
    NVIM_DISPATCHER = "nvim_dispatcher"
    NAMED_ZELLIJ = "named_zellij"
    VERSIONED_HERDR = "versioned_herdr"


class ActiveStrategy(StrEnum):
    """How (and whether) the consumer has live active output."""

    NO_ACTIVE_OUTPUT = "no_active_output"
    RESOLVED_ACTIVE_PATH = "resolved_active_path"
    PINNED_ACTIVE_PATH = "pinned_active_path"
    REPOSITORY_ONLY = "repository_only"


class RepositoryStrategy(StrEnum):
    """How repository output variants are produced."""

    NO_VARIANTS = "no_variants"
    MODE_VARIANTS = "mode_variants"
    VERSIONED_VARIANTS = "versioned_variants"


class MutationStrategy(StrEnum):
    """The commit-phase writer/selector strategy for the consumer."""

    WRITE_IF_CHANGED = "write_if_changed"
    SYMLINK_SAFE_ACTIVE_WRITE = "symlink_safe_active_write"
    PROFILE_AWARE_SELECTOR = "profile_aware_selector"
    ACTIVE_ONLY_BRIDGE = "active_only_bridge"
    REPOSITORY_VARIANT_WRITER = "repository_variant_writer"


@dataclass(frozen=True, slots=True)
class SyncDefinition:
    """Closed strategy record for one consumer (paths land with Phase 2 resolvers)."""

    renderer: RendererStrategy
    active: ActiveStrategy
    repository: RepositoryStrategy
    mutation: MutationStrategy


@dataclass(frozen=True, slots=True)
class RendererRegistration:
    """Immutable declaration of one active renderer consumer.

    Fields are normative (design §1, ADR-001): a unique active consumer ID, the
    renderer adapter implementing the formal port, a contract version, the
    closed supported mode set, output ownership, sync strategy metadata, and a
    human-readable summary label.
    """

    consumer_id: str
    renderer: Renderer
    contract_version: SupportedContractVersion
    modes: frozenset[RenderMode]
    output_kind: OutputKind
    sync: SyncDefinition
    summary_label: str = field(default="")
