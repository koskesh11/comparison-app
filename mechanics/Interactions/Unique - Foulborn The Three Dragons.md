---
type: interaction
status: draft
pob_refs: [ColdCanIgnite, ColdCannotFreeze, ColdCannotChill, ChaosCanShock, ChaosCanFreeze, ShockDuration, ShockEffectMod, FreezeDurationMod, ShockChanceOnCrit, FullDPS, conditionEnemyShocked, conditionShockEffect]
source: "task 027 batch 2c item-analyst-fr.md (seed AutoBuilder/FR CoC Occu Three Dragons v4.xml, item id 10, PoB 2.67.2, game 3.29); PoB Data/Uniques/helmet.lua:1665-1671, ModFoulbornMap.jsonc:346-348, ModFoulborn.lua:121-123, ModCache.lua:23005-23012, ModParser.lua:3670-3672, CalcOffence.lua:4315-4329, ConfigOptions.lua:1943-1947; poewiki The Three Dragons rev 1675049, Foulborn unique item rev 1702126"
last_confirmed_patch: "3.29.x"
---

Package note for the Foulborn The Three Dragons helmet in the FR v4 seed. Forbidden Rite deals only chaos damage (Void Manipulation removes the elemental part), so the two mutated lines (chaos can Freeze, chaos can Shock) are the only ones that feed an ailment; the +30% resistances and the original cold line are idle here. Gap note (patterns for the audit, not duplicated): [[Foulborn The Three Dragons]]; shock size: [[Own shock effect]] (model).
Trap 1: a helmet-only removal in PoB reads -0.76% FullDPS and understates the loss, because PoB keeps the emptied slot's socket group (4 curse gems) active; with that group disabled it reads -27.07%. Trap 2: ShockChance stays 100 without the line, only ShockDuration / ShockEffectMod / FreezeDurationMod vanish. Trap 3: the shock config (+14.37%) is valid only while the chaos-shock line is present.

