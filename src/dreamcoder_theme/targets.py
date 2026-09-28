"""Schema-validated, consumer-neutral Dreamcoder rollout target inventory."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import jsonschema
from jsonschema.exceptions import SchemaError

from .renderer_contract import ALL_RENDER_VARIANTS

Classification = Literal["required", "optional", "excluded"]
AUDITED_TARGET_IDS = (
    "antigravity",
    "bat",
    "btop",
    "cava",
    "codex-cli-settings",
    "codex-textmate",
    "delta",
    "doctor-maintenance",
    "dunst",
    "dusk-runtime",
    "firefox",
    "fzf",
    "generated-repository-contract",
    "gentleman-module-plan",
    "ghostty",
    "herdr",
    "hyprland-colors",
    "kitty",
    "ls-colors",
    "ml4w-hook-plan",
    "ml4w-structure",
    "neovim",
    "obsidian",
    "opencode-theme",
    "opencode-tui-selection",
    "pi",
    "rofi-colors",
    "shell-syntax",
    "starship",
    "theme-scheduler",
    "tmux",
    "tmux-kanagawa-bridge",
    "unrelated-application-settings",
    "wallpaper-matugen-hook",
    "warp",
    "waybar-colors",
    "zellij",
)


class ManifestError(ValueError):
    """Raised when a manifest cannot be safely consumed."""


@dataclass(frozen=True)
class Target:
    id: str
    classification: Classification
    reason: str
    contract: Mapping[str, Any]


@dataclass(frozen=True)
class TargetManifest:
    targets: tuple[Target, ...]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(target.id for target in self.targets)

    def require(self, target_id: str) -> Target:
        for target in self.targets:
            if target.id == target_id:
                return target
        raise ManifestError(f"unknown target: {target_id}")


def load_target_manifest(path: Path) -> TargetManifest:
    """Load a manifest without invoking any renderer, installer, or activation adapter."""
    payload = _load_json(path)
    _validate_schema(payload, path.with_name("targets.schema.json"))
    records = payload["targets"]
    if not isinstance(records, list):
        raise ManifestError("targets must be a list")
    _validate_records(records)
    targets = tuple(_target(record) for record in records)
    return TargetManifest(tuple(sorted(targets, key=lambda target: target.id)))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError(f"cannot read manifest {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ManifestError("manifest root must be an object")
    return cast(dict[str, Any], payload)


def _validate_schema(payload: Mapping[str, Any], schema_path: Path) -> None:
    schema = _load_json(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except SchemaError:
        raise ManifestError("invalid manifest schema") from None

    error = next(jsonschema.Draft202012Validator(schema).iter_errors(payload), None)
    if error is not None:
        location = ".".join(str(part) for part in error.absolute_path)
        raise ManifestError(f"schema validation failed at {location or 'root'}: {error.message}")


def _validate_records(records: list[Any]) -> None:
    ids: set[str] = set()
    outputs: set[str] = set()
    selectors: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ManifestError("target record must be an object")
        target_id = record["id"]
        if target_id in ids:
            raise ManifestError(f"duplicate target id: {target_id}")
        ids.add(target_id)
        render = record.get("render")
        if isinstance(render, dict):
            modes = set(render["modes"])
            if "dusk" in modes:
                raise ManifestError(f"dusk is not a runtime render mode: {target_id}")
            if modes != set(ALL_RENDER_VARIANTS):
                raise ManifestError(f"render variants must be dark and light: {target_id}")
            for output in render["repository_outputs"].values():
                if output in outputs:
                    raise ManifestError(f"duplicate repository output: {output}")
                outputs.add(output)
        selector = record["activation"]["selector"]
        if selector in selectors:
            raise ManifestError(f"duplicate selector ownership: {selector}")
        selectors.add(selector)
    missing = sorted(set(AUDITED_TARGET_IDS) - ids)
    extra = sorted(ids - set(AUDITED_TARGET_IDS))
    if missing or extra:
        details = [
            f"missing audited targets: {', '.join(missing)}" if missing else "",
            f"unknown audited targets: {', '.join(extra)}" if extra else "",
        ]
        raise ManifestError("; ".join(detail for detail in details if detail))


def _target(record: Mapping[str, Any]) -> Target:
    return Target(
        record["id"], cast(Classification, record["classification"]), record["reason"], record
    )
