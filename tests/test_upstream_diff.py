"""Tests for the read-only upstream ownership diff tool (scripts/upstream-diff.py).

All Git and network behavior is mocked at the module's single subprocess choke
point (``_run_git``): no real network, clone, checkout, or host state is ever
touched. The tests also prove the repository itself is never mutated and that
invalid input is rejected before any transport is attempted.
"""

from __future__ import annotations

import importlib.util
import json
import signal
from collections.abc import Callable
from pathlib import Path
from subprocess import PIPE, TimeoutExpired
from types import ModuleType, SimpleNamespace
from typing import Any, NoReturn

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/upstream-diff.py"
REAL_SCHEMA = ROOT / "docs/upstream-manifest.schema.json"

PIN = "1111111111111111111111111111111111111111"
HEAD = "3333333333333333333333333333333333333333"
URL = "https://github.com/mylinuxforwork/dotfiles.git"
VERIFIED = "2026-08-10T01:27:49Z"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("upstream_diff", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pinned_upstream(name: str = "ML4W") -> dict[str, str | None]:
    return {
        "name": name,
        "url": URL,
        "status": "pinned",
        "pinned_ref": PIN,
        "verified_on": VERIFIED,
    }


def _manifest(
    upstreams: dict[str, dict[str, object]] | None = None,
    owned_paths: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "version": 1,
        "provenance": {
            "verified_on": VERIFIED,
            "method": "verified",
            "command": "git ls-remote",
        },
        "upstreams": upstreams or {"ml4w": _pinned_upstream()},
        "owned_paths": owned_paths or {},
    }


class FakeGit:
    """Records every argv and answers per-command; unhandled calls fail the test."""

    def __init__(self, module: ModuleType) -> None:
        self.module = module
        self.calls: list[list[str]] = []
        self._handlers: list[tuple[Callable[[list[str]], bool], bytes | Exception]] = []

    def when(self, predicate: Callable[[list[str]], bool], outcome: bytes | Exception) -> FakeGit:
        self._handlers.append((predicate, outcome))
        return self

    def __call__(self, argv: list[str], cwd: Path, timeout: float) -> bytes:
        self.calls.append(list(argv))
        for predicate, outcome in self._handlers:
            if predicate(list(argv)):
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        raise AssertionError(f"unexpected git invocation: {' '.join(argv)}")

    def joined(self) -> str:
        return "\n".join(" ".join(call) for call in self.calls)


def _stub_git(module: ModuleType, fake: FakeGit) -> None:
    """Install the FakeGit as the module transport choke point."""
    setattr(module, "_run_git", fake)


def _success_diff_git(
    module: ModuleType, blob: bytes = b"upstream-content", tree: bytes = b"config/app.toml\0"
) -> FakeGit:
    fake = FakeGit(module)
    fake.when(lambda a: "init" in a, b"")
    fake.when(lambda a: "fetch" in a, b"")
    fake.when(lambda a: "cat-file" in a and "-e" in a, b"")
    fake.when(lambda a: "ls-tree" in a, tree)
    fake.when(lambda a: "cat-file" in a and "blob" in a, blob)
    return fake


@pytest.fixture
def env(tmp_path, monkeypatch):
    module = _load_module()
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "upstream-manifest.schema.json").write_text(REAL_SCHEMA.read_text())
    temp_base = tmp_path / "tmpbase"
    temp_base.mkdir()
    monkeypatch.setattr(module, "ROOT", repo)
    monkeypatch.setattr(module, "MANIFEST_PATH", docs / "upstream-manifest.json")
    monkeypatch.setattr(module, "SCHEMA_PATH", docs / "upstream-manifest.schema.json")
    monkeypatch.setattr(module, "_system_temp_base", lambda: temp_base)
    return SimpleNamespace(module=module, repo=repo, docs=docs, temp_base=temp_base)


