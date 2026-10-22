"""Check a calculated build context against vault rules.

Context (from audit.lua evaluate):
  skills:    [{name, isMain, isAttack, out: {stat: value}}]   # skills used together
  supports:  [granted effect ids linked to the main skill]
  keystones: [allocated keystone names]
"""

import operator

from vault import Rule

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
    return not wanted or any(s in ctx["supports"] for s in wanted)


def _targets(rule: Rule, ctx: dict) -> list[dict]:
    if rule.spec.get("evaluate_on") == "triggering_attack":
        return [s for s in ctx["skills"] if s["isAttack"]]
    return [s for s in ctx["skills"] if s["isMain"]]


def _compare(value, op: str, limit) -> bool:
    return value is None or limit is None or OPS[op](value, limit)


def _check_requirement(req: dict, targets: list[dict], ctx: dict) -> list[str]:
    main = next(s for s in ctx["skills"] if s["isMain"])["out"]
    op = req["op"]
    if "sum_over_skill_set" in req:
        stat = req["sum_over_skill_set"]
        total = sum(s["out"].get(stat) or 0 for s in ctx["skills"])
        limit = main.get(req["ref"])
        if _compare(total, op, limit):
            return []
        deficit = req.get("allow_deficit")
        if deficit and limit is not None:
            pool = main.get(deficit["pool"]) or 0
            if pool <= 0:
                return [f"total {stat} {total:.1f} vs {req['ref']} {limit:.1f} and no free {deficit['pool']} to cover it"]
            seconds = pool / (total - limit)
            if seconds >= deficit["min_seconds"]:
                return []
            return [f"total {stat} {total:.1f} vs {req['ref']} {limit:.1f}: pool empty after {seconds:.0f}s"]
        return [f"total {stat} {total:.1f} vs {req['ref']} {limit:.1f}"]
    failures = []
    stat = req.get("each_skill") or req["stat"]
    for skill in targets if "stat" in req else ctx["skills"]:
        value = skill["out"].get(stat)
        limit = req["value"] if "value" in req else skill["out"].get(req["ref"])
        if not _compare(value, op, limit):
            failures.append(f"{skill['name']}: {stat} {value:.1f} {op} {limit:.1f} failed")
    return failures


def violations(rules: list[Rule], ctx: dict) -> list[str]:
    found = []
    for rule in rules:
        if not applies(rule, ctx):
            continue
        targets = _targets(rule, ctx)
        for req in rule.spec.get("require") or []:
            found += [f"[{rule.name}] {msg}" for msg in _check_requirement(req, targets, ctx)]
        for item in rule.spec.get("forbid") or []:
            if item.get("keystone") in ctx["keystones"]:
                found.append(f"[{rule.name}] forbidden keystone {item['keystone']}")
    return found


def rule_name(violation: str) -> str:
    """'[Rule name] message' -> 'Rule name'."""
    return violation[1:violation.index("]")] if violation.startswith("[") else violation
