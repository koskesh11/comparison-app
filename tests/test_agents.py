"""Agent files load: valid frontmatter, generated output in sync, and rule hygiene (task 028).

Rule hygiene (tasks 028, 029): every rule unit in the prompt text of tools/make_agents.py (all uppercase string
constants except README, found automatically, plus every agent body) is a top-level bullet or a whole numbered
list; a list of output formats opts out with a `<!-- not-a-rule: reason -->` line right before it. Each unit carries a source tag
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
# Uppercase string constants of tools/make_agents.py that are documentation, not agent prompt text. Everything else
# (a new prompt constant too) is checked without being listed anywhere.
NOT_PROMPT = ("README",)
TAG_RE = re.compile(r'\((user|orchestrator), (\d{4}-\d{2}-\d{2})(?:, task (\d{3}))?'
                    r'(?:, supersedes: "([^"]+)")?\)')
UNTIL_RE = re.compile(r"\buntil\b(?! task \d{3} done)", re.IGNORECASE)
# other ways to say a rule is temporary; they must be written as `until task NNN done` too
TEMPORARY_RE = re.compile(r"\b(for now|temporar(?:y|ily)|while|once|until further notice)\b", re.IGNORECASE)
UNTIL_TASK_RE = re.compile(r"\buntil task (\d{3}) done", re.IGNORECASE)


NOT_A_RULE_RE = re.compile(r"^<!-- not-a-rule: \S.* -->$")
NUMBERED_RE = re.compile(r"^\d+\. ")


def rule_units(text: str) -> list[str]:
    """Rule units: a top-level bullet ("- " at column 0) or a whole numbered list ("1. " ...), each with its
    indented continuation lines. A list right after a `<!-- not-a-rule: reason -->` line is skipped."""
    units: list[list[str]] = []
    kind, skipping = "", False  # kind of the open unit: "bullet", "number" or ""
    for line in text.splitlines():
        if NOT_A_RULE_RE.match(line.strip()):
            kind, skipping = "", True
        elif line.startswith("- ") or NUMBERED_RE.match(line):
            now = "bullet" if line.startswith("- ") else "number"
            if not skipping and not (now == "number" and kind == "number"):
                units.append([])
            if not skipping:
                units[-1].append(line)
            kind = now
        elif kind and line.startswith((" ", "\t")) and line.strip():
            if not skipping:
                units[-1].append(line)
        else:
            kind, skipping = "", False  # blank line, heading or plain paragraph ends the list
    return ["\n".join(u) for u in units]


def prompt_texts(module) -> dict[str, str]:
    """Every text the agents get: uppercase string constants (found by scan) and each agent body."""
    texts = {name: value for name, value in vars(module).items()
             if name.isupper() and isinstance(value, str) and name not in NOT_PROMPT}
    texts.update({f"body of {agent[0]}": agent[5] for agent in module.AGENTS})
    return texts


def read_repo_file(path: str) -> str | None:
    target = ROOT / path
    return target.read_text(encoding="utf-8") if target.exists() else None


def backlog_problems(module, read=read_repo_file) -> list[str]:
    """product-lead's backlog names draft vault values awaiting the user; each note must still say draft."""
    problems = []
    for label, path in module.BACKLOG_DRAFTS.items():
        note = read(path)
        if note is None:
            problems.append(f"backlog '{label}': {path} does not exist")
        elif not re.search(r"^status:\s*draft\b|draft value", note, re.MULTILINE):
            problems.append(f"backlog '{label}' is stale: {path} is no longer a draft (status, or 'draft value' "
                            "in the text); drop it from BACKLOG_DRAFTS")
    return problems


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


# A tool named as something to call: "SendMessage(to: ...)" or "via SendMessage" (not "the WebFetch tool is ...").
TOOL_MENTION = re.compile(r"\b(SendMessage|WebFetch|WebSearch|Agent|Edit|Write)\((?=\w)"
                          r"|(?<=\bvia )(SendMessage|WebFetch|WebSearch)\b")

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

    def test_prompts_only_name_tools_the_agent_has(self) -> None:
        """A rule that tells an agent to call a tool it lacks can never be followed (task 029)."""
        for path in self.agent_files():
            data = frontmatter(path)
            if "tools" not in data:  # no tools line = all tools
                continue
            own = {t.strip() for t in str(data["tools"]).split(",")}
            body = path.read_text(encoding="utf-8").split("---", 2)[2]
            for name in sorted({a or b for a, b in TOOL_MENTION.findall(body)} - own):
                with self.subTest(agent=path.name, tool=name):
                    self.fail(f"{path.name} tells the agent to use {name}, but its tools are {sorted(own)}")

    def test_effort_floors(self) -> None:
        """User 2026-10-25: every Sonnet agent runs at effort high or above, every Haiku agent at xhigh."""
        floors = {"claude-sonnet-5-5": {"high", "xhigh", "max"}, "claude-haiku-5-5": {"xhigh"}}
        for path in self.agent_files():
            data = frontmatter(path)
            allowed = floors.get(data.get("model"))
            if allowed:
                with self.subTest(agent=path.name):
                    self.assertIn(data.get("effort"), allowed, f"{path.name}: effort below the user's floor")


