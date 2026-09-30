#!/usr/bin/env python3
"""Read-only upstream ownership diff for Dreamcoder dots.

Compares repository files declared in ``docs/upstream-manifest.json`` against
the pinned upstream commits. This script NEVER writes to the repository or the
home directory: upstream data is fetched into a temporary bare Git repository
under the system temporary directory (never under the repo or HOME) and removed
before the script exits.

Modes
-----
default (diff)    For each selected upstream with owned mappings, fetch the
                  pinned ref into a temporary bare Git repository and compare
                  each declared owned path against the upstream blob. Every
                  mapping is reported as SAME, DIFF, LOCAL-MISSING, or
                  UPSTREAM-MISSING; DIFF and the missing states are drift and
                  are reported without failing (information, exit 0). An
                  upstream with no owned mappings is reported honestly as
                  such and no network access is attempted for it.

--check-pins      Contact each selected upstream (git ls-remote) and verify the
                  pinned ref still matches the remote HEAD. A moved HEAD whose
                  pinned ref is still reachable is drift (report-only). A pin
                  that is no longer reachable, or any network/ref failure,
                  fails closed.

Only pinned upstreams are inspected; an ``unpinned`` upstream is reported as
such and skipped (honest state, never guessed).

Exit codes
----------
0  success, including reported drift and no-mappings results
1  runtime failure: network, ref, object, or path errors (fail closed)
2  usage or configuration errors: malformed manifest/schema, unsafe paths or
   URLs, unknown parameters (fail closed)

Output
------
Human mode prints one section per upstream. With --json, exactly one valid
JSON document is written to stdout; errors are always written to stderr with
a nonzero exit and never produce a partial or second JSON document (there is
no JSON error envelope).

Security properties
-------------------
- URL and path input is never accepted on the command line: ``--upstream`` is
  restricted to names declared in the manifest, and URLs/paths come only from
  the schema-validated manifest.
- URLs must be HTTPS repository URLs without credentials; owned paths must be
  relative, contain no ``..``/``.``/empty segments, no backslashes, and must
  resolve inside the repository root.
- Git runs with an explicit argv (no shell), a hardened environment
  (no system/global config, no terminal prompts, protocol restricted to
  https), a timeout that kills the whole process group, and no checkout.
- Duplicate JSON keys and overlapping ownership claims are rejected rather
  than guessed.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import shutil
import signal
import sys
import tempfile
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "docs/upstream-manifest.json"
SCHEMA_PATH = ROOT / "docs/upstream-manifest.schema.json"

EXIT_OK = 0
EXIT_RUNTIME = 1
EXIT_CONFIG = 2

SHA_REF_RE = re.compile(r"^[0-9a-f]{40}$")
HTTPS_URL_RE = re.compile(r"^https://[^@\s]+\.git$")
SAFE_RELATIVE_PATH_RE = re.compile(
    r"^(?:(?!(?:\.\.?)(?:\/|$))[^/\\]+(?:\/(?!(?:\.\.?)(?:\/|$))[^/\\]+)*)$"
)

GIT_TIMEOUT = 60.0
FETCH_TIMEOUT = 120.0
LSREMOTE_TIMEOUT = 60.0

# Environment variables that could redirect Git state or network behavior.
_UNSET_GIT_VARS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
    "GIT_COMMON_DIR",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSH_VARIANT",
    "GIT_ASKPASS",
    "GIT_PROXY_COMMAND",
)


class ConfigError(Exception):
    """Malformed manifest, schema, or configuration (exit code 2)."""


class GitError(Exception):
    """A Git invocation failed: network, ref, object, or path error (exit 1)."""


class _DuplicateKeyError(ValueError):
    """Raised while parsing JSON when an object repeats a key."""


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """object_pairs_hook that rejects duplicate JSON keys instead of guessing."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json(text: str, what: str) -> dict[str, Any]:
    try:
        return json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except json.JSONDecodeError as error:
        raise ConfigError(f"malformed JSON in {what}: {error}") from error
    except _DuplicateKeyError as error:
        raise ConfigError(f"malformed JSON in {what}: {error}") from error


def _system_temp_base() -> Path:
    """A temporary base that is never the repo and never under the home directory."""
    base = Path(tempfile.gettempdir()).resolve()
    home = Path.home().resolve()
    if base == home or str(base).startswith(str(home) + os.sep):
        fallback = Path("/tmp")
        return fallback if fallback.is_dir() else base
    return base


def _git_env() -> dict[str, str]:
    """Hardened environment for every Git invocation."""
    env = {key: value for key, value in os.environ.items() if key not in _UNSET_GIT_VARS}
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ALLOW_PROTOCOL": "https",
            "LC_ALL": "C",
            "TMPDIR": str(_system_temp_base()),
        }
    )
    return env


