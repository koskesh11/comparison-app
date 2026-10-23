"""Pure helpers for resource costs and source-gated scenario configuration."""

import math
import re

from display import fmt
from scoring import skill_out

RESOURCES: tuple[str, ...] = ("Mana", "Life", "ES")
KEYS = {
    "Mana": {"cost": "ManaPerSecondCost", "regen": "ManaRegenRecovery", "pool": "ManaUnreserved"},
    "Life": {"cost": "LifePerSecondCost", "regen": "LifeRegenRecovery", "pool": "LifeUnreserved"},
    "ES": {"cost": "ESPerSecondCost", "regen": "EnergyShieldRegenRecovery", "pool": "EnergyShield"},
}
RECHARGE_KEY = "EnergyShieldRecharge"
RECHARGE_DELAY_KEY = "EnergyShieldRechargeDelay"
ELDRITCH_BATTERY = "Eldritch Battery"
ES_UNVERIFIED = "unverified (Eldritch Battery not modelled)"
STAT_KEYS: list[str] = sorted({key for fields in KEYS.values() for key in fields.values()}
                              | {RECHARGE_KEY, RECHARGE_DELAY_KEY})
CONDITIONS = {"build_has_consecrated_ground_source"}


def _source(pattern: str, kind: str, conditional: bool, label: str) -> dict:
    return {"pattern": re.compile(pattern), "kind": kind,
            "conditional": conditional, "label": label}


CONSECRATED_SOURCES: tuple[dict, ...] = (
    # Data/Uniques/flask.lua:144,345,356,434; Data/ModItemExclusive.lua:5017
    _source(r"creates consecrated ground on use", "flask use", False, "flask use"),
    # TreeData/3_29/tree.lua:16449; Data/ModExplicit.lua:3003; Modules/ModParser.lua:2912
    _source(r"you have consecrated ground around you while stationary",
            "stationary", False, "stationary"),
    # TreeData/3_29/tree.lua:33255; Data/ModScalability.lua:1046,1050,1051,8034
    _source(r"(\d+% chance to )?create consecrated ground "
            r"(on melee kill|when you kill an enemy)(, lasting \d+ seconds)?",
            "on kill", True, "on kill"),
    # TreeData/3_29/tree.lua:17940; Data/ModJewelCharm.lua:88-89; Data/ModScalability.lua:1045,1049,8032
    _source(r"(\d+% chance to )?create consecrated ground "
            r"(on hit|when you hit a rare or unique enemy)(, lasting \d+ seconds)?",
            "on hit", True, "on hit"),
    # Data/ModScalability.lua:8036
    _source(r"create consecrated ground, lasting \d+ seconds, when you hit a magic, rare or unique enemy, "
            r"up to once every \d+ seconds", "on hit", True, "on hit"),
    # Data/ModScalability.lua:1047,8033
    _source(r"(\d+% chance to )?create consecrated ground when hit, lasting \d+ seconds",
            "when hit", True, "when hit"),
    # Data/ModScalability.lua:1044,8031
    _source(r"(\d+% chance to )?create consecrated ground on death, lasting \d+ seconds",
            "on death", True, "on death"),
    # Data/Uniques/body.lua:784-786; Data/ModItemExclusive.lua:3690; Data/ModScalability.lua:1048
    _source(r"(\d+% chance to )?create consecrated ground when you block",
            "on block", True, "on block"),
    # Data/Uniques/ring.lua:564; Data/ModItemExclusive.lua:3740
    _source(r"creates consecrated ground on critical strike", "on crit", True, "on crit"),
    # Data/ModScalability.lua:698
    _source(r"\d+% chance on critical strike to create consecrated ground",
            "on crit", True, "on crit"),
    # Data/Uniques/bow.lua:365; Data/ModItemExclusive.lua:5070,8218; Data/ModScalability.lua:1052,8035
    _source(r"(\d+% chance to )?create consecrated ground when you shatter an enemy",
            "on shatter", True, "on shatter"),
    # Data/ModScalability.lua:11958,11991
    _source(r"(purifying flame also creates consecrated ground around you|"
            r"puryfing flame has \d+% chance to also create consecrated ground around you)",
            "gem", True, "Purifying Flame"),
    # Data/Uniques/jewel.lua:480-481; Data/ModItemExclusive.lua:7827; Modules/ModParser.lua:5613-5614
    _source(r"(you have consecrated ground around you while stationary if strength is your highest attribute|"
            r"you have consecrated ground around you while)",
            "stationary attribute", True, "Rational Doctrine"),
    # Data/Uniques/Special/BoundByDestiny.lua:21; Modules/ModParser.lua:5616
    _source(r"consecrated ground around you while stationary if \d+ \w+ items are equipped",
            "stationary items", True, "Bound by Destiny"),
    # Data/Skills/act_int.lua:21409,21433
    _source(r".*gives a chance to create consecrated ground against stronger enemies\.?",
            "gem", True, "Zealotry"),
)