def _write_manifest(env: SimpleNamespace, manifest: dict[str, object]) -> None:
    (env.docs / "upstream-manifest.json").write_text(json.dumps(manifest))


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_empty_mappings_no_fetch(env, capsys):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)  # no handlers: any git call is a test failure
    _stub_git(env.module, fake)
    assert env.module.main([]) == 0
    assert fake.calls == []
    out = capsys.readouterr().out
    assert "no owned mappings declared" in out
    assert "0 owned mapping(s)" in out


def test_json_empty_mappings(env, capsys):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    report = json.loads(captured.out)
    assert report["mode"] == "diff"
    assert report["ok"] is True
    assert report["result"] == "no-mappings"
    assert report["upstreams"]["ml4w"]["mappings"] == []
    assert report["upstreams"]["ml4w"]["pinned_ref"] == PIN


def test_real_manifest_reports_no_mappings_without_transport(capsys):
    module = _load_module()  # points at the real pinned phase-1 manifest
    fake = FakeGit(module)
    _stub_git(module, fake)
    assert module.main(["--json"]) == 0
    assert fake.calls == []
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "no-mappings"
    assert set(report["upstreams"]) == {"ml4w", "gentleman-dots"}


def test_same_mapping_reports_same(env, capsys):
    local = env.repo / "config/app.toml"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"upstream-content")
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    fake = _success_diff_git(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "clean"
    entry = report["upstreams"]["ml4w"]["mappings"][0]
    assert entry["status"] == "SAME"
    assert entry["local_bytes"] == len(b"upstream-content")
    assert entry["upstream_bytes"] == len(b"upstream-content")
    # exact-bytes contract: only init/fetch/read-only plumbing is ever used
    for call in fake.calls:
        assert not any(
            token == word for token in call for word in ("checkout", "worktree", "clone")
        )


def test_diff_mapping_reports_drift_without_failing(env, capsys):
    local = env.repo / "config/app.toml"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"locally edited content")
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    fake = _success_diff_git(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 0  # DIFF is information, exit 0
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "drift"
    entry = report["upstreams"]["ml4w"]["mappings"][0]
    assert entry["status"] == "DIFF"
    assert entry["local_bytes"] == len(b"locally edited content")
    assert entry["upstream_bytes"] == len(b"upstream-content")


def test_human_output_lists_drift(env, capsys):
    local = env.repo / "config/app.toml"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"local content")
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    env.module._run_git = _success_diff_git(env.module, blob=b"upstream content")
    assert env.module.main([]) == 0
    out = capsys.readouterr().out
    assert "DRIFT: config/app.toml" in out
    assert "ml4w: pinned" in out


def test_local_missing_reported(env, capsys):
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    fake = _success_diff_git(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "drift"
    entry = report["upstreams"]["ml4w"]["mappings"][0]
    assert entry["status"] == "LOCAL-MISSING"
    assert entry["upstream_bytes"] == len(b"upstream-content")


def test_upstream_missing_reported(env, capsys):
    local = env.repo / "config/app.toml"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"local-only content")
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    fake = _success_diff_git(env.module, tree=b"other/file\0")  # path absent upstream
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "drift"
    entry = report["upstreams"]["ml4w"]["mappings"][0]
    assert entry["status"] == "UPSTREAM-MISSING"
    assert entry["local_bytes"] == len(b"local-only content")
    # the blob was never requested for an absent upstream path
    assert all("blob" not in call for call in fake.calls)


