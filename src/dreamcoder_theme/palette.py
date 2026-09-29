"""Palette tokens and contrast helpers."""

from __future__ import annotations

import json
import re
import subprocess
import warnings
from collections.abc import Callable
from pathlib import Path

# Re-export pure color math
from ._math import (
    apca_lc,
    compute_on_color,
    contrast,
    guard,
    hex_to_rgb,
    mix,
    rel_luminance,
    rgb_to_hex,
    surface_guard,
)
from .palette_tokens import ANSI_KEY_NAMES

# Re-export domain functions for backward compatibility
__all__ = [
    "apca_lc",
    "compute_on_color",
    "contrast",
    "guard",
    "hex_to_rgb",
    "load_guardrails",
    "mix",
    "rel_luminance",
    "rgb_to_hex",
    "surface_guard",
]


def load_variants(
    defaults: dict[str, dict[str, str]], tokens_file: Path
) -> dict[str, dict[str, str]]:
    if not tokens_file.exists():
        return defaults
    try:
        tokens = json.loads(tokens_file.read_text())
    except (json.JSONDecodeError, OSError):
        warnings.warn(f"invalid tokens file: {tokens_file}", stacklevel=2)
        return defaults
    modes = tokens.get("modes", {})
    merged = {key: value.copy() for key, value in defaults.items()}
    for key in ("dark", "light", "dusk"):
        if key in modes:
            merged[key].update(token for token in modes[key].items() if isinstance(token[1], str))

    for mode_key in ("dark", "light", "dusk"):
        if mode_key in modes and mode_key in defaults:
            for token_key in set(defaults[mode_key]) & set(modes[mode_key]):
                d = defaults[mode_key][token_key]
                t = modes[mode_key][token_key]
                if d != t:
                    warnings.warn(
                        f"palette divergence: {mode_key}.{token_key} = {t!r} (tokens.json) "
                        f"overrides {d!r} (palette_tokens.py). "
                        f"Run ./scripts/generate-palette-tokens.py.",
                        stacklevel=2,
                    )
    return merged


def matugen_mode_name(mode_name: str) -> str:
    return "light" if mode_name in {"light", "dusk"} else "dark"


def resolve_color(palette: dict[str, str], value: str) -> str:
    if value.endswith("_bright"):
        base = value.removesuffix("_bright")
        if base in palette:
            # Bright variants must always be LIGHTER than base.
            # Dark mode: text is light → mix with text to lighten.
            # Light mode: bg is light → mix with bg to lighten.
            if detect_mode(palette) == "light":
                mix_target = palette.get("bg", palette["text"])
            else:
                mix_target = palette["text"]
            return mix(palette[base], mix_target, 0.18)
    return palette.get(value, value)


