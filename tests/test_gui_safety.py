"""GUI renders data with textContent only (replaces the security reviewer's manual XSS sink check)."""
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
        for field in ("hd.scenario", "hd.leaveOut", "hd.skippedDrafts", ".dpsStat"):
            self.assertIn(field, text)

    def test_no_cancel_button(self) -> None:
        self.assertNotRegex(guide_script(), r'"Cancel"')


if __name__ == "__main__":
    unittest.main()
