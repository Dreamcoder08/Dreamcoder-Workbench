"""Pure GTK/Qt contracts; no installed configuration or desktop interaction."""

import configparser
import ctypes.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from dreamcoder_theme import renderers
from dreamcoder_theme.palette_tokens import VARIANTS

ROOT = Path(__file__).resolve().parents[2]
# Exact aliases from the installed Matugen gtk-colors.css template.
MATUGEN_ROLES = {
    "accent_color",
    "accent_fg_color",
    "accent_bg_color",
    "window_bg_color",
    "window_fg_color",
    "headerbar_bg_color",
    "headerbar_fg_color",
    "popover_bg_color",
    "popover_fg_color",
    "view_bg_color",
    "view_fg_color",
    "card_bg_color",
    "card_fg_color",
    "sidebar_bg_color",
    "sidebar_fg_color",
    "sidebar_border_color",
    "sidebar_backdrop_color",
}
QT_ROLES = (
    "WindowText",
    "Button",
    "Light",
    "Midlight",
    "Dark",
    "Mid",
    "Text",
    "BrightText",
    "ButtonText",
    "Base",
    "Window",
    "Shadow",
    "Highlight",
    "HighlightedText",
    "Link",
    "LinkVisited",
    "AlternateBase",
    "NoRole",
    "ToolTipBase",
    "ToolTipText",
    "PlaceholderText",
)


def gtk_colors(palette):
    content = renderers.gtk_content(palette)
    rows = re.findall(r"^@define-color (\w+) (#[0-9A-Fa-f]{6});$", content, re.M)
    assert len(rows) == content.count("@define-color")
    assert len(rows) == len(dict(rows)), "Duplicate named roles"
    assert "{" not in content, "Do not impose widget selectors"
    return dict(rows)


def qt_colors(palette):
    parser = configparser.ConfigParser()
    parser.read_string(renderers.qt6ct_content(palette))
    assert parser.sections() == ["ColorScheme"]
    section = parser["ColorScheme"]
    assert set(section) == {"active_colors", "inactive_colors", "disabled_colors"}
    groups = {}
    for group, value in section.items():
        fields = [field.strip() for field in value.split(",")]
        assert len(fields) == 21
        assert all(re.fullmatch(r"#ff[0-9a-f]{6}", field) for field in fields)
        groups[group] = dict(zip(QT_ROLES, ("#" + field[3:] for field in fields)))
    return groups


def contrast(a, b):
    def luminance(color):
        channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


def test_exports_and_canonical_gtk_roles():
    p = VARIANTS["dark"]
    colors = gtk_colors(p)
    assert colors.keys() >= MATUGEN_ROLES
    assert colors["view_bg_color"] == colors["theme_base_color"] == p["bg"]
    assert colors["window_bg_color"] == colors["theme_bg_color"] == p["surface0"]
    for role in ("headerbar_bg_color", "popover_bg_color", "card_bg_color"):
        assert colors[role] == p["surface1"]
    assert colors["sidebar_bg_color"] == p["surface0"]
    assert colors["sidebar_border_color"] == p["border_ui"]
    assert colors["accent_bg_color"] == p["accent"]
    assert colors["accent_fg_color"] == p["on_accent"]
    assert colors["theme_unfocused_fg_color"] == p["muted"]
    assert colors["insensitive_fg_color"] == p["disabled"]
    assert "gtk_content" in renderers.__all__
    assert "qt6ct_content" in renderers.__all__


def test_qt_positions_match_gtk_semantics():
    p = VARIANTS["dark"]
    gtk = gtk_colors(p)
    groups = qt_colors(p)
    for colors in groups.values():
        assert colors["Base"] == gtk["view_bg_color"] == "#000000"
        assert colors["Window"] == gtk["window_bg_color"].lower()
        assert (
            colors["Button"]
            == colors["AlternateBase"]
            == colors["ToolTipBase"]
            == p["surface1"].lower()
        )
        assert colors["NoRole"] == p["bg"].lower()
        assert colors["Shadow"] == p["bg"].lower()
        assert colors["Link"] == p["link"].lower()
        assert colors["LinkVisited"] == p["link_hover"].lower()
    # Assert the entire positional contract, including non-text bevel roles.
    expected_tokens = (
        "text",
        "surface1",
        "surface3",
        "surface2",
        "surface0",
        "border",
        "text",
        "text_heading",
        "text",
        "bg",
        "surface0",
        "bg",
        "accent",
        "on_accent",
        "link",
        "link_hover",
        "surface1",
        "bg",
        "surface1",
        "text",
        "subtle",
    )
    assert list(groups["active_colors"].values()) == [p[token].lower() for token in expected_tokens]
    assert groups["active_colors"]["Highlight"] == p["accent"].lower()
    assert groups["active_colors"]["HighlightedText"] == p["on_accent"].lower()
    assert groups["inactive_colors"]["WindowText"] == p["muted"].lower()
    assert groups["disabled_colors"]["Text"] == p["disabled"].lower()


