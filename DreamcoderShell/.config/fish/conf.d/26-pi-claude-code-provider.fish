# pi-claude-code-provider: run pi's Claude models through a pinned Claude Code
# binary (subscription limits, first-party auth). 2.1.280 is the newest version
# that serves claude-opus-5-5 without tripping the provider's isolation check
# (2.1.281 reports built-in plugins: chem/pi-claude-code-provider#12, #13).
# Remove the pin once the provider ships a fix, then run /pi-claude-code-provider-doctor.
set -gx PI_CLAUDE_CODE_PROVIDER_PATH $HOME/.local/opt/claude-2.1.280
