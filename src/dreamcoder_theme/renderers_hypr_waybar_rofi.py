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
        "shadow": "rgba(000000ff)",
        "scrim": "rgba(000000ff)",
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


def hypr_content(c: dict[str, str]) -> str:
    inactive = _rgba_to_argb(c.get("inactive_border", "rgba(89, 77, 70, 0.78)"))
    return f"""# Dreamcoder color layer for Hyprland.
# Import after ML4W/Gentleman defaults; this changes colors only.

general {{
    col.active_border = rgba({c["text"][1:]}ff) rgba({c["muted"][1:]}ff) 45deg
    col.inactive_border = {inactive}
}}

misc {{
    background_color = rgba({c["bg"][1:]}ff)
}}
"""


def waybar_content(c: dict[str, str]) -> str:
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

window#waybar {{
  background: {c["panel_rgba"]};
  color: @text;
  border-bottom: 1px solid alpha(@accent, 0.26);
}}

#workspaces button {{
  color: @muted;
  background: transparent;
  border: 1px solid transparent;
}}

#workspaces button.active {{
  color: @accent;
  background: {c["active_rgba"]};
  border-color: alpha(@focus, 0.82);
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
  border: 1px solid alpha(@border-ui, 0.78);
}}

#battery.warning {{ color: @warning; }}
#battery.critical {{ color: @error; }}
#network.disconnected {{ color: @error; }}
"""


def rofi_content(c: dict[str, str]) -> str:
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
  border-radius: 18px;
}}

entry {{
  background-color: @selected;
  text-color: @foreground;
  border: 1px;
  border-color: @focus;
  border-radius: 12px;
}}

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
    shadow: #000000;
    scrim: #000000;
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
