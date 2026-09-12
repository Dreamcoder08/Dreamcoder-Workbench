```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:72a2fa0c6824c9c5af558128a0cd056b62f60f75b6b71c5ab817e71a9e85abad
verdict: pass
blockers: 0
critical_findings: 0
requirements: 17/17
scenarios: 17/17
test_command: uv run pytest tests/ -v --tb=short
test_exit_code: 0
test_output_hash: sha256:656485676cd0ffc812fc5ea73b867d0d07e0c1cc74628804e9acf746e9dd018f
build_command: uv sync --all-extras
build_exit_code: 0
build_output_hash: sha256:4cb6e97bca26765e5fe271a29f2eca0c295e39e64ca98bab23828f34b3b9f36b
```

# Verification Report — fix-ml4w-keybindings-waybar

| Field | Value |
| --- | --- |
| **Change** | `fix-ml4w-keybindings-waybar` |
| **Mode** | Standard / repo-local (`actionContext.mode: repo-local`), interactive phase gate. **Strict TDD is NOT active.** |
| **Artifact store** | `openspec` (repo-local, authoritative) |
| **Date of this pass** | 2026-09-11 20:17 local (`2026-09-12T01:17:57Z`) |
| **Working tree** | `HEAD = 43fe2fea9546af071bedd6cac5cc5cab62ca111a`, dirty: `spec.md`, `tasks.md`, `openspec/config.yaml`, `pyproject.toml` (all intended, all covered by `evidence_revision`), plus an unrelated pre-existing `.pi/gentle-ai/sdd-preflight.json` |
| **Verdict** | **PASS** — 17/17 requirements, 17/17 scenarios, 0 blockers, 0 CRITICAL |
| **Files written this pass** | `openspec/changes/fix-ml4w-keybindings-waybar/verify-report.md` (the only tracked repo file). Command captures written under `/tmp/ml4wverify/` (outside the repo). |

This pass is a **fresh, full re-execution**. Every command below was run in this pass, every hash was computed this pass from the captured bytes on disk, and nothing was carried over from any earlier revision of this note. The previous report was inadmissible and is fully replaced; see `## Corrections to earlier revisions of this note`.

## evidence_revision — definition and reproduction

`evidence_revision = "sha256:" + sha256( newline-joined, sorted`git hash-object <path>`outputs for the fixed 25-file list below )`.

Notes that make the revision reproducible:

- `git hash-object <path>` hashes the **bytes on disk in the working tree** (not `HEAD`, not the index), so the revision covers the current uncommitted tree.
- The join is **newline-separated with no trailing newline**: the joined payload is exactly 1024 bytes (25 × 40 hex + 24 separators).
- `STATUS.md` and `verify-report.md` are **deliberately excluded**, because they are mutable status notes rather than verified surface. `STATUS.md` is rewritten by status bookkeeping and `verify-report.md` is the artifact this revision describes; hashing either would make the revision self-referential or unstable.
- `DreamcoderThemes/dreamcoder/waybar-night.css` is not in the list; the list is exactly the 25 paths specified for this change.

Python form (used to produce the revision):

```console
$ python3 /tmp/ml4wverify/evidence_revision.py
EVIDENCE_REVISION=sha256:72a2fa0c6824c9c5af558128a0cd056b62f60f75b6b71c5ab817e71a9e85abad
joined bytes: 1024 trailing newline: none
```

Shell form (independently reproduces the same digest — both were run this pass):

```console
$ printf '%s' "$(git hash-object <the 25 paths> | sort)" | sha256sum
72a2fa0c6824c9c5af558128a0cd056b62f60f75b6b71c5ab817e71a9e85abad  -
```

Blob-id list (sorted by blob id, i.e. in the exact order that is joined and hashed):

```text
0b6257e82576ce3095f9ee3e0c0340c30ed0eeab  src/dreamcoder_theme/renderers_hypr_waybar_rofi.py
2776479c52246c6072f34ab440599d891290024d  tests/ml4w/profile_validation.bats
428e770ae40dfae80f6ffa9fa3924c4c52c6c9be  DreamcoderThemes/dreamcoder/waybar-light.css
55cd7e1cc4c6e2ccfc4b1574317915778b215f5a  DreamcoderWaybar/.config/waybar/style.css
5bb18543449faf1ebd65f89ede7b6ffeff400803  tests/ml4w/generate_custom_lua.bats
69e9031cf3869ca8c25c528ebddfc30a3421fe65  src/dreamcoder_theme/sync.py
703e526f0bde66c19953dd8455e236893e0ccaea  ml4w_assets/hypr/conf/keybinding.lua
75c5b183ea5dbeeb8aaff49bd17ec7f986bd2940  scripts/setup-hyprland.sh
7ed6baa6df9664e770aa093707e7f668a0509f7c  DreamcoderProfiles/dreamcoder/default.json
7f5f353e22ebfb3fab870d005673e867e4e653f7  openspec/changes/fix-ml4w-keybindings-waybar/design.md
837f360967d31d65b26f0397f6b1c996325bf5af  DreamcoderProfiles/dreamcoder/asus-vivobook15.json
8b7155d2fcd659c31d6f0d3408835f3ff4343c0a  DreamcoderProfiles/dreamcoder/profile.schema.json
93abca65d3029d22e07d994ec7b6d9bdbbbeb911  pyproject.toml
95419cc5d3078344203a91219fa90fc6eed9fc2f  openspec/changes/fix-ml4w-keybindings-waybar/specs/ml4w-keybindings-waybar/spec.md
9ecdd8231bed18d3f529c2766cf75d341a7be90a  openspec/changes/fix-ml4w-keybindings-waybar/proposal.md
a0adfe97711c594ca2efc3cd7aed42495f94923b  ml4w_assets/hypr/conf/keybindings/dreamcoder.lua
aabc5885cd47660ea019261497a3b07f066d2e41  scripts/validate-ml4w-profiles.py
acedc9227bd58ee116cebb5ed3503ae15aa941e5  DreamcoderWaybar/.config/waybar/config.jsonc
c6141b362c2d838be092cbb0ae10cd1d58ea0e84  DreamcoderThemes/dreamcoder/waybar-dark.css
c6141b362c2d838be092cbb0ae10cd1d58ea0e84  DreamcoderThemes/dreamcoder/waybar.css
c6141b362c2d838be092cbb0ae10cd1d58ea0e84  DreamcoderThemes/waybar.css
dac7163e1df32a5678731f869cabaf4cf9459b52  openspec/changes/fix-ml4w-keybindings-waybar/tasks.md
e3db8ed9a1915350ce78d6018580550870b79618  scripts/generate-custom-lua.sh
f8bbc008eb097607e90256e79b6335467ca4f758  tests/ml4w/setup_hyprland.bats
fec3f4b1c02a6e7fb1bd701fbeb9bbf047fa34b2  README.md
```

