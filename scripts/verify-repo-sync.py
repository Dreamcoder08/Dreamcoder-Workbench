#!/usr/bin/env python3
"""Verify repository sync state: generated drift, profile validity, sensitive material, optional host tools.

Also validates the upstream manifest offline: schema conformance, 40-hex pinned
refs, HTTPS-only URLs, confined owned paths, ownership conflicts, and
consistency between the manifest and docs/sources.md. No network access is
performed by this verifier.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import jsonschema

from dreamcoder_theme.herdr_contract import SUPPORTED_PROFILES, detect_profile
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_herdr import herdr_content

ROOT = Path(__file__).resolve().parent.parent

HERDR_VARIANT_ROOT = ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder"
DEPLOY_DIR = ROOT / "DreamcoderProfiles/deploy"
DEPLOY_SCHEMA = DEPLOY_DIR / "deploy.schema.json"
SOURCE_MANIFEST = ROOT / "docs/sources.md"
UPSTREAM_MANIFEST = ROOT / "docs/upstream-manifest.json"
UPSTREAM_MANIFEST_SCHEMA = ROOT / "docs/upstream-manifest.schema.json"
# The upstream manifest and its schema are deliberately NOT scanned for
# sensitive content: they are verifier-owned records of upstream URLs and
# pinned refs, structurally validated below, and the sensitive scanner must
# not reject that legitimate URL/ref data as host material.
SCAN_TARGETS = (
    HERDR_VARIANT_ROOT,
    DEPLOY_DIR,
    SOURCE_MANIFEST,
    ROOT / "docs/herdr.md",
)

SHA_REF_RE = re.compile(r"^[0-9a-f]{40}$")
# 40-hex runs inside prose (for example backtick-quoted refs in sources.md).
SHA_REF_IN_TEXT_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
HTTPS_URL_RE = re.compile(r"^https://[^@\s]+\.git$")
SAFE_RELATIVE_PATH_RE = re.compile(
    r"^(?:(?!(?:\.\.?)(?:\/|$))[^/\\]+(?:\/(?!(?:\.\.?)(?:\/|$))[^/\\]+)*)$"
)
EXPECTED_UPSTREAM_NAMES = ("ml4w", "gentleman-dots")

SENSITIVE_PATTERNS = {
    "private key block": re.compile(r"BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY", re.IGNORECASE),
    "ssh public key material": re.compile(r"ssh-(?:rsa|ed25519|ecdsa) AAAA"),
    "credential token": re.compile(
        r"\b(?:ghp_|gho_|ghs_|ghu_|xox[baprs]-|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})\b"
    ),
    "ipv4 host address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}

FORBIDDEN_PROFILE_KEYS = (
    "address",
    "user",
    "host",
    "key",
    "token",
    "secret",
    "password",
    "private_key",
)


def _confined_relative(path_str: str) -> bool:
    """True when path_str is a safe relative path (no escape, no unsafe segments)."""
    if not path_str or "\u0000" in path_str or "\\" in path_str:
        return False
    if path_str.startswith("/") or re.match(r"^[A-Za-z]:", path_str):
        return False
    return bool(SAFE_RELATIVE_PATH_RE.match(path_str))


class _RepeatedKeyError(Exception):
    """Raised while parsing JSON when an object repeats a key."""


def _reject_repeated_keys(entries):
    """object_pairs_hook that rejects duplicate JSON keys instead of guessing."""
    result = {}
    for entry in entries:
        if entry[0] in result:
            raise _RepeatedKeyError(entry[0])
        result[entry[0]] = entry[1]
    return result


def _walk_keys(payload: object, prefix: str = "") -> list[str]:
    keys: list[str] = []
    if isinstance(payload, dict):
        for name, child in payload.items():
            path = f"{prefix}.{name}" if prefix else name
            keys.append(path)
            keys.extend(_walk_keys(child, path))
    elif isinstance(payload, list):
        for child in payload:
            keys.extend(_walk_keys(child, prefix))
    return keys


def drift_problems() -> list[str]:
    problems: list[str] = []
    for profile in SUPPORTED_PROFILES:
        base = HERDR_VARIANT_ROOT / profile.evidence.version
        for mode in ("dark", "light"):
            expected = herdr_content(profile, mode, VARIANTS[mode])
            path = base / f"config.{mode}.toml"
            if not path.is_file():
                problems.append(f"missing generated variant: {path}")
                continue
            try:
                tomllib.loads(path.read_text())
            except tomllib.TOMLDecodeError as error:
                problems.append(f"invalid TOML in generated variant {path}: {error}")
                continue
            if path.read_text() != expected:
                problems.append(
                    f"drift in generated variant {path} (regenerate with the theme sync)"
                )
    return problems


def deploy_profile_problems() -> list[str]:
    problems: list[str] = []
    if not DEPLOY_SCHEMA.is_file():
        return [f"missing deployment profile schema: {DEPLOY_SCHEMA}"]
    try:
        schema = json.loads(DEPLOY_SCHEMA.read_text())
    except (json.JSONDecodeError, OSError) as error:
        return [f"invalid deployment profile schema {DEPLOY_SCHEMA}: {error}"]
    for path in sorted(DEPLOY_DIR.glob("*.json")):
        if path.name == "deploy.schema.json":
            continue
        try:
            payload = json.loads(path.read_text())
            jsonschema.validate(payload, schema)
        except (json.JSONDecodeError, jsonschema.ValidationError) as error:
            problems.append(f"invalid deployment profile {path}: {error}")
            continue
        for key in FORBIDDEN_PROFILE_KEYS:
            if any(key == item.split(".")[-1] for item in _walk_keys(payload)):
                problems.append(f"forbidden sensitive key {key!r} in deployment profile {path}")
    return problems


def mobile_profile_problems() -> list[str]:
    path = DEPLOY_DIR / "mobile-termux.json"
    if not path.is_file():
        return [f"missing mobile deployment profile: {path}"]
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        return [f"mobile deployment profile is not valid JSON: {error}"]
    problems: list[str] = []
    if payload.get("terminal_default_mode") != "light":
        problems.append("mobile deployment profile must select Dreamcoder Light")
    herdr_ui = payload.get("herdr", {}).get("ui", {})
    if herdr_ui.get("pane_scrollbars") not in (False,):
        problems.append("mobile deployment profile must disable Herdr pane scrollbars")
    return problems


def source_manifest_problems() -> list[str]:
    problems: list[str] = []
    if not SOURCE_MANIFEST.is_file():
        return [f"missing source manifest: {SOURCE_MANIFEST}"]
    text = SOURCE_MANIFEST.read_text()
    for url in ("https://ml4w.com", "https://github.com/Gentleman-Programming/Gentleman.Dots"):
        if url not in text:
            problems.append(f"source manifest must declare upstream URL {url}")
    for phrase in ("source of truth", "secrets", "runtime state"):
        if phrase not in text:
            problems.append(f"source manifest must state the ownership boundary {phrase!r}")
    return problems


def _upstream_entry_problems(upstreams: dict) -> list[str]:
    """Per-upstream URL and pinned-ref checks."""
    problems: list[str] = []
    for name, upstream in upstreams.items():
        if not isinstance(upstream, dict):
            problems.append(f"upstream {name!r} must be an object")
            continue
        url = upstream.get("url", "")
        if not (isinstance(url, str) and HTTPS_URL_RE.match(url)):
            problems.append(f"upstream {name!r} must use an HTTPS repository URL: {url!r}")
        if upstream.get("status") == "pinned":
            ref = upstream.get("pinned_ref")
            if not (isinstance(ref, str) and SHA_REF_RE.match(ref)):
                problems.append(
                    f"upstream {name!r} pinned ref must be a 40-hex commit SHA: {ref!r}"
                )
    return problems


def upstream_manifest_problems() -> list[str]:
    problems: list[str] = []
    missing: list[str] = []
    if not UPSTREAM_MANIFEST.is_file():
        missing.append(f"missing upstream manifest: {UPSTREAM_MANIFEST}")
    if not UPSTREAM_MANIFEST_SCHEMA.is_file():
        missing.append(f"missing upstream manifest schema: {UPSTREAM_MANIFEST_SCHEMA}")
    if missing:
        return missing
    try:
        manifest = json.loads(
            UPSTREAM_MANIFEST.read_text(), object_pairs_hook=_reject_repeated_keys
        )
    except (json.JSONDecodeError, _RepeatedKeyError) as error:
        return [f"malformed upstream manifest {UPSTREAM_MANIFEST}: {error}"]
    try:
        schema = json.loads(
            UPSTREAM_MANIFEST_SCHEMA.read_text(), object_pairs_hook=_reject_repeated_keys
        )
    except (json.JSONDecodeError, _RepeatedKeyError) as error:
        return [f"malformed upstream manifest schema {UPSTREAM_MANIFEST_SCHEMA}: {error}"]
    try:
        jsonschema.validate(manifest, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        return [f"upstream manifest fails schema validation: {error.message}"]

    upstreams = manifest.get("upstreams", {})
    if not isinstance(upstreams, dict) or not upstreams:
        return ["upstream manifest must declare at least one upstream"]
    problems += _upstream_entry_problems(upstreams)
    if set(upstreams) != set(EXPECTED_UPSTREAM_NAMES):
        problems.append(
            "upstream manifest must declare exactly the named upstreams "
            f"{EXPECTED_UPSTREAM_NAMES!r}, found {sorted(upstreams)!r}"
        )
    problems += _owned_path_problems(manifest)
    problems += _doc_consistency_problems(manifest)
    return problems


def _owned_path_problems(manifest: dict) -> list[str]:
    """Path-confinement and ownership-conflict checks for manifest owned paths."""
    problems: list[str] = []
    upstreams = manifest.get("upstreams", {})
    owned_paths = manifest.get("owned_paths", {})
    if not isinstance(owned_paths, dict):
        return ["upstream manifest owned_paths must be an object"]
    for repo_path, mapping in owned_paths.items():
        if not _confined_relative(repo_path):
            problems.append(f"owned path is not confined to the repository: {repo_path!r}")
        if not isinstance(mapping, dict):
            problems.append(f"owned path {repo_path!r} must map to an object")
            continue
        owner = mapping.get("upstream")
        if owner not in upstreams:
            problems.append(f"owned path {repo_path!r} references unknown upstream {owner!r}")
        upstream_path = mapping.get("upstream_path", "")
        if not (isinstance(upstream_path, str) and _confined_relative(upstream_path)):
            problems.append(f"owned path {repo_path!r} has unsafe upstream_path {upstream_path!r}")
    for outer in owned_paths:
        for inner in owned_paths:
            if inner == outer or not inner.startswith(outer.rstrip("/") + "/"):
                continue
            outer_mapping = owned_paths[outer]
            inner_mapping = owned_paths[inner]
            if not (isinstance(outer_mapping, dict) and isinstance(inner_mapping, dict)):
                continue
            if outer_mapping.get("upstream") != inner_mapping.get("upstream"):
                problems.append(
                    f"ownership conflict: {inner!r} nests under {outer!r} "
                    "but is owned by a different upstream"
                )
    return problems


def _doc_consistency_problems(manifest: dict) -> list[str]:
    """Manifest-to-docs consistency: sources.md must agree with the manifest."""
    problems: list[str] = []
    if not SOURCE_MANIFEST.is_file():
        return problems  # reported by source_manifest_problems()
    text = SOURCE_MANIFEST.read_text()
    if "upstream-manifest.json" not in text:
        problems.append("docs/sources.md must reference the machine-readable upstream manifest")
    upstreams = manifest.get("upstreams", {})
    if not isinstance(upstreams, dict):
        return problems
    for name, upstream in upstreams.items():
        if not isinstance(upstream, dict):
            continue
        url = upstream.get("url")
        if isinstance(url, str) and url not in text:
            problems.append(
                f"docs/sources.md must list the verified upstream URL {url!r} for {name!r}"
            )
        if upstream.get("status") == "pinned":
            ref = upstream.get("pinned_ref")
            if isinstance(ref, str) and ref not in text:
                problems.append(f"docs/sources.md must record the pinned ref {ref!r} for {name!r}")
    doc_refs = set(SHA_REF_IN_TEXT_RE.findall(text))
    manifest_refs = {
        upstream.get("pinned_ref")
        for upstream in upstreams.values()
        if isinstance(upstream, dict) and upstream.get("status") == "pinned"
    }
    stale = sorted(doc_refs - manifest_refs)
    if stale:
        problems.append(
            "docs/sources.md records refs absent from the upstream manifest: " + ", ".join(stale)
        )
    return problems


def sensitive_absence_problems() -> list[str]:
    problems: list[str] = []
    for target in SCAN_TARGETS:
        if target.is_dir():
            files = sorted(p for p in target.rglob("*") if p.is_file())
        elif target.is_file():
            files = [target]
        else:
            continue
        for path in files:
            try:
                text = path.read_text()
            except (OSError, UnicodeDecodeError):
                continue
            for label, pattern in SENSITIVE_PATTERNS.items():
                if pattern.search(text):
                    problems.append(f"{label} pattern found in {path}")
    return problems


def optional_host_tool_problems() -> list[str]:
    problems: list[str] = []
    herdr = shutil.which("herdr")
    if herdr is None:
        print("herdr: not installed — optional config validation skipped (safe)")
        return problems
    # Validate the installed version's own variant; an unprofiled version
    # falls back to the 0.8.0 baseline.
    version_result = subprocess.run(
        [herdr, "--version"], capture_output=True, text=True, check=False
    )
    selection = detect_profile(str(version_result.stdout or ""))
    version = selection.profile.evidence.version if selection.profile else "0.8.0"
    variant = HERDR_VARIANT_ROOT / version / "config.light.toml"
    if not variant.is_file():
        problems.append(f"{version} light variant missing; cannot run optional herdr config check")
        return problems
    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp) / "config.toml"
        candidate.write_text(variant.read_text())
        env = {**os.environ, "HERDR_CONFIG_PATH": str(candidate)}
        result = subprocess.run(
            [herdr, "config", "check"], env=env, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            problems.append(
                f"herdr config check failed for the {version} light variant: "
                f"{result.stdout.strip()} {result.stderr.strip()}".strip()
            )
    return problems


def main() -> int:
    problems: list[str] = []
    problems += drift_problems()
    problems += deploy_profile_problems()
    problems += mobile_profile_problems()
    problems += source_manifest_problems()
    problems += upstream_manifest_problems()
    problems += sensitive_absence_problems()
    problems += optional_host_tool_problems()

    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if problems:
        return 1
    print("dreamcoder sync: OK — variants match the renderer, deployment profiles are valid,")
    print("mobile profile selects Light with Herdr pane scrollbars disabled, the upstream")
    print("manifest validates offline (schema, pins, confined paths, docs consistency), and")
    print("no sensitive material was found in the synchronization surface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
