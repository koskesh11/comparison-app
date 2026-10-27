"""Point git at the repo's hooks (.githooks/): the fast checks run before every commit (decision 006).

python tools/install_hooks.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ".githooks"


def install(root: Path = ROOT) -> str:
    if not (root / HOOKS / "pre-commit").exists():
        raise SystemExit(f"{HOOKS}/pre-commit not found in {root}")
    subprocess.run(["git", "config", "core.hooksPath", HOOKS], cwd=root, check=True, timeout=60)
    return f"git now runs {HOOKS}/pre-commit (python tools/check.py) before every commit"


if __name__ == "__main__":
    print(install())
    sys.exit(0)
