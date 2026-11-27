"""Focused desktop shell theme renderers."""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Dreamcoder → Material Design 3 (Matugen-compatible) color-role mapping.
# ML4W 2.13+ requires colors.lua + colors.conf with these exact tokens.
# ---------------------------------------------------------------------------


def _hex_to_rgba_ff(hex_color: str) -> str:
    """Convert #RRGGBB → rgba(RRGGBBff) for Matugen/Hyprland format."""
    return f"rgba({hex_color[1:]}ff)"


def _map_dc_to_material(c: dict[str, str]) -> dict[str, str]:
    """Map Dreamcoder palette tokens to Material Design 3 color roles."""
    h = _hex_to_rgba_ff
    # The components tier supplies the shadow ink (warm on Light, graphite on Dark).
    shadow = h(c["shadow_ink"]) if "shadow_ink" in c else "rgba(000000ff)"
    return {
        # Core surfaces
        "background": h(c["bg"]),
        "surface": h(c["bg"]),
        "surface_dim": h(c["bg_soft"]),
        "surface_bright": h(c["surface0"]),
        "surface_container_lowest": h(c["surface0"]),
        "surface_container_low": h(c["surface0"]),
        "surface_container": h(c["surface1"]),
        "surface_container_high": h(c["surface1"]),
        "surface_container_highest": h(c["surface2"]),
        "surface_variant": h(c["surface1"]),
        "surface_tint": h(c["accent"]),
        # On-colors
        "on_background": h(c["on_surface"]),
        "on_surface": h(c["on_surface"]),
        "on_surface_variant": h(c["muted"]),
        # Primary
        "primary": h(c["accent"]),
        "on_primary": h(c["on_accent"]),
        "primary_container": h(c["surface1"]),
        "on_primary_container": h(c["text"]),
        "primary_fixed": h(c["accent"]),
        "primary_fixed_dim": h(c["accent_2"]),
        "on_primary_fixed": h(c["bg"]),
        "on_primary_fixed_variant": h(c["accent"]),
        "inverse_primary": h(c["accent"]),
        # Secondary
        "secondary": h(c["accent_2"]),
        "on_secondary": h(c["on_accent"]),
        "secondary_container": h(c["surface1"]),
        "on_secondary_container": h(c["text"]),
        "secondary_fixed": h(c["accent_2"]),
        "secondary_fixed_dim": h(c["accent_2"]),
        "on_secondary_fixed": h(c["bg"]),
        "on_secondary_fixed_variant": h(c["accent_2"]),
        # Tertiary
        "tertiary": h(c["diagnostic"]),
        "on_tertiary": h(c["on_accent"]),
        "tertiary_container": h(c["surface0"]),
        "on_tertiary_container": h(c["text"]),
        "tertiary_fixed": h(c["diagnostic"]),
        "tertiary_fixed_dim": h(c["diagnostic"]),
        "on_tertiary_fixed": h(c["bg"]),
        "on_tertiary_fixed_variant": h(c["focus"]),
        # Error
        "error": h(c["error"]),
        "on_error": h(c["on_error"]),
        "error_container": h(c["surface0"]),
        "on_error_container": h(c["text"]),
        # Outline
        "outline": h(c["border"]),
        "outline_variant": h(c["border_ui"]),
        # Fixed
        "shadow": shadow,
        "scrim": shadow,
        "source_color": h(c["accent"]),
        # Inverse
        "inverse_on_surface": h(c["surface0"]),
        "inverse_surface": h(c["text"]),
    }


def _rgba_to_argb(value: str, default_alpha: str = "ff") -> str:
    """Convert rgba(r, g, b, a) to rgba(RRGGBBAA) for Hyprland."""
    match = re.match(
        r"rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01]?\.?\d*)\s*\)",
        value,
    )
    if not match:
        return value
    # Regex guarantees r/g/b are 1-3 digits; alpha may be empty for a
    # malformed-but-matching input (e.g. "rgba(1, 2, 3, )"), so conversion
    # is guarded to honor the passthrough contract above.
    try:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        a_hex = f"{round(float(match.group(4)) * 255):02x}"
    except ValueError:
        return value
    # int() truncates 3-digit channels; zfill only pads and never truncates,
    # which produced invalid 10-char rgba() (e.g. rgba(13811588ed)).
    return f"rgba({r:02x}{g:02x}{b:02x}{a_hex})"


