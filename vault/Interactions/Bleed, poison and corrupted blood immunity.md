---
type: interaction
status: draft
pob_refs: [BleedAvoidChance, PoisonAvoidChance, CorruptedBloodImmunity, BleedImmune, PoisonImmune, CorruptedBloodImmune, AvoidBleed, AvoidPoison, AvoidAilments, conditionBleeding]
source: "poewiki Bleeding rev 1700575, Poison rev 1700788, Corrupted Blood rev 1673502, Ailment rev 1673310, Immunity rev 1674448, Sirus rev 1702453 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua:1590,1620,3534-3566, ModParser.lua:4889-4917, Data/ModFlask.lua; live parse of every quoted line (b1c-mechanics-immunity.md); EK sample probe (b1c-pob-flasks.md)"
last_confirmed_patch: "3.29.x"
---

How the player stops bleeding, poison and corrupted blood on themselves. Corrupted blood is its own debuff (only the 10 highest stacks deal damage, armour does not reduce it, it should not be confused with bleeding) and has its own immunity text, so a 'Bleeding cannot be inflicted' line does not cover it. Taking all physical damage as elemental or chaos damage is effectively bleed immunity, and Chaos Inoculation makes poison harmless. Related: [[Bleed]] and [[Poison]] (the enemy-side notes), [[Physical damage taken as elemental]], [[Flask uptime]], [[Defences]].
Impact: PoB gives only avoid chances and a corrupted blood flag, no number for 'how much do I lose without immunity': bleed on you is never computed, corrupted blood has no damage model, and poison and ignite enter only through the hand-filled enemy damage-over-time config. EK sample: its Eternal Life flask moves BleedAvoidChance 0 to 100 and changes nothing else in the numbers (CI build, TotalEHP unchanged).
Pipeline: [[Receiving damage#Damage over time taken]] - bleed, poison and corrupted blood are damage over time (no armour, no block); the avoid roll sits in [[Defences#Ailment avoidance]].

```interaction
id: bleed-poison-cb-immunity
mechanic: "Bleeding, poison and corrupted blood on you: Immune (stops new, removes existing) or Cannot be inflicted (existing stay) or chance to avoid; corrupted blood is separate from bleeding and needs its own immunity text; damage over time ignores armour, only extra damage reduction mitigates corrupted blood"
family: defence
pipeline_step: ["Receiving damage#Damage over time taken", "Defences#Ailment avoidance"]
pipeline_why: "these ailments are damage over time that skips armour and block; the avoid roll is separate from damage avoidance and decides whether the debuff exists at all"
target: self
related: [bleed, poison, physical-taken-as-elemental, flask-uptime, defences, elemental-ailment-immunity, stun]
pob:
  measured: partial
  how: "output.BleedAvoidChance and PoisonAvoidChance = 100 if BleedImmune / PoisonImmune else min(100, AvoidBleed + AvoidAilments) (Modules/CalcDefence.lua:1620; shown Modules/CalcSections.lua:1899-1900). output.CorruptedBloodImmunity = flag CorruptedBloodImmune (CalcDefence.lua:1590), shown only as 'Corr Blood Immune: True' (CalcSections.lua:1905). Poison on you: the enemy-DoT model multiplies enemy PoisonChance by (1 - PoisonAvoidChance/100) (CalcDefence.lua:3542-3544). Bleed on you is never modelled: local enemyBleedChance = 0 and never assigned (CalcDefence.lua:3534; other uses 3545, 3607, 3609 only). Corrupted blood has no damage model (grep: only line 1590). The only gate for a number is the enemy damage-over-time config (damageCategoryConfig == DamageOverTime, CalcDefence.lua:3536-3566) that the user must fill by hand. Live parse (not ModCache): Bleeding cannot be inflicted, You are Immune to Bleeding, Corrupted Blood cannot be inflicted on you and Immunity to Poison / Bleeding and Corrupted Blood during Effect all parse (ModParser.lua:4889-4890,4912-4917); reactive 'if used while' flask lines parse as immunity under Condition UsingFlask, so PoB counts them permanent (same over-count as the elemental note). Generator reads output.BleedAvoidChance, PoisonAvoidChance, CorruptedBloodImmunity (boolean)."
  config:
    - {var: conditionBleeding, default: false, ref: "Modules/ConfigOptions.lua:1219 ('Are you Bleeding?', gates only 'while Bleeding' mods; type check, no explicit default)", class: b}
    - {var: enemy damage over time box, default: "empty (hand-set)", ref: "Modules/CalcDefence.lua:3536-3566 (damageCategoryConfig DamageOverTime; the config var name was not looked up)", class: c}
  unparsed:
    - "Adamant (node 49416): Remove Corrupted Blood when you use a Guard Skill - not parsed"
    - "Soul of Shakari: You cannot be Poisoned while there are at least 3 Poisons on you - not parsed"
    - "Drek, Apex Hunter (Ralakesh upgrade): Corrupted Blood cannot be inflicted on you if you have at least 5 Corrupted Blood Debuffs on you - not parsed"
model:
  proposed_kind: reactive_flask_immunity_window
  inputs: {from_pob: [flask tooltip duration and uptime, "BleedAvoidChance / PoisonAvoidChance / CorruptedBloodImmunity"], from_scenario: [enemy hit rate with bleed / poison / corrupted blood, scenario length]}
  params: {immunity_seconds_by_tier: "6-8 up to 15-17 s (reactive suffixes, Data/ModFlask.lua:216-219,232-235)", corrupted_blood_stack_cap: 10, first_application: "always lands (the flask is used while already affected)"}
  formula: "same as the elemental note: reactive 'if used while Bleeding / Poisoned / affected by Corrupted Blood' suffixes protect only the window after one use, PoB counts them permanent. 'during Effect' suffixes follow the flask uptime. No damage number for bleed or corrupted blood exists in PoB, so a generator that needs one has to use the config box by hand."
  calibration: "no norm found"
providers:
  - {kind: flask, name: "of the Lizard / Skink / Iguana (utility)", slot: flask, role: enables, target: self, text: "Immunity to Bleeding and Corrupted Blood during Effect + (49-45 / 44-40 / 39-35)% less Duration (lv 8 / 42 / 76)", source: "Data/ModFlask.lua:248-250", pob: full}
  - {kind: flask, name: "reactive: of Sealing / Alleviation / Allaying / Assuaging (life or mana flask)", slot: flask, role: enables, target: self, text: "Grants Immunity to Bleeding for (6-8 .. 15-17) seconds if used while Bleeding; Grants Immunity to Corrupted Blood for the same time if used while affected by Corrupted Blood (lv 8 / 32 / 56 / 80, weight 750 on life flasks); removes Corrupted Blood stacks on use. EK carries one (Condensed Eternal Life Flask of Sealing): BleedAvoidChance 0 to 100 with it", variant: "Condensed Eternal Life Flask of Sealing (EK sample, flask 2)", source: "Data/ModFlask.lua:216-219; b1c-pob-flasks.md (EK table: BleedAvoidChance 100 with, 0 with the flask off); wiki Modifier:FlaskBleedCorruptingBloodImmunity1", pob: partial}
  - {kind: flask, name: "poison flasks: Skunk / Hedgehog / Opossum (during effect), Antitoxin .. Antidote (reactive)", slot: flask, role: enables, target: self, text: "Immunity to Poison during Effect (lv 16 / 46 / 76); Grants Immunity to Poison for (6-8 .. 15-17) s if used while Poisoned (lv 16 / 38 / 60 / 82)", source: "Data/ModFlask.lua:232-238", pob: partial}
  - {kind: unique, name: "Craiceann's Carapace, Death's Door, The Ghastly Theatre (variant 2)", slot: body armour / boots / shield, role: enables, target: self, text: "Bleeding cannot be inflicted on you", variant: "The Ghastly Theatre variant 2", source: "Data/Uniques/body.lua:67; boots.lua:893; shield.lua:843", pob: full}
  - {kind: unique, name: "Ralakesh's Impatience (variants 3-5)", slot: boots, role: enables, target: self, text: "Corrupted Blood cannot be inflicted on you", variant: "Ralakesh's Impatience variants 3-5", source: "Data/Uniques/boots.lua:932", pob: full}
  - {kind: unique, name: "Viper's Scales, The Living Blade, The Infinite Pursuit (variant 2), Replica Alpha's Howl", slot: any, role: enables, target: self, text: "Cannot be Poisoned (Viper's Scales, The Living Blade); Infinite Pursuit variant 2 cannot be Poisoned while Bleeding; Replica Alpha's Howl 25% Avoid being Poisoned", source: "Data/Uniques/body.lua:910; sword.lua:265; boots.lua:69; helmet.lua:219", pob: full}
  - {kind: mod, name: "corrupted implicit (ring / belt ilvl 60+), corrupted jewel, Delve suffix", slot: ring / belt / jewel / armour, role: enables, target: self, text: "ring and belt: Bleeding cannot be inflicted on you; jewel (lv 33) and Delve armour suffix (lv 60): Corrupted Blood cannot be inflicted on you; Delve 50% chance to Avoid being Poisoned / Bleeding; corrupted jewel (20-25)% Avoid Bleeding / Poisoned", source: "Data/ModCorrupted.lua:141; Data/ModJewel.lua:20,39-40; Data/ModDelve.lua:25,188-189", pob: full}
  - {kind: mastery, name: "Protection Mastery", slot: tree, role: enables, target: self, text: "Corrupted Blood cannot be inflicted on you (tree effect 9074; live parse sets CorruptedBloodImmune). Wiki Sirus names this together with the jewel implicit", source: "TreeData/3_29/tree.lua (effect 9074, scan in b1c-mechanics-immunity.md); poewiki Sirus rev 1702453", pob: full}
  - {kind: mastery, name: "Armour and Evasion Mastery", slot: tree, role: enables, target: self, text: "Immune to Bleeding if Equipped Helmet has higher Armour than Evasion Rating; Immune to Poison if the helmet has higher Evasion (effect 43258)", source: "Modules/ModParser.lua:4912-4913; TreeData/3_29/tree.lua (effect 43258)", pob: partial}
  - {kind: gem, name: "Steelskin", slot: any, role: enables, target: self, text: "guard skill: AvoidBleed 100 and 'buff grants Immunity to Bleeding'; removes bleeding when used", source: "Data/Skills/act_str.lua block 11005-11100 (about line 11027, exact line not pinned); wiki Steelskin rev 1682040", pob: full}
  - {kind: notable, name: "Antivenom, Tolerance, Poison Avoidance smalls, Evasion Mastery", slot: tree, role: scales, target: self, text: "Tolerance 30% Avoid being Poisoned; small nodes 20% Poison Avoidance; Chaos Resistance and Avoidance smalls 10%; Evasion Mastery (effect 61741) 30% chance to Avoid being Poisoned / Bleeding / Impaled", source: "TreeData/3_29/tree.lua (scan in b1c-mechanics-immunity.md; effect 61741)", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Shakari, Drek Apex Hunter (Ralakesh upgrade)", slot: pantheon, role: enables, target: self, text: "Shakari: 50% less Duration of Poisons on You, cannot be Poisoned while 3 or more Poisons are on you; Drek: Corrupted Blood cannot be inflicted on you if you have at least 5 Corrupted Blood Debuffs", source: "Data/Pantheons.lua:185-188,232; wiki cargo pantheon_souls Shakari / Ralakesh ordinal 2", pob: none}
makes_redundant:
  - {provider: "Bleeding immunity (flask, gear, mastery)", when: "all physical damage taken as elemental or chaos damage", why: "bleed deals physical damage over time, so taking all physical as another type is effectively bleed immunity", source: "poewiki Ailment rev 1673310"}
  - {provider: "Poison immunity and avoid chance", when: "Chaos Inoculation", why: "immunity to chaos damage makes poison harmless although it can still be inflicted", source: "poewiki Poison rev 1700788"}
conflicts:
  - {with: "Bleeding immunity text", effect: "does not cover Corrupted Blood; it needs Corrupted Blood cannot be inflicted on you, the flask suffix with Corrupted Blood, or Protection Mastery", source: "poewiki Corrupted Blood rev 1673502"}
  - {with: "Reactive flask counted as permanent in PoB", effect: "PoB shows BleedAvoidChance 100 and CorruptedBloodImmunity true for the reactive suffix whenever a flask is in use, although the game grants it only after the debuff landed (EK sample: Sealing flask gives 0 to 100)", source: "Modules/ModParser.lua:4889-4890,4914-4917; b1c-pob-flasks.md"}
conditions:
  - {text: "Sirus (Pinnacle Boss scenario): Die Beam physical beam always applies Corrupted Blood (negated by the jewel implicit or Protection Mastery); Hyper Beam Barrage gives five stacks. Wiki Recommendations: 'Immunity to corrupted blood and Shock greatly help.' Generator requirement: corrupted blood immunity REQUIRED for a Sirus-ready build (the expert reading of that wiki line; the wiki wording is 'greatly help')", source: "poewiki Sirus rev 1702453; poewiki Corrupted Blood rev 1673502"}
  - {text: "Other pinnacle bosses and Mapping: generator requirement for bleed, poison and corrupted blood immunity: no norm found. Map sources of corrupted blood exist (Corrupting monster mod, Essence of Greed) but that is a mechanic fact, not an expert requirement", source: "poewiki Corrupted Blood rev 1673502; b1c-mechanics-immunity.md"}
  - {text: "Corrupted blood stacks: Q'ura Cleave 2 (8 enraged), Dominus Cleave 2; only the 10 highest stacks deal damage", source: "poewiki Corrupted Blood rev 1673502"}
  - {text: "the reactive 'if used while Bleeding / Poisoned' suffixes are fired in the game by the Instilling flask enchants 'Used when you start Bleeding' and 'Used when you become Poisoned'; PoB has no parser line for 'Used when' (shown as 'Not supported in PoB yet'), so it counts the reactive suffix as always on while the slot is ticked", source: "Data/EnchantmentFlask.lua:24-25; Main.lua:120; b1c-item-flasks.md; poewiki Instilling_Orb rev 1683037"}
uptime:
  Mapping:
    value: pob
    config: {}
    reasoning: "permanent sources (equipment, corrupted implicit, mastery, skill while active) are always up; during-effect flasks follow the flask uptime; reactive flasks are not prevention; no norm found for how much of the map needs it"
    source: "Modules/CalcDefence.lua:1590,1620; Data/ModFlask.lua:216-219,232-238,248-250"
  Pinnacle Boss:
    value: model
    config: {}
    reasoning: "Sirus applies corrupted blood on a fixed beam, so only a permanent immunity (jewel implicit, Protection Mastery, boots variant) is safe; a utility flask 'during Effect' depends on the flask uptime; the reactive_flask_immunity_window model decides the rest"
    source: "poewiki Sirus rev 1702453; Data/ModFlask.lua:216-219,248-250"
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Bleeding (rev 1700575); https://www.poewiki.net/wiki/Poison (rev 1700788); https://www.poewiki.net/wiki/Corrupted_Blood (rev 1673502); https://www.poewiki.net/wiki/Ailment (rev 1673310)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Sirus (rev 1702453)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:1590,1620,3534-3566; Modules/ModParser.lua:4889-4917; Data/ModFlask.lua:216-250; Data/Pantheons.lua; TreeData/3_29/tree.lua (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-mechanics-immunity.md; tasks/reports/027-evidence/b1c-pob-flasks.md", kind: discovery, patch: "3.29"}
not_verified:
  - "exact line of the Steelskin AvoidBleed in Data/Skills/act_str.lua (inside block 11005-11100, about 11027)"
  - "Bone Armour, Immortal Call and other guard skills for bleed or corrupted blood immunity were not checked"
  - "Slayer Endless Hunger: Maxroll mentions it for bleeding, but the 3.29 node text found only 'Cannot be Stunned while Leeching' (node 34484); its other lines were not read"
  - "config var name of the enemy damage-over-time box and its default"
  - "live PoB parse of the unique, implicit and tree lines was not run line by line; they count as parsed because they are absent from the unparsed list in the evidence"
  - "how PoB evaluates the helmet armour versus evasion condition of the Armour and Evasion Mastery"
  - "wiki Immunity page attributes Cannot be Blinded / Maimed to Ralakesh while PoB Pantheons.lua:249-251 has them on the Garukhan group (not relevant to this mechanic, recorded as a disagreement)"
  - "tattoo avoid-bleed and avoid-poison names (TattooPassives.lua:3455, 4250; override type order not confirmed)"
open_questions:
  - "The wiki says 'greatly help' for corrupted blood immunity at Sirus; the generator treats it as required (brief). Does the user agree, or should it be a scored preference?"
  - "Should the generator add its own bleed damage estimate, since PoB computes none (PoB leaves bleed on you at chance 0)?"
```
