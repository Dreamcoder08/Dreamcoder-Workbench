-- WezTerm configuration for Dreamcoder Workbench
-- https://github.com/dreamcoder08/dreamcoder-dots

local wez = require 'wezterm'
local config = wez.config_builder()

-- ─── Theme Detection ──────────────────────────────────
local function get_theme()
    local mode = os.getenv("DREAMCODER_THEME_MODE") or "dark"
    if mode == "light" then
        return wez.plugin.require_file("dreamcoder-light.lua", "dreamcoder-wezterm")
    else
        return wez.plugin.require_file("dreamcoder-dark.lua", "dreamcoder-wezterm")
    end
end

-- ─── Font ─────────────────────────────────────────────
config.font = wez.font('JetBrainsMono Nerd Font')
config.font_size = 14.0
config.line_height = 1.2

-- ─── Window ───────────────────────────────────────────
config.window_background_opacity = 0.76
config.window_decorations = "RESIZE"
config.window_padding = { left = 8, right = 8, top = 8, bottom = 8 }
config.initial_cols = 120
config.initial_rows = 35
config.window_close_confirmation = "NeverPrompt"

-- ─── Cursor ───────────────────────────────────────────
config.default_cursor_style = "BlinkingBlock"
config.cursor_blink_rate = 500
config.cursor_blink_ease_in = "Constant"
config.cursor_blink_ease_out = "Constant"

-- ─── Tab Bar ──────────────────────────────────────────
config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = true
config.hide_tab_bar_if_only_one_tab = true
config.show_tab_index_in_tab_bar = false

-- ─── Performance ──────────────────────────────────────
config.max_fps = 120
config.animation_fps = 60
config.front_end = "WebGpu"

-- ─── Key Bindings ─────────────────────────────────────
config.keys = {
    { key = "t", mods = "CTRL|SHIFT", action = wez.action.SpawnTab "CurrentPaneDomain" },
    { key = "w", mods = "CTRL|SHIFT", action = wez.action.CloseCurrentTab { confirm = false } },
    { key = "Tab", mods = "CTRL", action = wez.action.ActivateTabRelative(1) },
    { key = "5", mods = "CTRL|SHIFT", action = wez.action.SplitHorizontal { domain = "CurrentPaneDomain" } },
    { key = "6", mods = "CTRL|SHIFT", action = wez.action.SplitVertical { domain = "CurrentPaneDomain" } },
}

-- ─── Shell ────────────────────────────────────────────
config.default_prog = { "fish", "--login" }

return config
