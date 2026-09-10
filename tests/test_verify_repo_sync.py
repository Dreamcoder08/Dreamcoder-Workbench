"""Tests for the repository synchronization verifier (scripts/verify-repo-sync.py)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

from dreamcoder_theme.herdr_contract import (
    HERDR_073_PROFILE,
    HERDR_080_PROFILE,
    HERDR_082_PROFILE,
)
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_herdr import herdr_content

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify-repo-sync.py"


def _load_verifier() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_repo_sync", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_layout(module: ModuleType, root: Path) -> None:
    for profile in (HERDR_073_PROFILE, HERDR_080_PROFILE, HERDR_082_PROFILE):
        base = root / "DreamcoderHerdr/.config/herdr/dreamcoder" / profile.evidence.version
        base.mkdir(parents=True)
        (base / "config.dark.toml").write_text(herdr_content(profile, "dark", VARIANTS["dark"]))
        (base / "config.light.toml").write_text(herdr_content(profile, "light", VARIANTS["light"]))
    deploy = root / "DreamcoderProfiles/deploy"
    deploy.mkdir(parents=True)
    for name in ("deploy.schema.json", "desktop-arch.json", "mobile-termux.json"):
        (deploy / name).write_text((module.DEPLOY_DIR / name).read_text())
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "sources.md").write_text((module.SOURCE_MANIFEST).read_text())
    (docs / "herdr.md").write_text((ROOT / "docs/herdr.md").read_text())
    (docs / "upstream-manifest.json").write_text(module.UPSTREAM_MANIFEST.read_text())
    (docs / "upstream-manifest.schema.json").write_text(module.UPSTREAM_MANIFEST_SCHEMA.read_text())


def _point_module_at(module: ModuleType, monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(
        module, "HERDR_VARIANT_ROOT", root / "DreamcoderHerdr/.config/herdr/dreamcoder"
    )
    monkeypatch.setattr(module, "DEPLOY_DIR", root / "DreamcoderProfiles/deploy")
    monkeypatch.setattr(
        module, "DEPLOY_SCHEMA", root / "DreamcoderProfiles/deploy/deploy.schema.json"
    )
    monkeypatch.setattr(module, "SOURCE_MANIFEST", root / "docs/sources.md")
    monkeypatch.setattr(module, "UPSTREAM_MANIFEST", root / "docs/upstream-manifest.json")
    monkeypatch.setattr(
        module, "UPSTREAM_MANIFEST_SCHEMA", root / "docs/upstream-manifest.schema.json"
    )
    monkeypatch.setattr(
        module,
        "SCAN_TARGETS",
        (
            root / "DreamcoderHerdr/.config/herdr/dreamcoder",
            root / "DreamcoderProfiles/deploy",
            root / "docs/sources.md",
            root / "docs/herdr.md",
        ),
    )


def _run(module: ModuleType, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = module.main()
    captured = capsys.readouterr()
    return code, captured.out + captured.err


def test_clean_tree_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)

    code, output = _run(module, capsys)

    assert code == 0
    assert "OK" in output
    assert "skipped" in output


def test_drift_in_generated_variant_is_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    variant = tmp_path / "DreamcoderHerdr/.config/herdr/dreamcoder/0.8.0/config.light.toml"
    variant.write_text(variant.read_text() + "\n# tampered\n")

    code, output = _run(module, capsys)

    assert code == 1
    assert "drift" in output


def test_sensitive_material_in_scan_surface_is_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    leak = tmp_path / "DreamcoderHerdr/.config/herdr/dreamcoder/0.8.0/leak.txt"
    leak.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n")

    code, output = _run(module, capsys)

    assert code == 1
    assert "private key block" in output


def test_invalid_mobile_profile_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    mobile = tmp_path / "DreamcoderProfiles/deploy/mobile-termux.json"
    mobile.write_text(
        mobile.read_text().replace(
            '"terminal_default_mode": "light"', '"terminal_default_mode": "dark"'
        )
    )

    code, output = _run(module, capsys)

    assert code == 1
    assert "must select Dreamcoder Light" in output


def test_host_tool_failure_is_not_masked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: "/bin/herdr")

    class FakeResult:
        returncode = 1
        stdout = "invalid config"
        stderr = ""

    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: FakeResult())

    code, output = _run(module, capsys)

    assert code == 1
    assert "herdr config check failed" in output


def test_missing_source_manifest_fails_safely(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    (tmp_path / "docs/sources.md").unlink()

    code, output = _run(module, capsys)

    assert code == 1
    assert "missing source manifest" in output


def _base_manifest() -> dict:
    """A schema-valid upstream manifest mirroring the repository's declared upstreams."""
    return {
        "version": 1,
        "provenance": {
            "verified_on": "2026-08-10T01:27:49Z",
            "method": "test fixture",
            "command": "git ls-remote <url> HEAD",
        },
        "upstreams": {
            "ml4w": {
                "name": "ML4W (Hyprland desktop dotfiles)",
                "url": "https://github.com/mylinuxforwork/dotfiles.git",
                "status": "pinned",
                "pinned_ref": "46f2ca7f73fe98b16ce4ab6433a9ac29fa9fd033",
                "verified_on": "2026-08-10T01:27:49Z",
            },
            "gentleman-dots": {
                "name": "Gentleman.Dots (shell / editor / terminal base configuration)",
                "url": "https://github.com/Gentleman-Programming/Gentleman.Dots.git",
                "status": "pinned",
                "pinned_ref": "02584500de6378ff5f54d252dc28fce8424b088a",
                "verified_on": "2026-08-10T01:27:49Z",
            },
        },
        "owned_paths": {},
    }


