# Nushell environment for Dreamcoder Workbench
# https://github.com/dreamcoder08/dreamcoder-dots

# Path
$env.PATH = (
    $env.PATH
    | split row (char esep)
    | prepend $"($env.HOME)/.local/bin"
    | prepend $"($env.HOME)/.cargo/bin"
    | prepend $"($env.HOME)/.volta/bin"
    | prepend $"($env.HOME)/.bun/bin"
)

# Editor
$env.EDITOR = "nvim"
$env.VISUAL = "nvim"
$env.COLORTERM = "truecolor"

# Theme mode
$env.DREAMCODER_THEME_MODE = (
    if ($env.DREAMCODER_THEME_MODE? | is-empty) { "dark" }
    else { $env.DREAMCODER_THEME_MODE }
)
