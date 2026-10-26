---
type: interaction
status: draft
pob_refs: [PhysicalDamageConvertToFire, LightningDamageConvertToFire, ColdDamageConvertToFire, DealNoPhysical, DealNoCold, DealNoLightning, DealNoChaos, DealNoFire, Condition:HaveAvatarOfFire, conditionHaveVulconus, canDeal, FireHitAverage, FreezeDurationMod, ChillDuration]
source: "poewiki Avatar of Fire rev 1625575, Damage conversion rev 1673519 (fetched 2026-10-26); PoB 2.67.2 TreeData/3_29/tree.lua, Data/ModCache.lua, Modules/ModParser.lua, CalcOffence.lua, ConfigOptions.lua, Data/Uniques, Data/TattooPassives.lua, Data/Crucible.lua; headless probe of Fireball Elementalist, Worb and FR CoC Occu v4 2026-10-26 (task 027 batch 3c; evidence in scratchpad b3c/mechanics-researcher-C.md)"
last_confirmed_patch: "3.29.x"
---

Avatar of Fire (AoF) is a keystone that converts 50% of Physical, Cold and Lightning damage to Fire and makes the character deal no damage of any other type: the unconverted half of those three types and ALL chaos damage become zero. It is a gain only for a build that is almost all fire already and has other types as flat added damage with fire-only multipliers above 2x; for any build that deals chaos, cold or lightning on purpose it is a large loss or a complete zero. PoB reads both lines correctly (conversion table plus DealNo flags), so its number is trustworthy; what it cannot say is how the game treats the lost ailments (freeze, chill, bleed, poison come from the dropped damage types). Related: [[Conversion and gain as extra]] (order, over-conversion), [[Elemental Equilibrium]] (no synergy), [[Damage type can ailment]], [[Freeze]], [[Chill]], [[Shock]], [[Ignite]], [[Damage calculation]].

