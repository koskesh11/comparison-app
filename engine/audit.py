"""Audit a build with gear fixed: ranked improvement candidates, checked against vault rules.

Auditor.run() returns a structured report (used by the GUI); print_report() renders it for the CLI.
"""

import argparse
import json
from datetime import datetime
from collections.abc import Callable
from pathlib import Path

from obtainability import Obtainability
from pobhost import ENGINE_DIR, PobEngine, _lua_str
from models import apply_models, load_models, stat_keys as model_stat_keys
from rules import rule_name, stat_keys, violations
from tree_search import TreeSearch
from vault import load_gap_patterns, load_rules, load_scenarios

SCORE_STATS = ["FullDPS", "TotalEHP", "PhysicalMaximumHitTaken"]
EXTRA_STATS = ["CombinedDPS",  # fast what-ifs skip the FullDPS roll-up
               # sources shown under the KPI tiles
               "Life", "EnergyShield", "Armour", "Evasion", "BlockChance", "SpellBlockChance",
               "PhysicalDamageReduction", "ManaRegenRecovery", "ManaPerSecondCost"]
LOW_VALUE_SHARE = 0.01  # branch worth <1% of every score stat is a re-path candidate
KEEP_NODE_SHARE = 0.005  # small node worth >=0.5% DPS or EHP is kept when re-pathing
NO_WORSE_PCT = -0.1  # a re-path must not lose more than this % of DPS or EHP
DEFAULT_SCENARIO = "Pinnacle Boss"
WEAKEN_SHARE = 0.10  # an ailment stat dropping by 10%+ is shown as a trade-off


def change_pct(new: float, old: float) -> float | None:
    return 100 * (new - old) / old if old else None


def pct(new: float, old: float) -> str:
    value = change_pct(new, old)
    return f"{value:+.1f}%" if value is not None else "n/a"