class RuleHygieneTest(unittest.TestCase):
    """Checks on the real prompts, then fail-before cases on small bad fixtures."""

    def real_bullets(self) -> list[str]:
        return [u for text in prompt_texts(load_make_agents()).values() for u in rule_units(text)]

    def test_every_real_rule_is_tagged_and_unexpired(self) -> None:
        bullets = self.real_bullets()
        self.assertGreaterEqual(len(bullets), 40)
        problems = [p for b in bullets for p in rule_problems(b)]
        self.assertEqual(problems, [])

    def test_no_superseded_text_survives(self) -> None:
        module = load_make_agents()
        prompt = "\n".join(prompt_texts(module).values()) + module.README
        self.assertEqual(superseded_problems(self.real_bullets(), prompt), [])

    def test_product_lead_backlog_drafts_are_still_drafts(self) -> None:
        module = load_make_agents()
        self.assertGreaterEqual(len(module.BACKLOG_DRAFTS), 3)
        self.assertEqual(backlog_problems(module), [])
        body = next(a[5] for a in module.AGENTS if a[0] == "product-lead")
        for label in module.BACKLOG_DRAFTS:
            self.assertIn(label, body)

    def test_markers_are_not_in_the_generated_files(self) -> None:
        for path in AGENTS.glob("*.md"):
            self.assertNotIn("not-a-rule", path.read_text(encoding="utf-8"), path.name)

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
        bullets = rule_units("## Rules\n- Do X.\n  more words\n- Do Y. (user, 2026-10-24)\n")
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

    def test_numbered_list_is_one_unit_and_needs_a_tag(self) -> None:
        text = "## Modes\n1. First thing\n   more\n2. Second thing\n\nplain paragraph\n"
        units = rule_units(text)
        self.assertEqual(len(units), 1)
        self.assertEqual(len(rule_problems(units[0])), 1)
        tagged = text.replace("Second thing\n", "Second thing (user, 2026-10-24)\n")
        self.assertEqual(rule_problems(rule_units(tagged)[0]), [])

    def test_format_list_marker_exempts_exactly_that_list(self) -> None:
        text = ("Produce a map:\n<!-- not-a-rule: output format -->\n- part one\n- part two\n\n"
                "- a real rule. (user, 2026-10-24)\n- an untagged rule\n")
        self.assertEqual([u.splitlines()[0] for u in rule_units(text)],
                         ["- a real rule. (user, 2026-10-24)", "- an untagged rule"])
        self.assertEqual(len(rule_units(text.replace("<!-- not-a-rule: output format -->\n", ""))), 4)

    def test_new_prompt_constant_and_agent_body_are_found_without_a_list(self) -> None:
        class Fake:  # a make_agents stand-in: one new constant, one agent body, two non-prompt names
            NEW_NOTE = "- rule without a tag"
            README = "- docs"
            lower = "- not a constant"
            AGENTS = [("x", "lead", "", "D", "desc", "- body rule without a tag")]
        texts = prompt_texts(Fake)
        self.assertEqual(sorted(texts), ["NEW_NOTE", "body of x"])
        self.assertEqual(sum(len(rule_problems(u)) for t in texts.values() for u in rule_units(t)), 2)

    def test_stale_backlog_item_is_caught(self) -> None:
        class Fake:
            BACKLOG_DRAFTS = {"A rule": "vault/a.md", "B model": "vault/b.md", "C gone": "vault/c.md"}
        notes = {"vault/a.md": "---\nstatus: draft\n---", "vault/b.md": "---\nstatus: verified\n---"}
        problems = backlog_problems(Fake, notes.get)
        self.assertEqual(len(problems), 2)
        self.assertTrue("B model" in problems[0] and "C gone" in problems[1])

    def test_lesson_cap_is_caught(self) -> None:
        many = "# L\n" + "- lesson\n" * (MAX_ACTIVE_LESSONS + 1)
        self.assertEqual(active_lessons(many), MAX_ACTIVE_LESSONS + 1)
        self.assertEqual(active_lessons(many + "## Promoted\n- old one\n"), MAX_ACTIVE_LESSONS + 1)
        self.assertEqual(active_lessons("# L\n## Promoted\n- a\n- b\n"), 0)


if __name__ == "__main__":
    unittest.main()