# Deliberately excluded (default deny):
# - "create profane ground instead of consecrated ground" (TreeData/3_29/tree.lua:14241;
#   Data/Uniques/shield.lua:970)
# - "create fungal ground instead of consecrated ground" (TreeData/3_29/tree.lua:51799)
# - "+(1-2)% to Critical Strike Chance against Enemies on Consecrated Ground during Effect"
#   (Data/Uniques/flask.lua:149) and "50% increased Damage while on Consecrated Ground"
#   (Data/Uniques/ring.lua:566)
# - "Effects of Consecrated Ground you create Linger for 4 seconds"
#   (TreeData/3_29/tree.lua:16472; Data/Uniques/jewel.lua:484)
# - "Consecrated Ground you create applies 15% increased Damage taken to Enemies"
#   (TreeData/3_29/tree.lua:16448), "Consecrated Ground you create causes Life Regeneration to\n"
#   "also Recover Energy Shield for you and Allies" (TreeData/3_29/tree.lua:16471),
#   "Consecrated Ground you create grants 30% increased Accuracy Rating to you and Allies"
#   (TreeData/3_29/tree.lua:22888), and "Consecrated Ground you create also grants\n"
#   "50% reduced duration of Damaging Ailments on you" (TreeData/3_29/tree.lua:37624)
# - "Consecrated Ground created by this Flask has Tripled Radius" (Data/Uniques/flask.lua:148)
# - "Consecrated Ground created during Effect applies (7-10)% increased Damage taken to Enemies"
#   (Data/Uniques/flask.lua:150)
# - "20% increased Effect of Consecrated Ground you create" (TreeData/3_29/tree.lua:22887)
# - "Gain Arcane Surge for 4 seconds when you create Consecrated Ground while affected by Zealotry"
#   (Data/Uniques/Special/WatchersEye.lua:122)
# - "Inflict Hallowing Flame on Hit while on Consecrated Ground" (Data/Uniques/ring.lua:580)
# Consecrated Path, Holy Flame Totem, Word of Light, and Consecrate descriptions are also not
# passive state sources.

_TRIGGERS = {
    "triggeredByDamageTaken": "damage taken",
    "chanceToTriggerOnStun": "being stunned",
    "chanceToTriggerOnWardBreak": "ward break",
    "triggeredOnDeath": "death",
    "chanceToTriggerCounterattackOnBlock": "block",
    "chanceToTriggerCounterAttackOnHit": "being hit",
    "trigger_effect_group_on_block": "block",
}


def used_together(ctx: dict) -> list[dict]:
    """Return main-group skills followed by requested extra-group skills."""
    return list(ctx["skills"]) + list(ctx.get("usedTogether") or [])


def es_unverified(ctx: dict) -> str | None:
    return ES_UNVERIFIED if ELDRITCH_BATTERY in (ctx.get("keystones") or []) else None


def _recharge(out: dict) -> dict:
    per_second = out.get(RECHARGE_KEY) or 0
    delay = out.get(RECHARGE_DELAY_KEY)
    if not per_second:
        text = "none"
    elif delay is None:
        text = fmt(per_second, sign=True, thousands=True) + "/s"
    else:
        text = (fmt(per_second, sign=True, thousands=True) + "/s, only after "
                + fmt(delay, 2) + " s without damage")
    return {"perSecond": per_second, "delay": delay, "text": text}


def margin(ctx: dict, resource: str) -> dict:
    """Calculate regeneration minus costs for one resource."""
    fields = KEYS[resource]
    main = next(skill for skill in ctx["skills"] if skill["isMain"])
    out = skill_out(main)
    regen = out.get(fields["regen"]) or 0
    lines = [{"name": skill["name"], "value": -skill_out(skill)[fields["cost"]],
              "group": skill.get("group")}
             for skill in used_together(ctx) if (skill_out(skill).get(fields["cost"]) or 0) > 0]
    total = sum(-line["value"] for line in lines)
    remaining = regen - total
    pool = out.get(fields["pool"]) or 0
    pool_seconds = math.floor(max(pool, 0) / -remaining) if remaining < 0 else None
    result = {"resource": resource, "regen": regen, "lines": lines, "total": total,
              "margin": remaining, "pool": pool, "poolSeconds": pool_seconds, "hasCost": total > 0}
    if resource == "ES":
        result["recharge"] = _recharge(out)
        note = es_unverified(ctx)
        if note:
            result["unverified"] = note
    return result


def margins(ctx: dict) -> list[dict]:
    """Return margins for cost-bearing resources in fixed display order."""
    rows = [margin(ctx, resource) for resource in RESOURCES]
    return [row for row in rows if row["hasCost"]]


