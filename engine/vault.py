"""Read rule notes from the Obsidian vault: frontmatter + one ```rule``` block each."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

VAULT_DIR = Path(__file__).resolve().parent.parent / "vault"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
RULE_BLOCK = re.compile(r"```rule\n(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class Rule:
    name: str
    status: str
    kind: str
    spec: dict


def load_rules(vault_dir: Path = VAULT_DIR) -> list[Rule]:
    rules = []
    for path in sorted((vault_dir / "Rules").glob("*.md")):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        front, block = FRONTMATTER.match(text), RULE_BLOCK.search(text)
        if not front or not block:
            raise ValueError(f"{path.name}: needs frontmatter and a ```rule block")
        meta = yaml.safe_load(front.group(1)) or {}
        rules.append(Rule(path.stem, meta.get("status", "draft"), meta.get("kind", ""), yaml.safe_load(block.group(1)) or {}))
    return rules


GAP_BLOCK = re.compile(r"```gap\n(.*?)```", re.DOTALL)


def load_gap_patterns(vault_dir: Path = VAULT_DIR) -> list[dict]:
    """Mod patterns PoB can't value. Applied regardless of status: they only prevent false 'wasted' flags."""
    patterns = []
    for path in sorted((vault_dir / "Gaps").glob("*.md")):
        block = GAP_BLOCK.search(path.read_text(encoding="utf-8").replace("\r\n", "\n"))
        if block:
            patterns += (yaml.safe_load(block.group(1)) or {}).get("patterns") or []
    return patterns


def load_scenarios(vault_dir: Path = VAULT_DIR) -> dict[str, dict]:
    """Scenario notes (fight assumptions) by name; frontmatter holds pob_config etc."""
    scenarios = {}
    for path in sorted((vault_dir / "Scenarios").glob("*.md")):
        front = FRONTMATTER.match(path.read_text(encoding="utf-8").replace("\r\n", "\n"))
        if front:
            scenarios[path.stem] = yaml.safe_load(front.group(1)) or {}
    return scenarios