def matugen_scheme(path: Path, mode_name: str, adaptive: bool) -> dict[str, str]:
    if not adaptive or not path.is_file():
        return {}
    result = subprocess.run(
        [
            "matugen",
            "image",
            str(path),
            "--json",
            "hex",
            "-m",
            matugen_mode_name(mode_name),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
        timeout=30,
    )
    match = re.search(r"\{.*\}", result.stdout, flags=re.S)
    if not match:
        return {}
    try:
        return json.loads(match.group(0)).get("colors", {}).get(matugen_mode_name(mode_name), {})  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        return {}


def adaptive_palette(
    base: dict[str, str], mode_name: str, wallpaper: Path, adaptive: bool
) -> dict[str, str]:
    scheme = matugen_scheme(wallpaper, mode_name, adaptive)
    if not scheme:
        return base

    c = dict(base)
    bg = mix(c["bg"], scheme.get("background", c["bg"]), 0.18)
    if contrast(bg, c["text"]) >= 7:
        c["bg"] = bg
    c["surface0"] = surface_guard(
        mix(c["surface0"], scheme.get("surface_container", c["surface0"]), 0.16),
        c["bg"],
        mode_name,
    )
    c["surface1"] = surface_guard(
        mix(c["surface1"], scheme.get("surface_container_high", c["surface1"]), 0.18),
        c["bg"],
        mode_name,
    )
    c["surface2"] = surface_guard(
        mix(c["surface2"], scheme.get("surface_variant", c["surface2"]), 0.18),
        c["bg"],
        mode_name,
    )
    c["bg_soft"] = surface_guard(c["bg_soft"], c["bg"], mode_name)
    c["accent"] = guard(
        mix(c["prompt_accent"], scheme.get("primary", c["accent"]), 0.25),
        c["bg"],
        mode_name,
    )
    c["accent_2"] = guard(
        mix(c["prompt_accent_2"], scheme.get("secondary", c["accent_2"]), 0.22),
        c["bg"],
        mode_name,
    )
    c["diagnostic"] = guard(
        mix(c["diagnostic"], scheme.get("tertiary", c["diagnostic"]), 0.45),
        c["bg"],
        mode_name,
    )
    c["border"] = mix(c["border"], scheme.get("outline", c["border"]), 0.25)
    c["selection_bg"] = mix(
        c.get("selection_bg", c["surface1"]),
        scheme.get("primary_container", c.get("selection_bg", c["surface1"])),
        0.18,
    )
    c["selection"] = c["selection_bg"]
    c["prompt_accent"] = c["accent"]
    c["prompt_accent_2"] = c["accent_2"]
    return c


def ansi(palette: dict[str, str]) -> list[str]:
    mode_name = detect_mode(palette)
    safe = []
    for key in ANSI_KEY_NAMES:
        color = resolve_color(palette, key)
        if not color.startswith("#"):
            raise ValueError(f"ANSI key {key!r} resolved to non-hex {color!r}")
        safe.append(guard(color, palette["bg"], mode_name))
    return safe


def detect_mode(palette: dict[str, str]) -> str:
    """Return "dark" or "light" based on the palette's details key."""
    return "dark" if palette.get("details") == "darker" else "light"


def make_guard(palette: dict[str, str], minimum: float = 3.0) -> Callable[[str], str]:
    """Return a guard() bound to the palette's bg and mode.

    Usage:
        g = make_guard(c)          # min contrast 3.0
        g = make_guard(c, 2.8)     # custom minimum
        accent = g(c["accent"])    # guarded accent color
    """
    mode = detect_mode(palette)
    bg = palette["bg"]
    return lambda color: guard(color, bg, mode, minimum=minimum)


# ------------------------------------------------------------------
# Declarative APCA pair classes (ADR-002).
#
# Each class names its token pairs and the guardrail keys that own the
# threshold — light/dusk floor and dark floor. No numeric policy
# literals are allowed here; a missing guardrail key fails validation.
# ------------------------------------------------------------------
_APCA_PAIR_CLASSES: tuple[tuple[str, tuple[tuple[str, str], ...], str, str], ...] = (
    (
        "body",
        (
            ("text", "bg"),
            ("error", "bg"),
            ("warning", "bg"),
            ("success", "bg"),
            ("info", "bg"),
            ("diagnostic", "bg"),
        ),
        "minimum_apca_body",
        "minimum_apca_body_dark",
    ),
    (
        "heading",
        (("text_heading", "bg"),),
        "minimum_apca_heading_light",
        "minimum_apca_heading_dark",
    ),
    (
        "quiet",
        (
            ("muted", "bg"),
            ("comment", "bg"),
            ("subtle", "bg"),
            ("disabled", "bg"),
        ),
        "minimum_apca_quiet",
        "minimum_apca_quiet",
    ),
    (
        "ui",
        (
            ("border_ui", "bg"),
            ("border_hi", "bg"),
            ("focus", "bg"),
        ),
        "minimum_apca_ui",
        "minimum_apca_ui_dark",
    ),
    (
        "on-accent",
        (("on_accent", "accent"),),
        "minimum_apca_on_accent",
        "minimum_apca_on_accent",
    ),
)


def validate_palette(
    palette: dict[str, str],
    guardrails: dict[str, float] | None = None,
    *,
    mode: str | None = None,
) -> list[str]:
    """Return stable validation errors for a mode palette.

    Dual gate (ADR-002): WCAG 2.2 and APCA are independently blocking and
    both metrics are fully evaluated — a pass on one metric never waives a
    failure on the other. Thresholds are resolved from ``guardrails`` by
    key; APCA thresholds must be present or validation fails closed.

    ``mode`` defaults to the palette-derived base mode (``dark`` for
    ``details=darker``, otherwise ``light``).

    Metric diagnostics use the stable shape::

        {metric} fail: mode={mode} pair={fg}/{bg} \
            measured={value} guardrail={key}={threshold}
    """
    g = guardrails or {}
    if "bg" not in palette:  # fail fast, exactly like the former eager lookup
        raise KeyError("bg")
    effective_mode = mode if mode is not None else detect_mode(palette)
    text_min = g.get("minimum_text_contrast", 4.5)

    # -- WCAG 2.2 gate --------------------------------------------------
    errors = _wcag_text_tokens(palette, effective_mode, text_min)
    errors += _wcag_main_text(palette, effective_mode, g.get("preferred_main_text_contrast", 7.0))
    errors += _wcag_foreground_pairs(
        palette, effective_mode, text_min, g.get("minimum_terminal_selection_contrast", 7.0)
    )
    errors += _wcag_ansi(palette, effective_mode, g.get("minimum_terminal_ansi_contrast", 4.5))

    # -- APCA gate (independent; never short-circuits WCAG) -------------
    if mode is not None and mode not in ("light", "dark", "dusk"):
        errors.append(f"invalid mode: {mode}")
    errors += _apca_classes(palette, g, effective_mode, text_min)

    # -- Structural checks ----------------------------------------------
    errors += _structural_errors(palette, effective_mode)
    return errors


def _wcag_diag(
    mode: str, fg_key: str, bg_key: str, measured: float, key: str, threshold: float
) -> str:
    return (
        f"WCAG fail: mode={mode} "
        f"pair={fg_key}/{bg_key} measured={measured:.2f} "
        f"guardrail={key}={threshold}"
    )


def _apca_diag(
    mode: str, cls: str, fg_key: str, bg_key: str, lc: float, key: str, threshold: float
) -> str:
    return (
        f"APCA fail: mode={mode} "
        f"pair={fg_key}/{bg_key} class={cls} measured={abs(lc):.1f} "
        f"guardrail={key}={threshold}"
    )


def _wcag_text_tokens(palette: dict[str, str], mode: str, text_min: float) -> list[str]:
    errors: list[str] = []
    for key in ("text", "muted", "comment", "accent", "error", "warning", "diagnostic"):
        if key not in palette:
            errors.append(f"missing token: {key}")
            continue
        ratio = contrast(palette["bg"], palette[key])
        if ratio < text_min:
            errors.append(_wcag_diag(mode, key, "bg", ratio, "minimum_text_contrast", text_min))
    return errors


def _wcag_main_text(palette: dict[str, str], mode: str, main_min: float) -> list[str]:
    if "text" not in palette:
        return []
    ratio = contrast(palette["bg"], palette["text"])
    if ratio >= main_min:
        return []
    return [_wcag_diag(mode, "text", "bg", ratio, "preferred_main_text_contrast", main_min)]


def _wcag_foreground_pairs(
    palette: dict[str, str], mode: str, text_min: float, sel_min: float
) -> list[str]:
    errors: list[str] = []
    for fg_key, bg_key in (
        ("selection_fg", "selection_bg"),
        ("on_accent", "accent"),
        ("on_error", "error"),
    ):
        if fg_key not in palette or bg_key not in palette:
            continue
        ratio = contrast(palette[fg_key], palette[bg_key])
        if fg_key == "selection_fg":
            key, threshold = "minimum_terminal_selection_contrast", sel_min
        else:
            key, threshold = "minimum_text_contrast", text_min
        if ratio < threshold:
            errors.append(_wcag_diag(mode, fg_key, bg_key, ratio, key, threshold))
    return errors


def _wcag_ansi(palette: dict[str, str], mode: str, ansi_min: float) -> list[str]:
    errors: list[str] = []
    for index, color in enumerate(ansi(palette)):
        ratio = contrast(color, palette["bg"])
        if ratio < ansi_min:
            errors.append(
                _wcag_diag(
                    mode, f"ansi{index}", "bg", ratio, "minimum_terminal_ansi_contrast", ansi_min
                )
            )
    return errors


def _apca_classes(
    palette: dict[str, str], guardrails: dict[str, float], mode: str, text_min: float
) -> list[str]:
    errors: list[str] = []
    for cls, pairs, light_key, dark_key in _APCA_PAIR_CLASSES:
        key = light_key if mode in ("light", "dusk") else dark_key
        threshold = guardrails.get(key)
        if threshold is None:
            errors.append(f"missing guardrail key: {key}")
            continue
        for fg_key, bg_key in pairs:
            errors += _apca_pair(palette, mode, cls, (fg_key, bg_key), (key, threshold), text_min)
    return errors


def _apca_pair(
    palette: dict[str, str],
    mode: str,
    cls: str,
    pair: tuple[str, str],
    guardrail: tuple[str, float],
    text_min: float,
) -> list[str]:
    fg_key, bg_key = pair
    if fg_key not in palette or bg_key not in palette:
        return [f"missing token: {fg_key} (declared {cls} pair)"]
    errors: list[str] = []
    key, threshold = guardrail
    lc = apca_lc(palette[fg_key], palette[bg_key])
    if abs(lc) < threshold:
        errors.append(_apca_diag(mode, cls, fg_key, bg_key, lc, key, threshold))
    # Independent WCAG floor on the SAME declared pair (ADR-002 dual
    # gate): both metrics are required for every declared class, so
    # an APCA-boosted near-invisible pair cannot pass unremarked.
    ratio = contrast(palette[fg_key], palette[bg_key])
    if ratio < text_min:
        errors.append(_wcag_diag(mode, fg_key, bg_key, ratio, "minimum_text_contrast", text_min))
    return errors


def _structural_errors(palette: dict[str, str], mode: str) -> list[str]:
    errors = [
        f"{step} too close to bg"
        for step in ("bg_soft", "surface0", "surface1", "surface2", "surface3")
        if step in palette and contrast(palette[step], palette["bg"]) < 1.02
    ]
    if palette.get("comment") == palette.get("subtle"):
        errors.append("comment and subtle must differ")
    if palette.get("accent") == palette.get("accent_2"):
        errors.append("accent and accent_2 must differ")
    if mode == "light" and "surface3" not in palette:
        errors.append("light mode missing surface3")
    return errors


# Guardrail keys validate_palette() resolves; a missing key
# fails closed so thresholds always originate in the canonical token file.
_REQUIRED_GUARDRAIL_KEYS = (
    "minimum_text_contrast",
    "preferred_main_text_contrast",
    "minimum_terminal_ansi_contrast",
    "minimum_terminal_selection_contrast",
    "minimum_apca_body",
    "minimum_apca_body_dark",
    "minimum_apca_quiet",
    "minimum_apca_ui",
    "minimum_apca_ui_dark",
    "minimum_apca_on_accent",
    "minimum_apca_heading_light",
    "minimum_apca_heading_dark",
)


def _require_guardrails(guardrails: dict[str, float]) -> None:
    missing = [key for key in _REQUIRED_GUARDRAIL_KEYS if key not in guardrails]
    if missing:
        raise ValueError(f"missing required guardrails: {', '.join(missing)}")


def load_guardrails(tokens_file: Path) -> dict[str, float]:
    """Load numeric guardrails from the canonical token file, failing closed.

    Every threshold consumed by validation must originate here (ADR-002); a
    missing required key (or an unreadable file) raises instead of falling
    back to a code literal.
    """
    if not tokens_file.is_file():
        raise ValueError(f"tokens file not found: {tokens_file}")
    try:
        tokens = json.loads(tokens_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"invalid tokens file: {tokens_file}") from exc
    guardrails = tokens.get("guardrails", {})
    numeric = {k: float(v) for k, v in guardrails.items() if isinstance(v, (int, float))}
    _require_guardrails(numeric)
    return numeric
