#!/usr/bin/env bats
# ============================================================================
# Files under DreamcoderShell/.config/shell are sourced by the interactive
# .zshrc and .bashrc; they must never turn on errexit/nounset/pipefail.
# ============================================================================

@test "sourcing every shell lib file leaves bash options untouched" {
    run bash -c 'for f in DreamcoderShell/.config/shell/*/*.sh; do source "$f" >/dev/null 2>&1; done
        shopt -qo errexit && echo errexit; shopt -qo nounset && echo nounset; shopt -qo pipefail && echo pipefail; echo done'
    [ "$output" = "done" ]
}
