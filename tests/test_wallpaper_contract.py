"""Wallpaper <-> UI contract: measurable limits a wallpaper must meet (T7).

Spec: odd/tasks/dreamcoder-light-coherence.md, T7 (S1, S2, S7); contract in L11.

The limits live in ``components.wallpaper.<mode>`` of tokens.json. Synthetic
images are built with ImageMagick in ``tmp_path`` and checked through the
public CLI (``scripts/check-wallpaper.py``) and the module API.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.wallpaper_contract import Finding, evaluate, load_contract

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
SCHEMA = ROOT / "DreamcoderThemes/dreamcoder/tokens.schema.json"
CHECKER = ROOT / "scripts/check-wallpaper.py"
UHD = "3840x2160"
CODES = (
    "WALLPAPER_SIZE",
    "WALLPAPER_LIGHTNESS",
    "WALLPAPER_CHROMA",
    "WALLPAPER_HUE",
    "WALLPAPER_SAFE_ZONE",
    "WALLPAPER_READABILITY",
)

needs_magick = pytest.mark.skipif(
    shutil.which("magick") is None,
    reason="ImageMagick `magick` is not installed; synthetic wallpapers cannot be built",
)


def _tokens() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(TOKENS.read_text(encoding="utf-8"))
    return loaded


def _image(path: Path, size: str, top: str, bottom: str | None = None, *draw: str) -> Path:
    """Write a PNG: flat colour, or a vertical gradient, plus filled rectangles."""
    source = f"gradient:{top}-{bottom}" if bottom else f"xc:{top}"
    command = ["magick", "-size", size, source]
    for fill, box in (item.split("@") for item in draw):
        command += ["-fill", fill, "-draw", f"rectangle {box}"]
    subprocess.run([*command, str(path)], check=True, capture_output=True)
    return path


def _calm_light(path: Path) -> Path:
    return _image(path, UHD, "#F4EEE4", "#EFE6D9")


def _calm_dark(path: Path) -> Path:
    return _image(path, UHD, "#1A1713", "#141210")


def _run(mode: str, *files: Path, tokens: Path | None = None) -> subprocess.CompletedProcess[str]:
    extra = ["--tokens", str(tokens)] if tokens else []
    return subprocess.run(
        [sys.executable, str(CHECKER), "--mode", mode, *extra, *map(str, files)],
        capture_output=True,
        text=True,
        check=False,
    )


def _codes(result: subprocess.CompletedProcess[str]) -> list[str]:
    return [code for line in result.stdout.splitlines() for code in CODES if f": {code}:" in line]


# --- contract values come from tokens.json ----------------------------------


def test_contract_validates_against_the_schema() -> None:
    jsonschema.validate(_tokens(), json.loads(SCHEMA.read_text(encoding="utf-8")))


def test_contract_values_match_the_spec() -> None:
    wallpaper = _tokens()["components"]["wallpaper"]
    assert set(wallpaper) == {"light", "dark"}
    for mode, band in (("light", (0.86, 0.97)), ("dark", (0.08, 0.22))):
        contract = wallpaper[mode]
        assert contract["size"] == {
            "min_width": 3840,
            "min_height": 2160,
            "aspect": {"width": 16, "height": 9, "tolerance": 0.01},
        }
        assert (contract["lightness"]["min"], contract["lightness"]["max"]) == band
        assert contract["chroma"] == {"p95_max": 0.06, "mean_max": 0.035}
        assert contract["hue"] == {"center": 70, "tolerance": 25, "min_mean_chroma": 0.01}
        safe = contract["safe_zone"]
        assert (safe["fraction"], safe["max_std_lightness"]) == (0.06, 0.035)
        assert contract["readability"] == {
            "worst_fraction": 0.01,
            "text_min": 7,
            "muted_min": 4.5,
            "panel_text_min": 7,
        }
    assert wallpaper["light"]["safe_zone"]["min_mean_lightness"] == 0.88
    assert "min_mean_lightness" not in wallpaper["dark"]["safe_zone"]


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (["light", "size", "min_width"], "3840"),
        (["light", "size", "min_height"], 0),
        (["light", "size", "aspect", "tolerance"], -0.01),
        (["light", "lightness", "max"], 1.5),
        (["dark", "lightness", "min"], -0.1),
        (["light", "chroma", "p95_max"], "0.06"),
        (["light", "chroma", "mean_max"], -1),
        (["light", "hue", "center"], 360),
        (["light", "hue", "tolerance"], 0),
        (["light", "safe_zone", "fraction"], 0.9),
        (["light", "safe_zone", "min_mean_lightness"], 2),
        (["light", "readability", "text_min"], 0.5),
        (["light", "readability", "worst_fraction"], 0),
        (["light", "safe_zone", "surprise"], 1),
        (["light", "readability", "muted_min"], None),
        (["sepia"], {}),
    ],
)
def test_schema_rejects_a_malformed_entry(path: list[str], value: object) -> None:
    tokens = copy.deepcopy(_tokens())
    node = tokens["components"]["wallpaper"]
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = value
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, json.loads(SCHEMA.read_text(encoding="utf-8")))


@pytest.mark.parametrize("missing", ["size", "lightness", "chroma", "hue", "safe_zone"])
def test_schema_rejects_a_contract_missing_a_rule(missing: str) -> None:
    tokens = copy.deepcopy(_tokens())
    del tokens["components"]["wallpaper"]["light"][missing]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, json.loads(SCHEMA.read_text(encoding="utf-8")))


def test_schema_rejects_a_missing_wallpaper_component() -> None:
    tokens = copy.deepcopy(_tokens())
    del tokens["components"]["wallpaper"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, json.loads(SCHEMA.read_text(encoding="utf-8")))


def test_load_contract_reads_the_mode_entry_and_rejects_unknown_modes() -> None:
    tokens = _tokens()
    assert load_contract(tokens, "dark") == tokens["components"]["wallpaper"]["dark"]
    with pytest.raises(KeyError):
        load_contract(tokens, "sepia")


# --- module API over pixel lists --------------------------------------------

GRID = 48
ROWS = 27


def _flat(color: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    return [color] * (GRID * ROWS)


def _eval(
    pixels: list[tuple[int, int, int]],
    mode: str = "light",
    size: tuple[int, int] = (3840, 2160),
    contract: dict[str, Any] | None = None,
    palette: dict[str, str] | None = None,
) -> list[Finding]:
    return evaluate(
        pixels,
        grid_width=GRID,
        source_size=size,
        mode=mode,
        contract=contract or load_contract(_tokens(), mode),
        palette=palette or VARIANTS[mode],
    )


def test_module_calm_paper_has_no_findings() -> None:
    assert _eval(_flat((244, 238, 228))) == []


def test_module_findings_have_a_stable_code_and_message_and_one_per_rule() -> None:
    findings = _eval(_flat((20, 18, 16)), size=(1280, 720))
    codes = [finding.code for finding in findings]
    assert len(codes) == len(set(codes))
    assert {"WALLPAPER_SIZE", "WALLPAPER_LIGHTNESS", "WALLPAPER_SAFE_ZONE"} <= set(codes)
    assert all(finding.message for finding in findings)


def test_module_size_rule_covers_dimensions_and_aspect() -> None:
    paper = _flat((244, 238, 228))
    assert [f.code for f in _eval(paper, size=(3840, 2159))] == ["WALLPAPER_SIZE"]
    assert [f.code for f in _eval(paper, size=(3840, 2400))] == ["WALLPAPER_SIZE"]
    assert _eval(paper, size=(7680, 4320)) == []


def test_module_contract_values_drive_the_decision() -> None:
    paper = _flat((244, 238, 228))
    tight = copy.deepcopy(load_contract(_tokens(), "light"))
    tight["lightness"]["max"] = 0.5
    assert [f.code for f in _eval(paper, contract=tight)] == ["WALLPAPER_LIGHTNESS"]
    tight = copy.deepcopy(load_contract(_tokens(), "light"))
    tight["hue"]["center"] = 250
    assert [f.code for f in _eval(paper, contract=tight)] == ["WALLPAPER_HUE"]


def test_module_hue_is_ignored_below_the_minimum_mean_chroma() -> None:
    assert _eval(_flat((236, 236, 236))) == []


def test_module_readability_uses_the_palette_overlay_over_the_worst_top_pixels() -> None:
    pixels = _flat((244, 238, 228))
    pixels[0] = (0, 0, 0)
    palette = dict(VARIANTS["light"], module_rgba="rgba(237, 233, 227, 0.10)")
    codes = [f.code for f in _eval(pixels, palette=palette)]
    assert "WALLPAPER_READABILITY" in codes
    assert "WALLPAPER_READABILITY" not in [f.code for f in _eval(pixels)]


def test_module_dark_readability_looks_at_the_lightest_pixels() -> None:
    pixels = _flat((26, 23, 19))
    assert _eval(pixels, mode="dark") == []
    for index in range(GRID):
        pixels[index] = (250, 244, 232)
    codes = [f.code for f in _eval(pixels, mode="dark")]
    assert "WALLPAPER_READABILITY" in codes
    assert "WALLPAPER_SAFE_ZONE" in codes


# --- public CLI over synthetic images ---------------------------------------


@needs_magick
def test_cli_calm_warm_paper_passes_for_light(tmp_path: Path) -> None:
    image = _calm_light(tmp_path / "paper.png")
    result = _run("light", image)
    assert (result.returncode, result.stdout, result.stderr) == (0, f"OK {image}\n", "")


@needs_magick
def test_cli_calm_dark_passes_for_dark(tmp_path: Path) -> None:
    image = _calm_dark(tmp_path / "night.png")
    result = _run("dark", image)
    assert (result.returncode, result.stdout, result.stderr) == (0, f"OK {image}\n", "")


@needs_magick
def test_cli_mode_mismatch_is_reported(tmp_path: Path) -> None:
    light = _calm_light(tmp_path / "paper.png")
    dark = _calm_dark(tmp_path / "night.png")
    assert "WALLPAPER_LIGHTNESS" in _codes(_run("dark", light))
    assert "WALLPAPER_LIGHTNESS" in _codes(_run("light", dark))


def _small(path: Path) -> Path:
    return _image(path, "1672x941", "#F4EEE4")


def _too_dark(path: Path) -> Path:
    return _image(path, UHD, "#4A4440", "#3A3532")


def _orange(path: Path) -> Path:
    return _image(path, UHD, "#FFD0A0")


def _blue(path: Path) -> Path:
    return _image(path, UHD, "#E6EEF6")


def _busy_top(path: Path) -> Path:
    stripes = [f"#C9BBA6@{x},0 {x + 99},129" for x in range(0, 3840, 200)]
    return _image(path, UHD, "#F4EEE4", "#EFE6D9", *stripes)


def _blotch(path: Path) -> Path:
    return _image(path, UHD, "#F4EEE4", "#EFE6D9", "#3A3A3A@1200,0 2600,129")


@needs_magick
@pytest.mark.parametrize(
    ("build", "expected"),
    [
        (_small, "WALLPAPER_SIZE"),
        (_too_dark, "WALLPAPER_LIGHTNESS"),
        (_orange, "WALLPAPER_CHROMA"),
        (_blue, "WALLPAPER_HUE"),
        (_busy_top, "WALLPAPER_SAFE_ZONE"),
        (_blotch, "WALLPAPER_SAFE_ZONE"),
    ],
)
def test_cli_reports_each_violation_with_its_stable_code(
    tmp_path: Path, build: Any, expected: str
) -> None:
    image = build(tmp_path / "wall.png")
    result = _run("light", image)
    codes = _codes(result)
    assert result.returncode == 1
    assert result.stderr == ""
    assert expected in codes
    assert len(codes) == len(set(codes)), "one finding per rule"
    assert f"OK {image}" not in result.stdout
    assert all(line.startswith(f"{image}: WALLPAPER_") for line in result.stdout.splitlines())


@needs_magick
@pytest.mark.parametrize(
    ("build", "only"),
    [
        (_small, "WALLPAPER_SIZE"),
        (_orange, "WALLPAPER_CHROMA"),
        (_blue, "WALLPAPER_HUE"),
    ],
)
def test_cli_isolated_violations_raise_only_their_own_code(
    tmp_path: Path, build: Any, only: str
) -> None:
    assert _codes(_run("light", build(tmp_path / "wall.png"))) == [only]


@needs_magick
def test_cli_dark_blotch_under_the_bar_breaks_readability_and_safe_zone(tmp_path: Path) -> None:
    image = _image(tmp_path / "night.png", UHD, "#1A1713", "#141210", "#F2EBE0@1200,0 2600,129")
    result = _run("dark", image)
    assert result.returncode == 1
    assert {"WALLPAPER_READABILITY", "WALLPAPER_SAFE_ZONE"} <= set(_codes(result))


@needs_magick
def test_cli_checks_every_file_and_fails_if_any_fails(tmp_path: Path) -> None:
    good = _calm_light(tmp_path / "good.png")
    bad = _orange(tmp_path / "bad.png")
    result = _run("light", good, bad)
    assert result.returncode == 1
    assert f"OK {good}\n" in result.stdout
    assert f"{bad}: WALLPAPER_CHROMA:" in result.stdout


@needs_magick
def test_cli_unreadable_file_is_a_finding_not_a_crash(tmp_path: Path) -> None:
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    for target in (broken, tmp_path / "missing.png"):
        result = _run("light", target)
        assert result.returncode == 1
        assert f"{target}: WALLPAPER_UNREADABLE:" in result.stdout
        assert "Traceback" not in result.stderr


@needs_magick
def test_cli_limits_come_from_the_tokens_file(tmp_path: Path) -> None:
    image = _calm_light(tmp_path / "paper.png")
    assert _run("light", image).returncode == 0
    tokens = _tokens()
    tokens["components"]["wallpaper"]["light"]["lightness"] = {"min": 0.1, "max": 0.5}
    edited = tmp_path / "tokens.json"
    edited.write_text(json.dumps(tokens), encoding="utf-8")
    result = _run("light", image, tokens=edited)
    assert result.returncode == 1
    assert _codes(result) == ["WALLPAPER_LIGHTNESS"]


@needs_magick
def test_cli_has_no_side_effects(tmp_path: Path) -> None:
    image = _calm_light(tmp_path / "paper.png")
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    _run("light", image)
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_cli_help_describes_the_checker() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "light" in result.stdout
    assert "dark" in result.stdout
    assert "wallpaper" in result.stdout.lower()


def test_cli_requires_a_mode_and_a_file() -> None:
    for args in ([], ["--mode", "light"], ["--mode", "sepia", "x.png"]):
        result = subprocess.run(
            [sys.executable, str(CHECKER), *args], capture_output=True, text=True, check=False
        )
        assert result.returncode == 2
        assert result.stdout == ""
