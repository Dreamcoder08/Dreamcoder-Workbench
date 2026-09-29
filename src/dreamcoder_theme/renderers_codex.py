"""Focused CLI/editor theme renderers."""

from __future__ import annotations

from .renderers_opencode import opencode_content, opencode_tokens


def codex_tmtheme_content(c: dict[str, str]) -> str:
    t = opencode_tokens(c)
    selection = t["selection"]
    sel_fg = t["selection_fg"]
    line_highlight = c["surface1"]  # subtle, not same as selection
    gutter = c["surface2"]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>name</key><string>Dreamcoder</string>
  <key>settings</key>
  <array>
    <dict><key>settings</key><dict>
      <key>background</key><string>{c["bg"]}</string>
      <key>foreground</key><string>{c["text"]}</string>
      <key>caret</key><string>{c["accent"]}</string>
      <key>selection</key><string>{selection}</string>
      <key>selectionForeground</key><string>{sel_fg}</string>
      <key>lineHighlight</key><string>{line_highlight}</string>
      <key>gutter</key><string>{gutter}</string>
      <key>gutterForeground</key><string>{c["muted"]}</string>
      <key>invisibles</key><string>{c["comment"]}</string>
    </dict></dict>
    <dict><key>scope</key><string>comment</string><key>settings</key><dict><key>foreground</key><string>{t["comment"]}</string><key>fontStyle</key><string>italic</string></dict></dict>
    <dict><key>scope</key><string>keyword, storage</string><key>settings</key><dict><key>foreground</key><string>{t["keyword"]}</string><key>fontStyle</key><string>bold</string></dict></dict>
    <dict><key>scope</key><string>entity.name.function, support.function</string><key>settings</key><dict><key>foreground</key><string>{t["function"]}</string></dict></dict>
    <dict><key>scope</key><string>variable, meta.definition.variable</string><key>settings</key><dict><key>foreground</key><string>{t["variable"]}</string></dict></dict>
    <dict><key>scope</key><string>string</string><key>settings</key><dict><key>foreground</key><string>{t["string"]}</string></dict></dict>
    <dict><key>scope</key><string>constant.numeric, constant.language</string><key>settings</key><dict><key>foreground</key><string>{t["constant"]}</string></dict></dict>
    <dict><key>scope</key><string>entity.name.type, support.type</string><key>settings</key><dict><key>foreground</key><string>{t["type"]}</string></dict></dict>
    <dict><key>scope</key><string>punctuation</string><key>settings</key><dict><key>foreground</key><string>{t["punctuation"]}</string></dict></dict>
    <dict><key>scope</key><string>keyword.operator</string><key>settings</key><dict><key>foreground</key><string>{t["operator"]}</string></dict></dict>
    <dict><key>scope</key><string>constant.character.escape</string><key>settings</key><dict><key>foreground</key><string>{t["string"]}</string></dict></dict>
    <dict><key>scope</key><string>entity.name.tag</string><key>settings</key><dict><key>foreground</key><string>{t["keyword"]}</string></dict></dict>
    <dict><key>scope</key><string>entity.other.attribute-name</string><key>settings</key><dict><key>foreground</key><string>{t["property"]}</string></dict></dict>
    <dict><key>scope</key><string>invalid</string><key>settings</key><dict><key>foreground</key><string>{c["error"]}</string></dict></dict>
    <dict><key>scope</key><string>markup.heading, markup.bold</string><key>settings</key><dict><key>foreground</key><string>{c["accent"]}</string><key>fontStyle</key><string>bold</string></dict></dict>
    <dict><key>scope</key><string>markup.italic</string><key>settings</key><dict><key>foreground</key><string>{c["diagnostic"]}</string><key>fontStyle</key><string>italic</string></dict></dict>
    <dict><key>scope</key><string>meta.diff, meta.diff.header</string><key>settings</key><dict><key>foreground</key><string>{c["lavender"]}</string></dict></dict>
    <dict><key>scope</key><string>support.class, support.constant</string><key>settings</key><dict><key>foreground</key><string>{t["type"]}</string></dict></dict>
  </array>
</dict>
</plist>
"""


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
        consumer_id="codex_app",
        renderer=opencode_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Codex App JSON theme",
    ),
    RendererRegistration(
        consumer_id="codex_theme",
        renderer=codex_tmtheme_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Codex CLI TextMate theme",
    ),
    RendererRegistration(
        consumer_id="bat_theme",
        renderer=codex_tmtheme_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Bat TextMate theme",
    ),
)
