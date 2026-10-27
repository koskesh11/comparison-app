"""F12: tracked text files are stored with LF (.gitattributes); only files marked -text or eol=crlf may differ."""

import re
from pathlib import Path

from checks.common import git

ENTRY = re.compile(r"^(?P<index>i/\S*)\s+(?P<work>w/\S*)\s+attr/(?P<attr>.*?)\s*$")


def check(root: Path) -> list[str]:
    problems = []
    for entry in git(root, "ls-files", "--eol", "-z").split("\0"):
        info, _, name = entry.partition("\t")
        match = ENTRY.match(info)
        if not match or match["index"] not in ("i/crlf", "i/mixed"):
            continue
        attr = match["attr"]
        if attr == "-text" or "eol=crlf" in attr:
            continue
        problems.append(
            f"{name}: stored with {match['index'][2:]} line endings (attributes: '{attr or 'none'}'); "
            "run `git add --renormalize .` or mark it in .gitattributes with a reason"
        )
    return problems
