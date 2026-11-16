import { View, div } from "gpui-kit";
import { v_flex, h_flex, InputState, Input, TextView } from "gpui-base";
import { closeOverlay, exec, focused, panes, props, spaces, theme } from "herdr";
import {
  localFolder,
  parseProjects,
  projectsRequest,
  requestFor,
  resolveProject,
  resultFor,
  rowsFor,
  shortDate,
  snippet,
  typeTone,
} from "./recall.js";

function location() {
  const space = spaces().find((s) => s.active), f = focused();
  const pane = f?.pane ? panes().find((p) => p.pane === f.pane) : null;
  return { space, cwd: pane?.cwd || f?.cwd || space?.folder };
}

export default class EngramRecall extends View {
  init(_props, cx) {
    this.handle = cx.focus_handle(); this.sequence = 0; this.query = "";
    this.rows = []; this.open = null;
    this.input = InputState.new({ placeholder: "Search project memories…" });
    this.input.on("change", (_e, cx) => { this.query = this.input.value(); this.sequence++; cx.notify(); });
    this.input.on("submit", (_e, cx) => this.load(cx));
    this.input.focus();
    this.load(cx);
  }

  close() { this.sequence++; closeOverlay(props()?.overlay); }

  load(cx) {
    const { space, cwd } = location(), folder = localFolder(space, cwd);
    const sequence = ++this.sequence, query = this.query.trim();
    this.project = null; this.rows = []; this.open = null;
    if (!folder) {
      this.message = space?.machine ? "Recall is unavailable for remote spaces." : "No local project folder is focused.";
      cx.notify(); return;
    }
    this.message = "Loading…"; cx.notify();
    cx.spawn(async (cx) => {
      let message = "", project = null, rows = null;
      try {
        project = resolveProject(folder, parseProjects(await exec("curl", projectsRequest())));
        if (!project) {
          message = `Engram has no project for ${folder}.`;
        } else {
          const answer = await exec("curl", requestFor(project, query));
          rows = query ? rowsFor(answer) : null;
          message = rows ? (rows.length ? "" : "No results for this project.") : resultFor(query, answer);
        }
      } catch { message = "Engram is offline or the request failed."; }
      if (sequence !== this.sequence) return;
      this.project = project; this.rows = rows || []; this.message = message; cx.notify();
    });
  }

  row(r, t) {
    const expanded = this.open === r.id;
    return v_flex().id(`engram-row-${r.id}`).gap(3).px(9).py(6).rounded(7).cursor_pointer()
      .hover((s) => s.bg(t.hover))
      .on_click((_e, cx) => { this.open = expanded ? null : r.id; cx.notify(); })
      .child(h_flex().gap(8).items_center()
        .child(div().flex_none().w(84).text_size(10.5).text_color(t[typeTone(r.type)]).child(r.type))
        .child(div().flex_1().min_w(0).truncate().text_size(12.5).text_color(t.foreground).child(r.title))
        .child(div().flex_none().text_size(10.5).text_color(t.dim).child(shortDate(r.created))))
      .when(expanded, (el) => el.child(div().p(8).child(TextView.markdown(`engram-md-${r.id}`, r.content).selectable(true).scrollable(false))))
      .when(!expanded, (el) => el.child(div().text_size(11.5).text_color(t.muted).truncate().child(snippet(r.content))));
  }

  render() {
    const t = theme();
    return v_flex().id("dc-engram").track_focus(this.handle)
      .on_key_down((e, cx) => { if (e.key === "escape") { this.close(); cx.stop_propagation(); } })
      .w_full().h(400).p(18).gap(12).bg(t.popover).text_color(t.foreground)
      .child(h_flex().items_center()
        .child(div().flex_1().text_size(15).font_semibold().child("Engram recall"))
        .child(div().text_size(11).text_color(t.dim).child(`${this.project || "No project"} · Enter · Esc`)))
      .child(Input.new(this.input).h(36).px(10).rounded(9).border_1().border_color(t.accent).bg(t.background).text_size(12.8).text_color(t.foreground))
      .child(v_flex().id("engram-results").flex_1().min_h(0).overflow_y_scrollbar()
        .when(this.rows.length > 0, (el) => el.children(this.rows.map((r) => this.row(r, t))))
        .when(this.rows.length === 0, (el) =>
          el.child(TextView.markdown("engram-markdown", this.message || ""))));
  }
}
