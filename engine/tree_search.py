"""Passive tree + mastery search built on PoB's own PowerBuilder (the heatmap / Power Report engine).

PoB scores every node (and the whole path to it) and every option of unallocated masteries. This module
turns that into swaps: drop the branches that cost the least, spend every freed point on the best paths.
Every candidate is then calculated exactly, checked for tree connectivity and against vault rules, and
explained by the PoB modifier sources that change ("why").
"""

from dataclasses import dataclass

POWER_STATS = ["FullDPS", "TotalEHP"]
OBJECTIVES = {"dps": "FullDPS", "ehp": "TotalEHP"}  # each objective gets its own best swaps (trade-offs)
OTHER = {"dps": "ehp", "ehp": "dps"}
MAX_DISTANCE = 8            # PoB nodePowerMaxDepth
MAX_BRANCH_POINTS = 12      # bigger branches are trunks, not swap candidates
REMOVAL_CANDIDATES = 15     # cheapest branches / strongest additions tried per objective
SWAPS_PER_OBJECTIVE = 3
MIN_GAIN_PCT = 0.5
WHY_LINES = 4
RECOVERY_WORDS = ("leech", "regenerat", "recoup", "recover")


@dataclass(frozen=True)
class Option:
    node_id: int
    name: str
    ids: tuple[int, ...]   # path (additions) or dependents (removals)
    gain: dict             # objective -> % change of the whole path/branch
    notable: bool


def power_pct(node: dict, stat: str, base: dict) -> float:
    p = node["power"].get(stat) or {}
    value = p.get("path") if p.get("path") is not None else p.get("single") or 0
    return 100 * value / base[stat] if base[stat] else 0.0


def acceptable(dims: dict, objective: str) -> bool:
    """Gains enough, and doesn't give away more of the other dimension than it gains (no lopsided trades)."""
    gain = dims[objective] or 0
    other_loss = -(dims[OTHER[objective]] or 0)
    return gain >= MIN_GAIN_PCT and other_loss <= gain


