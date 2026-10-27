---
type: interaction
status: draft
pob_refs: [ImpaleChance, ImpaleEffect, ImpaleStacksMax, multiplierImpalesOnEnemy, SkillTriggerRate, TotalDPS, FullDPS, SkillDPS, ManaUnreserved, TotalEHP]
source: "CoC EK Assa.xml item id 12 (gloves, PoB 2.67.2, game 3.29), headless removal and per-line probes (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md); PoB Data/ModCache.lua:14847, ModParser.lua:3904, Data/Vestigial.lua:1271-1273; poewiki Entropic Devastation rev 1647790"
last_confirmed_patch: "3.29.x"
---

Entropic Devastation is the only source of spell impale in the EK seed: every spell crit impales, with 41% increased Impale effect on top. That is 48.6% of FullDPS but 0% of the main skill's TotalDPS (Ethereal Knives hit damage does not read the impale), so the delta must be read from FullDPS, never from TotalDPS alone.
The gloves also hold four gems in their sockets (Enlighten, Flesh and Stone, Herald of Purity, Tempest Shield); Circle of Guilt needs that Herald of Purity (see [[Unique - Circle of Guilt]]). Grants Call of Steel is not in PoB.
A removal delta is a PoB number for one target at max impale stacks, not a game fact: PoB keeps the emptied slot's gems active.

