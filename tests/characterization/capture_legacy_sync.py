"""Characterization harness for the current (legacy) sync plan.

Hexagonal-architecture-v2 Phase 0 tasks 0.2 + 0.3: capture, for all 33
consumers declared by ``sync.py:COVERAGE``, the resolved active path,
repository variant paths per mode, mode set, writer/selector behavior,
summary rows (via the real ``print_summary``), and the rendered content
hashes produced by the current ``prepare()``/render path — WITHOUT running
any writer, selector, or filesystem mutation.

Variant paths are derived from the authoritative ``COVERAGE.artifact`` (Dark)
row by mode substitution ("dark" -> light, "Dark" -> Light), which matches
every current repository artifact naming pattern.

Outputs (deterministic, sorted):
  - tests/fixtures/legacy_sync_characterization.json
  - tests/fixtures/legacy_output_hashes.json

Run:  python tests/characterization/capture_legacy_sync.py
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
SRC = REPO_ROOT / "src"
FIXTURES = HERE.parent / "fixtures"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme.herdr_contract import SUPPORTED_PROFILES  # noqa: E402
from dreamcoder_theme.renderers import (  # noqa: E402
    antigravity_content,
    bat_content,
    btop_content,
    cava_content,
    codex_tmtheme_content,
    delta_content,
    dunst_content,
    firefox_content,
    fzf_content,
    ghostty_content,
    hypr_colors_conf_content,
    hypr_colors_lua_content,
    hypr_content,
    kitty_content,
    kitty_ui_content,
    lazygit_content,
    ls_colors_content,
    nvim_content,
    obsidian_content,
    opencode_content,
    pi_theme_content,
    rofi_content,
    rofi_matugen_content,
    starship_content,
    tmux_content,
    warp_content,
    waybar_content,
    waybar_matugen_content,
    zsh_syntax_content,
)
from dreamcoder_theme.renderers_herdr import herdr_content  # noqa: E402
from dreamcoder_theme.settings import ROOT, theme_paths  # noqa: E402
from dreamcoder_theme.sync import COVERAGE, prepare, print_summary  # noqa: E402

MODES = ("dark", "light")

# Builders used by the current sync path for repository variant artifacts.
BUILDERS = {
    "kitty": kitty_content,
    "kitty_ui": kitty_ui_content,
    "ghostty": ghostty_content,
    "warp": warp_content,
    "starship": starship_content,
    "codex_app": opencode_content,
    "codex_theme": codex_tmtheme_content,
    "bat_theme": codex_tmtheme_content,
    "pi_theme": pi_theme_content,
    "antigravity": antigravity_content,
    "tmux": tmux_content,
    "lazygit": lazygit_content,
    "zsh_syntax": zsh_syntax_content,
    "ls_colors": ls_colors_content,
    "bat": bat_content,
    "delta": delta_content,
    "fzf": fzf_content,
    "btop": btop_content,
    "dunst": dunst_content,
    "firefox": firefox_content,
    "obsidian": obsidian_content,
    "cava": cava_content,
    "nvim": nvim_content,
    "hyprland": hypr_content,
    "hypr_colors_lua": hypr_colors_lua_content,
    "hypr_colors_conf": hypr_colors_conf_content,
    "waybar": waybar_content,
    "rofi": rofi_content,
}

# Active (live) path per consumer as resolved by the current sync path.
# Values are ThemePaths attribute names; "repo:<relpath>" marks an active file
# that lives in the repository; None marks repo-only consumers.
ACTIVE_PATHS: dict[str, str | None] = {
    "kitty": "kitty",
    "kitty_ui": "kitty_ui",
    "ghostty": "ghostty",
    "warp": "warp",
    "starship": "starship",
    "codex_app": None,
    "codex_theme": "codex_theme",
    "bat_theme": "bat_theme_dir",
    "pi_theme": "pi_theme",
    "antigravity": None,
    "tmux": "tmux",
    "lazygit": "lazygit",
    "zsh_syntax": "zsh_syntax",
    "ls_colors": "ls_colors",
    "bat": "bat",
    "delta": "delta",
    "fzf": "fzf",
    "btop": "btop",
    "dunst": "dunst",
    "firefox": "firefox",
    "obsidian": "obsidian",
    "cava": "cava",
    "opencode": "opencode",
    "zellij": None,  # selector-only active behavior (zellij_config)
    "nvim": "nvim",
    "hyprland": "repo:DreamcoderThemes/dreamcoder/hyprland.conf",
    "hypr_colors_lua": "hypr_colors_lua",
    "hypr_colors_conf": "hypr_colors_conf",
    "waybar": "repo:DreamcoderThemes/dreamcoder/waybar.css",
    "waybar_matugen": "active:waybar/colors.css",
    "rofi": "repo:DreamcoderThemes/dreamcoder/rofi.rasi",
    "rofi_matugen": "active:rofi/colors.rasi",
    "herdr": None,
}


def rel(p: Path) -> str:
    """Deterministic POSIX path relative to the repository root."""
    resolved = p if p.is_absolute() else ROOT / p
    try:
        return resolved.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def variant_paths_for(row) -> dict[str, str | None]:
    """Per-mode repository artifact paths from the COVERAGE (Dark) artifact."""
    artifact = row.artifact
    if artifact.startswith("active:"):
        return {m: artifact for m in MODES}
    out: dict[str, str | None] = {}
    for mode in MODES:
        resolved = artifact
        if "<version>" in resolved:
            complete = next(
                (p for p in SUPPORTED_PROFILES if p is not None and p.is_complete), None
            )
            resolved = resolved.replace(
                "<version>", complete.evidence.version if complete else "unknown"
            )
        out[mode] = resolved.replace("dark", mode).replace("Dark", mode.title())
    return out


def active_path_for(row, paths) -> str | None:
    spec = ACTIVE_PATHS[row.consumer_id]
    if spec is None:
        return None
    if spec.startswith("repo:"):
        return rel(ROOT / spec.removeprefix("repo:"))
    if spec.startswith("active:"):
        return spec
    return rel(getattr(paths, spec))


def sha256_bytes(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def capture_characterization() -> dict:
    paths = theme_paths()
    rows: list[dict] = []
    for row in COVERAGE:
        rows.append(
            {
                "consumer_id": row.consumer_id,
                "klass": row.klass,
                "writer": row.writer,
                "selection_strategy": row.selection_strategy,
                "source": row.source,
                "artifact": row.artifact,
                "modes": list(MODES),
                "active_path": active_path_for(row, paths),
                "variant_paths": variant_paths_for(row),
            }
        )

    theme_paths_snapshot = {
        name: rel(getattr(paths, name))
        for name in sorted(
            p for p in dir(paths) if not p.startswith("_") and isinstance(getattr(paths, p), Path)
        )
    }
    selector_paths = {
        "ghostty_config": rel(paths.ghostty_config),
        "warp_settings": rel(paths.warp_settings),
        "zellij_config": rel(paths.zellij_config),
        "codex_config": rel(paths.codex_config),
        "pi_settings": rel(paths.pi_settings),
    }

    buf = io.StringIO()
    with redirect_stdout(buf):
        print_summary("dark", paths, {}, [])
    summary_output = buf.getvalue().splitlines()

    return {
        "schema": "dreamcoder.legacy-sync-characterization.v1",
        "consumer_rows": rows,
        "theme_paths": theme_paths_snapshot,
        "selector_paths": selector_paths,
        "summary_output": summary_output,
    }


def artifact_hash_for(row, base_mode: str, prepared) -> dict:
    """Hash the exact bytes the current path writes for one consumer+mode."""
    cid = row.consumer_id
    active = prepared.active
    variants = prepared.variants

    result: dict[str, str | None] = {"path": None, "sha256": None}
    if cid == "herdr":
        complete = next((p for p in SUPPORTED_PROFILES if p is not None and p.is_complete), None)
        if complete is not None:
            path = rel(
                ROOT
                / "DreamcoderHerdr/.config/herdr/dreamcoder"
                / complete.evidence.version
                / f"config.{base_mode}.toml"
            )
            content = herdr_content(complete, base_mode, variants[base_mode])
            result = {"path": path, "sha256": sha256_bytes(content)}
    elif cid == "opencode":
        path = rel(ROOT / ".opencode/themes/dreamcoder.json")
        result = {
            "path": path,
            "sha256": sha256_bytes(opencode_content(active, transparent_background=True)),
        }
    elif cid in {"waybar_matugen", "rofi_matugen"}:
        fn = waybar_matugen_content if cid == "waybar_matugen" else rofi_matugen_content
        path = f"active:{'waybar/colors.css' if cid == 'waybar_matugen' else 'rofi/colors.rasi'}"
        result = {"path": path, "sha256": sha256_bytes(fn(active))}
    else:
        vpath = variant_paths_for(row)[base_mode]
        builder = BUILDERS.get(cid)
        if builder is not None and vpath is not None:
            result = {"path": vpath, "sha256": sha256_bytes(builder(variants[base_mode]))}
    return result


def capture_output_hashes() -> dict:
    artifacts: dict[str, dict[str, dict]] = {}
    for base_mode in ("dark", "light"):
        prepared = prepare(base_mode)
        for row in COVERAGE:
            artifacts.setdefault(row.consumer_id, {})[base_mode] = artifact_hash_for(
                row, base_mode, prepared
            )
    return {
        "schema": "dreamcoder.legacy-output-hashes.v1",
        "modes": ["dark", "light"],
        "artifacts": artifacts,
    }


def main() -> int:
    FIXTURES.mkdir(parents=True, exist_ok=True)

    characterization = capture_characterization()
    char_path = FIXTURES / "legacy_sync_characterization.json"
    char_path.write_text(
        json.dumps(characterization, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    hashes = capture_output_hashes()
    hash_path = FIXTURES / "legacy_output_hashes.json"
    hash_path.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"wrote {char_path.relative_to(REPO_ROOT)} ({len(characterization['consumer_rows'])} consumer rows)"
    )
    print(f"wrote {hash_path.relative_to(REPO_ROOT)} ({len(hashes['artifacts'])} consumers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
