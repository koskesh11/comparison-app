---
type: rule
kind: validity
status: verified
pob_refs: [ManaCost, ManaCostPayablePool, ManaPerSecondCost, ManaRegenRecovery, ESCost, LifeCost, EnergyShield, LifeUnreserved, ESPerSecondCost, LifePerSecondCost, EnergyShieldRegenRecovery, LifeRegenRecovery, CostESInsteadOfManaOrLife]
source: user (CoC EK Assa, Deep Thoughts — EK 160.7/s + Cyclone 26.8/s vs 209 regen); merged with the per-resource draft by user decision 2026-10-22 (task 003)
last_confirmed_patch: 3.29.0
---

```rule
applies: always
skill_set: used_together        # e.g. CoC: trigger attack + every spell it triggers
require:
  - { each_skill: ManaCost, op: "<=", ref: ManaCostPayablePool }
  - { sum_over_skill_set: ManaPerSecondCost, op: "<=", ref: ManaRegenRecovery,
      allow_deficit: { pool: ManaUnreserved, min_seconds: 30 } }   # a small deficit is fine if the pool lasts
  - { each_skill: ESCost, op: "<=", ref: EnergyShield }
  - { each_skill: LifeCost, op: "<=", ref: LifeUnreserved }   # "<=" so 0 cost with a 0 pool passes; paying exactly all remaining life: UNVERIFIED
  - { sum_over_skill_set: ESPerSecondCost, op: "<=", ref: EnergyShieldRegenRecovery }   # no deficit window (user 2026-10-22)
  - { sum_over_skill_set: LifePerSecondCost, op: "<=", ref: LifeRegenRecovery }         # no deficit window (user 2026-10-22)
```

Costs must be **summed** across skills used at the same time. Checking each skill alone missed that
removing Deep Thoughts gives −47 mana/s (232 drain vs 185 regen).

A deficit is allowed if the unreserved pool lasts ≥ 30 s of continuous use (Worb: Focused Channelling
raises cost the longer you channel; −2/s against a full pool is not a real problem). 30 s is a draft value.

**ES and life (user decision 2026-10-22):** per use, ES cost ≤ EnergyShield and life cost ≤ LifeUnreserved (lines
above). Per second, ES and life cost must not exceed regen: no deficit window (mana keeps its 30 s; last two lines).
A per-second line is skipped when its summed cost is 0, so a build with no ES/life costs never breaks on negative regen
(e.g. Righteous Fire). Paths relative to `%APPDATA%\Path of Building Community` (PoB 2.67.2).
- PoB keys: per use `Modules/CalcOffence.lua:1692-1895`; per second = cost x Speed, for a triggered skill Speed =
  trigger rate (`CalcOffence.lua:5916-5955`). Only mana has a payable-pool key (`CalcOffence.lua:1898`), so ES and
  life use the pool itself. Recovery keys = regen - degen + recovery (`Modules/CalcDefence.lua:1313`).
- Regen, not recharge: ES recharge (`CalcDefence.lua:1371`) is display-only in PoB and any damage interrupts it.
  Wiki *Energy shield*: recharge "is not interrupted ... by loss from non-damage sources or skill costs" (3.5.0).
- Whispers of Infinity moves mana AND life costs to ES (`CalcOffence.lua:1766-1784`).
- FR CoC v4 (headless, Pinnacle Boss): Cyclone 45.1 + FR 1,121.1 = 1,166.2 ES/s vs EnergyShieldRegenRecovery 2,250.6.
- 2,250.6 needs `conditionOnConsecratedGround` = true (Bottled Faith; its "Creates Consecrated Ground on Use" parses
  to nothing, `Modules/ModParser.lua:5094`); without it 1,266.5/s. Counted only for builds that have a source
  (decision 5, [[Pinnacle Boss]] `conditional_config`).
- Skill set "used together" = every skill in the main socket group + skills in other enabled groups that are triggered
  at a rate (v4: Mark On Hit 19.4 + Automation 14.0 ES/s). Not summed, shown with the reason: self-cast skills in other
  groups (PoB's rate = full cast speed, e.g. v4 curses 87.7 ES/s each) and skills triggered by damage taken / block /
  stun (rate depends on hits you take, e.g. EK Vulnerability via CwDT 321.2 mana/s).
- Open: Eldritch Battery ("Spend Energy Shield before Mana for Skill Mana Costs ... 50% less Energy Shield Recharge
  Rate", `TreeData/3_28/tree.lua:65655`) moves mana costs into ESPerSecondCost (`CalcOffence.lua:5919-5923`), so the
  mana line sums 0 and the ES line compares them with ES regen only; mana regen (paid once ES is empty) and recharge are
  not counted. Which recovery to compare against is UNVERIFIED; EB builds can show a false ES break until it is.

Related: [[Trigger attack under the CoC cap]] (trigger rate sets the cost per second).