def _run_git(argv: list[str], cwd: Path, timeout: float) -> bytes:
    """Run Git with an explicit argv, no shell, hardened env, and a hard timeout.

    The child is placed in its own process group so a timeout kills the whole
    group (including git's remote helper subprocesses).
    """
    try:
        proc = Popen(
            argv,
            cwd=str(cwd),
            env=_git_env(),
            stdout=PIPE,
            stderr=PIPE,
            shell=False,
            start_new_session=True,
        )
    except OSError as error:
        raise GitError(f"cannot start Git: {error}") from error
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        proc.wait()
        raise GitError(f"Git timed out after {timeout:.0f}s: {' '.join(argv)}") from None
    if proc.returncode != 0:
        detail = (stderr or stdout).decode("utf-8", errors="replace").strip()
        raise GitError(f"Git exited {proc.returncode}: {' '.join(argv)}\n{detail}")
    return stdout


def _confined_relative(path_str: str, label: str) -> Path:
    """Return a confined relative Path, or raise ConfigError for unsafe input."""
    if not path_str or "\x00" in path_str or "\\" in path_str:
        raise ConfigError(f"{label} is not a confined relative path: {path_str!r}")
    if path_str.startswith("/") or re.match(r"^[A-Za-z]:", path_str):
        raise ConfigError(f"{label} must be relative to the repository root: {path_str!r}")
    if not SAFE_RELATIVE_PATH_RE.match(path_str):
        raise ConfigError(f"{label} contains forbidden path segments: {path_str!r}")
    return Path(*path_str.split("/"))


