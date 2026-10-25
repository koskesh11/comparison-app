"""Agent files load: valid frontmatter, generated output in sync, and rule hygiene (task 028).

Rule hygiene: every rule bullet in the prompt sections of tools/make_agents.py carries a source tag
`(user|orchestrator, YYYY-MM-DD[, task NNN][, supersedes: "old text"])`; a conditional rule says
`until task NNN done` and fails once that task is done; a `supersedes:` text must be gone from the prompts;
a learnings file has at most MAX_ACTIVE_LESSONS active lessons (bullets outside "## Promoted"/"## Retired").
"""
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
VALID_EFFORT = {"low", "medium", "high", "xhigh", "max"}
TASKS = ROOT / "tasks"
LEARNINGS = ROOT / "docs" / "studio" / "learnings"
MAX_ACTIVE_LESSONS = 30
# Prompt constants in tools/make_agents.py whose top-level bullets are rules/facts and need a source tag.
RULE_CONSTANTS = ("FACTS", "LEAD_NOTE", "SPECIALIST_NOTE", "LEARNING_LEAD", "LEARNING_SPECIALIST",
                  "CODEX_NOTE", "ORCHESTRATOR_BODY")
TAG_RE = re.compile(r'\((user|orchestrator), (\d{4}-\d{2}-\d{2})(?:, task (\d{3}))?'
                    r'(?:, supersedes: "([^"]+)")?\)')
UNTIL_RE = re.compile(r"\buntil\b(?! task \d{3} done)", re.IGNORECASE)
# other ways to say a rule is temporary; they must be written as `until task NNN done` too
TEMPORARY_RE = re.compile(r"\b(for now|temporar(?:y|ily)|while|once|until further notice)\b", re.IGNORECASE)
UNTIL_TASK_RE = re.compile(r"\buntil task (\d{3}) done", re.IGNORECASE)


def rule_bullets(text: str) -> list[str]:
    """Top-level bullets ("- " at column 0) with their indented continuation lines."""
    bullets: list[list[str]] = []
    open_bullet = False
    for line in text.splitlines():
        if line.startswith("- "):
            bullets.append([line])
            open_bullet = True
        elif open_bullet and line.startswith((" ", "\t")) and line.strip():
            bullets[-1].append(line)
        else:
            open_bullet = False  # blank line, heading or plain paragraph ends the bullet
    return ["\n".join(b) for b in bullets]


def task_status(number: str) -> str | None:
    """Status of tasks/NNN-*.md, None when the task file does not exist."""
    for path in sorted(TASKS.glob(f"{number}-*.md")):
        match = re.search(r"^status:\s*(\w+)", path.read_text(encoding="utf-8"), re.MULTILINE)
        return match.group(1) if match else None
    return None


def rule_problems(bullet: str, status_of=task_status) -> list[str]:
    """Why a rule bullet breaks the hygiene rules (empty list = fine)."""
    head = bullet.splitlines()[0][:70]
    tag = TAG_RE.search(bullet)
    if not tag:
        return [f"no source tag (user|orchestrator, YYYY-MM-DD[, task NNN]): {head}"]
    problems = []
    origin = tag.group(3)
    if origin and status_of(origin) is None:
        problems.append(f"tag names task {origin} but tasks/{origin}-*.md does not exist: {head}")
    untagged = TAG_RE.sub("", bullet)
    if UNTIL_RE.search(untagged) or TEMPORARY_RE.search(untagged):
        problems.append(f"conditional rule must say 'until task NNN done': {head}")
    for number in UNTIL_TASK_RE.findall(untagged):
        state = status_of(number)
        if state is None:
            problems.append(f"expiry task {number} does not exist: {head}")
        elif state == "done":
            problems.append(f"expired: task {number} is done, remove or change the rule: {head}")
    return problems


def superseded_problems(bullets: list[str], prompt_text: str) -> list[str]:
    """A `supersedes: "text"` tag is broken while that text still stands in the prompts."""
    haystack = TAG_RE.sub("", prompt_text)
    problems = []
    for bullet in bullets:
        for tag in TAG_RE.finditer(bullet):
            old = tag.group(4)
            if old and old in haystack:
                problems.append(f"supersedes \"{old}\" but that text still exists in the prompts")
    return problems


def active_lessons(markdown: str) -> int:
    """Lesson bullets outside the "## Promoted" / "## Retired" sections."""
    count, settled = 0, False
    for line in markdown.splitlines():
        if line.startswith("#"):
            settled = bool(re.match(r"#+\s*(promoted|retired)\b", line, re.IGNORECASE))
        elif line.startswith("- ") and not settled:
            count += 1
    return count