@pytest.mark.parametrize(
    "manifest",
    [
        # non-HTTPS repository URL
        _manifest(
            upstreams={
                "ml4w": {
                    "name": "ML4W",
                    "url": "http://example.com/dots.git",
                    "status": "pinned",
                    "pinned_ref": PIN,
                    "verified_on": VERIFIED,
                }
            }
        ),
        # malformed pinned ref
        _manifest(upstreams={"ml4w": {**_pinned_upstream(), "pinned_ref": "not-a-sha"}}),
        # pinned upstream without any ref
        _manifest(
            upstreams={
                "ml4w": {"name": "ML4W", "url": URL, "status": "pinned", "verified_on": VERIFIED}
            }
        ),
        # unpinned upstream carrying a ref
        _manifest(
            upstreams={
                "ml4w": {
                    "name": "ML4W",
                    "url": URL,
                    "status": "unpinned",
                    "pinned_ref": PIN,
                    "verified_on": None,
                }
            }
        ),
        # unsafe local owned path
        _manifest(
            owned_paths={"../escape": {"upstream": "ml4w", "upstream_path": "config/app.toml"}}
        ),
        # unsafe upstream path
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "../../etc/passwd"}
            }
        ),
        # mapping referencing an unknown upstream
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ghost", "upstream_path": "config/app.toml"}
            }
        ),
        # nested ownership claims
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "a"},
                "config/app.toml/extra": {"upstream": "ml4w", "upstream_path": "b"},
            }
        ),
        # unsupported content: unknown mapping field
        _manifest(
            owned_paths={
                "config/app.toml": {
                    "upstream": "ml4w",
                    "upstream_path": "config/app.toml",
                    "surprise": True,
                }
            }
        ),
    ],
)
def test_invalid_manifest_rejected_before_transport(env, manifest, capsys):
    _write_manifest(env, manifest)
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    assert env.module.main() == 2
    assert fake.calls == []
    assert "upstream-diff:" in capsys.readouterr().err


def test_malformed_json_rejected_before_transport(env, capsys):
    (env.docs / "upstream-manifest.json").write_text("{definitely not json")
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    assert env.module.main() == 2
    assert fake.calls == []
    assert "upstream-diff:" in capsys.readouterr().err


def test_duplicate_json_key_rejected(env, capsys):
    raw = json.dumps(_manifest())
    raw = raw.replace('"version": 1', '"version": 1, "version": 1', 1)
    (env.docs / "upstream-manifest.json").write_text(raw)
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    assert env.module.main() == 2
    assert fake.calls == []
    assert "duplicate JSON key" in capsys.readouterr().err


def test_unknown_upstream_flag_rejected(env):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    with pytest.raises(SystemExit) as exc:
        env.module.main(["--upstream", "ghost"])
    assert exc.value.code == 2
    assert fake.calls == []


def test_arbitrary_url_flag_rejected(env):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    with pytest.raises(SystemExit) as exc:
        env.module.main(["--url", "https://example.com/evil.git"])
    assert exc.value.code == 2
    assert fake.calls == []


def test_transport_failure_fails_closed(env, capsys):
    local = env.repo / "config/app.toml"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"local")
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    fake = FakeGit(env.module)
    fake.when(lambda a: "init" in a, b"")
    fake.when(lambda a: "fetch" in a, env.module.GitError("boom: network unreachable"))
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""  # no partial JSON on stdout
    assert "boom: network unreachable" in captured.err


