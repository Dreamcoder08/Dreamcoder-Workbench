"""Reversible ownership, exclusively inside injected temporary paths."""

import ctypes.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from dreamcoder_theme.writers_gtk_qt import update_gtk_import, update_qt_palette

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return path.read_bytes() if path.exists() else None


@pytest.fixture
def paths(tmp_path):
    config = tmp_path / "config"
    canonical = tmp_path / 'canonical space "quoted".css'
    canonical.write_text("@define-color view_bg_color #000000;\n")
    return config, canonical, tmp_path / "ownership.json"


@pytest.mark.parametrize(
    "writer,original",
    [
        (update_gtk_import, b"/* personal */\n@import 'colors.css';\nlabel { color: red; }"),
        (
            update_qt_palette,
            b'; personal\r\n[Appearance]\r\ncolor_scheme_path = "old path"\r\ncustom_palette=false\r\nstyle=Fusion\r\n\r\n[Fonts]\r\nfixed=Mono',
        ),
    ],
)
def test_roundtrip_and_repeat_preserve_bytes(paths, writer, original):
    config, canonical, state = paths
    config.write_bytes(original)
    assert writer(config, canonical, state, "dark")
    active, owned = read(config), read(state)
    assert not writer(config, canonical, state, "dark")
    assert (read(config), read(state)) == (active, owned)
    assert writer(config, canonical, state, "light")
    assert read(config) == original
    assert not state.exists()
    assert not writer(config, canonical, state, "light")


@pytest.mark.parametrize(
    "writer,original",
    [
        (update_gtk_import, "/* personal */\nlabel { color: red; }\n"),
        (update_qt_palette, "[Appearance]\nstyle=Fusion\n[Fonts]\nfixed=Mono\n"),
    ],
)
def test_unrelated_edits_survive(paths, writer, original):
    config, canonical, state = paths
    config.write_text(original)
    writer(config, canonical, state, "dark")
    config.write_text(
        config.read_text().replace("personal", "edited").replace("Mono", "Serif") + "\n"
    )
    writer(config, canonical, state, "light")
    assert (
        config.read_text() == original.replace("personal", "edited").replace("Mono", "Serif") + "\n"
    )


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
@pytest.mark.parametrize("damage", ["config", "state", "missing", "binding"])
def test_conflicts_zero_writes(paths, writer, damage, monkeypatch):
    config, canonical, state = paths
    writer(config, canonical, state, "dark")
    if damage == "config":
        config.write_text(
            config.read_text()
            .replace("dreamcoder managed", "other managed")
            .replace("custom_palette=true", "custom_palette=false")
        )
    elif damage == "state":
        state.write_text('{"version": 999}')
    elif damage == "missing":
        config.unlink()
    else:
        canonical = canonical.with_name("other.css")
        canonical.write_text("/* other */")
    before = read(config), read(state)

    def reject_write(*args, **kwargs):
        pytest.fail("Conflict attempted a config/state write")

    monkeypatch.setattr(Path, "write_bytes", reject_write)
    monkeypatch.setattr("dreamcoder_theme.writers_gtk_qt.write_if_changed", reject_write)
    for mode in ("dark", "light"):
        with pytest.raises(ValueError):
            writer(config, canonical, state, mode)
        assert (read(config), read(state)) == before


@pytest.mark.parametrize(
    "original",
    [
        None,
        b"",
        b"; comment\n",
        b"[Other]\nkey=value",
        b"[Appearance]\nstyle=Fusion\n",
        b"[Appearance]\ncustom_palette=true\n",
    ],
)
def test_qt_absence_restoration(paths, original):
    config, canonical, state = paths
    if original is not None:
        config.write_bytes(original)
    update_qt_palette(config, canonical, state, "dark")
    update_qt_palette(config, canonical, state, "light")
    assert read(config) == original


@pytest.mark.parametrize(
    "original",
    [
        "[Appearance\nstyle=Fusion\n",
        "key=value\n",
        "[Appearance]\ncolor_scheme_path=x\ncolor_scheme_path=y\n",
        '[Appearance]\n"color_scheme_path"=x\n',
        "[Appearance]\ncustom_palette=maybe\n",
        "[Appearance]\n[Appearance]\n",
        "[Appearance] garbage\n",
        "[Appearance]\n bad continuation\n",
        "[appearance]\ncolor_scheme_path=x\n",
        "[Appearance/sub]\ncolor_scheme_path=x\n",
    ],
)
def test_qt_rejected_layouts(paths, original):
    config, canonical, state = paths
    config.write_text(original)
    with pytest.raises(ValueError):
        update_qt_palette(config, canonical, state, "dark")
    assert config.read_text() == original
    assert not state.exists()


