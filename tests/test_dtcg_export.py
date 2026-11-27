"""DTCG 2025.10 export: `scripts/export-dtcg.py` and the checked-in generated file.

Spec: odd/tasks/dreamcoder-light-coherence.md, T15 (S2, S4). Every test goes through the
public command line; the vendored official schema validates offline.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from dreamcoder_theme.color_space import hex_to_unit_rgb, oklch_to_hex, parse_oklch
from dreamcoder_theme.elevation import resolve_components

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/export-dtcg.py"
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
SCHEMA = ROOT / "tests/fixtures/dtcg/format-2025.10.json"
GENERATED = ROOT / "docs/generated/dreamcoder.tokens.json"
SCHEMA_URL = "https://www.designtokens.org/schemas/2025.10/format.json"

HEX = re.compile(r"^#[0-9a-f]{6}$")
RGBA = re.compile(r"^rgba\((\d+), (\d+), (\d+), ([0-9.]+)\)$")


def run_export(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


@pytest.fixture(scope="module")
def exported(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    out = tmp_path_factory.mktemp("dtcg") / "tokens.json"
    result = run_export("--output", str(out))
    assert result.returncode == 0, result.stderr
    return json.loads(out.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def source() -> dict[str, Any]:
    return json.loads(TOKENS.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def validator() -> jsonschema.Draft7Validator:
    return jsonschema.Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def walk(node: dict[str, Any], path: tuple[str, ...] = ()) -> dict[tuple[str, ...], dict[str, Any]]:
    """Every token (an object with `$value`) keyed by its path."""
    found: dict[tuple[str, ...], dict[str, Any]] = {}
    for key, child in node.items():
        if key.startswith("$") or not isinstance(child, dict):
            continue
        if "$value" in child:
            found[(*path, key)] = child
        else:
            found.update(walk(child, (*path, key)))
    return found


def get(doc: dict[str, Any], dotted: str) -> dict[str, Any]:
    node: Any = doc
    for part in dotted.split("."):
        node = node[part]
    return node  # type: ignore[no-any-return]


def resolve(doc: dict[str, Any], token: dict[str, Any]) -> dict[str, Any]:
    """Follow `{a.b.c}` aliases to the token that holds a concrete value."""
    seen = 0
    while isinstance(token["$value"], str) and token["$value"].startswith("{"):
        token = get(doc, token["$value"][1:-1])
        seen += 1
        assert seen < 10, "alias cycle"
    return token


def px(value: float) -> dict[str, Any]:
    return {"value": value, "unit": "px"}


def srgb(hex_color: str) -> list[float]:
    return [round(c, 6) for c in hex_to_unit_rgb(hex_color)]


def test_schema_declared_and_valid(
    exported: dict[str, Any], validator: jsonschema.Draft7Validator
) -> None:
    assert exported["$schema"] == SCHEMA_URL
    assert sorted(validator.iter_errors(exported), key=str) == []
    for group in ("primitive", "semantic", "component"):
        assert exported[group]["$description"]
    assert "tokens.json" in exported["primitive"]["$description"]


def test_validator_rejects_a_color_with_two_components(
    exported: dict[str, Any], validator: jsonschema.Draft7Validator
) -> None:
    broken = copy.deepcopy(exported)
    token = next(iter(walk(broken["primitive"]["light"]).values()))
    token["$value"]["components"] = token["$value"]["components"][:2]
    assert list(validator.iter_errors(broken)), "the schema must reject a 2-component colour"


def test_every_mode_with_primitives_is_exported(
    exported: dict[str, Any], source: dict[str, Any]
) -> None:
    assert set(exported["primitive"]) - {"$description"} == set(source["primitives"])
    assert {"light", "dark"} <= set(source["primitives"])


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_primitives_are_oklch_with_exact_hex(
    exported: dict[str, Any], source: dict[str, Any], mode: str
) -> None:
    tokens = walk(exported["primitive"][mode])
    primitives = source["primitives"][mode]
    assert len(tokens) == len(primitives) > 0
    for name, text in primitives.items():
        family, step = name.split(".")
        token = tokens[(family, step)]
        lightness, chroma, hue = parse_oklch(text)
        assert token["$type"] == "color"
        assert token["$value"] == {
            "colorSpace": "oklch",
            "components": [lightness, chroma, hue],
            "hex": oklch_to_hex(lightness, chroma, hue),
        }


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_semantic_hex_roles_alias_their_primitive(
    exported: dict[str, Any], source: dict[str, Any], mode: str
) -> None:
    tokens = walk(exported["semantic"][mode])
    bindings = source["bindings"][mode]
    assert len(bindings) >= 40
    for role, name in bindings.items():
        token = tokens[(role,)]
        assert token["$type"] == "color"
        assert token["$value"] == f"{{primitive.{mode}.{name}}}"
        concrete = resolve(exported, token)
        assert concrete["$value"]["hex"] == source["modes"][mode][role].lower()


def test_every_alias_resolves_to_an_existing_token(
    exported: dict[str, Any], source: dict[str, Any]
) -> None:
    aliases = 0
    for token in walk(exported).values():
        value = token["$value"]
        if isinstance(value, str) and value.startswith("{"):
            aliases += 1
            assert "$value" in resolve(exported, token)
    bound = sum(len(roles) for roles in source["bindings"].values())
    assert aliases >= bound


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_translucent_roles_are_srgb_with_alpha(
    exported: dict[str, Any], source: dict[str, Any], mode: str
) -> None:
    tokens = walk(exported["semantic"][mode])
    translucent = 0
    for role, raw in source["modes"][mode].items():
        match = RGBA.match(str(raw))
        if match is None:
            continue
        r, g, b, alpha = (int(match[1]), int(match[2]), int(match[3]), float(match[4]))
        base = f"#{r:02x}{g:02x}{b:02x}"
        assert tokens[(role,)]["$value"] == {
            "colorSpace": "srgb",
            "components": srgb(base),
            "alpha": alpha,
            "hex": base,
        }
        translucent += 1
    assert translucent > 0


def test_dark_semantic_roles_resolve_to_their_colour(
    exported: dict[str, Any], source: dict[str, Any]
) -> None:
    tokens = walk(exported["semantic"]["dark"])
    checked = 0
    for role, raw in source["modes"]["dark"].items():
        if not isinstance(raw, str) or not (raw.startswith("#") or raw.startswith("rgba(")):
            continue
        token = tokens[(role,)]
        assert token["$type"] == "color"
        value = resolve(exported, token)["$value"]
        assert HEX.match(value["hex"])
        if raw.startswith("#"):
            assert value["hex"] == raw.lower()
            assert "alpha" not in value
        else:
            assert value["colorSpace"] == "srgb"
            assert value["components"] == srgb(value["hex"])
            match = RGBA.match(raw)
            assert match is not None
            assert value["alpha"] == float(match[4])
        checked += 1
    assert checked >= 40
    assert not any("." in key for path in tokens for key in path)


def test_spacing_radius_are_px_dimensions(exported: dict[str, Any], source: dict[str, Any]) -> None:
    components = source["components"]
    for step, value in components["spacing"].items():
        token = get(exported, f"component.spacing.{step}")
        assert (token["$type"], token["$value"]) == ("dimension", px(value))
    for step, value in components["radius"].items():
        token = get(exported, f"component.radius.{step}")
        assert (token["$type"], token["$value"]) == ("dimension", px(value))


def test_motion_durations_and_curves(exported: dict[str, Any], source: dict[str, Any]) -> None:
    motion = source["components"]["motion"]
    for name, value in motion["duration"].items():
        token = get(exported, f"component.motion.duration.{name}")
        assert (token["$type"], token["$value"]) == ("duration", {"value": value, "unit": "ms"})
    for name, points in motion["curve"].items():
        token = get(exported, f"component.motion.curve.{name}")
        assert (token["$type"], token["$value"]) == ("cubicBezier", points)


def test_light_elevation_matches_resolved_shadows(
    exported: dict[str, Any], source: dict[str, Any]
) -> None:
    resolved = resolve_components(source, "light")["elevation"]
    assert set(resolved) == set(source["components"]["elevation"]["levels"])
    for level, css in resolved.items():
        token = get(exported, f"component.elevation.{level}")
        assert token["$type"] == "shadow"
        layers = [part.strip() for part in re.split(r"(?<=\)),\s*", css)]
        assert len(layers) == len(token["$value"]) == 2
        for layer, shadow in zip(layers, token["$value"], strict=True):
            match = re.match(
                r"^(\S+?)(?:px)? (\S+?)(?:px)? (\S+?)(?:px)? rgba\((\d+), (\d+), (\d+), ([0-9.]+)\)$",
                layer,
            )
            assert match is not None, layer
            x, y, blur = (float(match[i]) for i in (1, 2, 3))
            base = f"#{int(match[4]):02x}{int(match[5]):02x}{int(match[6]):02x}"
            assert shadow["offsetX"] == px(x)
            assert shadow["offsetY"] == px(y)
            assert shadow["blur"] == px(blur)
            assert shadow["spread"] == px(0)
            assert shadow["color"] == {
                "colorSpace": "srgb",
                "components": srgb(base),
                "alpha": float(match[7]),
                "hex": base,
            }


def test_output_is_deterministic(tmp_path: Path) -> None:
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    for target in (first, second):
        assert run_export("--output", str(target)).returncode == 0
    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes().endswith(b"}\n")


def test_checked_in_export_matches_a_fresh_render(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh.json"
    assert run_export("--output", str(fresh)).returncode == 0
    assert GENERATED.read_bytes() == fresh.read_bytes(), (
        "docs/generated/dreamcoder.tokens.json is stale: run `make dtcg`"
    )


def test_default_output_is_the_generated_file() -> None:
    before = GENERATED.read_bytes()
    result = run_export()
    assert result.returncode == 0, result.stderr
    assert GENERATED.read_bytes() == before


def test_unreadable_tokens_exit_two(tmp_path: Path) -> None:
    result = run_export("--tokens", str(tmp_path / "missing.json"), "--output", str(tmp_path / "o"))
    assert result.returncode == 2
    assert not (tmp_path / "o").exists()
    assert result.stderr.strip()
