# Herdr Runtime Contract Evidence

## Herdr 0.7.3 installed-runtime profile

`herdr-0.7.3` is bound to local
`herdr 0.7.3`, binary SHA-256
`043ef43ecbabda28465dcff1eec3184518150d567b8b8f20cda9c6c88770641d`, and the
official v0.7.3 source tag object `d0111c9f9022e0ec26d8f03236a91b026b567d45`,
which points to source commit `299dd4163a96381ec2d8e5bde13d7ba6d6432373`.

The official version-bound configuration reference documents `[theme]` keys
`name`, `auto_switch`, `dark_name`, and `light_name`, plus exactly these
`[theme.custom]` keys:

`accent`, `panel_bg`, `surface0`, `surface1`, `surface_dim`, `overlay0`,
`overlay1`, `text`, `subtext0`, `mauve`, `green`, `yellow`, `red`, `blue`,
`teal`, and `peach`.

Custom colors accept hex values, so repository variants serialize canonical
Dreamcoder tokens as `#RRGGBB` strings. `window-title`, `tab-title`, and every
other undocumented custom field are excluded.

## Static repository variants

`theme.name` selects a built-in base theme and defaults to `catppuccin`.
`theme.auto_switch` defaults to `false`; `theme.dark_name` and
`theme.light_name` are optional and apply only to host-appearance switching.

The managed static Dark and Light repository variants emit only
`name = "catppuccin"` and the allow-listed custom overrides. They deliberately
omit `auto_switch`, `dark_name`, and `light_name`; no labels are invented. The
variants are generated under
`DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3/` and are never selected or
written to the user's active configuration by theme synchronization.

## Isolated validation and reload evidence

An isolated temporary environment using `HERDR_CONFIG_PATH`, XDG directories,
and `HERDR_SOCKET_PATH` accepted a valid candidate configuration.
`herdr server reload-config` reported applied with no diagnostics and
`restart_needed: false`; restoring a valid configuration also succeeded.

Unknown fields are silently accepted by this runtime. Reload is therefore not
an exhaustive schema validator. The renderer emits the documented allow-list
only, and later activation work must preserve this limitation.

## Herdr 0.8.2 source-derived profile

This profile is derived from public upstream source, not from runtime observation.
The official `v0.8.2` tag object
`34ba52cc6ff3b723e6fc0130485ec24582dbe205` peels to commit
`9eb521456ac0d19d3ab3d9d7cea3cca10baa8a4c` in
[herdrdev/herdr](https://github.com/herdrdev/herdr).

The profile uses `src/config/theme.rs` as its identity source. Its authoritative
bytes hash to SHA-256
`9d7bdfdb391d12112e7d4eb1bd3895e50bdb6556255ef75e634094a969684e2d`.
That source declares `catppuccin-latte` as the canonical light base, applies
`[theme.custom]` after the base, and accepts `#RRGGBB`. It also declares
`sidebar_bg`, `active_row_bg`, and `selection_bg`. Dreamcoder maps those fields
to `bg`, `surface0`, and `selection`, respectively.

The source-derived procedural evidence is bounded to these upstream files at the
same commit:

| Source | SHA-256 | Established behavior |
| --- | --- | --- |
| `src/config/io.rs` | `21fcd99c826f2c54da45a826ffd04119746dfffe6b8c0d8fddc8c2b321fd49e4` | XDG config resolution, missing-file defaults, and parse-failure diagnostics |
| `src/session.rs` | `3e00d617307466271bb12c4deb9dc94175a8c7e112f3b444d4566ad7991aa38e` | Explicit session selection and socket precedence |
| `src/cli/server.rs` | `aeaf6a7746d20f21d3ce856c6bf78684786bd75d5087c1340d2240422285a1eb` | `server reload-config` request and JSON output |
| `src/cli/server_not_running.rs` | `9c3e74052f49407008e7c5ce92745a01d48db1eed1381efbfa0125b11a53c983` | `server_not_running` error code |
| `src/app/mod.rs` | `3e9b89b55e576f9d49be02f55058144ffbec56f69f0879c7bbcc4706d8ebf9ab` | `applied`, `partial`, and `failed` reload outcomes; failed parsing keeps current config |
| `src/ui/sidebar.rs` | `152f9357b85cbcf5cdb070f3e9c7a18dcb0a5a25f4070bab9ac07954ff711c8f` | Sidebar fill and active/selection row token use |

No live Herdr command was executed to establish this profile. In particular,
this evidence does not claim that a server was running or that reload was
observed locally.

## Herdr 0.9.0 installed-runtime profile

`herdr-0.9.0` is bound to local `herdr 0.9.0`, binary SHA-256
`4fa1a01158dd8043da92d31b270780b0dcc10603038d9b61cac4d81ab63fb71f` at
`~/.cargo/bin/herdr`, observed directly (not source-derived) via
`herdr --default-config`, which the binary itself prints as its complete,
authoritative default configuration reference.

This is a materially different schema from the 0.7.3 profile this
repository's activation validator (`herdr_activation._CANONICAL_UI`,
`_CANONICAL_KEYS`, `_HERDR_VERSION`) currently pins to:

