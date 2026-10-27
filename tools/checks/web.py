"""F9: browser code. Every .js file parses (`node --check`); no inline script, style or event handler in HTML.

The HTML sink test (tests/web/test_ui_safety.py, from the first app's test_gui_safety.py) comes with the web code.
"""

import re
import shutil
import subprocess
from pathlib import Path

from checks.common import WEB, Skip, files, rel

INLINE = {
    "inline script": re.compile(r"<script(?![^>]*\bsrc=)[^>]*>", re.IGNORECASE),
    "style element": re.compile(r"<style\b", re.IGNORECASE),
    "style attribute": re.compile(r"\sstyle\s*=", re.IGNORECASE),
    "event handler attribute": re.compile(r"\son[a-z]+\s*=", re.IGNORECASE),
}


def check(root: Path) -> list[str]:
    problems = []
    for path in files(root, (WEB,), "*.html"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            problems += [
                f"{rel(root, path)}:{number}: {label}" for label, pattern in INLINE.items() if pattern.search(line)
            ]
    scripts = list(files(root, (WEB,), "*.js"))
    if scripts and not shutil.which("node"):
        raise Skip("node is not installed")
    for path in scripts:
        result = subprocess.run(["node", "--check", str(path)], check=False, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            problems.append(f"{rel(root, path)}: {result.stderr.strip().splitlines()[0] if result.stderr else 'error'}")
    return problems
