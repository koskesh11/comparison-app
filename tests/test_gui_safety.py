"""GUI renders data with textContent only (replaces the security reviewer's manual XSS sink check)."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

GUI = Path(__file__).resolve().parents[1] / "gui" / "index.html"
SINKS = re.compile(r"\.innerHTML\b|\.outerHTML\b|insertAdjacentHTML|document\.write\s*\(|\beval\s*\(|new\s+Function\s*\(")
START = "// ---- guide check"
END = '$("gnav").addEventListener'
# words a player must never see (spec E4); matched inside string literals only
INTERNAL = re.compile(r"\b(sha|sha256|job|CompareTab|XML|import code)\b", re.IGNORECASE)
LITERAL = re.compile(r'"(?:[^"\\\n]|\\.)*"|`(?:[^`\\]|\\.)*`')


def page() -> str:
    return GUI.read_text(encoding="utf-8")


def guide_script() -> str:
    text = page()
    start, end = text.index(START), text.index(END)
    return text[start:end]


class GuiSafetyTest(unittest.TestCase):
    def test_no_html_sinks(self) -> None:
        hits = [f"index.html:{n}: {line.strip()}"
                for n, line in enumerate(page().splitlines(), 1)
                if SINKS.search(line)]
        self.assertEqual(hits, [], "use textContent / createElement instead:\n" + "\n".join(hits))

    def test_script_parses(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        script = re.search(r"<script>(.*)</script>", page(), re.S).group(1)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "page.js"
            path.write_text(script, encoding="utf-8")
            done = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


class GuideCheckViewTest(unittest.TestCase):
    def test_guide_view_exists(self) -> None:
        text = guide_script()
        for name in ("renderGuideInput", "renderGuideResult", "guidePoll", "schedulePreview", "saveCopy"):
            self.assertIn(f"function {name}", text)

    def test_guide_text_is_never_html_or_a_link(self) -> None:
        text = guide_script()
        self.assertIsNone(SINKS.search(text))
        self.assertNotIn("href", text)
        self.assertNotIn("setAttribute(\"on", text)
        # the only way to build elements is h(): attributes never come from guide data
        for attr in re.findall(r"""h\("[a-z0-9]+",\s*\{([^}]*)\}""", text):
            self.assertNotRegex(attr, r"\b(?:href|src|style|srcdoc)\b\s*:(?!\s*['\"])")

    def test_player_wording(self) -> None:
        bad = []
        for literal in LITERAL.findall(guide_script()):
            if literal.startswith('"/api') or literal.startswith('"jobId'):
                continue
            if INTERNAL.search(re.sub(r"\$\{[^}]*\}", "", literal)):
                bad.append(literal)
        self.assertEqual(bad, [], "internal words in player-facing strings")

    def test_numbers_are_null_safe(self) -> None:
        text = guide_script()
        for helper in ("gPct", "gBig", "gMargin", "gPlain", "gCell"):
            line = next(l for l in text.splitlines() if l.startswith(f"const {helper} ="))
            self.assertIn("Number.isFinite", line, helper)
        # no raw number formatting on row data
        self.assertNotRegex(text, r"\.toFixed\(|\.toLocaleString\(")
        for fn in ("detailLines", "numbersCell", "guideRow", "gotPreview"):
            self.assertRegex(text, rf"function {fn}\([^)]*\) \{{[^}}]*?\b(?:obj|arr)\(", fn)

    def test_guide_check_sends_the_same_drafts_checkbox_as_the_audit(self) -> None:
        """GATE 2 H3: the route defaults drafts to off, so the GUI must send the checkbox like the audit does."""
        text = page()
        audit_call = next(l for l in text.splitlines() if 'api("/api/audit"' in l)
        guide_call = next(l for l in text.splitlines() if 'api("/api/guide-check"' in l)
        self.assertIn('includeDrafts: $("drafts").checked', audit_call)
        self.assertIn('includeDrafts: $("drafts").checked', guide_call)
        self.assertEqual(1, text.count('id="drafts"'))

    def test_header_shows_the_settings_the_numbers_were_measured_with(self) -> None:
        text = guide_script()
        self.assertIn("pts.note", text)
        for field in ("hd.scenario", "hd.leaveOut", "hd.skippedDrafts", ".dpsStat"):
            self.assertIn(field, text)

    def test_no_cancel_button(self) -> None:
        self.assertNotRegex(guide_script(), r'"Cancel"')


if __name__ == "__main__":
    unittest.main()


# ---- real render of the guide view in node, with a minimal stub DOM ------------------------------
REPORT = Path(__file__).resolve().parent / "fixtures" / "guide_report_ek.json"
HARNESS = r"""
class Node { constructor() { this.children = []; this.attrs = {}; this.handlers = {}; this.className = ""; this.parent = null; }
  append(...c) { for (const x of c) { x.parent = this; this.children.push(x); } }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  getAttribute(k) { return this.attrs[k] ?? null; }
  addEventListener(k, f) { this.handlers[k] = f; }
  replaceChildren(...c) { this.children = []; this.append(...c); }
  replaceWith() {} focus() {} click() { this.clicked = true; if (this.handlers.change) this.handlers.change({ target: this }); }
  get isConnected() { return false; }
  get classList() { return { add() {}, remove() {}, toggle() {}, contains: () => false }; }
  get textContent() { return this.text !== undefined ? this.text : this.children.map((c) => c.textContent).join(" "); }
  set textContent(v) { this.text = String(v); this.children = []; }
  all(tag) { return this.children.flatMap((c) => [...(c.tag === tag ? [c] : []), ...(c.all ? c.all(tag) : [])]); }
  find(pred) { return this.children.flatMap((c) => [...(pred(c) ? [c] : []), ...(c.find ? c.find(pred) : [])]); } }