- **`[keys]`** grew from 4 required agent-navigation bindings to dozens of
  prefix-mode action bindings (`help`, `settings`, `detach`,
  `reload_config`, `workspace_picker`, `goto`, `new_workspace`,
  `new_worktree`, tab/pane focus and resize actions, `[[keys.command]]`
  custom commands, `[keys.indexed]`, and more). The default `prefix`
  changed from `"ctrl+a"` (0.7.3 canonical) to `"ctrl+b"`. The three
  0.7.3-canonical agent-nav keys (`previous_agent`, `next_agent`,
  `focus_agent`) still exist by name but now default to `""` (unset)
  rather than to a bound value.
- **`[ui]`** grew from a single `accent` key to a large settings surface
  (`sidebar_width`, `pane_borders`, `tab_bar_right`, `window_title`,
  `agent_panel_sort`, `status_indicators`, nested `[ui.sidebar.agents]`,
  `[ui.sidebar.spaces]`, `[ui.toast]`, `[ui.toast.herdr]`,
  `[ui.toast.clipboard]`, `[ui.sound]`, `[ui.sound.agents]`, and more).
  The default `accent` is the named color `"cyan"`, not a hex value.
- **`[theme.custom]`** field names shifted from 0.7.3's
  (`accent, panel_bg, surface0, surface1, surface_dim, overlay0, overlay1,
  text, subtext0, mauve, green, yellow, red, blue, teal, peach`) to
  `sidebar_bg`, `active_row_bg`, `selection_bg`, `panel_bg`, `accent`, and
  per-channel colors — matching, not contradicting, the 0.8.2
  source-derived profile's field names above. Layered
  `[theme.custom.light]` / `[theme.custom.dark]` sub-tables are new and
  apply only when `auto_switch = true`.
- **`[theme]`** documents eleven built-in base themes (`catppuccin,
  terminal, tokyo-night, dracula, nord, gruvbox, one-dark, solarized,
  kanagawa, rose-pine, vesper`) versus 0.7.3's narrower set.
- A real, documented `onboarding` top-level key exists (`# onboarding =
  true`, commented default). The checked-in `DreamcoderHerdr/.../0.8.2/
  config.dark.toml` previously carried an `onboarding = false` line that
  a since-run `./scripts/dreamcoder sync` silently regenerated away
  during this same session (Dreamcoder's renderer does not emit this
  field). Whether that line was itself valid evidence-backed content or
  accidental drift could not be determined after the fact; flagging here
  rather than asserting either way.

**Not yet gathered**: the official `v0.9.0` source tag/commit reference
(no embedded git SHA found via `strings` on the release binary in a quick
pass) and an isolated `HERDR_CONFIG_PATH`/reload validation cycle
specific to 0.9.0's schema (only informal evidence exists: this
session's live `herdr server reload-config` against the running 0.8.2→
0.9.0 server returned `"status": "applied"` for an 0.8.2-shaped
`[theme.custom]` payload, which is consistent with, but does not prove,
0.9.0 still accepting that older field set).

**Implication for `herdr_activation.py`**: `_validate_source`'s exact
dict-equality check against a single global `_CANONICAL_UI`/
`_CANONICAL_KEYS`, and `_herdr_version_matches`'s exact-string pin to
`"herdr 0.7.3"`, cannot be extended to 0.9.0 by adding one more constant
— the schema itself restructured (new nested tables, changed defaults,
renamed/added fields), and this repository observed the installed
version advance 0.8.2 → 0.9.0 within a single working session. Deciding
how activation should validate against a moving, restructuring upstream
schema (per-version canonical constants forever, a narrower allow-list
check, or dropping strict equality in favor of the "unknown fields are
silently accepted" behavior already documented above for 0.7.3) is a
design decision, not a patch, and is left open here rather than decided
unilaterally.

## Herdr 0.9.1 installed-binary profile

`herdr-0.9.1` is bound to local `herdr 0.9.1` (installed by `herdr update`
from 0.9.0), binary SHA-256
`2a02fed16beb651ef006e1d43f048f652ca4dc58ad053cd2d44450563d5c54b7` at
`~/.cargo/bin/herdr`. Unlike the 0.9.0 note above, 0.9.1's
`herdr config check` rejects unknown keys (`unknown config key
theme.custom.<name>; ignoring key`) and unknown theme names with a non-zero
exit, which closes the open question of whether the 0.8.2 field set is still
accepted: each generated `0.9.1/config.{dark,light}.toml` passed
`HERDR_CONFIG_PATH=<variant> herdr config check` with `config: ok`. The profile
therefore reuses the 0.8.2 theme, custom, and ui field sets exactly and adds no
new fields.

Observed default-config deltas (`herdr --default-config`, 374 lines, SHA-256
`a62a4a2fc4746dd392976916d3333b89598cc30407819de9544cc8f4b4502fa8`):
`[ui] pane_scrollbars` defaults to `true`, `[ui] accent` to `"cyan"`,
`[keys] prefix` to `"ctrl+b"`, and the agent navigation keys are unset. The
Dreamcoder variant sets all of them explicitly, so those defaults do not leak
into it. Reload remains `herdr server reload-config`; no live reload was
observed for this profile (server not running at capture time). A version
between two profiles (for example 0.9.0) fails closed; only versions newer than
the newest profile fall back to it.

## Fail-closed boundary

Unknown or malformed version output remains `unsupported-contract`; an absent
executable remains `skipped-not-installed`. Repository generation does not read,
select, or mutate user-owned configuration.
