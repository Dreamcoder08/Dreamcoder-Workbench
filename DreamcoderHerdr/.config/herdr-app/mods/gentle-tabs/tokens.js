// Gentle Shell Desktop design tokens and the small pieces every gentle-* mod draws the same way.
// Source of truth: design/herdr-desktop/01-inspector.html (`:root` and the BASE rules).
//
// CANONICAL COPY. gpui-shell refuses imports outside a mod's own folder ("Module `../x.js`
// resolves outside the application directory"), so every gentle-* mod carries a byte-identical
// copy of this file as `./tokens.js`. Edit it here, then copy it to: gentle-sidebar, gentle-spaces,
// gentle-agents, gentle-tabs, gentle-inspector, gentle-status, gentle-palette, gentle-tokens and
// gentle-pane (see herdr/FIDELITY-T6.md); gentle-chat has its own tokens.js.
//
// Colours (S14): the layout's root `"theme": { "light": "gentle-shell-light", "dark":
// "gentle-shell-dark" }` (herdr/themes/*.json) sets the Herdr theme roles to the palette of the
// appearance Herdr shows (the system's, or settings.json `appearance`), so `theme()` names come
// first and follow a theme pick; HEX (dark, the artboard) and HEX_LIGHT (herdr/FIDELITY-light.md)
// are the fallback and the home of the colours that have no Herdr role, picked by `settings().dark`.

import { div, svg } from "gpui-kit";
import { h_flex } from "gpui-base";
import { theme, fonts, settings } from "herdr";

// The artboard palette (01-inspector.html :root, lines 15-31): the dark appearance.
export const HEX = {
  canvas: "#000000", // --canvas → canvas (behind cards) and background (inside the centre card)
  chrome: "#0B0B0B", // --chrome → chrome
  surface: "#1F1F1F", // --surface → surface
  raised: "#2E2E2E", // --raised → raised
  user: "#14161E", // --user (no role)
  selected: "#1E202D", // --selected → selected / hover
  line: "#2E2E2E", // --line → border
  lineStrong: "#6B6B6B", // --line-strong → input
  text: "#E6E6E6", // --text → foreground
  muted: "#C7C7C7", // --muted → muted
  faint: "#A7A7A7", // --faint → dim
  accent: "#A5B4FC", // --accent → accent
  accentSoft: "#D4B5FD", // --accent-soft (no role)
  ok: "#34D399", // --ok → done
  warn: "#FBBF24", // --warn → blocked
  err: "#FB8585", // --err (no role)
  info: "#7DD3FC", // --info → working
  onAccent: "#000000", // .btn.primary color → accent_foreground
  btnLine: "#E6E6E617", // .btn border (no role)
};
const DARK = HEX;

