"""F4: no hand-written file over 400 lines (decision 006); exemptions only for files we do not write, with a reason."""

import tomllib
from pathlib import Path

from checks.common import NEW_TESTS, NEW_TOOLS, SRC, WEB, files, rel

LIMIT = 400
SUFFIXES = {".py", ".lua", ".js", ".css", ".html"}
EXEMPTIONS = Path("tools/checks/size_exemptions.toml")


def exemptions(root: Path) -> tuple[dict[str, str], list[str]]:
    path = root / EXEMPTIONS
    if not path.exists():
        return {}, []
    entries = tomllib.loads(path.read_text(encoding="utf-8")).get("exempt", [])
    problems = [
        f"{EXEMPTIONS.as_posix()}: entry {entry.get('path', '?')} has no reason"
        for entry in entries
        if not str(entry.get("reason", "")).strip()
    ]
    return {entry["path"]: entry.get("reason", "") for entry in entries if "path" in entry}, problems


def check(root: Path) -> list[str]:
    exempt, problems = exemptions(root)
    for path in files(root, (SRC, *NEW_TESTS, WEB, *NEW_TOOLS), "*"):
        name = rel(root, path)
        if path.suffix not in SUFFIXES or name in exempt:
            continue
        count = len(path.read_text(encoding="utf-8").splitlines())
        if count > LIMIT:
            problems.append(f"{name}: {count} lines (limit {LIMIT}); split it, it does two jobs")
    return problems
