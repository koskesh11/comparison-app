---
type: rule
kind: build_method
status: draft
pob_refs: ["Spec:LifeInc", "Spec:EnergyShieldInc", "Spec:ArmourInc", "Life", "EnergyShield", "Armour", "Mana"]
source: "user, 2026-10-26 (tasks/042-fireball-golemancer.md, log 15:56 USER METHOD); PoB 2.67.2 Modules/Calcs.lua, CalcPerform.lua, CalcDefence.lua, ModParser.lua, Classes/Item.lua"
last_confirmed_patch: 3.29.x
---

```rule
# DRAFT, the user verifies. Engine-inert on purpose: no require/forbid/when keys, so rules.py evaluates nothing.
# Do not turn a check into `require: {stat: ...}` yet: rules.py reads `stat` from the main skill's output
# (skill_out) and _compare() passes when the value is None, so a player-level key such as Spec:LifeInc
# would silently always pass (false negative).
applies: generator_gear_stage
method:
  - step: shell
    do: "make the 4 defensive pieces first (boots, gloves, body armour, helmet) at league-start budget"
  - step: measure
    do: "read what that gear alone gives at character level 90: Life, EnergyShield, Armour"
    pob: "build.calcsTab.mainOutput (engine/pob_headless.lua:96); Life CalcPerform.lua:89-93, EnergyShield / Armour CalcDefence.lua:1064-1065"
  - step: tree_fills_gap
    do: "grow the tree only for the gap between the shell and the targets"
  - step: shield
    do: "treat the shield slot as a choice: defence or offence"
checks:
  - id: tree-life-baseline
    require: "increased maximum Life from the passive tree >= about 100%"
    pob_stat: "mainOutput['Spec:LifeInc'] = modDB:Sum('INC', {source='Tree'}, 'Life'), Modules/Calcs.lua:439-442 (calcs.buildOutput, line 384)"
    tolerance: "about; exact floor not given by the user"
  - id: no-gear-mana
    forbid: "maximum Mana mods on the 4 shell pieces"
    unless: "the build scales mana: Eldritch Battery, Mind Over Matter, mana stacking"
    pob_stat: "per item: item.modList entries named Mana (ModParser.lua:180-181 maps 'mana' / 'maximum mana' to Mana; list built in Classes/Item.lua); keystones from ctx.keystones (engine/audit.lua:182)"
  - id: league-start-gear
    require: "rares with moderate mods, or tier 4-5 uniques"
    pob_stat: "rarity: item.rarity (Classes/Item.lua:430, 450). PoB has no unique tier and no 'moderate' measure"
not_verified:
  - "whether Spec:LifeInc counts anointed notables, tattoos and jewels socketed in the tree (source filter 'Tree')"
  - "the exception list for the life baseline (CI sets Life to 1, CalcPerform.lua:84-86; pure ES builds?)"
  - "the scope of 'mana mods': maximum mana only, or also mana regeneration, leech and cost mods"
  - "what 'tier 4-5 unique' and 'moderate mods' mean in numbers (loot-filter tier? price?)"
```

The user's league-start method (draft, 2026-10-26). Build a gear "shell" first: boots, gloves, body armour and helmet as moderate rares or tier 4-5 uniques, with no mana mods unless the build scales mana (Eldritch Battery, Mind Over Matter, mana stacking). Measure what that gear alone gives at level 90 (life, ES, armour); the tree then fills only the gap. About 100% increased life from the tree is the baseline he expects of any build. The shield is special: it can carry defence or offence.

Why it is here: the generator's gear stage places no items and grows the tree first, so the tree is built blind to the gear (task 042 log, 15:56). PoB computes each number, but it does not enforce this order or these thresholds.
