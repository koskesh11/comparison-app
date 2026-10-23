"""Make every skill installed on this computer available in this project.

Links (Windows directory junctions, no admin needed) each skill folder from the known skill sources into
<project>/.claude/skills/<name>. Re-run after updating a source; it is idempotent.

Rules:
- A skill is a folder with a SKILL.md.
- Names already loaded elsewhere are skipped: user skills (~/.claude/skills) and Claude Code built-ins.
- When two sources have the same name, the earlier source in SOURCES wins.
- Only junctions this script created are replaced or removed; real folders are never touched.
- Linked names are written to .claude/skills/.gitignore (personal setup, not part of the shared repo).

Usage: python tools/link_skills.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
PROJECT = Path(__file__).resolve().parents[1]
TARGET = PROJECT / ".claude" / "skills"
MANIFEST = TARGET / ".linked.json"

# Order = precedence on name clashes.
SOURCES: list[tuple[str, Path]] = [
    ("superpowers", HOME / ".claude" / "plugins" / "superpowers" / "skills"),
    ("ecc", HOME / ".claude" / "plugins" / "ECC" / "skills"),
    ("agents (skills CLI)", HOME / ".agents" / "skills"),
    ("codex", HOME / ".codex" / "skills"),
    ("od-skills", HOME / "Desktop" / "Wabe GmbH" / ".od-skills"),
]
# Not linked on purpose: ~/.codex/vendor_imports (a cached copy of OpenAI's curated catalog, not installed;
# many need Codex-only tools) and Codex plugin skills (Codex app features such as pets, artifact templates).

# Codex-internal skills that need Codex's own tools.
SKIP_DIRS = {".system"}

# Claude Code built-in or bundled skill names: a project copy would shadow or be shadowed.
BUILTIN = {
    "security-review", "init", "simplify", "loop", "schedule", "run", "claude-api", "update-config",
    "keybindings-help", "fewer-permission-prompts", "plugin-authoring", "dataviz", "artifact-design",
    "artifact-diagramming", "artifact-capabilities",
}


def skill_dirs(root: Path) -> list[Path]:
    """Folders under root (up to 3 levels) that contain a SKILL.md; nested skills stop the descent."""
    found: list[Path] = []
    if not root.is_dir():
        return found

    def walk(d: Path, depth: int) -> None:
        for child in sorted(d.iterdir()):
            if not child.is_dir() or child.name in SKIP_DIRS or child.name.startswith("."):
                continue
            if (child / "SKILL.md").is_file():
                found.append(child)
            elif depth < 3:
                walk(child, depth + 1)

    walk(root, 1)
    return found


def frontmatter_name(skill: Path) -> str:
    """The `name:` from SKILL.md frontmatter, else the folder name (od-skills folders carry a hash)."""
    try:
        text = (skill / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return skill.name
    if text.startswith("---"):
        for line in text.splitlines()[1:40]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("\"'")
                if name:
                    return name
    return skill.name


def user_level_names() -> set[str]:
    root = HOME / ".claude" / "skills"
    return {p.name for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()} if root.is_dir() else set()


def is_junction(p: Path) -> bool:
    try:
        return p.is_junction() if hasattr(p, "is_junction") else bool(os.readlink(p))
    except OSError:
        return False


def make_junction(link: Path, target: Path) -> None:
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                            capture_output=True, encoding="oem", errors="replace")
    if result.returncode != 0:
        raise OSError(f"mklink failed for {link}: {result.stderr.strip() or result.stdout.strip()}")


def plan() -> tuple[dict[str, tuple[str, Path]], list[str]]:
    taken = user_level_names() | BUILTIN
    chosen: dict[str, tuple[str, Path]] = {}
    skipped: list[str] = []
    for label, root in SOURCES:
        for skill in skill_dirs(root):
            name = frontmatter_name(skill)
            if name in taken:
                skipped.append(f"{name} ({label}): already loaded at user level or built in")
            elif name in chosen:
                skipped.append(f"{name} ({label}): duplicate, kept {chosen[name][0]}")
            else:
                chosen[name] = (label, skill)
    return chosen, skipped


def main() -> int:
    dry = "--dry-run" in sys.argv
    chosen, skipped = plan()
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    if not dry:
        TARGET.mkdir(parents=True, exist_ok=True)

    removed = [n for n in previous if n not in chosen]
    for name in removed:
        link = TARGET / name
        if is_junction(link) and not dry:
            os.rmdir(link)  # removes the junction only, never the source

    created = 0
    for name, (label, src) in sorted(chosen.items()):
        link = TARGET / name
        if link.exists() or is_junction(link):
            if not is_junction(link):
                skipped.append(f"{name}: real folder in project, left untouched")
                continue
            if Path(os.path.realpath(link)) == Path(os.path.realpath(src)):
                continue
            if not dry:
                os.rmdir(link)
        if not dry:
            make_junction(link, src)
        created += 1

    if not dry:
        MANIFEST.write_text(json.dumps({n: str(s) for n, (_, s) in sorted(chosen.items())}, indent=1),
                            encoding="utf-8")
        ignore = ["# generated by tools/link_skills.py: personal skill links, not part of the repo",
                  ".gitignore", ".linked.json", *sorted(chosen)]
        (TARGET / ".gitignore").write_text("\n".join(ignore) + "\n", encoding="utf-8")

    by_source: dict[str, int] = {}
    for label, _ in chosen.values():
        by_source[label] = by_source.get(label, 0) + 1
    print(f"{'DRY RUN: ' if dry else ''}linked {len(chosen)} skills ({created} new/changed, "
          f"{len(removed)} removed): {by_source}")
    print(f"skipped {len(skipped)}:")
    for line in skipped:
        print("  -", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
