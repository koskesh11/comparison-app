"""Compare pinned values with the numbers claimed in tasks/003 "Phase A spec" and tasks/000 log.

Each check compares at the precision the claim was written with. Sources: tasks/003-integrate-fr-coc-learnings.md
(Phase A spec, A1/A2/A3 acceptance) and tasks/000-interaction-research.md (log 2026-10-21).
"""

FR_PREFIX = "Forbidden Rite"


def _skill(snap: dict, name: str) -> dict:
    """Main-group skill by exact name, or the Forbidden Rite variant for name == FR_PREFIX."""
    for s in snap["skills"]:
        if s["name"] == name or (name == FR_PREFIX and s["name"].startswith(FR_PREFIX)):
            return s
    return {"name": name, "out": {}}


def _skill_dps(snap: dict, name: str) -> dict:
    for row in snap["skillDPS"]:
        if row["name"] == name or (name == FR_PREFIX and row["name"].startswith(FR_PREFIX)):
            return row
    return {}


def _dps(snap: dict, name: str) -> float | None:
    """PoB's own Full DPS row: dps x count (what FullDPS sums)."""
    row = _skill_dps(snap, name)
    return row["dps"] * row["count"] if row else None


def _pct(new: float | None, old: float | None) -> float | None:
    return 100 * (new - old) / old if new is not None and old else None


def _es_costs(snap: dict) -> float:
    return sum(s["out"].get("ESPerSecondCost") or 0 for s in snap["skills"])


def _es_net(snap: dict) -> float:
    return (snap["mainOutput"].get("EnergyShieldRegenRecovery") or 0) - _es_costs(snap)


def check(label: str, expected: float | str, actual, digits: int = 2, scale: float = 1.0, source: str = "") -> dict:
    if isinstance(expected, str):
        status = "MATCH" if actual == expected else "MISMATCH"
        return {"check": label, "expected": expected, "actual": actual, "status": status, "source": source}
    if actual is None:
        return {"check": label, "expected": f"{expected:,.{digits}f}", "actual": None, "status": "MISMATCH",
                "source": source}
    shown = f"{actual / scale:,.{digits}f}"
    status = "MATCH" if shown == f"{expected:,.{digits}f}" else "MISMATCH"
    return {"check": label, "expected": f"{expected:,.{digits}f}", "actual": shown, "actualRaw": actual,
            "status": status, "source": source}


def _dps_checks(r: dict) -> list[dict]:
    v1, v2, v3, v4 = (r[k]["snapshot"] for k in ("v1", "v2", "v3", "v4"))
    full = {k: r[k]["snapshot"]["summary"]["stats"]["FullDPS"] for k in ("v1", "v2", "v3", "v4")}
    src = "summary.stats.FullDPS"
    return [
        check("v4 FullDPS", 57001026.47, full["v4"], 2, source=src),
        check("v3 FullDPS (M)", 38.49, full["v3"], 2, 1e6, src),
        check("v3->v4 FullDPS %", 48.1, _pct(full["v4"], full["v3"]), 1, source=src),
        check("v3->v4 FR % (SkillDPS dps x count)", 48.5, _pct(_dps(v4, FR_PREFIX), _dps(v3, FR_PREFIX)), 1,
              source="mainOutput.SkillDPS"),
        check("v3->v4 Cyclone % (SkillDPS)", -25.0, _pct(_dps(v4, "Cyclone"), _dps(v3, "Cyclone")), 1,
              source="mainOutput.SkillDPS"),
        check("v3->v4 main-skill CombinedDPS % (what today's audit scores)", -25.0,
              _pct(v4["summary"]["stats"]["CombinedDPS"], v3["summary"]["stats"]["CombinedDPS"]), 1,
              source="summary.stats.CombinedDPS (main skill Cyclone)"),
        check("v1->v2 FullDPS %", 184.4, _pct(full["v2"], full["v1"]), 1, source=src),
        check("v2->v3 FullDPS %", 146.4, _pct(full["v3"], full["v2"]), 1, source=src),
    ]