### Hash method for command output

Every `*_output_hash` and every hash in the command table is:

```text
sha256:<hex>  where <hex> = sha256 of the captured output bytes on disk
               produced by: sha256sum "/tmp/ml4wverify/<name>.out"
```

Each capture was produced by redirecting stdout **and** stderr to one file:

```text
<exact command> > "/tmp/ml4wverify/<name>.out" 2>&1
```

## Envelope admissibility proof

The envelope above was written to a temp file (exact file at `/tmp/ml4wverify/envelope_fenced.md`) and validated:

```console
$ gentle-ai sdd-verify-validate --input /tmp/ml4wverify/envelope_fenced.md --requirements 17 --scenarios 17
{
  "valid": true,
  "verdict": "pass",
  "evidence_revision": "sha256:72a2fa0c6824c9c5af558128a0cd056b62f60f75b6b71c5ab817e71a9e85abad"
}
$ echo $?
0
```

The envelope contains **exactly the 13 admitted fields, in the admitted order**. `supersedes_evidence_revision`, `head` and `head_tree` — the three fields that caused the previous admission denial — are absent.

## Native status and actionContext findings

```console
gentle-ai sdd-status fix-ml4w-keybindings-waybar --json
```

| Field | Value from the authoritative engine |
| --- | --- |
| `nextRecommended` | `verify` **before** this write → **`archive`** after this write (re-read below) |
| `blockedReasons[0]` before this write | `"verification evidence is incomplete: unknown verify result field supersedes_evidence_revision"` |
| `blockedReasons[0]` after this write | `"native SDD runtime execution is blocked(maintainer_decision) for \"fix-ml4w-keybindings-waybar\" … this work unit's attempt or changed-line budget needs a maintainer decision …"` |
| `artifacts.applyProgress` | `missing` |
| `artifacts.proposal / specs / design / tasks / verifyReport` | `done` / `done` / `done` / `done` / `done` |
| `taskProgress` | `total: 6, completed: 6, pending: 0, allComplete: true` |
| `dependencies` | `proposal/specs/design/tasks/apply: all_done`, `verify: ready`, `archive: blocked` |
| `applyState` | `all_done` |
| `actionContext.mode` | `repo-local` |
| `actionContext.workspaceRoot` / `allowedEditRoots` | `/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots` (single root) |

Interpretation:

- **The admission blocker is cleared, and it was replaced by a runtime-budget gate.** Before this write, `blockedReasons[0]` was emitted because the *previous* `verify-report.md` carried the unknown field `supersedes_evidence_revision`. This report removes it, and the engine now reports `dependencies.verify: all_done`, `dependencies.archive: ready` and `nextRecommended: archive`. The new `blockedReasons[0]` is unrelated to verification quality: it is the bounded-attempt accounting (see "Bounded-attempt gate" below), because this replacement report measured **521 changed lines** against the objective's `max_changed_lines: 400`.
- **The new blocker is a maintainer decision gate, and it was left standing deliberately.** The attempt settled with `outcome: passed`, `evidence_revision: sha256:72a2fa0c…` and `changed_line_budget_exceeded: true`; the runtime now reports `decision_required: true`, `complete: false`, `next_action: "reset"`. Resetting is an explicit maintainer scope decision and is never automatic, so it was **not** performed here. The reset command, for the maintainer, is `gentle-ai sdd-attempt reset --cwd <repo> --change fix-ml4w-keybindings-waybar --expected-revision sha256:09b763eb7f8522ec47336b5ecad47bbd042bdab7d913f58871aa6a5c023bd214 --request-id "<unique>" --reason "<why>" --actor "<actor>"`. The overrun is an artifact of **rewriting** a 32.5 KB report in place (the whole file is replaced, so the diff counts the full document twice); it is not new implementation surface.
- **The native hard stops do not fire.** Active change selection is unambiguous; `tasks.md` is present and non-empty (9,899 bytes, `- [x] T1`…`T6`); `allowedEditRoots` is populated and every verified path resolves inside `workspaceRoot`; implementation ownership is proven by the two apply commits and by `git hash-object` over the 25 in-repo paths.
- `artifacts.applyProgress: missing` is accurate — `openspec/changes/fix-ml4w-keybindings-waybar/apply-progress.md` does not exist. Because `testing.strict_tdd: false` and `apply.tdd: false`, no `TDD Cycle Evidence` table is contractually required from it, and every fact it would have carried is independently re-proved below from primary evidence. Recorded as WARNING 7, not a blocker; it is **not** reconstructed retroactively, because a back-dated artifact would be unreviewable.

### Bounded-attempt gate

The change already had a running attempt (`work_unit: verify-fix-ml4w-conformance`, objective generation 3, `max_attempts: 1`, `max_changed_lines: 400`). That exact attempt was continued rather than duplicated:

```console
$ gentle-ai sdd-attempt acquire --cwd . --change fix-ml4w-keybindings-waybar \
    --request-id "verify-ml4w-2026-verifyspec-fresh" \
    --work-unit "verify-fix-ml4w-conformance" \
    --evidence-goal "Fresh verification of fix-ml4w-keybindings-waybar after spec conformance, tasks checkboxes, pyyaml dev extra and uv build command" \
    --max-attempts 1 --max-changed-lines 400 \
    --token sha256:37bcb7bd9449e9ad1b24999c4ac79cd08e4ecd3d6408918879c0b0b9f15f15a5
{"state":"proceed","token":"sha256:37bcb7bd9449e9ad1b24999c4ac79cd08e4ecd3d6408918879c0b0b9f15f15a5"}
```

State `proceed` authorised this launch; the token was retained and is settled with `--outcome passed` and this pass's `evidence_revision`.

## Commands executed this pass

Every command was run in this pass. Captures live under `/tmp/ml4wverify/`; hashes are `sha256` of those exact bytes.

