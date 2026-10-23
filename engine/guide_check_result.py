"""KPI deltas, chips, locks, and tested guide rows."""

from audit import NO_WORSE_PCT
from rules import WORSE_MARK, rule_name, worsened
from scoring import change_pct

ZERO_LIMIT = 0.1


def _number(value) -> float:
    return value if isinstance(value, (int, float)) else 0


def kpis(auditor, ctx: dict) -> dict:
    out = auditor.main_out(ctx)
    return {"dps": _number(out.get(auditor.dps_key)),
            "ehp": _number(out.get("TotalEHP")),
            "manaMargin": _number(auditor.mana_margin(ctx)),
            "maxHit": _number(out.get("PhysicalMaximumHitTaken"))}


def rule_breaks(auditor, base_ctx: dict, ctx: dict) -> list[str]:
    """New rule breaks plus checks of an already-broken rule that the change makes worse (spec B6)."""
    return auditor.breaks(ctx) + worsened(auditor.rules, base_ctx, ctx)


def build_result(auditor, base_ctx: dict, ctx: dict) -> tuple[dict, dict, list[str]]:
    before, after = kpis(auditor, base_ctx), kpis(auditor, ctx)
    delta = {"dpsPct": change_pct(after["dps"], before["dps"]),
             "ehpPct": change_pct(after["ehp"], before["ehp"]),
             "manaMargin": after["manaMargin"] - before["manaMargin"],
             "maxHit": change_pct(after["maxHit"], before["maxHit"])}
    dims = auditor.dimensions(ctx, base_ctx)
    return {"base": before, "after": after, "delta": delta}, dims, rule_breaks(auditor, base_ctx, ctx)


def is_zero(result: dict, dims: dict, breaks: list[str]) -> bool:
    delta = result["delta"]
    values = (delta.get("dpsPct"), delta.get("ehpPct"), delta.get("maxHit"))
    pct_zero = all(value is None or abs(value) < ZERO_LIMIT for value in values)
    return (pct_zero and abs(delta.get("manaMargin") or 0) < ZERO_LIMIT
            and not dims.get("loses") and not dims.get("weakens") and not breaks)


def _break_reason(violation: str) -> str:
    name = rule_name(violation)
    prefix = f"[{name}]"
    message = violation[len(prefix):].strip() if violation.startswith(prefix) else violation
    if WORSE_MARK in message:
        return f"Makes a rule you already break worse: {name} ({message.replace(WORSE_MARK, '')})"
    return f"Breaks a rule: {name} ({message})"


def _chips(result: dict, breaks: list[str], availability: dict,
           interaction: dict | None, statuses: dict[str, str]) -> list[str]:
    delta = result["delta"]
    dps, ehp = delta.get("dpsPct") or 0, delta.get("ehpPct") or 0
    tradeoff = min(dps, ehp) < NO_WORSE_PCT
    chips = ["trade-off"] if tradeoff else (["helps"] if max(dps, ehp) > 0.1 else [])
    if breaks:
        chips.append("breaks a rule")
    if availability.get("state") == "unobtainable":
        chips.append("unobtainable")
    refs = (interaction or {}).get("vaultRefs") or []
    if any(statuses.get(name) == "draft" for name in refs):
        chips.append("draft note")
    return chips


def assemble_row(row: dict, result: dict, dims: dict, breaks: list[str],
                 availability: dict, interaction: dict | None, breakdown: list[dict],
                 statuses: dict[str, str], league: str, league_date: str | None,
                 node_alone: dict | None = None) -> dict:
    locked, reason = False, None
    if breaks:
        locked, reason = True, _break_reason(breaks[0])
    elif availability.get("state") == "unobtainable":
        date = f" (data {league_date})" if league_date else ""
        locked = True
        reason = f"Not obtainable in {league}: {availability.get('text')}{date}"
    zero = is_zero(result, dims, breaks)
    return {**row, "rank": None, "result": result,
            "chips": _chips(result, breaks, availability, interaction, statuses),
            "locked": locked, "lockReason": reason, "tickable": not locked,
            "sortScore": max(result["delta"].get("dpsPct") or 0,
                             result["delta"].get("ehpPct") or 0),
            "why": [], "breakdown": breakdown, "interaction": interaction,
            "availability": availability, "price": None, "breaks": breaks,
            "nodeAlone": node_alone, "conditional": None,
            "zeroNote": ("PoB shows no effect here; it may still matter for a requirement or a jewel."
                         if zero else None), "dims": dims}


def carries_value(row: dict) -> bool:
    """A zero row stays ranked when it is locked or its own vault refs (rule flags, gap patterns, gem models) apply."""
    return bool(row.get("locked") or (row.get("interaction") or {}).get("carries"))
