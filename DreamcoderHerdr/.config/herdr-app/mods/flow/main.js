// Flow metrics for the focused repo over the last 14 days, from gh:
// merged PRs per week, open-to-merge lead time, and PR size vs the 400-line rule.
// Measure instead of trusting the feeling of speed.
import { View, div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { spaces, panes, focused, exec, theme, nextCommand, home } from "herdr";
import { duration, flowStats, parseGhJson } from "./stats.js";

const DAYS = 14;
const REFRESH_MS = 10 * 60000;
const FIELDS = "number,title,url,createdAt,mergedAt,additions,deletions";

function location() {
  const space = spaces().find((s) => s.active), f = focused();
  const pane = f?.pane ? panes().find((p) => p.pane === f.pane) : null;
  return { cwd: pane?.cwd || f?.cwd || space?.folder, on: space?.machine ?? null };
}

export default class Flow extends View {
  init(_props, cx) {
    this.stats = null; this.slowest = []; this.error = null; this.repo = null;
    this.refresh(cx);
    cx.timer.every(REFRESH_MS, (cx) => this.refresh(cx));
    cx.timer.every(5000, (cx) => { if (JSON.stringify(location()) !== this.context) this.refresh(cx); });
    cx.spawn(async (cx) => { for (;;) if ((await nextCommand()) === "refresh") this.refresh(cx); });
  }

  refresh(cx) {
    if (this.busy) return;
    const { cwd, on } = location();
    if (!cwd) return;
    this.context = JSON.stringify({ cwd, on });
    this.busy = true; cx.notify();
    cx.spawn(async (cx) => {
      try {
        const top = await exec("git", ["rev-parse", "--show-toplevel"], { cwd, on });
        if (top.code !== 0) { this.stats = null; this.repo = null; this.error = `Not a git repository: ${cwd.replace(home(), "~")}`; return; }
        const root = top.stdout.trim();
        this.repo = root.split("/").pop();
        const since = new Date(Date.now() - DAYS * 86400_000).toISOString().slice(0, 10);
        const r = await exec("gh", ["pr", "list", "--state", "merged", "--search", `merged:>=${since}`, "--limit", "200", "--json", FIELDS], { cwd: root, on });
        if (r.code !== 0) { this.error = r.stderr.trim().split("\n")[0] || "gh pr list failed"; return; }
        const prs = parseGhJson(r.stdout);
        this.stats = flowStats(prs, Date.now(), DAYS);
        this.slowest = prs.filter((p) => p.mergedAt)
          .map((p) => ({ ...p, leadH: (Date.parse(p.mergedAt) - Date.parse(p.createdAt)) / 3600_000 }))
          .sort((a, b) => b.leadH - a.leadH).slice(0, 5);
        this.error = null;
      } catch (e) {
        this.error = String(e?.message || e);
      } finally { this.busy = false; cx.notify(); }
    });
  }

  tile(t, id, label, value, note, alert = false) {
    return v_flex().id(id).flex_1().min_w(0).p(10).gap(2).rounded(8).bg(t.raised).border_1().border_color(alert ? t.blocked : t.border)
      .child(div().text_size(11).text_color(t.dim).child(label))
      .child(div().text_size(20).font_semibold().text_color(alert ? t.blocked : t.foreground).child(value))
      .child(div().text_size(11).text_color(t.muted).truncate().child(note));
  }

  render(cx) {
    const t = theme(), s = this.stats;
    const header = h_flex().gap(8).px(10).h(36).flex_none().items_center().border_b(1).border_color(t.border)
      .child(div().font_semibold().text_color(t.foreground).child("Flow"))
      .child(div().flex_1().min_w(0).truncate().text_color(t.dim).child(`${this.repo ?? ""} · last ${DAYS} days`))
      .child(div().id("flow-refresh").flex_none().px(6).rounded(5).cursor_pointer().text_color(this.busy ? t.dim : t.accent)
        .hover((st) => st.bg(t.hover)).tooltip("Refresh").on_click((_e, cx) => this.refresh(cx)).child(this.busy ? "…" : "⟳"));
    const body = v_flex().id("flow-body").flex_1().min_h(0).p(10).gap(10).overflow_y_scrollbar()
      .when(Boolean(this.error), (el) => el.child(div().text_color(t.blocked).child(this.error)))
      .when(Boolean(s) && !this.error, (el) => el
        .child(h_flex().gap(8)
          .child(this.tile(t, "flow-merged", "Merged", String(s.merged), `${s.perWeek} per week`))
          .child(this.tile(t, "flow-lead", "Lead time", duration(s.leadMedianH), `median · p90 ${duration(s.leadP90H)}`)))
        .child(h_flex().gap(8)
          .child(this.tile(t, "flow-size", "PR size", s.sizeMedian == null ? "—" : `±${Math.round(s.sizeMedian)}`, "median changed lines"))
          .child(this.tile(t, "flow-over", "Over 400", `${Math.round(s.overShare * 100)}%`, "of merged PRs", s.overShare > 0.25)))
        .child(div().pt(4).text_size(11).text_color(t.dim).child("Slowest to merge"))
        .children(this.slowest.map((p) => h_flex().id(`flow-pr-${p.number}`).gap(8).px(6).h(26).items_center().rounded(6).cursor_pointer()
          .hover((st) => st.bg(t.hover)).on_click((_e, cx) => { try { cx.open_url(p.url); } catch { exec("xdg-open", [p.url]).catch(() => {}); } })
          .child(div().flex_none().w(44).text_color(t.dim).child(`#${p.number}`))
          .child(div().flex_1().min_w(0).truncate().text_color(t.foreground).child(p.title))
          .child(div().flex_none().text_color(t.muted).child(duration(p.leadH))))));
    return v_flex().id("flow").size_full().bg(t.surface).text_size(12.5).child(header).child(body);
  }
}
