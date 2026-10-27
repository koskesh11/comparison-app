---
type: interaction
status: draft
pob_refs: [CritChanceLucky, CritLucky, LuckyHits, UnluckyHits, Unexciting, ExtremeLuck, BifurcateCrit, CritChance, PreEffectiveCritChance, PreBifurcateCritChance, AccuracyHitChance, CritChanceCap, LowLife, Focused]
source: "wiki Luck rev 1660583, Critical strike rev 1698799, Accuracy rev 1612031; PoB 2.67.2 CalcOffence.lua, CalcTriggers.lua, ModParser.lua, ConfigOptions.lua, Data/ModCache.lua, Data/ModMaster.lua, TreeData/3_29/tree.lua, Data/TimelessJewelData/LegionPassives.lua, Data/TattooPassives.lua, Data/Uniques; mechanics-researcher-damage-calc.md, pob-coverage-auditor-calc-order.md, tree-ascendancy-analyst.md (task 027)"
last_confirmed_patch: "3.29.x"
---

A lucky critical strike chance rolls the crit check twice and keeps the better result, so a crit chance p becomes 2p - p^2 (40% becomes 64%, wiki example); the gain is a 100% more multiplier at p near 0 and falls to 0% at p = 100%. PoB computes this only in effective mode (against the enemy), as 1 - (1-p)^2 after the crit chance cap and before the hit-chance multiplication, and uses the lucky chance for Cast on Critical Strike triggers through the source skill's CritChance. The same sources often carry a price (Calculated Risk makes your hits unlucky), which PoB also computes, except the incoming-damage lines.

