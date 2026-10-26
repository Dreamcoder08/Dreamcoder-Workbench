"""Resolve explicitly configured agent colors for OpenCode's hex-only TUI.

OpenCode 2.1.4 createAgent.color passes agent.color directly to RGBA.fromHex,
not through the theme-name resolver. Use the renderer as the role authority.
Only gentle-orchestrator (primary) and dangerous-gentleman (accent) recognize
previous canonical hex: a manual identical hex on these IDs is unavoidably
indistinguishable from managed output. Other agents' hex values are never owned.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

from .palette_tokens import VARIANTS
from .renderers_opencode import opencode_content
from .writers import write_if_changed

MANAGED_ROLES = {"gentle-orchestrator": "primary", "dangerous-gentleman": "accent"}
_HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")


def resolve_agent_color(
    value: Any,
    agent_id: str,
    theme: Mapping[str, str],
    prior_themes: list[Mapping[str, str]],
) -> Any:
    """Pure resolution; only explicit role names or known managed hex opt in."""
    if not isinstance(value, str):
        return value
    resolved = theme.get(value)
    if isinstance(resolved, str) and _HEX.fullmatch(resolved):
        return resolved
    role = MANAGED_ROLES.get(agent_id)
    if role and _HEX.fullmatch(value):
        prior_values = {prior[role].lower() for prior in prior_themes}
        if value.lower() in prior_values:
            return theme[role]
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate keys rather than silently lose user configuration."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def update_opencode_agent_colors(
    path: Path,
    active: dict[str, str],
    variants: Mapping[str, dict[str, str]] = VARIANTS,
) -> bool:
    """Patch only agent color fields in an existing valid JSON object.

    False means missing, rejected, or unchanged; invalid documents are never
    rewritten. Prefer a unique value patch, verified against the intended JSON;
    ambiguous formatting falls back to serialization without semantic changes.
    Canonical defaults plus loaded variants recognize prior base-mode output.
    """
    try:
        original = path.read_text()
        data = json.loads(original, object_pairs_hook=_unique_object)
    except (OSError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    agents = data.get("agent", {})
    if not isinstance(agents, dict) or any(not isinstance(a, dict) for a in agents.values()):
        return False

    theme = json.loads(opencode_content(active, transparent_background=True))["theme"]
    prior_themes = [
        json.loads(opencode_content(palette, transparent_background=True))["theme"]
        for palette in (*VARIANTS.values(), *variants.values())
    ]
    intended = deepcopy(data)
    replacements = []
    for agent_id, agent in agents.items():
        if "color" not in agent:
            continue
        old = agent["color"]
        new = resolve_agent_color(old, agent_id, theme, prior_themes)
        if new != old:
            intended["agent"][agent_id]["color"] = new
            replacements.append((old, new))
    if not replacements:
        return False

    patched = original
    for old, new in replacements:
        pattern = re.compile(r'("color"\s*:\s*)' + re.escape(json.dumps(old)))
        if len(pattern.findall(patched)) != 1:
            patched = json.dumps(intended, indent=2)
            break

        def replace_color(match: re.Match[str]) -> str:
            return match[1] + json.dumps(new)

        patched = pattern.sub(replace_color, patched)
    # A text match is not a parser: ensure prompts and all unrelated fields survive.
    try:
        verified = json.loads(patched, object_pairs_hook=_unique_object)
    except ValueError:
        verified = None
    if verified != intended:
        patched = json.dumps(intended, indent=2)
    return write_if_changed(path, patched)