def load_make_agents():
    spec = importlib.util.spec_from_file_location("make_agents_under_test", ROOT / "tools" / "make_agents.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


class RuleHygieneTest(unittest.TestCase):
    """Checks on the real prompts, then fail-before cases on small bad fixtures."""

    def real_bullets(self) -> list[str]:
        module = load_make_agents()
        return [b for name in RULE_CONSTANTS for b in rule_bullets(getattr(module, name))]

    def test_every_real_rule_is_tagged_and_unexpired(self) -> None:
        bullets = self.real_bullets()
        self.assertGreaterEqual(len(bullets), 25)
        problems = [p for b in bullets for p in rule_problems(b)]
        self.assertEqual(problems, [])

    def test_no_superseded_text_survives(self) -> None:
        module = load_make_agents()
        prompt = "\n".join(str(getattr(module, n)) for n in RULE_CONSTANTS)
        prompt += "\n".join(agent[5] for agent in module.AGENTS) + module.README
        self.assertEqual(superseded_problems(self.real_bullets(), prompt), [])

    def test_learnings_files_stay_small(self) -> None:
        files = sorted(LEARNINGS.glob("*.md"))
        self.assertGreaterEqual(len(files), 5)
        for path in files:
            with self.subTest(file=path.name):
                n = active_lessons(path.read_text(encoding="utf-8"))
                self.assertLessEqual(n, MAX_ACTIVE_LESSONS,
                                     f"{n} active lessons: merge duplicates, move promoted ones under '## Promoted'")

    # ---- fail-before fixtures: each check must catch its own break ----
    def test_missing_tag_is_caught(self) -> None:
        bullets = rule_bullets("## Rules\n- Do X.\n  more words\n- Do Y. (user, 2026-10-24)\n")
        self.assertEqual(len(bullets), 2)
        self.assertEqual(len(rule_problems(bullets[0])), 1)
        self.assertEqual(rule_problems(bullets[1]), [])

    def test_expired_rule_is_caught(self) -> None:
        statuses = {"004": "done", "019": "doing"}
        bullet = "- No meta tasks until task 004 done. (user, 2026-10-22)"
        self.assertEqual(len(rule_problems(bullet, statuses.get)), 1)
        self.assertEqual(rule_problems(bullet.replace("004", "019"), statuses.get), [])
        self.assertEqual(len(rule_problems(bullet.replace("004", "777"), statuses.get)), 1)

    def test_conditional_rule_must_name_a_task(self) -> None:
        self.assertEqual(len(rule_problems("- No meta tasks until P1 is done. (user, 2026-10-22)", {}.get)), 1)

    def test_other_temporary_wordings_are_caught(self) -> None:
        for phrase in ("for now", "temporarily", "while the pilot runs", "once P1 is done", "until further notice"):
            with self.subTest(phrase=phrase):
                bullet = f"- Budget is relaxed {phrase}. (user, 2026-10-24)"
                self.assertEqual(len(rule_problems(bullet, {}.get)), 1)
        ok = "- Relaxed until task 019 done. (user, 2026-10-24)"
        self.assertEqual(rule_problems(ok, {"019": "doing"}.get), [])

    def test_tag_task_must_exist(self) -> None:
        self.assertEqual(len(rule_problems("- Do X. (user, 2026-10-22, task 004)", {}.get)), 1)

    def test_superseded_text_is_caught(self) -> None:
        bullets = ['- Parallel. (user, 2026-10-25, task 028, supersedes: "at most 2 per dispatch")']
        self.assertEqual(len(superseded_problems(bullets, "keep it at most 2 per dispatch")), 1)
        self.assertEqual(superseded_problems(bullets, "parallel when independent"), [])
        # the tag's own quote must not count as "still exists"
        self.assertEqual(superseded_problems(bullets, bullets[0]), [])

    def test_lesson_cap_is_caught(self) -> None:
        many = "# L\n" + "- lesson\n" * (MAX_ACTIVE_LESSONS + 1)
        self.assertEqual(active_lessons(many), MAX_ACTIVE_LESSONS + 1)
        self.assertEqual(active_lessons(many + "## Promoted\n- old one\n"), MAX_ACTIVE_LESSONS + 1)
        self.assertEqual(active_lessons("# L\n## Promoted\n- a\n- b\n"), 0)


if __name__ == "__main__":
    unittest.main()
