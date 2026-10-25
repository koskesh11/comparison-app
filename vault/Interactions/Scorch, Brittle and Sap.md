---
type: interaction
status: draft
pob_refs: [EnemyScorchChance, EnemyBrittleChance, EnemySapChance, ScorchChanceOnHit, BrittleChanceOnHit, SapChanceOnHit, ScorchChanceOnCrit, BrittleChanceOnCrit, SapChanceOnCrit, ScorchEffectMod, BrittleEffectMod, SapEffectMod, ScorchDuration, CurrentScorch, CritAlwaysAltAilments, IgniteCanScorch, ScorchCanStack, inflictScorch, inflictBrittle, inflictSap, conditionEnemyScorched, conditionScorchedEffect, ScorchStacks, conditionEnemyBrittle, conditionBrittleEffect, conditionEnemySapped, conditionSapEffect, ailmentMode, enemyIsBoss]
source: "poewiki Scorch rev 1673547, Brittle rev 1553576, Sapped rev 1660590, Ailment rev 1673310, Version 3.25.0 rev 1698361 (fetched 2026-10-25); PoB 2.67.2 CalcOffence.lua / CalcPerform.lua / CalcDefence.lua / Data.lua / ModParser.lua / ConfigOptions.lua; PoB Data/Uniques, TreeData/3_29/tree.lua; vault Models/Own shock effect, Interactions/Enemy ailment threshold"
last_confirmed_patch: "3.29.x"
---

The three "alternate" elemental ailments, one per element: Scorch (fire) lowers the target's elemental resistances by up to 30%, Brittle (cold) gives hits against it up to +6% critical strike chance, Sap (lightning) makes it deal up to 20% less damage, each for 4 s. Size is (D/T)^0.4 of the hit of that element against the ailment threshold, so all three reach their maximum at about 28% of the threshold (0.6^2.5 = 27.89%). They normally need a chance (crits do not inflict them) and count as elemental ailments for [[Elemental ailment count]]. PoB reads only a chance for them: the effect is the config pair "Is the enemy Scorched / Effect of Scorched" (same for Brittle, Sap), so the build value is invisible until you tick and size it; the size model is the one in [[Own shock effect]] with other constants. Related: [[Shock]], [[Ignite]] (Oath of Summer turns ignite into scorch), [[Exposure]] (a different resistance debuff, strongest applies per element), [[Enemy ailment threshold]], [[Chance on hit uptime]].

