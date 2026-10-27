"""F10: every mechanics note parses: front matter with `type` and `status: draft | verified`; a Rules or Models note
has exactly one fenced block of its kind. A broken note fails here, not when a loader first reads it."""

import re
from pathlib import Path

from checks.common import MECHANICS, rel

STATUSES = {"draft", "verified"}
ONE_BLOCK = {"Rules": "rule", "Models": "model"}
SKIP_FOLDERS = {"_templates", ".obsidian"}
FIELD = re.compile(r"^([A-Za-z_]\w*):\s*(.*?)\s*$")


def front_matter(text: str) -> dict[str, str] | None:
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return None
    fields = {}
    for line in lines[1 : lines.index("---", 1)]:
        if match := FIELD.match(line):
            fields[match.group(1)] = match.group(2)
    return fields


def check_note(root: Path, path: Path) -> list[str]:
    name, text = rel(root, path), path.read_text(encoding="utf-8")
    fields = front_matter(text)
    if fields is None:
        return [f"{name}: no front matter (--- ... ---) at the top"]
    problems = []
    if not fields.get("type"):
        problems.append(f"{name}: front matter has no `type`")
    if fields.get("status") not in STATUSES:
        problems.append(f"{name}: status is '{fields.get('status')}', expected draft or verified")
    kind = ONE_BLOCK.get(path.parent.name)
    if kind and len(re.findall(rf"^```{kind}\s*$", text, re.MULTILINE)) != 1:
        problems.append(f"{name}: needs exactly one ```{kind} block")
    return problems


def check(root: Path) -> list[str]:
    folder = root / MECHANICS
    if not folder.exists():
        return [f"{MECHANICS.as_posix()}/ not found (the notes folder, decision 013)"]
    problems = []
    for path in sorted(folder.rglob("*.md")):
        parts = path.relative_to(folder).parts
        if len(parts) > 1 and not SKIP_FOLDERS & set(parts):
            problems += check_note(root, path)
    return problems
