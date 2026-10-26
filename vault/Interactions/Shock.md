---
type: interaction
status: draft
pob_refs: [conditionEnemyShocked, conditionShockEffect, ShockChanceOnHit, ShockChanceOnCrit, ShockEffectMod, ShockDuration, ShockMax, ChaosCanShock, LightningCannotShock, ailmentMode, enemyIsBoss]
source: "poewiki Shock rev 1606037, Ailment rev 1673310 (fetched 2026-10-24); PoB 2.67.2 CalcOffence.lua / CalcPerform.lua / ConfigOptions.lua / ModParser.lua; vault Models/Own shock effect; Data/Uniques, TreeData/3_29/tree.lua, Data/Skills"
last_confirmed_patch: "3.29.x"
---

Shock is a debuff that makes the enemy take more damage (default max 50%, 2 s base duration). Hits with lightning damage (or damage allowed to shock) shock; crits shock 100%. Strength = 50% x (hit damage / ailment threshold)^0.4 x (1 + effect mods), minimum 5%. PoB computes the effect only in a breakdown table; DPS changes only through the config pair `conditionEnemyShocked` + `conditionShockEffect` or a guaranteed source. The existing verified chain for how big your own shock is: [[Own shock effect]] (reuse, do not redo). The Foulborn The Three Dragons chaos-shock mutation is described in [[Foulborn The Three Dragons]]. Related: [[Freeze]], [[Chill]], [[Enemy ailment threshold]], [[Damage type can ailment]], [[Elemental ailment count]]. Providers beyond the seed set: see tasks/reports/027-research.md.

