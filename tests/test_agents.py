"""Agent files load: valid frontmatter, generated output in sync (replaces a manual orchestrator check)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
VALID_EFFORT = {"low", "medium", "high", "xhigh", "max"}


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise AssertionError(f"{path.name}: no frontmatter")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise AssertionError(f"{path.name}: frontmatter is not a mapping")
    return data


class AgentFilesTest(unittest.TestCase):
    def agent_files(self) -> list[Path]:
        return sorted(p for p in AGENTS.glob("*.md") if p.name != "README.md")

    def test_frontmatter_valid(self) -> None:
        files = self.agent_files()
        self.assertGreaterEqual(len(files), 30)
        for path in files:
            with self.subTest(agent=path.name):
                data = frontmatter(path)
                self.assertEqual(data.get("name"), path.stem)
                self.assertTrue(data.get("description"))
                if "effort" in data:
                    self.assertIn(data["effort"], VALID_EFFORT)

    def test_generator_reproduces_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, str(ROOT / "tools" / "make_agents.py"), tmp],
                           check=True, capture_output=True)
            generated = Path(tmp) / ".claude" / "agents"
            for path in self.agent_files() + [AGENTS / "README.md"]:
                with self.subTest(agent=path.name):
                    self.assertEqual(path.read_text(encoding="utf-8"),
                                     (generated / path.name).read_text(encoding="utf-8"),
                                     "agent file out of sync: run python tools/make_agents.py .")


if __name__ == "__main__":
    unittest.main()
