"""Pure DPS scoring and per-skill presentation helpers."""

from display import fmt, fmt_pct


def change_pct(new: float, old: float) -> float | None:
    return 100 * (new - old) / old if old else None


def pct(new: float, old: float) -> str:
    return fmt_pct(change_pct(new, old))


def skill_out(skill: dict) -> dict:
    """Return a skill's output table, normalizing Lua's empty-array encoding."""
    out = skill.get("out")
    return out if isinstance(out, dict) else {}


def dps_key(out: dict) -> str:
    return "FullDPS" if (out.get("FullDPS") or 0) > 0 else "CombinedDPS"


def dps_measure(ctx: dict) -> dict:
    main = next(skill for skill in ctx["skills"] if skill["isMain"])
    if dps_key(skill_out(main)) == "FullDPS":
        return {"key": "FullDPS", "warning": None}
    warning = ("No skill group is in Full DPS ('Include in Full DPS' unticked): "
               f"DPS % uses the main skill {main['name']} only")
    return {"key": "CombinedDPS", "warning": warning}


def skill_rows(ctx: dict) -> list[dict]:
    rows = [{
        "name": row["name"],
        "part": row.get("skillPart") or None,
        "count": row.get("count") or 1,
        "dps": row.get("dps") or 0.0,
        "contribution": (row.get("dps") or 0.0) * (row.get("count") or 1),
    } for row in (ctx.get("skillDPS") or [])]
    return sorted(rows, key=lambda row: (-row["contribution"], row["name"], row["part"] or ""))


def projectile_count(ctx: dict, name: str, part: str | None) -> float | None:
    matches = [skill for skill in ctx.get("skills", []) if skill["name"] == name]
    if not matches:
        return None
    skill = next((row for row in matches if row.get("part") == part), matches[0])
    return skill_out(skill).get("ProjectileCount")


def skill_changes(ctx: dict, base_ctx: dict) -> list[dict]:
    new = {(row["name"], row["part"]): row for row in skill_rows(ctx)}
    base = {(row["name"], row["part"]): row for row in skill_rows(base_ctx)}
    keys = set(new) | set(base)
    rows = []
    for name, part in keys:
        new_row, base_row = new.get((name, part)), base.get((name, part))
        before = base_row["contribution"] if base_row else 0.0
        after = new_row["contribution"] if new_row else 0.0
        rows.append({"name": name, "part": part,
                     "count": (new_row or base_row)["count"],
                     "from": before, "to": after, "pct": change_pct(after, before),
                     "projectiles": projectile_count(ctx, name, part)})
    return sorted(rows, key=lambda row: (-row["from"], row["name"], row["part"] or ""))


def attack_names(ctx: dict) -> str:
    return ", ".join(sorted(skill["name"] for skill in ctx["skills"] if skill.get("isAttack")))


def ordinal(number: int) -> str:
    suffix = "th" if 10 < number % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def trigger_overshoot_why(rate: float | None, cap: float | None, source_rate: float | None,
                          names: str) -> str | None:
    if (rate is None or cap is None or source_rate is None or cap <= 0 or rate <= 0
            or rate >= cap - 1e-9 or source_rate <= cap + 1e-9):
        return None
    every_n = round(source_rate / rate)
    every = f" (about every {ordinal(every_n)} attack)" if every_n >= 2 else ""
    source = names or "trigger source"
    return (f"{source} attack rate {fmt(source_rate, 2)}/s overshoots the {fmt(cap, 2)}/s cap: "
            f"only {fmt(100 * rate / source_rate)}% of attacks trigger{every}; see breakpoints (B5)")


def trigger_info(ctx: dict) -> dict[str, dict]:
    attacks = attack_names(ctx)
    result = {}
    for skill in ctx["skills"]:
        out = skill_out(skill)
        rate = out.get("SkillTriggerRate")
        if rate is None:
            continue
        cap = out.get("TriggerRateCap") or None
        source_rate = out.get("EffectiveSourceRate") or None
        at_cap = cap is not None and rate >= cap - 1e-9
        why = _trigger_why(rate, cap, source_rate, at_cap, attacks)
        result[skill["name"]] = {"rate": rate, "cap": cap, "sourceRate": source_rate,
                                 "atCap": at_cap, "why": why}
    return result


def _trigger_why(rate: float, cap: float | None, source_rate: float | None,
                 at_cap: bool, attack_names: str) -> str | None:
    if at_cap or cap is None:
        return None
    if source_rate is None:
        return "below the cap; PoB gives no reason"
    if rate >= source_rate - 1e-9:
        source = attack_names or "the trigger source"
        return f"limited by the trigger source: {source} at {fmt(source_rate, 2)}/s"
    overshoot = trigger_overshoot_why(rate, cap, source_rate, attack_names)
    if overshoot is not None:
        return overshoot
    return f"below the cap and below the source rate ({fmt(source_rate, 2)}/s); PoB gives no further reason"


def base_skill_rows(ctx: dict) -> list[dict]:
    triggers = trigger_info(ctx)
    return [{**row, "trigger": triggers.get(row["name"])} for row in skill_rows(ctx)]


def tile_text(rows: list[dict]) -> str:
    contributions = []
    for row in rows:
        if not row["contribution"]:
            continue
        detail = f"{row['part']}, x{row['count']:g}" if row["part"] is not None else f"x{row['count']:g}"
        contributions.append(f"{row['name']} {fmt(row['contribution'] / 1e6, 2)}M ({detail})")
    text = " + ".join(contributions)
    for row in rows:
        trigger = row.get("trigger")
        if trigger:
            cap = f" of {fmt(trigger['cap'], 2)}/s cap" if trigger["cap"] is not None else ""
            text += f"; {row['name']} {fmt(trigger['rate'], 2)}/s{cap}"
    return text


def skill_pcts_text(changes: list[dict], limit: int = 2) -> str:
    rows = [row for row in changes if row["pct"] is not None][:limit]
    labels = []
    for row in rows:
        details = [row["part"]] if row.get("part") is not None else []
        if row.get("projectiles") is not None:
            details.append(f"{fmt(row['projectiles'])} proj")
        suffix = f" ({', '.join(details)})" if details else ""
        labels.append(f"{row['name']}{suffix} {fmt_pct(row['pct'])}")
    return ", ".join(labels)
