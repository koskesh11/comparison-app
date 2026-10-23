"""Audit a build with gear fixed: ranked improvement candidates, checked against vault rules.

Auditor.run() returns a structured report (used by the GUI); print_report() renders it for the CLI.
"""

import argparse
import hashlib
import json
from datetime import datetime
from collections.abc import Callable
from pathlib import Path

import costs
import part_variants
import unobtainable
from display import fmt, fmt_pct
from obtainability import Obtainability
from pobhost import ENGINE_DIR, PobEngine, _lua_str
from models import apply_models, load_models, stat_keys as model_stat_keys
from rules import rule_name, stat_keys, violations
from scoring import (base_skill_rows, change_pct, dps_key, dps_measure, pct, skill_changes,
                     skill_out, skill_pcts_text, tile_text)
from tree_search import TreeSearch
from vault import load_gap_patterns, load_rules, load_scenarios

SCORE_STATS = ["FullDPS", "TotalEHP", "PhysicalMaximumHitTaken"]
EXTRA_STATS = ["CombinedDPS", "SkillTriggerRate", "TriggerRateCap", "EffectiveSourceRate", "ProjectileCount",
               # sources shown under the KPI tiles
               "Life", "EnergyShield", "Armour", "Evasion", "BlockChance", "SpellBlockChance",
               "PhysicalDamageReduction", "ManaRegenRecovery", "ManaPerSecondCost", *costs.STAT_KEYS]
LOW_VALUE_SHARE = 0.01  # branch worth <1% of every score stat is a re-path candidate
KEEP_NODE_SHARE = 0.005  # small node worth >=0.5% DPS or EHP is kept when re-pathing
NO_WORSE_PCT = -0.1  # a re-path must not lose more than this % of DPS or EHP
DEFAULT_SCENARIO = "Pinnacle Boss"
WEAKEN_SHARE = 0.10  # an ailment stat dropping by 10%+ is shown as a trade-off


