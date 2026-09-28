# Herdr Integration

← Back to [docs/README.md](README.md)

> Version-bound Herdr compatibility contracts, repository-owned generated
> variants, and deployment profile settings. Live configuration is never part of
> this repository.

## Onboarding a new Herdr version

- [ ] Detect the installed binary version (`herdr --version`) and its exact config path
- [ ] Capture evidence: binary identity, `herdr config check`, reload command, config path (see the contract table)
- [ ] Generate the versioned variant(s) under `DreamcoderHerdr/.config/herdr/dreamcoder/` from the canonical `tokens.json`
- [ ] Verify repo sync: `python3 scripts/verify-repo-sync.py`

## Supported runtime contracts

Herdr integration is gated by complete, version-bound evidence. A profile is
usable only when every asserted behavior is present and unambiguous. Detection
matches the exact installed version; an absent, upgraded, downgraded, or
incompletely profiled binary fails closed without modifying any Herdr
configuration.

| Profile | Version | Validation | Reload | Config path | Notes |
| --- | --- | --- | --- | --- | --- |
| `herdr-0.7.3` | 0.7.3 | `herdr config check` | `herdr server reload-config` | `~/.config/herdr/config.toml` | Pre-existing supported profile |
| `herdr-0.8.0` | 0.8.0 | `herdr config check` | `herdr server reload-config` | `~/.config/herdr/config.toml` (overridable by `HERDR_CONFIG_PATH`) | Installed-binary evidence |
| `herdr-0.8.2` | 0.8.2 | Source-derived | `herdr server reload-config` | XDG config path (overridable by `HERDR_CONFIG_PATH`) | Public upstream source; no local runtime observation |
| `herdr-0.9.1` | 0.9.1 | `herdr config check` | `herdr server reload-config` | `~/.config/herdr/config.toml` (overridable by `HERDR_CONFIG_PATH`) | Installed-binary evidence |

### Herdr 0.8.0 installed-binary evidence

Observed exactly from the installed executable, with nothing beyond it asserted:

- Executable: `herdr`, version `0.8.0`
- Binary SHA-256:
  `b872ea7e40fa2cb17e857ac9b62b1bf26db7b403c622f5d2f3f5b35f6e9acd28`
- Default config confirms `[ui] pane_scrollbars = false`
- Config validation: `herdr config check`
- Reload command: `herdr server reload-config`
- Config path: `~/.config/herdr/config.toml`, overridable via `HERDR_CONFIG_PATH`

The 0.8.0 variant reuses the previously evidenced theme and keys structure and
adds only the observed 0.8.0 deltas: `[ui] pane_scrollbars = false` and the
binary identity above.

### Herdr 0.8.2 source-derived evidence

The `herdr-0.8.2` profile is grounded in the official `v0.8.2` source at commit
`9eb521456ac0d19d3ab3d9d7cea3cca10baa8a4c`; it is not a claim about an
observed local runtime. The source establishes `catppuccin-latte` as the light
base and the custom `sidebar_bg`, `active_row_bg`, and `selection_bg` tokens.
See the complete hashes and procedural boundaries in
[`herdr-contract-evidence.md`](../src/dreamcoder_theme/herdr-contract-evidence.md).

### Herdr 0.9.1 installed-binary evidence

Observed from the executable installed by `herdr update` (0.9.0 → 0.9.1):

- Executable: `~/.cargo/bin/herdr`, version `0.9.1`
- Binary SHA-256:
  `2a02fed16beb651ef006e1d43f048f652ca4dc58ad053cd2d44450563d5c54b7`
- Config validation: `herdr config check`. In 0.9.1 it is strict: unknown keys
  (`theme.custom.*`, `ui.*`) and unknown theme names are reported as issues and
  exit non-zero, so a passing check proves every emitted field is recognized.
- Reload command: `herdr server reload-config`
- Config path: `~/.config/herdr/config.toml`, overridable via `HERDR_CONFIG_PATH`
- Default-config deltas relevant to the Dreamcoder variant (`herdr --default-config`):
  `[ui] pane_scrollbars` now defaults to `true` (the variant keeps `false`);
  `[ui] accent` defaults to the named color `"cyan"` (the variant pins a hex);
  `[keys] prefix` defaults to `"ctrl+b"` and `previous_agent` / `next_agent` /
  `focus_agent` are unset by default (the variant keeps `ctrl+a` and its agent
  bindings); `catppuccin-latte` is a valid built-in theme name.

The 0.9.1 variants carry the same field set as 0.8.2 (catppuccin base,
`catppuccin-latte` for Light, sidebar/active-row/selection tokens). Each
generated variant passed `HERDR_CONFIG_PATH=<variant> herdr config check`. A
live reload was not observed (the server was not running when captured).

## Generated repository variants

Versioned variants are generated from the Dreamcoder Workbench canonical tokens
(`DreamcoderThemes/dreamcoder/tokens.json`) by the theme sync and checked in so
drift is detectable:

```text
DreamcoderHerdr/.config/herdr/dreamcoder/
  0.7.3/config.dark.toml
  0.7.3/config.light.toml
  0.8.0/config.dark.toml
  0.8.0/config.light.toml
  0.8.2/config.dark.toml
  0.8.2/config.light.toml
  0.9.1/config.dark.toml
  0.9.1/config.light.toml
```

