// The status bar, with the work-unit budget beside it: authored changed lines
// on the focused branch (additions plus deletions) against its base, red past
// 400. The branch, machine and agent count stay as the shipped bar showed them.
import { View, div, svg } from "gpui-kit";
import { h_flex } from "gpui-base";
import { spaces, panes, focused, agents, exec, readTextFile, theme, run, window, keys, props } from "herdr";
import { BASES, READ, REVIEWABLE_LINES, budget, countLines, label, parseLog, parseNumstat, parseStatus } from "./budget.js";

const REFRESH_MS = 15000;

// The focused place to measure: its pane folder on this machine, or the space's
// folder on another one. Same rule the shipped Changes and Files panels use.
function location() {
  const space = spaces().find((s) => s.active), f = focused();
  const pane = f?.pane ? panes().find((p) => p.pane === f.pane) : null;
  const on = f?.pane === null ? (f.terminal?.includes("/") ? f.terminal.split("/")[0] : null) : space?.machine ?? null;
  return { cwd: pane?.cwd || f?.cwd || space?.folder, on };
}

export default class Status extends View {
  init(_props, cx) {
    this.context = null;
    this.value = null;
    this.slices = [];
    this.busy = false;
    this.refresh(cx);
    cx.timer.every(REFRESH_MS, (cx) => this.refresh(cx));
  }

  // The branch base this repo works from, or null when it has none of them.
  async base(git) {
    for (const candidate of BASES) {
      const r = await git(["rev-parse", "--verify", "--quiet", candidate]);
      if (r.code === 0) return candidate;
    }
    return null;
  }

  refresh(cx) {
    const { cwd, on } = location(), context = JSON.stringify({ cwd, on });
    if (context !== this.context) {
      this.context = context;
      this.value = null;
      this.slices = [];
    }
    if (!cwd || this.busy) return;
    this.busy = true;
    cx.spawn(async (cx) => {
      try {
        const git = (args) => exec("git", [...READ, ...args], { cwd, on });
        const top = await git(["rev-parse", "--show-toplevel"]);
        if (top.code !== 0) return;
        const root = top.stdout.trim();
        const inRoot = (args) => exec("git", [...READ, ...args], { cwd: root, on });
        if ((await inRoot(["rev-parse", "--verify", "HEAD"])).code !== 0) return;
        const base = await this.base(inRoot);
        if (!base) return;

        // Committed on the branch since it forked, then everything not committed yet.
        const committed = parseNumstat((await inRoot(["diff", "--numstat", "-z", "--no-renames", `${base}...HEAD`])).stdout);
        const dirty = parseNumstat((await inRoot(["diff", "HEAD", "--numstat", "-z", "--no-renames"])).stdout);
        // Untracked files carry no numstat: count their lines so a new file is not free.
        let fresh = 0;
        for (const entry of parseStatus((await inRoot(["status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all"])).stdout)) {
          if (entry.xy !== "??") continue;
          const text = await readTextFile(`${root}/${entry.path}`, { on }).catch(() => null);
          if (text && !text.includes("\0")) fresh += countLines(text);
        }

        const value = budget([committed, dirty, { add: fresh, del: 0 }]);
        value.base = base;
        this.value = value;
        this.slices = parseLog((await inRoot(["log", "--numstat", "--no-renames", "--format=__C__%h %s", `${base}..HEAD`])).stdout);
      } catch {
        this.value = null;
        this.slices = [];
      } finally {
        this.busy = false;
        cx.notify();
      }
    });
  }

  // The palette key as actually bound, not a hardcoded one.
  hint(t) {
    const mac = window()?.platform === "macos";
    const mod = { cmd: mac ? "⌘" : "Ctrl+", ctrl: mac ? "⌃" : "Ctrl+", shift: mac ? "⇧" : "Shift+", alt: mac ? "⌥" : "Alt+", option: mac ? "⌥" : "Alt+" };
    const b = keys().find((k) => k.section === "global" && k.action === "app.palette");
    const parts = b && b.keys.endsWith("--") ? [...b.keys.slice(0, -2).split("-"), "-"] : b?.keys.split("-");
    const key = parts && parts.map((p) => mod[p.toLowerCase()] ?? p.toUpperCase()).join("");
    return key ? `${key}  commands` : "commands";
  }

  tip(value, slices) {
    const head = `${value.base}...HEAD · ${value.lines} authored lines (additions plus deletions)`;
    const rule = `Work-unit budget: ${REVIEWABLE_LINES}`;
    if (!slices.length) return `${head}\n${rule}`;
    const rows = slices.map((c) => `${c.add + c.del > REVIEWABLE_LINES ? "!" : " "} ${c.short} · +${c.add} \u2212${c.del}`);
    return [head, rule, "", ...rows].join("\n");
  }

  chip(t) {
    const value = this.value;
    if (!value || value.lines === 0) return null;
    const over = value.over;
    return h_flex()
      .id("budget")
      .gap(5)
      .items_center()
      .tooltip(this.tip(value, this.slices))
      .child(div().text_color(over ? t.blocked : t.muted).child(label(value)))
      .child(div().text_color(over ? t.blocked : t.dim).child(`/ ${REVIEWABLE_LINES}`));
  }

  render(cx) {
    // A space switch must show its own repo at once, not on the next tick.
    if (JSON.stringify(location()) !== this.context) this.refresh(cx);

    const t = theme();
    const space = spaces().find((s) => s.active);
    const list = agents();
    const needs = list.filter((a) => a.status === "blocked").length;
    const part = (icon, text) => h_flex().gap(6).items_center().child(svg(`mods/workspace-chrome/${icon}.svg`).size(13)).child(text);
    const chip = this.chip(t);
    // compact: only the budget chip, for a bar that already shows branch and machine (gentle-shell).
    if (props()?.compact === true) {
      return h_flex().size_full().px(10).items_center().justify_end().bg(t.chrome).border_t(1).border_color(t.border)
        .text_size(11.8).when(Boolean(chip), (el) => el.child(chip));
    }
    return h_flex()
      .size_full()
      .px(14)
      .gap(16)
      .items_center()
      .bg(t.chrome)
      .border_t(1)
      .border_color(t.border)
      .text_size(11.8)
      .text_color(t.muted)
      .child(part(space?.machine ? "server" : "monitor", space?.machine ?? "This computer"))
      .when(Boolean(space?.branch), (el) => el.child(part("branch", space.branch)))
      .child(h_flex().gap(6).items_center().child(div().size(6).rounded(3).bg(t.dim)).child(`${list.length} agents`)
        .when(needs > 0, (el) => el.child(div().text_color(t.blocked).child(`· ${needs} needs you`))))
      .when(Boolean(chip), (el) => el.child(chip))
      .child(div().flex_1())
      .child(div().id("palette").text_color(t.dim).on_click(() => run("app.palette")).child(this.hint(t)));
  }
}
