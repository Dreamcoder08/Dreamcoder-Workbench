-- Configuration
-- ============================================================================
-- CONTRACT: This file only defines keybindings NOT managed by the Dreamcoder
-- machine profile (custom.lua, generated from DreamcoderProfiles/*.json).
--
-- The profile JSON owns: applications, workspaces, window focus/move,
-- fullscreen/floating/split toggles, screenshots, theme/hyprsunset, the F1-F12
-- multimedia row (volume, brightness, media, lock) and the keyboard backlight.
--
-- Editing those binds: edit the profile JSON (DreamcoderProfiles/dreamcoder/
-- asus-vivobook15.json on this laptop) and re-run generate-custom-lua.sh.
-- Do NOT add them here again or Hyprland double-fires them (duplicate binds).
-- ============================================================================
local mainMod = "SUPER" -- Sets "Windows" key as main modifier

-- Applications (profile-owned: RETURN/B/E/SPACE/V/CTRL+K/CTRL+M/CTRL+S/CTRL+C)
-- Only the emoji picker stays here.
hl.bind(mainMod .. " + CTRL + E", hl.dsp.exec_cmd("~/.config/ml4w/settings/emojipicker.sh"), { description = "Open the emoji picker" })

-- Windows
-- Profile owns: Q (kill), F (fullscreen), T (float), H/L/K/J + arrows (focus),
-- SHIFT+H/L/K/J + arrows (move window), Y (toggle split).
hl.bind(mainMod .. " + SHIFT + Q", hl.dsp.exec_cmd("hyprctl activewindow | grep pid | tr -d 'pid:' | xargs kill"), { description = "Quit active window and all open instances" })
hl.bind(mainMod .. " + M", hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" }), { description = "Toggle Maximize Window" })
hl.bind(mainMod .. " + SHIFT + T", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-allfloat"), { description = "Toggle floating for all windows of workspace" })
hl.bind(mainMod .. " + ALT + T", function() hl.dispatch(hl.dsp.window.float({ action = "toggle" })); hl.dispatch(hl.dsp.window.pin()) end, { description = "Toggle floating + pinned" })
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.resize({ x = 100, y = 0, relative = true }), { repeating = true }, { description = "Increase window width with keyboard" })
hl.bind(mainMod .. " + SHIFT + left", hl.dsp.window.resize({ x = -100, y = 0, relative = true }), { repeating = true }, { description = "Reduce window width with keyboard" })
hl.bind(mainMod .. " + SHIFT + down", hl.dsp.window.resize({ x = 0, y = 100, relative = true }), { repeating = true }, { description = "Increase window height with keyboard" })
hl.bind(mainMod .. " + SHIFT + up", hl.dsp.window.resize({ x = 0, y = -100, relative = true }), { repeating = true }, { description = "Reduce window height with keyboard" })
hl.bind(mainMod .. " + G", hl.dsp.group.toggle(), { description = "Toggle window group" })
-- hl.bind(mainMod .. " + SHIFT + G", hl.dsp.group.active("f"), { description = "Switch to next group window" })
hl.bind(mainMod .. " + ALT + left", hl.dsp.window.swap({ direction = "l" }), { description = "Swap tiled window left" })
hl.bind(mainMod .. " + ALT + right", hl.dsp.window.swap({ direction = "r" }), { description = "Swap tiled window right" })
hl.bind(mainMod .. " + ALT + up", hl.dsp.window.swap({ direction = "u" }), { description = "Swap tiled window up" })
hl.bind(mainMod .. " + ALT + down", hl.dsp.window.swap({ direction = "d" }), { description = "Swap tiled window down" })

-- Actions
hl.bind(mainMod .. " + CTRL + R", hl.dsp.exec_cmd("hyprctl reload"), { description = "Reload Hyprland configuration" })
hl.bind(mainMod .. " + SHIFT + A", hl.dsp.exec_cmd("~/.config/hypr/scripts/toggle-animations.sh"), { description = "Toggle animations" })
hl.bind(mainMod .. " + PRINT", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh"), { description = "Take a screenshot" })
hl.bind(mainMod .. " + ALT + F", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh --instant"), { description = "Take an instant full-screen screenshot" })
hl.bind(mainMod .. " + ALT + S", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh --instant-area"), { description = "Take an instant area screenshot" })
hl.bind(mainMod .. " + ALT + A", hl.dsp.exec_cmd("~/.config/hypr/scripts/text-extractor.sh"), { description = "Extract text from an area" })
hl.bind(mainMod .. " + CTRL + P", hl.dsp.exec_cmd("qs ipc call power toggle"), { description = "Start Power Menu" })
hl.bind(mainMod .. " + SHIFT + W", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-wallpaper-app --random"), { description = "Change the wallpaper" })
hl.bind(mainMod .. " + CTRL + W", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-wallpaper-app"), { description = "Open wallpaper selector" })
hl.bind(mainMod .. " + ALT + W", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-wallpaper-automation"), { description = "Start random wallpaper script" })
hl.bind(mainMod .. " + CTRL + RETURN", hl.dsp.exec_cmd("~/.config/hypr/scripts/launcher.sh"), { description = "Open application launcher" })
hl.bind(mainMod .. " + SHIFT + B", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-reload-statusbar"), { description = "Reload Status Bar" })
hl.bind(mainMod .. " + CTRL + B", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-statusbar"), { description = "Toggle Status Bar" })
hl.bind(mainMod .. " + ALT + B", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-statusbar-autohide"), { description = "Toggle Status Bar Autohide" })
-- ML4W 2.16 moved "Reload Dock" to SUPER + SHIFT + D, which is profile-owned
-- here (Dreamcoder theme toggle), so the dock reload stays unbound.
hl.bind(mainMod .. " + ALT + D", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-dock-autohide"), { description = "Toggle Dock Autohide" })
hl.bind(mainMod .. " + SHIFT + R", hl.dsp.exec_cmd("~/.config/hypr/scripts/loadconfig.sh"), { description = "Reload hyprland config" })
hl.bind(mainMod .. " + CTRL + T", hl.dsp.exec_cmd("~/.config/waybar/themeswitcher.sh"), { description = "Open waybar theme switcher" })
hl.bind(mainMod .. " + SHIFT + M", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-theme"), { description = "Toggle between light and dark mode" })
hl.bind(mainMod .. " + ALT + G", hl.dsp.exec_cmd("~/.config/hypr/scripts/gamemode.sh"), { description = "Toggle game mode" })
hl.bind(mainMod .. " + CTRL + L", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-power -l"), { description = "Lock Screen" })
-- Note: SHIFT + H is profile-owned (Move Window Left); hyprsunset is
-- profile-owned too via SHIFT + U (on) / SHIFT + I (off).
hl.bind(mainMod .. " + Tab", hl.dsp.exec_cmd("qs -p ~/.local/share/quickshell-overview ipc call overview toggle"), { description = "Open Select Window Menu" })
hl.bind("CTRL + ALT + T", hl.dsp.exec_cmd("~/.config/ml4w/themes/themes.sh"), { description = "Open Select Window Menu" })

-- AZERTY keyboard layout setup (ported from ML4W 2.16 default.lua)
-- The profile owns SUPER + [0-9] workspace binds. On AZERTY the number row
-- needs Shift, so Hyprland sees the unshifted keysyms instead of the digits;
-- bind those keysyms here only when an AZERTY layout is detected, so QWERTY
-- layouts never get duplicate workspace binds.
local azerty_keys = {
    fr = { "ampersand", "eacute", "quotedbl", "apostrophe", "parenleft",
           "minus", "egrave", "underscore", "ccedilla", "agrave" },
    be = { "ampersand", "eacute", "quotedbl", "apostrophe", "parenleft",
           "section", "egrave", "exclam", "ccedilla", "agrave" },
}

-- Variants of the layouts above that are not AZERTY
local non_azerty_variants = {
    fr = { us = true, bepo = true, bepo_afnor = true, dvorak = true },
    be = { wang = true },
}

local function detect_azerty()
    local f = io.open(os.getenv("HOME") .. "/.config/hypr/input.lua", "r")
    if not f then return nil end
    local content = f:read("*all")
    f:close()

    -- kb_layout may be a list ("be,us"); the first entry is the primary one
    local layout = content:match('kb_layout%s*=%s*"([^",]*)')
    local variant = content:match('kb_variant%s*=%s*"([^",]*)') or ""
    if not layout then return nil end
    layout = layout:lower():gsub("%s", "")
    variant = variant:lower():gsub("%s", "")

    local excluded = non_azerty_variants[layout]
    if excluded and excluded[variant] then return nil end
    return azerty_keys[layout]
end

local ws_keys = detect_azerty()
if ws_keys then
    for i = 1, 10 do
        hl.bind(mainMod .. " + " .. ws_keys[i],         hl.dsp.focus({ workspace = i }),        { description = "Focus workspace " .. i })
        hl.bind(mainMod .. " + SHIFT + " .. ws_keys[i], hl.dsp.window.move({ workspace = i }), { description = "Move window to workspace " .. i })
    end
end

-- Special workspace (scratchpad)
-- Note: SHIFT + S is profile-owned (screenshot screen), so only plain S here.
hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special("scratchpad"), { description = "Toggle special workspace scratchpad" })

-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }), { description = "Switch to next workspace" })
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }), { description = "Switch to previous workspace" })

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true, description = "Move window with the mouse" })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true, description = "Resize window with the mouse" })

-- Laptop multimedia keys (backup for the physical function keys)
-- Profile also binds F1-F12 directly; both coexist without collisions so the
-- hardware works whether it emits XF86* or plain F1-F12 keycodes.
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true, description = "Raise volume" })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true, description = "Lower volume" })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true, repeating = true, description = "Mute audio" })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true, repeating = true, description = "Mute microphone" })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"),                  { locked = true, repeating = true, description = "Increase brightness" })
hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"),                  { locked = true, repeating = true, description = "Decrease brightness" })

-- Requires playerctl
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true, description = "Next track" })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true, description = "Pause audio" })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true, description = "Play audio" })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true, description = "Previous track" })