def _v4_checks(v4: dict) -> list[dict]:
    fr, cyc = _skill_dps(v4, FR_PREFIX), _skill_dps(v4, "Cyclone")
    fr_out = _skill(v4, FR_PREFIX)["out"]
    s = "mainOutput.SkillDPS"
    return [
        check("v4 SkillDPS FR dps (M)", 56.83, fr.get("dps"), 2, 1e6, s),
        check("v4 SkillDPS FR skillPart", "All Primary Projectiles", fr.get("skillPart"), source=s),
        check("v4 SkillDPS FR count", 1, fr.get("count"), 0, source=s),
        check("v4 SkillDPS Cyclone dps (M)", 0.17, cyc.get("dps"), 2, 1e6, s),
        check("v4 SkillDPS Cyclone count", 1, cyc.get("count"), 0, source=s),
        check("v4 FR SkillTriggerRate /s", 7.52, fr_out.get("SkillTriggerRate"), 2, source="evaluate FR out"),
        check("v4 FR TriggerRateCap /s", 7.58, fr_out.get("TriggerRateCap"), 2, source="evaluate FR out"),
        check("v4 Cyclone Speed /s", 7.52, _skill(v4, "Cyclone")["out"].get("Speed"), 2, source="evaluate Cyclone out"),
    ]


FR_MAIN = "evaluate FR out.TotalDPS (FR as main skill; differs from its SkillDPS row)"


def _fr_total(snap: dict) -> float | None:
    """FR's own TotalDPS with FR as the main skill (what PoB's sidebar shows when FR is selected)."""
    return _skill(snap, FR_PREFIX)["out"].get("TotalDPS")


def _measure_checks(r: dict) -> list[dict]:
    """The 000-log FR numbers use FR as main skill; the v4 tile uses SkillDPS. Both measures, side by side."""
    v1, v2, v3, v4, src = (r[k]["snapshot"] for k in ("v1", "v2", "v3", "v4", "source"))
    return [
        check("v1 FR (M, TotalDPS as main)", 5.27, _fr_total(v1), 2, 1e6, FR_MAIN),
        check("v2 FR (M, TotalDPS as main)", 15.45, _fr_total(v2), 2, 1e6, FR_MAIN),
        check("v3 FR (M, TotalDPS as main)", 38.4, _fr_total(v3), 1, 1e6, FR_MAIN),
        check("v4 FR (M, TotalDPS as main; tile claim 56.83 is SkillDPS)", 56.83, _fr_total(v4), 2, 1e6, FR_MAIN),
        check("v3->v4 FR % (TotalDPS as main)", 48.5, _pct(_fr_total(v4), _fr_total(v3)), 1, source=FR_MAIN),
        check("source FR (M, TotalDPS as main)", 16.60, _fr_total(src), 2, 1e6, FR_MAIN),
    ]


def _per_build_checks(r: dict) -> list[dict]:
    v1, v2, v3 = (r[k]["snapshot"] for k in ("v1", "v2", "v3"))
    s1 = v1["summary"]["stats"]
    rows = [check("v1 FR (M, SkillDPS)", 5.27, _dps(v1, FR_PREFIX), 2, 1e6, "mainOutput.SkillDPS"),
            check("v1 PhysicalMaximumHitTaken (k)", 33.3, s1["PhysicalMaximumHitTaken"], 1, 1e3, "summary.stats")]
    rows += [check(f"v1 {res} %", 89, s1[res], 0, source="summary.stats")
             for res in ("FireResist", "ColdResist", "LightningResist")]
    rows += [
        check("v2 FR (M, SkillDPS)", 15.45, _dps(v2, FR_PREFIX), 2, 1e6, "mainOutput.SkillDPS"),
        check("v2 FR SkillTriggerRate /s", 10.03, _skill(v2, FR_PREFIX)["out"].get("SkillTriggerRate"), 2,
              source="evaluate FR out"),
        check("v3 FR (M, SkillDPS)", 38.4, _dps(v3, FR_PREFIX), 1, 1e6, "mainOutput.SkillDPS"),
        check("v3 FR SkillTriggerRate /s", 5.07, _skill(v3, FR_PREFIX)["out"].get("SkillTriggerRate"), 2,
              source="evaluate FR out"),
        check("v3 FR ProjectileCount", 5, _skill(v3, FR_PREFIX)["out"].get("ProjectileCount"), 0,
              source="evaluate FR out"),
    ]
    return rows


