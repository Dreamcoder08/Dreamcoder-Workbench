"""Persistent settings store for Dreamcoder Control Center."""

from __future__ import annotations

from typing import Any

from .core import read_json, settings_path, write_json

SETTINGS_SCHEMA: dict[str, dict[str, Any]] = {
    "terminal.default_mode": {
        "type": "string",
        "enum": ["light", "dark"],
        "default": "light",
        "description": "Default terminal theme mode.",
    },
    "profile.active": {
        "type": "string",
        "default": "default",
        "description": "Active machine profile name.",
    },
    "motion.active": {
        "type": "string",
        "enum": ["battery", "balanced", "fluid", "cinematic"],
        "default": "balanced",
        "description": "Active motion preset.",
    },
}


def settings_schema() -> dict[str, Any]:
    return {"schema": "dreamcoder.settings-schema.v1", "settings": SETTINGS_SCHEMA}


def flatten_settings(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_settings(value, path))
        else:
            flat[path] = value
    return flat


def validate_setting_value(key: str, value: Any) -> list[str]:
    spec = SETTINGS_SCHEMA.get(key)
    if spec is None:
        return []
    errors = []
    if spec.get("type") == "string" and not isinstance(value, str):
        errors.append(f"{key} must be a string")
    if "enum" in spec and value not in spec["enum"]:
        allowed = ", ".join(spec["enum"])
        errors.append(f"{key} must be one of: {allowed}")
    return errors


def validate_settings(data: dict[str, Any] | None = None) -> dict[str, Any]:
    source = settings_get() if data is None else data
    flat = flatten_settings(source) if isinstance(source, dict) else {}
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    for key, value in flat.items():
        if key not in SETTINGS_SCHEMA:
            warnings.append(
                {"key": key, "message": "Unknown setting; preserved for forward compatibility"}
            )
            continue
        for message in validate_setting_value(key, value):
            errors.append({"key": key, "message": message})
    return {
        "schema": "dreamcoder.settings-validation.v1",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def set_nested_setting(key: str, value: Any) -> None:
    data = read_json(settings_path(), {})
    cursor = data
    parts = key.split(".")
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[parts[-1]] = value
    write_json(settings_path(), data)


def settings_get(key: str | None = None) -> Any:
    data = read_json(settings_path(), {})
    if key is None:
        return data
    value: Any = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def settings_set(key: str, value: str) -> dict[str, Any]:
    errors = validate_setting_value(key, value)
    if errors:
        raise ValueError("; ".join(errors))
    set_nested_setting(key, value)
    return {"key": key, "value": value, "path": str(settings_path())}