class Text extends Node { constructor(t) { super(); this.text = String(t); } }
class El extends Node { constructor(tag) { super(); this.tag = tag; } }
const ids = {};
global.Node = Node;
global.document = { createElement: (t) => new El(t), createTextNode: (t) => new Text(t),
  getElementById: (id) => (ids[id] ||= new El("div")), addEventListener() {} };
global.window = global; global.fetch = async () => ({ ok: false, json: async () => ({}) });
global.localStorage = { getItem: () => null, setItem() {} };
"""
HARNESS_RUN = r"""
const input = JSON.parse(require("fs").readFileSync(0, "utf8"));
const out = {};
renderGuideResult(input.report);
out.main = ids.main.textContent;
out.a = G.groups.a ? G.groups.a.textContent : "";
out.b = G.groups.b.textContent; out.bRows = G.groups.b.all("li").length;
out.c = G.groups.c.textContent;
out.locked = ids.main.find((n) => n.tag === "span" && n.className === "lock").map((n) => n.attrs["aria-label"]);
const box = ids.main.find((n) => n.tag === "input" && n.attrs.type === "checkbox")[0];
let prevented = false;
if (box.handlers.keydown) box.handlers.keydown({ key: "Enter", target: box, preventDefault() { prevented = true; } });
out.enter = { clicked: box.clicked === true, prevented };
out.fmt = input.fmt.map(([v, d]) => fmtNum(v, d));
out.fmtSigned = [fmtNum(-0, 1, { sign: true }), fmtNum(NaN, 1), fmtNum(Infinity, 1), fmtNum(null, 1)];
process.stdout.write(JSON.stringify(out));
"""


def run_render(report: dict, fmt: list | None = None) -> dict:
    node = shutil.which("node")
    if node is None:
        raise unittest.SkipTest("node is not installed")
    text = page()
    script = re.search(r"<script>(.*)</script>", text, re.S).group(1)
    script = script[: script.index(END)]
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "render.js"
        path.write_text(HARNESS + script + HARNESS_RUN, encoding="utf-8")
        done = subprocess.run([node, str(path)], input=json.dumps({"report": report, "fmt": fmt or []}),
                              capture_output=True, text=True, timeout=60)
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


class GuideRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_real_report_renders_every_group(self) -> None:
        rep = self.report
        out = run_render(rep)
        for name in ("main", "a", "b", "c"):
            for bad in ("[object", "undefined", "NaN", "null"):
                self.assertNotIn(bad, out[name], f"{bad!r} in {name}")
            # the EK report has no real tiny loss, so a "-0.0" / "-0.1" would be float noise shown as a loss
            self.assertNotRegex(out[name], r"-0\.[01]", name)
        labels = [r["label"] for r in rep["notTested"]]
        self.assertEqual(len(labels), 63)
        for label in labels:
            self.assertIn(label, out["c"])
        self.assertTrue(any(r["reason"] in out["c"] for r in rep["notTested"] if r.get("reason")))
        for r in rep["rows"] + rep["noChange"]:
            self.assertIn(r["label"], out["a"])
        self.assertEqual((len(rep["rows"]), len(rep["noChange"])), (65, 8))
        self.assertEqual(out["bRows"], len(rep["config"]))
        self.assertEqual(out["bRows"], 15)

    def test_not_tested_row_shows_reason(self) -> None:
        rep = json.loads(json.dumps(self.report))
        rep["notTested"].append({"category": "unique", "chips": ["not tested"], "detail": "Mageblood detail line",
                                 "id": "x:1", "label": "Mageblood", "reason": "You wear Mageblood", "result": None})
        out = run_render(rep)
        self.assertIn("You wear Mageblood", out["c"])
        self.assertIn("Mageblood detail line", out["c"])
        self.assertIn("not tested", out["c"])
        self.assertNotIn("[object", out["c"])

    def test_locked_row_has_aria_label_and_enter_toggles(self) -> None:
        rep = json.loads(json.dumps(self.report))
        rep["rows"][0]["locked"] = True
        rep["rows"][0]["lockReason"] = "Needs a free socket"
        rep["rows"][1]["locked"] = True
        rep["rows"][1]["lockReason"] = ""
        out = run_render(rep)
        self.assertIn("Can't be applied: Needs a free socket", out["locked"])
        self.assertIn("Can't be applied", out["locked"])
        self.assertEqual(out["enter"], {"clicked": True, "prevented": True})

    def test_numbers_round_down(self) -> None:
        cases = [(-41.578, 1), (41.578, 1), (7.5757, 1), (0, 1), (-0, 1), (0.29999999999, 1), (-0.0001, 1), (1234.5, 0), (-1e-12, 1), (1e-12, 1)]
        out = run_render(self.report, cases)
        # PoE rounds down: negatives go toward -infinity, so -0.0001 shows -0.1 (user decision)
        self.assertEqual(out["fmt"], ["-41.6", "41.5", "7.5", "0.0", "0.0", "0.3", "-0.1", "1,234", "0.0", "0.0"])
        self.assertEqual(out["fmtSigned"], ["0.0", "n/a", "n/a", "n/a"])
