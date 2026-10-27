---
type: gap
status: draft
source: "PoB 2.67.2 (3.29) source, file:line below; headless test on FR CoC Occu Three Dragons v4 (in memory, 2026-10-21); Inbox note Foulborn Three Dragons - chaos shock and freeze"
last_confirmed_patch: "3.29.x"
---

```gap
# Foulborn The Three Dragons: lines that change nothing in PoB DPS but are the point of the item.
# "Your Chaos Damage can Ignite" is left out on purpose: PoB values it when the skill can deal fire.
patterns:
  - match: "Your Chaos Damage can Shock"
    why: "chaos hits can shock; PoB works out the shock but adds it to DPS only via config or a guaranteed shock source (vault Model: Own shock effect). Elemental Focus or Secrets of Suffering remove it with no DPS change"
  - match: "Your Chaos Damage can Freeze"
    why: "chaos hits can freeze: crowd control, PoB has no DPS value for it (only the 'Is the enemy Frozen?' switch); bosses: freeze not assumed. Elemental Focus or Secrets of Suffering remove it with no DPS change"
  - match: "Your Cold Damage can Ignite but not Freeze or Chill"
    slot: "Helmet"
    why: "Three Dragons drawback kept on Foulborn versions: cold can't freeze or chill (with both chaos mutations nothing can chill); no change in PoB when the build deals no cold damage"
```

Research: [[Foulborn Three Dragons - chaos shock and freeze]]. PoB paths are relative to `%APPDATA%\Path of Building Community`.

**Why these lines show "no change".**
- PoB parses them into the flags ChaosCanShock / ChaosCanFreeze (`Modules/ModParser.lua:3638`). Chaos damage counts toward shock and freeze only with these flags (`Modules/CalcOffence.lua:4315-4329`); crits always apply them (`CalcOffence.lua:4243-4250`).
- PoB adds your own shock to DPS only through config (`conditionEnemyShocked` + `conditionShockEffect`, `Modules/ConfigOptions.lua:1943-1950`) or a guaranteed source (ShockBase / ShockOverride / ShockMinimum, `Modules/CalcPerform.lua:3565-3606`). So the shock is real but invisible to a DPS check. How big it is: [[Own shock effect]].
- Freeze has no DPS value in PoB at all.

**No slot on the chaos patterns:** the same lines exist on other uniques (`Data/ModItemExclusive.lua:3834-3835`, `7512`).

**Ignite left out:** PoB values "Your Chaos Damage can Ignite" when the skill can deal fire (`CalcOffence.lua:5131`). In v4, Void Manipulation's `deal_no_elemental_damage` (`Data/Skills/sup_dex.lua:4578`) makes PoB skip the ignite block (`CalcOffence.lua:4991`).

**Verified headless (2026-10-21, "FR CoC Occu Three Dragons v4", in memory):**
- The helmet lines are UNIQUE, so the audit puts them in "uniquePackage" and shows this why text there.
- Adding Secrets of Suffering drops ShockChanceOnCrit and FreezeChanceOnCrit from 100 to 0 while FR DPS stays identical.

UNVERIFIED: whether chaos shock from Forbidden Rite actually applies in game as PoB computes it (user to test).
