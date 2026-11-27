import json
from pathlib import Path

import pytest

from dreamcoder_theme.targets import ManifestError, load_target_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "DreamcoderThemes" / "dreamcoder" / "targets.json"


def _read_fixture(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        pytest.fail(f"required test fixture is unreadable: {path}: {error}")


def _write_manifest(tmp_path: Path, mutate) -> Path:
    try:
        payload = json.loads(_read_fixture(MANIFEST))
    except json.JSONDecodeError as error:
        pytest.fail(f"required test fixture is invalid JSON: {MANIFEST}: {error}")
    mutate(payload)
    path = tmp_path / "targets.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "targets.schema.json").write_text(
        _read_fixture(MANIFEST.parent / "targets.schema.json"), encoding="utf-8"
    )
    return path


def test_manifest_loads_complete_audited_classification_in_stable_order():
    manifest = load_target_manifest(MANIFEST)

    assert manifest.ids == tuple(sorted(manifest.ids))
    assert len(manifest.targets) == 36
    assert manifest.require("kitty").classification == "required"
    assert manifest.require("herdr").classification == "excluded"
    assert manifest.require("herdr").reason.startswith("gated:")


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("missing-targets.json", "cannot read manifest"),
        ("invalid-targets.json", "cannot read manifest"),
    ],
)
def test_manifest_rejects_missing_or_invalid_input(tmp_path, path, message):
    manifest_path = tmp_path / path
    if path == "invalid-targets.json":
        manifest_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ManifestError, match=message):
        load_target_manifest(manifest_path)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload["targets"][0].pop("activation"), "activation"),
        (lambda payload: payload["targets"][0].update(reason=""), "reason"),
        (
            lambda payload: payload["targets"].append(payload["targets"][0].copy()),
            "duplicate target id",
        ),
        (
            lambda payload: payload["targets"][0]["render"].update(modes=["dark", "invalid"]),
            "render variants must be dark and light",
        ),
    ],
)
def test_manifest_rejects_invalid_target_contracts(tmp_path, mutate, message):
    with pytest.raises(ManifestError, match=message):
        load_target_manifest(_write_manifest(tmp_path, mutate))


def test_manifest_rejects_duplicate_repository_outputs_and_selectors(tmp_path):
    def duplicate_ownership(payload):
        duplicate = payload["targets"][1]
        duplicate["render"]["repository_outputs"] = payload["targets"][0]["render"][
            "repository_outputs"
        ]
        duplicate["activation"]["selector"] = payload["targets"][0]["activation"]["selector"]

    with pytest.raises(ManifestError, match="duplicate repository output"):
        load_target_manifest(_write_manifest(tmp_path, duplicate_ownership))


def test_manifest_rejects_duplicate_selector_ownership(tmp_path):
    def duplicate_selector(payload):
        payload["targets"][1]["activation"]["selector"] = payload["targets"][0]["activation"][
            "selector"
        ]

    with pytest.raises(ManifestError, match="duplicate selector ownership"):
        load_target_manifest(_write_manifest(tmp_path, duplicate_selector))


def test_manifest_rejects_an_incomplete_audited_inventory(tmp_path):
    def remove_kitty(payload):
        payload["targets"] = [target for target in payload["targets"] if target["id"] != "kitty"]

    with pytest.raises(ManifestError, match="missing audited targets: kitty"):
        load_target_manifest(_write_manifest(tmp_path, remove_kitty))