Pipeline: [[Damage calculation#Critical strike]] - luck changes the crit chance before the crit multiplier is applied to the hit; the damage-luck variants (crit damage is lucky) act in [[Damage calculation#Damage roll]].

```interaction
id: lucky-critical-strikes
mechanic: "Your Critical Strike Chance is Lucky: the crit roll is made twice and the better kept, p -> 2p - p^2 (wiki Luck rev 1660583); PoB applies it only in effective mode as 1-(1-p)^2 (Unexciting: 3p^2-2p^3, three rolls: 1-(1-p)^3), then multiplies by attack hit chance"
family: buff
target: self
related: [coc-trigger, power-charges, chance-on-hit-uptime]
pipeline_step: ["Damage calculation#Critical strike", "Damage calculation#Damage roll"]
pipeline_why: "Luck acts on the crit chance roll (Critical strike step, wiki Critical strike rev 1698799: 'Sources of luck ... for critical strike chance will perform multiple rolls and keep one of the outcomes'); 'Damage with Critical Strikes is Lucky' re-rolls the damage range instead and belongs to the Damage roll step"
pob:
  measured: partial
  how: "CalcOffence.lua:3107-3130: CritChance = (base+additional) x inc x more, capped by CritChanceCap (default 100) at 3109, then in effective mode only (3117 'env.mode_effective and Flag CritChanceLucky') critRolls = 1, doubled by ExtremeLuck (3120-3122), and CritChance = 1-(1-p)^(rolls+1) (3128) or with Unexciting 3p^2-2p^3 (3124-3126); then Bifurcate (3133-3135, applied after luck, matching the wiki 'Luck will apply individually to each of the two rolls'), Every3/5UseCrit (3139-3144) and x AccuracyHitChance/100 (3146; attacks only, spells have AccuracyHitChance 100, 2230-2231, matching wiki Accuracy rev 1612031 'This does not affect critical strikes by spells'). Cast on Critical Strike reads the source skill's cached CritChance (CalcTriggers.lua:761-781), so lucky crit raises the trigger chance. 'Damage with Critical Strikes is Lucky' sets CritLucky (CalcOffence.lua:3454; ModParser.lua:3568) and 'Damage with Hits is Unlucky' sets UnluckyHits (ModCache.lua:15023). Not modelled: 'Damage of Enemies Hitting you is Unlucky' (ModCache.lua:15004 nil) and 'Enemies' Damage with Critical Strikes against you is Lucky' (ModCache.lua:15426 nil); no Unlucky flag exists for crit chance (grep of ModParser/CalcOffence)"
  config:
    - {var: conditionLowLife, default: false, ref: "Modules/ConfigOptions.lua:177", class: b}
    - {var: conditionFocused, default: false, ref: "Modules/ConfigOptions.lua:1003", class: b}
  unparsed:
    - "Calculated Risk: 'Damage of Enemies Hitting you is Unlucky' (ModCache.lua:15004 returns nil)"
    - "Dance with Death keystone: 'Enemies' Damage with Critical Strikes against you is Lucky' (ModCache.lua:15426 returns nil)"
model: null
providers:
  - {kind: ascendancy, name: "Calculated Risk 14103 (Saboteur)", slot: tree, role: enables, target: self, text: "Your Critical Strike Chance is Lucky; Damage of Enemies Hitting you is Unlucky; Damage with Hits is Unlucky (trade-off node: unlucky hits average (2 x min + max)/3 instead of (min + max)/2)", source: "TreeData/3_29/tree.lua:84646-84660; ModCache.lua:23015, 15023; Modules/CalcOffence.lua:3464-3486", pob: partial}
  - {kind: jewel, name: "Brutal Restraint (Asenath variant: Dance with Death keystone)", slot: jewel, role: enables, target: self, text: "Dance with Death: Can't use Helmets; Your Critical Strike Chance is Lucky; Your Damage with Critical Strikes is Lucky; Enemies' Damage with Critical Strikes against you is Lucky (timeless jewel, Maraketh, limited to 1)", source: "Data/Uniques/jewel.lua:1827-1833; Data/TimelessJewelData/LegionPassives.lua:10945-10971; ModCache.lua:14527, 23015, 23027", pob: partial, variant: "Asenath (Dance with Death)"}
  - {kind: unique, name: "Relic of the Pact", slot: wand, role: enables, target: self, text: "Your Critical Strike Chance is Lucky while on Low Life; Grants Level 1 Blood Sacrament Skill (Ultimatum unique)", source: "Data/Uniques/wand.lua:293-305; ModCache.lua:23017; ModParser.lua:3561", pob: config}
  - {kind: unique, name: "Hyperboreus", slot: belt, role: enables, target: self, text: "crafted option: Your Critical Strike Chance is Lucky while Focused (variants 10 and 19); Chill nearby Enemies when you Focus", source: "Data/Uniques/belt.lua:409-458 (line 449); ModCache.lua:23016; ModParser.lua:3562", pob: config, variant: "Lucky Crit Chance while Focused (Current)"}
  - {kind: mod, name: "veiled belt suffix 'of Craft' (LuckyCriticalsDuringFocus)", slot: belt, role: enables, target: self, text: "Your Critical Strike Chance is Lucky while Focused (unveiled belt suffix, level 72)", source: "Data/ModMaster.lua:580; ModCache.lua:23016", pob: config}
  - {kind: runegraft, name: "Runegraft of Stability", slot: tree, role: blocks, target: self, text: "Your Lucky or Unlucky effects are instead Unexciting (median of three rolls: 3p^2 - 2p^3, which is below the plain chance p under 50% and above it over 50%; limited to 1)", source: "Data/TattooPassives.lua:2418-2430; Modules/ModParser.lua:4080; CalcOffence.lua:3124-3126; wiki Luck rev 1660583", pob: full}
  - {kind: unique, name: "Azadi Crest", slot: shield, role: scales, target: self, text: "Your Lucky or Unlucky effects use the best or worst from three rolls instead of two (crit chance 1-(1-p)^3)", source: "Data/Uniques/shield.lua:1290-1301; ModParser.lua:4147; CalcOffence.lua:3120-3122", pob: full}
makes_redundant:
  - {provider: "more increased Critical Strike Chance", when: "the lucky chance already approaches 100% (p near 1)", why: "the lucky gain is (2 - p) times the chance and vanishes at p = 100%, and PoB caps the base chance at CritChanceCap 100 before rolling", source: "wiki Luck rev 1660583 (Effectiveness); CalcOffence.lua:3109, 3128"}
conflicts:
  - {with: "Runegraft of Stability", effect: "replaces lucky by unexciting: crit chance 3p^2 - 2p^3 (at p = 30% that is 21.6% vs 51% lucky); wiki: Unexciting cancels both lucky and unlucky", source: "Data/TattooPassives.lua:2429; wiki Luck rev 1660583: 'Sources of Unexciting modifiers usually cancel out both Lucky and Unlucky modifiers.'"}
  - {with: "Calculated Risk (own downside)", effect: "Damage with Hits is Unlucky lowers the average hit; lucky crit chance does not touch the damage roll ('These stats do not affect other mechanics like chance to hit/accuracy or critical strike chance')", source: "TreeData/3_29/tree.lua:84655; wiki Luck rev 1660583"}
  - {with: "Lucky and Unlucky on the same stat", effect: "cancel each other out", source: "wiki Luck rev 1660583: 'Lucky and Unlucky modifiers affecting the same stat or mechanic will cancel each other out.'"}
conditions:
  - {text: "lucky crit chance = 2p - p^2 (p = crit chance before luck); the wiki's own example: 40% -> 64%; computed with the same formula and rounded down: 12% -> 22%, 30% -> 51%, 55% -> 79%, 75% -> 93%", source: "wiki Luck rev 1660583 (no version history section): 'CritChance_{Lucky} = 2 x CritChance_{Default} - CritChance_{Default}^2' and 'It should be noted that these calculations neglect the effect of accuracy on critical strikes.'"}
  - {text: "relative size: with percentage rolls lucky is up to a 100% more modifier, falling linearly towards 0% as the chance rises (gain factor 2 - p)", source: "wiki Luck rev 1660583 (Effectiveness): 'lucky/unlucky rolls will be up to a 100% more/less modifier, changing linearly towards 0% as critical chance increases'"}
  - {text: "attacks: accuracy is checked a second time for the crit, and a failed check turns the crit into a regular hit; spells skip this check", source: "wiki Accuracy rev 1612031: 'accuracy is checked a second time when attack hits attempt to deal a critical strike. Failing this accuracy check will cause a hit with sufficient critical strike chance to become a regular hit. This does not affect critical strikes by spells.' (PoB CalcOffence.lua:3146, 2230-2231 agrees)"}
  - {text: "bifurcated critical strikes make two crit rolls and luck applies to each roll", source: "wiki Critical strike rev 1698799: 'Luck will apply individually to each of the two rolls.'; PoB CalcOffence.lua:3128-3135"}
  - {text: "PoB shows the lucky chance only in effective mode (against an enemy); the plain CritChance of the non-effective view has no luck", source: "Modules/CalcOffence.lua:3117"}
  - {text: "Cast on Critical Strike triggers read the source skill's CritChance, so lucky crit chance also raises the trigger chance in PoB", source: "Modules/CalcTriggers.lua:761-781"}
uptime:
  Mapping:       {value: always, config: {conditionLowLife: "true only for Relic of the Pact if the build is on Low Life", conditionFocused: "true only for the Hyperboreus / veiled belt option if Focus is up"}, reasoning: "Calculated Risk and Dance with Death have no condition, so PoB's lucky chance applies at all times (effective mode); the Low Life and Focused providers are conditional (config class b) and their uptime is not derivable here", source: "TreeData/3_29/tree.lua:84653; LegionPassives.lua:10968; ModParser.lua:3560-3562"}
  Pinnacle Boss: {value: always, config: {conditionLowLife: "as in Mapping", conditionFocused: "as in Mapping"}, reasoning: "unconditional providers are independent of the target; PoB multiplies by attack hit chance against the boss's evasion (spells: 100%), so the effective gain shrinks for attacks that miss", source: "Modules/CalcOffence.lua:2230-2234, 3146"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Luck (rev 1660583)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Critical_strike (rev 1698799)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Accuracy (rev 1612031)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:2230-2234, 3107-3146, 3452-3486, CalcTriggers.lua:761-781, ModParser.lua:3560-3568, 4080, 4147, ConfigOptions.lua:177, 1003", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/ModCache.lua:14527, 15004, 15023, 15426, 23015-23027, 23074, 23076; TreeData/3_29/tree.lua:84646; Data/TimelessJewelData/LegionPassives.lua:10945; Data/TattooPassives.lua:2418; Data/Uniques/{wand,belt,shield,jewel}.lua; Data/ModMaster.lua:580", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/mechanics-researcher-damage-calc.md (D8, D9), tree-ascendancy-analyst.md line 120", kind: discovery, patch: "3.29"}
not_verified:
  - "the wiki Luck page has no version history section, so no patch date for the lucky crit rules; the formula is as of rev 1660583 (2026-07-07)"
  - "wiki formula text says the calculation neglects accuracy; PoB multiplies the lucky chance by AccuracyHitChance for attacks: wiki Accuracy confirms the second check, but whether the lucky re-roll happens before or after that check is not stated (PoB: luck first, then accuracy)"
  - "Calculated Risk wording on the live wiki/passive list (the 3.29 tree data is the only source read)"
  - "the 3_28_alternate tree (alternate ascendancies) also contains 'Your Critical Strike Chance is Lucky' nodes (tree.lua:13741, 40062); the main 3_29 tree has only Calculated Risk (grep)"
  - "Focus cooldown and uptime for the Focused providers; Low Life threshold: 50% since 3.14.0, PoB Data.lua:240 / CalcPerform.lua:570 (see [[Pain Attunement]]); the old 35% value is outdated"
  - "obtainability of Relic of the Pact, Hyperboreus, the veiled belt suffix and the Brutal Restraint Asenath seed (not checked)"
  - "whether 'Enemies' Damage with Critical Strikes against you is Lucky' matters for EHP (PoB does not parse it)"
open_questions:
  - "Is Calculated Risk (lucky crit chance, unlucky hits and unlucky enemy hits) acceptable as a generator pick, or is it a lopsided trade the user wants rejected? (PoB can show both sides except the enemy-unlucky line)"
```