@pytest.mark.parametrize(
    "form",
    [
        "@import 'colors.css';",
        '@import "colors.css";',
        '@import url("colors.css");',
        "@import url('colors.css');",
        "@import url(colors.css);",
    ],
)
def test_gtk_forms_placement_and_matugen_is_not_owned(paths, form):
    config, canonical, state = paths
    colors = config.parent / "colors.css"
    colors.write_text("label { color: red; }\n")
    original = f"/* lead */\n{form}\n/* keep */\nlabel {{ color: blue; }}\n"
    config.write_text(original)
    update_gtk_import(config, canonical, state, "dark")
    active = config.read_text()
    assert active.index(form) < active.index("dreamcoder") < active.index("label")
    colors.write_text("label { color: green; }\n")
    assert not update_gtk_import(config, canonical, state, "dark")
    update_gtk_import(config, canonical, state, "light")
    assert config.read_text() == original
    assert colors.read_text() == "label { color: green; }\n"


@pytest.mark.parametrize(
    "original",
    [
        "label {}\n@import 'colors.css';\n",
        "@import nonsense;\n",
        "/* unclosed",
        "@import 'colors.css' screen;",
        "@charset 'utf-8';\n",
        "@import url();\n",
    ],
)
def test_gtk_rejects_unsupported_import_layout(paths, original):
    config, canonical, state = paths
    config.write_text(original)
    with pytest.raises(ValueError):
        update_gtk_import(config, canonical, state, "dark")
    assert config.read_text() == original
    assert not state.exists()


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
def test_links_and_path_rebinding(paths, writer):
    config, canonical, state = paths
    target = config.with_name("target")
    target.write_text("")
    config.symlink_to(target)
    writer(config, canonical, state, "dark")
    assert config.is_symlink()
    config.unlink()
    other = config.with_name("other")
    other.write_bytes(target.read_bytes())
    config.symlink_to(other)
    before = read(config), read(state)
    with pytest.raises(ValueError):
        writer(config, canonical, state, "light")
    assert (read(config), read(state)) == before


def snapshot_files(paths):
    return [(read(path), path.stat().st_mtime_ns if path.exists() else None) for path in paths]


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
@pytest.mark.parametrize("pair", [(0, 1), (0, 2), (1, 2)])
@pytest.mark.parametrize("via_symlink", [False, True])
def test_filesystem_aliases_rejected_before_writes(paths, writer, pair, via_symlink, monkeypatch):
    config = paths[0]
    config.write_text("/* sentinel */\n" if writer is update_gtk_import else "; sentinel\n")
    source, alias = paths[pair[0]], paths[pair[1]]
    if alias.exists():
        alias.unlink()
    os.link(source, alias)
    index = next(index for index in pair if index != 2)
    if via_symlink:
        # State is deliberately never a symlink; config/canonical can be.
        referent = paths[index]
        link = referent.with_name("injected-link")
        link.symlink_to(referent)
        paths = tuple(link if i == index else path for i, path in enumerate(paths))
    before = snapshot_files(paths)
    calls = []
    write_bytes = Path.write_bytes

    def record_bytes(path, data):
        calls.append(path)
        return write_bytes(path, data)

    monkeypatch.setattr(Path, "write_bytes", record_bytes)
    monkeypatch.setattr(
        "dreamcoder_theme.writers_gtk_qt.write_if_changed",
        lambda *args, **kwargs: calls.append(args[0]),
    )
    for mode in ("dark", "light"):
        with pytest.raises(ValueError, match="distinct"):
            writer(*paths, mode)
        assert not calls
        assert snapshot_files(paths) == before
        if via_symlink:
            assert paths[index].is_symlink()


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
@pytest.mark.parametrize("aliased_index", [0, 1])
def test_owned_state_alias_rejected_before_release(paths, writer, aliased_index, monkeypatch):
    writer(*paths, "dark")
    aliased = paths[aliased_index]
    aliased.unlink()
    os.link(paths[2], aliased)
    before = snapshot_files(paths)

    def reject_mutation(*args, **kwargs):
        pytest.fail("Owned alias rejection attempted a write or release")

    monkeypatch.setattr(Path, "write_bytes", reject_mutation)
    monkeypatch.setattr(Path, "unlink", reject_mutation)
    monkeypatch.setattr("dreamcoder_theme.writers_gtk_qt.write_if_changed", reject_mutation)
    for mode in ("dark", "light"):
        with pytest.raises(ValueError, match="distinct"):
            writer(*paths, mode)
        assert snapshot_files(paths) == before