class Auditor:
    def __init__(self, build_path: Path, include_drafts: bool, progress: Callable[[str], None] = lambda _: None,
                 disabled_skills: list[str] | None = None, scenario: str = DEFAULT_SCENARIO):
        self.progress = progress
        progress("Starting Path of Building")
        self.engine = PobEngine()
        self.build_path = build_path
        self.summary = self.engine.load_build(build_path)
        self.scenarios = load_scenarios()
        if scenario not in self.scenarios:
            raise ValueError(f"unknown scenario {scenario!r}; vault has {sorted(self.scenarios)}")
        self.scenario = scenario
        self.load_audit_hooks(disabled_skills or [])
        all_rules = load_rules()
        self.rules = [r for r in all_rules if r.status == "verified" or include_drafts]
        self.skipped = [r.name for r in all_rules if r not in self.rules]
        self.models = [m for m in load_models() if m.status == "verified" or include_drafts]
        self.keys = sorted(stat_keys(self.rules) | model_stat_keys(self.models) | set(SCORE_STATS) | set(EXTRA_STATS)
                           | set(self.capability_keys))
        self.equipped = set(self.call("equippedTitlesJSON"))
        progress("Loading league data")
        self.obtainable = Obtainability.load()
        self.suggestions: list[dict] = []
        self._base_broken: set[str] | None = None

    def load_audit_hooks(self, disabled_skills: list[str]) -> None:
        """(Re)load audit.lua and leave out skills the user doesn't run in this scenario."""
        self.engine.run(f"dofile({_lua_str((ENGINE_DIR / 'audit.lua').as_posix())})")
        # reservations as saved in the file, before anything is left out (so the user can pick what they run)
        self.reservations = self.call("reservationsJSON")
        self.disabled_skills = self.call("disableSkillsJSON", {"names": disabled_skills}) if disabled_skills else []
        self.dps_after_leave_out = self.raw_main_out().get("FullDPS")
        config = self.scenarios[self.scenario].get("pob_config") or {}
        if config:
            self.call("setConfigJSON", {"config": config})
        self.capability_keys = self.call("capabilityKeysJSON")

    # ---- helpers -------------------------------------------------------------------------

    def evaluate(self, remove_ids: list[int] | None = None, add_ids: list[int] | None = None) -> dict:
        request = json.dumps({"removeNodes": remove_ids or [], "addNodes": add_ids or [], "stats": self.keys})
        return self.adjust(json.loads(self.engine.run(f"return evaluateJSON({_lua_str(request)})")))

    def breaks(self, ctx: dict) -> list[str]:
        """Rule breaks a change *introduces*. Rules the starting build already breaks don't block suggestions."""
        if self._base_broken is None:
            self._base_broken = {rule_name(v) for v in violations(self.rules, self.evaluate())}
        return [v for v in violations(self.rules, ctx) if rule_name(v) not in self._base_broken]

    def raw_main_out(self) -> dict:
        """Main skill output straight from PoB, without vault models."""
        request = json.dumps({"removeNodes": [], "addNodes": [], "stats": ["FullDPS"]})
        return self.main_out(json.loads(self.engine.run(f"return evaluateJSON({_lua_str(request)})")))

    def dps_breakdown(self, final_dps: float) -> list[dict]:
        """How the shown DPS is built up from PoB's own number, step by step."""
        steps = [{"label": "PoB, your file as saved", "dps": self.summary["stats"]["FullDPS"]}]
        if self.disabled_skills:
            steps.append({"label": "Leaving out " + ", ".join(self.disabled_skills), "dps": self.dps_after_leave_out})
        config = self.scenarios[self.scenario].get("pob_config") or {}
        if config:
            steps.append({"label": f"Scenario {self.scenario}: " + ", ".join(f"{k}={v}" for k, v in config.items()),
                          "dps": self.raw_main_out().get("FullDPS")})
        applied = [m for k in self.evaluate()["skills"] for m in k.get("models", [])]
        for m in applied:
            hits = f"{m['multiplier']} hits (expected {m['expected']:.2f}, rounded down; range {m['range'][0]}-{m['range'][1]})"
            note = (f"{hits}, agrees with your PoB count {m['pobCount']}" if m["multiplier"] == m["pobCount"]
                    else f"{hits} replaces your PoB count {m['pobCount']}")
            steps.append({"label": f"Model: {m['model']}: {note}", "dps": None})
        if applied:
            steps[-1]["dps"] = final_dps
        return steps

    def adjust(self, ctx: dict) -> dict:
        """Apply vault Models (mechanics PoB doesn't calculate) to a calculated context."""
        return apply_models(self.models, ctx, self.equipped)

    def call(self, function: str, request: dict | None = None):
        arg = _lua_str(json.dumps(request)) if request is not None else ""
        return json.loads(self.engine.run(f"return {function}({arg})"))

    @staticmethod
    def main_out(ctx: dict) -> dict:
        return next(s for s in ctx["skills"] if s["isMain"])["out"]

    @staticmethod
    def mana_margin(ctx: dict) -> float:
        """Mana regen left after every skill used together has paid its cost per second."""
        regen = Auditor.main_out(ctx).get("ManaRegenRecovery") or 0
        return regen - sum(s["out"].get("ManaPerSecondCost") or 0 for s in ctx["skills"])

    @staticmethod
    def main_models(ctx: dict) -> list[dict]:
        return next(s for s in ctx["skills"] if s["isMain"]).get("models", [])

    def dimensions(self, ctx: dict, base_ctx: dict, dps_key: str = "FullDPS") -> dict:
        out, base = self.main_out(ctx), self.main_out(base_ctx)
        return {
            "dps": change_pct(out[dps_key] or 0, base[dps_key] or 0),
            "ehp": change_pct(out["TotalEHP"] or 0, base["TotalEHP"] or 0),
            "physMaxHit": change_pct(out["PhysicalMaximumHitTaken"] or 0, base["PhysicalMaximumHitTaken"] or 0),
            "manaFrom": self.mana_margin(base_ctx),
            "manaTo": self.mana_margin(ctx),
            # model results (e.g. Winter Orb hits) before -> after, so AoE/projectile changes are visible
            "models": [{"model": b["model"], "from": b["multiplier"], "to": a["multiplier"]}
                       for b, a in zip(self.main_models(base_ctx), self.main_models(ctx))],
            "loses": [k for k in self.capability_keys if (base.get(k) or 0) > 0 and (out.get(k) or 0) <= 0],
            # ailment chance/effect/duration that gets noticeably weaker (not just disappears)
            "weakens": [f"{k} {change_pct(out.get(k) or 0, base[k]):+.0f}%" for k in self.capability_keys
                        if (base.get(k) or 0) > 0 and 0 < (out.get(k) or 0) <= base[k] * (1 - WEAKEN_SHARE)],
        }

    def suggest(self, change: dict) -> int:
        """Register an applicable change; returns its 1-based id."""
        self.suggestions.append(change)
        return len(self.suggestions)

    # ---- tests ---------------------------------------------------------------------------

    def gem_levels(self, base_ctx: dict) -> list[dict]:
        targets = {}
        for gem in self.call("listMainGemsJSON"):
            better = [v for v in self.obtainable.best_gem_variants(gem["name"])
                      if (v.level, v.quality) != (gem["level"], gem["quality"])
                      and v.level >= gem["level"] and v.quality >= gem["quality"]]
            if better:
                targets[gem["name"]] = [{"level": v.level, "quality": v.quality} for v in better]
        if not targets:
            return []
        rows = []
        for g in self.call("auditGemLevelsJSON", {"stats": self.keys, "targets": targets})["gems"]:
            g["ctx"] = self.adjust(g["ctx"])
            broken = self.breaks(g["ctx"])
            change = {"type": "gem", "name": g["gem"], "level": g["toLevel"], "quality": g["toQuality"]}
            diffs = self.call("gemStatDiffJSON", {"name": g["gem"],
                                                  "from": {"level": g["fromLevel"], "quality": g["fromQuality"]},
                                                  "to": {"level": g["toLevel"], "quality": g["toQuality"]}})
            rows.append({
                "id": None if broken else self.suggest(change), "gem": g["gem"], "from": g["from"], "to": g["to"],
                "dims": self.dimensions(g["ctx"], base_ctx, "CombinedDPS"), "rejected": broken,
                "statChanges": [{"from": d["fromText"] or d["stat"], "to": d["toText"] or d["stat"]} for d in diffs[:3]],
            })
        return rows

    def support_swaps(self, top: int = 10) -> dict:
        protected = sorted({s for r in self.rules for s in (r.spec.get("when") or {}).get("linked_support_any") or []})
        result = self.call("auditSupportSwapsJSON", {"stats": self.keys, "protected": protected})
        result["base"] = self.adjust(result["base"])
        for swap in result["swaps"]:
            swap["ctx"] = self.adjust(swap["ctx"])
        base = self.main_out(result["base"])
        valid, rejected, unobtainable = [], 0, 0
        for swap in result["swaps"]:
            if not self.obtainable.gem_obtainable(swap["with"]):
                unobtainable += 1
            elif self.breaks(swap["ctx"]):
                rejected += 1
            else:
                valid.append((self.main_out(swap["ctx"])["CombinedDPS"] - base["CombinedDPS"], swap))
        valid.sort(key=lambda v: v[0], reverse=True)
        items = [{
            "id": self.suggest({"type": "swap", "replaced": swap["replaced"], "with": swap["with"]}),
            "replaced": swap["replaced"], "with": swap["with"],
            "dims": self.dimensions(swap["ctx"], result["base"], "CombinedDPS"),
        } for gain, swap in valid[:top] if gain > 0]
        return {"tried": len(result["swaps"]), "unobtainable": unobtainable, "rejected": rejected,
                "protected": protected, "items": items}

    def wasted_mods(self, base_ctx: dict) -> dict:
        mods = self.call("auditWastedModsJSON")
        gaps = load_gap_patterns()
        crit_capped = any((k["out"].get("CritChance") or 0) >= 100 for k in base_ctx["skills"])

        def blind_spot(mod: dict) -> str | None:
            for g in gaps:
                if g["match"].lower() in mod["line"].lower() and g.get("slot", "") in mod["slot"]:
                    return g["why"]
            return None

        groups = {"wasted": [], "uniquePackage": [], "conditional": [], "overcapped": [], "cantMeasure": [], "unparsed": []}
        for m in mods:
            row = {"slot": m["slot"], "item": m["item"], "line": m["line"], "why": ""}
            fixed_line = m["rarity"] in ("UNIQUE", "RELIC") and not m["crafted"]
            if m["unsupported"]:
                groups["unparsed"].append(row)
            elif m["changed"] == 0:
                why = blind_spot(m)
                if fixed_line:
                    # a unique is a package: its lines can't be rerolled away, so never "wasted"
                    groups["uniquePackage"].append({**row, "why": why or "no effect in PoB: drawback, irrelevant here, "
                                                                          "or something PoB can't measure"})
                elif why:
                    groups["cantMeasure"].append({**row, "why": why})
                elif m["conditions"]:
                    groups["conditional"].append({**row, "why": "only when: " + ", ".join(m["conditions"])
                                                  + " (off in PoB config)"})
                elif crit_capped and "critical strike chance" in m["line"].lower():
                    groups["overcapped"].append({**row, "why": "crit already 100%"})
                else:
                    groups["wasted"].append(row)
        return {"checked": len(mods), "groups": groups}

    def repath(self, base_ctx: dict, max_rounds: int = 4) -> dict:
        base = self.main_out(base_ctx)
        keep = [node_id for node_id in self.call("listAllocatedNormalJSON") if self.node_value(node_id, base) >= KEEP_NODE_SHARE]
        for _ in range(max_rounds):
            plan = self.call("repathJSON", {"keep": keep})
            if "error" in plan:
                return {"status": "failed", "message": plan["error"]}
            saved = plan["currentPoints"] - plan["newPoints"]
            if saved <= 0:
                return {"status": "none", "message": f"no cheaper path ({plan['currentPoints']} points)"}
            ctx = self.evaluate(plan["removeIds"], plan["addIds"])
            if not self.breaks(ctx):
                dims = self.dimensions(ctx, base_ctx)
                if min(dims["dps"] or 0, dims["ehp"] or 0) < NO_WORSE_PCT:
                    return {"status": "none", "message": f"cheaper path exists ({saved} points) but loses "
                            f"DPS {dims['dps']:+.1f}% / EHP {dims['ehp']:+.1f}%"}
                return {"status": "found", "currentPoints": plan["currentPoints"], "newPoints": plan["newPoints"],
                        "id": self.suggest({"type": "repath", "removeIds": plan["removeIds"], "addIds": plan["addIds"]}),
                        "dims": self.dimensions(ctx, base_ctx), "drop": plan["removed"], "take": plan["added"]}
            needed = [i for i in plan["removeIds"] if self.breaks(self.evaluate([i]))]
            if not needed:
                # nodes only break a rule together: keep the one with the biggest effect on rule stats
                rule_stats = stat_keys(self.rules)

                def impact(node_id: int) -> float:
                    out = self.main_out(self.evaluate([node_id]))
                    return sum(abs((out.get(k) or 0) - (base.get(k) or 0)) / max(abs(base.get(k) or 0), 1)
                               for k in rule_stats)
                needed = [max(plan["removeIds"], key=impact)]
            keep += needed
        return {"status": "none", "message": f"no valid cheaper path after {max_rounds} rounds"}

    def node_value(self, node_id: int, base: dict) -> float:
        """Largest relative DPS/EHP loss from removing one node."""
        out = self.main_out(self.evaluate([node_id]))
        return max((base[k] - (out[k] or 0)) / base[k] for k in ("FullDPS", "TotalEHP") if base[k])

    def branches(self, base_ctx: dict) -> list[dict]:
        base = self.main_out(base_ctx)
        rows = []
        for b in self.call("listBranchesJSON"):
            ctx = self.evaluate(b["removeIds"])
            out = self.main_out(ctx)
            shares = [abs((out[k] or 0) - base[k]) / base[k] for k in SCORE_STATS if base[k]]
            # only low-value branches that can actually go (removing them breaks no rule)
            if max(shares) < LOW_VALUE_SHARE and not self.breaks(ctx):
                rows.append({"name": b["name"], "points": b["points"], "dims": self.dimensions(ctx, base_ctx),
                             "required": [], "lowValue": True})
        return sorted(rows, key=lambda r: r["name"])

    def kpi_sources(self, base_ctx: dict) -> dict:
        """Where each headline number comes from (all values straight from PoB's output)."""
        out = self.main_out(base_ctx)
        num = lambda k: out.get(k) or 0  # noqa: E731
        drains = [{"label": f"{s['name']} cost", "value": -(s["out"].get("ManaPerSecondCost") or 0)}
                  for s in base_ctx["skills"] if s["out"].get("ManaPerSecondCost")]
        return {
            "ehp": [{"label": "PoB Total EHP (enemy hits until death, all layers)", "value": num("TotalEHP")},
                    {"label": "Life", "value": num("Life")}, {"label": "Energy Shield", "value": num("EnergyShield")},
                    {"label": "Armour", "value": num("Armour")}, {"label": "Evasion", "value": num("Evasion")},
                    {"label": "Block / Spell block %", "value": f"{num('BlockChance'):.0f} / {num('SpellBlockChance'):.0f}"}],
            "physMaxHit": [{"label": "PoB max physical hit you survive", "value": num("PhysicalMaximumHitTaken")},
                           {"label": "Phys damage reduction %", "value": f"{num('PhysicalDamageReduction'):.0f}"},
                           {"label": "Life + ES pool", "value": num("Life") + num("EnergyShield")}],
            "manaMargin": [{"label": "Mana regen (PoB)", "value": num("ManaRegenRecovery")}, *drains,
                           {"label": "= margin per second", "value": self.mana_margin(base_ctx)}],
        }

    def run(self) -> dict:
        base_ctx = self.evaluate()
        base = self.main_out(base_ctx)
        report = {
            "disabledSkills": self.disabled_skills,
            "scenario": {"name": self.scenario, "config": self.scenarios[self.scenario].get("pob_config") or {}},
            "build": {**self.summary, "skills": [k["name"] for k in base_ctx["skills"]], "league": self.obtainable.league,
                      # which file version was analysed, so a mismatch with what's open in PoB is visible
                      "file": str(self.build_path),
                      "savedAt": datetime.fromtimestamp(self.build_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")},
            "rules": {"active": [r.name for r in self.rules], "skipped": self.skipped,
                      "currentViolations": violations(self.rules, base_ctx)},
            "models": [m for k in base_ctx["skills"] for m in k.get("models", [])],
            "dpsBreakdown": self.dps_breakdown(base["FullDPS"]),
            "kpiSources": self.kpi_sources(base_ctx),
            "reservation": {**self.reservations,
                            "overReserved": (self.reservations.get("manaUnreserved") or 0) < 0
                            or (self.reservations.get("lifeUnreserved") or 0) < 0},
            "base": {"dps": base["FullDPS"], "ehp": base["TotalEHP"], "physMaxHit": base["PhysicalMaximumHitTaken"],
                     "manaMargin": self.mana_margin(base_ctx)},
        }
        steps = [("gems", "Testing gem upgrades", lambda: self.gem_levels(base_ctx)),
                 ("swaps", "Testing support gem swaps", self.support_swaps),
                 ("mods", "Checking gear and flask mods", lambda: self.wasted_mods(base_ctx)),
                 ("repath", "Searching cheaper tree paths", lambda: self.repath(base_ctx)),
                 ("treeSwaps", "Searching notable swaps", lambda: TreeSearch(self).run(base_ctx)),
                 ("branches", "Checking tree branches", lambda: self.branches(base_ctx))]
        report["sections"] = {}
        for key, label, step in steps:
            self.progress(label)
            report["sections"][key] = step()
        report["suggestions"] = self.suggestions
        return report


# ---- CLI rendering ---------------------------------------------------------------------------

def fmt_dims(d: dict) -> str:
    part = lambda v: f"{v:+.1f}%" if v is not None else "n/a"  # noqa: E731
    loses = f" | LOSES: {', '.join(d['loses'])}" if d.get("loses") else ""
    loses += f" | WEAKENS: {', '.join(d['weakens'])}" if d.get("weakens") else ""
    loses += "".join(f" | hits {m['from']} -> {m['to']}" for m in d.get("models", []))
    return f"DPS {part(d['dps'])} | EHP {part(d['ehp'])} | mana margin {d['manaFrom']:+.0f} -> {d['manaTo']:+.0f}/s{loses}"


def print_report(report: dict) -> None:
    b, r, s = report["build"], report["rules"], report["sections"]
    print(f"== {b['buildName']} ({b['ascendancy']}), skills used together: {', '.join(b['skills'])}")
    print(f"   file: {b['file']} (saved {b['savedAt']})")
    print(f"   scenario: {report['scenario']['name']} {report['scenario']['config']}"
          + (f" | left out: {', '.join(report['disabledSkills'])}" if report["disabledSkills"] else ""))
    print(f"   rules: {len(r['active'])} active" + (f", skipped (draft): {', '.join(r['skipped'])}" if r["skipped"] else ""))
    for step in report.get("dpsBreakdown", []):
        value = f"{step['dps']:,.0f}" if step["dps"] is not None else ""
        print(f"   DPS  {value:>14}  {step['label']}")
    for m in report.get("models", []):
        print(f"   model: {m['model']}: {m['multiplier']} hits (expected {m['expected']:.2f}, rounded down), range {m['range']} (your PoB count: {m['pobCount']})")
    for v in r["currentViolations"]:
        print(f"   !! current build breaks: {v}")

    print(f"\n-- Gem upgrades (only variants seen in {b['league']})")
    for g in s["gems"] or [{"none": True}]:
        if g.get("none"):
            print("   all gems already at the best obtainable level/quality")
            break
        tag = f"[{g['id']}]" if g["id"] else "   "
        print(f"   {tag} {g['gem']} {g['from']} -> {g['to']}: {fmt_dims(g['dims'])}"
              + (f"  REJECTED: {g['rejected'][0]}" if g["rejected"] else ""))
        for c in g["statChanges"]:
            print(f"         {c['from']}  ->  {c['to']}")

    sw = s["swaps"]
    print(f"\n-- Support gem swaps ({sw['tried']} tried, {sw['unobtainable']} not in {b['league']},"
          f" {sw['rejected']} break a rule, protected: {', '.join(sw['protected']) or '-'})")
    for item in sw["items"]:
        print(f"   [{item['id']}] {item['replaced']} -> {item['with']}: {fmt_dims(item['dims'])}")
    if not sw["items"]:
        print("   no swap beats the current links")

    mods = s["mods"]
    print(f"\n-- Gear & flask mods ({mods['checked']} checked)")
    for label, rows in mods["groups"].items():
        print(f"   [{label}] {len(rows)}")
        for m in rows:
            print(f"      {m['slot']:<10} {m['item'][:28]:<28} {m['line']}" + (f"  ({m['why']})" if m["why"] else ""))

    rp = s["repath"]
    print("\n-- Re-path (keep notables/keystones/masteries/jewels + small nodes that matter)")
    if rp["status"] == "found":
        print(f"   [{rp['id']}] {rp['currentPoints']} -> {rp['newPoints']} points: {fmt_dims(rp['dims'])}")
        print(f"      drop: {', '.join(rp['drop'])}\n      take: {', '.join(rp['take']) or '-'}")
    else:
        print(f"   {rp['message']}")

    tree = s["treeSwaps"]
    print(f"\n-- Passive tree (PoB power report: {tree['nodesScored']} nodes, {tree['masteriesScored']} masteries scored)")
    for objective, label in (("dps", "DPS"), ("ehp", "EHP")):
        print(f"   Best additions for {label} per point (PoB path power):")
        for a in tree["bestAdditions"][objective][:5]:
            print(f"      {a['name']:<30} {a['points']} pts  DPS {a['gain']['dps']:+.1f}%  EHP {a['gain']['ehp']:+.1f}%")
        print(f"   Swaps for {label}:")
        for t in tree["swaps"][objective] or []:
            print(f"   [{t['id']}] drop {t['drop']} ({t['dropPoints']} pts) -> take {', '.join(t['take'])}")
            for label_, details in (("drop", t.get("dropDetails", [])), ("take", t.get("takeDetails", []))):
                for d in details:
                    print(f"         {label_}: {d}")
            for w in t.get("why", []):
                print(f"         why: {w}")
            for w in t.get("warnings", []):
                print(f"         !! {w}")
            if t.get("unspentPoints"):
                print(f"         !! {t['unspentPoints']} point(s) left unspent")
            print(f"         {fmt_dims(t['dims'])}")
        if not tree["swaps"][objective]:
            print("      none that passes every rule")
    print("   Mastery options:")
    for m in tree["masteries"]:
        print(f"   [{m['id']}] {m['mastery']}: '{m['from']}' -> '{m['to']}': {fmt_dims(m['dims'])}")
    if not tree["masteries"]:
        print("      current choices are the best")

    print("\n-- Tree branches")
    for row in s["branches"]:
        flag = "REQUIRED: " + "; ".join(row["required"]) if row["required"] else "low value, re-path candidate"
        print(f"   {row['name']:<28} {row['points']:>2} pts | {fmt_dims(row['dims'])}  {flag}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("build", type=Path)
    parser.add_argument("--include-drafts", action="store_true", help="also apply draft vault rules")
    parser.add_argument("--leave-out", action="append", default=[], help="skill to leave out, e.g. 'Aspect of the Brine King'")
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO, help="vault scenario, e.g. Mapping")
    args = parser.parse_args()
    print_report(Auditor(args.build.resolve(), args.include_drafts, disabled_skills=args.leave_out,
                         scenario=args.scenario).run())