def _confined_local(path_str: str, label: str) -> Path:
    """Confine a local owned path and verify it cannot escape the repo root."""
    relative = _confined_relative(path_str, label)
    resolved_root = ROOT.resolve()
    candidate = (resolved_root / relative).resolve()
    if not str(candidate).startswith(str(resolved_root) + os.sep):
        raise ConfigError(f"{label} resolves outside the repository root: {path_str!r}")
    return relative


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        raise ConfigError(f"missing upstream manifest: {MANIFEST_PATH}")
    if not SCHEMA_PATH.is_file():
        raise ConfigError(f"missing upstream manifest schema: {SCHEMA_PATH}")
    try:
        manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
        schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError(f"cannot read upstream manifest or schema: {error}") from error
    manifest = _load_json(manifest_text, str(MANIFEST_PATH))
    schema = _load_json(schema_text, str(SCHEMA_PATH))
    try:
        jsonschema.validate(manifest, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise ConfigError(f"upstream manifest fails schema validation: {error.message}") from error
    return manifest


def _validate_manifest(manifest: dict[str, Any]) -> None:
    """Fail closed on unsafe URLs, refs, paths, and ownership conflicts."""
    upstreams = manifest["upstreams"]
    for name, upstream in upstreams.items():
        url = upstream["url"]
        if not HTTPS_URL_RE.match(url):
            raise ConfigError(
                f"upstream {name!r}: URL is not a confined HTTPS repository URL: {url!r}"
            )
        if upstream["status"] == "pinned" and not SHA_REF_RE.match(upstream["pinned_ref"] or ""):
            raise ConfigError(
                f"upstream {name!r}: pinned ref is not a 40-hex commit SHA: {upstream['pinned_ref']!r}"
            )
        if upstream["status"] == "unpinned" and upstream.get("pinned_ref") is not None:
            raise ConfigError(f"upstream {name!r}: unpinned upstream must not declare a pinned ref")

    owned = manifest["owned_paths"]
    local_paths: list[str] = []
    for local_path, mapping in owned.items():
        up_name = mapping["upstream"]
        if up_name not in upstreams:
            raise ConfigError(f"owned path {local_path!r} references unknown upstream {up_name!r}")
        _confined_local(local_path, f"owned local path {local_path!r}")
        _confined_relative(mapping["upstream_path"], f"upstream path of {local_path!r}")
        local_paths.append(local_path)

    for first, second in itertools.pairwise(sorted(local_paths)):
        if second.startswith(first + "/"):
            raise ConfigError(f"overlapping ownership claims: {first!r} and {second!r}")


def _unpinned_result(upstream: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": upstream["name"],
        "url": upstream["url"],
        "pinned_ref": None,
        "status": "unpinned",
        "note": "unpinned upstream — no ref recorded; nothing to diff or check",
    }


def _require_pin_fetchable(name: str, url: str, pin: str) -> None:
    """Fail closed unless the pinned commit can still be fetched by hash.

    `git ls-remote <url> <sha>` cannot do this: it matches ref names, never hashes, so it
    exits 2 for every pin that is no longer the remote HEAD. Fetching the hash into a
    throwaway bare repo (as _diff_upstream does) is the check that reflects reality.
    """
    temp_dir: Path | None = None
    try:
        temp_dir = Path(
            tempfile.mkdtemp(prefix="dreamcoder-upstream-pin-", dir=str(_system_temp_base()))
        )
        _run_git(["git", "init", "--bare", "--quiet", str(temp_dir)], ROOT, GIT_TIMEOUT)
        _run_git(
            ["git", "-C", str(temp_dir), "fetch", "--no-tags", "--depth=1", url, pin],
            ROOT,
            FETCH_TIMEOUT,
        )
    except GitError as exc:
        raise GitError(
            f"pinned ref {pin} for {name} is no longer reachable on the remote: {exc}"
        ) from exc
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _check_pin(name: str, upstream: dict[str, Any]) -> dict[str, Any]:
    """Verify the pinned ref against the remote HEAD (drift is report-only)."""
    url = upstream["url"]
    pin = upstream["pinned_ref"]
    head_out = _run_git(["git", "ls-remote", "--exit-code", url, "HEAD"], ROOT, LSREMOTE_TIMEOUT)
    head = head_out.decode("utf-8", errors="replace").split("\t", 1)[0].strip()
    if not SHA_REF_RE.match(head):
        raise GitError(f"unexpected git ls-remote output for {url}: {head_out!r}")

    result: dict[str, Any] = {
        "name": upstream["name"],
        "url": url,
        "pinned_ref": pin,
        "status": "current",
        "note": "pinned ref matches remote HEAD",
    }
    if head != pin:
        _require_pin_fetchable(name, url, pin)
        result["status"] = "stale"
        result["note"] = (
            f"remote HEAD {head} differs from pinned ref {pin}; pin still reachable — "
            "drift, report-only"
        )
    return result


def _diff_upstream(name: str, upstream: dict[str, Any], owned: dict[str, Any]) -> dict[str, Any]:
    """Fetch the pinned ref into a temporary bare repo and diff owned paths."""
    pin = upstream["pinned_ref"]
    url = upstream["url"]
    mappings = {local: m for local, m in owned.items() if m["upstream"] == name}
    result: dict[str, Any] = {
        "name": upstream["name"],
        "url": url,
        "pinned_ref": pin,
        "status": "ok",
        "mappings": [],
        "note": "no owned mappings declared — nothing to diff",
    }
    if not mappings:
        return result
    result["note"] = f"diffed {len(mappings)} owned mapping(s) against pinned ref"

    temp_dir: Path | None = None
    try:
        temp_dir = Path(
            tempfile.mkdtemp(prefix="dreamcoder-upstream-diff-", dir=str(_system_temp_base()))
        )
        _run_git(["git", "init", "--bare", "--quiet", str(temp_dir)], ROOT, GIT_TIMEOUT)
        _run_git(
            ["git", "-C", str(temp_dir), "fetch", "--no-tags", "--depth=1", url, pin],
            ROOT,
            FETCH_TIMEOUT,
        )
        # Confirm the pinned commit resolved locally before treating any
        # missing path as an upstream-side absence (fail closed on pins that
        # did not resolve).
        _run_git(
            ["git", "-C", str(temp_dir), "cat-file", "-e", f"{pin}^{{commit}}"],
            ROOT,
            GIT_TIMEOUT,
        )
        listing = _run_git(
            ["git", "-C", str(temp_dir), "ls-tree", "-r", "--name-only", "-z", pin],
            ROOT,
            GIT_TIMEOUT,
        )
        upstream_files = {
            entry.decode("utf-8", errors="replace") for entry in listing.split(b"\0") if entry
        }
        for local_path, mapping in sorted(mappings.items()):
            upstream_path = mapping["upstream_path"]
            entry: dict[str, Any] = {
                "local_path": local_path,
                "upstream_path": upstream_path,
                "status": "",
                "local_bytes": None,
                "upstream_bytes": None,
            }
            local_file = ROOT / local_path
            in_upstream = upstream_path in upstream_files
            if not local_file.is_file():
                entry["status"] = "LOCAL-MISSING"
                if in_upstream:
                    entry["upstream_bytes"] = len(
                        _run_git(
                            [
                                "git",
                                "-C",
                                str(temp_dir),
                                "cat-file",
                                "blob",
                                f"{pin}:{upstream_path}",
                            ],
                            ROOT,
                            GIT_TIMEOUT,
                        )
                    )
            elif not in_upstream:
                entry["status"] = "UPSTREAM-MISSING"
                entry["local_bytes"] = local_file.stat().st_size
            else:
                upstream_bytes = _run_git(
                    ["git", "-C", str(temp_dir), "cat-file", "blob", f"{pin}:{upstream_path}"],
                    ROOT,
                    GIT_TIMEOUT,
                )
                local_bytes = local_file.read_bytes()
                entry["local_bytes"] = len(local_bytes)
                entry["upstream_bytes"] = len(upstream_bytes)
                entry["status"] = "SAME" if local_bytes == upstream_bytes else "DIFF"
            result["mappings"].append(entry)
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)
    return result