def _has_components(c: dict[str, str]) -> bool:
    """Palettes carry the components tier (geometry, elevation, rhythm) in both modes."""
    return "elevation_e1" in c


def _is_light_chrome(c: dict[str, str]) -> bool:
    """Light-only semantic chrome (solid frame, pigment chips); geometry is shared."""
    return _has_components(c) and c.get("details") == "lighter"


def _px(value: str) -> str:
    return value.removesuffix("px")


def _hypr_rhythm(c: dict[str, str]) -> tuple[str, str]:
    """Modes with components: (gap lines, animations block) from the rhythm tier.

    Gaps are s1 inside and s4 outside windows. Hyprland speeds are in deciseconds
    (1 ds = 100 ms), so the quick/base/slow durations become 1.2/2/3.2.
    """
    if not _has_components(c):
        return "", ""

    def speed(name: str) -> str:
        return f"{int(c[f'motion_duration_{name}'].removesuffix('ms')) / 100:g}"

    def curve(name: str) -> str:
        return c[f"motion_curve_{name}"].removeprefix("cubic-bezier(").removesuffix(")")

    gaps = f"\n    gaps_in = {_px(c['space_s1'])}\n    gaps_out = {_px(c['space_s4'])}"
    animations = f"""
animations {{
    enabled = true
    bezier = dc_enter, {curve("enter")}
    bezier = dc_exit, {curve("exit")}
    bezier = dc_move, {curve("move")}
    animation = windowsIn, 1, {speed("base")}, dc_enter
    animation = windowsOut, 1, {speed("quick")}, dc_exit
    animation = windowsMove, 1, {speed("base")}, dc_move
    animation = fadeIn, 1, {speed("base")}, dc_enter
    animation = fadeOut, 1, {speed("quick")}, dc_exit
    animation = border, 1, {speed("quick")}, dc_move
    animation = workspaces, 1, {speed("slow")}, dc_move
}}
"""
    return gaps, animations


def hypr_content(c: dict[str, str]) -> str:
    inactive = _rgba_to_argb(c.get("inactive_border", "rgba(89, 77, 70, 0.78)"))
    # Light: one solid accent frame (no gradient); other modes keep the ink gradient.
    active = (
        f"rgba({c['accent'][1:]}ff)"
        if _is_light_chrome(c)
        else f"rgba({c['text'][1:]}ff) rgba({c['muted'][1:]}ff) 45deg"
    )
    gaps, animations = _hypr_rhythm(c)
    return f"""# Dreamcoder color layer for Hyprland.
# Import after ML4W/Gentleman defaults; this changes colors only.

general {{
    col.active_border = {active}
    col.inactive_border = {inactive}{gaps}
}}

misc {{
    background_color = rgba({c["bg"][1:]}ff)
}}
{animations}"""


def _waybar_chips(c: dict[str, str]) -> tuple[str, str]:
    """Light only: (selection colour, chip rules); pigment wash, never a solid fill.

    Count badges are a neutral clay chip with accent text; only the critical state
    takes the error wash. The ML4W launcher tile is an umber wash.
    """
    if not _is_light_chrome(c):
        return "", ""
    radius = c["radius_r2"]
    return (
        f"@define-color selection {c['selection']};\n",
        f"""
/* Count badges and tiles: a pigment wash over paper, never a saturated solid. */
#custom-updates {{
  background: @selection;
  color: @accent;
  border-radius: {radius};
  padding: 0 {c["space_s2"]};
  margin: {c["space_s1"]};
  font-weight: {c["type_emphasis_weight"]};
}}

#custom-updates.critical {{
  background: alpha(@error, 0.14);
  color: @error;
}}
""",
    )