def test_gtk_dark_text_and_disabled_aliases_are_readable():
    colors = gtk_colors(VARIANTS["dark"])
    for text, background in (
        ("view_fg_color", "view_bg_color"),
        ("window_fg_color", "window_bg_color"),
        ("headerbar_fg_color", "headerbar_bg_color"),
        ("popover_fg_color", "popover_bg_color"),
        ("card_fg_color", "card_bg_color"),
        ("sidebar_fg_color", "sidebar_bg_color"),
        ("accent_fg_color", "accent_bg_color"),
        ("insensitive_fg_color", "insensitive_bg_color"),
        ("theme_unfocused_fg_color", "theme_unfocused_bg_color"),
    ):
        assert contrast(colors[text], colors[background]) >= 4.5, text


@pytest.mark.parametrize("group", ["active_colors", "inactive_colors", "disabled_colors"])
def test_qt_text_is_readable_in_every_group(group):
    colors = qt_colors(VARIANTS["dark"])[group]
    # Disabled roles deliberately meet 4.5:1 too, not merely Qt's exemption.
    for text, background in (
        ("WindowText", "Window"),
        ("Text", "Base"),
        ("ButtonText", "Button"),
        ("ToolTipText", "ToolTipBase"),
        ("PlaceholderText", "Base"),
        ("HighlightedText", "Highlight"),
        ("Link", "Base"),
        ("LinkVisited", "Base"),
    ):
        assert contrast(colors[text], colors[background]) >= 4.5, (group, text)


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_renderers_are_pure_deterministic_and_palette_driven(mode):
    p = dict(VARIANTS[mode])
    before = dict(p)
    for renderer in (renderers.gtk_content, renderers.qt6ct_content):
        first = renderer(p)
        assert renderer(p) == first
        assert p == before
        changed = dict(p, accent="#123456", bg="#010203")
        assert renderer(changed) != first
    assert gtk_colors(p)["view_bg_color"] == p["bg"]
    assert qt_colors(p)["active_colors"]["Base"] == p["bg"].lower()


@pytest.mark.parametrize(
    "name,renderer_name", [("gtk-dark.css", "gtk_content"), ("qt6ct-dark.conf", "qt6ct_content")]
)
def test_dark_assets_equal_pure_render(name, renderer_name):
    assert (ROOT / "DreamcoderThemes/dreamcoder" / name).read_text() == getattr(
        renderers, renderer_name
    )(VARIANTS["dark"])


# GTK major versions must use separate processes: their GObject type names collide.
GTK_PROBE = r"""
import ctypes as C
import sys
gtk = C.CDLL(sys.argv[1])
gtk.gtk_css_provider_new.restype = C.c_void_p
gtk.gtk_css_provider_load_from_path.argtypes = [C.c_void_p, C.c_char_p] + ([C.c_void_p] if sys.argv[2] == '3' else [])
gtk.gtk_css_provider_to_string.argtypes = [C.c_void_p]
gtk.gtk_css_provider_to_string.restype = C.c_void_p
provider = gtk.gtk_css_provider_new()
gtk.gtk_css_provider_load_from_path(provider, sys.argv[3].encode(), *([None] if sys.argv[2] == '3' else []))
result = gtk.gtk_css_provider_to_string(provider)
assert result
print(C.string_at(result).decode())
glib = C.CDLL('libglib-2.0.so.0')
glib.g_free.argtypes = [C.c_void_p]
glib.g_free(result)
gobject = C.CDLL('libgobject-2.0.so.0')
gobject.g_object_unref.argtypes = [C.c_void_p]
gobject.g_object_unref(provider)
"""


@pytest.mark.parametrize("major", ["3", "4"])
def test_native_gtk_import_cascade_survives_matugen_overwrite(tmp_path, major):
    library = ctypes.util.find_library("gtk-" + major)
    if not library:
        pytest.skip("GTK parser unavailable: gtk-" + major)
    # All HOME/XDG and both agent homes are fixtures; discard inherited overrides.
    env = {key: value for key, value in os.environ.items() if key in {"PATH", "LANG", "LC_ALL"}}
    for key in (
        "HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_CACHE_HOME",
        "PI_CODING_AGENT_DIR",
        "PI_AGENT_DIR",
        "GENTLE_SHELL_HOME",
    ):
        env[key] = str(tmp_path / key.lower())
    (tmp_path / "canonical.css").write_text(renderers.gtk_content(VARIANTS["dark"]))
    (tmp_path / "gtk.css").write_text(
        "@import 'colors.css';\n@import 'canonical.css';\n"
        "label { color: @view_fg_color; background-color: @view_bg_color; }\n"
    )
    for matugen_bg in ("#654321", "#fedcba"):
        (tmp_path / "colors.css").write_text(
            f"@define-color view_bg_color {matugen_bg};\n@define-color view_fg_color #112233;\n"
        )
        probe = subprocess.run(
            [sys.executable, "-c", GTK_PROBE, library, major, str(tmp_path / "gtk.css")],
            env=env,
            text=True,
            capture_output=True,
            timeout=20,
            check=True,
        )
        assert not probe.stderr, probe.stderr
        assert "@define-color view_bg_color rgb(0,0,0);" in probe.stdout
        assert "@define-color view_fg_color rgb(230,230,230);" in probe.stdout
        assert probe.stdout.count("@define-color view_bg_color ") == 1
        assert "background-color: @view_bg_color;" in probe.stdout
