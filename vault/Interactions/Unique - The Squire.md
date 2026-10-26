---
type: interaction
status: draft
pob_refs: [LinkedSupport, SocketCount, BlockChance, BlockRecovery, TotalDPS]
source: "PoB 2.67.2 Data/Uniques/shield.lua:883-894, Modules/ModParser.lua:3426, Modules/CalcSetup.lua:1594-1597 and 1815-1830, Data/ModFoulbornMap.jsonc:565-568, Data/ModFoulborn.lua:764-767, Data/ModCache.lua lines per provider; poewiki The Squire rev 1677261, Foulborn unique item rev 1702126; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

The Squire is a 3-socket shield whose socketed support gems also support the skill in the main hand (stat support_gems_socketed_in_off_hand_also_support_main_hand_skills). For a build that is three extra support sockets for the main-hand skill without a 6L chest, plus block, armour/evasion and support quality.
In PoB the supports of the group slotted to the shield are added to the skill slotted in Weapon 1 only (CalcSetup.lua:1815-1830); a body-armour skill gets nothing: both golden builds keep their main skill in the body group, so as built the Squire adds 0 to it (PoB swap delta, b5c-ia3.md section 2 row R2 = R1). It cannot be used with a two-handed main hand.
3.29.0 removed "All Sockets are White" (wiki rev 1677261, existing copies keep it). PoB keeps both through its two variants, but its Foulborn map still holds the removed mod (see open questions).
Uniques are packages: every line is valued, including the downside that is the point (none in the text; the constraint is structural).

