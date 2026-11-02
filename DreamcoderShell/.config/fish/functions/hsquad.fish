function hsquad --description 'Open a Herdr app squad (two Gentle Shell panes and Claude Code) in a project space'
    set -l dir $PWD
    test (count $argv) -gt 0; and set dir $argv[1]
    set dir (path resolve -- $dir)
    if not test -d $dir
        echo "hsquad: not a directory: $dir" >&2
        return 1
    end
    if not herdr-app status >/dev/null 2>&1
        echo "hsquad: the Herdr app is not running" >&2
        return 1
    end
    set -l name (path basename -- $dir)
    # Reuse the space made for this folder; otherwise give the project its own space.
    set -l space (herdr-app ls | python3 -I -c 'import json, sys
spaces = json.load(sys.stdin)["spaces"]
print(next((s["id"] for s in spaces if s["folder"] == sys.argv[1]), ""))' $dir)
    if test -n "$space"
        herdr-app do tab.new --space $space --name $name --folder $dir --argv '["gentle-shell"]' >/dev/null; or return 1
    else
        herdr-app do space.new --folder $dir --tab $name --argv '["gentle-shell"]' >/dev/null; or return 1
    end
    herdr-app do terminal.open --place right --folder $dir --argv '["gentle-shell"]' >/dev/null; or return 1
    herdr-app do terminal.open --place down --folder $dir --argv '["claude"]' >/dev/null
end