PERMISSIVE_SCHEMA = {"type": "object"}


def _override_manifest_files(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    manifest: dict,
    schema: dict,
) -> None:
    """Point the module at isolated manifest/schema files with custom content."""
    manifest_path = root / "docs/upstream-manifest.json"
    schema_path = root / "docs/upstream-manifest.schema.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    schema_path.write_text(json.dumps(schema, indent=2))
    monkeypatch.setattr(module, "UPSTREAM_MANIFEST", manifest_path)
    monkeypatch.setattr(module, "UPSTREAM_MANIFEST_SCHEMA", schema_path)


def test_malformed_upstream_schema_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    (tmp_path / "docs/upstream-manifest.schema.json").write_text("{not json")

    code, output = _run(module, capsys)

    assert code == 1
    assert "malformed upstream manifest schema" in output


def test_bad_upstream_url_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    manifest = _base_manifest()
    manifest["upstreams"]["ml4w"]["url"] = "http://github.com/mylinuxforwork/dotfiles.git"
    _override_manifest_files(module, monkeypatch, tmp_path, manifest, PERMISSIVE_SCHEMA)

    code, output = _run(module, capsys)

    assert code == 1
    assert "must use an HTTPS repository URL" in output


def test_bad_pinned_ref_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    manifest = _base_manifest()
    manifest["upstreams"]["gentleman-dots"]["pinned_ref"] = "deadbeef"
    _override_manifest_files(module, monkeypatch, tmp_path, manifest, PERMISSIVE_SCHEMA)

    code, output = _run(module, capsys)

    assert code == 1
    assert "pinned ref must be a 40-hex commit SHA" in output


def test_unsafe_owned_path_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    manifest = _base_manifest()
    manifest["owned_paths"] = {"../escape": {"upstream": "ml4w", "upstream_path": "config"}}
    _override_manifest_files(module, monkeypatch, tmp_path, manifest, PERMISSIVE_SCHEMA)

    code, output = _run(module, capsys)

    assert code == 1
    assert "not confined to the repository" in output


def test_ownership_conflict_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    manifest = _base_manifest()
    manifest["owned_paths"] = {
        "DreamcoderNvim/colors": {"upstream": "ml4w", "upstream_path": "colors"},
        "DreamcoderNvim/colors/dark.lua": {
            "upstream": "gentleman-dots",
            "upstream_path": "dark.lua",
        },
    }
    _override_manifest_files(module, monkeypatch, tmp_path, manifest, PERMISSIVE_SCHEMA)

    code, output = _run(module, capsys)

    assert code == 1
    assert "ownership conflict" in output


def test_manifest_docs_mismatch_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_verifier()
    _install_layout(module, tmp_path)
    _point_module_at(module, monkeypatch, tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    sources = tmp_path / "docs/sources.md"
    stale_ref = "1" * 40
    sources.write_text(
        sources.read_text().replace("46f2ca7f73fe98b16ce4ab6433a9ac29fa9fd033", stale_ref)
    )

    code, output = _run(module, capsys)

    assert code == 1
    assert "refs absent from the upstream manifest" in output
