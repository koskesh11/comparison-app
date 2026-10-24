"""Check a calculated build context against vault rules.

Context (from audit.lua evaluate):
  skills:       [{name, isMain, isAttack, out: {stat: value}}]   # main socket group
  usedTogether: [{name, group, index, out: {stat: value}}]       # requested other-group skills
  supports:  [granted effect ids linked to the main skill]
  keystones: [allocated keystone names]

Rule specs may use top-level ``when_support_linked`` to require one of a list of
granted effect ids, independently of ``when.linked_support_any``.
"""

import math
import operator

import costs
from display import fmt
from scoring import skill_out
from vault import Rule

WORSE_TOLERANCE = 0.05  # below the one decimal the messages show
WORSE_MARK = " - already broken in your build and made worse"
OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}


def stat_keys(rules: list[Rule]) -> set[str]:
    keys = set()
    for rule in rules:
        for req in rule.spec.get("require") or []:
            for field in ("stat", "ref", "each_skill", "sum_over_skill_set"):
                if field in req:
                    keys.add(req[field])
            if "allow_deficit" in req:
                keys.add(req["allow_deficit"]["pool"])
    return keys


def applies(rule: Rule, ctx: dict) -> bool:
    when = rule.spec.get("when") or {}
    wanted = when.get("linked_support_any")
    linked = rule.spec.get("when_support_linked")
    if linked is not None and (not isinstance(linked, list)
                               or not all(isinstance(item, str) for item in linked)):
        raise ValueError(f"rule {rule.name!r}: when_support_linked must be a list of granted effect ids")
    nested_matches = not wanted or any(s in ctx["supports"] for s in wanted)
    top_level_matches = linked is None or any(s in ctx["supports"] for s in linked)
    return nested_matches and top_level_matches


def _targets(rule: Rule, ctx: dict) -> list[dict]:
    if rule.spec.get("evaluate_on") == "triggering_attack":
        return [s for s in ctx["skills"] if s["isAttack"]]
    return [s for s in ctx["skills"] if s["isMain"]]


def _compare(value, op: str, limit) -> bool:
    return value is None or limit is None or OPS[op](value, limit)


def _gap(value, limit) -> float:
    """How far a failing comparison is from passing, in the stat's own unit."""
    return abs(limit - value) if value is not None and limit is not None else 1.0


def _sum_failures(req: dict, ctx: dict, main: dict) -> list[tuple[str, str, float]]:
    op, stat = req["op"], req["sum_over_skill_set"]
    total = sum(skill_out(s).get(stat) or 0 for s in costs.used_together(ctx))
    limit = main.get(req["ref"])
    note = costs.es_unverified(ctx) if stat == costs.KEYS["ES"]["cost"] else None
    suffix = f" [{note}]" if note else ""
    key, gap = f"total {stat}", _gap(total, limit)
    if total == 0 or _compare(total, op, limit):
        return []
    deficit = req.get("allow_deficit")
    if deficit and limit is not None:
        pool = main.get(deficit["pool"]) or 0
        if pool <= 0:
            return [(f"total {stat} {fmt(total, 1)} vs {req['ref']} {fmt(limit, 1)} "
                     f"and no free {deficit['pool']} to cover it{suffix}", key, gap)]
        seconds = math.floor(pool / (total - limit))
        if seconds >= deficit["min_seconds"]:
            return []
        return [(f"total {stat} {fmt(total, 1)} vs {req['ref']} {fmt(limit, 1)}: "
                 f"pool empty after {seconds}s{suffix}", key, gap)]
    return [(f"total {stat} {fmt(total, 1)} vs {req['ref']} {fmt(limit, 1)}{suffix}", key, gap)]


def _failures(req: dict, targets: list[dict], ctx: dict) -> list[tuple[str, str, float]]:
    """Failed checks of one requirement as (message, key, shortfall); the key names what failed."""
    main = skill_out(next(s for s in ctx["skills"] if s["isMain"]))
    if "sum_over_skill_set" in req:
        return _sum_failures(req, ctx, main)
    failures = []
    stat = req.get("each_skill") or req["stat"]
    for skill in targets if "stat" in req else costs.used_together(ctx):
        out = skill_out(skill)
        value = out.get(stat)
        limit = req["value"] if "value" in req else out.get(req["ref"])
        if not _compare(value, req["op"], limit):
            failures.append((f"{skill['name']}: {stat} {fmt(value, 1)} {req['op']} {fmt(limit, 1)} failed",
                             f"{skill['name']}: {stat}", _gap(value, limit)))
    return failures


def _rule_failures(rules: list[Rule], ctx: dict) -> list[tuple[str, str, str, float]]:
    """Every failed check as (rule name, message, key, shortfall)."""
    found = []
    for rule in rules:
        if not applies(rule, ctx):
            continue
        targets = _targets(rule, ctx)
        for req in rule.spec.get("require") or []:
            found += [(rule.name, message, key, gap) for message, key, gap in _failures(req, targets, ctx)]
        for item in rule.spec.get("forbid") or []:
            if item.get("keystone") in ctx["keystones"]:
                found.append((rule.name, f"forbidden keystone {item['keystone']}",
                              f"keystone {item['keystone']}", 1.0))
    return found


def violations(rules: list[Rule], ctx: dict) -> list[str]:
    return [f"[{name}] {message}" for name, message, _, _ in _rule_failures(rules, ctx)]


def worsened(rules: list[Rule], base_ctx: dict, ctx: dict) -> list[str]:
    """Checks of an already-broken rule that fail by more than before, or that are new inside it (spec B6)."""
    before = {(name, key): gap for name, _, key, gap in _rule_failures(rules, base_ctx)}
    broken = {name for name, _ in before}
    found = []
    for name, message, key, gap in _rule_failures(rules, ctx):
        if name not in broken:
            continue  # a rule the change breaks anew is reported by the caller's own break check
        old = before.get((name, key), 0.0)
        if gap > old + WORSE_TOLERANCE:
            found.append(f"[{name}] {message}{WORSE_MARK} (short by {fmt(old, 1)} before, {fmt(gap, 1)} now)")
    return found


def rule_name(violation: str) -> str:
    """'[Rule name] message' -> 'Rule name'."""
    return violation[1:violation.index("]")] if violation.startswith("[") else violation
