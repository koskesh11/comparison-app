---
type: interaction
status: draft
pob_refs: [socketCount, linkedGems, EnergyShield, Armour, Evasion, TotalEHP]
source: "PoB 2.67.2 Data/Uniques/body.lua:722-724, Data/Bases/body.lua:411-414, Classes/Item.lua:2613-2616, Modules/ModStore.lua:781-785; poewiki Tabula Rasa rev 1698806; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Tabula Rasa is a Simple Robe with 6 linked white sockets, no attribute requirements and no defence of any kind (PoB zeroes the base energy shield by a hack in Item.lua). For a build it is the cheapest 6-link: any gem colour fits, no Fusing or Chromatic crafting, at the price of the whole body-armour defence layer.
PoB does check socket colour, but only for quality: a gem in a socket of its own colour gets +10% quality (Data.lua:303 MatchingSocketQualityBonus = 10; CalcActiveSkill.lua:553-557 GemSocketQuality), and white sockets never match. So Tabula costs that quality: EK -1.0% FullDPS, Worb -4.7% (all of the DPS loss; PoB removal/swap delta, see package.removal). PoB does not check socket COUNT (a 7th gem in the 6-socket group was counted). The big cost is defence: TotalEHP -54% (EK) / -46% (Worb) Pinnacle. A generator needs a link-count rule plus a quality rule.
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
  how: "Links: the data line 'Sockets: W-W-W-W-W-W' (Data/Uniques/body.lua:722-724, hyphen = linked) is read as 6 linked sockets. Zero defence: PoB hack Classes/Item.lua:2613-2616 sets ArmourData EnergyShield 0 and requirements.int 0 for Tabula Rasa (base Simple Robe, Data/Bases/body.lua:411-414), so the EHP loss shows in output. Socket colour: SkillsTab.lua:1237-1268 UpdateSocketGroups sets gem.matchesSocket when the socket colour equals the gem colour (white never matches; item.sockets.colourAlwaysMatches = Dialla), Data.lua:303 MatchingSocketQualityBonus = 10, CalcActiveSkill.lua:553-557 adds GemSocketQuality +10 to the skill (CalcSetup.lua:1680/1757 for supports), so six white sockets lose that quality on every gem that would have matched; GemProperty tags (ModStore.lua:781-785) and SocketAlwaysMatches (Item.lua:2688) also read the colour. Socket COUNT is not checked: a 7th gem added to the 6-socket body group counted (b5c-ia3.md section 1). Measured as a swap of the golden build's rare body armour for Tabula (in memory, PoB 2.67.2), see package.removal."
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Tabula Rasa", variant: "no variants", slot: body armour, role: blocks, target: self, text: "6 Linked White Sockets never match a gem colour: the +10% matching-socket quality is lost on every gem that a coloured socket would match", source: "Data.lua:303; SkillsTab.lua:1237-1268; CalcActiveSkill.lua:553-557; measured b5c-ia3.md section 1 (isolation rows, all-white rare)", pob: full}
  - {kind: unique, name: "Tabula Rasa", variant: "no variants", slot: body armour, role: blocks, target: self, text: "Has no Attribute Requirements or Energy Shield (hidden wiki mod RemoveStatsFromTabulaRasa, cargo local_unique_tabula_rasa_no_requirement_or_energy_shield)", source: "Classes/Item.lua:2613-2616 (hack); poewiki Tabula Rasa rev 1698806", pob: full}
  - {kind: unique, name: "Tabula Rasa", variant: "no variants", slot: body armour, role: enables, target: self, text: "Has 6 Linked White Sockets (hidden wiki mod ItemHasSixLinkedWhiteSocketsUniqueBodyInt6, cargo local_six_linked_white_sockets)", source: "Data/Uniques/body.lua:722-724", pob: full}
