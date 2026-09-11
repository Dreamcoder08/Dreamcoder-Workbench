# Renderer Registry Specification

## Purpose

`renderer_registry.py`'s 33 `REGISTRATIONS` MUST accurately describe
`sync.py`'s real per-consumer active/repository/mutation behavior. It stays
validation-only, never wired into the live sync path — a mismatch is a bug
in the registration, never a license to change `sync.py`.

## Requirements

### Requirement: codex_app declares its real renderer

The `codex_app` registration in `renderers_codex.py` MUST set
`renderer=opencode_content`, matching `sync.py`'s `VARIANT_REGISTRY` row for
`DreamcoderCodexApp` and `render_coverage_plan()`'s
`"codex_app": opencode_content(...)` — not `codex_tmtheme_content`.
`output_kind` stays `"active-and-repository"` with
`ActiveStrategy.RESOLVED_ACTIVE_PATH` / `RepositoryStrategy.MODE_VARIANTS`.

#### Scenario: codex_app renderer matches sync.py's real generator

- GIVEN the registration where `consumer_id == "codex_app"`
- WHEN a test compares `reg.renderer` to `sync.opencode_content`
- THEN they are the same function object, and not `codex_tmtheme_content`

### Requirement: antigravity declares a pinned-active strategy

`antigravity` MUST represent that `sync.py` always writes
`DreamcoderAntigravity/Dreamcoder.json` from `variants["dark"]`, never the
live active mode. If no existing `ActiveStrategy` member expresses
"active output pinned to a fixed variant," add exactly one new member in
`renderer_contract.py` and apply it to every registration with this same
pinned-active behavior, not only `antigravity`.

#### Scenario: antigravity active strategy is not live-mode-resolved

- GIVEN the `antigravity` registration
- WHEN a test reads `reg.sync.active`
- THEN it is not `ActiveStrategy.RESOLVED_ACTIVE_PATH` unless that value is
  proven to already model pinned-mode semantics

### Requirement: symlink-safe consumers use the matching MutationStrategy

Every registration whose repository-tracked active-mirror write in
`sync.py`'s `sync_repo_snippets()` routes through `write_active_repo_file()`
(unlink-stale-symlink guard) MUST NOT declare
`MutationStrategy.WRITE_IF_CHANGED`. If no existing member represents this
guard, add exactly one new `MutationStrategy` member and apply it to exactly
the 21 consumers whose repo active-mirror write is confirmed against live
`sync.py` call sites — `antigravity`, `codex_app`, `codex_theme`,
`bat_theme`, `pi_theme`, `kitty_ui`, `opencode` (the `.opencode` dotfile),
`hyprland`, `waybar`, `rofi`, `zsh_syntax`, `ls_colors`, `fzf`, `bat`,
`delta`, `btop`, `dunst`, `cava`, `firefox`, `obsidian`, `lazygit` — not only
the one that surfaced the bug. Consumers whose only `sync.py` write is a bare
`write_if_changed()` on a live path or a pure `write_variant_files()` call
(`kitty`, `tmux`, `starship`, `nvim`) MUST keep `WRITE_IF_CHANGED`.
`zellij`, `ghostty`, and `warp` keep `PROFILE_AWARE_SELECTOR`; that value
describes the live selector patch, a separate dimension from the repo
active-mirror mutation strategy (documented accepted model gap).

#### Scenario: every write_active_repo_file consumer avoids WRITE_IF_CHANGED

- GIVEN the `consumer_id`s confirmed to route through `write_active_repo_file()`
- WHEN a test reads each matching registration's `reg.sync.mutation`
- THEN none equal `MutationStrategy.WRITE_IF_CHANGED`

#### Scenario: bare write_if_changed consumers are unaffected

- GIVEN a `consumer_id` whose `sync.py` call site is a bare `write_if_changed()`
  with no repository mirror
- WHEN a test reads that registration's `reg.sync.mutation`
- THEN it still equals `MutationStrategy.WRITE_IF_CHANGED`

