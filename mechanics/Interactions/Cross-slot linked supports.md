---
type: interaction
status: draft
pob_refs: [LinkedSupport, TotalDPS, FullDPS, TotalEHP, SocketGroupSlot]
source: "PoB 2.67.2 Modules/ModParser.lua:3421-3427, Modules/CalcSetup.lua:1594-1598 and 1814-1834 (and :833, :1480, :1606, :1790), Classes/Item.lua:2247, Data/Uniques/shield.lua:892, Data/Uniques/amulet.lua:1199, Data/ModItemExclusive.lua:7709-7710; poewiki The Squire rev 1677261, Uul-Netol's Vow rev 1700789; tasks/reports/027-evidence/b5c-pca.md section B, b5c-mr.md section B, b5c-ia3.md section 2, b5c-ia4.md (task 027 lane 5c)"
last_confirmed_patch: "3.29.x"
---

Two uniques let support gems socketed in one item also support the skills of another slot: The Squire (shield supports -> main hand skills) and Uul-Netol's Vow (amulet supports -> body armour skills). In PoB the link is a plain "add the supports of socket group A to the skills of group B" step, and it only fires for skill groups whose Skills-tab slot equals the target slot.
Generator hint: the value appears only when the generator puts the main skill into a socket group assigned to the target slot (Weapon 1 for The Squire, Body Armour for Uul-Netol's Vow). If the main skill sits in another slot's group (the golden builds keep it in the body-armour group) the item adds nothing: measured delta 0 on Worb.xml as built. The slot choice of the main skill is therefore part of the item decision, not a later detail.
All numbers below are PoB removal/swap deltas on a golden build, not game facts. PoB checks neither the socket layout of the source item nor the colours of the cross-linked gems beyond ordinary support compatibility.

Pipeline: [[Damage calculation#More and less]] - cross-linked supports are ordinary support gems on the target skill (more / less pool, quality, level). Item note with the other lines of the shield: [[Unique - The Squire]].

```interaction
id: cross-slot-linked-supports
mechanic: "Support gems socketed in one item also support the skills of another equipment slot (The Squire: shield -> main hand incl. item-granted skills; Uul-Netol's Vow: amulet -> body armour); PoB applies them only to skill groups assigned to the target slot"
family: resource
pipeline_step: ["Damage calculation#More and less"]
pipeline_why: "the cross-linked supports join the target skill's support list like directly linked ones, so their more / less multipliers, added damage and quality enter the normal damage pool"
target: self
related: [unique-the-squire, damage-calculation]
pob:
  measured: full
  how: "Parse ModParser.lua:3421-3427: pattern 'socketed support gems can also support skills from ...'; captured text 'main hand' gives targetSlotName Weapon 1, ANY other wording silently becomes Body Armour. Source slot = slot of the item carrying the mod (Classes/Item.lua:2247). Collect CalcSetup.lua:1594-1598 (crossLinkedSupportGroups[sourceSlot]); apply CalcSetup.lua:1814-1834: every active skill whose group slot (' Swap' stripped, :1738) equals the target slot gets the supports of the socket groups whose slot equals the source slot, via addBestSupport (normal compatibility, level, quality, best-of-duplicates). Item-granted skills are included: their groups carry slot = grantedSkill.slotName (:833, :1480) and the loop sits outside the group.source branch, except groups with noSupports (:1499, :1790). Weapon swap: groups of the inactive set are disabled (:1606) and the mod comes from the active set's items, so the link follows the active set. Measured with PoB's own rebuild order on Worb.xml (b5c-ia3 section 2, b5c-ia4: Worb rows identical after the re-run)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "The Squire", slot: shield, role: enables, target: self, text: "Socketed Support Gems can also Support Skills from your Main Hand (shield Weapon 2 -> Weapon 1; all variants, 3 sockets)", source: "Data/Uniques/shield.lua:892; Data/ModCache.lua:21788; Modules/CalcSetup.lua:1594-1598, 1814-1834; b5c-pca.md section B Providers; poewiki The Squire rev 1677261", pob: full}
  - {kind: unique, name: "Uul-Netol's Vow", slot: amulet, role: enables, target: self, text: "Socketed Support Gems can also Support Skills from Equipped Body Armour (Unset Amulet, 1 socket; amulet -> Body Armour)", source: "Data/Uniques/amulet.lua:1199; Data/ModCache.lua:21787; Modules/CalcSetup.lua:1594-1598, 1814-1834; b5c-pca.md section B Providers; poewiki Uul-Netol's Vow rev 1700789", pob: full}
  - {kind: mod, name: "SupportGemsSocketedInOffHandAlsoSupportMainHandSkills", slot: shield, role: enables, target: self, text: "item-exclusive mod id behind the Squire line (level 90 in the data; whether it can be crafted or only rolls on the unique is not checked)", source: "Data/ModItemExclusive.lua:7709; b5c-pca.md section B Providers", pob: full}
  - {kind: mod, name: "SupportGemsSocketedInAmuletAlsoSupportBodySkills", slot: amulet, role: enables, target: self, text: "item-exclusive mod id behind the Uul-Netol's Vow line (level 90 in the data; whether it can be crafted or only rolls on the unique is not checked)", source: "Data/ModItemExclusive.lua:7710; b5c-pca.md section B Providers", pob: full}
makes_redundant:
  - {provider: "a 6-link body armour or extra weapon sockets for the target skill", when: "the target skill sits in the target slot's group and the source item holds the supports", why: "the source item's sockets (3 on The Squire, 1 on Uul-Netol's Vow) reach the target skill as extra support sockets", source: "Modules/CalcSetup.lua:1814-1834; Data/Uniques/shield.lua:892; Data/Uniques/amulet.lua:1199"}
conflicts:
  - {with: "two-handed weapon in the main hand (The Squire)", effect: "the shield cannot be equipped, so the Squire link does not exist", source: "poewiki The Squire rev 1677261 ('the shield cannot be used with two-handed weapons')"}
  - {with: "main skill in a socket group assigned to another slot (e.g. the body-armour group while using The Squire)", effect: "the cross-linked supports do not reach it: measured 0 change on Worb.xml as built", source: "Modules/CalcSetup.lua:1814-1834; b5c-ia3.md section 2 rows R1 = R2"}
  - {with: "granted skills with noSupports (triggered / no-support item skills)", effect: "no supports at all, cross-linked ones included", source: "Modules/CalcSetup.lua:1499, 1790"}
  - {with: "a new wording of the line in a future patch", effect: "PoB parses any slot text other than 'main hand' as Body Armour, so a new provider with another slot would be linked to the wrong group until ModParser is fixed", source: "Modules/ModParser.lua:3421-3427"}
conditions:
  - {text: "the supported skill must be in a socket group (or item-granted group) whose slot is the target slot: Weapon 1 for The Squire, Body Armour for Uul-Netol's Vow; a gem group with no slot assigned is not reached", source: "Modules/CalcSetup.lua:1814-1834; b5c-pca.md section B 'Main-hand group needs'"}
  - {text: "the supports must sit in a socket group assigned to the source item's slot (Weapon 2 for the Squire, Amulet for the Vow), enabled or the main group", source: "Modules/CalcSetup.lua:1608, 1620-1622, 1669-1731; b5c-pca.md section B"}
  - {text: "each cross-linked support must still be compatible with the target skill (normal support rules); e.g. an attack support listed on a spell has no effect expected", source: "Modules/CalcSetup.lua:1814-1834 (addBestSupport); b5c-ia3.md NOT VERIFIED (Faster Attacks on Frostbite not confirmed filtered)"}
  - {text: "item-granted skills of the target slot receive the supports too (wiki: 'includes both Skills from Gems or Skills granted by items'); PoB agrees", source: "poewiki The Squire rev 1677261 Mechanics; poewiki Uul-Netol's Vow rev 1700789; Modules/CalcSetup.lua:833, 1480, 1814-1834; b5c-ia3.md p5 (Balefire / Scorching Ray)"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "static item line, no condition; use PoB's own number with the main skill in the target slot's group. PoB removal/swap delta on Worb.xml (Winter Orb, Mapping): Squire group disabled 543,555 -> enabled 1,291,133 TotalDPS (+137.5 percent) with 3 supports Increased Critical Strikes / Increased Critical Damage / Added Cold Damage and Winter Orb moved alone into a Weapon 1 group", source: "b5c-ia3.md section 2 Worb rows R3 vs R4"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same item line. PoB removal/swap delta on Worb.xml (Winter Orb, Pinnacle): 382,055 -> 896,796 TotalDPS (+134.7 percent), same setup. About +1.9 percent of this is the Squire's own part (+7 quality on the supports, +10 from a matching socket colour on Added Cold Damage): the control with the same 3 supports linked directly gives 880,232", source: "b5c-ia3.md section 2 Worb rows R3 / R4 / R5"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/The_Squire (rev 1677261)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Uul-Netol%27s_Vow (rev 1700789)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/ModParser.lua, Modules/CalcSetup.lua, Classes/Item.lua, Data/Uniques/shield.lua, Data/Uniques/amulet.lua, Data/ModItemExclusive.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b5c-pca.md (section B), b5c-mr.md (section B), b5c-ia3.md (section 2), b5c-ia4.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: game behaviour for item-granted skills beyond the wiki quote; PoB also gives the granted skill the supports of the Weapon 1 group itself, which in the game would need those gems socketed in the weapon (b5c-ia3.md section 2, p5)"
  - "NOT VERIFIED: weapon-swap set in game: PoB strips ' Swap' from the slot name (CalcSetup.lua:1610, 1738) and follows the active set (:1606); the game's rule for the second weapon set is undocumented (b5c-mr.md B3)"
  - "NOT VERIFIED: real socket colours and link layout of The Squire; PoB forces 3 linked sockets of the base's default colour via 'Has 3 Sockets' (Item.lua:2640-2661); since 3.29.0 a new drop no longer has all white sockets (wiki rev 1677261), so colour-matched bonuses (e.g. the +10 on Added Cold Damage) may not hold"
  - "NOT VERIFIED: delta on Ethereal Knives (CoC Assassin): rows exist (b5c-ia3.md, +92.7 percent Pinnacle) but Ethereal Knives stops being CoC-triggered in the moved setup, so it is not the real build and is not used here"
  - "NOT VERIFIED: any measured delta for Uul-Netol's Vow (no headless run in lane 5c)"
  - "NOT VERIFIED: whether the Foulborn Squire variants change the link (not measured; the Foulborn lines replace block and quality lines only, see the Squire note)"
open_questions:
  - "Cost side (PoB swap delta on Worb.xml, Winter Orb, body-group main skill, no links used): swapping the golden shield for The Squire costs Winter Orb -2.4 percent (Pinnacle and Mapping) and TotalEHP -26 percent Pinnacle (76,837 -> 56,723) / -35 percent Mapping (81,163 -> 52,707), block 44 -> 34 (b5c-ia3.md section 2 R1 vs R0). Is the trade accepted for a build that keeps the main skill in the weapon group?"
  - "Should the generator treat 'main skill in a Weapon 1 group' as a required choice whenever The Squire is a candidate, even though that group loses the body-armour links the golden builds use?"
```
