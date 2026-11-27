"""Resolve the primitive tier (OKLCH) into the semantic tier (hex per mode).

``tokens.json`` keeps ``modes.<mode>`` as flat hex so every existing consumer
reads it unchanged; ``primitives`` and ``bindings`` say where each semantic
value comes from, and the health gate proves the two never drift apart.
"""

from __future__ import annotations

from typing import Any

from .color_space import oklch_to_hex, parse_oklch


class TierError(ValueError):
    """A binding names a missing primitive, or a primitive is out of range."""


def resolve_mode(tokens: dict[str, Any], mode: str) -> dict[str, str]:
    primitives: dict[str, str] = tokens.get("primitives", {}).get(mode, {})
    bindings: dict[str, str] = tokens.get("bindings", {}).get(mode, {})
    resolved: dict[str, str] = {}
    for key, name in bindings.items():
        if name not in primitives:
            raise TierError(f"{mode}: {key} -> {name} is not a primitive")
        try:
            resolved[key] = oklch_to_hex(*parse_oklch(primitives[name]))
        except ValueError as error:
            raise TierError(f"{mode}: primitive {name}: {error}") from error
    return resolved


def drift(tokens: dict[str, Any]) -> list[str]:
    """Semantic values that disagree with their bound primitive."""
    problems: list[str] = []
    for mode in tokens.get("bindings", {}):
        for key, value in resolve_mode(tokens, mode).items():
            actual = str(tokens["modes"][mode].get(key, "")).lower()
            if actual != value:
                problems.append(f"TIER_DRIFT: {mode}.{key} is {actual}, primitive gives {value}")
    return problems
