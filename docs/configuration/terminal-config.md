# Configure a terminal

Choose the terminal you actually use and review its configuration before installing or changing it. The [desktop installation guide](../../INSTALL.md) covers the full overlay; component availability varies by platform. Theme generation does not install a terminal or guarantee that an open window reloads its colors.

## Apply and verify a theme

With the repository virtual environment active, the [theme system guide](theme-system.md) explains the wrapper's `dark`, `light` and `sync` operations and their writes. Check the application's selected theme and reload or restart it if needed.

| Integration | What the repository provides |
|------------|-------------------------------|
| Kitty | Generated color and UI configuration; sync manages the UI include. |
| Ghostty | Generated theme and a configuration selector. |
| Warp | Generated theme and settings updates. |
| Orca IDE | Best-effort update of an existing live profile, not a repository theme file. |

A generated file is not evidence that other terminals, fonts, shortcuts or platform combinations are configured. Consult the terminal's own documentation for its font, keybindings and reload behavior.

## Orca IDE profile

Orca IDE is distinct from the GNOME screen reader. Sync and mode activation attempt to update its existing profile; missing or malformed profiles are skipped. When `profile-state.db.authority` says `sqlite`, the database at `~/.config/orca/profiles/local-default/profile-state.db` is authoritative and the adjacent JSON is an export. The integration also supports a legacy JSON store. `ORCA_DATA_PATH` overrides the JSON path and thereby the default database directory; `ORCA_STATE_DB_PATH` overrides the database path directly.

The managed entries use IDs `manual:dreamcoder-dark` and `manual:dreamcoder-light`, selected as `custom:<id>` with colors in each entry's nested `terminal` object. The settings also select separate light and dark themes, set divider colors and update the app chrome mode. Existing unrelated theme entries are retained. SQLite updates advance the profile revision and payload hash and back up the database first; editing the JSON export does not change the authoritative SQLite profile.

Orca's main window holds a profile in memory and can overwrite external edits. A `skipped-running` result means close the window and retry the wrapper's `dark` or `light` command, then reopen Orca. Other skipped results require inspecting the profile rather than assuming it was updated.

Next, configure your [shell](shell-config.md) or [multiplexer](multiplexer-config.md), or return to the [documentation hub](../README.md).