Pipeline: [[Damage calculation#Conversion]] - AoF adds three conversion lines to the fixed order Physical -> Lightning -> Cold -> Fire -> Chaos (chaos comes after fire, so it can never be converted) and then forbids every type but fire at the end of the hit; converted damage keeps the modifiers of every type on its path, so fire gets the cold/lightning/physical increased and more once each plus its own.

Measured (PoB 2.67.2 headless, keystone added as a custom mod 'Avatar of Fire' = keystone only, path cost not included; enemy level from headless env.enemyLevel: Pinnacle = 84, None = 85; CombinedDPS of the main skill; FR figures are FullDPS because the FR spell is triggered):

| build / scenario | base | with AoF | delta |
|---|---|---|---|
| Fireball Elementalist (as built, NOT a validator seed), Pinnacle | 285,468.3 | 286,303.0 | +0.29% (fire hit avg 35,744.5 -> 36,041.5; the 234 lightning is converted, nothing else changes) |
| Fireball Elementalist, None | 390,510.4 | 391,541.5 | +0.26% |
| Worb (as built), Pinnacle / None | 1,343,497.5 / 1,934,211.1 | 0 / 0 | -100%: Bitter Frost (tree 12128) already says 'Cannot deal non-Cold Damage' = DealNo Physical/Fire/Lightning/Chaos; AoF adds DealNoCold, so all five types are blocked |
| Worb with Bitter Frost removed (what-if, control 1,179,893.8 / 1,706,879.4), Pinnacle / None | 1,179,893.8 / 1,706,879.4 | 143,266.7 / 451,919.1 | -87.86% / -73.52% (cold hit avg 37,077.7 -> 0, fire hit avg 88.1 -> 4,409.3 at Pinnacle; FullDPS -88.15%) |
| FR CoC Occu v4 (as built), Pinnacle / None | FullDPS 57,001,026.5 / 67,300,151.8 | 0 / 0 | -100%: the Forbidden Rite spell is 100% chaos (hit avg 191,717.9; physical, cold, fire, lightning 0) and Void Manipulation already blocks cold, fire, lightning; AoF blocks physical and chaos |

What-if on the Fireball (custom line 'Adds 20000 to 30000 <type> Damage to Spells', then AoF), to show the break-even:

| added type | Pinnacle without / with AoF | None without / with AoF |
|---|---|---|
| Cold | 4,247,383 / 5,877,239 (+38.37%) | 6,254,468 / 8,044,471 (+28.62%) |
| Lightning | 4,013,913 / 5,652,956 (+40.83%) | 5,908,913 / 7,731,162 (+30.84%) |
| Physical | 8,278,746 / 9,838,944 (+18.85%) | 9,798,408 / 13,456,063 (+37.33%) |

Reading (derived from the PoB damage pipeline, not a separate source): 50% of type X moved to fire keeps X's modifiers and gains the fire-only modifiers, so AoF wins on X only if the fire-only increased x more x penetration multiplier is above 2 (the lost half) after the enemy's resistance gap; the Fireball has a very high fire-only multiplier, so converted flat damage nearly doubles in value. Worb loses -73% to -88% even with Bitter Frost removed because its modifiers are cold-specific and the enemy's cold resistance is negative with exposure and Frostbite (-22, effective -40.5% at Pinnacle) while its fire resistance is 50 (effective 67.5%). Ailments in the same probes: with the cold part gone the outputs ChillDuration and FreezeDurationMod vanished (Worb without Bitter Frost, Fireball with added cold); ShockChance and ShockEffectMod stayed (cause not traced); Ignite DPS rose with the fire hit (Fireball +1.2%).

```interaction
id: avatar-of-fire
mechanic: "Keystone '50% of Physical, Cold and Lightning Damage Converted to Fire Damage / Deal no Non-Fire Damage': 50% of each of the three types is converted to fire (added to other conversions of the same source, a total above 100% is scaled down with skill sources first); the unconverted 50% of physical, cold, lightning and all chaos damage is dealt as zero; converted damage takes the modifiers of every type on its path once each; chaos comes after fire in the conversion order and is never converted; wiki: the conversion and the no-non-fire rule do not affect self-damage such as Blood Rage or Forbidden Rite; uniques with the Avatar of Fire modifier do the same, taking the keystone as well gives no extra benefit"
family: pipeline
target: self
related: [conversion-gain-as-extra, elemental-equilibrium, damage-type-can-ailment, freeze, shock, ignite]
pipeline_step: ["Damage calculation#Conversion"]
pipeline_why: "AoF's three PhysicalDamageConvertToFire / LightningDamageConvertToFire / ColdDamageConvertToFire BASE 50 mods enter buildConversionTable (CalcOffence.lua:1939-1986) and calcDamage recurses over the earlier types (CalcOffence.lua:70-113), so the fire damage is built before increased and more; the DealNo flags are read afterwards as canDeal (CalcOffence.lua:1932-1935) and zero every non-fire type at the hit (CalcOffence.lua:3408), in skill DoT (5814-5818) and in the ailment source damage (4318)."
pob:
  measured: full
  how: "Node name line parses to Keystone LIST + Condition:HaveAvatarOfFire (Data/ModCache.lua:14326, used by 'while you have Avatar of Fire' mods, ModParser.lua:1922-1923); stat line 1 parses to PhysicalDamageConvertToFire, LightningDamageConvertToFire, ColdDamageConvertToFire BASE 50 (Data/ModCache.lua:10369 from Modules/ModParser.lua:2264-2268); stat line 2 parses to DealNoPhysical, DealNoLightning, DealNoCold, DealNoChaos FLAG (Data/ModCache.lua:15074 from ModParser.lua:5302 and dealNoNonDamageType 2018-2030; DealNoFire is not set). Keystone mods enter through modLib.mergeKeystones (Modules/ModTools.lua:248-259, CalcSetup.lua:775). Consumers in Modules/CalcOffence.lua: canDeal[type] = not Flag(DealNo<type>, DealNoDamage) at 1932-1935; hit damage of a type is computed only if canDeal (3408) while the conversion recursion reads the earlier types' base damage whatever canDeal says (70-113), so converted fire survives while the unconverted half is dropped; ailments take their source damage only from canDeal types (calcAverageSourceDamage 4318, freeze 5405-5408, bleed 4413, poison 4686, ignite 4991, 5103-5131, impale 5597); skill DoT of a blocked type is 0 (5814-5818). Measured: table above; Fireball +0.29% / +0.26%, Worb 0, FR 0. NOT modelled: the 4-s-in-8-s window of Vulconus (config box conditionHaveVulconus turns AoF on for the whole fight), how the game treats ailments of converted damage, enemy-side effects, minion versions beyond the MinionModifier keystone."
  config:
    - {var: conditionHaveVulconus, default: false, ref: "Modules/ConfigOptions.lua:1677-1680 (ifFlag Condition:HaveVulconus; sets Condition:HaveAvatarOfFire and the Avatar of Fire keystone for the whole fight)", class: b}
  unparsed:
    - "Xoph's Blood (Data/Uniques/amulet.lua:1357): 'Cover Enemies in Ash when they Hit you' - Data/ModCache.lua:14803 is nil (the combined try with the Avatar of Fire line at :14804 is nil too); the Avatar of Fire line itself parses (:14326)"
    - "Earendel's Embrace: 'Summoned Skeletons Cover Enemies in Ash on Hit' - Data/ModCache.lua:22000 is nil; the 'Summoned Skeletons have Avatar of Fire' line parses (:22004)"
model: null
providers:
  - {kind: keystone, name: "Avatar of Fire", slot: tree, role: applies, target: self, text: "50% of Physical, Cold and Lightning Damage Converted to Fire Damage / Deal no Non-Fire Damage (node 44941, left side of the tree between Templar and Marauder)", source: "TreeData/3_29/tree.lua:28408,28412; Data/ModCache.lua:10369,15074; wiki Avatar of Fire rev 1625575", pob: full}
  - {kind: unique, name: "Xoph's Blood", slot: Amulet, role: applies, target: self, text: "Avatar of Fire (the modifier, same effect as the keystone; the keystone on top gives nothing extra) plus Cover Enemies in Ash when they Hit you, 10% increased maximum Life, +(20-40)% Fire Resistance, Damage Penetrates 10% Fire Resistance", source: "Data/Uniques/amulet.lua:1346-1358; Data/ModCache.lua:14326; wiki Avatar of Fire rev 1625575", pob: full}
  - {kind: unique, name: "Vulconus", slot: Dagger, role: applies, target: self, text: "Every 8 seconds, gain Avatar of Fire for 4 seconds (4/8 = 50% of the time); 50% of Physical Damage Converted to Fire while you have Avatar of Fire; (160-200)% increased Critical Strike Chance while you have it; +2000 Armour while you do NOT have it. PoB: config box conditionHaveVulconus = on the whole fight", source: "Data/Uniques/dagger.lua:286,301-306; Modules/ConfigOptions.lua:1677-1680; Modules/ModParser.lua:5462", pob: config}
  - {kind: unique, name: "Earendel's Embrace (and Replica)", slot: Sceptre, role: applies, target: self, text: "Summoned Skeletons have Avatar of Fire (Replica: Raised Zombies); minion only, via MinionModifier Keystone", source: "Data/Uniques/mace.lua:509,522; Modules/ModParser.lua:4466,4482", pob: partial}
  - {kind: tattoo, name: "Keystone tattoo: Avatar of Fire", slot: tree, role: applies, target: self, text: "tattoo entry that turns a passive into Avatar of Fire", source: "Data/TattooPassives.lua:179", pob: full}
  - {kind: mod, name: "Crucible weapon tree: Avatar of Fire", slot: Weapon, role: applies, target: self, text: "WeaponTreeKeystoneAvatarOfFire (weapon tree keystone, level 30; weights sword 20, axe 20, mace 40, sceptre 20, staff 20)", source: "Data/Crucible.lua:1350", pob: full}
  - {kind: keystone, name: "Bitter Frost", slot: tree, role: blocks, target: self, text: "Cannot deal non-Cold Damage: with Avatar of Fire every type is blocked = 0 damage (measured on Worb)", source: "TreeData/3_29/tree.lua:56305; headless probe 2026-10-26 (DealNo source Tree:12128)", pob: full}
  - {kind: support, name: "Void Manipulation", slot: any, role: blocks, target: self, text: "deals no cold, fire or lightning damage (chaos-only); with Avatar of Fire every type is blocked = 0 damage (measured on FR)", source: "headless probe 2026-10-26 (DealNo source Skill:SupportVoidManipulation); Data/Skills/sup_dex.lua:4559-4560", pob: full}
makes_redundant:
  - {provider: "Avatar of Fire keystone", when: "Xoph's Blood (or another item with the 'Avatar of Fire' modifier) is equipped", why: "wiki: the unique modifier has the same effect as the keystone and taking both gives no additional benefit", source: "https://www.poewiki.net/wiki/Avatar_of_Fire rev 1625575 (Related unique items)"}
  - {provider: "Vulconus's 'Every 8 seconds, gain Avatar of Fire for 4 seconds'", when: "the Avatar of Fire keystone is allocated", why: "the keystone is permanent, the timed grant adds nothing; Vulconus's own 50% physical to fire and crit lines then count for the whole fight (PoB: the keystone sets Condition:HaveAvatarOfFire, so Vulconus's conditional mods are always on and its 50% would be added to the keystone's 50%, sum 100% physical to fire - game behaviour unverified)", source: "Data/Uniques/dagger.lua:301-306; Data/ModCache.lua:14326,10364"}
conflicts:
  - {with: "Bitter Frost, Void Manipulation, any 'Deal no Non-X' / 'Cannot deal non-X' source", effect: "every damage type ends up blocked: total damage 0 (Worb 1,343,497.5 -> 0, FR FullDPS 57,001,026.5 -> 0, both scenarios)", source: "headless probe 2026-10-26; Modules/CalcOffence.lua:1932-1935; Modules/ModParser.lua:5302"}
  - {with: "chaos damage (Forbidden Rite, Void Manipulation, Withering, chaos DoT)", effect: "chaos is last in the conversion order, so it cannot be converted to fire and 'Deal no Non-Fire' sets it to 0; the FR spell is 100% chaos", source: "wiki Damage conversion rev 1673519 (order Physical -> Lightning -> Cold -> Fire -> Chaos); headless probe (FR spell: chaos 191,717.9 hit avg, all else 0)"}
  - {with: "cold, lightning and physical builds (Worb, shock/freeze/chill builds, bleed builds)", effect: "half of the type is lost, the rest hits the enemy's fire resistance and loses cold/lightning enemy debuffs (Frostbite, cold exposure, shock): Worb without Bitter Frost -87.86% (Pinnacle) / -73.52% (None); chill and freeze duration outputs disappear; bleed (physical), poison (chaos) and skill DoT of blocked types are gated off in PoB", source: "headless probe 2026-10-26; Modules/CalcOffence.lua:4318,4413,4686,5405-5408,5814-5818"}
  - {with: "Elemental Equilibrium", effect: "no synergy: wiki says EE works against AoF because the player cannot use the cold/lightning weakness it creates; the pair works only with minions that deal cold/lightning damage (minions do not inherit EE, so the player's fire hits permanently expose cold and lightning). The wiki wording ('EE will add fire resistance') is the pre-3.16.0 version; current EE removes the fire exposure and exposes cold and lightning, see [[Elemental Equilibrium]]", source: "https://www.poewiki.net/wiki/Avatar_of_Fire rev 1625575; wiki Elemental Equilibrium rev 1605611"}
  - {with: "self-damage (Blood Rage, Forbidden Rite)", effect: "not affected by the conversion or the no-non-fire rule", source: "wiki Avatar of Fire rev 1625575"}
conditions:
  - {text: "permanent while allocated; no condition, no uptime", source: "TreeData/3_29/tree.lua:28408-28412"}
  - {text: "AoF's 50% adds to other conversions of the same source type; if the sum of 'converted to' lines for one type exceeds 100%, skill sources take precedence and the gear/passive part (incl. AoF) is scaled down to the rest", source: "wiki Damage conversion rev 1673519 (Overconversion); vault [[Damage calculation#Conversion]]"}
  - {text: "gain-as-extra is computed on the source type before 'converted to' removes it; the gained part is a damage type of its own and meets the same conversion and the no-non-fire check at the end (the what-ifs above used flat added damage, which is base damage of that type; a gain-as-extra line itself was not probed)", source: "wiki Damage conversion rev 1673519 (conversion order paragraph); Modules/CalcOffence.lua:70-113, 1932-1935"}
  - {text: "the keystone's text is the same in tree.lua 3_29 and the wiki cargo passive_skills; the conversion of cold and lightning (not only physical) is part of the current text; the date of that change is not on the wiki page", source: "TreeData/3_29/tree.lua:28412; wiki cargo passive_skills 'Avatar of Fire'; wiki Avatar of Fire rev 1625575 (version history ends at 1.0.0)"}
uptime:
  Mapping:
    value: always
    config: {conditionHaveVulconus: "only for the Vulconus variant; PoB treats it as 100%, the item gives 50%"}
    reasoning: "a keystone is on all the time; the cost (blocked types, lost ailments) is also permanent; no enemy condition is needed"
    source: "TreeData/3_29/tree.lua:28408-28412"
  Pinnacle Boss:
    value: always
    config: {conditionHaveVulconus: "Vulconus: AoF is up 4 s of every 8 s = 50% (dagger.lua:301); correct the crit and conversion lines by 50% if the box is ticked"}
    reasoning: "same as Mapping; the enemy's fire resistance is what matters: Pinnacle 50 (effective 67.5% with Worb's Eye of Malice) vs None 0, so the same build gains or loses a different share in each scenario (Fireball what-if +38% Pinnacle vs +29% None for cold, +19% vs +37% for physical)"
    source: "Data/Uniques/dagger.lua:301; headless probe 2026-10-26"
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Avatar_of_Fire (rev 1625575)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Damage_conversion (rev 1673519)", kind: wiki, patch: "3.29"}
  - {ref: "poewiki cargo passive_skills 'Avatar of Fire' stat text = the tree.lua text", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:28408,28412,56305; Data/ModCache.lua:10364,10369,14326,14803,15074,22000,22004; Modules/ModParser.lua:1922-1923,2018-2030,2264-2268,4466,4482,5302,5462; Modules/CalcOffence.lua:70-113,1932-1986,3408,4318,4413,4686,5405-5408,5814-5818; Modules/ConfigOptions.lua:1677-1680; Modules/ModTools.lua:248-259; Data/Uniques/amulet.lua:1346-1358, dagger.lua:286-306, mace.lua:509,522; Data/TattooPassives.lua:179; Data/Crucible.lua:1350", kind: pob, patch: "3.29"}
  - {ref: "headless probe 2026-10-26: Fireball Elementalist (league_start), Worb, FR CoC Occu Three Dragons v4, both enemyIsBoss scenarios, plus what-ifs (Bitter Frost removed; added damage lines); scratchpad b3c/probe.py, probeBF.py, probeAdd.py, frtypes2.py", kind: discovery, patch: "3.29"}
not_verified:
  - "how the game treats the ailments of damage that was converted: PoB drops chill and freeze when no cold damage remains (measured) and gates bleed/poison on physical/chaos; the wiki Damage conversion page (rev 1673519) has no ailment rule for converted damage, so whether fire converted from cold can freeze or chill is undocumented here"
  - "why ShockChance and ShockEffectMod stayed in the PoB output after lightning was removed (Fireball with added lightning + AoF, Worb): the cause was not traced"
  - "the date AoF began to convert cold and lightning (the wiki version history ends at 1.0.0; Vulconus still says 'Physical only'): no patch note found"
  - "Vulconus + keystone: PoB would add the keystone's 50% and Vulconus's 50% physical to fire (sum 100%); the game behaviour with both is unverified (the wiki only says the keystone is redundant next to the unique's Avatar of Fire modifier)"
  - "the wiki's line about Elemental Equilibrium describes the old (pre-3.16.0) resistance version: 'EE will add fire resistance to the enemy'; the current EE exposes cold and lightning and removes fire exposure"
  - "break-even rule 'fire-only multiplier above 2' is derived from the PoB pipeline and the Fireball what-ifs, not from a source; it ignores resistance and penetration differences"
  - "gain-as-extra under AoF (e.g. physical gained as cold): follows from the documented order and the PoB code but was not measured"
  - "Foulborn/variant versions of Xoph's Blood and Vulconus beyond the base lines read here; Replica Earendel's Embrace zombies not probed"
  - "FR spell's own chaos share was read from PoB (X=191,717.9, others 0); a version of FR without Void Manipulation was not probed"
open_questions:
  - "For the generator: should AoF be offered only as a package (fire-only skills, no chaos/cold/lightning support gems, fire-only flat added damage) and rejected whenever a DealNo source or a non-fire damage type exists, or does the user want to see the Fireball-style +0.3% as a candidate?"
```
