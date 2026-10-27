---
type: interaction
status: draft
pob_refs: [ImpaleChance, ImpaleChanceOnCrit, ImpaleEffect, ImpaleStacksMax, ImpaleAdditionalDurationChance, ImpaleDuration, ImpaleDurationMod, ImpaleStoredDamage, ImpaleModifier, ImpaleStacks, ImpaleDPS, impaleStoredHitAvg, EnemyImpalePhysicalDamageReduction, IgnoreEnemyImpalePhysicalDamageReduction, multiplierImpalesOnEnemy, conditionImpaledRecently]
source: "poewiki Impale rev 1699530 (2026-08-07), Version 3.25.0 rev 1698361, Version 3.29.0 rev 1699085 (fetched 2026-10-25); PoB 2.67.2 CalcOffence.lua / CalcPerform.lua / CalcSetup.lua / Data.lua / Data/Misc.lua / ConfigOptions.lua / Data/ModCache.lua; PoB Data/Skills/sup_dex.lua, Data/Uniques, TreeData/3_29/tree.lua; vault Interactions/Spell impale"
last_confirmed_patch: "3.29.x"
---

Impale is a debuff, not a damage-over-time ailment: a hit that impales records 10% of its unmitigated physical damage; each later hit on that target (by any source) deals that amount again as reflected physical damage, and consumes one of the 5 hits (or 8 s) the impale lasts. Several impales stack, so the damage per hit is the sum of all active ones (5 stacks = 50% of the recorded hit, times impale effect). The first hit gets nothing. PoB counts it as ImpaleDPS (CombinedDPS) and assumes the stack count is the maximum unless you set it; the ramp-up is not modelled. Spell sources (EK seed: Entropic Devastation) are in [[Spell impale]]. Related: [[Bleed]] (impale effect on bleed, bleed damage per impale), [[Fight length]], [[Enemy ailment threshold]] is NOT used (impale has no threshold).