class TreeSearch:
    def __init__(self, auditor):
        self.a = auditor

    def power_report(self) -> dict:
        self.a.progress("Running PoB power report (every node and mastery)")
        return self.a.call("powerReportJSON", {"stats": POWER_STATS, "maxDist": MAX_DISTANCE})

    def options(self, report: dict, base: dict) -> tuple[list[Option], list[Option]]:
        adds, removes = [], []
        candidates = {int(i): n for i, n in report["nodes"].items()
                      if n["alloc"] or (n.get("dist") and n["type"] in ("Notable", "Keystone", "Normal"))}
        paths = self.a.call("nodePathsJSON", {"ids": list(candidates)})
        for node_id, node in candidates.items():
            ids = tuple(paths.get(str(node_id)) or ())
            if not ids:
                continue
            gain = {obj: power_pct(node, stat, base) for obj, stat in OBJECTIVES.items()}
            option = Option(node_id, node["name"], ids, gain, node["type"] != "Normal")
            if node["alloc"] and option.notable and len(ids) <= MAX_BRANCH_POINTS:
                removes.append(option)  # gain here is what removing it does (<= 0)
            elif not node["alloc"]:
                adds.append(option)
        return adds, removes

    def exact(self, base_ctx: dict, remove_ids: list[int], add_ids: list[int]) -> dict | None:
        if not self.a.call("treeConnectedJSON", {"removeIds": remove_ids, "addIds": add_ids})["connected"]:
            return None
        ctx = self.a.evaluate(remove_ids, add_ids)
        if self.a.breaks(ctx):
            return None
        return {"ctx": ctx, "dims": self.a.dimensions(ctx, base_ctx)}

    @staticmethod
    def fill(budget: int, used: set, ranked: list[Option], picks: list[Option]) -> int:
        """Spend the remaining points greedily (best value per point first); returns points left."""
        for add in ranked:
            if budget <= 0:
                break
            new = set(add.ids) - used  # shared path nodes are only paid once
            if new and len(new) <= budget:
                picks.append(add)
                used |= set(add.ids)
                budget -= len(new)
        return budget

    def candidate(self, objective: str, drops: list[Option], picks: list[Option], ranked: list[Option],
                  base_ctx: dict) -> dict | None:
        removed = sorted({i for d in drops for i in d.ids})
        used = set(removed) | {i for p in picks for i in p.ids}
        spent = len({i for p in picks for i in p.ids})
        left = self.fill(len(removed) - spent, used, ranked, picks)  # no freed point stays unspent
        add_ids = list(dict.fromkeys(i for p in picks for i in p.ids))
        result = self.exact(base_ctx, removed, add_ids)
        if not result or not acceptable(result["dims"], objective):
            return None
        return {"drop": " + ".join(d.name for d in drops), "dropPoints": len(removed),
                "take": [f"{p.name} ({len(set(p.ids) - set(removed))} pts)" for p in picks],
                "dropNodes": [d.node_id for d in drops], "takeNodes": [p.node_id for p in picks],
                "removeIds": removed, "addIds": add_ids, "unspentPoints": max(left, 0), **result}

    def swaps_for(self, objective: str, adds: list[Option], removes: list[Option], base_ctx: dict) -> list[dict]:
        per_point = lambda o: o.gain[objective] / len(o.ids)  # noqa: E731
        ranked = sorted((o for o in adds if o.gain[objective] > 0), key=per_point, reverse=True)
        cheapest = sorted(removes, key=lambda o: -o.gain[objective] / len(o.ids))
        found = []
        # removal-first: drop one cheap branch, refill its points
        for rem in cheapest[:REMOVAL_CANDIDATES]:
            found.append(self.candidate(objective, [rem], [], ranked, base_ctx))
        # addition-first: fund one strong notable by dropping the cheapest branches (several if needed)
        for add in [o for o in ranked if o.notable][:REMOVAL_CANDIDATES]:
            needed, drops, dropped = len(add.ids), [], set()
            for rem in cheapest:
                if needed <= 0:
                    break
                if not set(rem.ids) & (dropped | set(add.ids)):
                    drops.append(rem)
                    dropped |= set(rem.ids)
                    needed -= len(rem.ids)
            if needed <= 0 and drops:
                found.append(self.candidate(objective, drops, [add], ranked, base_ctx))
        found = [f for f in found if f]
        found.sort(key=lambda f: f["dims"][objective] or 0, reverse=True)
        unique = {tuple(f["addIds"]) + (-1,) + tuple(f["removeIds"]): f for f in found}
        return list(unique.values())[:SWAPS_PER_OBJECTIVE]

    def explain(self, swaps: dict) -> None:
        """Attach node texts and the PoB modifier sources that actually change (why it helps)."""
        ids = {i for lst in swaps.values() for s in lst for i in s["dropNodes"] + s["takeNodes"]}
        stats = self.a.call("nodeStatsJSON", {"ids": sorted(ids)}) if ids else {}
        for lst in swaps.values():
            for s in lst:
                s["dropDetails"] = [stats.get(str(i), "") for i in s["dropNodes"]]
                s["takeDetails"] = [stats.get(str(i), "") for i in s["takeNodes"]]
                diffs = self.a.call("whyJSON", {"removeIds": s["removeIds"], "addIds": s["addIds"]})
                s["why"] = [f"{d['type']} {d['stat']} {d['from']:g} -> {d['to']:g} ({d['source']})" for d in diffs[:WHY_LINES]]
                # PoB's EHP is a hit pool: it ignores recovery, so dropping leech/regen looks free when it isn't
                dropped_text = " ".join(s["dropDetails"]).lower()
                s["warnings"] = [f"drops {word} — PoB's EHP doesn't count recovery, so the EHP number understates the loss"
                                 for word in RECOVERY_WORDS if word in dropped_text][:1]

    def masteries(self, base_ctx: dict) -> list[dict]:
        self.a.progress("Comparing every mastery option")
        rows = []
        for mastery in self.a.call("masteryOptionsJSON", {"stats": self.a.keys}):
            for option in mastery["options"]:
                ctx = self.a.adjust(option["ctx"])
                dims = self.a.dimensions(ctx, base_ctx, "CombinedDPS")
                if self.a.breaks(ctx) or not (acceptable(dims, "dps") or acceptable(dims, "ehp")):
                    continue
                rows.append({"id": self.a.suggest({"type": "mastery", "masteryId": mastery["masteryId"],
                                                   "effectId": option["effectId"], "name": mastery["name"]}),
                             "mastery": mastery["name"], "from": mastery["current"], "to": option["text"], "dims": dims})
        return sorted(rows, key=lambda r: max(r["dims"]["dps"] or 0, r["dims"]["ehp"] or 0), reverse=True)

    def run(self, base_ctx: dict) -> dict:
        base = self.a.main_out(base_ctx)
        report = self.power_report()
        adds, removes = self.options(report, base)
        swaps = {}
        for objective in OBJECTIVES:
            self.a.progress(f"Searching tree swaps for {objective.upper()}")
            swaps[objective] = [{**s, "id": self.a.suggest({"type": "repath", "removeIds": s["removeIds"], "addIds": s["addIds"]})}
                                for s in self.swaps_for(objective, adds, removes, base_ctx)]
        self.explain(swaps)
        notables = [o for o in adds if o.notable]
        top_adds = {obj: [{"name": o.name, "points": len(o.ids), "gain": o.gain}
                          for o in sorted(notables, key=lambda o: o.gain[obj] / len(o.ids), reverse=True)[:8]]
                    for obj in OBJECTIVES}
        return {"swaps": swaps, "masteries": self.masteries(base_ctx), "bestAdditions": top_adds,
                "nodesScored": len(report["nodes"]), "masteriesScored": len(report["masteries"])}
