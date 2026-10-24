"""Opt-in GTK/Qt ownership writers; no default paths or pipeline integration.

Only dark/light are accepted. False is a validated no-op, never a rejection.
ValueError means malformed/unsupported input, corrupt ownership, or managed
selection drift, detected before any writes. Files are UTF-8; original bytes,
including CRLF and missing final newlines, are retained outside owned spans.
Config writes follow existing writers' link-preserving semantics. State JSON
uses their atomic replacement helper. I/O failures are not transactional: the
caller must snapshot config AND state (T2b.3), including symlink referents.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .writers import write_if_changed

_MARKER = "/* dreamcoder managed canonical import */"
_KEYS = ("color_scheme_path", "custom_palette")


def _text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8") if path.exists() else ""
    except UnicodeError as exc:
        raise ValueError(f"{path}: configuration must be UTF-8") from exc


def _identity(path: Path) -> list[str]:
    return [str(path.absolute()), str(path.resolve())]


def _same_file(left: Path, right: Path) -> bool:
    """Compare referents, while allowing paths that have not been created yet."""
    if left.resolve() == right.resolve():
        return True
    try:
        return left.samefile(right)
    except FileNotFoundError:
        return False


def _digest(data: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _unique_json(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate ownership JSON field")
        result[key] = value
    return result


def _prepare(
    config: Path, canonical: Path, state: Path, mode: str, target: str
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    if mode not in {"dark", "light"}:
        raise ValueError("Only dark/light modes are supported")
    paths = (config, canonical, state)
    if any(not p.is_absolute() or any(ord(c) < 32 for c in str(p)) for p in paths):
        raise ValueError("Injected paths must be absolute and contain no control characters")
    if state.is_symlink() or any(
        _same_file(left, right) for index, left in enumerate(paths) for right in paths[index + 1 :]
    ):
        raise ValueError("Config, canonical and non-symlink state paths must be distinct")
    if config.name in {"colors.css", "settings.ini"} or (
        target == "gtk" and canonical.name == "colors.css"
    ):
        raise ValueError("Matugen colors.css and GTK settings.ini are never writer targets/assets")
    if config.is_symlink() and not config.exists():
        raise ValueError(f"{config}: dangling config symlink")
    binding = {"target": target, "paths": [_identity(p) for p in paths]}
    owned = None
    if state.exists():
        try:
            envelope = json.loads(_text(state), object_pairs_hook=_unique_json)
            if set(envelope) != {"version", "binding", "existed", "ownership", "checksum"}:
                raise ValueError("Unexpected ownership fields")
            checksum = envelope.pop("checksum")
            if (
                type(envelope["version"]) is not int
                or envelope["version"] != 1
                or type(envelope["existed"]) is not bool
            ):
                raise ValueError("Unsupported ownership version")
            if checksum != _digest(envelope) or envelope["binding"] != binding:
                raise ValueError("Corrupt state or path binding mismatch")
            if not config.exists():
                raise ValueError("Owned config is missing")
            owned = envelope
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ValueError(f"{state}: invalid ownership: {exc}") from exc
    if mode == "dark" and not canonical.is_file():
        raise ValueError(f"{canonical}: canonical asset is missing")
    return _text(config), binding, owned


def _finish(
    config: Path,
    state: Path,
    original: str,
    updated: str,
    binding: dict[str, Any],
    ownership: dict[str, Any],
    existed: bool,
) -> bool:
    if original == updated:
        return False
    envelope = {"version": 1, "binding": binding, "existed": existed, "ownership": ownership}
    envelope["checksum"] = _digest(envelope)
    # All parsing and ownership checks must precede this commit boundary.
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_bytes(updated.encode("utf-8"))
    write_if_changed(state, json.dumps(envelope, indent=2), replace_symlink=True)
    return True


def _release(config: Path, state: Path, updated: str, existed: bool) -> bool:
    if not existed and not updated and not config.is_symlink():
        config.unlink()
    else:
        config.write_bytes(updated.encode("utf-8"))
    state.unlink()
    return True


_CSS_STRING = r"""(?:"(?:\\[^\r\n]|[^"\\\r\n])*"|'(?:\\[^\r\n]|[^'\\\r\n])*')"""
_IMPORT = re.compile(
    r"@import\s+(" + _CSS_STRING + r"|url\(\s*(?:" + _CSS_STRING + r"|[^\s'\"()\\;]+)\s*\))\s*;",
    re.I,
)