@pytest.mark.parametrize("form", ['@import "{}";', '@import url("{}");'])
def test_canonical_file_uri_rejected_without_writes(paths, form, monkeypatch):
    config, canonical, state = paths
    config.write_text(form.format(canonical.as_uri()) + "\nlabel {}\n")
    before = snapshot_files(paths)

    def reject_write(*args, **kwargs):
        pytest.fail("Canonical URI rejection attempted a write")

    monkeypatch.setattr(Path, "write_bytes", reject_write)
    monkeypatch.setattr("dreamcoder_theme.writers_gtk_qt.write_if_changed", reject_write)
    for mode in ("dark", "light"):
        with pytest.raises(ValueError, match=r"canonical.*URI"):
            update_gtk_import(config, canonical, state, mode)
        assert snapshot_files(paths) == before
        assert not state.exists()


@pytest.mark.parametrize("alias_kind", ["symlink", "hardlink"])
def test_canonical_uri_alias_is_not_adopted(paths, alias_kind):
    config, canonical, state = paths
    alias = canonical.with_name("asset alias.css")
    if alias_kind == "symlink":
        alias.symlink_to(canonical)
    else:
        os.link(canonical, alias)
    config.write_text(f'@import "{alias.as_uri()}";\n')
    before = snapshot_files((*paths, alias))
    with pytest.raises(ValueError, match=r"canonical.*URI"):
        update_gtk_import(config, canonical, state, "dark")
    assert snapshot_files((*paths, alias)) == before


def test_unowned_gtk_escaped_absolute_selection_is_valid(paths):
    config, canonical, state = paths
    escaped = str(canonical).replace("\\", "\\5c ").replace('"', "\\22 ")
    original = f'@import "{escaped}";\nlabel {{}}\n'
    config.write_text(original)
    before = snapshot_files(paths)
    for mode in ("dark", "light"):
        assert not update_gtk_import(config, canonical, state, mode)
        assert snapshot_files(paths) == before
        assert not state.exists()


def test_unrelated_file_uri_import_is_preserved(paths):
    config, canonical, state = paths
    external = config.with_name("external space.css")
    external.write_text("/* personal external stylesheet */\n")
    original = f'@import "{external.as_uri()}";\nlabel {{}}\n'
    config.write_text(original)
    assert update_gtk_import(config, canonical, state, "dark")
    assert original.splitlines()[0] in config.read_text()
    assert update_gtk_import(config, canonical, state, "light")
    assert config.read_text() == original
    assert not state.exists()


def test_unowned_gtk_identical_import_is_never_adopted(paths):
    config, canonical, state = paths
    # Use a plain path to make this an ordinary valid unowned import.
    canonical = canonical.with_name("canonical.css")
    canonical.write_text("/* canonical */")
    original = f'@import "{canonical}";\nlabel {{}}\n'
    config.write_text(original)
    assert not update_gtk_import(config, canonical, state, "dark")
    assert not update_gtk_import(config, canonical, state, "light")
    assert not state.exists()
    assert config.read_text() == original