def test_check_pins_current(env, capsys):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    fake.when(lambda a: "ls-remote" in a, f"{PIN}\tHEAD\n".encode())
    _stub_git(env.module, fake)
    assert env.module.main(["--check-pins", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["mode"] == "check-pins"
    assert report["result"] == "pins-current"
    assert report["pins_stale"] == []
    assert report["upstreams"]["ml4w"]["status"] == "current"
    assert len(fake.calls) == 1


def _reachable_pin_git(module: ModuleType) -> FakeGit:
    """HEAD moved past the pin; the pinned commit is still fetchable by hash."""
    fake = FakeGit(module)
    fake.when(lambda a: "ls-remote" in a and a[-1] == "HEAD", f"{HEAD}\tHEAD\n".encode())
    fake.when(lambda a: "init" in a, b"")
    fake.when(lambda a: "fetch" in a and a[-1] == PIN, b"")
    fake.when(lambda a: "cat-file" in a and "-e" in a, b"")
    return fake


def test_check_pins_stale_reports_drift(env, capsys):
    _write_manifest(env, _manifest())
    fake = _reachable_pin_git(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--check-pins", "--json"]) == 0  # drift is report-only
    report = json.loads(capsys.readouterr().out)
    assert report["result"] == "pins-stale"
    assert report["pins_stale"] == ["ml4w"]
    assert report["upstreams"]["ml4w"]["status"] == "stale"
    assert "drift" in report["upstreams"]["ml4w"]["note"]


def test_check_pins_never_looks_a_hash_up_as_a_ref_name(env, capsys):
    # `git ls-remote <url> <sha>` matches ref NAMES, never hashes, so it always exits 2 for a
    # pin that is no longer the remote HEAD. Reachability must be checked by fetching the hash.
    _write_manifest(env, _manifest())
    fake = _reachable_pin_git(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--check-pins", "--json"]) == 0
    assert not any("ls-remote" in call and call[-1] == PIN for call in fake.calls)
    assert any("fetch" in call and call[-1] == PIN for call in fake.calls)


def test_check_pins_unreachable_pin_fails_closed(env, capsys):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    fake.when(lambda a: "ls-remote" in a and a[-1] == "HEAD", f"{HEAD}\tHEAD\n".encode())
    fake.when(lambda a: "init" in a, b"")
    fake.when(lambda a: "fetch" in a, env.module.GitError("upload-pack: not our ref"))
    _stub_git(env.module, fake)
    assert env.module.main(["--check-pins", "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no longer reachable" in captured.err


def test_check_pins_transport_failure_fails_closed(env, capsys):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    fake.when(lambda a: "ls-remote" in a, env.module.GitError("connection refused"))
    _stub_git(env.module, fake)
    assert env.module.main(["--check-pins"]) == 1
    assert "connection refused" in capsys.readouterr().err


def test_check_pins_missing_status_fails_closed(env, capsys):
    _write_manifest(env, _manifest())
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)

    def broken_pin_check(name: str, upstream: dict[str, object]) -> dict[str, object]:
        return {"name": name, "url": URL, "pinned_ref": PIN}

    env.module._check_pin = broken_pin_check
    assert env.module.main(["--check-pins", "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""  # no partial JSON on stdout
    assert "internal invariant violated" in captured.err
    assert fake.calls == []


def test_check_pins_skips_unpinned_upstream(env, capsys):
    _write_manifest(
        env,
        _manifest(
            upstreams={
                "ml4w": {
                    "name": "ML4W",
                    "url": URL,
                    "status": "unpinned",
                    "pinned_ref": None,
                    "verified_on": None,
                }
            }
        ),
    )
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--check-pins", "--json"]) == 0
    assert fake.calls == []
    report = json.loads(capsys.readouterr().out)
    assert report["upstreams"]["ml4w"]["status"] == "unpinned"
    assert report["result"] == "pins-current"


def test_unpinned_upstream_reported_without_transport(env, capsys):
    _write_manifest(
        env,
        _manifest(
            upstreams={
                "ml4w": {
                    "name": "ML4W",
                    "url": URL,
                    "status": "unpinned",
                    "pinned_ref": None,
                    "verified_on": None,
                }
            }
        ),
    )
    fake = FakeGit(env.module)
    _stub_git(env.module, fake)
    assert env.module.main(["--json"]) == 0
    assert fake.calls == []
    report = json.loads(capsys.readouterr().out)
    assert report["upstreams"]["ml4w"]["status"] == "unpinned"
    assert report["upstreams"]["ml4w"]["pinned_ref"] is None
    assert report["result"] == "no-mappings"


def test_repository_immutability(env, capsys):
    local = env.repo / "config/app.toml"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"local content")
    _write_manifest(
        env,
        _manifest(
            owned_paths={
                "config/app.toml": {"upstream": "ml4w", "upstream_path": "config/app.toml"}
            }
        ),
    )
    before = _snapshot(env.repo)
    fake = _success_diff_git(env.module, blob=b"upstream content differs")
    _stub_git(env.module, fake)
    assert env.module.main([]) == 0
    assert _snapshot(env.repo) == before  # no file touched or created
    for call in fake.calls:
        assert not any(
            token == forbidden
            for token in call
            for forbidden in ("checkout", "worktree", "clone", "commit", "push", "reset")
        )
    # the temporary bare repository was removed again
    assert list(env.temp_base.iterdir()) == []


def test_git_env_hardening(env, monkeypatch):
    module = env.module
    monkeypatch.setattr(
        module.os,
        "environ",
        {
            "HOME": "/home/tester",
            "PATH": "/usr/bin",
            "GIT_DIR": "/evil",
            "GIT_SSH_COMMAND": "evil",
            "GIT_ASKPASS": "evil",
            "LC_ALL": "fr_FR",
        },
    )
    git_env = module._git_env()
    assert git_env["GIT_CONFIG_NOSYSTEM"] == "1"
    assert git_env["GIT_CONFIG_SYSTEM"] == "/dev/null"
    assert git_env["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert git_env["GIT_TERMINAL_PROMPT"] == "0"
    assert git_env["GIT_ALLOW_PROTOCOL"] == "https"
    assert git_env["LC_ALL"] == "C"
    for redirected in ("GIT_DIR", "GIT_SSH_COMMAND", "GIT_ASKPASS"):
        assert redirected not in git_env
    assert git_env["HOME"] == "/home/tester"


def test_run_git_hardened_argv(env, monkeypatch):
    module = env.module
    recorded: dict[str, Any] = {}

    class FakeProc:
        returncode: int = 0
        pid: int = 999

        def __init__(self, *args: object, **kwargs: object) -> None:
            recorded["args"] = args
            recorded["kwargs"] = kwargs

        def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
            recorded["timeout"] = timeout
            return (b"stdout-data", b"")

    monkeypatch.setattr(module, "Popen", FakeProc)
    argv = ["git", "ls-remote", "--exit-code", URL, "HEAD"]
    out = module._run_git(argv, env.repo, 42.0)
    assert out == b"stdout-data"
    assert recorded["args"][0] == argv  # explicit argv list, never a shell string
    kwargs = recorded["kwargs"]
    assert kwargs["shell"] is False
    assert kwargs["start_new_session"] is True
    assert kwargs["stdout"] is PIPE and kwargs["stderr"] is PIPE
    assert kwargs["cwd"] == str(env.repo)
    assert kwargs["env"]["GIT_CONFIG_NOSYSTEM"] == "1"
    assert kwargs["env"]["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert kwargs["env"]["LC_ALL"] == "C"
    assert recorded["timeout"] == 42.0


def test_run_git_timeout_kills_process_group_and_fails_closed(env, monkeypatch):
    module = env.module
    killed: list[object] = []

    class FakeProc:
        pid: int = 1234
        returncode: int = 1

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def communicate(self, timeout: float | None = None) -> NoReturn:
            raise TimeoutExpired(cmd="git", timeout=timeout if timeout is not None else 0.0)

        def kill(self) -> None:
            killed.append("kill")

        def wait(self) -> int:
            return 1

    def _fake_getpgid(pid: int) -> int:
        return pid

    def _fake_killpg(pgid: int, sig: int) -> None:
        killed.append(sig)

    monkeypatch.setattr(module, "Popen", FakeProc)
    monkeypatch.setattr(module.os, "getpgid", _fake_getpgid)
    monkeypatch.setattr(module.os, "killpg", _fake_killpg)
    with pytest.raises(module.GitError, match="timed out"):
        module._run_git(["git", "fetch", URL, PIN], env.repo, 5.0)
    assert killed == [signal.SIGKILL]


def test_system_temp_base_never_home(monkeypatch, tmp_path):
    module = _load_module()
    fake_home = tmp_path / "home"
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(fake_home))
    monkeypatch.setattr(module.Path, "home", classmethod(lambda cls: fake_home))
    assert module._system_temp_base() == Path("/tmp")


def test_system_temp_base_keeps_foreign_dir(monkeypatch, tmp_path):
    module = _load_module()
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(tmp))
    monkeypatch.setattr(module.Path, "home", classmethod(lambda cls: tmp_path / "home"))
    assert module._system_temp_base() == tmp.resolve()
