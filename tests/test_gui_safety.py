"""GUI renders data with textContent only (replaces the security reviewer's manual XSS sink check)."""
import re
import unittest
from pathlib import Path

GUI = Path(__file__).resolve().parents[1] / "gui" / "index.html"
SINKS = re.compile(r"\.innerHTML\b|\.outerHTML\b|insertAdjacentHTML|document\.write\s*\(|\beval\s*\(|new\s+Function\s*\(")


class GuiSafetyTest(unittest.TestCase):
    def test_no_html_sinks(self) -> None:
        hits = [f"index.html:{n}: {line.strip()}"
                for n, line in enumerate(GUI.read_text(encoding="utf-8").splitlines(), 1)
                if SINKS.search(line)]
        self.assertEqual(hits, [], "use textContent / createElement instead:\n" + "\n".join(hits))


if __name__ == "__main__":
    unittest.main()