Pipeline: [[Damage calculation#Resistance, exposure and penetration]] - Scorch lowers the enemy's elemental resistance before the hit, so it works like exposure for fire, cold and lightning builds and not for physical or chaos builds; also [[Damage calculation#Critical strike]] for Brittle and [[Receiving damage#Damage taken modifiers]] for Sap (the enemy deals less damage to you).

```interaction
id: scorch-brittle-sap
mechanic: "Fire hits scorch (-up to 30% to all elemental resistances), cold hits make brittle (+up to 6% critical strike chance against it), lightning hits sap (target deals up to 20% less damage); 4 s each; size from the hit of that element vs the ailment threshold, Scorch 50 x (D/T)^0.4, Brittle 10 x (D/T)^0.4, Sap 100/3 x (D/T)^0.4, times (1+effect mods); crits do NOT inflict them without Secrets of Suffering; non-hit sources use the base 10% / 2% / 6%"
family: ailment
target: enemy
related: [shock, ignite, exposure, elemental-ailment-count, enemy-ailment-threshold, damage-type-can-ailment, chance-on-hit-uptime]
pipeline_step: ["Damage calculation#Resistance, exposure and penetration", "Damage calculation#Critical strike", "Receiving damage#Damage taken modifiers"]
pipeline_why: "Scorch subtracts from the enemy's elemental resistance that the hit then meets; Brittle adds base crit chance on hits against the enemy; Sap multiplies the enemy's own damage down (it reduces what you take). Each is sized by the hit of its element against the threshold, applied after that hit, and none of them touches the ailment DoTs' flat-damage source"
pob:
  measured: config
  how: "chance only: ailment chance on hit; crit chance is 100% for Ignite/Freeze/Shock but equal to the hit chance for the alternate ailments unless CritAlwaysAltAilments (Secrets of Suffering, ModParser.lua:2369) CalcOffence.lua:4231-4264; the chance just sets skillFlags.inflictScorch/Brittle/Sap (4262-4264), which reveals the config boxes; effect formulas and caps in the breakdown table only (CalcOffence.lua:5344-5376, ScorchEffectMod etc. 5684-5692); Data.lua:424-430 (default 10/2/6, max 30/6/20, duration 4, min 0); NO guaranteed source from hits (CalcPerform.lua:3582 comment), the effect enters only through ScorchVal/BrittleVal/SapVal set by the config (ConfigOptions.lua:1888-1890, 1935-1937, 1962-1964) or the Scorching Skitterbot (CalcPerform.lua:1420-1423), and then Scorch adds ElementalResist -N on the enemy (CalcPerform.lua:3535-3550), Brittle adds SelfCritChance +N (3551-3556, read at CalcOffence.lua:3102-3104), Sap adds Damage MORE -N on the enemy (3557-3562, read for damage taken at CalcDefence.lua:1715,1742). Ticking the condition box without an effect value gives the condition (for The Taming and 'against Scorched Enemies') but 0% effect"
  config:
    - {var: conditionEnemyScorched, default: false, ref: "Modules/ConfigOptions.lua:1884 (shown only with inflictScorch)", class: b}
    - {var: conditionScorchedEffect, default: 0, ref: "Modules/ConfigOptions.lua:1888 (count; the resistance reduction in %; tooltip 'up to -30%')", class: c}
    - {var: ScorchStacks, default: 0, ref: "Modules/ConfigOptions.lua:1892 (needs ScorchCanStack, Oath of Summer)", class: c}
    - {var: conditionEnemyBrittle, default: false, ref: "Modules/ConfigOptions.lua:1931 (shown only with inflictBrittle)", class: b}
    - {var: conditionBrittleEffect, default: 0, ref: "Modules/ConfigOptions.lua:1935 (count; critical strike chance in %, tooltip 'up to +6%')", class: c}
    - {var: conditionEnemySapped, default: false, ref: "Modules/ConfigOptions.lua:1958 (shown only with inflictSap)", class: b}
    - {var: conditionSapEffect, default: 0, ref: "Modules/ConfigOptions.lua:1962 (count; damage dealt reduction in %, tooltip 'up to 20%')", class: c}
    - {var: conditionEnemyOnScorchedGround, default: false, ref: "Modules/ConfigOptions.lua:1895 (Brittle/Sapped ground: 1939, 1966; also implies the ailment)", class: b}
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (sets the threshold T, see enemy-ailment-threshold)", class: b}
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210", class: b}
  unparsed:
    - "Legacy of Fury 'Nearby Enemies are Scorched' (variant 2): parsed as an enemy Condition:Scorched flag only (Data/ModCache.lua:18344), no resistance value: the effect still needs conditionScorchedEffect"
model:
  proposed_kind: alt_ailment_effect_uptime
  inputs: {from_pob: ["<Fire|Cold|Lightning>HitAverage and CritAverage", ScorchEffectMod, BrittleEffectMod, SapEffectMod, ScorchChanceOnHit, BrittleChanceOnHit, SapChanceOnHit, ScorchChanceOnCrit, Speed, HitChance, CritChance, ScorchDuration], from_scenario: [enemy ailment threshold T (enemy-ailment-threshold), "m = hits per use on ONE target (chance-on-hit-uptime)"]}
  params: {scorch: {base: 50, max: 30, default: 10}, brittle: {base: 10, max: 6, default: 2}, sap: {base: 33.33, max: 20, default: 6}, exponent: 0.4, duration_s: 4}
  formula: "per ailment: raw = base x (D/T)^0.4 x (1 + M); effect = min(raw, max), rounded down (Scorch/Sap to whole %, Brittle to 0.01); D = that element's hit damage (crit damage on crits); applied only when the chance rolls; uptime u from [[Chance on hit uptime]] (p = chance, d = 4 s, refresh): u = 1-(1-p)^(m*n); feed PoB: tick the condition box and set the effect box to floor(u x effect) only when u >= 0.99, otherwise blend two PoB runs"
  calibration: "wiki and PoB use the same formulas and maxima (Scorch 1/2, Brittle 10, Sap 1/3 times (D/T)^0.4; maximum at D/T about 27.89%); no in-game norm found for u"
providers:
  - {kind: keystone, name: "Secrets of Suffering", slot: tree, role: enables, target: enemy, text: "Cannot Ignite, Chill, Freeze or Shock; Critical Strikes inflict Scorch, Brittle and Sapped (the only crit source; PoB: CritAlwaysAltAilments)", source: "TreeData/3_29/tree.lua:85638 (node 57280); Modules/ModParser.lua:2369; Modules/CalcOffence.lua:4247-4250", pob: full}
  - {kind: unique, name: "Flamesight", slot: Helmet, role: applies, target: enemy, text: "25% chance to Scorch Enemies (variant 1) / (25-50)% (variant 2); Cannot inflict Ignite", source: "Data/Uniques/helmet.lua:636-640", pob: full, variant: "variants 1 and 2"}
  - {kind: unique, name: "Galesight", slot: Helmet, role: applies, target: enemy, text: "25% / (25-50)% chance to inflict Brittle; Cannot inflict Freeze or Chill", source: "Data/Uniques/helmet.lua:650-654", pob: full, variant: "variants 1 and 2"}
  - {kind: unique, name: "Thundersight", slot: Helmet, role: applies, target: enemy, text: "25% / (25-50)% chance to Sap Enemies; Cannot inflict Shock", source: "Data/Uniques/helmet.lua:776-780", pob: full, variant: "variants 1 and 2"}
  - {kind: unique, name: "Leadership's Price", slot: Amulet, role: applies, target: enemy, text: "You have Scorching Conflux, Brittle Conflux and Sapping Conflux while your two highest Attributes are equal (PoB: EnemyScorch/Brittle/SapChance 100 plus the other damage types can scorch, brittle or sap, conditional on the two highest attributes being equal)", source: "Data/Uniques/amulet.lua:816; Modules/ModParser.lua:3800-3806", pob: full}
  - {kind: unique, name: "The Unseen Hue", slot: Ring, role: applies, target: enemy, text: "Hits with Prismatic Skills always Scorch / inflict Brittle / Sap (by variant)", source: "Data/Uniques/ring.lua:1731-1743; Modules/ModParser.lua:3828; Data/ModCache.lua:16965-16967", pob: full}
  - {kind: ascendancy, name: "Oath of Summer (Raider)", slot: tree, role: scales, target: enemy, text: "Hits that would Ignite instead Scorch; You can inflict an additional Scorch on each Enemy (3.25.0; ScorchStacks config)", source: "TreeData/3_29/tree.lua:84777-84779 (node 33645); Modules/ModParser.lua:3036-3037; Modules/CalcPerform.lua:3539-3545; wiki Version 3.25.0 rev 1698361", pob: partial}
  - {kind: unique, name: "Legacy of Fury", slot: Boots, role: applies, target: enemy, text: "Nearby Enemies are Scorched (variant 2); (30-50)% increased Effect of Scorch; Drops Scorched Ground while moving (variant 1)", source: "Data/Uniques/boots.lua:763-769; Modules/ModParser.lua:5717; Data/ModCache.lua:18344", pob: partial, variant: "variant 2"}
  - {kind: unique, name: "Dawnbreaker", slot: Shield, role: applies, target: enemy, text: "Scorch Enemies in Close Range when you Block", source: "Data/Uniques/shield.lua:88; Modules/ModParser.lua:3768", pob: full}
  - {kind: unique, name: "Algor Mortis", slot: Gloves, role: applies, target: enemy, text: "(20-30)% chance to Sap Enemies in Chilling Areas", source: "Data/Uniques/gloves.lua:929; Modules/ModParser.lua:3840", pob: partial}
  - {kind: unique, name: "The Arkhon's Tools (Scorching Skitterbot)", slot: Belt, role: applies, target: enemy, text: "Summon Skitterbots also summons a Scorching Skitterbot (guaranteed Scorch at the skill default 10% x effect, no hit needed)", source: "Data/Uniques/belt.lua:1041-1043; Modules/ModParser.lua:3873; Modules/CalcPerform.lua:1420-1423", pob: full}
  - {kind: support, name: "Elemental Focus Support", slot: any, role: blocks, target: enemy, text: "supported skill cannot inflict status ailments, so no scorch, brittle or sap", source: "Data/SkillStatMap.lua:1059-1066", pob: full}
makes_redundant: []
conflicts:
  - {with: "Secrets of Suffering vs shock/freeze/chill/ignite", effect: "the keystone forbids Ignite, Chill, Freeze and Shock on the same build; it is the price for crit-driven scorch, brittle and sap", source: "TreeData/3_29/tree.lua:85638"}
  - {with: "Galesight / Flamesight / Thundersight", effect: "each forbids the main ailment of its own element (Flamesight no Ignite, Galesight no Freeze or Chill, Thundersight no Shock)", source: "Data/Uniques/helmet.lua:638,652,778"}
  - {with: "Exposure", effect: "Scorch lowers all elemental resistances like fire/cold/lightning exposure; PoB adds Scorch as ElementalResist on the enemy and exposure as the element's own Resist; they are separate lines in the enemy resist, so they add (wiki does not say; not verified)", source: "Modules/CalcPerform.lua:3535-3550, 3629-3658"}
conditions:
  - {text: "wiki quote: \"Scorch is an Elemental Ailment associated with fire that causes the affected target to have their Elemental Resistances lowered by up to 30%, based on the Fire Damage of the Hit, for 4 seconds.\" (3.10.0: max 30%, was 20%; duration 4 s, was 2)", source: "wiki Scorch rev 1673547, Version history 3.10.0"}
  - {text: "wiki quote: \"Hits against brittle enemies have up to +6% chance to critically strike afflicted enemies, based on the Cold Damage of the Hit that inflicted this ailment, for 4 seconds.\" (3.19.0: max +6% was +15%, default +2% was +5%)", source: "wiki Brittle rev 1553576, Version history 3.19.0"}
  - {text: "wiki quote: \"The player and enemies can deal up to 20% less damage due to the sap ailment.\" Formula E = 1/3 x (D/T)^0.4 x (1+M); non-hit sap 6% (e.g. Transfer-attuned Spirit Shield)", source: "wiki Sapped rev 1660590"}
  - {text: "wiki quote: \"The base chance to inflict all other ailments is 0%.\" (Critical strikes have 100% chance only for Ignite, Freeze and Shock); same-type instances have independent timers and only the strongest applies", source: "wiki Ailment rev 1673310; PoB Modules/CalcOffence.lua:4246-4250"}
  - {text: "the three secondary ailments count as elemental ailments (Ignite, Chill, Freeze, Shock, Scorch, Brittle, Sap = 7 types); duration modifiers for elemental ailments apply; since 3.21.1 they are not discarded for duration below 300 ms", source: "wiki Ailment rev 1673310; Version 3.21.1; vault Interactions/Elemental ailment count"}
uptime:
  Mapping:
    value: model
    config: {conditionEnemyScorched: "model: tick only when u >= 0.99", conditionScorchedEffect: "model: floor(u x effect) with effect from D/T of the fire hit (non-boss T, usually at the cap for pack hits)", conditionEnemyBrittle: "same with conditionBrittleEffect", conditionEnemySapped: "same with conditionSapEffect"}
    reasoning: "PoB drops the chance, so a 25-50% helmet line is a checkbox of 100% uptime or nothing; fast skills keep 4 s ailments up, slow single hits do not; pack T is about monster life so the effect is often at its cap; the Own shock effect model gives the same chain"
    source: "Modules/CalcOffence.lua:4231-4264,5344-5376; vault Interactions/Chance on hit uptime; vault Models/Own shock effect"
  Pinnacle Boss:
    value: model
    config: {conditionEnemyScorched: "model as above", conditionScorchedEffect: "model: boss T is huge (PoB x 7.68 x 404%), so a small fire hit gives a small scorch; D/T about 28% is needed for the maximum", conditionEnemyBrittle: "same", conditionEnemySapped: "same"}
    reasoning: "one target collects every hit (u from hit rate x chance x 4 s); effect size comes from T with enemyIsBoss; a crit-only source (Secrets of Suffering) has p = crit chance, not 100% of hits"
    source: "Modules/CalcOffence.lua:5333-5343; Modules/ConfigOptions.lua:2122,2157,2191; vault Interactions/Enemy ailment threshold"
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Scorch (rev 1673547, 2026-07-15)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Brittle (rev 1553576, 2025-08-04)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Sapped (rev 1660590, 2026-07-07)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310, 2026-07-11); Version_3.25.0 (rev 1698361): Oath of Summer", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:3102-3104,4231-4264,5344-5376,5684-5692; Modules/CalcPerform.lua:1420-1423,3498-3606; Modules/CalcDefence.lua:1715,1742; Modules/Data.lua:419-430; Modules/ConfigOptions.lua:1884-1968; Modules/ModParser.lua:2369,3036-3037,3768,3800-3806,3828,3840,3873 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "vault/Models/Own shock effect.md (verified by user 2026-10-22) and vault/Interactions/Enemy ailment threshold.md", kind: pob, patch: "3.29"}
not_verified:
  - "CONFLICT wiki vs PoB: the wiki pages say a base effect below 2% (Scorch), 1% (Brittle) and 2% (Sap) is discarded; PoB data min is 0 for all three (Data.lua:428-430), so PoB may count tiny effects the game discards"
  - "whether the alternate ailments are applied after the hit's damage (the Shock page says so for shock; the Scorch, Brittle and Sapped pages do not state it)"
  - "whether Scorch's elemental resistance reduction and exposure add up on the enemy as PoB shows (wiki silent)"
  - "Sap's effect on the player side: the wiki says 'enemies and the player' deal less damage; PoB applies it to the enemy's damage only"
  - "the PoB boss threshold factors (7.68, +404%) come from PoB data and are not checkable on the wiki (see enemy-ailment-threshold)"
  - "which unique/tree providers beyond those listed exist: the tree grep found only Secrets of Suffering and Oath of Summer for these ailments; the small 'Scorch chance' nodes of older trees were not found in 3_29"
  - "no seed uses these ailments; The Taming (Elemental ailment count) counts them if they are present"
open_questions: []
```