def _css_unescape(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        escaped = match.group(1)
        if re.fullmatch(r"[0-9a-fA-F]{1,6}\s?", escaped):
            number = int(escaped.strip(), 16)
            if not number or number > 0x10FFFF or 0xD800 <= number <= 0xDFFF:
                raise ValueError("Invalid CSS escape")
            return chr(number)
        return escaped

    return re.sub(r"\\([0-9a-fA-F]{1,6}\s?|.)", replace, value)


def _gtk_import_path(value: str, config: Path, canonical: Path) -> Path:
    parsed = urlparse(value)
    if value.startswith("/") or not parsed.scheme:
        return Path(value)
    if parsed.scheme == "file" and not (parsed.netloc or parsed.query or parsed.fragment):
        path = Path(unquote(parsed.path))
        # GTK4 decodes file URIs, but GTK3 treats them as relative file:/
        # paths. Never validate this as a canonical selection.
        if _same_file(path, canonical):
            raise ValueError(f"{config}: canonical GTK file URI is not portable to GTK3/4")
        return path
    raise ValueError("Unsupported GTK import URI")


def _gtk_layout(
    text: str, config: Path, canonical: Path
) -> tuple[int, list[tuple[int, int, Path]]]:
    """Accept leading imports in quoted/url forms, comments and whitespace.

    Reject media clauses, charset/other leading at-rules and late imports.
    Widget rules are retained verbatim, not interpreted or rewritten.
    """
    i = 0
    imports: list[tuple[int, int, Path]] = []
    while i < len(text):
        trivia = re.match(r"\s+|/\*.*?\*/", text[i:], re.S)
        if trivia:
            i += trivia.end()
            continue
        if text[i:].startswith("/*"):
            raise ValueError("Unterminated CSS comment")
        if text[i:].lower().startswith("@import"):
            match = _IMPORT.match(text, i)
            if not match:
                raise ValueError("Unsupported GTK import")
            value = match.group(1)
            if value.lower().startswith("url("):
                value = value[4:-1].strip()
            if value[:1] in {"'", '"'}:
                value = _css_unescape(value[1:-1])
            path = _gtk_import_path(value, config, canonical)
            imports.append((i, match.end(), (config.parent / path).resolve()))
            i = match.end()
            continue
        break
    # Lexically skip strings/comments so text inside them is not an import.
    remainder = text[i:]
    tokens = re.compile(r"/\*.*?\*/|" + _CSS_STRING, re.S)
    plain = tokens.sub("", remainder)
    if "/*" in plain or re.search(r"@import\b", plain, re.I):
        raise ValueError("Unterminated comment or import after widget rules")
    if remainder.lstrip().startswith("@"):
        raise ValueError("Unsupported leading GTK at-rule")
    return i, imports


def _css_path(path: Path) -> str:
    # GTK3 does not URI-decode percent escapes in imported file paths.
    return str(path).replace("\\", "\\5c ").replace('"', "\\22 ")


def update_gtk_import(config: Path, canonical: Path, state: Path, mode: str) -> bool:
    """Own one marked import after existing imports and before local rules.

    CSS-escaped absolute paths safely encode spaces/quotes/backslashes. An identical unowned
    LAST import is a no-op and never adopted; earlier/duplicate identical imports
    conflict. Light without state never removes an unowned import. State stores
    only the inserted span, original existence and lexical/resolved path binding.
    """
    text, binding, owned = _prepare(config, canonical, state, mode, "gtk")
    position, imports = _gtk_layout(text, config, canonical)
    matches = [row for row in imports if row[2] == canonical.resolve()]
    if owned:
        data = owned["ownership"]
        if (
            not isinstance(data, dict)
            or set(data) != {"inserted"}
            or not isinstance(data["inserted"], str)
        ):
            raise ValueError(f"{state}: invalid GTK ownership")
        fragment = data["inserted"]
        expected = f'{_MARKER}\n@import "{_css_path(canonical)}";\n'
        if (
            fragment not in {expected, "\n" + expected}
            or text.count(fragment) != 1
            or len(matches) != 1
            or text.count(_MARKER) != 1
        ):
            raise ValueError(f"{config}: managed GTK import drift")
        if imports[-1] != matches[0]:
            raise ValueError(f"{config}: managed import is no longer last")
        if mode == "dark":
            return False
        return _release(config, state, text.replace(fragment, "", 1), owned["existed"])
    if _MARKER in text:
        raise ValueError(f"{config}: managed marker without ownership")
    if mode == "light":
        return False
    if matches:
        if len(matches) == 1 and imports[-1] == matches[0]:
            return False
        raise ValueError(f"{config}: unowned canonical import has conflicting placement")
    fragment = f'{_MARKER}\n@import "{_css_path(canonical)}";\n'
    if position and text[position - 1] not in "\r\n":
        fragment = "\n" + fragment
    updated = text[:position] + fragment + text[position:]
    _gtk_layout(updated, config, canonical)
    return _finish(config, state, text, updated, binding, {"inserted": fragment}, config.exists())


def _qt_layout(
    text: str,
) -> tuple[list[str], dict[str, int], dict[str, tuple[int, str]]]:
    """Strict QSettings INI subset: unique bare keys and simple group headers.

    No continuation lines, quoted/escaped keys, duplicate groups/keys, section
    inheritance, or nested/case-variant Appearance groups. Unknown ordinary
    groups/values remain opaque. Owned values support bare or JSON-style quoted
    strings; unsupported QSettings encodings raise instead of guessing.
    """
    lines = text.splitlines(keepends=True)
    groups: dict[str, int] = {}
    rows: dict[str, dict[str, tuple[int, str]]] = {}
    group: str | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith((";", "#")):
            continue
        if stripped.startswith("["):
            match = re.fullmatch(r"\[([A-Za-z0-9_ /.-]+)\]", stripped)
            if not match or match[1] in groups:
                raise ValueError("Malformed or duplicate Qt section")
            group = match[1]
            if group.lower().startswith("appearance") and group != "Appearance":
                raise ValueError("Unsupported Qt Appearance section")
            groups[group] = index
            rows[group] = {}
            continue
        match = re.fullmatch(r"\s*([A-Za-z0-9_./-]+)\s*=([^\r\n]*)(?:\r?\n)?", line)
        if not match or group is None or match[1] in rows[group]:
            raise ValueError("Malformed, quoted or duplicate Qt key")
        key = match[1]
        if group == "Appearance" and key.lower() in _KEYS and key not in _KEYS:
            raise ValueError("Unsupported Qt key casing")
        rows[group][key] = (index, match[2].strip())
    appearance = rows.get("Appearance", {})
    for key in _KEYS:
        if key in appearance:
            value = _qt_value(appearance[key][1])
            if key == "custom_palette" and value not in {"true", "false"}:
                raise ValueError("Unsupported Qt custom_palette value")
    return lines, groups, appearance


def _qt_value(raw: str) -> str:
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except ValueError as exc:
            raise ValueError("Unsupported quoted Qt value") from exc
        if not isinstance(value, str):
            raise ValueError("Unsupported Qt string")
        return value
    if any(c in raw for c in ('"', "\\", "\x00")) or raw.startswith("@"):
        raise ValueError("Unsupported Qt value encoding")
    return raw


def _qt_expected(canonical: Path) -> dict[str, str]:
    path = str(canonical)
    return {"color_scheme_path": json.dumps(path, ensure_ascii=False), "custom_palette": "true"}


def update_qt_palette(config: Path, canonical: Path, state: Path, mode: str) -> bool:
    """Patch only Appearance color_scheme_path/custom_palette, preserving text.

    State records original/expected rows only for changed keys, any owned header
    and a missing-newline boundary. Already-correct keys are NOT owned/restored.
    While owned, both active values and exact owned representations must match;
    conflicts (including duplicates/quoting of keys) raise before writing.
    Added empty Appearance groups/configs are removed on Light; groups/files
    with subsequent unrelated user edits survive. Repeat Dark never rebases.
    """
    text, binding, owned = _prepare(config, canonical, state, mode, "qt")
    lines, groups, rows = _qt_layout(text)
    expected = _qt_expected(canonical)
    if owned:
        return _restore_qt(config, state, mode, canonical, owned, lines, groups, rows)
    if mode == "light":
        return False
    return _activate_qt(config, canonical, state, text, binding, lines, groups, rows, expected)


def _validate_qt_ownership(
    config: Path,
    state: Path,
    canonical: Path,
    data: Any,
    lines: list[str],
    groups: dict[str, int],
    rows: dict[str, tuple[int, str]],
) -> None:
    if not isinstance(data, dict) or set(data) != {"rows", "header", "added_section", "boundary"}:
        raise ValueError(f"{state}: invalid Qt ownership")
    patches = data["rows"]
    if not isinstance(patches, dict) or not patches or not set(patches) <= set(_KEYS):
        raise ValueError(f"{state}: invalid managed keys")
    for key in _KEYS:
        if key not in rows or _qt_value(rows[key][1]) != (
            str(canonical) if key == "color_scheme_path" else "true"
        ):
            raise ValueError(f"{config}: Qt active selection drift")
    for key, patch in patches.items():
        if (
            not isinstance(patch, dict)
            or set(patch) != {"before", "after"}
            or not isinstance(patch["after"], str)
            or (patch["before"] is not None and not isinstance(patch["before"], str))
        ):
            raise ValueError(f"{state}: invalid row ownership")
        if lines[rows[key][0]] != patch["after"]:
            raise ValueError(f"{config}: managed Qt key drift: {key}")
    header = data["header"]
    if (
        type(data["added_section"]) is not bool
        or not isinstance(data["boundary"], str)
        or (header is not None and not isinstance(header, str))
    ):
        raise ValueError(f"{state}: invalid Qt boundary")
    if header is not None and lines[groups["Appearance"]] != header + "\n":
        raise ValueError(f"{config}: managed Qt header drift")


def _restore_qt(
    config: Path,
    state: Path,
    mode: str,
    canonical: Path,
    owned: dict[str, Any],
    lines: list[str],
    groups: dict[str, int],
    rows: dict[str, tuple[int, str]],
) -> bool:
    data = owned["ownership"]
    _validate_qt_ownership(config, state, canonical, data, lines, groups, rows)
    if mode == "dark":
        return False
    for key, patch in data["rows"].items():
        lines[rows[key][0]] = patch["before"] or ""
    if data["header"] is not None:
        lines[groups["Appearance"]] = data["header"]
    updated = "".join(lines)
    if data["added_section"]:
        after_lines, after_groups, _ = _qt_layout(updated)
        start = after_groups["Appearance"]
        end = next(
            (
                i
                for i in range(start + 1, len(after_lines))
                if after_lines[i].strip().startswith("[")
            ),
            len(after_lines),
        )
        if not "".join(after_lines[start + 1 : end]).strip():
            del after_lines[start]
            updated = "".join(after_lines)
    boundary = data["boundary"]
    if boundary and updated.endswith(boundary + "\n"):
        updated = updated[:-1]
    _qt_layout(updated)
    return _release(config, state, updated, owned["existed"])


def _activate_qt(
    config: Path,
    canonical: Path,
    state: Path,
    text: str,
    binding: dict[str, Any],
    lines: list[str],
    groups: dict[str, int],
    rows: dict[str, tuple[int, str]],
    expected: dict[str, str],
) -> bool:
    newline = "\r\n" if "\r\n" in text else "\n"
    patches: dict[str, dict[str, Any]] = {}
    for key in _KEYS:
        desired = str(canonical) if key == "color_scheme_path" else "true"
        if key in rows and _qt_value(rows[key][1]) == desired:
            continue
        before = lines[rows[key][0]] if key in rows else None
        # Preserve indentation and delimiter whitespace on replaced rows.
        delimiter = re.match(r"\s*[^=]+=[ \t]*", before) if before else None
        prefix = delimiter[0] if delimiter else key + "="
        ending = (
            "\r\n"
            if before and before.endswith("\r\n")
            else "\n"
            if before and before.endswith("\n")
            else ""
            if before
            else newline
        )
        after = prefix + expected[key] + ending
        patches[key] = {"before": before, "after": after}
        if before is not None:
            lines[rows[key][0]] = after
    if not patches:
        return False
    added = "Appearance" not in groups
    boundary, header = "", None
    missing = "".join(p["after"] for p in patches.values() if p["before"] is None)
    if added:
        if text and not text.endswith("\n"):
            boundary = text.splitlines()[-1]
            lines.append("\n")
        lines.append("[Appearance]" + newline + missing)
    elif missing:
        index = groups["Appearance"]
        if not lines[index].endswith("\n"):
            header = lines[index]
            lines[index] += "\n"
        lines.insert(index + 1, missing)
    updated = "".join(lines)
    _qt_layout(updated)
    data = {"rows": patches, "header": header, "added_section": added, "boundary": boundary}
    return _finish(config, state, text, updated, binding, data, config.exists())