- Each variant carries the header `# Managed by Dreamcoder; repository variant only.`
- Light renders Dreamcoder Light; dark renders Dreamcoder dark.
- The 0.8.0 variants include `pane_scrollbars = false`.
- The 0.8.2 and 0.9.1 Light variants use `catppuccin-latte`; all 0.8.2 and
  0.9.1 variants explicitly map sidebar, active-row, and navigation-selection
  backgrounds.
- Active/live configuration (`~/.config/herdr/config.toml`, or whatever
  `HERDR_CONFIG_PATH` points to) stays out of git. The repository only ever
  ships static, versioned variants.

## Deployment profiles

`DreamcoderProfiles/deploy/` holds repository-safe deployment profiles:

- `desktop-arch.json` — desktop Arch Linux deployment; supports the full
  light/dark schedule via systemd timers. Herdr `[ui] pane_scrollbars` follows the
  Herdr default (`false`).
- `mobile-termux.json` — mobile Termux/Moshi deployment; selects Dreamcoder
  Light and disables Herdr pane scrollbars for narrow screens. It contains
  rendering settings only — never a device address, username, key, or host
  runtime state.

## Verification

```bash
python3 scripts/verify-repo-sync.py
```

This checks that every generated variant matches the renderer byte-for-byte,
that deployment profiles validate against their schema, that the mobile profile
selects Light with pane scrollbars disabled, that the source manifest is
present, and that no sensitive material exists in the synchronization surface.
When `herdr` is installed, the verifier additionally runs `herdr config check`
against a temporary copy of the light variant for the installed version (the
0.8.0 variant when that version has no profile) using `HERDR_CONFIG_PATH`
(never the live configuration). When `herdr` is absent, that step is skipped
safely.

## Live switching

`scripts/herdr-theme-switch.sh` detects the installed Herdr version, selects
the matching generated dark or light variant, and requests a live config
reload. It resolves the selector from `HERDR_CONFIG_PATH` first, then
`XDG_CONFIG_HOME`, then `~/.config/herdr/config.toml`.

The switcher deploys the selected variant as `config.<mode>.toml` next to the
selector and points `config.toml` at it, so Herdr's own writes never touch the
checked-in repository variants. Top-level scalar keys already present in the
deployed copy (for example `onboarding`) are preserved across switches.

When the installed version is newer than every complete checked-in profile, the
switcher uses the newest generated variant as a compatibility fallback, but only
after `herdr config check` (with `HERDR_CONFIG_PATH` pointed at that variant)
accepts it. An older or unrecognised version leaves the selector unchanged.

The switcher only manages absent selectors or existing symlinks. It refuses to
replace a regular `config.toml`, because that file may contain personalized
settings. To opt in, preserve that file elsewhere and explicitly replace it with
a symlink before switching. An unsupported or missing executable also leaves the
selector unchanged and makes activation fail rather than claiming success.

A typed `server_not_running` response means the generated variant was selected
and reload is deferred until Herdr starts. Only an `applied` result counts as a
completed live reload. `partial`, `failed`, malformed responses, and other errors
restore the previous selector and fail the enclosing Dreamcoder transaction.

## Development workflow scripts

Repository-owned helpers for a Herdr-based engineering flow. They operate on a
running Herdr server (start one with `herdr`); they never touch live
configuration.

- `scripts/herdr-workspace-dev.sh [PROJECT_DIR] [LABEL]` — creates a workspace
  for a project with three full-screen tabs: `pi` hosting the main agent, `git`
  running `lazygit`, and a plain `shell`. Defaults to the current directory and
  its basename. The root tab is renamed to `pi`, its shell is awaited before the
  agent starts, then the `git` and `shell` tabs are created with
  `herdr tab create` and awaited; `lazygit` runs only after the `git` tab's
  shell is ready. No panes are split.
- `scripts/herdr-review.sh [KIND] [TARGET] [PROJECT_DIR]` — splits the focused
  pane, starts a `reviewer` agent of `KIND` (`pi` by default; any kind Herdr
  supports, e.g. `codex`, `opencode`), prompts it to review the `TARGET` diff
  (`HEAD` by default), waits for it to settle, and prints the review.

Both scripts fail fast with a clear message when `herdr` or `jq` is missing or
when the project directory does not exist. They parse CLI JSON responses with
`jq` and capture pane, tab, and workspace IDs from the responses rather than
predicting them. Shared helpers live in `scripts/herdr-lib.sh`;
`herdr_wait_shell` polls a fresh pane until its shell renders the prompt
(terminal title set) before any command is sent, and `herdr_start_agent` then
starts the agent with a bounded retry, so a busy pane never leaves a lost
`lazygit` launch, an orphaned agent, or a spurious
`agent_pane_busy`/startup-timeout failure. Covered by
`shell-tests/test_herdr_workspace.bats`
and `shell-tests/test_herdr_review.bats`, which drive a fake `herdr` CLI
(including a retry scenario); run them with `bats shell-tests/test_herdr_*.bats`.
