"""Resolve glow effects from the semantic tokens they decorate.

A glow is a soft halo in the colour of a token (focus ring, brand, error). Its
geometry (blur, spread, alpha) lives once in ``components.glow``; its colour is
read from the mode's own semantic token, so a retuned pigment moves its glow
with it. Only a mode that stores ``effects`` resolves any; others get nothing.
``modes.<mode>.effects`` keeps the resolved strings for the consumers that read
the token file directly, and :func:`drift` proves they never diverge.
"""

from __future__ import annotations

from typing import Any

from .token_tiers import TierError


def _source(mode_tokens: dict[str, Any], mode: str, path: str) -> tuple[int, int, int]:
    node: Any = mode_tokens
    for step in path.split("."):
        if not isinstance(node, dict) or step not in node:
            raise TierError(f"{mode}: glow source {path} is not a token")
        node = node[step]
    text = str(node)
    if len(text) != 7 or not text.startswith("#"):
        raise TierError(f"{mode}: glow source {path} is {text!r}, not #RRGGBB")
    try:
        return int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16)
    except ValueError as error:
        raise TierError(f"{mode}: glow source {path} is {text!r}, not #RRGGBB") from error


def resolve_effects(tokens: dict[str, Any], mode: str) -> dict[str, str]:
    mode_tokens: dict[str, Any] = tokens.get("modes", {}).get(mode, {})
    if "effects" not in mode_tokens:
        return {}
    resolved: dict[str, str] = {}
    for name, spec in tokens.get("components", {}).get("glow", {}).items():
        red, green, blue = _source(mode_tokens, mode, spec["source"])
        blur, spread = int(spec["blur"]), int(spec["spread"])
        offsets = ["0", "0", f"{blur}px" if blur else "0"]
        if spread:
            offsets.append(f"{spread}px")
        colour = f"rgba({red}, {green}, {blue}, {float(spec['alpha']):.2f})"
        resolved[f"glow_{name}"] = f"{' '.join(offsets)} {colour}"
    return resolved


def drift(tokens: dict[str, Any]) -> list[str]:
    """Stored effects that disagree with the glows their source tokens give."""
    problems: list[str] = []
    for mode, mode_tokens in tokens.get("modes", {}).items():
        stored: dict[str, str] = mode_tokens.get("effects", {})
        for key, value in resolve_effects(tokens, mode).items():
            if stored.get(key) != value:
                problems.append(
                    f"EFFECTS_DRIFT: {mode}.{key} is {stored.get(key)!r}, tokens give {value!r}"
                )
    return problems