| # | Command | Exit | Outcome and evidence hash |
| --- | --- | --- | --- |
| 1 | `uv sync --all-extras` — **declared `build_command`** | **0** | `Resolved 35 packages / Checked 33 packages` · `sha256:4cb6e97bca26765e5fe271a29f2eca0c295e39e64ca98bab23828f34b3b9f36b` (104 B) |
| 2 | `uv run pytest tests/ -v --tb=short` — **declared `test_command`** | **0** | `collected 680 items` → **`680 passed, 2 warnings in 11.75s`** · `sha256:656485676cd0ffc812fc5ea73b867d0d07e0c1cc74628804e9acf746e9dd018f` (12,727 B) |
| 3 | `python3 scripts/validate-ml4w-profiles.py --ci` | **0** | both profiles `✅ passes all checks`; `🎉 All profiles clean!` · `sha256:57954a00a580f10b60c08395907646a0e167d0e92e7552935c9fa84a26471d2a` |
| 4 | `bats tests/ml4w/` | **0** | `1..34`, **34/34 ok** (14 generator + 11 profile + 9 setup-hyprland) · `sha256:8f27f0bfb8f33dc3d1ea51b5255e0282e6457b89a4e451f192a8152f154476ea` |
| 5 | `uv run ruff check src/ tests/` | **0** | `All checks passed!` · `sha256:5b196eb3a6acb50d3fa398d04ca284985cc1ffec870e940264b00780bfd2c971` |
| 6 | `uv run ruff format --check src/ tests/` | **0** | `111 files already formatted` · `sha256:f4d501ad7405c927e0a57b16f24ccd530ee06a8c4da5838f861086d20077e073` |
| 7 | `uv run mypy src/` | **0** | `Success: no issues found in 56 source files` · `sha256:41d9395eddcf64a0d68a1116fdf97be7b7d59c76e5640f2814141b9efce880aa` |
| 8 | `uv run python scripts/verify-theme-health.py` | **0** | `✓ Dreamcoder theme health guardrails passed` · `sha256:3c7e2daebe1d283e4238be33a3693302681d5bdc2e0fce3640459e2bdbb21898` |
| 9 | `bash -n scripts/generate-custom-lua.sh` | **0** | no output · `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |
| 10 | `bash -n scripts/setup-hyprland.sh` | **0** | no output · `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |
| 11 | `bash scripts/generate-custom-lua.sh --dry-run` (**read-only form**) | **0** | `✓ Auto-detected profile: asus-vivobook15 (DMI: Vivobook_ASUSLaptop M1502IA_M1502IA / ASUSTeK COMPUTER INC.)` · `sha256:9de232925b091eda6fcfd88e2c283cd4e9229d40440c2c6d21e80306f9807ac4` |
| 12 | `bash scripts/generate-custom-lua.sh --validate` (**read-only form**) | **0** | `✓ Profile JSON valid — matches schema`; `✓ Profile validation complete: …/asus-vivobook15.json` · `sha256:81d3b0fe6fd1b05bb619be9ee046ad30b0c23d1906bf0564ae95c6dbbb4824fb` |
| 13 | `luac -p /tmp/ml4wverify/13_generated.lua` | **0** | Lua from the dry-run body parses clean: `70` × `^hl.bind(`, **0** × `hyprctl dispatch`, **0** × `hl.bindl`/`hl.mouse_bind` · `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |
| 14 | `shellcheck --shell=bash scripts/generate-custom-lua.sh scripts/setup-hyprland.sh` | **0** | clean · `sha256:e3b0c442…` (empty) |
| 15 | `shellcheck --shell=bash scripts/*.sh` — **pre-existing follow-up, NOT `test_command`** | **1** | 17 findings, **all SC1091 (info)**, 0 warning/error · `sha256:6841799b5eb6fc1f9e80b7bd0f4fe477b7acc317a309ea69e1d847630c6c0cba` |
| 16 | JSONC parse of `DreamcoderWaybar/.config/waybar/config.jsonc` after stripping `//` lines | **0** | 19 top-level keys; anchors + 20 `window-rewrite` entries · `sha256:98c39e0ea7c72a5085c5ffd2dae495726698b1ff7539ee80834687a31849ff95` |
| 17 | Profile audit (`/tmp/ml4wverify/profile_audit.py`) | **0** | counts, modifier sets, duplicates, every FR1.x chord matched by `(mods,key)` · `sha256:0f6c0c6f4ab09a09f50dc90bb78d3ada8668cf4b62d8187190f120bf848b8bb5` |
| 18 | `hyprctl binds -j` | **0** | 119 binds · `sha256:1c49f51b244a39063c61f4cb57e6e436b83cfbb9e7b32993be0ab216e761bfff` |
| 19 | `hyprctl configerrors` | **0** | empty (2 B: newline) · `sha256:75a11da44c802486bc6f65640aa48a730f0f684c5c07a42ba3cd1735eb3fb070` |
| 20 | binds audit over capture 18 (`/tmp/ml4wverify/21_binds_audit.out`) | **0** | 119 binds / 118 distinct `(modmask,key)` / 0 real collisions · `sha256:79a3675fa377c2dd0a131c95ee768a8cb58a14024451ff5ddd33e7ed673356dc` |
| 21 | Schema audit (`/tmp/ml4wverify/schema_audit.py`) | **0** | FR3.1 fields + jsonschema validation of both profiles · `sha256:a80b13c73b77fdd6a489826ea0bca626676116b0698137d1aef6820c556f9c51` |
| 22 | `hyprctl version` | **0** | `Hyprland 0.56.2 … commit efb50993780079460b0cbed1363e2166a2de1d9f` · `sha256:2dba729f80922f40bc608af996f15b2f2eb9a74e594ec96f62ba22963a6da698` |

Two footnotes on exactness:

- Command 15 is recorded as a **pre-existing follow-up**, exactly as the spec's `## Known Gaps` requires. It is **not** presented as a blocker and is **not** the declared `test_command`. All 17 findings are `SC1091 (info)` at dynamic `source` sites (e.g. `source "${DREAMCODER_DOTS_DIR}/lib/env.sh"`), on host files that this change does not touch.
- The declared `test_command` string is `uv run pytest tests/ -v --tb=short`, but the project's `pyproject.toml` sets `addopts = "-q"`, so pytest prints its quiet progress format rather than a per-test `PASSED` list. The command string, the exit code (0) and the count (`collected 680 items` → `680 passed`) are unaffected.

## Build & tests execution

| Gate | Command | Exit | Result |
| --- | --- | --- | --- |
| Build | `uv sync --all-extras` | 0 | 35 packages resolved, 33 checked |
| Test | `uv run pytest tests/ -v --tb=short` | 0 | **680 passed**, 2 warnings, `collected 680 items` |
| Perf/edges suite | `bats tests/ml4w/` | 0 | **34/34 ok** |
| Profile contract | `python3 scripts/validate-ml4w-profiles.py --ci` | 0 | `🎉 All profiles clean!` |
| Lint | `uv run ruff check src/ tests/` | 0 | `All checks passed!` |
| Format | `uv run ruff format --check src/ tests/` | 0 | 111 files already formatted |
| Types | `uv run mypy src/` | 0 | no issues in 56 source files |
| Theme health | `uv run python scripts/verify-theme-health.py` | 0 | guardrails passed |
| Shell syntax | `bash -n scripts/generate-custom-lua.sh` / `setup-hyprland.sh` | 0 / 0 | clean |
| Lua syntax | `luac -p` on generated output | 0 | clean |
| Live config | `hyprctl configerrors` | 0 | empty |

`pyyaml>=6` note: `pyproject.toml` gained `pyyaml>=6` in the `dev` extra in this pass's surface (blob `93abca65`). This is required because `tests/test_lazygit_renderer.py` imports `yaml`; without it the suite fails at **collection**, so `uv sync --all-extras` is not merely a convenience here — it is what makes the declared `test_command` exit 0.

## Completeness

| Metric | Value | Status |
| --- | --- | --- |
| Tasks total (`taskProgress.total`) | 6 | — |
| Tasks completed (`taskProgress.completed`) | **6** | ✅ 6/6 |
| Tasks pending | 0 | ✅ |
| `allComplete` | `true` | ✅ |
| Unchecked markers `^\s*- \[ \]` in `tasks.md` | **0** | ✅ none remain |
| Checked markers `^\s*- \[x\]` in `tasks.md` | 6 (`T1`…`T6`) | ✅ |
| Requirements in spec (`^### Requirement:`) | 17 | ✅ |
| Scenarios in spec (`^#### Scenario:`) | 17 | ✅ |

**Exact unchecked implementation task lines: NONE REMAIN.** `grep -n '^\s*- \[ \]' tasks.md` exits 1 with no matches, so the "do not return a clean PASS while unchecked implementation tasks remain" rule is not triggered, and there is no archive blocker from task completeness.

## Spec-compliance matrix — 17 requirements / 17 scenarios

Legend: ✅ compliant and evidenced this pass.

| # | Requirement | Matching scenario | Evidence at this revision | Result |
| --- | --- | --- | --- | --- |
| 1 | **FR1.1** Standard ML4W app launchers | the five app launchers resolve to their commands in both profiles | Both profiles, matched by `(["SUPER"],key)`: `RETURN→kitty`, `B→firefox`, `E→thunar`, `SPACE→rofi -show drun`, `V→cliphist list \| rofi -dmenu \| cliphist decode \| wl-copy` | ✅ |
| 2 | **FR1.2** Ctrl+Win secondary app shortcuts | Ctrl+Win shortcuts resolve to the shipped chords | `["SUPER","CTRL"] M→kitty btop`, `S→flatpak run com.ml4w.settings`, `C→~/.config/ml4w/settings/calculator.sh`; `["SUPER","CTRL","SHIFT"] K→kitty nvim` — in **both** profiles. No `CTRL+SUPER+K` chord exists | ✅ |
| 3 | **FR1.3** Window management bindings | window management keys are bound once in both profiles | Both profiles: `SUPER+Q→hyprctl dispatch killactive`, `SUPER+F→… fullscreen 1`, `SUPER+T→… togglefloating`, `SUPER+Y→… togglesplit`; 0 intra-profile duplicate chords (command 17) | ✅ |
| 4 | **FR1.4** Workspace navigation bindings | all twenty workspace bindings exist in both profiles | Both profiles: 10/10 switch chords (`SUPER+1`…`SUPER+0` → `… workspace 1..10`) and 10/10 move chords (`SUPER+SHIFT+1`…`0` → `… movetoworkspace 1..10`) | ✅ |
| 5 | **FR1.5** Window focus and move bindings | focus and move chords cover letters and arrows in both profiles | Both profiles: `SUPER+H/J/K/L → movefocus l/d/u/r`; `SUPER+SHIFT+H/J/K/L → movewindow l/d/u/r`; all four arrows present in both families (8 chords per family). `SUPER+L` is `movefocus r`, not a lock chord — as the spec now states | ✅ |
| 6 | **FR1.6** System control bindings | system control chords are bound in the profile that owns them | `default`: `SUPER+ALT+L→hyprlock` ✅, bare `PRINT→grimblast save area` ✅. Both profiles: `SUPER+SHIFT+S→grimblast save screen` ✅. `asus` deliberately omits `SUPER+ALT+L` and `PRINT` (see #7) | ✅ |
| 7 | **FR1.7** Binding coverage across both profiles | both profiles meet the binding contract and stay valid | `default` **56** = SUPER 27, SUPER+SHIFT 22, SUPER+CTRL 4, SUPER+CTRL+SHIFT 1, SUPER+ALT 1, bare 1. `asus` **70** = SUPER 29, SUPER+SHIFT 22, SUPER+CTRL 4, SUPER+CTRL+SHIFT 1, bare 14 — no SUPER+ALT, no bare `PRINT`, bare row is the XF86/Fn multimedia row. Both > 40. Preserved: `SUPER+SHIFT+D` theme toggle, `SUPER+SHIFT+U/I` blue light, brightness F4/F5, volume F1/F2/F3/F10, media F7/F8/F9, `code:237/238` keyboard backlight. Validator prints `All profiles clean!` and exits 0. 0 intra-profile duplicate chords | ✅ |
| 8 | **FR2.1** Waybar configuration template exists | the Waybar config template declares the three module anchors | `DreamcoderWaybar/.config/waybar/config.jsonc` exists (blob `acedc922`); stripped-JSON parse yields 19 top-level keys including `modules-left`, `modules-center`, `modules-right` | ✅ |
| 9 | **FR2.2** Waybar taskbar module renders workspace buttons with app icons | the taskbar module declares window-rewrite icon mappings | `hyprland/workspaces` declares a **20-entry** `window-rewrite` mapping plus `format-icons` with the workspace glyph set (`1`–`10`, `active`, `default`). `style.css` `#workspaces button.active` declares **only** `font-weight: 700` — exactly the delivered scope the requirement now states, and no accent is claimed | ✅ |
| 10 | **FR2.3** Waybar standard modules | standard modules occupy the documented anchors | `modules-left = ["hyprland/workspaces"]`, `modules-center = ["clock"]`, `modules-right = ["network","pulseaudio","cpu","memory","battery","tray"]`; a matching configuration block exists for every listed module | ✅ |
| 11 | **FR2.4** Waybar theme integration import | the layout stylesheet imports only the color bridge | `style.css` has **exactly one** `@import`, at line 8: `@import url("colors.css");`. Zero `@define-color`, zero color literals, zero accent variables in the file. `config.jsonc` declares modules/options only and carries no CSS import of its own. `colors.css` is the Dreamcoder bridge written by the engine (`sync.py:162-163`, `waybar_matugen_content` = variables only) | ✅ |
| 12 | **FR3.1** Profile schema compatibility | schema fields and modifier arrays cover every delivered binding | `profile.schema.json` binding item exposes `key`, `mods`, `command`, `description`, `bind_type`, `options` (+ `button`, `mouse`, `submap_entry`); `required = [command, description, key]`; `mods.items.enum = [SUPER, SHIFT, CTRL, ALT, CTRL_SHIFT, SUPER_SHIFT]` with `uniqueItems: true`. Both profiles `jsonschema.validate` cleanly; letter, digit, arrow and `F1`–`F12` keys all present. No schema extension was needed by this change beyond what it already declares | ✅ |
| 13 | **FR3.2** Profile validation and Lua generation | validation passes and generation selects the DMI-detected profile | `--ci` exits 0 with `All profiles clean!`; `bash -n` exits 0; generation auto-detects `asus-vivobook15` from DMI `Vivobook_ASUSLaptop M1502IA_M1502IA` / `ASUSTeK COMPUTER INC.`, reports **70 bindings**, and its Lua passes `luac -p` | ✅ |
| 14 | **FR4.1** No theme engine changes | no theme engine source file is touched | Change file set = profiles, schema, Waybar template pair, ML4W scripts/assets, `tests/ml4w/`, `README.md`, `tasks.md`, `scripts/validate-ml4w-profiles.py`. **No `src/dreamcoder_theme/` path appears in either apply commit** (`095d58a`: 5 files; `469d96a`: 12 files). `DreamcoderThemes/dreamcoder/waybar-{dark,light,night}.css` remain engine-generated (last touched by commits `a3e6561`/`5a2b7ba`, unrelated to this change) and unedited here. `scripts/apply-theme-mode.sh:106-112` still repoints `~/.config/waybar/colors.css` to `colors-${VARIANT}.css` before the sync, and `:157` calls `restart_waybar`. `verify-theme-health.py` exits 0 | ✅ |
| 15 | **NFR1** Binding commands are valid dispatchers or shell commands | generated Lua contains no hyprctl dispatch calls | Generated Lua: **70** `hl.bind(`, **0** `hyprctl dispatch`, **0** `hl.bindl`/`hl.mouse_bind`; the generator translates `workspace`/`movetoworkspace`/`killactive`/`fullscreen`/`togglefloating`/`togglesplit`/`movefocus`/`movewindow` into `hl.dsp.*`. `luac -p` exits 0, `hyprctl configerrors` is empty on Hyprland 0.56.2. Bats tests 12 and 13 assert the negative dispatcher and bare-Fn cases | ✅ |
| 16 | **NFR2** Waybar config parses as valid JSONC | comment-stripped config parses as JSON | Comment-stripped `config.jsonc` parses with `json.loads` (exit 0), no trailing commas, expected module keys readable | ✅ |
| 17 | **NFR4** Bindings do not conflict with ML4W built-in defaults | the live bind table has no real collisions | `hyprctl binds -j` → **119** binds, **118** distinct `(modmask, key)`, **0 real collisions**. The single repeated pair `(0, "")` is the two keyless keyboard-backlight entries `Brillo teclado +` (arg `167`) and `Brillo teclado -` (arg `169`), both `dispatcher __lua`, `locked=true` — distinct binds, not a collision, exactly as the requirement states. Single-source-of-truth model holds: the selector loads the curated `dreamcoder.lua` variant (`ml4w_assets/hypr/conf/keybinding.lua`, blob `703e526f`) so profile binds are not declared twice. Bats test 25 asserts no profile contains a duplicate key+mods combination (0 found) | ✅ |

**Summary: 17/17 requirements and 17/17 scenarios compliant. 0 failed, 0 partial. 0 blockers, 0 CRITICAL.**

## Known Gaps (not counted as requirements)

The spec records four gaps under its own `## Known Gaps` heading as **non-normative**: they describe behaviour that is **not delivered** or **not provable** from this repository, and the spec forbids counting them as satisfied requirements. They are listed here verbatim in substance so no reader mistakes them for delivered behaviour, and they are **NOT counted in the 17/17** above.

| Gap | Substance | Status in this pass |
| --- | --- | --- |
| **(a) Active-workspace accent not reachable through the shipped import chain** | `style.css` imports only `colors.css`, which declares variables and no accent rule; the `#workspaces button.active` accent rule lives in engine-generated `DreamcoderThemes/dreamcoder/waybar-{dark,light,night}.css`, which `style.css` does not import. Delivered behaviour is the module plus `window-rewrite` only. | **Re-confirmed.** `colors.css` is produced by `waybar_matugen_content` (`sync.py:162-163`, docstring: *"Only defines `@define-color` variables … No layout rules"*). Live `~/.config/waybar/colors.css`, `colors-light.css`, `colors-dark.css`, `colors-night.css` all report `grep -c 'button.active'` → **0**, while `DreamcoderThemes/dreamcoder/waybar-light.css:37-40` contains `color: @accent; background: rgba(130, 79, 22, 0.34);`. FR2.2's current text explicitly scopes the requirement away from the accent, which is why the requirement itself is ✅. |
| **(b) Waybar deliverables are dormant templates — original NFR3/NFR5 unprovable** | No repository script installs `DreamcoderWaybar/`, so "Waybar starts without errors using this config" (original NFR3) and "Dreamcoder Light colors visible in all Waybar modules" (original NFR5) are not provable from the repository. | **Re-confirmed.** `~/.config/waybar/` contains `colors*.css`, `modules.json`, `launch.sh`, `themeswitcher.sh`, `toggle.sh` — but **no `config.jsonc` and no `style.css`**. Repo scripts assert the live Waybar config is ML4W-managed. Waybar has no parse-only mode, so no launch was attempted. Original NFR3/NFR5 are **absent from the current spec's requirement set** and are therefore not part of 17/17. |
| **(c) `shellcheck` reports 17 info-level findings** | `shellcheck --shell=bash scripts/*.sh` exits 1; all 17 are `SC1091 (info)` for dynamic `source` paths shellcheck cannot follow; no warning- or error-level findings. Pre-existing and unrelated to this change. | **Re-measured and confirmed.** Capture #15: exit **1**, 17 `SC1091` findings. Two of the host scripts in the change's own surface (`generate-custom-lua.sh`, `setup-hyprland.sh`) shellcheck **clean** individually (capture #14, exit 0). Not a blocker, not the `test_command`. |
| **(d) Earlier partial specs of this capability were superseded** | Earlier partial specs of this capability were superseded by archived changes; this delta is the single source of truth for the ML4W binding contract. | **Re-confirmed.** This report verifies against the delta at `openspec/changes/fix-ml4w-keybindings-waybar/specs/ml4w-keybindings-waybar/spec.md` (blob `95419cc5`). Follow-up: none — recorded so the superseded specifications are never treated as current. |

## Corrections to earlier revisions of this note

This section records what the replaced `verify-report.md` got wrong, so the earlier claims are not read as current.

1. **The previous report was inadmissible at the schema level.** Its envelope carried three fields the admission validator does not know: `supersedes_evidence_revision`, `head`, and `head_tree`. `gentle-ai sdd-verify-validate` rejected it with `unknown verify result field supersedes_evidence_revision`, and the native status engine surfaced the same reason in `blockedReasons[0]`. This is the direct cause of `verify: ready` / `archive: blocked` persisting after a "PASS" verdict had been written. The replacement envelope carries **exactly the 13 admitted fields in the admitted order** and validates as `{"valid": true, "verdict": "pass"}`.
2. **The previous report declared `requirements: 13/14` and `scenarios: 7/7`.** Both counts were wrong for the artifact that now exists, and any count other than the native one is rejected for a `pass` verdict. The current spec has **17** `^### Requirement:` lines and **17** `^#### Scenario:` lines; this report declares **17/17** and **17/17**, and each of the 17 is individually evidenced in the matrix above. No partial is declared anywhere.
3. **The previous claim that shellcheck exits 0 was FALSE.** The replaced note asserted "`ruff` / `mypy` / `shellcheck` / `verify-theme-health.py` exit 0". `shellcheck --shell=bash scripts/*.sh` exits **1** with 17 `SC1091` info findings. The correct statement is: the two scripts in this change's own surface exit 0 individually, while the repo-wide glob exits 1 for pre-existing info-level findings. That is recorded here as a pre-existing follow-up per the spec's own Known Gap (c), not as a blocker.
4. **The previous report's `build_exit_code: 1` came from a blocked command, not a real build failure.** Its `build_command` was `pip install -e ".[dev]"`; this host blocks `pip` machine-wide (the shim prints `⚠️  pip está bloqueado. Usá uv add / uv sync / uv run / uvx.`), so the nonzero exit measured environment policy rather than the project. The declared build commands are now the uv forms — `uv sync --all-extras`, exit **0** — which are what this report measures.
5. **The previous report's "680 passed" is superseded by the count measured in this pass.** The count re-measured here is also **680 passed** (`collected 680 items`, 2 warnings, exit 0), but it is stated on the strength of this pass's capture (`sha256:65648567…`, 12,727 B) and not carried over. The previous note's slower runtime figure (23.62 s) is likewise replaced by this pass's 11.75 s. No earlier hash is reused anywhere in this report.
6. **Any earlier `evidence_revision` is superseded and must not be reused.** Prior revisions hashed a 25-file set that included the pre-reconciliation spec and `STATUS.md`. This revision hashes the current working-tree bytes of the fixed 25-file list and excludes `STATUS.md` and `verify-report.md` by design. The two independently run derivations (Python and shell) agree on `sha256:72a2fa0c…`.

## Review workload / PR boundary findings

Forecast read from `tasks.md` → `## Review Workload Forecast`:

- **Total changed lines**: `~200` (JSON additions + new config files)
- **Chained PRs recommended**: `No — single cohesive change`
- **400-line budget risk**: `Low`
- **Decision needed before apply**: `No`

Verification against the actual boundary:

| Commit | Date | Files | Lines | vs. 400-line budget |
| --- | --- | --- | --- | --- |
| `095d58a` "feat: add ML4W standard keybindings, Waybar config, and fix F-key validator" | 2026-07-24 | 5 | **+856 / −1** | exceeded (~2.14×) |
| `469d96a` "fix(hypr): apply correct profile keybindings and dedupe ML4W binds" | 2026-08-04 | 12 | **+877 / −163** | exceeded (~2.60×) |

- **`Chain strategy` was never set** and **`size:exception` was never recorded** for this change (grep over `openspec/changes/fix-ml4w-keybindings-waybar/` finds `size:exception` only inside prose in the replaced report; no `Chain strategy` key exists in `tasks.md`). A `pass` verdict therefore cannot rely on `size:exception` — it rests on the forecast having recommended a single PR, which the implementation then respected.
- **The single-PR boundary was respected.** Both commits touch only the assigned surface — the two profile JSONs, `profile.schema.json`, the Waybar template pair, the ML4W scripts/assets/tests, `README.md`, and this change's own `tasks.md`. No `src/dreamcoder_theme/` file, no unrelated module, no scope creep. The verification confirms only the assigned slice is present.
- **WARNING 5**: the forecast's "~200 lines / Low risk" was a material underestimate against ~856 and ~877 changed lines. This is a **reporting-accuracy defect in `tasks.md`, not an implementation defect**, and it is recorded rather than silently passed.
- The current uncommitted surface (`spec.md` +460/−…, `tasks.md`, `scripts/validate-ml4w-profiles.py`… — measured as 5 files / +421 / −151 including the unrelated `.pi` preflight file) is change-artifact and config bookkeeping, not new implementation, so it does not re-open the PR boundary question.

## Strict TDD compliance

**Strict TDD is NOT active.** `openspec/config.yaml` declares `testing.strict_tdd: false` and `rules.apply.tdd: false`. No parent prompt asserted otherwise, and `apply-progress.md` does not exist (so no `TDD Cycle Evidence` table was claimed or could be). Consequently:

- No `TDD Cycle Evidence` table is required and none is asserted here.
- The absence of TDD evidence is **not** a CRITICAL finding, because the contract that would require it is switched off at the project level.
- No project-local `.pi/gentle-ai/support/strict-tdd-verify.md` override exists; the global guidance was consulted and its checks are inapplicable with TDD off.
- The `tests/ml4w/*.bats` suite is **post-hoc characterisation coverage** of a shell generator (introduced in `3ce95c6`, hardened in `469d96a`), not TDD evidence, and is not presented as such.

## Assertion quality findings

Reviewed `tests/ml4w/generate_custom_lua.bats`, `tests/ml4w/profile_validation.bats`, `tests/ml4w/setup_hyprland.bats` — 34 assertions, all GREEN this pass.

- **No tautologies.** Bind counts are derived from the profile JSON at runtime (`expected=$(jq '.keybindings.bindings | length' …)`), and the suite prints the observed value (`# bind function calls: 56 (expected 56)`, `# bind function calls: 70 (expected 70)`, `# dispatcher count: 70 (expected 70)`). A silently dropped binding fails the test rather than re-baselining it.
- **No ghost loops, no type-only assertions, no smoke-only tests.** Every assertion checks a concrete string, count, or exit status of real generated output.
- **Falsifiable negative assertions are present** and tied to real regressions: `hyprctl dispatch workspace` / `hyprctl dispatch movetoworkspace` must be absent from generated output (the Hyprland ≥ 0.55 Lua-parsing failure), bare Fn keys must not receive a SUPER prefix, and no profile may contain a duplicate key+mods combination (the duplicate-fire bug). Test 13 and test 25 cover these.
- **`luac -p` runs on real generated output** via a temp file, not on a checked-in fixture.
- **No implementation-detail CSS assertions.** There are no CSS assertions at all, so the classic "assert the stylesheet contains this rule" trap is absent.
- **Coverage gap (WARNING 4)**: `grep -rn 'DreamcoderWaybar\|config.jsonc\|hyprland/workspaces\|window-rewrite' tests/` returns **zero hits**. FR2.1–FR2.4 and NFR2 rest entirely on this report's manual parse (capture #16). Adding one test that the config parses and declares `hyprland/workspaces` would convert AC5/AC7-class checks from manual to automated.
- **Minor nit**: the bind-count greps still enumerate `^hl\.(bind|bindl|mouse_bind)\(` even though `bindl`/`mouse_bind` must never appear (measured 0 today). The assertion remains falsifiable, but the pattern keeps dead alternatives.

## Issues found

**CRITICAL — none.** No fabricated evidence, no failing acceptance criterion, no unchecked implementation task, no partial requirement, no security or destructive surface, no theme-engine violation.

**WARNING**

1. **The previous `verify-report.md` was schema-inadmissible and is replaced.** Its three unknown fields (`supersedes_evidence_revision`, `head`, `head_tree`) kept the native engine at `verify: ready` / `archive: blocked` despite a "PASS" verdict. Remediated in this artifact; the engine must be re-read after this write.
2. **`STATUS.md` is stale and partly inaccurate.** Its `## Partial — reconcile before archiving` section still lists FR1.5/FR1.2 and FR2.x as unreconciled, which the current spec text has since resolved. Its asus claim "no bare binding" contradicts the measured **14** bare bindings (the XF86/Fn row), and its "`super_mod`, `bindings`" note is superseded. Its other claims (56/70 bindings, `config.jsonc` exists, `bash -n` + `luac -p` pass, asus has no `SUPER+ALT`) are correct and were independently reconfirmed.
3. **`apply-progress.md` is missing.** The verify input contract names it as a required artifact; the engine reports `artifacts.applyProgress: missing`. Accepted as non-blocking because strict TDD is off and every fact it would carry is re-proved from primary evidence (the two apply commits, the current tree and blobs, the live dispatcher state, 34 green bats assertions and 680 green pytest assertions). It is recorded, **not** fabricated retroactively.
4. **No automated coverage for the Waybar half of the change** (see Assertion quality). The Waybar deliverables are evidenced only by this report's manual JSONC parse.
5. **The review-workload forecast was breached ~2× and ~2.6× with no `size:exception`.** A `tasks.md` reporting-accuracy defect; carried by the single-PR recommendation.
6. **`design.md` says `[NO CHANGE]` for scripts that did change.** `scripts/generate-custom-lua.sh`, `scripts/setup-hyprland.sh` and `scripts/validate-ml4w-profiles.py` are all marked `NO CHANGE` in the design's component map, yet each was modified by `469d96a` (DMI detection, curated-variant install step, Fn-key matcher). The design's component map is stale relative to the shipped implementation; the implementation is still coherent and inside the change's declared surface (FR4.1 holds).
7. **The live keyless-pair invariant is asserted, not machine-proved by the delivery.** `hyprctl binds -j` reports both keyboard-backlight binds as `modmask 0, key "", keycode 0`, distinguished only by `arg` (`167`/`169`) and `description`. This pass proves they are distinct **by argument**, which is the basis NFR4's carve-out names; the output alone cannot yield a duplicate count without that argument-level reading.

**SUGGESTION**

1. Wire the mode CSS import (or drop the accent wording entirely) so gap (a) is closed; that is the only change needed to make the Waybar accent genuinely reachable.
2. Decide whether `DreamcoderWaybar/` is a user-copy template or an installed target; if installed, add it to `setup-hyprland.sh` and reconcile with the existing ML4W-managed symlink assertion, then re-verify gap (b)'s two original statements.
3. Add one pytest asserting `DreamcoderWaybar/.config/waybar/config.jsonc` parses and contains `hyprland/workspaces` (WARNING 4).
4. Add per-line `# shellcheck source=` directives or a scoped `.shellcheckrc` to retire the 17 `SC1091` info findings (gap (c)).
5. Refresh `STATUS.md` (WARNING 2) so it stops contradicting the current spec and its own measurements.
6. Repair the `design.md` component map's `[NO CHANGE]` markers to match what actually changed (WARNING 6).
7. `custom.lua` embeds `-- Last generated: <timestamp>`, so its **file** hash is not a stable evidence anchor; keep anchoring on generator stdout plus bind/finding counts, as this report does.

## Verdict

**PASS — 17/17 requirements, 17/17 scenarios, 0 blockers, 0 CRITICAL, 7 WARNING.**

The change is delivered and independently re-verified in this pass at working tree `HEAD 43fe2fe` with `evidence_revision sha256:72a2fa0c6824c9c5af558128a0cd056b62f60f75b6b71c5ab817e71a9e85abad`. All 6 tasks are complete with **zero** unchecked markers. Every one of the 17 requirements and 17 scenarios was checked against real evidence produced in this pass: `default.json` carries 56 bindings and `asus-vivobook15.json` 70, with modifier sets matching FR1.7 digit-for-digit; all 20 workspace, 16 focus/move, 4 window-management, 5 app-launcher and 4 Ctrl+Win chords were matched by `(mods, key)` in both profiles with 0 intra-profile duplicates; the Waybar config parses to the exact `modules-left/center/right` layout with a 20-entry `window-rewrite` and `format-icons`; `style.css` has exactly one import (`colors.css`) and no color definitions; both profiles validate against `profile.schema.json`; both apply scripts pass `bash -n`; the DMI-detected generator emits 70 binds with 0 `hyprctl dispatch` and 0 `hl.bindl`/`hl.mouse_bind`, passing `luac -p`; the live table shows 119 binds / 118 distinct `(modmask, key)` / 0 real collisions with `hyprctl configerrors` empty; and no `src/dreamcoder_theme/` file is in the change's file set.

The four spec-recorded gaps — the unreachable accent rule, the dormant Waybar templates, shellcheck's 17 pre-existing `SC1091` info findings, and the superseded earlier partial specs — are recorded above as `## Known Gaps (not counted as requirements)` and are **explicitly not counted** in the 17/17. The current spec text already scopes FR2.2 away from the accent, which is why gap (a) coexists with a compliant FR2.2.

The PASS is not blanket: 7 WARNINGs are on record, one of which (the review-workload forecast breach) is a `tasks.md` accuracy defect and one of which (the stale `design.md` component map) is documentation drift. None is a correctness blocker.

**This report makes verification ready; archive itself was not performed.** After this write the engine reports `dependencies.verify: all_done`, `dependencies.archive: ready` and `nextRecommended: archive`, with `taskProgress 6/6` — the earlier `unknown verify result field supersedes_evidence_revision` reason is gone. One runtime gate still stands and it is **not** a verification-quality blocker: the bounded-attempt settle returned `state: blocked / reason: maintainer_decision` because this replacement measured 521 changed lines against a 400-line objective budget. That requires an explicit maintainer reset decision (command recorded above) and was **not** self-authorized here. On the review side, `apply-progress.md` remains absent (WARNING 3) and `STATUS.md` is stale (WARNING 2). I edited exactly one file, launched no child subagents, and fixed nothing.

## Cleanup / process evidence

- **Written inside `allowedEditRoots`**: `openspec/changes/fix-ml4w-keybindings-waybar/verify-report.md` (this file) only. No other tracked repo file was modified, and `STATUS.md`, `spec.md`, `tasks.md`, `proposal.md`, `design.md`, `openspec/config.yaml`, `pyproject.toml` and every source file were left byte-identical.
- **Written outside the repo**: command captures and helper scripts under `/tmp/ml4wverify/` (outside `allowedEditRoots`, removable, repo-neutral). The generated Lua used for `luac -p` lives only at `/tmp/ml4wverify/13_generated.lua`.
- **No overwrite of live Hyprland state**: the writing form of the generator was deliberately **not** run. `~/.config/hypr/custom.lua` is byte-identical before and after this pass — `sha256:b6a51a71f2fe6991…` prefix, 10,534 bytes, mtime `2026-09-11 19:56:04` unchanged. Only `--dry-run` and `--validate` were used, and `luac -p` ran on the extracted dry-run body.
- **No child subagents launched. No worktrees created. No servers or background processes started. No `sdd-attempt reset`.**
- **Pre-existing dirty file, untouched**: `.pi/gentle-ai/sdd-preflight.json` was already modified before this pass and was not written to.
- **Bounded-attempt bookkeeping**: the pre-existing `verify-fix-ml4w-conformance` attempt (`sha256:37bcb7bd…`) was continued with `--token`, not duplicated, and is settled with `--outcome passed` and this pass's `evidence_revision`.

## Key Learnings

1. **A "PASS" verdict cannot outrun its envelope schema.** The change was genuinely delivered, yet the native engine stayed at `verify: ready` / `archive: blocked` because `verify-report.md` carried three fields the admission validator does not know (`supersedes_evidence_revision`, `head`, `head_tree`). Admissibility is a separate gate from truth: exactly 13 fields, in order, inside a ` ```yaml ` fence whose first line is `schema: gentle-ai.verify-result/v1`.
2. **Counts must come from the parser the engine uses.** `requirements`/`scenarios` are the `^### Requirement:` and `^#### Scenario:` counts of the current spec (17/17), not a judgement about coverage. Declaring `13/14` while the artifact contains 17 makes a `pass` verdict unrepresentable, regardless of how well the code works.
3. **A blocked build command is not a failing build.** `pip` is blocked machine-wide on this host, so `pip install -e ".[dev]"` measured host policy, not the project. `uv sync --all-extras` is the honest build gate here — and it is load-bearing, because `pyyaml>=6` in the `dev` extra is what lets `tests/test_lazygit_renderer.py` import `yaml` and the suite collect at all.
4. **Repo-wide lint findings are not change findings.** `shellcheck --shell=bash scripts/*.sh` exits 1 with 17 pre-existing `SC1091` info findings, while both scripts inside this change's surface shellcheck clean individually. Two measurements of the "same" tool describe different things; the spec's `## Known Gaps` already says which one is normative.
5. **Anchoring evidence on files that rewrite themselves is a trap.** Two artifacts here rewrite or drift by design: `custom.lua` embeds a generation timestamp, and `STATUS.md` is mutable status bookkeeping. Hence a fixed 25-file blob-list revision that excludes both status notes, two independent derivations (Python and shell) agreeing on one digest, a read-only generator form (`--dry-run`/`--validate`), and hashes taken from captured bytes on disk rather than from memory.
