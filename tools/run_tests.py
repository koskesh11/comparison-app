"""Impact-selected, parallel test runner (task 024).

    python tools/run_tests.py                 # tests affected by the changed files (+ safety tests)
    python tools/run_tests.py --all           # every tests/test_*.py, in parallel
    python tools/run_tests.py --files engine/costs.py gui/index.html   # select as if these changed
    python tools/run_tests.py --list          # only print the selection and why

Changed files = git diff vs the merge-base with main (committed + uncommitted tracked) + untracked files.
Mapping: Python import graph (incl. imports inside functions) from every test file to the modules it reaches,
plus rules for non-Python inputs (Lua, GUI, vault, agents, hooks, golden.json). One subprocess per test file
(`python -m unittest tests.<module>`), longest files first, PoB-heavy files limited by CPU and free memory.
Standard library only. Exit code is non-zero if any file fails.
"""
from __future__ import annotations

import argparse
import ast
import ctypes
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAFETY_TESTS = ("test_gui_safety", "test_guard_readonly", "test_agents")
GOLDEN_TEST = "test_golden"
POB_MODULE = "pobhost"        # a test that reaches this module loads PoB's lua51.dll in-process
VAULT_MODULE = "vault"
IGNORED_PREFIXES = ("vault/.obsidian/",)   # Obsidian window state, not vault content
CODE_DIRS = ("engine", "tests", "tools", "tools/hooks")
MAX_WORKERS = 12              # total parallel test processes (16 CPU threads leave room for the OS)
MAX_HEAVY_WORKERS = 8          # PoB-loading processes at once
HEAVY_MB = 700                # per PoB-loading test process: Lua heap up to ~195 MB, x2-3 engines in some tests
LIGHT_MB = 120
MEM_FRACTION = 0.6            # use at most this share of the free RAM
TAIL_LINES = 40
SPLIT_AFTER_S = 40            # a file measured longer than this runs as one job per TestCase class
JOB_TIMEOUT_S = 900           # a hung file is killed and reported as failed
GUI_PATTERN = re.compile(r"""["']gui["']|index\.html""")


@dataclass
class Job:
    module: str                       # tests.test_x
    heavy: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class Result:
    job: Job
    seconds: float
    returncode: int
    tests: int
    skipped: int
    tail: str


# ---------------------------------------------------------------- git: changed files

def _git(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return [line.strip() for line in out.stdout.splitlines() if line.strip()] if out.returncode == 0 else []


def changed_files() -> list[str]:
    base = (_git("merge-base", "HEAD", "main") or ["HEAD"])[0]
    names = set(_git("diff", "--name-only", base)) | set(_git("ls-files", "--others", "--exclude-standard"))
    return sorted(n.replace("\\", "/") for n in names)


# ---------------------------------------------------------------- import graph

def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):                       # ast.walk also sees imports inside functions
        if isinstance(node, ast.Import):
            found.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split(".")[0])
            found.update(a.name for a in node.names)  # `from tests import golden_common`
    return found


def build_graph() -> dict[str, tuple[Path, set[str]]]:
    local: dict[str, Path] = {}
    for d in CODE_DIRS:
        for p in sorted((ROOT / d).glob("*.py")):
            local.setdefault(p.stem, p)
    return {name: (p, _imports(p) & local.keys() - {name}) for name, p in local.items()}


def closure(graph: dict, start: str) -> set[str]:
    seen, todo = set(), [start]
    while todo:
        cur = todo.pop()
        if cur in seen or cur not in graph:
            continue
        seen.add(cur)
        todo.extend(graph[cur][1])
    return seen


def test_modules() -> list[str]:
    return sorted(p.stem for p in (ROOT / "tests").glob("test_*.py"))


# ---------------------------------------------------------------- selection

def _own_text(graph: dict, name: str) -> str:
    return graph[name][0].read_text(encoding="utf-8", errors="replace")


def reasons_for(rel: str, test: str, graph: dict, reach: set[str]) -> str | None:
    """Why would a change to `rel` affect `test`? None if it would not."""
    p = Path(rel)
    stem, suffix = p.stem, p.suffix
    if suffix == ".py" and stem == test:
        return "this test file changed"
    if suffix == ".py" and stem in reach:
        return "imported (directly or transitively)"
    if suffix == ".lua" and rel.startswith("engine/") and POB_MODULE in reach:
        return f"Lua runs inside PoB, which this test drives via {POB_MODULE}"
    if rel.startswith(IGNORED_PREFIXES):
        return None
    if rel.startswith("vault/") and VAULT_MODULE in reach:
        return f"vault loaded through {VAULT_MODULE}"
    if rel.startswith("gui/") and GUI_PATTERN.search(_own_text(graph, test)):
        return "read by this test"
    if rel.startswith((".claude/agents/", "tools/make_agents")) and test == "test_agents":
        return "checked by test_agents"
    if rel == "tests/golden.json" and test == GOLDEN_TEST:
        return "baseline of test_golden"
    if suffix in (".py", ".lua", ".json") and not rel.startswith("tests/") and p.name in _own_text(graph, test):
        return f"{p.name} is named in this test"
    return None


