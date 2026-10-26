---
type: interaction
status: draft
pob_refs: [Kalandra's Touch, ItemCondition, TotalDPS, TotalEHP]
source: "PoB 2.67.2 Data/Uniques/ring.lua:1638-1642, Modules/CalcSetup.lua:1189-1226, Modules/ModStore.lua:699-712, Modules/ModParser.lua:1632-1633 and 3139, Data/ModCache.lua:19104; poewiki Kalandra's Touch rev 1627114; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Kalandra's Touch is a ring that reflects the opposite ring: PoB copies every mod of the other ring (implicits, enchantment, influence multipliers) except SocketedIn-tagged ones (CalcSetup.lua:1189-1226). On its own it is blank; the value is a second copy of the best ring, so the price follows that ring.
The effect is code, not a mod: the line "Reflects opposite Ring" is an unparsed leftover by design (ModCache.lua:19104; ModParser.lua:3139 "Display only"). The copied mods act at their usual pipeline steps.
PoB and the wiki disagree on one case: "if both Equipped Rings have X modifiers" masteries (see open questions).
Uniques are packages: every line is valued; the downside that is the point is that it is blank without a strong ring.

Pipeline: [[Damage calculation#Flat damage]] - no step of its own; the copied ring's mods act at their usual steps (here flat damage as an example); [[Defences#Resistance caps]] - copied resistances count to the cap

```interaction
id: unique-kalandras-touch
mechanic: "Unique package: a ring that reflects the opposite ring's mods (second copy of the best ring in the other ring slot)"
family: resource
pipeline_step: ["Damage calculation#Flat damage", "Defences#Resistance caps"]
pipeline_why: "the item has no mods of its own; the copied mods enter the same pools as the original ring's mods (flat damage, resistances, ...) at gear aggregation"
target: self
related: [damage-calculation, defences]
pob:
  measured: partial
  how: "Modules/CalcSetup.lua:1189-1226 copies every mod of the opposite ring (modList or slotModList) except SocketedIn-tagged ones, scaled by `scale`; adds the other ring's corrupted / influence multipliers (1206-1213) and the '<RingBase>Equipped' multiplier (1216-1218); own ExtraSkill implicits still apply (1223-1226). Modules/ModStore.lua:699-712 (ItemCondition) treats Kalandra's slot as the opposite ring; ModStore.lua:699-706 (bothSlots) replaces Kalandra with the other ring in BOTH slots, so 'both rings have X modifiers' (ModParser.lua:1632-1633) is TRUE in PoB. Wiki rev 1627114 says the mastery does not apply when Kalandra's reflects a ring with that modifier. Removal delta not measured (no headless run)."
  config: []
  unparsed: ["Kalandra's Touch: 'Reflects opposite Ring' -> Data/ModCache.lua:19104 {nil,'Reflects opposite Ring '} (leftover by design; effect coded in CalcSetup.lua:1189-1226)"]
model: null
providers:
  - {kind: unique, name: "Kalandra's Touch", variant: "no variants", slot: ring (slot 1 or 2), role: enables, target: self, text: "Reflects opposite Ring (cargo local_ring_duplicate_other_ring); the second line 'Mirrored' is a status line, not a provider", source: "Data/Uniques/ring.lua:1638-1642; Modules/CalcSetup.lua:1189-1226; Modules/ModParser.lua:3139; Data/ModCache.lua:19104", pob: partial}
package:
  seed: none
  slot: "Ring (slot 1 or 2)"
  base: "NOT VERIFIED (the evidence does not name the base; PoB lines Data/Uniques/ring.lua:1638-1642)"
  variant: "none"
  removal: "NOT MEASURED"
  downsides_that_are_the_point: ["blank on its own: needs a second strong ring; value = 2x the best ring and its price", "wiki rev 1627114: no benefit in both ring slots; does not reflect the extra ring slot of The Unseen Hand; no socket or gem copy; left / right-slot bonuses are not doubled"]
  foulborn: "none (no Kalandra entry in Data/ModFoulbornMap.jsonc)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level 60, req 1, release 3.19.0; added to the core drop pool in 3.20.0 (wiki rev 1627114); 2x Reflection of the Heart (divination card); 'technically cannot be chanced'; 3.26.0 copies the influence of the reflected ring; 3.27.0 wording 'opposite'; patch 3.29"
makes_redundant:
  - {provider: "a second best-in-slot ring", when: "the opposite ring is the one wanted twice", why: "the ring is copied", source: "Modules/CalcSetup.lua:1189-1226"}
conflicts:
  - {with: "slot-specific ring bonuses (e.g. Sibyl's Lament / Penumbra style)", effect: "left / right-slot bonuses are not doubled", source: "poewiki Kalandra's Touch rev 1627114"}
  - {with: "rings whose paired effects cancel each other (Snakepit / Shavronne's Revelation style)", effect: "chain and fork disabled when both are copied", source: "poewiki Kalandra's Touch rev 1627114"}
  - {with: "The Unseen Hand extra ring slot", effect: "cannot reflect it", source: "poewiki Kalandra's Touch rev 1627114"}
conditions:
  - {text: "needs another ring in the opposite slot; rarity is always unique; anointment is copied from the other ring, the item itself cannot be anointed", source: "poewiki Kalandra's Touch rev 1627114"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "inherits the copied ring's conditions; the copy itself is static", source: "Modules/CalcSetup.lua:1189-1226"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same as Mapping; inherits the copied ring's conditions", source: "Modules/CalcSetup.lua:1189-1226"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Kalandra%27s_Touch (rev 1627114)", kind: wiki, patch: "3.27"}
  - {ref: "PoB Data/Uniques/ring.lua, Modules/CalcSetup.lua, Modules/ModStore.lua, Modules/ModParser.lua, Data/ModCache.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: the mastery conflict below (no run, no game test)"
  - "NOT VERIFIED: whether `scale` in CalcSetup.lua:1202 equals 1 for rings (not run)"
  - "NOT VERIFIED: removal delta (no headless run); current availability of drop level 60 in early maps"
  - "No interaction note exists for ring copying; every ring provider note implicitly doubles under it (proposed: 'Kalandra's Touch (ring copy)'); no related id invented"
open_questions:
  - "CONFLICT PoB vs wiki: wiki efn says '20% increased maximum Energy Shield if both Equipped Rings have Evasion Modifiers' mastery does not apply when Kalandra's Touch reflects a ring with an evasion modifier (rev 1627114); PoB ModStore.lua:699-706 treats 'both rings have X modifiers' as true. PoB overstates for these masteries - which reading should the engine use? Needs a game test."
```