def waybar_content(c: dict[str, str]) -> str:
    # Modules sit at elevation e1 with the r2 radius (components tier, both modes).
    module_depth = (
        f"\n  border-radius: {c['radius_r2']};\n  box-shadow: {c['elevation_e1']};"
        f"\n  padding: 0 {c['space_s3']};\n  margin: {c['space_s1']};"
        f"\n  font-weight: {c['type_body_weight']};"
        if _has_components(c)
        else ""
    )
    button_rhythm, active_weight = (
        (f"\n  padding: 0 {c['space_s2']};", f"\n  font-weight: {c['type_emphasis_weight']};")
        if _has_components(c)
        else ("", "")
    )
    selection_color, chip_rules = _waybar_chips(c)
    return f"""/* Dreamcoder color layer for Waybar. */
@define-color bg {c["bg"]};
@define-color bg-soft {c["bg_soft"]};
@define-color surface {c["surface0"]};
@define-color surface-2 {c["surface2"]};
@define-color surface-3 {c["surface3"]};
@define-color text {c["text"]};
@define-color text-heading {c["text_heading"]};
@define-color muted {c["muted"]};
@define-color subtle {c["subtle"]};
@define-color comment {c["comment"]};
@define-color border {c["border"]};
@define-color border-ui {c["border_ui"]};
@define-color focus {c["focus"]};
@define-color accent {c["accent"]};
@define-color accent-2 {c["accent_2"]};
@define-color diagnostic {c["diagnostic"]};
@define-color lavender {c["lavender"]};
@define-color error {c["error"]};
@define-color success {c["success"]};
@define-color warning {c["warning"]};
@define-color link {c["link"]};
@define-color link-hover {c["link_hover"]};
{selection_color}
window#waybar {{
  background: {c["panel_rgba"]};
  color: @text;
  border-bottom: 1px solid alpha(@accent, 0.26);
}}

#workspaces button {{
  color: @muted;
  background: transparent;
  border: 1px solid transparent;{button_rhythm}
}}

#workspaces button.active {{
  color: @accent;
  background: {c["active_rgba"]};
  border-color: alpha(@focus, 0.82);{active_weight}
}}

#clock,
#battery,
#network,
#pulseaudio,
#cpu,
#memory,
#tray {{
  background: {c["module_rgba"]};
  color: @text;
  border: 1px solid alpha(@border-ui, 0.78);{module_depth}
}}

#battery.warning {{ color: @warning; }}
#battery.critical {{ color: @error; }}
#network.disconnected {{ color: @error; }}
{chip_rules}"""


def rofi_content(c: dict[str, str]) -> str:
    # Palettes with components take the radius scale (window r3, entry r2).
    window_radius = c.get("radius_r3", "18px")
    entry_radius = c.get("radius_r2", "12px")
    entry_padding, rows = (
        (
            f"\n  padding: {c['space_s2']} {c['space_s3']};",
            f"""
listview {{ spacing: {c["space_s1"]}; }}

element {{
  padding: {c["space_s2"]} {c["space_s3"]};
  border-radius: {entry_radius};
}}
""",
        )
        if _has_components(c)
        else ("", "")
    )
    # A tonal mode lights the top edge of the floating window (the overhead key, e3).
    window_edge = (
        f"\n  border-color: {c['elevation_edge_e3']} {c['border_ui']} {c['border_ui']}"
        f" {c['border_ui']};"
        if "elevation_edge_e3" in c
        else ""
    )
    return f"""/* Dreamcoder color layer for Rofi. */
* {{
  background: {c["panel_rgba"]};
  background-alt: {c["surface0"]};
  foreground: {c["text"]};
  muted: {c["muted"]};
  selected: {c["active_rgba"]};
  active: {c["accent"]};
  border-ui: {c["border_ui"]};
  focus: {c["focus"]};
  urgent: {c["error"]};
  border-color: {c["border_ui"]};
}}

window {{
  background-color: @background;
  border: 1px;
  border-color: @border-ui;
  border-radius: {window_radius};{window_edge}
}}

entry {{
  background-color: @selected;
  text-color: @foreground;
  border: 1px;
  border-color: @focus;
  border-radius: {entry_radius};{entry_padding}
}}
{rows}
element selected {{
  background-color: @selected;
  text-color: @foreground;
  border: 0 0 0 3px;
  border-color: @focus;
}}

element-text {{ text-color: @muted; }}
element selected element-text {{ text-color: @foreground; }}
"""