Pipeline: [[Damage calculation#Ailments from hits]] - the impale stores the unmitigated physical hit and pays out as separate reflected hits, so it works for high-hit-rate physical builds against armoured bosses (armour hits the sum, so stacking helps) and not for a slow single-hit build that never reaches full stacks. It also touches [[Damage calculation#Armour against hits]] (impale damage is mitigated by armour when it pays out) and [[Damage calculation#Damage taken]] (reflected-damage-taken mods apply).

```interaction
id: impale
mechanic: "A hit with a chance to impale records 10% of its unmitigated physical damage in an Impaled debuff (8 s, 5 hits); each later hit on the target deals the stored amount of every active impale as reflected physical damage (no damage on the first hit); impale effect scales it; mitigated by armour and physical reduction when it pays out; cannot be evaded, blocked or suppressed"
family: ailment
target: enemy
related: [spell-impale, bleed, chance-on-hit-uptime, fight-length]
pipeline_step: ["Damage calculation#Ailments from hits", "Damage calculation#Armour against hits", "Damage calculation#Damage taken"]
pipeline_why: "The impale records the hit before the target's mitigation (like damaging ailments), then pays out as a separate reflected hit that armour, physical damage reduction and damage-taken mods act on; adding more stacks raises the combined payout and so beats armour better than one big hit"
pob:
  measured: partial
  how: "stored hit = average unmitigated physical hit, crit-weighted (CalcOffence.lua:3396,3503-3509); chance on hit/crit CalcOffence.lua:4268 (effective mode only); stored damage 10% (Data.lua:268) x (1+ImpaleEffect inc) x ImpaleEffect more, plus the impale-effect-on-bleed term CalcOffence.lua:5605-5611; stacks = min(max, config) with max = ImpaleStacksMax (base 5, CalcSetup.lua:49, Data/Misc.lua:124) x (1 + extra-hit chance) CalcOffence.lua:5601-5603; config blank = MAX stacks (CalcPerform.lua:3384-3391); modifier = stored x stacks x (1 - physical reduction incl. enemy armour against the payout, CalcOffence.lua:5613-5618) x chance x reflected/physical damage taken CalcOffence.lua:5619-5622; ImpaleDPS = stored hit x (modifier - 1) x hit chance x dpsMultiplier (x hit rate when not average) added to CombinedDPS CalcOffence.lua:6159-6175; duration 8 s x ImpaleDuration mod rounded up to server ticks CalcOffence.lua:1639-1642 (DPS is 0 when duration <= 0). NOT computed: the ramp (no damage on the first hit), the real stack count at a low hit rate (PoB uses the maximum x chance), impales on dead enemies / Call of Steel, The Impaler keystone, 'Impales gain increased effect once 1 s has expired'"
  config:
    - {var: multiplierImpalesOnEnemy, default: "blank = maximum", ref: "Modules/ConfigOptions.lua:1651 (count, allows 0; visible with the impale flag; PoB clamps to the maximum at CalcPerform.lua:3388-3391)", class: c}
    - {var: conditionImpaledRecently, default: false, ref: "Modules/ConfigOptions.lua:1648 (for 'if you have Impaled Recently' mods, not for ImpaleDPS)", class: b}
  unparsed:
    - "The Impaler keystone (node 57257): 'Inflict 5 additional Impales on Enemies you Impale ... cannot be Impaled again for 5 s': Data/ModCache.lua:17171-17173, 22484-22486 (no mod)"
    - "Deliberate Brutality (node 56146): 'Impales you inflict gain 50% increased Effect once 1 second of Duration has expired': Data/ModCache.lua:17109 (no mod)"
    - "Impale Mastery 'chance on Hit to remove all Impales ... multiply Reflected Damage': Data/ModCache.lua:6284-6285 mis-parses a leading '20%' as Damage BASE 20 (flags 4)"
model:
  proposed_kind: impale_stack_count
  inputs: {from_pob: [ImpaleChance, ImpaleChanceOnCrit, ImpaleStacksMax, ImpaleAdditionalDurationChance, ImpaleDuration, HitSpeed, Speed, HitChance], from_scenario: ["H = hits per second on ONE target from ALL skills (every hit consumes one hit of every impale; chance-on-hit-uptime defines V and m)"]}
  params: {hits_per_impale_N: "ImpaleStacksMax x (1 + ImpaleAdditionalDurationChance/100), base 5", duration_d_s: "ImpaleDuration, base 8"}
  formula: "steady-state active impales S = c x min(N, H x d) with c = impale chance per hit (crit-weighted), N hits and d seconds of life (each impale lives min(N/H, d) s and is applied at c x H per s); PoB's S is c x N, equal for H x d >= N (H >= 0.625 hits/s with N 5, d 8); below that PoB overstates by N/(H x d); ramp time to S about N / (c x H) s, damage per hit = stored hit x 0.1 x S x impale effect; floor to whole percent. Derived from the wiki mechanics, not a wiki formula"
  calibration: "no norm found; derived: 5 hits and 8 s from wiki Impale rev 1699530 (PoB Data/Misc.lua:123-124); check against a PoB run with multiplierImpalesOnEnemy set to the model S"
providers:
  - {kind: support, name: "Impale Support", slot: any, role: applies, target: enemy, text: "60% chance to Impale on Hit with Attacks (attacks_impale_on_hit_%_chance 60); more physical damage; an enemy physical reduction penalty; requires an Attack skill (cannot support spells)", source: "Data/Skills/sup_dex.lua:2472-2520 (chance at 2494)", pob: full}
  - {kind: notable, name: "Savage Skewering", slot: tree, role: scales, target: enemy, text: "15% increased Impale Effect (3.25.0, cluster south of Duelist start)", source: "TreeData/3_29/tree.lua:61169 (node 6783); wiki Version 3.25.0 rev 1698361", pob: full}
  - {kind: notable, name: "Brutal Skewering", slot: tree, role: scales, target: enemy, text: "Impales you inflict last 1 additional Hit (ImpaleStacksMax +1; 3.25.0)", source: "TreeData/3_29/tree.lua:43388 (node 39904); Data/ModCache.lua:17110; wiki Version 3.25.0", pob: full}
  - {kind: notable, name: "Harpooner", slot: tree, role: applies, target: enemy, text: "20% chance to Impale with Two Handed Weapons; 30% increased Effect of Impales on Non-Impaled Enemies; 50% increased Impale Duration", source: "TreeData/3_29/tree.lua:23210-23212 (node 24858); Data/ModCache.lua:8257-8258,10246", pob: full}
  - {kind: notable, name: "Impale Chance (small passives) / Impale Mastery", slot: tree, role: applies, target: enemy, text: "10% chance to Impale with Attacks (node 13498); Impale Mastery options: 10% chance on Hit for all Impales to last 1 additional Hit, Impale Damage dealt ignores Enemy Physical Damage Reduction (3.25.0 replaced Overwhelm)", source: "TreeData/3_29/tree.lua:41825,23229-23271 (nodes 13498, 52074); Data/ModCache.lua:3595,17107", pob: partial}
  - {kind: keystone, name: "The Impaler", slot: tree, role: scales, target: enemy, text: "When your Hits Impale Enemies, also Impale other Enemies near them; Inflict 5 additional Impales on Enemies you Impale; for 5 s after they cannot be Impaled again and Impales cannot be Called (3.25.0: 5 additional, was 4)", source: "TreeData/3_29/tree.lua:40541-40545 (node 57257); wiki Version 3.25.0", pob: none}
  - {kind: notable, name: "Deliberate Brutality", slot: tree, role: scales, target: enemy, text: "Impales you inflict gain 50% increased Effect once 1 second of Duration has expired", source: "TreeData/3_29/tree.lua:54417 (node 56146); Data/ModCache.lua:17109", pob: none}
  - {kind: unique, name: "Woespike", slot: Ring, role: scales, target: enemy, text: "(10-20)% chance to Impale Enemies on Hit with Attacks; (20-30)% chance on Melee Hit for the Strongest Impale to last 1 additional Hit (3.28.0 value); 40-50% less Impale Duration (3.28.0)", source: "Data/Uniques/ring.lua:1809-1821; wiki Version 3.28.0 rev 1648325", pob: full, variant: "variant 2 (Current)"}
  - {kind: unique, name: "Entropic Devastation (Assassin's Mitts)", slot: Gloves, role: enables, target: enemy, text: "Critical Strikes with Spells inflict Impale; (30-50)% increased Effect of Impales inflicted with Spells; grants Call of Steel (EK seed)", source: "PoB Data/Uniques/gloves.lua:1141-1144; Modules/ModParser.lua:3904,582-585; vault Interactions/Spell impale", pob: full}
  - {kind: jewel, name: "Watcher's Eye (Pride)", slot: Jewel, role: scales, target: enemy, text: "Impales you inflict last 2 additional Hits while using Pride (EK seed)", source: "PoB Data/Uniques/Special/WatchersEye.lua:91-92; Modules/ModParser.lua:884; vault Interactions/Spell impale", pob: full, requires: ["Pride active"]}
  - {kind: unique, name: "Replica Heartbreaker", slot: Dagger, role: enables, target: enemy, text: "20% chance to Impale on Spell Hit; 20% inc Impale Effect", source: "PoB Data/Uniques/dagger.lua:195-196; Modules/ModParser.lua:581; vault Interactions/Spell impale", pob: full}
makes_redundant: []
conflicts:
  - {with: "Impale Support vs spells", effect: "the support needs an Attack skill; spell impale needs Entropic Devastation, Bladefall of Impaling or Replica Heartbreaker", source: "Data/Skills/sup_dex.lua:2472-2480; vault Interactions/Spell impale"}
  - {with: "The Impaler keystone", effect: "after it impales, the target cannot be Impaled again for 5 s and Impales cannot be Called from it; PoB reads none of it", source: "TreeData/3_29/tree.lua:40545; Data/ModCache.lua:17172"}
conditions:
  - {text: "wiki quote: \"The Impaled debuff records 10% of the physical damage of the hit that applies it. Each time the target is hit after that, by any source, the debuff deals that amount of reflected physical damage. Impale lasts for 5 hits by default, or 8 seconds.\" Introduced 3.5.0", source: "wiki Impale rev 1699530, Version history 3.5.0; PoB Data/Misc.lua:123-124, Modules/Data.lua:268"}
  - {text: "wiki quote: \"No impale damage is done on the first hit to enemies. The second hit deals 10% reflected damage, the third deals 20%, etc. This damage is capped at the total number of impales you land per hit multiplied by 10.\" (assumes 100% impale chance)", source: "wiki Impale rev 1699530 'Damage calculation'"}
  - {text: "wiki quote: \"Impale damage implicitly scales with the unmitigated physical damage of the hit that inflicts it.\" and \"Impale is mitigated normally when the debuff actually deals damage. It cannot be evaded, dodged, suppressed, or blocked, but it can be affected by mechanics such as damage taken as, avoidance, damage reduction, and modifiers to damage taken, including reflect-specific modifiers.\"", source: "wiki Impale rev 1699530; PoB Modules/CalcOffence.lua:5613-5622"}
  - {text: "the payout is a separate reflected hit: attacker offensive stats and Overwhelm-style penetration never apply; reducing the target's physical reduction needs Poacher's Mark, Crushed or the Impale Mastery ('ignores Enemy Physical Damage Reduction')", source: "wiki Impale rev 1699530; PoB Data/ModCache.lua:17107"}
  - {text: "impale needs physical damage in the hit (canDeal.Physical and an impale chance in effective mode)", source: "PoB Modules/CalcOffence.lua:4268,5597"}
uptime:
  Mapping:
    value: partial
    config: {multiplierImpalesOnEnemy: "blank = maximum stacks; pack members that die in k hits pay at most (k - 1) stacks, so the maximum is an upper bound"}
    reasoning: "PoB shows steady-state damage at the maximum stack count; a pack monster that dies in one or two hits gets no or one stack of payout (no damage on the first hit), so Mapping value is partial unless the hit rate on one pack is high or the build clears with several hits per monster"
    source: "Modules/CalcPerform.lua:3384-3391; wiki Impale rev 1699530 'Damage calculation'"
  Pinnacle Boss:
    value: pob
    config: {multiplierImpalesOnEnemy: "blank = maximum; valid when H x d >= N (about 0.625 hits/s on the boss for 5 hits / 8 s); below that use the stack model above"}
    reasoning: "a single boss takes every hit (all skills), so with a fast skill the impales are at the maximum within about N / (c x H) seconds (EK: 17.85 uses/s from the uptime notes); PoB already multiplies the payout by the impale chance, which equals c x N in steady state"
    source: "Modules/CalcOffence.lua:5601-5622; vault Interactions/Chance on hit uptime (V = 17.85/s for CoC EK + Cyclone)"
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Impale (rev 1699530, 2026-08-07)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.25.0 (rev 1698361): Savage/Brutal Skewering, The Impaler, Impale Mastery; Version_3.28.0 (rev 1648325): Woespike", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:1639-1642,3396,3503-3509,4268,5596-5636,6155-6175; Modules/CalcPerform.lua:3384-3391; Modules/CalcSetup.lua:49; Modules/Data.lua:268; Data/Misc.lua:123-124; Modules/ConfigOptions.lua:1648,1651; Data/ModCache.lua:3595,6284-6285,8257-8258,10246,17107-17110,17171-17173 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "vault/Interactions/Spell impale.md (EK providers) and vault/Interactions/Chance on hit uptime.md", kind: pob, patch: "3.29"}
not_verified:
  - "the steady-state stack formula S = c x min(N, H x d) is derived from the wiki mechanics by this note, not quoted; it assumes each hit applies at most one impale and every hit on the target consumes one hit of every active impale"
  - "CONFLICT between notes: vault Spell impale lists Deliberate Brutality as pob: full, but Data/ModCache.lua:17109 shows the node text unparsed (no mod); needs a PoB check on the EK build"
  - "Impale Mastery 'remove all Impales' line is mis-parsed as a flat 20% Damage mod in the cache (ModCache.lua:6285); effect on PoB numbers not measured"
  - "whether impale damage is crit-weighted in the stored hit as PoB does (CalcOffence.lua:3503-3509) or uses the non-crit hit; the wiki says 'the physical damage of the hit'"
  - "armour applying to the summed payout (PoB uses armourReductionF on stored x stacks) versus per stack; the wiki says each impale is added together when consumed"
  - "Call of Steel (hidden gem granted by Entropic Devastation) is not modelled by PoB (no Call of Steel code in CalcOffence / CalcPerform)"
  - "the 'Jewel' kind for Watcher's Eye and the exact lines of the EK providers are taken from the Spell impale note, not re-read here"
open_questions: []
```