def _es_checks(r: dict) -> list[dict]:
    v2, v4, src = (r[k]["snapshot"] for k in ("v2", "v4", "source"))
    e = "evaluate out; net = EnergyShieldRegenRecovery - sum ESPerSecondCost (main group)"
    return [
        check("v2 ES regen /s", 2250.6, v2["mainOutput"].get("EnergyShieldRegenRecovery"), 1, source=e),
        check("v2 Cyclone ES/s", 60.2, _skill(v2, "Cyclone")["out"].get("ESPerSecondCost"), 1, source=e),
        check("v2 FR ES/s", 1494.8, _skill(v2, FR_PREFIX)["out"].get("ESPerSecondCost"), 1, source=e),
        check("v2 ES net /s", 695.6, _es_net(v2), 1, source=e),
        check("v2 ES pool", 17116, v2["mainOutput"].get("EnergyShield"), 0, source=e),
        check("v4 ES regen /s", 2250.6, v4["mainOutput"].get("EnergyShieldRegenRecovery"), 1, source=e),
        check("v4 Cyclone ES/s", 45.1, _skill(v4, "Cyclone")["out"].get("ESPerSecondCost"), 1, source=e),
        check("v4 FR ES/s", 1121.1, _skill(v4, FR_PREFIX)["out"].get("ESPerSecondCost"), 1, source=e),
        check("v4 ES costs sum /s", 1166.2, _es_costs(v4), 1, source=e),
        check("v4 ES net /s", 1084.4, _es_net(v4), 1, source=e),
        check("source ES net /s", 1077.0, _es_net(src), 1, source=e),
        check("source FR (M, SkillDPS)", 16.60, _dps(src, FR_PREFIX), 2, 1e6, "mainOutput.SkillDPS"),
        check("source FR SkillTriggerRate /s", 10.03, _skill(src, FR_PREFIX)["out"].get("SkillTriggerRate"), 2,
              source="evaluate FR out"),
        check("source FR ES/s", 1555.0, _skill(src, FR_PREFIX)["out"].get("ESPerSecondCost"), 1, source=e),
    ]


def _other_group_es(snap: dict, name: str) -> float | None:
    for row in snap["otherGroups"]:
        if row["name"] == name:
            return row["out"].get("ESPerSecondCost")
    return None


def _golden_checks(audit: dict, r: dict) -> list[dict]:
    ek, worb = audit["EK"]["snapshot"], audit["Worb"]["snapshot"]
    mana = {row["label"]: row["value"] for row in ek["kpiSources"]["manaMargin"]}
    model = next((m for m in worb["models"] if m["model"] == "Winter Orb projectile overlap"), {})
    v4 = r["v4"]["snapshot"]
    return [
        check("EK FullDPS as saved", 15136639.02, ek["summary"]["stats"]["FullDPS"], 2, source="Auditor.summary"),
        check("Worb FullDPS as saved", 7176019.15, worb["summary"]["stats"]["FullDPS"], 2, source="Auditor.summary"),
        check("EK mana regen /s", 209.4, mana.get("Mana regen (PoB)"), 1, source="kpiSources.manaMargin"),
        check("EK EK cost /s", 160.7, -(mana.get("Ethereal Knives cost") or 0), 1, source="kpiSources.manaMargin"),
        check("EK Cyclone cost /s", 26.8, -(mana.get("Cyclone cost") or 0), 1, source="kpiSources.manaMargin"),
        check("EK mana margin /s", 21.9, ek["base"]["manaMargin"], 1, source="Auditor base.manaMargin"),
        check("Worb Winter Orb pobCount", 5, model.get("pobCount"), 0, source="Auditor models"),
        check("Worb Winter Orb multiplier", 4, model.get("multiplier"), 0, source="Auditor models"),
        check("Worb Winter Orb expected (~4.4)", 4.4, model.get("expected"), 1, source="Auditor models"),
        check("v4 Assassin's Mark (Mark On Hit group) ES/s", 19.4, _other_group_es(v4, "Assassin's Mark"), 1,
              source="otherGroups"),
        check("v4 Withering Step (Automation group) ES/s", 14.0, _other_group_es(v4, "Withering Step"), 1,
              source="otherGroups"),
    ]


def evidence_checks(audit: dict, raw: dict) -> list[dict]:
    return (_dps_checks(raw) + _v4_checks(raw["v4"]["snapshot"]) + _per_build_checks(raw) + _measure_checks(raw)
            + _es_checks(raw) + _golden_checks(audit, raw))