Pipeline: [[Damage calculation#Ailments from hits]] - the two Foulborn lines decide which damage types may inflict shock and freeze; the shock magnitude then acts as damage taken ([[Damage calculation#Damage taken]]).

```interaction
id: unique-foulborn-three-dragons
mechanic: "Unique package: Foulborn The Three Dragons lets the chaos-only Forbidden Rite hits Shock and Freeze (the item is the only ailment source of the build) and adds +30% resistances; the cold line is a drawback that costs nothing while no cold damage is dealt"
family: ailment
target: enemy
pipeline_step: ["Damage calculation#Ailments from hits", "Damage calculation#Damage taken"]
pipeline_why: "the Foulborn lines are damage-type-can-ailment flags (which hit types may inflict the ailment); the shock they enable raises damage taken by the enemy"
related: [damage-type-can-ailment, shock, freeze, chill, ignite, enemy-ailment-threshold, elemental-overload, curse-application]
pob:
  measured: partial
  how: "Flags parsed (ModCache.lua:23005 ChaosCanFreeze, 23007 ChaosCanShock, 23012 ColdCanIgnite + ColdCannotFreeze + ColdCannotChill, ModParser.lua:3671). CalcOffence.lua:4315-4329 calcAverageSourceDamage: a damage type counts for an ailment if it is the ailment's own type (and not <Type>Cannot<Ailment>) or has <Type>Can<Ailment>. PoB counts shock in DPS only via the config pair below (default off); freeze has no DPS value. Headless removals in memory on the seed: helmet slot emptied = FullDPS 57,001,026 -> 56,567,803 (-0.76%, helmet ES -164 only); helmet emptied AND its socket group (group 6: Punishment 21, Despair 20, Temporal Chains 21, Enfeeble 21, B-B-B-G) disabled = 41,569,877 (-27.07%), Cyclone -25.85%, curses applied Assassin's Mark only (was 5). Per line: removing line 1, 2, 3 or 4 alone = 0.00% FullDPS; line 3 removed drops FR FreezeDurationMod; line 4 removed drops FR ShockDuration 2.667 s and ShockEffectMod; plain Three Dragons (fire shock, cold ignite, lightning freeze) = 0.00% but the FR shock/freeze outputs are absent. Shock config on (conditionEnemyShocked + conditionShockEffect 26): FullDPS 57,001,026 -> 65,190,713 (+14.37%), FR 56,834,383 -> 64,998,438, Cyclone 166,643 -> 192,275; the same +14.37% appears with line 4 removed, so the config does not read the item. A headless removal delta is not a game fact: it is PoB's single-enemy model with the config unticked."
  config:
    - {var: conditionEnemyShocked, default: false, ref: "Modules/ConfigOptions.lua:1943", class: b}
    - {var: conditionShockEffect, default: 0, ref: "Modules/ConfigOptions.lua:1947", class: b}
  unparsed: []
model: null
package:
  seed: "AutoBuilder/FR CoC Occu Three Dragons v4.xml"
  slot: Helmet
  base: "Golden Mask (B-B-B-G, Evasion 124, ES 26, quality 20)"
  xml_item_id: 10
  variant: "none (Data/Uniques/helmet.lua:1665-1671 has no Variant lines; the selected item is the XML text, two {mutated} lines, Implicits: 0)"
  removal: "FullDPS -0.76% with the helmet emptied (ES 17,116 -> 16,952, Evasion 336 -> 36, EHP 273,342 -> 270,720), -27.07% with its 4-socket curse group also disabled - in-memory removal; PoB keeps the emptied slot's gems active, so the in-game loss is larger"
  lost_with_item:
    - "socket group 6 (4 helmet sockets): Punishment 21, Despair 20, Temporal Chains 21, Enfeeble 21 - the -27.07% row, unless the four curses move to other sockets"
    - "ES -164 (FR adds 20% of max ES as chaos damage: ChaosHitAverage 191,718 -> 190,256 = the -0.76%)"
    - "Evasion -300, EHP 273,342 -> 270,720"
    - "FR ShockDuration / ShockEffectMod / FreezeDurationMod outputs"
    - "conditions UsingHelmet, UniqueItemInHelmet"
  downsides_that_are_the_point:
    - "Your Cold Damage can Ignite but not Freeze or Chill (original Three Dragons drawback, kept): costs 0.00% here because the build deals no cold damage (Void Manipulation); nothing in the build reads chilled / frozen enemies"
  foulborn: "two mutated lines: Lightning-freeze line replaced by 'Your Chaos Damage can Freeze' (ModFoulbornMap.jsonc:346 -> ModFoulborn.lua:123), Fire-shock line replaced by 'Your Chaos Damage can Shock' (jsonc:348 -> ModFoulborn.lua:121); pairing is fixed per original line (wiki Foulborn unique item rev 1702126); the Cold line is the only original line left (a third option 'Your Chaos Damage can Ignite' at jsonc:347 was not taken). PoB reads Data/ModFoulbornMap.jsonc (Modules/Data.lua:1480), not ModFoulbornMap.lua"
  obtainability: "base unique: drop_enabled 1, is_drop_restricted 0, release 1.1.1, drop level 35 (wiki The Three Dragons rev 1675049, 3.29.x). Foulborn: from a Foulborn variant of the unique via Ancient Wombgift at the Genesis Tree or Grasping Coffers (Hive Fortress / Colony) (wiki Foulborn unique item rev 1702126, 3.29.x). TWO mutated lines need the multi-Foulborn outcome; no Ancient Orb path; the 3-to-1 recipe no longer re-rolls a Foulborn since 3.27.0c. NOT VERIFIED: Genesis Tree availability in the running league, price, drop weight of the double mutation"
providers:
  - {kind: unique, name: "The Three Dragons", slot: Helmet, role: sustains, target: self, text: "+30% to all Elemental Resistances (global, no local_ prefix; ElementalResist BASE 30)", source: "Data/Uniques/helmet.lua:1668; Data/ModCache.lua:1794", pob: full}
  - {kind: unique, name: "The Three Dragons", slot: Helmet, role: blocks, target: enemy, text: "Your Cold Damage can Ignite but not Freeze or Chill (original line, not mutated; ColdCanIgnite + ColdCannotFreeze + ColdCannotChill)", source: "Data/Uniques/helmet.lua:1670; Data/ModCache.lua:23012; Modules/ModParser.lua:3671", pob: full}
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Freeze (ChaosCanFreeze; FR FreezeChanceOnCrit 100, crowd control only, bosses keep the 50% action-speed floor)", source: "Data/ModFoulbornMap.jsonc:346; Data/ModFoulborn.lua:123; Data/Uniques/helmet.lua:1671; Data/ModCache.lua:23005", pob: partial, variant: "Your Lightning Damage can Freeze but not Shock"}
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Shock (ChaosCanShock; the point of the item: FR ShockDuration 2.667 s, 7.524 triggers/s, +14.37% FullDPS with the shock config at effect 26)", source: "Data/ModFoulbornMap.jsonc:348; Data/ModFoulborn.lua:121; Data/Uniques/helmet.lua:1669; Data/ModCache.lua:23007; Modules/ConfigOptions.lua:1943-1947", pob: config, variant: "Your Fire Damage can Shock but not Ignite"}
makes_redundant:
  - {provider: "+30% to all Elemental Resistances (line 1)", when: "the other gear already caps resistances", why: "with -30% the overcaps stay Fire 41, Cold 49, Lightning 79 (were 71 / 79 / 109), no PoB output changes (0.00% FullDPS)", source: "item-analyst-fr.md (H_minus_res row); seed measured"}
  - {provider: "Your Cold Damage can Ignite but not Freeze or Chill", when: "the build deals no cold damage (Void Manipulation on Forbidden Rite)", why: "flags drop, no output changes; cond scan found no vs-chilled / vs-frozen payoff in the player or enemy modDB", source: "item-analyst-fr.md (cond_scan.json)"}
conflicts:
  - {with: "Elemental Focus (support) / Secrets of Suffering", effect: "remove the ailment the lines enable (ShockChanceOnCrit and FreezeChanceOnCrit 100 -> 0 with Secrets of Suffering, FR DPS identical) - see damage-type-can-ailment", source: "vault Gaps/Foulborn The Three Dragons.md (headless 2026-10-21); item-analyst-fr.md"}
  - {with: "Void Manipulation (support)", effect: "removes elemental damage so cold / fire / lightning lines of the item are idle; also makes PoB skip the ignite block, so the Foulborn chaos-ignite option would show no change", source: "Data/Skills/sup_dex.lua:4578; Modules/CalcOffence.lua:4991 (per the gap note, not re-measured)"}
conditions:
  - {text: "Shock value needs the enemy shocked: PoB sets nothing by itself, conditionEnemyShocked (check) + conditionShockEffect (count) must be set by the scenario; valid only while the chaos-shock line is present", source: "Modules/ConfigOptions.lua:1943-1947"}
  - {text: "FR ShockChance / FreezeChance stay 100 with the lines removed (crits always try); read ShockDuration / ShockEffectMod / FreezeDurationMod, not the chance field, to see whether the ailment can land", source: "item-analyst-fr.md per-line deltas"}
  - {text: "Chaos damage counts toward shock / freeze only with the ChaosCan* flags (Forbidden Rite deals chaos damage based on energy shield)", source: "Modules/CalcOffence.lua:4315-4329; Data/Skills/act_int.lua:7536"}
uptime:
  Mapping:       {value: high, config: {conditionEnemyShocked: true, conditionShockEffect: "model: Own shock effect"}, reasoning: "crit chance 100%, ShockDuration 2.667 s, CoC trigger 7.524/s -> shock up about 100% of the time (vault model); freeze: chance 100 on crit, value is crowd control on maps, not measurable in PoB", source: "item-analyst-fr.md; vault Models/Own shock effect.md"}
  Pinnacle Boss: {value: high, config: {conditionEnemyShocked: true, conditionShockEffect: 26}, reasoning: "same uptime; magnitude is boss-threshold dependent: 26% Pinnacle (vault model figure, FullDPS 57.00M -> 65.19M re-run), 24% standard boss, capped 50% on no-boss (model note, not re-run); freeze not assumed (50% action-speed floor)", source: "item-analyst-fr.md; vault Models/Own shock effect.md; vault Interactions/Freeze.md"}
seeds: [FR]
sources:
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-fr.md (Foulborn The Three Dragons section)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/The_Three_Dragons (rev 1675049)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Foulborn_unique_item (rev 1702126)", kind: wiki, patch: "3.29"}
not_verified:
  - "In-game behaviour of chaos shock / freeze from Forbidden Rite (vault gap note: user to test)"
  - "Shock effect 26% for Pinnacle taken from the vault model; only the FullDPS result at 26 was re-run"
  - "Chaos ignite effect (Foulborn option not taken) inferred from the gap note, not re-measured"
  - "Genesis Tree availability, price and double-mutation odds"
open_questions:
  - "Should the generator treat the two Foulborn chaos lines as the reason to keep this helmet (only ailment source for a chaos-only build), and carry the 4-socket curse group to another slot if the helmet is swapped?"
```
