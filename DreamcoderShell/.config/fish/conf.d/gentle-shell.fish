# Prefer the official self-contained Gentle Shell installation.
if test -x "$HOME/.gentle-shell/bin/gentle-shell"
    set -gx PATH "$HOME/.gentle-shell/bin" (string match -v -- "$HOME/.gentle-shell/bin" $PATH)
end
