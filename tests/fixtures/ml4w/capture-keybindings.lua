-- Load the public variant with a recording Hyprland API; never execute commands.
-- Usage: lua capture-keybindings.lua <variant.lua> [key combination]
local commands = {}
local noop = function() return {} end
hl = {
    bind = function(key, action)
        if type(action) == "table" and action.command then
            assert(not commands[key], "duplicate command binding: " .. key)
            commands[key] = action.command
        end
    end,
    dsp = {
        exec_cmd = function(command) return { command = command } end,
        window = setmetatable({}, { __index = function() return noop end }),
        workspace = { toggle_special = noop },
        group = { toggle = noop },
        focus = noop,
    },
}
dofile(arg[1])
if arg[2] then
    assert(commands[arg[2]], "missing command binding: " .. arg[2])
    print(commands[arg[2]])
else
    local keys = {}
    for key in pairs(commands) do keys[#keys + 1] = key end
    table.sort(keys)
    for _, key in ipairs(keys) do print(key .. "\t" .. commands[key]) end
end