// The light palette (S14), in the same names: derived from design/system.md (no light artboard),
// every text colour WCAG AA on canvas, chrome and selected (herdr/FIDELITY-light.md). Mirrors
// herdr/themes/gentle-shell-light.json `colors`.
export const HEX_LIGHT = {
  canvas: "#F9F6F2",
  chrome: "#F2EEE9",
  surface: "#FEFDFA",
  raised: "#EEE9E2",
  user: "#F0E8E0",
  selected: "#F1D7C2",
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

// Whether Herdr shows the dark appearance now (settings().dark); dark when it does not say.
export function isDark() {
  try { return settings()?.dark !== false; } catch { return true; }
}

// Fonts: the --sans / --mono stacks (01-inspector.html lines 32-33); the first installed family
// wins, as in CSS (same stacks as herdr/mods/gentle-chat/tokens.js). Inter is not installed on the
// reference machine, so the artboard renders in the system UI font: GPUI's ".SystemUIFont".
const SANS_STACK = ["Inter", "SF Pro Text", "SF Pro", ".SystemUIFont"];
const MONO_STACK = ["IosevkaTerm NF", "Iosevka Term", "JetBrains Mono", "SF Mono", "Menlo"];
function pick(stack) {
  let installed;
  try { installed = new Set(fonts()); } catch { installed = new Set(); }
  return stack.find((f) => installed.has(f)) ?? stack[stack.length - 1];
}
export const sans = () => pick(SANS_STACK);
export const mono = () => pick(MONO_STACK);
const fontsOnce = () => {
  let installed;
  try { installed = new Set(fonts()); } catch { installed = new Set(); }
  const first = (stack) => stack.find((f) => installed.has(f)) ?? stack[stack.length - 1];
  return { sans: first(SANS_STACK), mono: first(MONO_STACK) };
};

// The palette with the live theme roles first, and the two font families (read once per call).
export function tokens() {
  const t = theme() ?? {};
  const f = fontsOnce();
  const HEX = isDark() ? DARK : HEX_LIGHT;
  return {
    sans: f.sans,
    mono: f.mono,
    canvas: t.canvas ?? HEX.canvas, // behind the cards (window, work body, active tab)
    card: t.background ?? HEX.canvas, // inside the centre card (chat, terminal): Herdr "background"
    chrome: t.chrome ?? HEX.chrome,
    surface: t.surface ?? HEX.surface,
    raised: t.raised ?? HEX.raised,
    user: HEX.user,
    selected: t.selected ?? HEX.selected,
    hover: t.hover ?? HEX.selected,
    line: t.border ?? HEX.line,
    lineStrong: t.input ?? HEX.lineStrong,
    text: t.foreground ?? HEX.text,
    muted: t.muted ?? HEX.muted,
    faint: t.dim ?? HEX.faint,
    accent: t.accent ?? HEX.accent,
    accentSoft: HEX.accentSoft,
    onAccent: t.accent_foreground ?? HEX.onAccent,
    ok: t.done ?? HEX.ok,
    warn: t.blocked ?? HEX.warn,
    err: HEX.err,
    info: t.working ?? HEX.info,
    btnLine: HEX.btnLine,
  };
}

// ---- Pieces ----------------------------------------------------------------------------------

// .eyebrow: 600 11px/1.4 mono, uppercase, muted (letter-spacing .1em: GPUI has none).
export function eyebrow(c, text, color) {
  return div().font_family(c.mono).font_weight(600).text_size(11).line_height("15.4px").text_color(color ?? c.muted).child(String(text).toUpperCase());
}

// .state: a 7px dot (idle: a 5px ring, queue: a dashed ring) and a 12px label in the state colour.
// kind: work | need | done | idle | fail | queue. `label` may be empty (a tab shows only the dot).
export const STATE_COLOR = { work: "info", need: "warn", done: "ok", idle: "muted", fail: "err", queue: "muted" };
export function stateDot(c, kind) {
  const color = c[STATE_COLOR[kind] ?? "muted"];
  if (kind === "idle") return div().size(8).flex_none().rounded(4).border(1.5).border_color(color);
  if (kind === "queue") return div().size(8).flex_none().rounded(4).border(1.5).border_dashed().border_color(color);
  // The artboard pulses a working dot (opacity 1 → .35, 1.6s). Not here (S13, herdr/PERF.md): any
  // native animation redraws the whole window every frame while it is drawn, and one pulsing dot
  // kept Herdr app at ≈40 % CPU for as long as a session worked. The dot and its word say it.
  return div().size(7).flex_none().rounded(4).bg(color);
}
export function state(c, kind, label, extra) {
  let el = h_flex().gap(6).items_center().flex_none().whitespace_nowrap().text_size(12).line_height("18px")
    .text_color(c[STATE_COLOR[kind] ?? "muted"]).child(stateDot(c, kind));
  if (label) el = el.child(String(label));
  if (extra) el = el.child(extra);
  return el;
}

// .bar: 4px pill track (raised) with a fill (muted, or accent / info / ok). pct 0..100.
export function bar(c, pct, tone) {
  const p = Math.max(0, Math.min(100, Number(pct) || 0));
  return div().h(4).flex_1().min_w(40).rounded(999).bg(c.raised).overflow_hidden()
    .child(div().h_full().w(`${p}%`).rounded(999).bg(tone ? c[tone] : c.muted));
}

// .btn: 5px 10px, radius 8, 1px #ffffff17 border, 12px muted; .primary: accent fill, #1a1218 600;
// .danger: hover goes err. `icon`: an svg path drawn at 13px before the label.
export function btn(c, id, label, opts = {}) {
  const { primary, danger, icon, onClick } = opts;
  let el = h_flex().id(id).flex_none().gap(6).items_center().px(10).py(5).rounded(8).border(1).text_size(12).line_height("18px").whitespace_nowrap().cursor_pointer();
  if (primary) el = el.bg(c.accent).border_color(c.accent).text_color(c.onAccent).font_weight(600);
  else el = el.border_color(c.btnLine).text_color(c.muted).hover((s) => (danger ? s.border_color(c.err).text_color(c.err) : s.border_color(c.accent).text_color(c.accentSoft)));
  if (icon) el = el.child(svg(icon).size(13).flex_none());
  el = el.child(String(label));
  if (onClick) el = el.on_click(onClick);
  return el;
}

// kbd: 0 5px, 1px line-strong border, radius 5, 11px muted mono. An inline box is as tall as
// the font's content area: 13.5 + 2 × 1 = 15.5 (measured in the render).
export function kbd(c, text) {
  return div().flex_none().px(5).rounded(5).border(1).border_color(c.lineStrong).font_family(c.mono).text_size(11).line_height("13.5px").text_color(c.muted).child(text);
}

// A session's kind (snapshot.js SESSION_KINDS: Herdr, TUI) as a small labelled badge: its own icon
// (`mods/<mod>/icons/<kind.icon>.svg`, carried by every mod that shows it) and its word in the
// kbd's mono look, so the kind never rests on colour alone. Herdr reads in the info tone, TUI in
// the accent-soft tone.
// A remote session (S14) shows its machine's name instead of the word, in the warn tone, and says
// in its tooltip that its feed stays on that machine. `machine`: the name, for remote only.
export function kindBadge(c, kind, mod, machine) {
  const tone = kind.kind === "herdr" ? c.info : kind.kind === "remote" ? c.warn : c.accentSoft;
  const label = kind.kind === "remote" && machine ? machine : kind.label;
  const remote = kind.kind === "remote";
  return h_flex().flex_none().h(17).px(5).gap(4).items_center().rounded(5).border(1).border_color(c.lineStrong)
    .font_family(c.mono).font_weight(600).text_size(10.5).line_height("13.5px").text_color(tone)
    .when(remote, (el) => el.max_w(120).overflow_hidden())
    .tooltip(remote && machine ? `${kind.about} (${machine})` : kind.about)
    .child(svg(`mods/${mod}/icons/${kind.icon}.svg`).size(11).flex_none())
    .child(remote ? div().min_w(0).truncate().child(label) : label);
}

// ---- Formats ---------------------------------------------------------------------------------

// $3.42, $0.49 (the artboard always shows cents).
export function money(n) {
  const v = Number(n);
  return Number.isFinite(v) ? `$${v.toFixed(2)}` : "$0.00";
}

// A session's own spend as its TUI footer writes it (lib/shell-bar.ts formatCost): $33.46 from a
// dollar up, $0.247 below (S10: the same value the TUI shows). Sums keep money()'s cents.
export function sessionCost(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "$0.000";
  return `$${v >= 1 ? v.toFixed(2) : v.toFixed(3)}`;
}

// 41m, 3m 12s, 41s, 1h 05m.
export function span(ms) {
  const s = Math.max(0, Math.round((Number(ms) || 0) / 1000));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return s % 60 && m < 10 ? `${m}m ${s % 60}s` : `${m}m`;
  const h = Math.floor(m / 60);
  return `${h}h ${String(m % 60).padStart(2, "0")}m`;
}

// 0:42, 12:09 (a job's elapsed time).
export function clock(ms) {
  const s = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}` : `${m}:${String(r).padStart(2, "0")}`;
}

// "2 min ago", "just now", "3 h ago".
export function ago(ms, now = Date.now()) {
  const s = Math.max(0, Math.floor((now - Number(ms)) / 1000));
  if (!Number.isFinite(s) || s < 45) return "just now";
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  return h < 48 ? `${h} h ago` : `${Math.round(h / 24)} d ago`;
}

// "in 2h 10m" until a reset time (ms epoch), or "" when unknown.
export function until(at, now = Date.now()) {
  if (at === null || at === undefined || !Number.isFinite(Number(at))) return "";
  const s = Math.floor((Number(at) - now) / 1000);
  if (s <= 0) return "now";
  const m = Math.round(s / 60), h = Math.floor(m / 60), d = Math.floor(h / 24);
  if (d > 0) return `in ${d}d ${h % 24}h`;
  if (h > 0) return `in ${h}h ${m % 60}m`; // "in 2h 10m" (artboard l.355)
  return `in ${Math.max(1, m)}m`;
}

// A usage window's short label: "week" → "7d" (the artboard's 5h / 7d).
export const windowLabel = (w) => (w?.label === "week" ? "7d" : String(w?.label ?? ""));

// A Gentle Shell terminal's own title without pi's "π - " prefix: "π - herdr-gentle-shell" →
// "herdr-gentle-shell". The fallback name when a session has no name (the artboard names tabs
// and agents by session).
export const sessionTitle = (title) => String(title ?? "").replace(/^\s*π\s*[-–—·:]?\s*/u, "").trim();

// "claude-bridge/claude-opus-5-5" → "Opus 5.5" (the artboard's model names); anything else as
// given, without its provider. Same rule as gentle-chat/feed.js prettyModel.
export function prettyModel(id) {
  if (typeof id !== "string" || !id) return null;
  const bare = id.slice(id.lastIndexOf("/") + 1);
  const m = /^claude-([a-z]+)-(\d+)(?:-(\d+))?/.exec(bare);
  if (!m) return bare;
  return `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}${m[3] ? `.${m[3]}` : ""}`;
}

// A subagent's role tag: the agent name without the "gentle-ai-" / "gentle-" prefix
// ("gentle-ai-worker" → "worker"), as the chat's subagent card.
export const agentRole = (name) => String(name ?? "agent").replace(/^gentle-ai-/, "").replace(/^gentle-/, "");

// The sentence-case word for a phase: "implementing" → "Implementing".
export const cap = (s) => (s ? String(s).charAt(0).toUpperCase() + String(s).slice(1) : "");
