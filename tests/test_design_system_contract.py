import copy
import json
from pathlib import Path

import jsonschema
import pytest

from dreamcoder_theme.design_system import (
    evaluate_contract,
    load_contract,
    load_tokens,
    resolve_role,
)

ROOT = Path(__file__).resolve().parents[1]
THEME_ROOT = ROOT / "DreamcoderThemes" / "dreamcoder"


@pytest.fixture
def contract():
    return load_contract(THEME_ROOT / "design-system.json")


@pytest.fixture
def tokens():
    return load_tokens(THEME_ROOT / "tokens.json")


def test_contract_and_tokens_schemas_require_three_modes(contract, tokens):
    contract_schema = json.loads((THEME_ROOT / "design-system.schema.json").read_text())
    token_schema = json.loads((THEME_ROOT / "tokens.schema.json").read_text())
    jsonschema.validate(contract, contract_schema)
    jsonschema.validate(tokens, token_schema)

    assert set(tokens["modes"]) == {"light", "dusk", "dark"}
    assert "dark_oled" not in tokens
    assert "avoid_pure_black_white" not in tokens["guardrails"]

    incomplete = copy.deepcopy(tokens)
    del incomplete["modes"]["dusk"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(incomplete, token_schema)

    extra_mode = copy.deepcopy(tokens)
    extra_mode["modes"]["night"] = copy.deepcopy(tokens["modes"]["dark"])
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(extra_mode, token_schema)

    oled_light = copy.deepcopy(tokens)
    oled_light["modes"]["light"]["surface_policy"] = copy.deepcopy(
        tokens["modes"]["dark"]["surface_policy"]
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(oled_light, token_schema)


def test_dark_metadata_is_owned_by_the_canonical_dark_mode(tokens):
    dark = tokens["modes"]["dark"]
    assert dark["name"] == "Dreamcoder Dark"
    assert set(("aliases", "effects", "typography", "surface_policy")) <= set(dark)
    assert dark["surface_policy"]["pure_black_policy"] == {
        "canvas": True,
        "functional_surfaces": False,
        "scrollable_surfaces": False,
    }


def test_roles_are_traceable_to_canonical_tokens(contract, tokens):
    resolved = resolve_role(contract, tokens, "dusk", "selection.text")

    assert resolved.value == tokens["modes"]["dusk"]["selection_fg"]
    assert resolved.source == "modes.dusk.selection_fg"
    assert resolved.chain == ("selection.text", "text", "background")


def test_unknown_and_cyclic_role_derivations_are_rejected(contract, tokens):
    with pytest.raises(ValueError, match="unknown role"):
        resolve_role(contract, tokens, "dark", "missing")

    cyclic = copy.deepcopy(contract)
    cyclic["roles"]["text"]["parent"] = "muted"
    cyclic["roles"]["muted"]["parent"] = "text"
    with pytest.raises(ValueError, match="cyclic role derivation"):
        resolve_role(cyclic, tokens, "dark", "text")


def test_derivations_reject_unknown_and_cyclic_inputs(contract, tokens):
    derived = copy.deepcopy(contract)
    derived["roles"]["derived-text"] = {
        "layer": "component-state",
        "derivation": {"id": "alias", "inputs": ["text"]},
    }
    assert (
        resolve_role(derived, tokens, "dark", "derived-text").value
        == tokens["modes"]["dark"]["text"]
    )

    unknown = copy.deepcopy(derived)
    unknown["roles"]["derived-text"]["derivation"]["inputs"] = ["missing-input"]
    with pytest.raises(ValueError, match="unknown role"):
        resolve_role(unknown, tokens, "dark", "derived-text")

    cyclic = copy.deepcopy(derived)
    cyclic["roles"]["derived-text"]["derivation"]["inputs"] = ["derived-text"]
    with pytest.raises(ValueError, match="cyclic role derivation"):
        resolve_role(cyclic, tokens, "dark", "derived-text")


def test_six_target_three_mode_contract_passes(contract, tokens):
    assert evaluate_contract(contract, tokens) == []


def test_contract_declares_checked_in_dark_css_artifact(contract):
    artifact = next(row for row in contract["artifacts"] if row["id"] == "dark-css")

    assert artifact["lifecycle"] == "checked-in"
    assert artifact["source"] == "DreamcoderThemes/dreamcoder/tokens.json"
    assert artifact["generator"] == "python scripts/generate-dark-css.py"
    assert artifact["path"] == "DreamcoderThemes/dreamcoder/dreamcoder-dark.css"
    assert artifact["validation"] == "exact-bytes"


def test_adapter_parity_rejects_semantic_provenance_drift(contract, tokens):
    broken = copy.deepcopy(contract)
    broken["targets"]["kitty"]["fields"]["text"] = "background"

    findings = evaluate_contract(broken, tokens)

    assert any(
        finding.code == "SEMANTIC_PROVENANCE_MISMATCH"
        and finding.target == "kitty"
        and finding.role == "text"
        for finding in findings
    )


def test_missing_dusk_target_role_and_mapping_fail_explicitly(contract, tokens):
    broken = copy.deepcopy(contract)
    del broken["targets"]["opencode"]["modes"][-1]
    del broken["targets"]["kitty"]["fields"]["focus"]
    del broken["targets"]["kitty"]["mappings"]["focus"]

    findings = evaluate_contract(broken, tokens)

    assert any(
        f.code == "MISSING_TARGET_MODE" and f.target == "opencode" and f.mode == "dusk"
        for f in findings
    )
    assert any(
        f.code == "PARITY_MISSING_FIELD" and f.target == "kitty" and f.role == "focus"
        for f in findings
    )


def test_success_status_covers_every_target_declaring_success(contract, tokens):
    success_status = next(row for row in contract["matrix"] if row["id"] == "success-status")
    success_targets = {
        target
        for target, target_contract in contract["targets"].items()
        if "success" in target_contract["required_roles"]
    }

    assert set(success_status["targets"]) == success_targets
    assert contract["targets"]["tmux"]["fields"]["success"] == "success-colour"
    assert "success" not in contract["targets"]["tmux"].get("mappings", {})


def test_matrix_requires_declared_target_roles_and_orders_findings(contract, tokens):
    broken = copy.deepcopy(contract)
    broken["matrix"][0]["targets"] = ["missing-target"]
    broken["matrix"][1]["foreground"] = "missing-role"

    findings = evaluate_contract(broken, tokens)

    assert any(f.code == "MATRIX_UNKNOWN_TARGET" for f in findings)
    assert any(f.code == "MATRIX_MISSING_ROLE" and f.role == "missing-role" for f in findings)
    assert findings == sorted(
        findings,
        key=lambda finding: (
            finding.code,
            finding.target or "",
            finding.mode or "",
            finding.role or "",
            finding.artifact or "",
        ),
    )
