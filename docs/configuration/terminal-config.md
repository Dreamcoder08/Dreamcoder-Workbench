# Terminal Configuration

## Supported Terminals

| Terminal | Theme Format | Notes |
|----------|-------------|-------|
| Kitty | `.conf` | GPU-accelerated, primary terminal |
| Ghostty | Custom | Custom shaders, blur effects |
| WezTerm | `.lua` | Cross-platform, Lua config |
| Alacritty | `.toml` | Minimal, fast |
| Orca | Live profile state (SQLite) | Written into Orca's own profile, not a repo file |

### Orca

Orca migrated its profile from JSON to SQLite. The authoritative store is
`~/.config/orca/profiles/local-default/profile-state.db`, and the
`profile-state.db.authority` marker says `sqlite`. The neighbouring
`orca-data.json` is only an export Orca rewrites on save — editing it changes
nothing Orca reads. `ORCA_DATA_PATH` overrides the profile directory and
`ORCA_STATE_DB_PATH` overrides the database path directly.

Both `dreamcoder dark` and `dreamcoder sync` write the profile's `settings`
document: they define `Dreamcoder Dark` and `Dreamcoder Light` in
`terminalCustomThemes`, select them through `terminalThemeDark` /
`terminalThemeLight`, enable `terminalUseSeparateLightTheme`, set the
per-appearance divider colors from the palette `border_ui` token, and set the
app chrome `theme` to the active Dreamcoder mode.

A custom theme is addressed by id, not by display name: Orca reads the
selection as `custom:<id>` and takes the colors from the entry's nested
`terminal` object. The managed ids are `manual:dreamcoder-dark` and
`manual:dreamcoder-light`. Entries missing usable colors are silently
discarded by Orca, which is why a name-only entry leaves Orca on a built-in
scheme while still showing the configured name.

The database row records the profile revision it was written at and a
`content_hash` of the exact payload bytes, and the profile revision in
`profile_state_meta` moves with it; the previous database is copied to
`profile-state.db.dreamcoder-backup.<timestamp>` before each write.

Orca holds its profile in memory while its main window is open and flushes
that copy over external edits, so the sync skips the store and reports
`skipped-running` instead of writing something that would be discarded.
Close Orca, then re-run `dreamcoder dark` or `dreamcoder light` to apply.

## Theme Switching

Terminals auto-detect `DREAMCODER_THEME_MODE` env var:

```bash
export DREAMCODER_THEME_MODE="dark"  # or "light"
```

## Font Configuration

All terminals use JetBrainsMono Nerd Font:

```
Font: JetBrainsMono Nerd Font
Size: 14pt
Ligatures: Enabled
```

## Key Bindings

Common key bindings across terminals:

| Action | Kitty | Ghostty | WezTerm | Alacritty |
|--------|-------|---------|---------|-----------|
| New tab | Ctrl+Shift+T | Ctrl+Shift+T | Ctrl+Shift+T | Ctrl+Shift+T |
| Close tab | Ctrl+Shift+W | Ctrl+Shift+W | Ctrl+Shift+W | Ctrl+Shift+W |
| Split horizontal | Ctrl+Shift+5 | Ctrl+Shift+5 | Ctrl+Shift+5 | Ctrl+Shift+5 |
| Split vertical | Ctrl+Shift+6 | Ctrl+Shift+6 | Ctrl+Shift+6 | Ctrl+Shift+6 |
