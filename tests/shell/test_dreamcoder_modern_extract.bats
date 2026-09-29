#!/usr/bin/env bats
# ============================================================================
# extract() in dreamcoder-modern.sh is sourced by bash and zsh. In bash, a
# single `local a=... b=${a...}` expands b BEFORE a is assigned (ShellCheck
# SC2318), which left the default output directory empty.
# ============================================================================

setup() {
    WORK="$(mktemp -d)"
    cd "${WORK}"
    python3 - <<'PY'
import zipfile
with zipfile.ZipFile("sample.zip", "w") as z:
    z.writestr("hello.txt", "hi")
PY
}

teardown() {
    cd /
    rm -rf "${WORK}"
}

extract_in_bash() {
    bash -c "source '${BATS_TEST_DIRNAME}/../../DreamcoderShell/.config/shell/aliases/dreamcoder-modern.sh' >/dev/null 2>&1; extract $*"
}

@test "extract defaults the output directory to the archive name without extension" {
    run extract_in_bash sample.zip
    [ "$status" -eq 0 ]
    [ -f "${WORK}/sample/hello.txt" ]
}

@test "extract honours an explicit output directory for zip archives" {
    run extract_in_bash sample.zip custom
    [ "$status" -eq 0 ]
    [ -f "${WORK}/custom/hello.txt" ]
}

@test "extract rejects an unknown archive type" {
    : > notes.unknown
    run extract_in_bash notes.unknown
    [ "$status" -eq 1 ]
}
