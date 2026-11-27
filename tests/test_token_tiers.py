"""Three-tier token contract: OKLCH primitives -> semantic modes.

Spec: odd/tasks/dreamcoder-light-coherence.md, T2 (S2, S3).
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import jsonschema
import pytest

from dreamcoder_theme.color_space import format_oklch, hex_to_oklch, oklch_to_hex, parse_oklch
from dreamcoder_theme.token_tiers import TierError, drift, resolve_mode

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
SCHEMA = ROOT / "DreamcoderThemes/dreamcoder/tokens.schema.json"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
TIERED_MODES = ("light",)


def _tokens() -> dict:
    return json.loads(TOKENS.read_text(encoding="utf-8"))


def test_oklch_text_round_trips_every_light_hex() -> None:
    for key, value in _tokens()["modes"]["light"].items():
        if isinstance(value, str) and HEX.match(value):
            text = format_oklch(*hex_to_oklch(value))
            assert oklch_to_hex(*parse_oklch(text)) == value.lower(), key


@pytest.mark.parametrize("text", ["oklch(1.2 0.01 40)", "oklch(0.5 0.1)", "#fff", "oklch(a b c)"])
def test_parse_oklch_rejects_malformed_text(text: str) -> None:
    with pytest.raises(ValueError):
        parse_oklch(text)


@pytest.mark.parametrize("mode", TIERED_MODES)
def test_every_semantic_hex_is_bound_to_a_primitive(mode: str) -> None:
    tokens = _tokens()
    hex_keys = {k for k, v in tokens["modes"][mode].items() if isinstance(v, str) and HEX.match(v)}
    assert hex_keys == set(tokens["bindings"][mode])


@pytest.mark.parametrize("mode", TIERED_MODES)
def test_semantic_values_equal_their_resolved_primitives(mode: str) -> None:
    tokens = _tokens()
    resolved = resolve_mode(tokens, mode)
    for key, value in resolved.items():
        assert tokens["modes"][mode][key].lower() == value, key


@pytest.mark.parametrize("mode", TIERED_MODES)
def test_no_primitive_is_dead(mode: str) -> None:
    tokens = _tokens()
    assert set(tokens["primitives"][mode]) == set(tokens["bindings"][mode].values())


def test_unknown_primitive_reference_is_an_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["bindings"]["light"]["bg"] = "paper.missing"
    with pytest.raises(TierError, match=r"bg -> paper\.missing"):
        resolve_mode(tokens, "light")


def test_schema_accepts_tiers_and_rejects_bad_primitives() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    tokens = _tokens()
    jsonschema.validate(tokens, schema)
    broken = copy.deepcopy(tokens)
    first = next(iter(broken["primitives"]["light"]))
    broken["primitives"]["light"][first] = "#f9f6f2"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(broken, schema)
    broken = copy.deepcopy(tokens)
    broken["primitives"]["light"]["Bad Name"] = "oklch(0.5 0.01 40)"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(broken, schema)


def test_format_oklch_never_emits_hue_360() -> None:
    parse_oklch(format_oklch(*hex_to_oklch("#f33f8b")))


@pytest.mark.parametrize("value", ["oklch(0.5000 0.1000 400.00)", "oklch(0.5000 0.9000 40.00)"])
def test_schema_rejects_what_the_parser_rejects(value: str) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    tokens = copy.deepcopy(_tokens())
    tokens["primitives"]["light"]["paper.974"] = value
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, schema)


def test_primitive_drift_is_reported() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["primitives"]["light"]["paper.974"] = "oklch(0.9600 0.0062 75.41)"
    assert any(p.startswith("TIER_DRIFT: light.bg ") for p in drift(tokens))


def test_out_of_range_primitive_is_a_tier_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["primitives"]["light"]["paper.974"] = "oklch(0.9743 0.0062 400.00)"
    with pytest.raises(TierError, match=r"paper\.974"):
        resolve_mode(tokens, "light")
