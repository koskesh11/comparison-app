"""Hand an implementation brief to Codex (gpt-5.6-sol, medium effort) via the Codex plugin's companion script.

  python tools/codex_task.py tasks/codex/<brief>.md            # write-capable run, waits for the result
  python tools/codex_task.py tasks/codex/<brief>.md --resume   # continue the previous Codex run
  python tools/codex_task.py tasks/codex/<brief>.md --read-only

Model and effort are fixed here so every coding agent uses the same Codex setup.
"""

import argparse
import subprocess
import sys
from pathlib import Path

CODEX_MODEL = "gpt-5.6-sol"
CODEX_EFFORT = "medium"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_CACHE = Path.home() / ".claude" / "plugins" / "cache" / "openai-codex" / "codex"


def companion_script() -> Path:
    """Newest installed version of the Codex plugin's companion script."""
    scripts = sorted(PLUGIN_CACHE.glob("*/scripts/codex-companion.mjs"),
                     key=lambda p: [int(x) if x.isdigit() else x for x in p.parent.parent.name.split(".")])
    if not scripts:
        sys.exit(f"Codex plugin not found under {PLUGIN_CACHE} (install/enable the openai-codex plugin)")
    return scripts[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("brief", type=Path, help="markdown brief for Codex (relative to the project root)")
    parser.add_argument("--resume", action="store_true", help="continue the last Codex run instead of starting fresh")
    parser.add_argument("--read-only", action="store_true", help="let Codex investigate without editing files")
    args = parser.parse_args()

    brief = (PROJECT_ROOT / args.brief).resolve()
    if PROJECT_ROOT not in brief.parents or not brief.is_file():
        sys.exit(f"brief must be an existing file inside {PROJECT_ROOT}")

    command = ["node", str(companion_script()), "task", "--model", CODEX_MODEL, "--effort", CODEX_EFFORT,
               "--cwd", str(PROJECT_ROOT), "--prompt-file", str(brief.relative_to(PROJECT_ROOT))]
    if not args.read_only:
        command.append("--write")
    command.append("--resume-last" if args.resume else "--fresh")
    sys.exit(subprocess.run(command, cwd=PROJECT_ROOT).returncode)


if __name__ == "__main__":
    main()
