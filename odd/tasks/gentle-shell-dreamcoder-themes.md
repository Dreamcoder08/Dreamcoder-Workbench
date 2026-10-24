# Gentle Shell Dreamcoder mode integration

## Objective
Make `dreamcoder light` and `dreamcoder dark` apply the canonical Dreamcoder design system to Gentle Shell as well as Pi.

## Problem and approach
Gentle Shell defaults to an isolated `~/.gentle-shell/agent` home while existing generation targets only `~/.pi/agent`. The Pi helper repoints the stable active file to a variant and ignores configured destinations. Use canonical renderer output and persistent `dreamcoder` selection in both homes; preserve unrelated settings and user work. Avoid duplicate palettes and unnecessary sibling repository changes.

## Scope and constraints
- Theme settings, rendering/sync, shell activation, regression tests, smallest existing theme guide.
- Respect `GENTLE_SHELL_HOME`, Pi runtime/configuration overrides and explicit theme/settings destinations with consistent precedence.
- Never run the full system mode command against the real desktop during tests.
- Existing unrelated dirty files, especially `scripts/apply-system-mode.sh`, remain untouched.
- No commits, push or PR authorized. RDD clone-local is off.
- Hot reload depends on selected active user theme; report limitations honestly.

## Tasks
- [x] T1 (implemented and corrected with self-verification; no commit authorized): Implement dual-home generation/selection and stable-file mode activation, with focused RED/GREEN tests and guide update.
- [x] T2 (verified and current dark theme activated; no commit authorized): Assess diff, follow verification plan, and activate only Gentle Shell/Pi theme files in the current mode without changing the rest of the desktop.

## Acceptance and checks
Both modes produce canonical role colors in both homes, preserve unrelated settings, honor custom directories, and do not mutate repository variant files through legacy symlinks. Focused commands: `bats tests/shell/test_pi_theme.bats`; `pytest tests/test_pi_theme_generation.py tests/test_dreamcoder_sync.py -q`; applicable renderer/control tests; `python scripts/validate-markdown-links.py`. Use isolated homes for functional checks. Check actual installed Gentle Shell theme selection after bounded activation.

## Evidence and progress
Read-only exploration confirmed existing canonical Pi renderer and default Gentle Shell isolated home in sibling runtime launcher. Real Pi settings select `dreamcoder`; installed active theme is currently a symlink to the dark repository variant. Worker observed RED (legacy symlink and missing home fields), then GREEN for generation/sync, five Bats cases, transaction rollback, renderer and CLI activation tests; markdown links passed. Parent active LSP probe: seven changed Python files clean. ASSESS was unavailable due to untracked-scope declaration and returned high-risk fallback requiring independent verification. Independent verifier observed 109 Python tests and 5 Bats tests passing plus markdown exit 0. It identified that bounded helper preparation may call Matugen with external template side effects when wallpaper adaptation is enabled; tests disable adaptation. Correction completed: standalone helper sets process-local `DREAMCODER_ADAPTIVE=0`; normal system sync remains adaptive. Fake-Matugen test observed RED invocation before fix and GREEN no invocation for both modes after fix; 6/6 Bats and 12 focused Python tests passed plus markdown exit 0. Corrected independent verification passed: 109 Python tests, 6/6 Bats, markdown links and scoped diff checks exit 0. Current dark mode activated via bounded helper after agent-file backup under `~/.cache/dreamcoder/agent-theme-backups/20261002-223240`. Both real agent homes now contain regular stable theme files matching validated canonical dark output and settings select `dreamcoder`; repository variants remained byte-identical.

## Limitations and next step
Full live desktop switching and broader suite were deliberately not run; desktop adapters were mocked. Active-session hot reload was not visually verified; use `/reload` or restart Gentle Shell if its prior theme remains visible. Tests were run in a clean isolated environment to avoid inherited agent overrides. Normal mode commands retain transactional rollback; standalone helper is nontransactional. RDD is off and native assessment fell back to independent verification due untracked declaration; no native review was started. No commit was authorized or created. Implementation is ready for user use with `dreamcoder light` / `dreamcoder dark`.