def protected_supports(rules: list) -> list[str]:
    return sorted({support for rule in rules
                   for support in (rule.spec.get("when") or {}).get("linked_support_any") or []})


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Auditor:
    multi_part = False

    def __init__(self, build_path: Path, include_drafts: bool, progress: Callable[[str], None] = lambda _: None,
                 disabled_skills: list[str] | None = None, scenario: str = DEFAULT_SCENARIO):
        self.progress = progress
        progress("Starting Path of Building")
        self.engine = PobEngine()
        self.build_path = build_path
        self.source_sha256 = file_sha256(build_path)
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
        self.extra_skills, self.excluded_costs = costs.classify_other_skills(
            self.call("otherSkillsJSON", {"stats": costs.STAT_KEYS}))
        self.equipped = set(self.call("equippedTitlesJSON"))
        ctx = self.evaluate()
        self.dps_measure = dps_measure(ctx)
        self.multi_part = any((skill.get("partCount") or 0) >= 2 for skill in ctx["skills"])
        self.dps_key = self.dps_measure["key"]
        progress("Loading league data")
        self.obtainable = Obtainability.load()
        self.suggestions: list[dict] = []
        self._base_broken: set[str] | None = None
        self._swap_levels: dict[str, dict] | None = None
        self._shown_dims: dict[tuple[tuple[int, ...], tuple[int, ...]], dict] = {}

    def load_audit_hooks(self, disabled_skills: list[str]) -> None:
        """(Re)load audit.lua and leave out skills the user doesn't run in this scenario."""
        self.engine.run(f"dofile({_lua_str((ENGINE_DIR / 'audit.lua').as_posix())})")
        # reservations as saved in the file, before anything is left out (so the user can pick what they run)
        self.reservations = self.call("reservationsJSON")
        self.disabled_skills = self.call("disableSkillsJSON", {"names": disabled_skills}) if disabled_skills else []
        self.dps_after_leave_out = self.raw_dps()
        config = self.scenarios[self.scenario].get("pob_config") or {}
        if config:
            self.call("setConfigJSON", {"config": config})
        self.dps_after_config = self.raw_dps() if config else None
        self.conditional = self.apply_conditional_config()
        applied = any(row["applied"] for row in self.conditional)
        self.dps_after_conditional = self.raw_dps() if applied else None
        self.capability_keys = self.call("capabilityKeysJSON")

    def apply_conditional_config(self) -> list[dict]:
        cfg = self.scenarios[self.scenario].get("conditional_config") or {}
        if not cfg:
            return []
        lines = self.call("consecratedSourcesJSON")["lines"]
        plan = costs.plan_conditional(cfg, lines)
        applied = {row["var"]: row["value"] for row in plan if row["applied"]}
        if applied:
            self.call("setConfigJSON", {"config": applied})
        return plan

    # ---- helpers -------------------------------------------------------------------------

    def extra_request(self) -> list[dict]:
        return [{"group": row["group"], "index": row["index"]} for row in self.extra_skills]

    def evaluate(self, remove_ids: list[int] | None = None, add_ids: list[int] | None = None,
                 parts: bool = False) -> dict:
        values = {"removeNodes": remove_ids or [], "addNodes": add_ids or [], "stats": self.keys,
                  "extraSkills": self.extra_request()}
        if parts and self.multi_part:
            values["partVariants"] = True
        request = json.dumps(values)
        return self.adjust(json.loads(self.engine.run(f"return evaluateJSON({_lua_str(request)})")))

    def with_parts(self, request: dict) -> dict:
        return {**request, "partVariants": True} if self.multi_part else request

    def base_context(self) -> dict:
        if not self.multi_part:
            return self.evaluate()
        ctx = self.evaluate(parts=True)
        self.multi_part = bool(ctx.get("byPart"))
        return ctx

    def breaks(self, ctx: dict) -> list[str]:
        """Rule breaks a change *introduces*. Rules the starting build already breaks don't block suggestions."""
        if self._base_broken is None:
            self._base_broken = {rule_name(v) for v in violations(self.rules, self.evaluate())}
        return [v for v in violations(self.rules, ctx) if rule_name(v) not in self._base_broken]

    def raw_main_out(self) -> dict:
        """Main skill output straight from PoB, without vault models."""
        request = json.dumps({"removeNodes": [], "addNodes": [],
                              "stats": ["FullDPS", "CombinedDPS"]})
        return self.main_out(json.loads(self.engine.run(f"return evaluateJSON({_lua_str(request)})")))

    def raw_dps(self) -> float | None:
        out = self.raw_main_out()
        return out.get(dps_key(out))

    def dps_breakdown(self, final_dps: float) -> list[dict]:
        """How the shown DPS is built up from PoB's own number, step by step."""
        stats = self.summary["stats"]
        steps = [{"label": "PoB, your file as saved", "dps": stats.get(dps_key(stats))}]
        if self.disabled_skills:
            steps.append({"label": "Leaving out " + ", ".join(self.disabled_skills), "dps": self.dps_after_leave_out})
        config = self.scenarios[self.scenario].get("pob_config") or {}
        if config:
            steps.append({"label": f"Scenario {self.scenario}: " + ", ".join(f"{k}={v}" for k, v in config.items()),
                          "dps": self.dps_after_config})
        for row in sorted((item for item in self.conditional if item["applied"]), key=lambda item: item["var"]):
            label = (f"Scenario {self.scenario}: {row['var']}={str(row['value']).lower()} "
                     f"(source: {costs.source_name(row['source'])})")
            steps.append({"label": label, "dps": self.dps_after_conditional})
        applied = [m for k in self.evaluate()["skills"] for m in k.get("models", [])]
        for m in applied:
            hits = (f"{m['multiplier']} hits (expected {fmt(m['expected'], 2)}, rounded down; "
                    f"range {m['range'][0]}-{m['range'][1]})")
            note = (f"{hits}, agrees with your PoB count {m['pobCount']}" if m["multiplier"] == m["pobCount"]
                    else f"{hits} replaces your PoB count {m['pobCount']}")
            steps.append({"label": f"Model: {m['model']}: {note}", "dps": None})
        if applied:
            steps[-1]["dps"] = final_dps
        return steps

    def adjust(self, ctx: dict) -> dict:
        """Apply vault Models (mechanics PoB doesn't calculate) to a calculated context."""
        result = apply_models(self.models, ctx, self.equipped)
        if "byPart" in ctx:
            result = {**result, "byPart": [
                {**row, "ctx": apply_models(self.models, row["ctx"], self.equipped)}
                for row in ctx["byPart"]
            ]}
        return result

    def call(self, function: str, request: dict | None = None):
        arg = _lua_str(json.dumps(request)) if request is not None else ""
        return json.loads(self.engine.run(f"return {function}({arg})"))

    @staticmethod
    def main_out(ctx: dict) -> dict:
        return skill_out(next(s for s in ctx["skills"] if s["isMain"]))

    @staticmethod
    def mana_margin(ctx: dict) -> float:
        """Mana regen left after every skill used together has paid its cost per second."""
        return costs.margin(ctx, "Mana")["margin"]

    @staticmethod
    def main_models(ctx: dict) -> list[dict]:
        return next(s for s in ctx["skills"] if s["isMain"]).get("models", [])

    def dimensions(self, ctx: dict, base_ctx: dict) -> dict:
        out, base = self.main_out(ctx), self.main_out(base_ctx)
        dims = {
            "dps": change_pct(out[self.dps_key] or 0, base[self.dps_key] or 0),
            "ehp": change_pct(out["TotalEHP"] or 0, base["TotalEHP"] or 0),
            "physMaxHit": change_pct(out["PhysicalMaximumHitTaken"] or 0, base["PhysicalMaximumHitTaken"] or 0),
            "manaFrom": self.mana_margin(base_ctx),
            "manaTo": self.mana_margin(ctx),
            "costs": costs.cost_dims(ctx, base_ctx),
            # model results (e.g. Winter Orb hits) before -> after, so AoE/projectile changes are visible
            "models": [{"model": b["model"], "from": b["multiplier"], "to": a["multiplier"]}
                       for b, a in zip(self.main_models(base_ctx), self.main_models(ctx))],
            "loses": [k for k in self.capability_keys if (base.get(k) or 0) > 0 and (out.get(k) or 0) <= 0],
            # ailment chance/effect/duration that gets noticeably weaker (not just disappears)
            "weakens": [f"{k} {fmt_pct(change_pct(out.get(k) or 0, base[k]), 0)}"
                        for k in self.capability_keys
                        if (base.get(k) or 0) > 0 and 0 < (out.get(k) or 0) <= base[k] * (1 - WEAKEN_SHARE)],
            "skills": skill_changes(ctx, base_ctx),
        }
        return {**dims, "parts": part_variants.parts_dims(ctx, base_ctx, dims, self.dps_key)}

    def shown_dims(self, remove_ids: list[int], add_ids: list[int], base_ctx: dict, dims: dict) -> dict:
        if not self.multi_part:
            return dims
        key = (tuple(remove_ids), tuple(add_ids))
        if key not in self._shown_dims:
            ctx = self.evaluate(remove_ids, add_ids, parts=True)
            self._shown_dims[key] = self.dimensions(ctx, base_ctx)
        return self._shown_dims[key]

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
        request = self.with_parts({"stats": self.keys, "targets": targets,
                                   "extraSkills": self.extra_request()})
        for g in self.call("auditGemLevelsJSON", request)["gems"]:
            g["ctx"] = self.adjust(g["ctx"])
            broken = self.breaks(g["ctx"])
            change = {"type": "gem", "name": g["gem"], "level": g["toLevel"], "quality": g["toQuality"]}
            diffs = self.call("gemStatDiffJSON", {"name": g["gem"],
                                                  "from": {"level": g["fromLevel"], "quality": g["fromQuality"]},
                                                  "to": {"level": g["toLevel"], "quality": g["toQuality"]}})
            rows.append({
                "id": None if broken else self.suggest(change), "gem": g["gem"], "from": g["from"], "to": g["to"],
                "dims": self.dimensions(g["ctx"], base_ctx), "rejected": broken,
                "statChanges": [{"from": d["fromText"] or d["stat"], "to": d["toText"] or d["stat"]} for d in diffs[:3]],
            })
        return rows

    def support_swaps(self, top: int = 10) -> dict:
        protected = protected_supports(self.rules)
        if self._swap_levels is None:
            self._swap_levels = unobtainable.swap_levels(self.obtainable)
        request = {
            "stats": self.keys, "protected": protected, "levels": self._swap_levels,
            "extraSkills": self.extra_request()}
        result = self.call("auditSupportSwapsJSON", request)
        result["base"] = self.adjust(result["base"])
        for swap in result["swaps"]:
            swap["ctx"] = self.adjust(swap["ctx"])
        base = self.main_out(result["base"])
        valid, rejected = [], 0
        unobtainable_count = unobtainable.skipped_count(result)
        for swap in result["swaps"]:
            if not self.obtainable.gem_obtainable(swap["with"]):
                unobtainable_count += 1
            elif self.breaks(swap["ctx"]):
                rejected += 1
            else:
                valid.append((self.main_out(swap["ctx"])[self.dps_key] - base[self.dps_key], swap))
        valid.sort(key=lambda item: (-item[0], item[1]["with"], item[1]["replaced"] or ""))
        items = [{
            "id": self.suggest({"type": "swap", "replaced": swap["replaced"], "with": swap["with"],
                                "level": swap["level"], "quality": swap["quality"]}),
            "replaced": swap["replaced"], "with": swap["with"], "level": swap["level"],
            "quality": swap["quality"],
            "dims": self.dimensions(swap["ctx"], result["base"]),
        } for gain, swap in valid[:top] if gain > 0]
        Auditor._swap_parts(self, items, request)
        return {"tried": len(result["swaps"]), "unobtainable": unobtainable_count, "rejected": rejected,
                "protected": protected, "items": items}

    def _swap_parts(self, items: list[dict], request: dict) -> None:
        if not self.multi_part or not items:
            return
        candidates = [{"replaced": item["replaced"], "with": item["with"]} for item in items]
        result = self.call("auditSupportSwapsJSON",
                           {**request, "candidates": candidates, "partVariants": True})
        base = self.adjust(result["base"])
        swaps = {}
        for swap in result["swaps"]:
            swap["ctx"] = self.adjust(swap["ctx"])
            swaps.setdefault((swap["replaced"], swap["with"]), swap)
        for item in items:
            match = swaps.get((item["replaced"], item["with"]))
            if match is not None:
                item["dims"] = self.dimensions(match["ctx"], base)

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
                            f"DPS {fmt_pct(dims['dps'])} / EHP {fmt_pct(dims['ehp'])}"}
                shown = self.shown_dims(plan["removeIds"], plan["addIds"], base_ctx, dims)
                return {"status": "found", "currentPoints": plan["currentPoints"], "newPoints": plan["newPoints"],
                        "id": self.suggest({"type": "repath", "removeIds": plan["removeIds"], "addIds": plan["addIds"]}),
                        "dims": shown, "drop": plan["removed"], "take": plan["added"]}
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
        return max((base[k] - (out[k] or 0)) / base[k] for k in [self.dps_key, "TotalEHP"] if base[k])

    def branches(self, base_ctx: dict) -> list[dict]:
        base = self.main_out(base_ctx)
        rows = []
        for b in self.call("listBranchesJSON"):
            ctx = self.evaluate(b["removeIds"])
            out = self.main_out(ctx)
            stats = [self.dps_key, "TotalEHP", "PhysicalMaximumHitTaken"]
            shares = [abs((out[k] or 0) - base[k]) / base[k] for k in stats if base[k]]
            # only low-value branches that can actually go (removing them breaks no rule)
            if max(shares) < LOW_VALUE_SHARE and not self.breaks(ctx):
                rows.append({"name": b["name"], "points": b["points"], "dims": self.dimensions(ctx, base_ctx),
                             "required": [], "lowValue": True})
        return sorted(rows, key=lambda r: (r["name"], r["points"]))

    def kpi_sources(self, base_ctx: dict) -> dict:
        """Where each headline number comes from (all values straight from PoB's output)."""
        out = self.main_out(base_ctx)
        num = lambda k: out.get(k) or 0  # noqa: E731
        drains = [{"label": f"{s['name']} cost",
                   "value": -(skill_out(s).get("ManaPerSecondCost") or 0)}
                  for s in costs.used_together(base_ctx) if skill_out(s).get("ManaPerSecondCost")]
        return {
            "ehp": [{"label": "PoB Total EHP (enemy hits until death, all layers)", "value": num("TotalEHP")},
                    {"label": "Life", "value": num("Life")}, {"label": "Energy Shield", "value": num("EnergyShield")},
                    {"label": "Armour", "value": num("Armour")}, {"label": "Evasion", "value": num("Evasion")},
                    {"label": "Block / Spell block %",
                     "value": f"{fmt(num('BlockChance'))} / {fmt(num('SpellBlockChance'))}"}],
            "physMaxHit": [{"label": "PoB max physical hit you survive", "value": num("PhysicalMaximumHitTaken")},
                           {"label": "Phys damage reduction %", "value": fmt(num("PhysicalDamageReduction"))},
                           {"label": "Life + ES pool", "value": num("Life") + num("EnergyShield")}],
            "manaMargin": [{"label": "Mana regen (PoB)", "value": num("ManaRegenRecovery")}, *drains,
                           {"label": "= margin per second", "value": self.mana_margin(base_ctx)}],
            "costs": costs.kpi_entries(base_ctx),
        }

    def run(self) -> dict:
        base_ctx = self.base_context()
        base = self.main_out(base_ctx)
        report = {
            "disabledSkills": self.disabled_skills,
            "dpsMeasure": self.dps_measure,
            "scenario": {"name": self.scenario, "config": self.scenarios[self.scenario].get("pob_config") or {},
                         "conditional": self.conditional},
            "build": {**self.summary, "skills": [k["name"] for k in base_ctx["skills"]], "league": self.obtainable.league,
                      # which file version was analysed, so a mismatch with what's open in PoB is visible
                      "file": str(self.build_path),
                      "savedAt": datetime.fromtimestamp(self.build_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")},
            "rules": {"active": [r.name for r in self.rules], "skipped": self.skipped,
                      "currentViolations": violations(self.rules, base_ctx)},
            "models": [m for k in base_ctx["skills"] for m in k.get("models", [])],
            "dpsBreakdown": self.dps_breakdown(base[self.dps_key]),
            "kpiSources": self.kpi_sources(base_ctx),
            "reservation": {**self.reservations,
                            "overReserved": (self.reservations.get("manaUnreserved") or 0) < 0
                            or (self.reservations.get("lifeUnreserved") or 0) < 0},
            "base": {"dps": base[self.dps_key], "ehp": base["TotalEHP"],
                     "physMaxHit": base["PhysicalMaximumHitTaken"], "manaMargin": self.mana_margin(base_ctx),
                     "skills": base_skill_rows(base_ctx), "costs": costs.margins(base_ctx)},
            "costs": {"extras": self.extra_skills, "excluded": self.excluded_costs},
        }
        steps = [("unobtainable", "Checking gem obtainability", lambda: unobtainable.check(self, base_ctx)),
                 ("gems", "Testing gem upgrades", lambda: self.gem_levels(base_ctx)),
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
    part = lambda v: fmt_pct(v)  # noqa: E731
    loses = f" | LOSES: {', '.join(d['loses'])}" if d.get("loses") else ""
    loses += f" | WEAKENS: {', '.join(d['weakens'])}" if d.get("weakens") else ""
    loses += "".join(f" | hits {m['from']} -> {m['to']}" for m in d.get("models", []))
    skill_text = skill_pcts_text(d.get("skills") or [])
    loses += f" | {skill_text}" if skill_text else ""
    cost_text = costs.dims_text(d.get("costs") or {})
    return (f"DPS {part(d['dps'])} | EHP {part(d['ehp'])} | mana margin "
            f"{fmt(d['manaFrom'], sign=True)} -> {fmt(d['manaTo'], sign=True)}/s{cost_text}{loses}")


def _print_parts(dims: dict) -> None:
    text = part_variants.parts_text(dims)
    if text:
        print("         " + text)


def _print_cost_summary(report: dict) -> None:
    for row in report["base"]["costs"]:
        charges = " - ".join(
            f"{line['name']}" + (f" (group {line['group']})" if line["group"] is not None else "")
            + f" {fmt(-line['value'], 1, thousands=True)}" for line in row["lines"])
        pool = f", pool lasts {row['poolSeconds']}s" if row["poolSeconds"] is not None else ""
        print(f"   cost {row['resource']}: regen {fmt(row['regen'], 1, thousands=True)}/s - {charges} "
              f"= {fmt(row['margin'], 1, sign=True, thousands=True)}/s{pool}")
        if row.get("unverified"):
            print(f"   !! {row['unverified']}")
        if row["resource"] == "ES":
            print(f"   ES recharge (not counted): {row['recharge']['text']}")
    for row in report["costs"]["excluded"]:
        values = ", ".join(f"{fmt(row['value'][resource], 1, thousands=True)} {resource}/s"
                           for resource in costs.RESOURCES if resource in row["value"])
        print(f"   not summed: {row['name']} (group {row['group']}) {values}: {row['reason']}")
    for row in report["scenario"]["conditional"]:
        if row["applied"]:
            print(f"   scenario conditional: {row['var']}={str(row['value']).lower()} "
                  f"-> applied (source: {row['source']})")
        else:
            print(f"   scenario conditional: {row['var']}={str(row['value']).lower()} "
                  "-> not applied (build has no source)")
        for source in row.get("conditionalSources") or []:
            print(f"   {source}")


def _print_header(report: dict) -> None:
    b, r, s = report["build"], report["rules"], report["sections"]
    print(f"== {b['buildName']} ({b['ascendancy']}), skills used together: {', '.join(b['skills'])}")
    print(f"   file: {b['file']} (saved {b['savedAt']})")
    print(f"   scenario: {report['scenario']['name']} {report['scenario']['config']}"
          + (f" | left out: {', '.join(report['disabledSkills'])}" if report["disabledSkills"] else ""))
    if report["dpsMeasure"]["warning"]:
        print(f"   !! {report['dpsMeasure']['warning']}")
    skills = tile_text(report["base"]["skills"])
    if skills:
        print(f"   skills: {skills}")
    print(f"   rules: {len(r['active'])} active" + (f", skipped (draft): {', '.join(r['skipped'])}" if r["skipped"] else ""))
    _print_cost_summary(report)
    for step in report.get("dpsBreakdown", []):
        value = fmt(step["dps"], thousands=True) if step["dps"] is not None else ""
        print(f"   DPS  {value:>14}  {step['label']}")
    for m in report.get("models", []):
        print(f"   model: {m['model']}: {m['multiplier']} hits "
              f"(expected {fmt(m['expected'], 2)}, rounded down), range {m['range']} "
              f"(your PoB count: {m['pobCount']})")
    for v in r["currentViolations"]:
        print(f"   !! current build breaks: {v}")


def _print_unobtainable(report: dict) -> None:
    section = report["sections"].get("unobtainable") or {"items": []}
    for line in unobtainable.alert_lines(section, fmt_dims):
        print(line)


def _print_gems_and_swaps(report: dict) -> None:
    b, s = report["build"], report["sections"]
    print(f"\n-- Gem upgrades (only variants seen in {b['league']})")
    for g in s["gems"] or [{"none": True}]:
        if g.get("none"):
            print("   all gems already at the best obtainable level/quality")
            break
        tag = f"[{g['id']}]" if g["id"] else "   "
        print(f"   {tag} {g['gem']} {g['from']} -> {g['to']}: {fmt_dims(g['dims'])}"
              + (f"  REJECTED: {g['rejected'][0]}" if g["rejected"] else ""))
        _print_parts(g["dims"])
        for c in g["statChanges"]:
            print(f"         {c['from']}  ->  {c['to']}")

    sw = s["swaps"]
    print(f"\n-- Support gem swaps ({sw['tried']} tried, {sw['unobtainable']} not in {b['league']},"
          f" {sw['rejected']} break a rule, protected: {', '.join(sw['protected']) or '-'})")
    for item in sw["items"]:
        print(f"   [{item['id']}] {item['replaced']} -> {item['with']}: {fmt_dims(item['dims'])}")
        _print_parts(item["dims"])
    if not sw["items"]:
        print("   no swap beats the current links")
def _print_mods_and_repath(report: dict) -> None:
    s = report["sections"]
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
        _print_parts(rp["dims"])
        print(f"      drop: {', '.join(rp['drop'])}\n      take: {', '.join(rp['take']) or '-'}")
    else:
        print(f"   {rp['message']}")


def _print_tree(report: dict) -> None:
    s = report["sections"]
    tree = s["treeSwaps"]
    print(f"\n-- Passive tree (PoB power report: {tree['nodesScored']} nodes, {tree['masteriesScored']} masteries scored)")
    for objective, label in (("dps", "DPS"), ("ehp", "EHP")):
        print(f"   Best additions for {label} per point (PoB path power):")
        for a in tree["bestAdditions"][objective][:5]:
            print(f"      {a['name']:<30} {a['points']} pts  "
                  f"DPS {fmt_pct(a['gain']['dps'])}  EHP {fmt_pct(a['gain']['ehp'])}")
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
            _print_parts(t["dims"])
        if not tree["swaps"][objective]:
            print("      none that passes every rule")
    print("   Mastery options:")
    for m in tree["masteries"]:
        print(f"   [{m['id']}] {m['mastery']}: '{m['from']}' -> '{m['to']}': {fmt_dims(m['dims'])}")
        _print_parts(m["dims"])
    if not tree["masteries"]:
        print("      current choices are the best")


def _print_branches(report: dict) -> None:
    s = report["sections"]
    print("\n-- Tree branches")
    for row in s["branches"]:
        flag = "REQUIRED: " + "; ".join(row["required"]) if row["required"] else "low value, re-path candidate"
        print(f"   {row['name']:<28} {row['points']:>2} pts | {fmt_dims(row['dims'])}  {flag}")


def print_report(report: dict) -> None:
    _print_header(report)
    _print_unobtainable(report)
    _print_gems_and_swaps(report)
    _print_mods_and_repath(report)
    _print_tree(report)
    _print_branches(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("build", type=Path)
    parser.add_argument("--include-drafts", action="store_true", help="also apply draft vault rules")
    parser.add_argument("--leave-out", action="append", default=[], help="skill to leave out, e.g. 'Aspect of the Brine King'")
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO, help="vault scenario, e.g. Mapping")
    args = parser.parse_args()
    print_report(Auditor(args.build.resolve(), args.include_drafts, disabled_skills=args.leave_out,
                         scenario=args.scenario).run())