def cost_dims(ctx: dict, base_ctx: dict) -> dict:
    """Return margin changes only when both contexts evaluated the same number of extra skills."""
    if len(ctx.get("usedTogether") or []) != len(base_ctx.get("usedTogether") or []):
        return {}
    result = {}
    for resource in RESOURCES:
        before, after = margin(base_ctx, resource), margin(ctx, resource)
        if before["hasCost"] or after["hasCost"]:
            result[resource] = {"from": before["margin"], "to": after["margin"]}
            note = ((es_unverified(ctx) or es_unverified(base_ctx))
                    if resource == "ES" else None)
            if note:
                result[resource]["unverified"] = note
    return result


def kpi_entries(ctx: dict) -> list[dict]:
    """Build source rows for each cost-bearing resource KPI."""
    entries = []
    for row in margins(ctx):
        resource = row["resource"]
        sources = [{"label": f"{resource} regen (PoB)", "value": row["regen"]}]
        sources += [{"label": f"{line['name']} cost" +
                    (f" (group {line['group']})" if line["group"] is not None else ""),
                     "value": line["value"]} for line in row["lines"]]
        sources.append({"label": "= margin per second", "value": row["margin"]})
        entry = {"resource": resource, "sources": sources, "margin": row["margin"],
                 "poolSeconds": row["poolSeconds"]}
        if row.get("unverified"):
            entry["unverified"] = row["unverified"]
        entries.append(entry)
    return entries


def dims_text(dims_costs: dict) -> str:
    """Format non-Mana resource margin dimensions for compact CLI rows."""
    parts = []
    for resource in RESOURCES:
        if resource == "Mana" or resource not in dims_costs:
            continue
        row = dims_costs[resource]
        text = (f" | {resource} margin {fmt(row['from'], sign=True, thousands=True)} -> "
                f"{fmt(row['to'], sign=True, thousands=True)}/s")
        if row.get("unverified"):
            text += f" [{row['unverified']}]"
        parts.append(text)
    return "".join(parts)


def _trigger_name(reactive_by: str | None) -> str:
    if reactive_by is None:
        return "an incoming event"
    if " (" in reactive_by and reactive_by.endswith(")"):
        key = reactive_by.rsplit(" (", 1)[1][:-1]
    else:
        key = reactive_by.removeprefix("skillData.").split(" (", 1)[0]
    return _TRIGGERS.get(key, key)


def _cost_values(row: dict) -> dict:
    out = skill_out(row)
    return {resource: out.get(KEYS[resource]["cost"]) or 0 for resource in RESOURCES
            if (out.get(KEYS[resource]["cost"]) or 0) > 0}


def classify_other_skills(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split other-group cost skills into used-together and excluded rows."""
    extras, excluded = [], []
    for row in sorted(rows, key=lambda item: (item["group"], item["index"])):
        values = _cost_values(row)
        if not values:
            continue
        core = {"group": row["group"], "index": row["index"], "name": row["name"]}
        if row["triggered"] and not row["reactive"]:
            extras.append(core)
            continue
        if row["reactive"]:
            reason = f"triggered by {_trigger_name(row.get('reactiveBy'))}: rate depends on hits you take"
        else:
            reason = "self-cast: PoB's rate is full cast speed, not how often you cast it"
        excluded.append({**core, "reason": reason, "value": values})
    return extras, excluded


def _validate_conditionals(conditional_config: dict) -> None:
    known = ", ".join(sorted(CONDITIONS))
    for var in sorted(conditional_config):
        entry = conditional_config[var]
        only_if = entry.get("only_if") if isinstance(entry, dict) else None
        if not isinstance(entry, dict) or only_if not in CONDITIONS or "value" not in entry:
            raise ValueError(f"scenario conditional_config {var!r}: unknown or missing only_if "
                             f"{only_if!r}; known: {known}")


def plan_conditional(conditional_config: dict | None, source_lines: list[dict]) -> list[dict]:
    """Plan source-gated config settings without changing engine state."""
    config = conditional_config or {}
    _validate_conditionals(config)
    if not config:
        return []
    matches = [(row, consecrated_source(row["line"])) for row in source_lines]
    matches = [(row, match) for row, match in matches if match is not None]
    matches.sort(key=lambda item: (item[0]["name"], item[0]["line"]))
    source = next((row for row, match in matches if not match["conditional"]), None)
    source_text = f"{source['name']}: {source['line']}" if source else None
    conditional_sources = sorted({
        f"conditional source (off): {row['name']}: {row['line']} ({match['label']})"
        for row, match in matches if match["conditional"]
    })
    return [{"var": var, "value": config[var]["value"], "applied": source is not None,
             "source": source_text, "conditionalSources": conditional_sources}
            for var in sorted(config)]


def consecrated_source(line: str) -> dict | None:
    """Return the first explicit consecrated-ground source matching a complete line."""
    text = line.strip().lower()
    return next((entry for entry in CONSECRATED_SOURCES
                 if entry["pattern"].fullmatch(text)), None)


def source_name(source: str) -> str:
    """Return the item/name prefix of a rendered conditional source."""
    return source.partition(": ")[0]
