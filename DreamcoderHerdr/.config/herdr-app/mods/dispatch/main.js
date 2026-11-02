// Dispatch: type a task, pick a role, launch an agent with that task, by
// default in a fresh worktree (made by the `hwt` fish function). Roles other
// than Claude Code come from ~/.config/herdr-core/templates. Enter launches,
// Esc closes. Opened with `mod.open:dispatch`.
import { View, div } from "gpui-kit";
import { v_flex, h_flex, InputState, Input } from "gpui-base";
import { agents, closeOverlay, exec, focused, home, notify, panes, props, readTextFile, run, spaces, theme } from "herdr";
import { branchFor, ceilingWarning, launchFor } from "./plan.js";

const ROLES = [
  { id: "claude", label: "Claude Code", worktree: true },
  { id: "explorer", label: "Explorer", worktree: false },
  { id: "reviewer", label: "Reviewer", worktree: false },
  { id: "verifier", label: "Verifier", worktree: false },
];

function location() {
  const space = spaces().find((s) => s.active), f = focused();
  const pane = f?.pane ? panes().find((p) => p.pane === f.pane) : null;
  return { space, cwd: pane?.cwd || f?.cwd || space?.folder };
}

export default class Dispatch extends View {
  init(_props, cx) {
    this.task = ""; this.role = ROLES[0]; this.worktree = this.role.worktree; this.busy = false;
    this.input = InputState.new({ placeholder: "What should the agent do?" });
    this.input.on("change", (_e, cx) => { this.task = this.input.value(); cx.notify(); });
    this.input.on("submit", (_e, cx) => this.launch(cx));
    this.input.focus();
    cx.timer.after(600, () => this.input.focus());
    this.handle = cx.focus_handle();
  }

  close() { closeOverlay(props()?.overlay); }

  launch(cx) {
    const task = this.task.trim();
    if (!task || this.busy) return;
    const { space, cwd } = location();
    if (!space || !cwd) return notify({ title: "Dispatch: no folder", level: "warning" });
    if (space.machine) return notify({ title: "Dispatch runs on this computer only", body: space.name, level: "warning" });
    this.busy = true; cx.notify();
    const role = this.role, worktree = this.worktree;
    cx.spawn(async (cx) => {
      try {
        const template = role.id === "claude" ? null : await readTextFile(`${home()}/.config/herdr-core/templates/${role.id}.md`);
        const plan = launchFor(role.id, template, task);
        const top = await exec("git", ["rev-parse", "--show-toplevel"], { cwd });
        let folder = top.code === 0 ? top.stdout.trim() : cwd, name = role.label;
        if (worktree) {
          if (top.code !== 0) throw new Error("A worktree needs a git repository");
          const branch = branchFor(task);
          // The branch is [a-z0-9/-] only, so single quotes are safe for fish.
          const r = await exec("fish", ["-c", `hwt -n '${branch}'`], { cwd: folder });
          if (r.code !== 0) throw new Error(r.stderr.trim().split("\n").pop() || `hwt exited ${r.code}`);
          folder = r.stdout.trim().split("\n").pop(); name = branch;
        }
        const warning = ceilingWarning(agents().filter((a) => a.status === "working").length);
        if (warning) notify({ title: "Squad at its ceiling", body: warning, level: "warning" });
        this.close();
        run("tab.new", { name, folder, argv: plan.argv, task: plan.task });
      } catch (e) {
        notify({ title: "Dispatch failed", body: String(e?.message || e), level: "error" });
      } finally { this.busy = false; cx.notify(); }
    });
  }

  render() {
    const t = theme();
    const chip = (r) => {
      const on = r.id === this.role.id;
      return h_flex().id(`role-${r.id}`).h(28).px(10).items_center().rounded(7).cursor_pointer().text_size(12)
        .border_1().border_color(on ? t.accent : t.input).bg(on ? t.selected : t.raised).text_color(on ? t.foreground : t.muted)
        .hover((s) => s.bg(t.hover))
        .on_click((_e, cx) => { this.role = r; this.worktree = r.worktree; cx.notify(); })
        .child(r.label);
    };
    const target = this.worktree ? `new worktree · ${branchFor(this.task)}` : "current folder";
    return v_flex().id("dispatch").track_focus(this.handle)
      .on_key_down((e, cx) => { if (e.key === "escape") { this.close(); cx.stop_propagation(); } })
      .w_full().min_h(0).p(18).gap(12).bg(t.popover).text_color(t.foreground)
      .child(h_flex().items_center()
        .child(div().flex_1().text_size(15).font_semibold().child("Dispatch an agent"))
        .child(div().text_size(11).text_color(t.dim).child("Enter · Esc")))
      .child(Input.new(this.input).h(36).px(10).rounded(9).border_1().border_color(t.accent).bg(t.background).text_size(12.8).text_color(t.foreground))
      .child(h_flex().gap(6).children(ROLES.map(chip)))
      .child(h_flex().gap(8).items_center()
        .child(h_flex().id("worktree-toggle").gap(6).items_center().cursor_pointer()
          .on_click((_e, cx) => { this.worktree = !this.worktree; cx.notify(); })
          .child(div().size(14).rounded(4).border_1().border_color(this.worktree ? t.accent : t.input).bg(this.worktree ? t.accent : t.background))
          .child(div().text_size(12).text_color(t.muted).child("New worktree")))
        .child(div().flex_1().min_w(0).truncate().text_size(11.5).text_color(t.dim).child(this.busy ? "Launching…" : target)));
  }
}
