"""``dreamcoder sync`` must parse its arguments before touching anything.

``main()`` used to ignore ``sys.argv``: ``dreamcoder sync --help`` ran a full sync
against the live configuration instead of printing usage.
"""

from __future__ import annotations

import pytest

from dreamcoder_theme import sync


@pytest.fixture
def no_side_effects(monkeypatch):
    # Python 3.14 colours argparse output when FORCE_COLOR is set (the Dreamcoder
    # shell exports it); keep the assertions independent of the ambient terminal.
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    monkeypatch.delenv("CLICOLOR_FORCE", raising=False)
    monkeypatch.setenv("NO_COLOR", "1")
    calls: list[str] = []

    def boom(name: str):
        def _fail(*_a, **_k):
            calls.append(name)
            raise AssertionError(f"{name} ran before argument parsing finished")

        return _fail

    monkeypatch.setattr(sync.subprocess, "run", boom("subprocess.run"))
    monkeypatch.setattr(sync, "theme_paths", boom("theme_paths"))
    monkeypatch.setattr(sync, "prepare", boom("prepare"))
    return calls


def test_help_prints_usage_and_exits_zero_without_syncing(no_side_effects, capsys):
    with pytest.raises(SystemExit) as exc:
        sync.main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "usage: dreamcoder sync" in out
    assert "DREAMCODER_THEME_MODE" in out
    assert no_side_effects == []


def test_unknown_argument_is_rejected_without_syncing(no_side_effects, capsys):
    with pytest.raises(SystemExit) as exc:
        sync.main(["--frobnicate"])
    assert exc.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
    assert no_side_effects == []
