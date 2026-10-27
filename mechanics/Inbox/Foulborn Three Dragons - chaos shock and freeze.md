---
type: research
status: draft
pob_refs: [MutatedUniqueHelmetDexInt4ChaosDamageCanShock, MutatedUniqueHelmetDexInt4ChaosDamageCanFreeze, ChaosCanShock, ChaosCanFreeze, enemyIsBoss, conditionEnemyShocked, conditionShockEffect, conditionEnemyFrozen, ailmentMode, ForbiddenRite]
source: "PoB 2.67.2-beta data/source (3.29); poewiki API pages Foulborn unique item, The Three Dragons, Shock, Freeze, Ailment, Critical strike, Self-damage, The Genesis Tree, Forbidden Rite, Version 3.27.0/3.28.0/3.29.0 (fetched 2026-10-21); trade API Allflame 2026-10-21; headless PoB test on CoC EK Assa.xml (in memory, not saved)"
last_confirmed_patch: 3.29.x
---

```gap
# Draft for Gaps/ (Inbox is not loaded by the app). Both lines change nothing in PoB DPS, but they are the point of the item.
patterns:
  - { match: "Your Chaos Damage can Shock",  slot: "Helmet", why: "PoB works out the shock but never adds it to DPS; set Effect of Shock in config" }
  - { match: "Your Chaos Damage can Freeze", slot: "Helmet", why: "freeze is crowd control; PoB has no value for it" }
```

## 1. Foulborn mechanics
- Added in **3.27.0**: "Introduced to the game in Keepers league." (wiki *Foulborn unique item*, version history). 3.27.0c: "Added over 80 new Foulborn Unique items".
- What gets replaced: "one or more of their modifiers replaced by Foulborn modifiers ... The Foulborn modifier that is added is directly correlated with the original modifier that was replaced." Each original line has one fixed replacement. PoB has the same mapping: `Data/ModFoulbornMap.jsonc:345-349` and the wiki table on *The Three Dragons* page:
  - Lightning freezes-but-not-shock (`LightningFreezesUniqueHelmetDexInt4`) -> **Your Chaos Damage can Freeze**
  - Fire shocks-but-not-ignite (`FireShocksUniqueHelmetDexInt4`) -> **Your Chaos Damage can Shock**
  - Cold ignites-but-not-freeze/chill (`ColdIgnitesUniqueHelmetDexInt4_`) -> Your Chaos Damage can Ignite
  - +(26-30)% all elemental resistances: never replaced.
- One item can have **both**. Genesis Tree notable *Extremely Foul* says: "Birthed Foulborn Uniques have a 20% chance of multiple Foulborn Modifiers". The Genesis Tree has been in core since 3.28.0 and is still there in 3.29.0 (wiki *The Genesis Tree*). Checked on the trade API (2026-10-21): Allflame has 43 listings with both mods, 300 with chaos shock, 343 with chaos freeze; Standard has 12 with both. Two listings I fetched read: +26% res / Cold ignite line / {mutated} Chaos Freeze / {mutated} Chaos Shock. The user's own `3.28/Ninja Ideas/Trickster Unholy Trinity Frostblade Three Dragons Chaos.xml` (lines 565-580) has this exact item.

## 2. How PoB applies it
- Parsing: `ModParser.lua:3638` turns "your (%w+) damage can (%w+)" into the flags `ChaosCanShock` and `ChaosCanFreeze` (cache: `ModCache.lua:23005,23007`).
- Chance to shock or freeze: `CalcOffence.lua:4231-4258` sets `ShockChanceOnCrit`/`FreezeChanceOnCrit` = 100 for every hit skill. Non-crit hits only get "chance to" mods. The damage type does not affect the chance.
- Which damage counts: `CalcOffence.lua:4315-4329` (`calcAverageSourceDamage`) adds Chaos Hit/Crit average damage to the shock or freeze source damage only when `ChaosCanShock`/`ChaosCanFreeze` is set. Shock's own type is Lightning and Freeze's is Cold (`Data.lua:424-431`). The wiki agrees: "If the player is able to shock with multiple different damage types, the shock's effect is determined by the total damage dealt by all applicable damage types." (*Shock*)
- Crits, from the wiki (*Ailment*, current page): "Critical strikes have 100% chance to inflict Ignite, Freeze, and Shock." *Critical strike* adds: "These ailments can still be discarded if they do not reach the minimum ailment threshold." The 3.28.0 notes still mention "Critical Strikes against you do not inherently inflict Elemental Ailments", so the mechanic still exists. PoB's `ailmentMode` (Average / Crits Only, `ConfigOptions.lua:210`) weights hits and crits.
- Headless test: Forbidden Rite 20/0 added to the CoC EK Assa tree (crit 80.58%), helmet swapped in memory:
  - Plain Three Dragons: shock and freeze flags both **false**, even though ShockChance is 80.58%. That is the damage-type gate working.
  - Chaos-shock: shock flag true. Chaos-freeze: freeze flag true. Both: both flags true. Chill stays false in every case, so chaos-freeze does not chill. The wiki says the same: "freeze and Chill are separate ailments" (*Freeze*, citing Mark_GGG on Three Dragons).
  - **TotalDPS was the same for all 4 helmets** (61,580.95 vs Pinnacle). `CurrentShock` = 0. PoB never feeds the shock it works out back into damage. The enemy's shock only comes from config `ShockVal` or item `ShockBase`/`ShockOverride` mods (`CalcPerform.lua:3565-3610`, `ConfigOptions.lua:1943-1950`). Freeze is only the "Is the enemy Frozen?" switch (`ConfigOptions.lua:1924`).