### Requirement: hypr_colors_lua/conf declare active output plus repository variants

`hypr_colors_lua` and `hypr_colors_conf` MUST declare
`output_kind="active-and-repository"`,
`ActiveStrategy.RESOLVED_ACTIVE_PATH`, `RepositoryStrategy.MODE_VARIANTS`, and
`MutationStrategy.WRITE_IF_CHANGED` — matching all of live `sync.py`, not only
`sync_repo_snippets()`. `sync_repo_snippets()` calls `write_variant_files()`
for both (never `write_active_repo_file()`), while `sync_active_targets()`
writes the live active file (`~/.config/hypr/colors.lua` / `colors.conf`)
through a bare `write_if_changed()` on every sync. A repository-only
registration would falsely assert that no active output exists.

#### Scenario: hypr_colors_lua/conf declare active output and repository variants

- GIVEN the `hypr_colors_lua` and `hypr_colors_conf` registrations
- WHEN a test reads `reg.output_kind`, `reg.sync.active`, `reg.sync.repository`, and `reg.sync.mutation`
- THEN `output_kind == "active-and-repository"`, `active == RESOLVED_ACTIVE_PATH`, `repository == MODE_VARIANTS`, and `mutation == WRITE_IF_CHANGED`

### Requirement: zellij registration matches an explicit generation decision

The `zellij` registration's `RepositoryStrategy.MODE_VARIANTS` claim MUST be
resolved against one design-recorded decision: either (a) correct the claim
to match that only Night is generated today (orphaned `.kdl` status
documented as a follow-up, never silently deleted), or (b) wire real
dark/light `.kdl` generation so the existing claim becomes true.

#### Scenario: zellij registration matches real generated variants

- GIVEN the recorded design decision
- WHEN a test compares the `zellij` registration's `RepositoryStrategy` to
  the `.kdl` variant files `sync.py` actually writes
- THEN the declaration matches exactly (no claimed-but-unwritten variant,
  no written-but-unclaimed variant)

#### Scenario: orphaned .kdl files are never deleted without confirmation

- GIVEN dark/light `.kdl` files found orphaned
- WHEN the decision selects "correct the registry's claim"
- THEN they are documented as a follow-up risk and no deletion occurs here

### Requirement: herdr registration represents all 3 supported profiles

The `herdr` registration(s) MUST represent that
`sync_herdr_repo_variants()` writes dark/light(+night) variants for every
`is_complete` profile in `SUPPORTED_PROFILES` (`herdr-0.7.3`, `-0.8.0`,
`-0.8.2`), each under its own versioned directory. A single hardcoded
profile/mode entry MUST NOT stand in for this fan-out.

#### Scenario: herdr registration covers every supported profile

- GIVEN `herdr_contract.SUPPORTED_PROFILES` (3 complete profiles)
- WHEN a test reads the `herdr` consumer's registration(s)
- THEN all 3 profile versions are represented, not one fixed profile/mode

### Requirement: all corrected registrations remain valid under validate_registry()

Every fix (new enum variants, edited fields) MUST keep
`validate_registry(REGISTRATIONS)` returning an empty list, satisfied
through the existing checks (`_check_contract_version`, `_check_modes`,
`_check_ownership`, `_check_strategy_compatibility`, `_check_renderer`,
`_check_expected_ids`). A new enum variant MUST NOT be added without also
updating `_OWNERSHIP_RULES` and/or `_check_strategy_compatibility` when it
introduces a new ownership/strategy combination.

#### Scenario: full registry validates clean after all fixes

- GIVEN the fully corrected `REGISTRATIONS` tuple (33 consumers)
- WHEN `validate_registry()` runs with no arguments
- THEN it returns an empty list

#### Scenario: new enum variant is wired into ownership/strategy checks

- GIVEN any new enum member added by this change
- WHEN a registration using it is validated
- THEN `_check_ownership`/`_check_strategy_compatibility` evaluate it against
  explicit rules, not pass by matching no rule
