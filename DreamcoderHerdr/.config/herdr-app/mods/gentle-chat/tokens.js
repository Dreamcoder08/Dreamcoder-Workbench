// Gentle Shell Desktop design tokens: the values of design/herdr-desktop/01-inspector.html
// (`:root` lines 13-35 and the component CSS), for every Gentle Shell Desktop mod.
//
// SHARED MODULE. This file is the one source for the centre column (gentle-chat, T5) and the
// sidebar / inspector / status mods (T6). A mod can only import files inside its own folder,
// so T6 mods carry a byte-for-byte COPY of this file; edit it here first, then re-copy it
// (`cp herdr/mods/gentle-chat/tokens.js herdr/mods/<mod>/tokens.js`). Pure: no host calls at
// module level (mods reload in place), only `herdr` reads inside the functions.
//
// Colour policy (T5 brief): a token with a Herdr theme role reads `theme()[role]`, so the
// window follows the layout's theme and the theme picker; a token without a role is the exact
// artboard hex. The layout (herdr/layouts/gentle-shell.json) makes the roles equal the artboard
// through its root `"theme": { "light": "gentle-shell-light", "dark": "gentle-shell-dark" }`
// (S14): herdr/themes/gentle-shell-dark.json carries LAYOUT_COLORS in its `colors`, the light
// file LIGHT_COLORS; without them, the roles show the person's theme (graphite, ...) and only the
// hex tokens stay Gentle. The hex of the appearance Herdr shows (`settings().dark`) is used.

import { fonts, settings } from "herdr";

// name: [artboard hex, Herdr theme role or null, artboard source]
const TOKENS = {
  // The artboard paints both with --canvas (l.15): the window behind the cards (Herdr `canvas`)
  // and the centre card itself (.views l.258, Herdr `background` = the terminals' cards). Inside
  // the chat, every var(--canvas) is the card surface, so gentle-chat uses `background`.
  canvas: ["#000000", "canvas", "--canvas (Gentleman-Cute bg) l.15, behind the cards"],
  background: ["#000000", "background", "--canvas on .views l.258, the centre card surface"],
  chrome: ["#0B0B0B", "chrome", "--chrome (bgPanel) l.16"],
  surface: ["#1F1F1F", "surface", "--surface (system.md --surface) l.17"],
  raised: ["#2E2E2E", "raised", "--raised (system.md --surface-1) l.18"],
  user: ["#14161E", null, "--user (userMessageBg) l.19"],
  selected: ["#1E202D", "selected", "--selected (selection) l.20"],
  hover: ["#1E202D", "hover", "--selected is also the hover fill l.20"],
  line: ["#2E2E2E", "border", "--line (borderSubtle) l.21"],
  lineStrong: ["#6B6B6B", "input", "--line-strong (border) l.22"],
  text: ["#E6E6E6", "foreground", "--text l.23"],
  muted: ["#C7C7C7", "muted", "--muted l.24"],
  faint: ["#A7A7A7", "dim", "--faint l.25"],
  accent: ["#A5B4FC", "accent", "--accent l.26"],
  accentSoft: ["#D4B5FD", null, "--accent-soft l.27"],
  ok: ["#34D399", "done", "--ok l.28"],
  warn: ["#FBBF24", "blocked", "--warn l.29"],
  err: ["#FB8585", null, "--err l.30"],
  info: ["#7DD3FC", "working", "--info l.31"],
  onAccent: ["#000000", null, ".btn.primary / .send text l.94, l.183"],
  btnLine: ["#E6E6E617", null, ".btn border l.92"],
};

// What the layout's root `"colors"` sets so every role above shows the artboard value (T6).
// `popover` (menus) and the primary button roles have no token of their own here but the
// artboard fixes them too (l.107, l.94).
export const LAYOUT_COLORS = {
  ...Object.fromEntries(Object.values(TOKENS).filter(([, role]) => role).map(([hex, role]) => [role, hex])),
  popover: "#2E2E2E",
  accent_foreground: "#000000",
  solid: "#A5B4FC",
  solid_foreground: "#000000",
};

// The light appearance (S14): the same names, derived from design/system.md (no light artboard;
// herdr/FIDELITY-light.md has every value and its WCAG contrast). Same values as
// herdr/mods/gentle-tokens/tokens.js HEX_LIGHT.
const LIGHT = {
  canvas: "#F9F6F2",
  background: "#F9F6F2",
  chrome: "#F2EEE9",
  surface: "#FEFDFA",
  raised: "#EEE9E2",
  user: "#F0E8E0",
  selected: "#F1D7C2",
  hover: "#EEE9E2",
  line: "#E3DDD4",
  lineStrong: "#8E8479",
  text: "#1E1814",
  muted: "#5E574F",
  faint: "#645C53",
  accent: "#8B440C",
  accentSoft: "#A73B15",
  ok: "#1C6C31",
  warn: "#795700",
  err: "#A12623",
  info: "#125F94",
  onAccent: "#FEFDFA",
  btnLine: "#1E18141F",
};

// What herdr/themes/gentle-shell-light.json `colors` sets (the light LAYOUT_COLORS).
export const LIGHT_COLORS = {
  ...Object.fromEntries(Object.entries(TOKENS).filter(([, [, role]]) => role).map(([name, [, role]]) => [role, LIGHT[name]])),
  popover: "#FEFDFA",
  accent_foreground: "#FEFDFA",
  solid: "#8B440C",
  solid_foreground: "#FEFDFA",
  idle: "#5E574F",
  selection: "#8B440C33",
};

const isColor = (v) => typeof v === "string" && /^#[0-9a-fA-F]{3,8}$/.test(v);

// Whether Herdr shows the dark appearance now (settings().dark); dark when it does not say.
export function isDark() {
  try { return settings()?.dark !== false; } catch { return true; }
}

// The palette for one render: `t` is `theme()`.
export function palette(t) {
  const p = {};
  const dark = isDark();
  for (const [name, [hex, role]] of Object.entries(TOKENS)) {
    const own = dark ? hex : LIGHT[name];
    p[name] = role && isColor(t?.[role]) ? t[role] : own;
  }
  return p;
}

// `#rrggbb` + alpha (0..1) → `#rrggbbaa`, as the artboard's 8-digit hexes (`#e0c27a14`).
export function alpha(color, a) {
  const c = String(color);
  const six = /^#[0-9a-fA-F]{6}$/.test(c) ? c : /^#[0-9a-fA-F]{8}$/.test(c) ? c.slice(0, 7) : null;
  if (!six) return c;
  return six + Math.round(Math.max(0, Math.min(1, a)) * 255).toString(16).padStart(2, "0");
}

// Type: --sans / --mono stacks (l.32-33). The first installed family wins, like CSS.
const SANS = ["Inter", "SF Pro Text", "SF Pro", ".SystemUIFont"];
const MONO = ["IosevkaTerm NF", "Iosevka Term", "JetBrains Mono", "SF Mono", "Menlo"];
let installed = null;
function pick(stack) {
  if (!installed) {
    try { installed = new Set(fonts()); } catch { installed = new Set(); }
  }
  return stack.find((f) => installed.has(f)) ?? stack[stack.length - 1];
}
export const sans = () => pick(SANS);
export const mono = () => pick(MONO);

// Radii (l.34) and the window's own numbers.
export const R = { sm: 8, md: 12, lg: 16, pill: 999, inner: 6, kbd: 5, window: 10 };