@pytest.mark.parametrize("major", ["3", "4"])
@pytest.mark.parametrize("representation", ["escaped", "uri"])
@pytest.mark.parametrize(
    "filename", ['canonical space "quoted".css', r"back\slash #hash.css", "non-ascii-é.css"]
)
def test_native_gtk_writer_parser_and_overwrite(paths, major, filename, representation):
    library = ctypes.util.find_library("gtk-" + major)
    assert library, "Required GTK fixture parser unavailable"
    config, canonical, state = paths
    canonical = canonical.with_name(filename)
    canonical.write_text("@define-color view_bg_color #000000;\n")
    colors = config.parent / "colors.css"
    colors.write_text("@define-color view_bg_color #abcdef;\nlabel { color: red; }\n")
    config.write_text("@import url('colors.css');\nlabel { background-color: @view_bg_color; }\n")
    if representation == "uri":
        config.write_text(
            f'@import "{canonical.as_uri()}";\nlabel {{ background-color: @view_bg_color; }}\n'
        )
        before = snapshot_files((config, canonical, state))
        with pytest.raises(ValueError, match=r"canonical.*URI"):
            update_gtk_import(config, canonical, state, "dark")
        assert snapshot_files((config, canonical, state)) == before
    else:
        update_gtk_import(config, canonical, state, "dark")
    probe = r"""
import ctypes as C, sys
lib = C.CDLL(sys.argv[1])
lib.gtk_css_provider_new.restype = C.c_void_p
lib.gtk_css_provider_load_from_path.argtypes = [C.c_void_p, C.c_char_p] + ([C.c_void_p] if sys.argv[2] == '3' else [])
lib.gtk_css_provider_to_string.argtypes = [C.c_void_p]
lib.gtk_css_provider_to_string.restype = C.c_void_p
p = lib.gtk_css_provider_new()
lib.gtk_css_provider_load_from_path(p, sys.argv[3].encode(), *([None] if sys.argv[2] == '3' else []))
print(C.string_at(lib.gtk_css_provider_to_string(p)).decode())
"""
    env = {key: value for key, value in os.environ.items() if key in {"PATH", "LANG", "LC_ALL"}}
    for key in (
        "HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_CACHE_HOME",
        "PI_AGENT_DIR",
        "PI_CODING_AGENT_DIR",
        "GENTLE_SHELL_HOME",
    ):
        env[key] = str(config.parent / key)
    for value in ("#123456", "#fedcba"):
        colors.write_text(f"@define-color view_bg_color {value};\nlabel {{ color: red; }}\n")
        result = subprocess.run(
            [sys.executable, "-c", probe, library, major, str(config)],
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
        if representation == "uri" and major == "3":
            assert "file:" in result.stderr
            assert "@define-color view_bg_color rgb(0,0,0);" not in result.stdout
        else:
            assert not result.stderr
            assert "@define-color view_bg_color rgb(0,0,0);" in result.stdout
            assert "background-color: @view_bg_color;" in result.stdout


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
@pytest.mark.parametrize(
    "raw", ["null", "[]", "{", '{"version":true}', '{"version":1,"version":2}']
)
def test_corrupt_standalone_state_is_not_success(paths, writer, raw):
    config, canonical, state = paths
    state.write_text(raw)
    before = read(config), read(state)
    for mode in ("dark", "light"):
        with pytest.raises(ValueError):
            writer(config, canonical, state, mode)
        assert (read(config), read(state)) == before


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
@pytest.mark.parametrize("mismatch", ["target", "state_path", "config_path", "canonical_missing"])
def test_ownership_identity_is_not_transferable(paths, writer, mismatch):
    config, canonical, state = paths
    writer(config, canonical, state, "dark")
    if mismatch == "target":
        writer = update_qt_palette if writer is update_gtk_import else update_gtk_import
    elif mismatch == "state_path":
        moved = state.with_name("moved-state.json")
        moved.write_bytes(state.read_bytes())
        state = moved
    elif mismatch == "config_path":
        copied = config.with_name("copied-config")
        copied.write_bytes(config.read_bytes())
        config = copied
    else:
        canonical.unlink()
    before = read(config), read(state)
    with pytest.raises(ValueError):
        writer(config, canonical, state, "dark")
    assert (read(config), read(state)) == before


@pytest.mark.parametrize("edit", ["style=personal\n", "; personal comment\n", "\n"])
def test_qt_added_group_preserves_new_personal_content(paths, edit):
    config, canonical, state = paths
    update_qt_palette(config, canonical, state, "dark")
    config.write_text(config.read_text() + edit)
    update_qt_palette(config, canonical, state, "light")
    expected = "[Appearance]\n" + edit if edit.strip() else edit
    assert config.read_text() == expected
    assert not state.exists()


def test_qt_correct_unowned_selection_is_not_adopted(paths):
    config, canonical, state = paths
    original = f'[Appearance]\ncolor_scheme_path={json.dumps(str(canonical))}\ncustom_palette="true"\nstyle=Fusion\n'
    config.write_text(original)
    assert not update_qt_palette(config, canonical, state, "dark")
    assert not update_qt_palette(config, canonical, state, "light")
    assert config.read_text() == original
    assert not state.exists()


def test_qt_state_contains_no_unrelated_config(paths):
    config, canonical, state = paths
    config.write_text(
        "[Appearance]\ncustom_palette=true\nstyle=Personal\n[Fonts]\nfixed=Personal Font\n"
    )
    update_qt_palette(config, canonical, state, "dark")
    data = json.loads(state.read_text())
    assert data["version"] == 1
    assert set(data["ownership"]["rows"]) == {"color_scheme_path"}
    assert "Personal" not in state.read_text()
    config.write_text(config.read_text().replace("Personal Font", "New Font"))
    update_qt_palette(config, canonical, state, "light")
    assert "custom_palette=true" in config.read_text()
    assert "fixed=New Font" in config.read_text()


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
@pytest.mark.parametrize(
    "invalid", ["mode", "relative", "collision", "control", "state_link", "matugen", "settings"]
)
def test_invalid_contract_rejected_without_writes(paths, writer, invalid):
    config, canonical, state = paths
    config.write_text("/* sentinel */" if writer is update_gtk_import else "; sentinel\n")
    mode = "dark"
    if invalid == "mode":
        mode = "dusk"
    elif invalid == "relative":
        canonical = Path("relative.css")
    elif invalid == "collision":
        state = config
    elif invalid == "control":
        canonical = canonical.with_name("bad\npath.css")
    elif invalid == "state_link":
        state.symlink_to(config)
    elif invalid == "matugen":
        config = config.with_name("colors.css")
    else:
        config = config.with_name("settings.ini")
    before = read(config), read(state)
    with pytest.raises(ValueError):
        writer(config, canonical, state, mode)
    assert (read(config), read(state)) == before


@pytest.mark.parametrize("original", [None, b"", b"/* comment */", b"@import 'colors.css';"])
def test_gtk_absent_and_no_final_newline_roundtrip(paths, original):
    config, canonical, state = paths
    if original is not None:
        config.write_bytes(original)
    update_gtk_import(config, canonical, state, "dark")
    update_gtk_import(config, canonical, state, "light")
    assert read(config) == original


@pytest.mark.parametrize(
    "original",
    ["[Appearance]", "[Appearance]\ncolor_scheme_path=old", "[Appearance]\ncustom_palette=false"],
)
def test_qt_eof_key_or_header_roundtrip(paths, original):
    config, canonical, state = paths
    config.write_text(original)
    update_qt_palette(config, canonical, state, "dark")
    update_qt_palette(config, canonical, state, "light")
    assert config.read_text() == original


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
def test_valid_state_with_duplicate_fields_is_corrupt(paths, writer):
    config, canonical, state = paths
    writer(config, canonical, state, "dark")
    state.write_text(state.read_text().replace('"version": 1,', '"version": 1, "version": 1,'))
    before = read(config), read(state)
    with pytest.raises(ValueError, match="Duplicate"):
        writer(config, canonical, state, "light")
    assert (read(config), read(state)) == before


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
def test_light_can_restore_after_canonical_asset_removed(paths, writer):
    config, canonical, state = paths
    writer(config, canonical, state, "dark")
    canonical.unlink()
    assert writer(config, canonical, state, "light")
    assert not config.exists()
    assert not state.exists()


def test_unowned_gtk_conflicting_import_placement_rejected(paths):
    config, canonical, state = paths
    canonical = canonical.with_name("canonical.css")
    canonical.write_text("/* canonical */")
    original = f'@import "{canonical}";\n@import "colors.css";\nlabel {{}}\n'
    config.write_text(original)
    with pytest.raises(ValueError, match="conflicting placement"):
        update_gtk_import(config, canonical, state, "dark")
    assert config.read_text() == original
    assert not state.exists()


@pytest.mark.parametrize("writer", [update_gtk_import, update_qt_palette])
def test_semantically_identical_owned_representation_drift_is_explicit(paths, writer):
    config, canonical, state = paths
    writer(config, canonical, state, "dark")
    content = config.read_text()
    if writer is update_qt_palette:
        content = content.replace("custom_palette=true", 'custom_palette="true"')
    else:
        content = content.replace("@import ", "@import  ")
    config.write_text(content)
    before = read(config), read(state)
    with pytest.raises(ValueError, match="drift"):
        writer(config, canonical, state, "light")
    assert (read(config), read(state)) == before