def hypr_colors_lua_content(c: dict[str, str]) -> str:
    """Generate colors.lua in Matugen/Material-You format for ML4W Hyprland."""
    m = _map_dc_to_material(c)
    lines = []
    for key in sorted(m.keys()):
        lines.append(f'{key} = "{m[key]}"')
    return "\n".join(lines) + "\n"


def hypr_colors_conf_content(c: dict[str, str]) -> str:
    """Generate colors.conf in Matugen/Material-You format for ML4W Hyprland."""
    m = _map_dc_to_material(c)
    lines = []
    for key in sorted(m.keys()):
        lines.append(f"${key} = {m[key]}")
    return "\n".join(lines) + "\n"


def waybar_matugen_content(c: dict[str, str]) -> str:
    """Generate Waybar colors.css using ML4W/Matugen variable names.

    Only defines @define-color variables with Dreamcoder palette values.
    No layout rules — ML4W themes handle design. Colors only.
    Uses Matugen's exact format: underscore names, #RRGGBB hex.
    """
    m = _map_dc_to_material(c)

    def _hex_to_rgb(hex_color: str) -> str:
        hx = hex_color.lstrip("#")
        return f"{int(hx[0:2], 16)}, {int(hx[2:4], 16)}, {int(hx[4:6], 16)}"

    def _raw_hex(k: str) -> str:
        """Extract #RRGGBB from rgba(RRGGBBff)."""
        v = m[k]
        if v.startswith("rgba(") and v.endswith("ff)"):
            return "#" + v[5:-3]
        return v

    bg_rgb = _hex_to_rgb(c["bg"])

    lines = [
        "/*",
        " * Dreamcoder colors for ML4W Waybar",
        " * Generated by Dreamcoder sync — only replaces Matugen color values.",
        " * ML4W theme CSS files own the layout/design.",
        " */",
        f"@define-color blur_background rgba({bg_rgb}, 0.3);",
        f"@define-color blur_background8 rgba({bg_rgb}, 0.8);",
        "",
    ]
    for key in sorted(m.keys()):
        lines.append(f"@define-color {key} {_raw_hex(key)};")
    return "\n".join(lines) + "\n"


def rofi_matugen_content(c: dict[str, str]) -> str:
    """Generate Rofi colors.rasi using ML4W/Matugen variable names.

    Only defines color variables with Dreamcoder palette values.
    No layout rules — ML4W configs handle design. Colors only.
    Uses Matugen's exact format: hyphenated names, #RRGGBB for most,
    rgba(r, g, b, a) for background.
    """

    def _rgb(r: int, g: int, b: int, a: float) -> str:
        return f"rgba({r}, {g}, {b}, {a})"

    def _hex_to_rgb_int(hex_color: str) -> tuple[int, int, int]:
        hx = hex_color.lstrip("#")
        return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))

    r, g, b = _hex_to_rgb_int(c["bg"])
    bg_rgba = _rgb(r, g, b, 0.96)
    shadow = c.get("shadow_ink", "#000000")

    return f"""/* Dreamcoder colors for ML4W Rofi — only replaces Matugen color values. */
* {{
    background: {bg_rgba};
    primary: {c["accent"]};
    primary-fixed: {c["accent"]};
    primary-fixed-dim: {c["accent_2"]};
    on-primary: {c["on_accent"]};
    on-primary-fixed: {c["on_accent"]};
    on-primary-fixed-variant: {c["accent"]};
    primary-container: {c["surface1"]};
    on-primary-container: {c["text"]};
    secondary: {c["accent_2"]};
    secondary-fixed: {c["accent_2"]};
    secondary-fixed-dim: {c["accent_2"]};
    on-secondary: {c["on_accent"]};
    on-secondary-fixed: {c["bg"]};
    on-secondary-fixed-variant: {c["accent_2"]};
    secondary-container: {c["surface1"]};
    on-secondary-container: {c["text"]};
    tertiary: {c["diagnostic"]};
    tertiary-fixed: {c["diagnostic"]};
    tertiary-fixed-dim: {c["diagnostic"]};
    on-tertiary: {c["bg"]};
    on-tertiary-fixed: {c["bg"]};
    on-tertiary-fixed-variant: {c["focus"]};
    tertiary-container: {c["surface0"]};
    on-tertiary-container: {c["text"]};
    error: {c["error"]};
    on-error: {c["on_error"]};
    error-container: {c["surface0"]};
    on-error-container: {c["text"]};
    surface: {c["bg"]};
    on-surface: {c["text"]};
    on-surface-variant: {c["muted"]};
    outline: {c["border"]};
    outline-variant: {c["border_ui"]};
    shadow: {shadow};
    scrim: {shadow};
    inverse-surface: {c["text"]};
    inverse-on-surface: {c["surface0"]};
    inverse-primary: {c["accent"]};
    surface-dim: {c["bg_soft"]};
    surface-bright: {c["surface0"]};
    surface-container-lowest: {c["surface0"]};
    surface-container-low: {c["surface0"]};
    surface-container: {c["surface1"]};
    surface-container-high: {c["surface1"]};
    surface-container-highest: {c["surface2"]};
}}"""


