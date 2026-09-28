-- ========================================================
-- Dreamcoder — auto-detect dispatcher
-- ========================================================
-- Usage: vim.cmd.colorscheme("dreamcoder")
-- Auto-loads the correct variant based on:
--   1. DREAMCODER_THEME_MODE env var (set by `dreamcoder light`)
--   2. ~/.cache/dreamcoder/cursor-cli.env (persisted by apply-theme-mode.sh)
--   3. vim.o.background (Neovim's own setting)
--   4. Fallback: dark
-- Direct variant access: colorscheme dreamcoder-dark / dreamcoder-light
-- ========================================================

vim.g.colors_name = "dreamcoder"

-- Glass blur stays dark-only; light needs opaque paper backgrounds for readability.
vim.opt.winblend = 10
vim.opt.pumblend = 10

-- Find variant files relative to this file's location
local src = debug.getinfo(1, "S").source:match("@?(.*)")
local theme_dir = src:match("^(.*[/\\])") or "."

-- Resolve base mode: env var > cache file > vim.o.background > dark
local mode = vim.env.DREAMCODER_THEME_MODE

if not mode then
  local cache_file = vim.fn.expand("~/.cache/dreamcoder/cursor-cli.env")
  local f = io.open(cache_file, "r")
  if f then
    for line in f:lines() do
      local m = line:match('^export DREAMCODER_THEME_MODE="(.-)"')
      if m then
        mode = m
        break
      end
    end
    f:close()
  end
end

if not mode then
  mode = vim.o.background or "dark"
end

if mode == "dark" then
  dofile(theme_dir .. "dreamcoder-dark.lua")
else
  dofile(theme_dir .. "dreamcoder-light.lua")
end