package:
  seed: none
  slot: "Body Armour"
  base: "Simple Robe (socketLimit 6)"
  variant: "none"
  removal: "PoB swap delta (Tabula Rasa replaces the golden build's rare body armour, in memory; the rare's life, resists and attributes are lost too, so it is not Tabula alone; b5c-ia3.md section 1, FullDPS re-run b5c-ia4.md section 5). CoC EK Assa (replaced: Cataclysm Shroud, Necrotic Armour; skill Ethereal Knives, CoC-triggered): Pinnacle FullDPS -1.05% (15,148,519 -> 14,989,880), Ethereal Knives TotalDPS -1.03% (7,728,445 -> 7,649,097), TotalEHP -54.2% (145,259 -> 66,598); Mapping FullDPS -1.10% (14,431,692 -> 14,273,034), TotalEHP -49.1% (71,911 -> 36,600). Worb (replaced: Empyrean Guardian, Sacred Chainmail; skill Winter Orb): Pinnacle FullDPS and Winter Orb TotalDPS -4.65% (6,717,488 -> 6,405,046; 1,343,498 -> 1,281,009), TotalEHP -45.6% (76,837 -> 41,789); Mapping FullDPS -4.65% (9,671,056 -> 9,221,239), TotalEHP -69.6% (81,163 -> 24,666). Isolation (same rare, all 6 sockets white): the DPS loss is identical to the Tabula swap in both builds (EK Ethereal Knives 7,649,097; Worb Winter Orb 1,281,009), so the DPS cost is the lost +10% socket quality; EHP is lost only with the missing body defences. Quality lost per build: EK 4 of 6 gems matched before (Increased Critical Strikes, Increased Critical Damage, Cast On Critical Strike, Ethereal Knives), Worb only Winter Orb (q30 -> 20) and Infused Channelling. Headless deltas, not game facts."
  downsides_that_are_the_point: ["no defence at all: no ES / armour / evasion, not even base values (wiki rev 1698806; Mark_GGG quote 'offers offensive power ... at the cost of defenses')"]
  foulborn: "none (no Tabula entry in Data/ModFoulbornMap.jsonc, grep returned nothing)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level 3, release 0.10.5; poewiki rev 1698806; recipes 9 Humility, 9 Vanity (corrupted), 3 Sambodhi's Wisdom (two-implicit corrupted); vendor 20 Orb of Fusing (3.19.0 note); patch 3.29"
makes_redundant:
  - {provider: "Chromatic Orb socket colouring, Orb of Fusing 6-link crafting, Jeweller's Orb", when: "Tabula Rasa is worn", why: "the item already has 6 linked sockets of any gem colour (but no colour-match quality: PoB gives +10% quality only to gems in a socket of their own colour, Data.lua:303)", source: "poewiki Tabula Rasa rev 1698806; b5c-ia3.md section 1"}
conflicts:
  - {with: "gems that would get the +10% matching-socket quality in a coloured body armour", effect: "white sockets never match in PoB, so every such gem loses 10% quality (EK -1.05%, Worb -4.65% FullDPS Pinnacle)", source: "Data.lua:303; CalcActiveSkill.lua:553-557; b5c-ia3.md section 1"}
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
  - "NOT VERIFIED: 4L-to-6L deltas (only the swap against the golden builds' rare 6-socket bodies was run); whether a generator seed should treat 6L as the baseline"
  - "NOT VERIFIED: current area-level availability of drop level 3 in the running league"
  - "PoB does not limit gems to the socket count: Worb with Tabula + a 7th gem (Added Cold Damage) in the body group: Winter Orb TotalDPS 1,281,009 -> 1,615,067 (Pinnacle), 1,844,248 -> 2,325,185 (Mapping), FullDPS 6,405,046 -> 8,075,334 / 9,221,239 -> 11,625,924, requirements counted the gem, itemWarnings empty (b5c-ia3.md section 1, b5c-ia4.md section 5). A generator must enforce the socket count itself. NOT VERIFIED: why the same 7th gem changed nothing for Ethereal Knives in the EK build"
  - "NOT VERIFIED: the game effect of white sockets on 'Socketed Red / Green / Blue' effects (not tested)"
  - "No interaction note exists for gem links and sockets (proposed: 'Gem links and sockets'); no related id invented"
open_questions:
  - "Should the generator model link count as a rule (4L / 5L / 6L), since PoB does not check socket count (7th gem counted) and prices Tabula only by its lost colour-match quality and lost defences, not by the free 6L?"
```