## 3. Thresholds and bosses
- Shock effect = `50 * (D/T)^0.4 * effectMod`, minimum 5, maximum 50 (`CalcOffence.lua:5352-5357`, `Data.lua:428`). Wiki formula: E = 1/2*(D/T)^0.4*(1+M). The wiki tags it "potentially outdated", from 3.9.0. "Hits require enough shocking damage to reach 5% shock effect. Shocks discarded for not reaching this minimum are never applied" (*Shock*). D is the damage the enemy actually takes, after chaos resistance (*Ailment*). PoB's chaos average was 3,969 vs Pinnacle and 5,670 vs no boss, a ratio of 0.70, matching 30% boss chaos resistance.
- Freeze: "0.06 seconds for every 1% of the target's ailment threshold ... up to a maximum of 50% (3 seconds)". It needs at least 0.3 s, or it is discarded (*Freeze*). PoB's breakdown agrees (`CalcOffence.lua:5398-5413`): threshold must be at most `D * 20 * FreezeDurationMod`.
- Threshold T (`CalcOffence.lua:5333-5342`) = `monsterAilmentThresholdTable[lvl]` (`Misc.lua:15`) x 7.68 (if boss) x `mapLevelBossLifeMult` (`Misc.lua:473`) x `mapLevelBossAilmentMult` (`Misc.lua:474`) x enemy Life MORE x AilmentThreshold MORE.
  - The MORE is 488 for Standard Boss and 404 for Pinnacle/Uber (`ConfigOptions.lua:2122/2157/2191`).
  - Pinnacle, level 84: 16265 x 7.68 x 21.46 x 0.47 x 5.04 = **6,349,995**, matching PoB's breakdown row "(Pinnacle)".
  - Non-boss, level 85: 38,852.
- What that means vs Pinnacle with no effect/duration mods. Chaos damage taken per hit needed:
  - shock 5%: ~20.1k
  - shock 10%: ~113.6k
  - shock 20%: ~642.6k
  - freeze 0.3 s: ~317.5k (= T/20)
  - In the test, a 19.6k Forbidden Rite crit showed "4%" in PoB's table. In game that shock is discarded. PoB's table still lists sub-5% rows.
- Freeze on bosses: no immunity, but they have a minimum action speed. 3.25.0: "Pinnacle Bosses, Shaper Guardians and Elder Guardians can now have up to 50% Action Speed reduction (previously 30%)" (*Freeze*). The [[Pinnacle Boss]] scenario already says `freeze_assumable: false`.

## 4. Interactions
- Remaining original lines:
  - Chaos-shock only: fire can ignite again, lightning still **cannot** shock, cold cannot freeze or chill, lightning still freezes.
  - Chaos-freeze only: lightning can shock again, fire shocks but cannot ignite, cold still cannot freeze or chill.
  - Both (the trade-listed version): fire and lightning are back to normal. Only the cold line stays, so **no damage type can chill** (`ModCache.lua:23012`), and cold hits can ignite. The wiki notes the item does not convert "chance to" mods.
- Forbidden Rite is pure chaos. It gets guaranteed shock/freeze only on **its own** crits (base crit 6%, `act_int.lua`); non-crits need "chance to" mods. Cyclone's crits only trigger it (CoC details belong to the skills agent). The shock/freeze lines also apply to any chaos damage Cyclone deals.
- Forbidden Rite's self-hit: "Self-damage is unaffected by the player's offensive stats, including conversion and ailment stats" (*Self-damage*). That suggests you cannot shock or freeze yourself. UNVERIFIED for Three Dragons specifically. PoB does not model it.
- Forbidden Rite base damage is 14% of max life in 3.29.0 (patch note). PoB matches: `act_int.lua:7469` = 14.

## 5. PoB support and building it
- Every line parses with no unparsed leftovers (headless test). PoB marks the item Foulborn, adds the "Foulborn" prefix (`Item.lua:1551-1608`), and works without `{mutated}` tags (pasted in-game text works).
- Item editor (support for toggling these was added in PoB 2.66.0, `changelog.txt:208`):
  1. Open the Items tab and find The Three Dragons in the unique list. Searching "foulborn" works (`ItemDBControl.lua:156-161`).
  2. Each line that can be replaced has a checkbox with a Breach icon (`ItemsTab.lua:1039-1076, 1101-1141`).
  3. Tick the Fire line to get chaos shock, and the Lightning line to get chaos freeze.
- PoB lets you tick **any** combination. That is not proof the item exists in game; check the trade API.

## Open / UNVERIFIED
- Real 3.29 ailment thresholds of specific pinnacle bosses. PoB uses one generic number; the wiki's Sirus ~25M figure is a 2020 playtest from before the 3.15 rebalance.
- The shock formula's "potentially outdated" tag on the wiki.
- How the "multiple" Foulborn count is decided (2 vs 3 mods) is undocumented.