def select(changed: list[str], graph: dict) -> dict[str, list[str]]:
    chosen: dict[str, list[str]] = {}
    for t in test_modules():
        reach = closure(graph, t)
        why = [f"{rel} ({r})" for rel in changed if (r := reasons_for(rel, t, graph, reach))]
        if why:
            chosen[t] = why
    for t in SAFETY_TESTS:
        if t in test_modules():
            chosen.setdefault(t, []).append("always: cheap safety test")
    return chosen


def unmapped(changed: list[str], chosen: dict[str, list[str]]) -> list[str]:
    """Changed code files that no test picked up (new module without test, not covered)."""
    hit = " ".join(r for rs in chosen.values() for r in rs if not r.startswith("always"))
    return [c for c in changed if c.endswith((".py", ".lua", ".html")) and f"{c} (" not in hit]


# ---------------------------------------------------------------- resources and scheduling

def free_memory_mb() -> int | None:
    if os.name == "nt":
        class Status(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + \
                       [(n, ctypes.c_ulonglong) for n in ("tot", "avail", "tpf", "apf", "tv", "av", "aev")]
        st = Status()
        st.length = ctypes.sizeof(st)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return int(st.avail // (1024 * 1024))
        return None
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return None


def worker_caps(heavy_jobs: int, total_jobs: int, requested: int | None) -> tuple[int, int, str]:
    """(total workers, heavy workers, explanation) from CPUs and free memory."""
    cpus = os.cpu_count() or 4
    mem = free_memory_mb()
    budget = None if mem is None else int(mem * MEM_FRACTION)
    heavy = min(MAX_HEAVY_WORKERS, max(1, cpus // 2))
    if budget is not None:
        heavy = min(heavy, max(1, budget // HEAVY_MB))
    total = requested or min(MAX_WORKERS, cpus)
    if budget is not None:
        total = min(total, max(1, (budget - heavy * HEAVY_MB) // LIGHT_MB + heavy))
    total = max(1, min(total, total_jobs))
    heavy = max(1, min(heavy, total, heavy_jobs or 1))
    ram = "?" if mem is None else f"{mem} MB"
    return total, heavy, f"cpus={cpus}, free RAM={ram} -> workers {total}, PoB-heavy {heavy}"


def _times_path() -> Path:
    common = _git("rev-parse", "--git-common-dir")
    base = (ROOT / common[0]).resolve() if common else ROOT
    return base / "autobuilder_test_times.json"      # inside .git: never tracked, shared by worktrees


def load_times() -> dict[str, float]:
    try:
        return json.loads(_times_path().read_text())
    except (OSError, ValueError):
        return {}


def save_times(old: dict[str, float], results: list[Result]) -> None:
    ok = [r for r in results if r.returncode == 0]
    new = {**old, **{r.job.module: round(r.seconds, 1) for r in ok}}
    for r in ok:                                         # class jobs: the file's serial time = sum of its classes
        parent = r.job.module.rsplit(".", 1)[0]
        if parent.count(".") == 1:
            new[parent] = round(sum(x.seconds for x in ok if x.job.module.startswith(parent + ".")), 1)
    try:
        _times_path().write_text(json.dumps(new, indent=1))
    except OSError:
        pass


def test_classes(path: Path) -> list[str]:
    """Top-level public classes with a base class (unittest.TestCase subclasses), in file order."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return []
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef) and n.bases and not n.name.startswith("_")]


def make_jobs(chosen: dict[str, list[str]], graph: dict, times: dict[str, float]) -> list[Job]:
    jobs: list[Job] = []
    times = dict(times)                                  # local copy: estimates must not reach the saved cache
    for t, reasons in chosen.items():
        heavy, module = POB_MODULE in closure(graph, t), f"tests.{t}"
        classes = test_classes(graph[t][0])
        if times.get(module, 0.0) >= SPLIT_AFTER_S and len(classes) > 1:   # file is the bottleneck: split by class
            jobs += [Job(f"{module}.{c}", heavy, reasons) for c in classes]
            for c in classes:
                times.setdefault(f"{module}.{c}", times[module] / len(classes))
        else:
            jobs.append(Job(module, heavy, reasons))
    # longest first: measured time, else PoB-heavy before light
    jobs.sort(key=lambda j: (-times.get(j.module, 0.0), not j.heavy))
    return jobs


def _parse(output: str) -> tuple[int, int]:
    ran = re.search(r"^Ran (\d+) tests?", output, re.M)
    skipped = re.search(r"skipped=(\d+)", output)
    return (int(ran.group(1)) if ran else 0), (int(skipped.group(1)) if skipped else 0)


def _finish(job: Job, proc: subprocess.Popen, started: float, log) -> Result:
    log.seek(0)
    out = log.read().decode("utf-8", errors="replace")      # file, not a pipe: a chatty child cannot block
    log.close()
    tests, skipped = _parse(out)
    tail = "\n".join(out.splitlines()[-TAIL_LINES:])
    return Result(job, time.monotonic() - started, proc.returncode, tests, skipped, tail)


def _start(job: Job, env: dict) -> tuple:
    log = tempfile.TemporaryFile()
    proc = subprocess.Popen([sys.executable, "-m", "unittest", job.module], cwd=ROOT, env=env,
                            stdout=log, stderr=subprocess.STDOUT)
    return proc, job, time.monotonic(), log


def run_jobs(jobs: list[Job], total: int, heavy_cap: int) -> list[Result]:
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
    pending, running, results = list(jobs), [], []
    while pending or running:
        heavy_now = sum(1 for _, j, _, _ in running if j.heavy)
        for job in list(pending):
            if len(running) >= total:
                break
            if job.heavy and heavy_now >= heavy_cap:
                continue                                  # a light job further down may still start
            pending.remove(job)
            heavy_now += job.heavy
            running.append(_start(job, env))
        time.sleep(0.05)
        for proc, _, began, _ in running:
            if proc.poll() is None and time.monotonic() - began > JOB_TIMEOUT_S:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)                     if os.name == "nt" else proc.kill()
        for entry in [e for e in running if e[0].poll() is not None]:
            running.remove(entry)
            results.append(_finish(entry[1], entry[0], entry[2], entry[3]))
            print(status_line(results[-1]), flush=True)
    return results


# ---------------------------------------------------------------- output

def status_line(r: Result) -> str:
    state = "OK  " if r.returncode == 0 else "FAIL"
    skip = f", {r.skipped} skipped" if r.skipped else ""
    return f"[{state}] {r.seconds:6.1f}s  {r.job.module:<36} {r.tests} tests{skip}"


def print_summary(results: list[Result], wall: float) -> int:
    failed = [r for r in results if r.returncode != 0]
    for r in failed:
        print(f"\n===== FAILED {r.job.module} (exit {r.returncode}) - last {TAIL_LINES} lines =====\n{r.tail}")
    serial = sum(r.seconds for r in results)
    slowest = max(results, key=lambda r: r.seconds, default=None)
    print(f"\n{len(results)} files, {sum(r.tests for r in results)} tests, {len(failed)} failed files; "
          f"wall {wall:.1f}s (sum of file times {serial:.1f}s)")
    if slowest:
        print(f"slowest file: {slowest.job.module} {slowest.seconds:.1f}s "
              f"({slowest.seconds / wall * 100:.0f}% of the wall time)")
    return 1 if failed else 0


def print_selection(chosen: dict[str, list[str]], changed: list[str], miss: list[str]) -> None:
    print(f"changed files: {len(changed)}")
    ignored = [c for c in changed if c.startswith(IGNORED_PREFIXES)]
    if ignored:
        print(f"ignored (not content, Obsidian window state): {len(ignored)} under " + ", ".join(IGNORED_PREFIXES))
    for t, rs in sorted(chosen.items()):
        shown = rs if len(rs) <= 3 else rs[:3] + [f"... and {len(rs) - 3} more"]
        print(f"  {t}: " + " | ".join(shown))
    if miss:
        print("note: no test reaches " + ", ".join(miss) + " (new module without test, or not covered)")


# ---------------------------------------------------------------- main

def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="run every test file")
    ap.add_argument("--files", nargs="+", metavar="PATH", help="select as if these files changed")
    ap.add_argument("--list", action="store_true", help="print the selection, do not run")
    ap.add_argument("--workers", type=int, help="override the total worker count")
    ap.add_argument("--slow", action="store_true", help="set AUTOBUILDER_SLOW=1 (test_determinism etc.)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.slow:
        os.environ["AUTOBUILDER_SLOW"] = "1"
    graph = build_graph()
    changed = [f.replace("\\", "/") for f in args.files] if args.files else changed_files()
    chosen = {t: ["--all"] for t in test_modules()} if args.all else select(changed, graph)
    if not args.all:
        print_selection(chosen, changed, unmapped(changed, chosen))
    if args.list or not chosen:
        return 0
    times = load_times()
    jobs = make_jobs(chosen, graph, times)
    total, heavy, note = worker_caps(sum(j.heavy for j in jobs), len(jobs), args.workers)
    slow = os.environ.get("AUTOBUILDER_SLOW") == "1"
    print(f"running {len(jobs)} test files; {note}; AUTOBUILDER_SLOW={'1' if slow else 'unset'}", flush=True)
    start = time.monotonic()
    results = run_jobs(jobs, total, heavy)
    code = print_summary(results, time.monotonic() - start)
    save_times(times, results)
    return code


if __name__ == "__main__":
    sys.exit(main())
