"""Pure evaluation of the Dreamcoder terminal-first design-system contract."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

from .renderers_ghostty_warp import ghostty_content, warp_content
from .renderers_kitty import kitty_content
from .renderers_opencode import opencode_content
from .renderers_starship import starship_content
from .renderers_tmux import tmux_content

Severity = Literal["error", "warning", "info"]
Renderer = Any


@dataclass(frozen=True)
class Finding:
    """One stable, machine-readable contract evaluation result."""

    code: str
    severity: Severity
    mode: str | None
    target: str | None
    role: str | None
    artifact: str | None
    measured: float | str | None
    required: float | str | None
    message: str


@dataclass(frozen=True)
class RenderedTarget:
    """Renderer output normalized to declared target field names."""

    target: str
    mode: str
    fields: Mapping[str, str]
    content: str


@dataclass(frozen=True)
class ResolvedRole:
    """A role value and its canonical provenance chain."""

    role: str
    value: str
    source: str
    chain: tuple[str, ...]


_RENDERERS: dict[str, Renderer] = {
    "kitty_content": kitty_content,
    "ghostty_content": ghostty_content,
    "warp_content": warp_content,
    "starship_content": starship_content,
    "tmux_content": tmux_content,
    "opencode_content": opencode_content,
}

# Precompiled at module level: every pattern is a static literal, so no
# regex is ever built from dynamic (potentially user-controlled) input.
_TMUX_FIELD_PATTERNS: dict[str, re.Pattern[str]] = {
    "status-style.bg": re.compile(r'status-style "bg=([^,"]+)'),
    "message-style.bg": re.compile(r'message-style "fg=[^,]+,bg=([^,"]+)'),
    "status-left.text": re.compile(r'status-left "#\[fg=([^,\]]+),bold\]'),
    "status-left.muted": re.compile(r'status-left ".*?#S\s+#\[fg=([^\]]+)\]'),
    "window-status-current-style": re.compile(r'window-status-current-style "fg=([^,"]+)'),
    "pane-active-border-style": re.compile(r'pane-active-border-style "fg=([^,"]+)'),
    "window-status-bell-style": re.compile(r'window-status-bell-style "fg=[^,]+,bg=([^,"]+)'),
    "success-colour": re.compile(r'@dreamcoder-success-colour "([^"]+)'),
}


def load_contract(path: Path) -> dict[str, Any]:
    """Load author-owned policy without resolving any user-home paths."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"cannot read design-system contract {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid design-system contract {path}: {exc}") from exc
    return cast(dict[str, Any], document)


def load_tokens(path: Path) -> dict[str, Any]:
    """Load canonical tokens without generating or writing any output."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"cannot read canonical tokens {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid canonical tokens {path}: {exc}") from exc
    return cast(dict[str, Any], document)


def resolve_role(
    contract: Mapping[str, Any], tokens: Mapping[str, Any], mode: str, role: str
) -> ResolvedRole:
    """Resolve one role while rejecting unknown references and role cycles."""
    roles = contract["roles"]
    if role not in roles:
        raise ValueError(f"unknown role: {role}")

    chain: list[str] = []

    def resolve(name: str) -> tuple[str, str]:
        if name in chain:
            raise ValueError(f"cyclic role derivation: {' -> '.join((*chain, name))}")
        if name not in roles:
            raise ValueError(f"unknown role: {name}")
        chain.append(name)
        definition = roles[name]
        parent = definition.get("parent")
        if parent:
            resolve(parent)
        derivation = definition.get("derivation")
        if derivation is not None:
            if not isinstance(derivation, Mapping):
                raise ValueError(f"invalid derivation for role: {name}")
            inputs = derivation.get("inputs")
            if not isinstance(inputs, list) or not inputs:
                raise ValueError(f"derivation requires inputs: {name}")
            input_values = [resolve(input_name) for input_name in inputs]
            if derivation.get("id") != "alias":
                raise ValueError(f"unknown derivation: {derivation.get('id')}")
            value, _ = input_values[0]
            return value, f"derivation:alias({','.join(inputs)})"
        source = definition.get("source")
        if not isinstance(source, str):
            raise ValueError(f"role requires canonical source or derivation: {name}")
        source = source.replace("{mode}", mode)
        resolved: Any = tokens
        for part in source.split("."):
            if not isinstance(resolved, Mapping) or part not in resolved:
                raise ValueError(f"missing canonical role source: {source}")
            resolved = resolved[part]
        if not isinstance(resolved, str):
            raise ValueError(f"canonical role is not a color string: {source}")
        return resolved, source

    value, source = resolve(role)
    return ResolvedRole(role=role, value=value, source=source, chain=tuple(chain))


def render_target(
    target: str, mode: str, palette: Mapping[str, str], target_contract: Mapping[str, Any]
) -> RenderedTarget:
    """Invoke only a declared renderer and normalize its existing output."""
    renderer_name = target_contract["renderer"]
    try:
        content = _RENDERERS[renderer_name](dict(palette))
    except KeyError as error:
        raise ValueError(f"unknown renderer callable: {renderer_name}") from error
    raw_fields = _parse_renderer_output(target, content)
    fields = {
        role: raw_fields[field]
        for role, field in target_contract["fields"].items()
        if field in raw_fields
    }
    return RenderedTarget(target=target, mode=mode, fields=fields, content=content)


def evaluate_contract(  # noqa: PLR0912
    contract: Mapping[str, Any], tokens: Mapping[str, Any]
) -> list[Finding]:
    """Evaluate role provenance, three-mode parity, and matrix coverage in memory."""
    findings: list[Finding] = []
    expected_modes = tuple(contract["modes"])
    canonical_modes = tokens.get("modes", {})
    for mode in expected_modes:
        if mode not in canonical_modes:
            findings.append(
                _finding("MISSING_MODE", mode=mode, message=f"canonical mode '{mode}' is missing")
            )
            continue
        for role in contract["roles"]:
            try:
                resolve_role(contract, tokens, mode, role)
            except ValueError as error:
                findings.append(
                    _finding("ROLE_RESOLUTION", mode=mode, role=role, message=str(error))
                )

    rendered: dict[tuple[str, str], RenderedTarget] = {}
    for target, target_contract in contract["targets"].items():
        declared_modes = tuple(target_contract.get("modes", ()))
        for mode in expected_modes:
            if mode not in declared_modes:
                findings.append(
                    _finding(
                        "MISSING_TARGET_MODE",
                        mode=mode,
                        target=target,
                        message=f"target '{target}' does not declare mode '{mode}'",
                    )
                )
                continue
            palette = canonical_modes.get(mode)
            if not isinstance(palette, Mapping):
                continue
            try:
                rendered[(target, mode)] = render_target(target, mode, palette, target_contract)
            except (KeyError, ValueError, json.JSONDecodeError) as error:
                findings.append(
                    _finding("RENDER_FAILURE", mode=mode, target=target, message=str(error))
                )

    for target, target_contract in contract["targets"].items():
        for mode in expected_modes:
            output = rendered.get((target, mode))
            if output is None:
                continue
            mappings = target_contract.get("mappings", {})
            for role, rendered_value in output.fields.items():
                expected_role = mappings.get(role, role)
                if expected_role.startswith("renderer:"):
                    continue
                try:
                    expected = resolve_role(contract, tokens, mode, expected_role)
                except ValueError as error:
                    findings.append(
                        _finding(
                            "SEMANTIC_PROVENANCE_INVALID",
                            mode=mode,
                            target=target,
                            role=role,
                            message=str(error),
                        )
                    )
                    continue
                if rendered_value != expected.value:
                    findings.append(
                        _finding(
                            "SEMANTIC_PROVENANCE_MISMATCH",
                            mode=mode,
                            target=target,
                            role=role,
                            measured=rendered_value,
                            required=expected.value,
                            message=(
                                f"target '{target}' field for role '{role}' does not match "
                                f"canonical role '{expected_role}'"
                            ),
                        )
                    )
            for role in target_contract["required_roles"]:
                if role in output.fields:
                    continue
                mapped_to = mappings.get(role)
                if mapped_to and mapped_to in output.fields:
                    continue
                findings.append(
                    _finding(
                        "PARITY_MISSING_FIELD",
                        mode=mode,
                        target=target,
                        role=role,
                        message=(
                            f"target '{target}' omits required role '{role}'; "
                            "declare a field or explicit semantic mapping"
                        ),
                    )
                )

    for row in contract["matrix"]:
        for target in row["targets"]:
            target_contract = contract["targets"].get(target)
            if target_contract is None:
                findings.append(
                    _finding(
                        "MATRIX_UNKNOWN_TARGET", target=target, role=row["id"], message=row["id"]
                    )
                )
                continue
            supported = set(target_contract["required_roles"]) | set(
                target_contract.get("mappings", {})
            )
            for role in (row["foreground"], row["background"]):
                if role not in supported:
                    findings.append(
                        _finding(
                            "MATRIX_MISSING_ROLE",
                            target=target,
                            role=role,
                            required=row["id"],
                            message=f"matrix row '{row['id']}' requires role '{role}' for target '{target}'",
                        )
                    )
    return sorted(findings, key=_finding_sort_key)


def _finding(
    code: str,
    severity: Severity = "error",
    mode: str | None = None,
    target: str | None = None,
    role: str | None = None,
    artifact: str | None = None,
    measured: float | str | None = None,
    required: float | str | None = None,
    message: str = "",
) -> Finding:
    return Finding(code, severity, mode, target, role, artifact, measured, required, message)


def _finding_sort_key(finding: Finding) -> tuple[str, str, str, str, str]:
    return (
        finding.code,
        finding.target or "",
        finding.mode or "",
        finding.role or "",
        finding.artifact or "",
    )


def _parse_renderer_output(target: str, content: str) -> dict[str, str]:  # noqa: PLR0912
    if target == "opencode":
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"renderer {target!r} produced invalid JSON: {exc}") from exc
        return {f"theme.{key}": value for key, value in parsed["theme"].items()}
    if target == "kitty":
        return _space_assignments(content)
    if target == "ghostty":
        fields = _equals_assignments(content)
        for line in content.splitlines():
            if line.startswith("palette = "):
                number, value = line.removeprefix("palette = ").split("=", 1)
                fields[f"palette.{number}"] = value
        return fields
    if target == "warp":
        fields = _colon_assignments(content)
        section = ""
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.endswith(":"):
                section = stripped[:-1]
            elif ":" in stripped and section in {"normal", "bright"}:
                key, value = stripped.split(":", 1)
                fields[f"terminal_colors.{section}.{key}"] = value.strip().strip("'")
        return fields
    if target == "starship":
        star_fields: dict[str, str] = {}
        in_palette = False
        for line in content.splitlines():
            if line == "[palettes.dreamcoder]":
                in_palette = True
                continue
            if in_palette and line.startswith("["):
                break
            if in_palette and " = " in line:
                key, value = line.split(" = ", 1)
                star_fields[f"palette.{key}"] = value.strip().strip('"')
        return star_fields
    if target == "tmux":
        return _tmux_fields(content)
    raise ValueError(f"no adapter for target: {target}")


def _space_assignments(content: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in content.splitlines():
        parts = line.split()
        if len(parts) >= 2 and not line.lstrip().startswith("#"):
            fields[parts[0]] = parts[-1]
    return fields


def _equals_assignments(content: str) -> dict[str, str]:
    return {
        key.strip(): value.strip()
        for line in content.splitlines()
        if " = " in line and not line.lstrip().startswith("#")
        for key, value in [line.split(" = ", 1)]
    }


def _colon_assignments(content: str) -> dict[str, str]:
    return {
        key.strip(): value.strip().strip("'")
        for line in content.splitlines()
        if ":" in line and not line.lstrip().startswith("#")
        for key, value in [line.strip().split(":", 1)]
    }


def _tmux_fields(content: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for name, pattern in _TMUX_FIELD_PATTERNS.items():
        match = pattern.search(content)
        if match:
            fields[name] = match.group(1)
    return fields