from .renderer_contract import (  # noqa: E402
    ActiveStrategy,
    MutationStrategy,
    RendererRegistration,
    RendererStrategy,
    RepositoryStrategy,
    SyncDefinition,
)

REGISTRATIONS: tuple[RendererRegistration, ...] = (
    RendererRegistration(
        consumer_id="hyprland",
        renderer=hypr_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Hyprland main colors",
    ),
    RendererRegistration(
        consumer_id="hypr_colors_lua",
        renderer=hypr_colors_lua_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        # Verified against live sync.py (not the prior "active"/NO_VARIANTS/
        # ACTIVE_ONLY_BRIDGE declaration): sync_active_targets() writes the
        # live ~/.config/hypr/colors.lua active file via plain
        # write_if_changed(paths.hypr_colors_lua, ...), AND
        # sync_repo_snippets() separately writes MODE_VARIANTS repo snippets
        # via write_variant_files() — never write_active_repo_file(). Both
        # writers use bare write_if_changed, so mutation stays
        # WRITE_IF_CHANGED (this consumer is correctly absent from the
        # Slice B SYMLINK_SAFE_ACTIVE_WRITE sweep).
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.WRITE_IF_CHANGED,
        ),
        summary_label="Hyprland Lua colors",
    ),
    RendererRegistration(
        consumer_id="hypr_colors_conf",
        renderer=hypr_colors_conf_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        # See hypr_colors_lua comment above — identical verified shape:
        # live active write (sync_active_targets -> paths.hypr_colors_conf)
        # plus repo MODE_VARIANTS snippets (sync_repo_snippets), both via
        # bare write_if_changed, never write_active_repo_file().
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.WRITE_IF_CHANGED,
        ),
        summary_label="Hyprland conf colors",
    ),
    RendererRegistration(
        consumer_id="waybar",
        renderer=waybar_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Waybar CSS",
    ),
    RendererRegistration(
        consumer_id="waybar_matugen",
        renderer=waybar_matugen_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.NO_VARIANTS,
            mutation=MutationStrategy.ACTIVE_ONLY_BRIDGE,
        ),
        summary_label="Waybar matugen bridge",
    ),
    RendererRegistration(
        consumer_id="rofi",
        renderer=rofi_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Rofi theme",
    ),
    RendererRegistration(
        consumer_id="rofi_matugen",
        renderer=rofi_matugen_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.NO_VARIANTS,
            mutation=MutationStrategy.ACTIVE_ONLY_BRIDGE,
        ),
        summary_label="Rofi matugen bridge",
    ),
)
