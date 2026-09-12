# ============================================================================
# BATS tests: --profile argument guard in the ML4W scripts
# ============================================================================
# Both scripts must reject `--profile` with no following value with a clear
# message. Under `set -u`, referencing an unset positional parameter aborts
# with "unbound variable" before an unguarded `${1}` test can evaluate, so the
# guard must use `${1:-}`.

load '../helpers/setup'

@test "setup-hyprland: --profile without a value fails with a clear message" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/setup-hyprland.sh" --profile 2>&1
  [ "$status" -ne 0 ]
  [[ "$output" == *"requires a non-empty profile name"* ]]
  [[ "$output" != *"unbound variable"* ]]
}

@test "verify-ml4w-setup: --profile without a value fails with a clear message" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/verify-ml4w-setup.sh" --profile 2>&1
  [ "$status" -ne 0 ]
  [[ "$output" == *"requires a non-empty profile name"* ]]
  [[ "$output" != *"unbound variable"* ]]
}

@test "setup-hyprland: --profile with an empty value fails clearly" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/setup-hyprland.sh" --profile "" 2>&1
  [ "$status" -ne 0 ]
  [[ "$output" == *"requires a non-empty profile name"* ]]
}

@test "verify-ml4w-setup: --profile with an empty value fails clearly" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/verify-ml4w-setup.sh" --profile "" 2>&1
  [ "$status" -ne 0 ]
  [[ "$output" == *"requires a non-empty profile name"* ]]
}

@test "setup-hyprland: --profile with a value is accepted" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/setup-hyprland.sh" --profile default --dry-run 2>&1
  [[ "$output" == *"Using profile: default"* ]]
}