Pipeline: [[Damage calculation#Damage taken]] - shock is increased damage taken by the enemy, additive with other taken mods (not a more multiplier), applied after the hit that caused it; PoB counts it only through the shock config pair

```interaction
id: shock
mechanic: "Hits with lightning damage (or damage allowed to shock) shock: enemy takes increased damage, E = 50% x (D/T)^0.4 x (1+M), min 5%, default max 50%, base duration 2 s; crits shock 100%; shocks do not stack (strongest applies) except with Oath of Spring; a hit applies shock AFTER its damage"
family: ailment
pipeline_step: ["Damage calculation#Damage taken"]
pipeline_why: "shock is increased damage taken by the enemy, additive with other taken mods (not a more multiplier), applied after the hit that caused it; PoB counts it only through the shock config pair"
target: enemy
related: [freeze, chill, enemy-ailment-threshold, damage-type-can-ailment, elemental-ailment-count, exposure]
pob:
  measured: partial
  how: "chance, duration and effect-mod outputs (CalcOffence.lua:5352-5360,5430-5445); the resulting shock vs threshold is a breakdown TABLE only (5446-5495), never an output number; the enemy takes extra damage only if enemyDB ShockVal>0 or a guaranteed source exists (ShockOverride / ShockBase / ShockMinimum; CalcPerform.lua:3519-3535,3560-3596); crit chance 100% unless CritsDontAlwaysShock (CalcOffence.lua:4243-4250); model for the number: vault Models/Own shock effect"
  config:
    - {var: conditionEnemyShocked, default: false, ref: "Modules/ConfigOptions.lua:1943", class: b}
    - {var: conditionShockEffect, default: 0, ref: "Modules/ConfigOptions.lua:1947 (count; ticking only conditionEnemyShocked gives the condition but 0% increased damage taken)", class: c}
    - {var: ShockStacks, default: 0, ref: "Modules/ConfigOptions.lua:1951 (needs the ShockCanStack flag)", class: c}
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210", class: b}
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086", class: b}
  unparsed:
    - "Shaper of Storms: all three lines parse; the effect is inert without the config box. ShockMinimum is not a ShockOverride, so the loop does not set Condition:Shocked for it (CalcPerform.lua:3565-3606; Shaper node 27038 allocated in Worb.xml). M4 on Worb (Aspect of the Brine King left out, TotalDPS, task 027 batch 1, 2026-10-26): box conditionEnemyShocked off = 932,580 (equals the run with the node deallocated, so 0% from Shaper); box on with conditionShockEffect empty = 1,314,291 (+40.9% over box off, Shaper's floor alone = 25 x 1.8 shock effect mod = 45%); as in the file (box on, effect 57) = 1,343,498 (+44.1% over box off), the 57 is above the floor and the 50 max so the node adds nothing there. Default of the box false (ConfigOptions.lua:1943). The sidebar CurrentShock shows 45 while the box is off although nothing is applied (display/DPS mismatch). Replaces the earlier '0% per 021-gate1 N4, not re-measured'. Source: b1-pob-coverage-auditor.md"
model: null
providers:
  # seed: Foulborn The Three Dragons (FR)
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Shock (global flag ChaosCanShock)", variant: "mutation REPLACES the original line 'Your Fire Damage can Shock but not Ignite' (mutated id MutatedUniqueHelmetDexInt4ChaosDamageCanShock)", source: "Data/ModFoulbornMap.jsonc:348 -> Data/ModFoulborn.lua:121; original Data/Uniques/helmet.lua:1669; wiki Modifier stat chaos_damage_can_shock (no local_ prefix = global); vault Gaps/Foulborn The Three Dragons", pob: partial}
  - {kind: unique, name: "The Three Dragons (plain)", slot: Helmet, role: enables, target: enemy, text: "Your Fire Damage can Shock but not Ignite (FireCanShock + FireCannotIgnite); Lightning cannot shock (LightningCannotShock) while the lightning-freeze line stands", source: "Data/Uniques/helmet.lua:1669,1671; Modules/ModParser.lua:3670-3672", pob: full}
  # gems and supports
  - {kind: support, name: "Overcharge Support", slot: any, role: applies, target: enemy, text: "50% chance to shock, shock as though dealt 690% more damage (L20), 25% less damage", source: "Data/Skills/sup_int.lua:5158", pob: full}
  - {kind: support, name: "Innervate Support", slot: any, role: applies, target: enemy, text: "20% chance to shock; added lightning for 8 s after killing a shocked enemy", source: "Data/Skills/sup_int.lua:3953", pob: full, payoff_of: [conditionEnemyShocked, innervateInnervation]}
  - {kind: support, name: "Elemental Proliferation Support", slot: any, role: applies, target: enemy, text: "20% chance to Freeze, Shock and Ignite", source: "Data/Skills/sup_int.lua:2151", pob: full}
  - {kind: support, name: "Coursing Current Support", slot: any, role: scales, target: enemy, text: "3.29.0: L3 shock effect +28%; shocks cause chill and chills cause shock", source: "Data/Skills/sup_int.lua:1318,1340; wiki Version 3.29.0", pob: partial}
  - {kind: gem, name: "Conductivity", slot: any, role: applies, target: enemy, text: "curse: chance_to_be_shocked_% 25 on the cursed enemy (SelfShockChance, CalcOffence.lua:4232) + lightning res -36; uses a curse slot", source: "Data/Skills/act_int.lua:3069,3136", pob: full}
  - {kind: gem, name: "Hexblast", slot: any, role: enables, target: enemy, text: "all damage can shock/freeze/ignite: the only gem that lets chaos damage shock without a unique", source: "Data/Skills/act_int.lua:9084", pob: full}
  - {kind: support, name: "Elemental Focus Support", slot: any, role: blocks, target: enemy, text: "cannot_inflict_status_ailments: supported skill cannot shock (or freeze/chill/ignite)", source: "Data/SkillStatMap.lua:1059-1066", pob: full}
  # uniques
  - {kind: unique, name: "Voltaxic Rift", slot: Bow, role: enables, target: enemy, text: "Your Chaos Damage can Shock; +40% to Maximum Effect of Shock; Hits Shock as though dealing 300% more (variant 4)", source: "Data/Uniques/bow.lua:517-519", pob: full}
  - {kind: unique, name: "Echoforge", slot: Sword, role: enables, target: enemy, text: "Your Chaos Damage can Shock", source: "Data/Uniques/sword.lua:825", pob: full}
  - {kind: unique, name: "Zerphi's Heart", slot: Amulet, role: enables, target: enemy, text: "Chaos Damage can Ignite, Chill and Shock", source: "Data/Uniques/amulet.lua:1025; Modules/ModParser.lua:3674", pob: full, variant: "variant 2"}
  - {kind: unique, name: "Starforge", slot: Sword, role: enables, target: enemy, text: "Your Physical Damage can Shock", source: "Data/Uniques/sword.lua:1034", pob: full, variant: "variant 3"}
  - {kind: unique, name: "Voidforge", slot: Sword, role: enables, target: enemy, text: "Your Elemental Damage can Shock (cold and fire)", source: "Data/Uniques/sword.lua:1070; Modules/ModParser.lua:3644", pob: full, variant: "variant 3"}
  - {kind: unique, name: "Yoke of Suffering", slot: Amulet, role: enables, target: enemy, text: "Your Elemental Damage can Shock; (5-10)% chance to Shock; Enemies take (5-10)% increased Damage per type of Ailment you inflicted (9 types in PoB); drawback 30% REDUCED duration of ailments on Enemies", source: "Data/Uniques/amulet.lua:1370-1374; Modules/ModParser.lua:3604-3613", pob: full, variant: "variant 2"}
  - {kind: unique, name: "Valako's Sign", slot: Ring, role: applies, target: enemy, text: "25% chance to Shock; 40% inc Damage with Hits against Shocked Enemies", source: "Data/Uniques/ring.lua:1475,1483", pob: partial, variant: "variant 4", payoff_of: [conditionEnemyShocked]}
  - {kind: unique, name: "Inpulsa's Broken Heart", slot: Body Armour, role: scales, target: enemy, text: "(15-25)% inc Effect of Shock; Shocked Enemies you Kill Explode; (20-50)% inc Damage if you have Shocked an Enemy Recently; package/drawback 'Unaffected by Shock'", source: "Data/Uniques/body.lua:1272-1279", pob: partial, variant: "variant 3"}
  - {kind: unique, name: "The Taming", slot: Ring, role: applies, target: enemy, text: "10% chance to Freeze, Shock and Ignite; shock counts as one of the 7 elemental ailment types", source: "Data/Uniques/ring.lua:1272", pob: full}
  - {kind: unique, name: "Rashkaldor's Patience", slot: Amulet, role: applies, target: enemy, text: "Always Freeze, Shock and Ignite; drawback 20% reduced duration of Elemental Ailments on Enemies (Current)", source: "Data/Uniques/amulet.lua:939,943", pob: full}
  - {kind: unique, name: "Storm's Gift / The Stormheart / Call of the Brotherhood", slot: various, role: applies, target: enemy, text: "Enemies you kill are Shocked and Shocks you inflict spread within 1.5 m (Storm's Gift gloves); 50% chance to Shock Chilled Enemies (The Stormheart staff); spells have 100% chance to Shock against Frozen Enemies (Call of the Brotherhood, Foulborn swaps it for a frozen-kill power charge)", source: "Data/Uniques/gloves.lua:1116-1117; staff.lua:685; ring.lua:225", pob: partial, payoff_of: [conditionEnemyChilled, conditionEnemyFrozen]}
  - {kind: unique, name: "Vessel of Vinktar", slot: Flask, role: applies, target: enemy, text: "Shocks nearby Enemies during Effect (10% inc damage taken); drawback 'You are Shocked during Effect (50% inc damage taken)'; variant 15 also +(25-40)% Shock effect and spread", source: "Data/Uniques/flask.lua:466-467,472-473", pob: partial, variant: "variants 14-18 Current"}
  # tree
  - {kind: mod, name: "Shock Chance / Lightning Damage and Shock Chance smalls", slot: tree, role: applies, target: enemy, text: "15% chance to Shock (62697); 10% (49588, 61264, 46469); Raider Evasion chance to Shock (5926); Tattoo of the Valako Shaman 5%", source: "TreeData/3_29/tree.lua:59723,50640,85045; Data/TattooPassives.lua:4542", pob: full}
  - {kind: ascendancy, name: "Shaper of Storms (Elementalist)", slot: tree, role: enables, target: enemy, text: "Hits always Shock / Shocks from your Hits always increase Damage taken by at least 25% / All Damage can Shock", source: "TreeData/3_29/tree.lua:50157 (node 27038); Modules/ModParser.lua:2828-2833", pob: partial}
  - {kind: ascendancy, name: "Avatar of the Wilds / Fidelitas' Spike", slot: tree, role: applies, target: enemy, text: "Your Hits always inflict Freeze, Shock and Ignite while Unbound (Raider); Hits always Shock / Deal no Physical Damage (Reliquarian)", source: "TreeData/3_29/tree.lua:84823,20976; Modules/ModParser.lua:3041-3046", pob: full}
  - {kind: mastery, name: "Lightning Mastery (effects 50993, 28569, 64063)", slot: tree, role: scales, target: enemy, text: "+15% to Maximum Effect of Shock; Shocks you inflict spread to other Enemies within 1 metre; maximum Mana modifiers also apply to Shock Effect at 30%", source: "TreeData/3_29/tree.lua:43029,43038,43044", pob: full}
  - {kind: ascendancy, name: "Oath of Spring (Raider)", slot: tree, role: scales, target: enemy, text: "Maximum Effect of Shock is 2% increased Damage taken / You can apply up to 50 Shocks to each Enemy (the only multi-shock source; stacks with itself)", source: "TreeData/3_29/tree.lua:84989 (node 31364)", pob: partial}
  - {kind: notable, name: "High Voltage", slot: tree, role: abuses, target: enemy, text: "100% inc Critical Strike Chance against Shocked Enemies (granted passive in Worb, 021-gate1 N3)", source: "TreeData/3_29/tree.lua:69734 (node 58168)", pob: config, payoff_of: [conditionEnemyShocked]}
  - {kind: notable, name: "Storm Weaver / Stormrider", slot: tree, role: abuses, target: enemy, text: "Enemies Shocked or Frozen by you take 5% increased Elemental Damage (Storm Weaver); 25% inc Cold Damage with Hits vs Shocked and power charge when you Shock a Chilled enemy (Stormrider)", source: "TreeData/3_29/tree.lua:34801,87756", pob: config, payoff_of: [conditionEnemyShocked, conditionEnemyFrozen]}
  - {kind: keystone, name: "Secrets of Suffering", slot: tree, role: blocks, target: enemy, text: "Cannot Ignite, Chill, Freeze or Shock", source: "TreeData/3_29/tree.lua:85638 (node 57280)", pob: full}
  - {kind: keystone, name: "Avatar of Fire / Voracious Flame / Bitter Frost / Perfect Agony", slot: tree, role: blocks, target: enemy, text: "restrict damage types (no lightning) or forbid non-crit ailments", source: "TreeData/3_29/tree.lua:28412,47294,56305,80926", pob: full}
makes_redundant: []
conflicts:
  - {with: "Elemental Focus (support) / Secrets of Suffering", effect: "remove ShockChanceOnCrit and FreezeChanceOnCrit (100 -> 0) with no FR DPS change (verified headless 2026-10-21)", source: "vault Gaps/Foulborn The Three Dragons; Data/SkillStatMap.lua:1059-1066"}
  - {with: "Foulborn The Three Dragons plain lines", effect: "plain Three Dragons stops lightning from shocking; the Foulborn mutation of the fire-shock line removes the FireCannotIgnite drawback with it", source: "Data/Uniques/helmet.lua:1669-1671; Data/ModFoulbornMap.jsonc:346-348"}
conditions:
  - {text: "shock needs at least 5% effect; shocks below the minimum are never applied and do not count as shocking for 'when you shock' stats; the max effect is never 'always 50%' on a boss (huge threshold)", source: "https://www.poewiki.net/wiki/Shock rev 1606037"}
  - {text: "non-damaging shock base effect 15% (was 20% before 3.9.0); increased/reduced effect applies additively after the base and cannot exceed the max; sources of maximum shock effect are additive with each other (3.19.0)", source: "https://www.poewiki.net/wiki/Shock rev 1606037; patch 3.19.0"}
  - {text: "boss threshold in PoB = monsterAilmentThresholdTable[level] x 7.68 x map mults x AilmentThreshold more (Boss +488%, Pinnacle/Uber +404%): see enemy-ailment-threshold", source: "Modules/CalcOffence.lua:5333-5343; Modules/ConfigOptions.lua:2122,2157,2191"}
uptime:
  Mapping:
    value: partial
    config: {conditionEnemyShocked: "ON only with a shock source", conditionShockEffect: "model (vault Models/Own shock effect), not a flat 50"}
    reasoning: "100% on crit or lightning hits, but effect on packs is large only if the hit is big against the threshold; short 2 s duration"
    source: "build-strategist table (tasks/reports/027-research.md); vault Models/Own shock effect"
  Pinnacle Boss:
    value: model
    config: {conditionEnemyShocked: "per vault Models/Own shock effect", conditionShockEffect: "model: e.g. FR CoC v4 26% at Pinnacle T 6,349,995 (+14.4% FullDPS)"}
    reasoning: "boss threshold is huge (404%), so the real effect is often 5-15% for a small hit; the existing PoB-chain model decides"
    source: "vault Models/Own shock effect (verified by user 2026-10-22); Modules/CalcOffence.lua:5333-5343"
seeds: [FR, Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Shock (rev 1606037, 2026-01-25)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:4243-4250,5333-5360; Modules/CalcPerform.lua:3519-3606; Modules/ConfigOptions.lua:1943-1951 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "vault/Models/Own shock effect.md and vault/Gaps/Foulborn The Three Dragons.md", kind: pob, patch: "3.29"}
not_verified:
  - "Worb's own shock source is NOT identified in the evidence; the Worb sample ticks conditionShockEffect 57 but where it comes from is unknown"
  - "the wiki shock formula is tagged 'potentially outdated'; whether the 5% minimum applies before or after effect mods (PoB applies Data min 5 to the final value)"
  - "real shock effect for a given hit vs boss threshold (breakdown only in PoB); the generic boss threshold"
  - "whether chaos shock from Forbidden Rite applies in game as PoB computes it (user to test)"
  - "whether PoB models multiple shocks (Oath of Spring) beyond the ShockCanStack flag; only parse text read"
  - "Shaper of Storms (wiki rev 1537040): the patch number of the 15% -> 25% minimum change is not shown in the fetched text; whether the in-game floor is applied after 'increased Effect of Shock' (wiki and PoB say it is scaled; the Shock page says the 5% minimum comes first); why PoB shows CurrentShock 45 while the condition is off was read from code, not looked up (b1-pob-coverage-auditor.md)"
open_questions:
  - "Which source gives the shock in the Worb sample (conditionShockEffect 57)?"
  - "Impact of Shaper of Storms: EK 'CoC EK Assa' has no Shaper and no shock (CurrentShock 0, enemy ShockVal 0, DamageTaken INC 0), so nothing. Fireball Elementalist: +40.9% TotalDPS in PoB terms only if conditionEnemyShocked is ticked (measured on Worb, not on a fire build; Shaper's All Damage can Shock makes fire hits shock at 100%); the generator must tick the box and leave conditionShockEffect below 45 or empty so the floor decides, otherwise the audit sees 0. Whether a fire build gains the same +40.9% is not measured (Worb's enemy already carries DamageTaken 50 from tree 60170). Which Fireball config should the generator assume for the shock box?"
```
