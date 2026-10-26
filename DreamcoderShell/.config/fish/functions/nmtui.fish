function nmtui --description 'NetworkManager with terminal-native Dreamcoder colors'
    if command -q dreamcoder-nmtui
        command dreamcoder-nmtui $argv
    else
        command nmtui $argv
    end
end