Pipeline: [[Damage calculation#Ailments from hits]] - the impale is applied by a hit and its effect is read from the stored hits afterwards.

```interaction
id: unique-entropic-devastation
mechanic: "Unique package: Entropic Devastation makes every spell crit inflict Impale (with 41% increased Impale effect), the only spell impale source in the EK seed and 48.6% of its FullDPS, and holds four gems in its sockets"
family: ailment
target: enemy
pipeline_step: ["Damage calculation#Ailments from hits"]
pipeline_why: "Impale is applied on a crit hit (chance 100 with the Condition CriticalStrike) and its effect and stack count act on the stored hit damage afterwards, not on the hit"
related: [impale, spell-impale, heralds, coc-trigger, chance-on-hit-uptime, unique-circle-of-guilt]
pob:
  measured: partial
  how: "ImpaleChance BASE 100 [Condition CriticalStrike] flags=2 (spell) from ModCache.lua:14847 (ModParser.lua:3904); the 41% line is ImpaleEffect INC 41 (live parse). Seed (headless, in memory): whole removal FullDPS -48.558% (15,136,639 -> 7,786,547), main TotalDPS 0.000%; 'Full Impale DPS' 7,350,092 leaves output.SkillDPS (Ethereal Knives 7,722,462, Cyclone 62,519, Bleed 1,566 unchanged). Impale scaling in this build (multiplierImpalesOnEnemy, ConfigOptions.lua:1651, with Entropic present): 0 stacks 7.787M; 1: 8.651M; 2: 9.715M; 3: 10.79M; 4: 11.88M; 5: 12.96M; unset = ImpaleStacksMax 7: 15.137M (about +1.05M per stack). Grants Call of Steel is unparsed (ModCache.lua:16441 = nil), item.grantedSkills = 0"
  config:
    - {var: multiplierImpalesOnEnemy, default: false, ref: "Modules/ConfigOptions.lua:1651", class: b}
  unparsed:
    - "Entropic Devastation: Grants Call of Steel (ModCache.lua:16441, red; the skill is not in PoB)"
model: null
providers:
  - {kind: unique, name: "Entropic Devastation", variant: "no variants; Shaper Item; not Foulborn", slot: gloves, role: enables, target: enemy, text: "Critical Strikes with Spells inflict Impale", source: "Data/ModCache.lua:14847; ModParser.lua:3904; per-line removal FullDPS -48.558%, TotalDPS 0.000%", pob: full}
  - {kind: unique, name: "Entropic Devastation", variant: "no variants", slot: gloves, role: scales, target: enemy, text: "41% increased Effect of Impales inflicted with Spells", source: "live parse ImpaleEffect INC 41 (not in ModCache); per-line removal FullDPS -14.616% (12,924,214)", pob: full}
  - {kind: unique, name: "Entropic Devastation", variant: "corruption implicit", slot: gloves, role: scales, target: self, text: "+1 to Level of Socketed Gems (the 4 glove sockets)", source: "Data/ModCache.lua:182; per-line removal: FullDPS 0, Mana unreserved 107 -> 81", pob: full}
  - {kind: unique, name: "Entropic Devastation", variant: "no variants", slot: gloves, role: sustains, target: self, text: "111% increased Evasion and Energy Shield (local on the item)", source: "live parse EvasionAndEnergyShield INC 111; per-line removal: ES 5189 -> 5129, TotalEHP -1.9%", pob: full}
  - {kind: unique, name: "Entropic Devastation", variant: "no variants", slot: gloves, role: enables, target: self, text: "Grants Call of Steel", source: "Data/ModCache.lua:16441 (red); item.grantedSkills = 0; value unmeasured", pob: none}
package:
  seed: "CoC EK Assa.xml (PoB 2.67.2, game 3.29), item set 1"
  slot: Gloves
  base: "NOT VERIFIED (base Evasion 273 and ES 56 are in the evidence; the base name is not)"
  xml_item_id: 12
  variant: "none (no variants); Shaper Item; corrupted (+1 to Level of Socketed Gems); not Foulborn"
  removal: "FullDPS -48.558% (15,136,639 -> 7,786,547), main TotalDPS 0.000%, TotalEHP -3.0% - in-memory removal; PoB keeps the emptied slot's gems active, so the in-game loss is larger (4 gems)"
  lost_with_item:
    - "Spell impale: 'Full Impale DPS' 7,350,092 (48.6% of FullDPS)"
    - "Sockets W-G-W-B with Enlighten 3, Flesh and Stone 20, Herald of Purity 20, Tempest Shield 21 (group 3, slot Gloves): PoB keeps them active; in game Herald of Purity (which Circle of Guilt needs) and the reservation efficiency would have to move to other sockets"
    - "ES 5189 -> 5073, Evasion 14082 -> 13372, Mana unreserved 107 -> 81; conditions UniqueItemInGloves / UsingGloves; ShaperItem count 2 -> 1"
  downsides_that_are_the_point: []
  foulborn: "none: no Entropic key in Data/ModFoulbornMap.jsonc, no Foulborn text in wiki rev 1647790. Lead, not Foulborn: Data/Vestigial.lua:1271-1273 DivergentSpellImpaleOnCritChanceUnique__1 'Critical Strikes with Spells have 50% chance to inflict Impale' (ModItemExclusive.lua:8645) is selectable as a vestigial implicit on gloves only (AddImplicitPopup.lua:127): 50% instead of 100% on an alternative glove. Acquisition NOT VERIFIED"
  obtainability: "poewiki Entropic Devastation rev 1647790 (patch 3.29): introduced 3.20.0, is_drop_restricted, drops from Uber Shaper; 3.21.0 fixed the Shaper influence (a legacy copy without influence exists); the seed is the current text (Shaper Item). The seed copy is corrupted (+1 socketed gems), so trade-only as a corrupted copy; rolls 111% evasion and ES and 41% impale effect are within the (100-150)% and (30-50)% ranges. Boss-kill cost to farm: not assessed"
makes_redundant: []
conflicts:
  - {with: "Impale Support", effect: "needs an Attack skill, so it cannot replace this item on Ethereal Knives (a spell)", source: "Spell impale note"}
conditions:
  - {text: "Watcher's Eye Pride adds +2 impale hits to the stack count (ImpaleStacksMax 7 in this build)", source: "ImpaleStacksMax 7 (item-analyst-ek.md); aura-conditional-uniques note"}
  - {text: "Per-hit rate (PoB fields): SkillTriggerRate 8.93/s x HitChance 100% x CritChance 100% = 8.93 impaling spell crits/s on one target (m = 1 per trigger by the vault shotgun rule; projectiles per trigger NOT counted)", source: "item-analyst-ek.md; Chance on hit uptime note"}
uptime:
  Mapping:       {value: pob, config: {multiplierImpalesOnEnemy: "unset = max stacks"}, reasoning: "PoB assumes max impale stacks on every enemy; the per-enemy hit rate in maps is unmodelled (assumption as in the vault Chance on hit uptime EK row). Value when up: 15.137M vs 7.787M at 0 stacks (+94%)", source: "ConfigOptions.lua:1651; item-analyst-ek.md"}
  Pinnacle Boss: {value: high, config: {multiplierImpalesOnEnemy: "unset = max stacks"}, reasoning: "one target: 7 stacks need 7 hits = 0.8 s at 8.93 hits/s, then each hit adds one and consumes one, about 100% at max stacks; duration 8 s base or 7 hits (Impale and Spell impale notes). PoB's assumption of 100% is correct for the boss", source: "item-analyst-ek.md"}
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Entropic_Devastation (rev 1647790)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/ModCache.lua:14847 and 16441, Modules/ModParser.lua:3904, Data/Vestigial.lua:1271-1273", kind: pob, patch: "3.29"}
  - {ref: "headless probes on CoC EK Assa.xml, PoB 2.67.2 (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: Call of Steel value (not modelled in PoB)"
  - "NOT VERIFIED: per-enemy impale uptime in maps"
  - "NOT VERIFIED: how a player gets the vestigial 50%-on-crit spell impale implicit"
  - "NOT VERIFIED: the gloves base name; boss-kill cost to farm"
open_questions:
  - "Should a gloves swap that drops spell impale be rejected outright for a seed with Ethereal Knives, or priced as a loss of 48.6% FullDPS and re-socketing Herald of Purity?"
```
