# Herdr Theme Activation Specification

## Purpose

Define the narrowly bounded managed activation of exactly Herdr 0.7.3 with Dreamcoder Light and Dreamcoder Dark configurations. The operation MUST fail closed before mutation whenever its runtime, path, source, backup, write, or recovery contract cannot be established safely.

## Requirements

### Requirement: Exact supported runtime

Managed activation MUST support exactly `herdr 0.7.3`. Any other, absent, malformed, or unverifiable version MUST fail before backup or mutation.

#### Scenario: Version gate fails closed

- GIVEN Herdr is unavailable or `herdr --version` does not return exactly `herdr 0.7.3`
- WHEN managed activation is requested
- THEN activation MUST fail before creating a backup or mutating any target
- AND the existing active configuration MUST remain unchanged

### Requirement: Environment-derived active target

The system MUST resolve the active configuration from `HERDR_CONFIG_PATH` when it is set. Otherwise, it MUST derive the standard Herdr configuration path from the XDG configuration home, using the XDG default based on `HOME` when `XDG_CONFIG_HOME` is unset. The implementation MUST NOT contain a hardcoded user-specific path.

#### Scenario: Override and fallback resolution

- GIVEN `HERDR_CONFIG_PATH` is set to a valid safe target
- WHEN activation resolves its target
- THEN that override MUST be selected
- GIVEN `HERDR_CONFIG_PATH` is unset and XDG variables are valid
- WHEN activation resolves its target
- THEN the XDG-derived Herdr target MUST be selected
- AND no user-specific absolute path MUST be introduced

#### Scenario: Unsafe target resolution

- GIVEN the override or derived path is empty, invalid, ambiguous, or unsafe
- WHEN activation resolves its target
- THEN activation MUST fail before backup or mutation

### Requirement: Complete bounded variants

The system MUST produce exactly two managed variants: Dreamcoder Light and Dreamcoder Dark. The variants MUST preserve canonical upstream `[ui]` and `[keys]` values exactly, except that Dreamcoder Light MUST set `[ui].accent` to the palette `accent`: upstream's `#6FA0AF` reaches only about 2.6:1 on the Light background. Dreamcoder palette ownership MUST be limited to `[theme]`, `[theme.custom]` and that one Light `[ui].accent` field; no other sections MAY be palette-driven.

#### Scenario: Light and Dark preserve canonical non-theme values

- GIVEN the canonical upstream Herdr configuration
- WHEN Dreamcoder Light and Dreamcoder Dark variants are generated
- THEN Dreamcoder Dark MUST contain the canonical `[ui]` values exactly, including `accent = "#6FA0AF"`
- AND Dreamcoder Light MUST contain the canonical `[ui]` values except `accent`, which MUST equal the Light palette `accent`
- AND both variants MUST contain the canonical `[keys]` values exactly: `prefix = "ctrl+a"`, `previous_agent = "prefix+alt+k"`, `next_agent = "prefix+alt+j"`, and `focus_agent = "prefix+ctrl+1..9"`
- AND palette differences MUST occur only in `[theme]`, `[theme.custom]` and the Light `[ui].accent`
- AND no third variant MAY be produced

### Requirement: Backup-before-mutation and atomic replacement

For an existing active configuration, activation MUST create and successfully retain a distinct backup before any mutation. The selected complete variant MUST be prepared before the resolved target is atomically replaced. A backup failure or write failure MUST leave the prior active configuration unchanged whenever possible.

#### Scenario: Existing target is safely replaced

- GIVEN a valid existing active configuration and a selected Light or Dark variant
- WHEN activation proceeds
- THEN the existing file MUST be backed up successfully before replacement
- AND the target MUST be atomically replaced with the complete selected variant
- AND the retained backup MUST preserve the prior user-owned configuration

#### Scenario: Absent target is created safely

- GIVEN no active configuration exists
- WHEN activation proceeds with a valid selected variant
- THEN the system MAY create the target atomically
- AND it MUST NOT claim that existing user data was backed up
- AND if activation fails, it MUST remove only the newly created target when safe

#### Scenario: Backup or write failure

- GIVEN backup creation or atomic replacement fails
- WHEN activation attempts the operation
- THEN activation MUST return a failure identifying the failed stage
- AND it MUST NOT report success
- AND the prior target MUST remain unchanged or be restored from the backup

### Requirement: Documented reload and truthful recovery

After a successful replacement, the system MUST use only the documented `herdr server reload-config` command, and only when reload is applicable to the invocation and runtime context. Reload MUST NOT be attempted before replacement. A failed attempted reload MUST trigger restoration of the prior active configuration; restoration failure MUST be surfaced explicitly.

#### Scenario: Applicable reload succeeds

- GIVEN the target was replaced successfully and reload is applicable
- WHEN activation invokes reload
- THEN it MUST invoke only `herdr server reload-config`
- AND activation MUST report success only when the reload succeeds

#### Scenario: Reload is not applicable

- GIVEN the target was replaced successfully but reload is not applicable
- WHEN activation completes
- THEN it MUST report the file update without claiming a live reload
- AND it MUST NOT infer undocumented server or process semantics

#### Scenario: Reload failure restores prior state

- GIVEN replacement succeeded and an attempted documented reload fails
- WHEN activation handles the failure
- THEN it MUST restore the prior active configuration atomically from the retained backup where possible
- AND it MUST report the reload failure and restoration result
- AND a restoration failure MUST produce an explicit failed outcome with the backup location

### Requirement: Bounded failure safety and non-goals

The operation MUST fail closed for malformed or unsafe active targets, unsupported modes, backup failures, write failures, reload failures, and restore failures. It MUST modify only the resolved Herdr target and directly associated transaction backup or temporary file.

#### Scenario: Unsafe active configuration is rejected

- GIVEN the active target is malformed, unsafe, or cannot be safely read or replaced
- WHEN managed activation is requested
- THEN activation MUST stop without collateral changes
- AND it MUST report the failed safety stage and actionable recovery information

#### Scenario: Scope remains bounded

- GIVEN managed Herdr activation runs
- WHEN it generates or activates a variant
- THEN it MUST NOT modify Hyprland, Ghostty, other targets, palette token definitions, Fish or shell auto-switching, or unrelated user configuration
- AND it MUST NOT introduce a user configuration migration or merge framework
- AND it MUST NOT claim unproven server, process, scheduling, or reload semantics