Pipeline: [[Damage calculation#More and less]] - supports from the shield link into the main-hand skill and apply their more / less multipliers; [[Receiving damage#Block]] - the block line

```interaction
id: unique-the-squire
mechanic: "Unique package: a 3-socket shield whose support gems also support the main-hand skill (extra support sockets for the weapon skill) with block, armour/evasion and support quality"
family: resource
pipeline_step: ["Damage calculation#More and less", "Receiving damage#Block"]
pipeline_why: "the cross-linked supports are ordinary support gems on the main-hand skill (more / less pool); the block line acts in the block step after all mitigation"
target: self
related: [block, cross-slot-linked-supports]
pob:
  measured: partial
  how: "ModParser.lua:3426 creates LinkedSupport {targetSlotName='Weapon 1'} from the line (ModCache.lua:21788). CalcSetup.lua:1594-1597 builds crossLinkedSupportGroups[Weapon 2] = {'Weapon 1'}; CalcSetup.lua:1815-1830 adds the supports of every socket group slotted to the shield to the displayGemList / appliedSupportList of the skill in slot Weapon 1. Also run: the supports reach a skill in a Weapon 1 group (R3 vs R4) and a main-hand item-granted skill (Balefire / Scorching Ray), see package.removal. The cross-linked supports are ordinary supports, so the matching-socket +10% quality applies to them by their socket colour (Added Cold Damage q37 = 20 + Squire 7 + 10 on a G socket, b5c-ia3.md section 2). Other lines are plain parses (ModCache lines in providers)."
  config: []
  unparsed: ["The Squire (variant Pre 3.29.0): 'All Sockets are White' -> ModCache.lua:13660 parses to {} (display only)"]
model: null
providers:
  - {kind: unique, name: "The Squire", variant: "Current", slot: shield, role: sustains, target: self, text: "Implicit: 120% increased Block Recovery", source: "Data/Uniques/shield.lua:883-894; Data/ModCache.lua:4661", pob: full}
  - {kind: unique, name: "The Squire", variant: "Current", slot: shield, role: enables, target: self, text: "Has 3 Sockets", source: "Data/ModCache.lua:16689", pob: partial}
  - {kind: unique, name: "The Squire", variant: "Pre 3.29.0", slot: shield, role: enables, target: self, text: "All Sockets are White (removed in 3.29.0 for new drops; existing copies keep it)", source: "Data/Uniques/shield.lua:885-886; Data/ModCache.lua:13660; poewiki The Squire rev 1677261", pob: none}
  - {kind: unique, name: "The Squire", variant: "Current", slot: shield, role: scales, target: self, text: "+(5-8)% to Quality of Socketed Support Gems", source: "Data/ModCache.lua:394, 527, 2257, 2586 (GemProperty quality, keyword support, SocketedIn)", pob: full}
  - {kind: unique, name: "The Squire", variant: "Current", slot: shield, role: enables, target: self, text: "Socketed Support Gems can also Support Skills from your Main Hand", source: "Data/ModCache.lua:21788; Modules/ModParser.lua:3426; Modules/CalcSetup.lua:1594-1597, 1815-1830", pob: full}
  - {kind: unique, name: "The Squire", variant: "Current", slot: shield, role: sustains, target: self, text: "(100-150)% increased Armour and Evasion (local)", source: "Data/Uniques/shield.lua:883-894 (cargo local_armour_and_evasion_+%, parsed live)", pob: full}
  - {kind: unique, name: "The Squire", variant: "Current", slot: shield, role: sustains, target: self, text: "+(3-5)% Chance to Block", source: "Data/ModCache.lua:1666, 2202", pob: full}
  - {kind: foulborn, name: "The Squire", variant: "+(3-5)% Chance to Block", slot: shield, role: enables, target: self, text: "Ignore Attribute Requirements of Socketed Gems", source: "Data/ModFoulborn.lua:764-767; Data/ModCache.lua:17073 (GemProperty req 0); poewiki The Squire rev 1677261", pob: partial}
  - {kind: foulborn, name: "The Squire", variant: "+(5-8)% to Quality of Socketed Support Gems", slot: shield, role: scales, target: self, text: "+1 to Level of Socketed Gems", source: "Data/ModFoulborn.lua:764-767; Data/ModCache.lua:182 (GemProperty level +1, SocketedIn); poewiki The Squire rev 1677261", pob: partial}
package:
  seed: none
  slot: "Shield (off-hand)"
  base: "Elegant Round Shield (same base as The Oppressor)"
  variant: "Current; a 'Pre 3.29.0' variant exists"
  removal: "PoB swap/removal deltas (b5c-ia3.md section 2, re-run identical in b5c-ia4.md section 5), golden build Worb (skill Winter Orb, Pinnacle / Mapping; replaced shield: Vengeance Chant, Titanium Spirit Shield, 27% cold damage, +108 life): (a) whole swap with the main skill left in the body group (R1 vs R0): Winter Orb TotalDPS -2.4% / -2.4% (1,343,498 -> 1,310,904; 1,934,211 -> 1,887,287), TotalEHP -26.2% / -35.1% (76,837 -> 56,723; 81,163 -> 52,707), block 44 -> 34; (b) the three shield supports (Increased Critical Strikes, Increased Critical Damage, Added Cold Damage, gem level 20) change NOTHING for the body-slot Winter Orb (R2 = R1), as built; (c) the same skill moved into a Weapon 1 group (setup change, not the user build): Squire group enabled vs disabled (R3 vs R4) Winter Orb TotalDPS +134.7% / +137.5% (896,796 vs 382,055; 1,291,133 vs 543,555) and FullDPS +134.7% / +137.5%; the same three supports linked directly (R5 control, 880,232) leave the Squire's own part at +1.9% (+7 quality on supports, +10 matching socket on Added Cold Damage); R3-R5 lack the body group's Focused/Infused Channelling and Arcane Surge, so compare only inside R3-R5. Golden build CoC EK Assa (skill Ethereal Knives, CoC-triggered; replaced shield: Phoenix Mark, Titanium Spirit Shield): shield swap alone leaves Ethereal Knives TotalDPS unchanged (7,728,445 / 7,331,707) with TotalEHP 145,259 -> 75,095 (-48.3%) Pinnacle and 71,911 -> 40,671 (-43.4%) Mapping; with Ethereal Knives moved alone into a Weapon 1 group (no longer CoC-triggered, Speed 2.8 not 8.9, so NOT the real build) the group adds +92.7% / +102.2% (1,266,878 vs 657,302; 1,238,441 vs 612,524), own part +1.4%; the EK 'old group re-filled' row is an artefact (Pride, Clarity, Enlighten lost). Item-granted main-hand skill (Worb with Balefire sceptre, Scorching Ray, PoB swap, no DPS number): receives the Squire's three supports (q7 more than the gem) and only Arcane Surge without the Squire group. Headless deltas, not game facts."
  downsides_that_are_the_point: ["none among the lines; structural: the shield cannot be used with a two-handed weapon (wiki rev 1677261); since 3.29.0 a new drop has random socket colours (colour requirements matter on the shield)"]
  foulborn: "3.29: replaces +(3-5)% Chance to Block with 'Ignore Attribute Requirements of Socketed Gems' and +(5-8)% quality with '+1 to Level of Socketed Gems' (wiki rev 1677261); PoB Data/ModFoulbornMap.jsonc:565-568 still maps the REMOVED original AllSocketsAreWhiteUniqueShieldStrDex7_ -> NoAttributeRequirements (pre-3.29 pairing) and has no block-chance replacement; wiki: legacy Foulborn can have both block and ignore requirements"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level null (base item level applies, NOT VERIFIED how), req 70, release 3.16.0; wiki rev 1677261: Tainted Mythic Orb grants The Squire or The Oppressor ('The Oppressor is much more common'); 8 The Shieldbearer, or 3 Akil's Prophecy for a random two-implicit corrupted Elegant Round Shield; Foulborn via Genesis Tree / Grasping Coffers (wiki rev 1702126); patch 3.29"
makes_redundant:
  - {provider: "a second weapon-slot link set / 6L body armour for the main-hand skill", when: "The Squire supports sit in the shield group", why: "three extra support sockets reach the main-hand skill", source: "Modules/CalcSetup.lua:1815-1830"}
conflicts:
  - {with: "two-handed main hand", effect: "the shield cannot be equipped", source: "poewiki The Squire rev 1677261"}
  - {with: "skills not slotted in the main hand (e.g. body-armour group)", effect: "do not receive the shield supports", source: "Modules/CalcSetup.lua:1594-1597, 1815-1830"}
conditions:
  - {text: "the supported skill must be socketed in the main-hand weapon (slot Weapon 1)", source: "Modules/CalcSetup.lua:1815-1830; Data/ModCache.lua:21788 (targetSlotName Weapon 1)"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "static item lines; no condition", source: "Data/Uniques/shield.lua:883-894"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same as Mapping", source: "Data/Uniques/shield.lua:883-894"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/The_Squire (rev 1677261)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Foulborn_unique_item (rev 1702126)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/shield.lua, Modules/CalcSetup.lua, Modules/ModParser.lua, Data/ModFoulbornMap.jsonc, Data/ModFoulborn.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: link layout of 'Has 3 Sockets' (the PoB item text needs 'Sockets:' with hyphens; the unique DB line is only 'Has 3 Sockets')"
  - "Item-granted main-hand skills: PoB gives them the supports (CalcSetup.lua:833 and 1480 set the group slot to the granting slot; run: Scorching Ray from Balefire, b5c-ia3.md section 2); wiki rev 1677261: 'includes both Skills from Gems or Skills granted by items'. PoB also gives that skill the Weapon 1 group's own supports, which in the game needs those gems socketed in the weapon: NOT VERIFIED against the game"
  - "NOT VERIFIED: the exact Foulborn pairing in 3.29 for PoB users (PoB's map is stale)"
  - "NOT VERIFIED: Genesis Tree / Foulborn route in the running league; the Pre 3.29.0 (all white) and Foulborn variants were not run; the real drop's socket colours and links (PoB forces 3 linked G sockets, Item.lua:2640-2661)"
  - "NOT VERIFIED: whether Faster Attacks (an attack support) listed on Frostbite / Frostblink after the swap is filtered later in PoB (no DPS effect seen); EK shield-swap EHP loss includes the Phoenix Mark line 'Socketed Gems have 20% increased Reservation Efficiency' (ManaUnreserved 107 -> 32, still positive)"
  - "The cross-slot link itself is described in [[cross-slot-linked-supports]]; [[block]] carries only the block line"
open_questions:
  - "PoB ModFoulbornMap.jsonc:565-568 still maps the removed mod 'All Sockets are White' (3.29.0 removed it, wiki rev 1677261): trust the wiki pairing for Foulborn Squire?"
```
