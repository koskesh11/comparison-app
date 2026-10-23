"""Token use of this project's Claude Code sessions, by agent and model (task 019).

Reads the local transcripts (~/.claude/projects/<project>/**/*.jsonl), counts each API message once, and weights
tokens by list price so Opus/Sonnet/Haiku and cache reads/writes are comparable (cost units, not a bill).
Usage: python tools/token_usage.py [--since YYYY-MM-DD] [--until YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from collections import defaultdict

PROJECT_DIR = os.path.expanduser(r"~/.claude/projects/c--Users-7800x3D-Desktop-pob-autobuilder")
# USD per million tokens (input, output, cache read), claude-api reference cached 2026-10-06.
# Cache writes cost 1.25x input.
PRICE = {"opus": (4.0, 20.0, 0.20), "sonnet": (2.0, 10.0, 0.20), "haiku": (0.10, 0.50, 0.01)}
FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def model_family(model: str | None) -> str | None:
    return next((k for k in PRICE if k in (model or "")), None)


def agent_name(path: str) -> str:
    if "subagents" not in path:
        return "MAIN"
    try:
        with open(path.replace(".jsonl", ".meta.json"), encoding="utf-8") as f:
            return json.load(f).get("agentType", "?")
    except (OSError, ValueError):
        return "?"


def messages(path: str, since: str, until: str) -> list[tuple[str, dict]]:
    """One (model, usage) per API message; streamed copies of a message are merged by max per field."""
    best: dict[str, tuple[str, dict]] = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message") or {}
            usage = msg.get("usage")
            ts = d.get("timestamp", "")
            if d.get("type") != "assistant" or not usage or not (since <= ts[:10] <= until):
                continue
            mid = msg.get("id") or id(d)
            old = best.get(mid, (None, {}))[1]
            best[mid] = (msg.get("model"), {k: max(old.get(k) or 0, usage.get(k) or 0) for k in FIELDS})
    return list(best.values())


def cost(usage: dict, family: str) -> float:
    pi, po, pc = PRICE[family]
    return (usage["input_tokens"] * pi + usage["cache_creation_input_tokens"] * pi * 1.25
            + usage["cache_read_input_tokens"] * pc + usage["output_tokens"] * po) / 1e6


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="0000-00-00")
    ap.add_argument("--until", default="9999-99-99")
    args = ap.parse_args()
    rows: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0, 0, 0, 0, 0.0, 0])
    for path in glob.glob(os.path.join(PROJECT_DIR, "**", "*.jsonl"), recursive=True):
        name = agent_name(path)
        for model, usage in messages(path, args.since, args.until):
            family = model_family(model)
            if not family:
                continue
            row = rows[(name, family)]
            for i, k in enumerate(FIELDS):
                row[i] += usage[k]
            row[4] += cost(usage, family)
            row[5] += 1
    total = sum(r[4] for r in rows.values()) or 1.0
    print(f"{'agent':26} {'model':6} {'calls':>6} {'ctx-write(M)':>12} {'ctx-read(M)':>11} {'out(M)':>7} {'units':>7} {'%':>5}")
    for (name, family), r in sorted(rows.items(), key=lambda kv: -kv[1][4]):
        print(f"{name:26} {family:6} {r[5]:6} {(r[0] + r[1]) / 1e6:12.2f} {r[2] / 1e6:11.1f} {r[3] / 1e6:7.2f} "
              f"{r[4]:7.1f} {100 * r[4] / total:5.1f}")
    calls = sum(r[5] for r in rows.values())
    print(f"TOTAL {total:.1f} cost units over {calls} calls ({args.since} .. {args.until})")


if __name__ == "__main__":
    main()