def _required_status(payload: dict[str, Any], label: str) -> str:
    """Return the payload's status string, failing closed when it is absent.

    Results are produced by this script, so a missing or non-string status is an
    internal invariant violation, not a reportable state: refuse to guess it.
    """
    status = payload.get("status")
    if not isinstance(status, str):
        raise GitError(
            f"internal invariant violated: {label} has no string status (got {status!r})"
        )
    return status


def _build_report(mode: str, results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report: dict[str, Any] = {"mode": mode, "ok": True, "result": "ok", "upstreams": results}
    if mode == "check-pins":
        stale = sorted(
            name
            for name, item in results.items()
            if _required_status(item, f"upstream {name!r}") == "stale"
        )
        report["pins_stale"] = stale
        report["result"] = "pins-stale" if stale else "pins-current"
        return report
    mapping_count = sum(len(item.get("mappings", [])) for item in results.values())
    drift_count = sum(
        1
        for name, item in results.items()
        for entry in item.get("mappings", [])
        if _required_status(entry, f"mapping for {name}") != "SAME"
    )
    if mapping_count == 0:
        report["result"] = "no-mappings"
    elif drift_count:
        report["result"] = "drift"
    else:
        report["result"] = "clean"
    return report


def _print_human(mode: str, report: dict[str, Any]) -> None:
    for name, item in report["upstreams"].items():
        if item["status"] == "unpinned":
            print(f"{name}: unpinned — no ref recorded; nothing to check")
            continue
        print(f"{name}: pinned {item['pinned_ref']}")
        if mode == "check-pins":
            if item["status"] == "current":
                print("  pin current — matches remote HEAD")
            else:
                print(
                    "  STALE pin — remote HEAD differs; pinned ref still reachable (drift, report-only)"
                )
            continue
        mappings = item["mappings"]
        print(f"  {len(mappings)} owned mapping(s)")
        if not mappings:
            print("  no owned mappings declared — nothing to diff")
        for entry in mappings:
            status = entry["status"]
            if status == "SAME":
                print(
                    f"  SAME: {entry['local_path']} matches upstream {entry['upstream_path']} "
                    f"({entry['local_bytes']} bytes)"
                )
            elif status == "DIFF":
                print(
                    f"  DRIFT: {entry['local_path']} (upstream {entry['upstream_path']}) "
                    f"local {entry['local_bytes']} bytes vs upstream {entry['upstream_bytes']} bytes"
                )
            elif status == "LOCAL-MISSING":
                suffix = (
                    f" (upstream has {entry['upstream_bytes']} bytes)"
                    if entry["upstream_bytes"] is not None
                    else ""
                )
                print(f"  LOCAL-MISSING: {entry['local_path']} is absent locally{suffix}")
            else:
                print(
                    f"  UPSTREAM-MISSING: {entry['upstream_path']} absent at the pinned ref "
                    f"(local {entry['local_bytes']} bytes)"
                )


def _parse_args(argv: list[str] | None, manifest: dict[str, Any]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dreamcoder upstream-diff",
        description=(
            "Read-only upstream ownership diff against pinned refs. Never writes "
            "to the repository or the home directory; fails closed on errors."
        ),
    )
    parser.add_argument(
        "--upstream",
        choices=sorted(manifest["upstreams"]),
        help="only inspect this upstream (default: all upstreams in the manifest)",
    )
    parser.add_argument(
        "--check-pins",
        action="store_true",
        help="verify pinned refs against remote HEAD instead of diffing (drift is report-only)",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        manifest = _load_manifest()
        _validate_manifest(manifest)
    except ConfigError as error:
        print(f"upstream-diff: {error}", file=sys.stderr)
        return EXIT_CONFIG

    args = _parse_args(argv, manifest)
    names = [args.upstream] if args.upstream else sorted(manifest["upstreams"])
    mode = "check-pins" if args.check_pins else "diff"

    results: dict[str, dict[str, Any]] = {}
    try:
        for name in names:
            upstream = manifest["upstreams"][name]
            if upstream["status"] == "unpinned":
                results[name] = _unpinned_result(upstream)
            elif mode == "check-pins":
                results[name] = _check_pin(name, upstream)
            else:
                results[name] = _diff_upstream(name, upstream, manifest["owned_paths"])
    except GitError as error:
        print(f"upstream-diff: {error}", file=sys.stderr)
        return EXIT_RUNTIME

    try:
        report = _build_report(mode, results)
    except GitError as error:
        print(f"upstream-diff: {error}", file=sys.stderr)
        return EXIT_RUNTIME
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_human(mode, report)
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
