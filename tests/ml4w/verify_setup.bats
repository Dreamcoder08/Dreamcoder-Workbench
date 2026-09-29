# ============================================================================
# BATS tests: scripts/verify-ml4w-setup.sh robustness
# ============================================================================
# The script used to interpolate file paths into inline Python source, so a path
# with an apostrophe broke schema validation (and a crafted one could inject
# code); paths now travel through sys.argv. A missing jsonschema also skipped the
# check without saying so.

load '../helpers/setup'

# tests/helpers/setup.bash points HOME at a temp dir, which hides user-site Python
# packages (jsonschema often lives there). Keep the invoking user's package base so the
# schema check really runs instead of being skipped.
use_real_python_userbase() {
  local real_home
  real_home="$(getent passwd "$(id -u)" | cut -d: -f6)"
  export PYTHONUSERBASE="${real_home}/.local"
}

# A throwaway dots tree whose directory name contains an apostrophe.
make_dots_tree() {
  DOTS="${TEST_TEMP_HOME}/dots'tree"
  mkdir -p "${DOTS}/lib" "${DOTS}/DreamcoderProfiles/dreamcoder"
  cp "${DREAMCODER_DOTS_DIR}/lib/"*.sh "${DOTS}/lib/"
  cp "${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/default.json" \
     "${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/profile.schema.json" \
     "${DOTS}/DreamcoderProfiles/dreamcoder/"
}

run_verify() {
  DREAMCODER_DOTS_DIR="${DOTS}" run bash "${BATS_TEST_DIRNAME}/../../scripts/verify-ml4w-setup.sh" \
    --profile default
}

@test "verify-ml4w-setup: schema validation works when the dots path contains an apostrophe" {
  use_real_python_userbase
  python3 -c 'import jsonschema' 2>/dev/null || skip "python jsonschema not installed"
  command -v jq >/dev/null || skip "jq not installed"
  make_dots_tree
  run_verify
  [[ "$output" == *"Profile matches schema"* ]]
}

@test "verify-ml4w-setup: says so when schema validation is skipped for lack of jsonschema" {
  make_dots_tree
  # A python3 without jsonschema: a shim earlier in PATH.
  mkdir -p "${TEST_TEMP_HOME}/bin"
  printf '#!/bin/sh\nexit 1\n' >"${TEST_TEMP_HOME}/bin/python3"
  chmod +x "${TEST_TEMP_HOME}/bin/python3"
  PATH="${TEST_TEMP_HOME}/bin:${PATH}" run_verify
  [[ "$output" == *"Schema validation skipped"* ]]
}

@test "verify-ml4w-setup: a missing jq is reported as skipped, not as invalid JSON" {
  make_dots_tree
  # PATH with every tool except jq: symlink the basics into an empty bin dir.
  mkdir -p "${TEST_TEMP_HOME}/nojq"
  for tool in bash env dirname basename cat grep sed awk tr cut head tail sort uniq date git python3 readlink; do
    src="$(command -v "$tool" 2>/dev/null)" && ln -sf "$src" "${TEST_TEMP_HOME}/nojq/$tool"
  done
  PATH="${TEST_TEMP_HOME}/nojq" run_verify
  [[ "$output" == *"jq is not installed"* ]]
  [[ "$output" == *"JSON check skipped (needs jq)"* ]]
  [[ "$output" != *"INVALID JSON"* ]]
}
