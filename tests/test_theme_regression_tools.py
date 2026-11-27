"""Visual regression tools: perceptual diff, specimen board and `make theme-check`.

Spec: odd/tasks/dreamcoder-light-coherence.md, T10 (S4). Every test goes through the
public command line, never through module internals.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest

from dreamcoder_theme.color_space import delta_e2000

ROOT = Path(__file__).resolve().parents[1]
THEME_DIFF = ROOT / "scripts/theme-diff.py"
SPECIMEN = ROOT / "scripts/generate-specimen.py"
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
TOKENS_RELATIVE = "DreamcoderThemes/dreamcoder/tokens.json"

PIGMENT_ROLES = (
    "accent",
    "accent_2",
    "error",
    "warning",
    "success",
    "sage",
    "focus",
    "diagnostic",
    "info",
    "lavender",
    "mauve",
)

LIGHT: dict[str, str] = {
    "bg": "#f9f6f2",
    "surface0": "#fefdfa",
    "surface1": "#ede9e3",
    "surface2": "#e3ddd5",
    "text": "#1e1813",
    "muted": "#2b241e",
    "comment": "#5f544c",
    "accent": "#874004",
    "error": "#9c2024",
    "border_ui": "#5f544c",
    "focus": "#016367",
}
GUARDRAILS = {
    "minimum_text_contrast": 4.5,
    "minimum_apca_body": 75,
    "minimum_apca_ui": 60,
}


def _run(*args: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    # pre-commit exports GIT_INDEX_FILE (and hooks may set GIT_DIR/GIT_WORK_TREE): a scratch
    # repo that inherited them would write the caller's real index.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        [str(a) for a in args], capture_output=True, text=True, check=False, cwd=cwd, env=env
    )


def _tokens(path: Path, light: dict[str, str]) -> Path:
    document = {"guardrails": GUARDRAILS, "modes": {"light": light}}
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _diff(
    tmp_path: Path, base: dict[str, str], head: dict[str, str], *flags: str
) -> subprocess.CompletedProcess[str]:
    base_file = _tokens(tmp_path / "base.json", base)
    head_file = _tokens(tmp_path / "head.json", head)
    return _run(
        sys.executable, THEME_DIFF, "--base-file", base_file, "--head-file", head_file, *flags
    )


# -- theme-diff -----------------------------------------------------------------------


def test_identical_inputs_report_no_perceptual_change(tmp_path: Path) -> None:
    first = _diff(tmp_path, LIGHT, LIGHT)
    second = _diff(tmp_path, LIGHT, LIGHT, "--fail-on-floor")
    assert first.returncode == 0, first.stderr
    assert first.stdout == "theme-diff: no perceptual change (11 roles compared)\n"
    assert first.stderr == ""
    assert second.returncode == 0
    assert second.stdout == first.stdout


def test_changed_roles_report_delta_e_and_mark_the_visible_ones(tmp_path: Path) -> None:
    head = {**LIGHT, "accent": "#874105", "error": "#8c1f3a"}
    result = _diff(tmp_path, LIGHT, head)
    small = f"{delta_e2000(LIGHT['accent'], head['accent']):.2f}"
    large = f"{delta_e2000(LIGHT['error'], head['error']):.2f}"
    assert float(small) < 2 <= float(large)
    assert result.returncode == 0, result.stderr
    lines = {line.split()[0]: line for line in result.stdout.splitlines() if "." in line.split()[0]}
    assert f"ΔE {small}" in lines["light.accent"]
    assert "≥2" not in lines["light.accent"]
    assert f"ΔE {large}" in lines["light.error"]
    assert "≥2" in lines["light.error"]
    assert "#9c2024 -> #8c1f3a" in lines["light.error"]
    assert "light.text" not in result.stdout
    assert "summary: 2 of 11 roles changed, 1 at or above ΔE 2, " in result.stdout
    assert f"max ΔE {large} (light.error)" in result.stdout
    assert f"min ΔE {small} (light.accent)" in result.stdout
    assert "floors crossed: 0" in result.stdout


def test_a_crossed_contrast_floor_is_reported_and_fails_only_on_request(tmp_path: Path) -> None:
    head = {**LIGHT, "text": "#b0a69c"}
    informative = _diff(tmp_path, LIGHT, head)
    gated = _diff(tmp_path, LIGHT, head, "--fail-on-floor")
    assert informative.returncode == 0, informative.stderr
    floor_lines = [x for x in informative.stdout.splitlines() if x.startswith("FLOOR ")]
    assert any("light.text on bg" in line and "WCAG" in line for line in floor_lines)
    assert any("light.text on bg" in line and "APCA" in line for line in floor_lines)
    assert "floors crossed: " in informative.stdout
    assert "floors crossed: 0" not in informative.stdout
    assert gated.returncode == 1
    assert gated.stdout == informative.stdout


def test_a_floor_that_was_already_failing_is_not_a_crossing(tmp_path: Path) -> None:
    weak = {**LIGHT, "comment": "#b0a69c"}
    weaker = {**LIGHT, "comment": "#a89e94"}
    result = _diff(tmp_path, weak, weaker, "--fail-on-floor")
    assert result.returncode == 0, result.stderr
    assert "FLOOR" not in result.stdout
    assert "floors crossed: 0" in result.stdout


def test_a_git_ref_is_compared_against_the_working_tree(tmp_path: Path) -> None:
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    (repo / "DreamcoderThemes/dreamcoder").mkdir(parents=True)
    tokens = _tokens(repo / TOKENS_RELATIVE, LIGHT)
    env = ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
    for command in (["init", "-q"], ["add", "."], [*env, "commit", "-q", "-m", "base"]):
        assert _run("git", *command, cwd=repo).returncode == 0
    _tokens(tokens, {**LIGHT, "error": "#8c1f3a"})

    result = _run(sys.executable, THEME_DIFF, "HEAD", "--repo", repo)
    assert result.returncode == 0, result.stderr
    assert "light.error" in result.stdout
    assert "base HEAD" in result.stdout
    assert "1 of 11 roles changed" in result.stdout

    missing = _run(sys.executable, THEME_DIFF, "no-such-ref", "--repo", repo)
    assert missing.returncode == 2
    assert missing.stdout == ""
    assert "no-such-ref" in missing.stderr


def test_help_documents_every_option() -> None:
    result = _run(sys.executable, THEME_DIFF, "--help")
    assert result.returncode == 0
    for option in ("REF", "--base-file", "--head-file", "--repo", "--fail-on-floor"):
        assert option in result.stdout


def test_the_feature_branch_diffs_against_itself_without_change() -> None:
    result = _run(
        sys.executable, THEME_DIFF, "--base-file", TOKENS, "--head-file", TOKENS, "--fail-on-floor"
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("theme-diff: no perceptual change (")


# -- specimen -------------------------------------------------------------------------


def test_specimen_is_deterministic_and_lists_every_primitive_and_pigment_role(
    tmp_path: Path,
) -> None:
    first, second = tmp_path / "a" / "one.svg", tmp_path / "b.svg"
    one = _run(sys.executable, SPECIMEN, "--output", first)
    two = _run(sys.executable, SPECIMEN, "--output", second)
    assert one.returncode == 0, one.stderr
    assert two.returncode == 0, two.stderr
    assert one.stdout == f"wrote {first}\n"
    assert first.read_bytes() == second.read_bytes()

    root = ET.fromstring(first.read_text(encoding="utf-8"))
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    text = "".join(root.itertext())
    primitives: dict[str, Any] = json.loads(TOKENS.read_text(encoding="utf-8"))["primitives"][
        "light"
    ]
    for name in primitives:
        assert name in text, name
    for role in PIGMENT_ROLES:
        assert role in text, role
    for level in ("e0", "e1", "e2", "e3", "e4"):
        assert level in text, level
    assert re.search(r"\d+\.\d{2}:1", text), "contrast numbers missing"
    assert "ΔE" in text


def test_specimen_regenerates_the_checked_in_board_byte_for_byte(tmp_path: Path) -> None:
    checked_in = ROOT / "docs/generated/dreamcoder-light-specimen.svg"
    fresh = tmp_path / "fresh.svg"
    assert _run(sys.executable, SPECIMEN, "--output", fresh).returncode == 0
    assert checked_in.read_bytes() == fresh.read_bytes()


DARK_SPECIMEN = ROOT / "docs/generated/dreamcoder-dark-specimen.svg"
DARK_PIGMENT_FAMILIES = (
    "madder",
    "ochre",
    "malachite",
    "verdigris",
    "indigo",
    "iris",
    "violet",
    "cochineal",
)


def test_dark_specimen_is_deterministic_and_lists_every_dark_primitive_and_pigment_role(
    tmp_path: Path,
) -> None:
    first, second = tmp_path / "a" / "one.svg", tmp_path / "b.svg"
    one = _run(sys.executable, SPECIMEN, "--mode", "dark", "--output", first)
    two = _run(sys.executable, SPECIMEN, "--mode", "dark", "--output", second)
    assert one.returncode == 0, one.stderr
    assert two.returncode == 0, two.stderr
    assert one.stdout == f"wrote {first}\n"
    assert first.read_bytes() == second.read_bytes()

    root = ET.fromstring(first.read_text(encoding="utf-8"))
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    text = "".join(root.itertext())
    tokens: dict[str, Any] = json.loads(TOKENS.read_text(encoding="utf-8"))
    for name in tokens["primitives"]["dark"]:
        assert name in text, name
    for family in DARK_PIGMENT_FAMILIES:
        assert any(n.startswith(f"{family}.") for n in tokens["primitives"]["dark"]), family
    for role in (*PIGMENT_ROLES, "selection", "text_heading", "comment", "subtle"):
        assert role in text, role
    for level in ("e0", "e1", "e2", "e3", "e4"):
        assert level in text, level
    assert "Dreamcoder Dark specimen" in text
    assert "Light" not in text
    assert re.search(r"\d+\.\d{2}:1", text), "contrast numbers missing"
    assert "Lc" in text
    assert "ΔE" in text


def test_dark_specimen_draws_tonal_elevation_without_visible_shadows(tmp_path: Path) -> None:
    out = tmp_path / "dark.svg"
    assert _run(sys.executable, SPECIMEN, "--mode", "dark", "--output", out).returncode == 0
    svg = out.read_text(encoding="utf-8")
    assert "feDropShadow" not in svg
    assert "filter=" not in svg
    tokens: dict[str, Any] = json.loads(TOKENS.read_text(encoding="utf-8"))
    edges = tokens["components"]["elevation"]["edge"]["dark"]
    assert set(edges) == {"e3", "e4"}
    assert "top edge" in "".join(ET.fromstring(svg).itertext())


def test_dark_specimen_regenerates_the_checked_in_board_byte_for_byte(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh.svg"
    assert _run(sys.executable, SPECIMEN, "--mode", "dark", "--output", fresh).returncode == 0
    assert DARK_SPECIMEN.read_bytes() == fresh.read_bytes()


def test_the_default_mode_is_light_and_writes_the_light_board(tmp_path: Path) -> None:
    explicit, default = tmp_path / "explicit.svg", tmp_path / "default.svg"
    assert _run(sys.executable, SPECIMEN, "--mode", "light", "--output", explicit).returncode == 0
    assert _run(sys.executable, SPECIMEN, "--output", default).returncode == 0
    assert explicit.read_bytes() == default.read_bytes()
    assert "Dreamcoder Light specimen" in default.read_text(encoding="utf-8")


def test_the_specimen_rejects_an_unknown_mode() -> None:
    result = _run(sys.executable, SPECIMEN, "--mode", "sepia", "--output", "/dev/null")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


@pytest.mark.skipif(shutil.which("make") is None, reason="make not installed")
def test_make_specimen_regenerates_both_modes() -> None:
    result = _run("make", "-n", "specimen", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if "generate-specimen.py" in line]
    assert len(lines) == 2
    assert any("--mode" not in line for line in lines), "the light board keeps the bare command"
    assert any("--mode dark" in line for line in lines)


def test_the_preview_hook_regenerates_and_checks_both_specimens() -> None:
    hook = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    entry = next(line for line in hook.splitlines() if "generate-theme-preview.py" in line)
    assert "generate-specimen.py --mode dark" in entry
    assert "docs/generated/dreamcoder-light-specimen.svg" in entry
    assert "docs/generated/dreamcoder-dark-specimen.svg" in entry


# -- make theme-check -----------------------------------------------------------------


@pytest.mark.skipif(shutil.which("make") is None, reason="make not installed")
def test_theme_check_lists_every_step_without_running_them() -> None:
    result = _run("make", "-n", "theme-check", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    out = result.stdout
    for step in (
        "sync-dreamcoder-theme.py",
        "DREAMCODER_WRITE_LIVE=0",
        "git diff --exit-code",
        "verify-theme-health.py",
        "pytest",
        "check-wallpaper.py",
    ):
        assert step in out, step
    assert out.index("sync-dreamcoder-theme.py") < out.index("git diff --exit-code")
    assert out.index("git diff --exit-code") < out.index("verify-theme-health.py")
    assert out.index("verify-theme-health.py") < out.index("pytest")
    assert out.index("pytest") < out.index("check-wallpaper.py")


@pytest.mark.skipif(shutil.which("make") is None, reason="make not installed")
@pytest.mark.parametrize(
    ("target", "script"), [("theme-diff", "theme-diff.py"), ("specimen", "generate-specimen.py")]
)
def test_helper_targets_run_their_script(target: str, script: str) -> None:
    result = _run("make", "-n", target, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    assert script in result.stdout


@pytest.mark.skipif(shutil.which("make") is None, reason="make not installed")
def test_existing_make_targets_are_untouched() -> None:
    result = _run("make", "-n", "python-lint", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    assert "ruff check src/ tests/" in result.stdout
    assert "ruff format --check src/ tests/" in result.stdout


def test_theme_check_checks_each_wallpaper_mode_with_its_own_mode_flag() -> None:
    dry = _run("make", "-n", "theme-check", cwd=ROOT)
    assert dry.returncode == 0, dry.stderr
    for mode in ("light", "dark"):
        assert f"DreamcoderWallpapers/dreamcoder-{mode}-*.png" in dry.stdout
        assert f"--mode {mode}" in dry.stdout


@pytest.mark.skipif(shutil.which("make") is None, reason="make not installed")
def test_failing_wallpaper_check_stops_make_before_the_next_mode(tmp_path: Path) -> None:
    (tmp_path / "DreamcoderWallpapers").mkdir()
    for mode in ("light", "dark"):
        (tmp_path / "DreamcoderWallpapers" / f"dreamcoder-{mode}-a b.png").write_bytes(b"x")
    probe = tmp_path / "probe.mk"
    probe.write_text(
        "probe:\n\t$(call check_wallpapers,light)\n\t$(call check_wallpapers,dark)\n\techo END\n",
        encoding="utf-8",
    )
    result = _run(
        "make", "-f", ROOT / "Makefile", "-f", probe, "probe", "PYTHON=false", cwd=tmp_path
    )
    assert result.returncode != 0
    assert "--mode light" in result.stdout
    assert "--mode dark" not in result.stdout
    assert "END" not in result.stdout
