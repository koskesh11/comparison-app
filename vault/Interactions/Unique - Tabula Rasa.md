---
type: interaction
status: draft
pob_refs: [socketCount, linkedGems, EnergyShield, Armour, Evasion, TotalEHP]
source: "PoB 2.67.2 Data/Uniques/body.lua:722-724, Data/Bases/body.lua:411-414, Classes/Item.lua:2613-2616, Modules/ModStore.lua:781-785; poewiki Tabula Rasa rev 1698806; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Tabula Rasa is a Simple Robe with 6 linked white sockets, no attribute requirements and no defence of any kind (PoB zeroes the base energy shield by a hack in Item.lua). For a build it is the cheapest 6-link: any gem colour fits, no Fusing or Chromatic crafting, at the price of the whole body-armour defence layer.
PoB counts links but never checks socket colour, so the item adds nothing to PoB's numbers against any other 6L body armour; its value is the freed gear slot and the early 6L. The cost shows in EHP (not measured). A generator needs a link-count rule, not a PoB delta.
Uniques are packages: every line is valued, including the downside that is the point (no defence).

Pipeline: [[Damage calculation#More and less]] - 6 links decide how many supports apply to the skill; [[Receiving damage#Energy shield]] - the armour contributes no ES / armour / evasion

```interaction
id: unique-tabula-rasa
mechanic: "Unique package: a 6-linked white-socket body armour with zero defence - the cheapest 6L at the cost of all body-armour defence"
family: resource
pipeline_step: ["Damage calculation#More and less", "Receiving damage#Energy shield"]
pipeline_why: "six links let six supports apply to the main skill (their more / less multipliers); the base defence values are zero by design, so the item adds nothing in Receiving damage"
target: self
related: [energy-shield-hybrid, damage-calculation, receiving-damage]
pob:
  measured: partial
  how: "Links: the data line 'Sockets: W-W-W-W-W-W' (Data/Uniques/body.lua:722-724, hyphen = linked) is read as 6 linked sockets. Zero defence: PoB hack Classes/Item.lua:2613-2616 sets ArmourData EnergyShield 0 and requirements.int 0 for Tabula Rasa (base Simple Robe, Data/Bases/body.lua:411-414), so the EHP loss shows in output. Socket colour is not checked anywhere in the link logic (only GemProperty tags ModStore.lua:781-785 and SocketAlwaysMatches Item.lua:2688 read it), so the item gives nothing in PoB over any other 6L body armour. Removal delta not measured (no headless run)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Tabula Rasa", variant: "no variants", slot: body armour, role: blocks, target: self, text: "Has no Attribute Requirements or Energy Shield (hidden wiki mod RemoveStatsFromTabulaRasa, cargo local_unique_tabula_rasa_no_requirement_or_energy_shield)", source: "Classes/Item.lua:2613-2616 (hack); poewiki Tabula Rasa rev 1698806", pob: full}
  - {kind: unique, name: "Tabula Rasa", variant: "no variants", slot: body armour, role: enables, target: self, text: "Has 6 Linked White Sockets (hidden wiki mod ItemHasSixLinkedWhiteSocketsUniqueBodyInt6, cargo local_six_linked_white_sockets)", source: "Data/Uniques/body.lua:722-724", pob: full}
package:
  seed: none
  slot: "Body Armour"
  base: "Simple Robe (socketLimit 6)"
  variant: "none"
  removal: "NOT MEASURED"
  downsides_that_are_the_point: ["no defence at all: no ES / armour / evasion, not even base values (wiki rev 1698806; Mark_GGG quote 'offers offensive power ... at the cost of defenses')"]
  foulborn: "none (no Tabula entry in Data/ModFoulbornMap.jsonc, grep returned nothing)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level 3, release 0.10.5; poewiki rev 1698806; recipes 9 Humility, 9 Vanity (corrupted), 3 Sambodhi's Wisdom (two-implicit corrupted); vendor 20 Orb of Fusing (3.19.0 note); patch 3.29"
makes_redundant:
  - {provider: "Chromatic Orb socket colouring, Orb of Fusing 6-link crafting, Jeweller's Orb", when: "Tabula Rasa is worn", why: "the item already has 6 linked sockets of any gem colour", source: "poewiki Tabula Rasa rev 1698806"}
conflicts:
  - {with: "any other body armour (unique body mods, e.g. Kaom's Heart)", effect: "occupies the body slot and brings no defence", source: "b2c-item-analyst-leaguestart.md"}
  - {with: "gem lines 'Gems Socketed in Red Sockets' (Dialla-style)", effect: "never match white sockets", source: "Modules/ModStore.lua:781-782 (compares socketColor)"}
conditions:
  - {text: "no config gate; the zero-defence base is applied by the Item.lua hack for this item name only", source: "Classes/Item.lua:2613-2616"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "static item; the zero defence lowers EHP in every scenario (not measured)", source: "Data/Uniques/body.lua:722-724"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same as Mapping; no scenario condition", source: "Data/Uniques/body.lua:722-724"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Tabula_Rasa (rev 1698806)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/body.lua, Data/Bases/body.lua, Classes/Item.lua, Modules/ModStore.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: removal / 4L-to-6L deltas (no headless run); whether a generator seed should treat 6L as the baseline"
  - "NOT VERIFIED: current area-level availability of drop level 3 in the running league"
  - "NOT VERIFIED: PoB behaviour when a socket group has more gems than sockets (grep 'too many gems' in SkillsTab / CalcSetup found nothing)"
  - "No interaction note exists for gem links and sockets (proposed: 'Gem links and sockets'); no related id invented"
open_questions:
  - "Should the generator model link count as a rule (4L / 5L / 6L), since PoB output does not see socket colour or the Tabula advantage?"
```
