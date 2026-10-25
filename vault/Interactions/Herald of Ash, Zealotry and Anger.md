---
type: interaction
status: draft
pob_refs: [FireMin, FireMax, PhysicalDamageGainAsFire, hoaOverkill, conditionOnConsecratedGround, ManaReservedPercent, ManaReservedBase, TotalDPS, FullDPS, CritChance]
source: "poewiki Herald of Ash rev 1681840, Zealotry rev 1682036, Anger rev 1681684 (fetched 2026-10-26); PoB 2.67.2 Data/Skills/act_str.lua, act_int.lua, sup_str.lua, Modules/CalcOffence.lua, CalcPerform.lua, ConfigOptions.lua; skill-gem-analyst measured runs (gems L20/q20 added in memory, nothing saved)"
last_confirmed_patch: "3.29.x"
---

Three self-buffing gems: Anger gives you and nearby allies added fire damage to attacks and spells, Zealotry gives 15% more spell damage and 39% increased spell crit chance at L20 (plus a 10% chance to create Consecrated Ground on hitting a rare or unique), and Herald of Ash gives 20% of Physical Damage as extra Fire plus an overkill burn when you kill. Zealotry has no cast speed effect: neither PoB data (act_int.lua:21403-21464) nor wiki rev 1682036 lists one. Only skill-specific effects are written here; generic aura and reservation rules are batch 4, reservation appears only as PoB output numbers. Herald of Ash adds nothing to a build with no physical base damage, and Brutality removes the added fire of Anger and Herald of Ash on the supported skill.

Pipeline: [[Damage calculation#Flat damage]] - Anger is added damage scaled by the skill's damage effectiveness (Fireball L20 480%); [[Damage calculation#More and less]] - Zealotry's 15% more spell damage; [[Damage calculation#Critical strike]] - Zealotry adds increased crit CHANCE only; [[Damage calculation#Gain as extra]] - Herald of Ash converts only PHYSICAL base damage; [[Damage calculation#Damage over time]] - the overkill burn is its own DoT, not an ignite

Impact (a) EK: Herald of Ash and Anger = 0 (Brutality removes the added fire; the PoB +1.1% is a reservation-side artifact, not damage). Zealotry = +21.5% FullDPS in PoB (15% more spell damage on paper; the rest is not isolated) for 441 mana reserved (unreserved 107 -> -334): the sample is already at 91.1% reserved. Zealotry's crit chance is wasted on EK (CritChance already 100%, CoC). Consecrated Ground from Zealotry is not modelled by PoB. Impact (b) Fireball Elementalist: Anger = +25.6% on a fire-only Fireball (Bladefall run, same gem level) for 50% base reservation; Zealotry = +18% (Worb ratio) for the same reservation; Herald of Ash = 0 unless there is physical base spell damage. Anger + Zealotry together = 100% base reservation (batch 4). Goal arithmetic from a different build, order of magnitude only: 252k -> Anger alone 316k (x1.256) -> with Zealotry about 373k, not yet 500k.

```interaction
id: herald-ash-zealotry-anger
mechanic: "Anger: added Fire Damage to attacks and spells; Zealotry: 15% more Spell Damage and 39% increased Spell Critical Strike Chance (L20) plus 10% chance to create Consecrated Ground on hitting a Rare or Unique; Herald of Ash: 20% of Physical Damage as extra Fire (L20) and an overkill burn when you kill; Zealotry has no cast speed effect"
family: buff
pipeline_step: ["Damage calculation#Flat damage", "Damage calculation#More and less", "Damage calculation#Critical strike", "Damage calculation#Gain as extra", "Damage calculation#Damage over time"]
pipeline_why: "Anger FireMin/FireMax BASE is added damage (flat step), Zealotry is Damage MORE Spell plus CritChance INC Spell, Herald of Ash is PhysicalDamageGainAsFire (physical base only) and its burn is a separate FireDot"
target: self
related: [consecrated-ground, culling-strike, spell-projectile-supports]
pob:
  measured: partial
  how: "Anger FULL (Data/Skills/act_str.lua:380-391, GlobalEffect Aura buff, statMap FireMin/Max BASE with Spell/Attack keyword, baseEffectiveness 2.25, L20 row 441). Zealotry damage and crit FULL (act_int.lua:21409-21416 statMap Damage MORE Spell and CritChance INC Spell); the gem stat create_consecrated_ground_on_hit_%_vs_rare_or_unique_enemy (constantStat 10 at act_int.lua:21433) is in neither Data/SkillStatMap.lua nor any Modules/*.lua (grep of both returned nothing) and the item-text form is unparsed (parseMod n=-1). Herald of Ash buff FULL (act_str.lua:5733-5790: physical_damage_%_to_add_as_fire -> PhysicalDamageGainAsFire, GlobalEffect Buff); the burn is CONFIG ONLY: it needs hoaOverkill (ConfigOptions.lua:489-492, count, default 0, shown only when Herald of Ash is a skill, tooltip 'base Burning damage is equal to 25% of Overkill damage'); burn formula act_str.lua:5738-5740 (FireDot = hoaOverkill x (1 + hoaMoreBurn/100) x hoaOverkillPercent; L20 38% more burn; 1500/6000 = 25% of overkill per act_str.lua:5772); CalcOffence.lua:5841-5843 removes the global INC damage from the HoA burn (dotIsHeraldOfAsh), only burning-specific increases apply; the overkill value is a hand-set input and PoB does not derive it from enemy life or hit size. Reservation, PoB output only (Worb base with the gem added): Anger 44.64% (607 mana), Zealotry 44.64% (607 mana), Herald of Ash 22.32% (304 mana) from skillData.ManaReservedPercent / ManaReservedBase (CalcPerform.lua:2050-2065); gem data manaReservationPercent 50 / 50 / 25 at L20 (act_str.lua:441, act_int.lua:21464, act_str.lua:5800)"
  config:
    - {var: hoaOverkill, default: 0, ref: "Modules/ConfigOptions.lua:489-492", class: c}
    - {var: conditionOnConsecratedGround, default: false, ref: "Modules/ConfigOptions.lua:1148 (the only PoB consecrated ground input)", class: b}
  unparsed:
    - "Zealotry (gem line): You and nearby Non-Minion Allies have a 10% chance to create Consecrated Ground on Hitting a Rare or Unique Enemy (gem stat unmapped)"
model: null
providers:
  - {kind: gem, name: "Anger", slot: any, role: scales, target: self, text: "You and nearby allies deal x to y additional Fire Damage with Attacks / Spells (3.14.0: same amount for both); wiki L20 109-155, PoB at gem level 20 reads FireMin/Max 119-169 incl. quality; reservation 50% base at L20", source: "Data/Skills/act_str.lua:375-441; wiki Anger rev 1681684", pob: full}
  - {kind: gem, name: "Zealotry", slot: any, role: scales, target: self, text: "L20: 15% more Spell Damage, 39% increased Spell Critical Strike Chance, 10% chance to create Consecrated Ground on hitting a Rare or Unique; no cast speed; wiki: the stat applies to skills used by proxies only after the proxy has died (likely a bug), so totems, traps and mines are effectively excluded", source: "Data/Skills/act_int.lua:21403-21464; wiki Zealotry rev 1682036", pob: partial}
  - {kind: gem, name: "Herald of Ash", slot: any, role: scales, target: self, text: "L20: 20% of Physical Damage as extra Fire (3.25.0: 15% at L1 to 20% at L20, no longer more Spell Fire Damage); kills while active apply a burn to nearby enemies based on overkill damage (not an ignite)", source: "Data/Skills/act_str.lua:5733-5800; wiki Herald of Ash rev 1681840", pob: partial}
  - {kind: unique, name: "Watcher's Eye (Zealotry / Anger variants)", slot: Jewel, role: scales, target: self, text: "Zealotry variant makes consecrated ground increase damage taken (stacks with Bottled Faith); Anger variant: Always Scorch", source: "vault Consecrated ground note; item-analyst.md (WatchersEye.lua), not re-read this batch", pob: partial}
  - {kind: flask, name: "Bottled Faith", slot: Flask 1, role: scales, target: self, text: "consecrated ground source for the FR seed", source: "vault Seed unique pins note", pob: partial}
  - {kind: support, name: "Brutality", slot: any, role: blocks, target: self, text: "deal_no_elemental_damage on the supported skill: zeroes the extra fire of Anger and Herald of Ash (EK sample group: Increased Critical Strikes, Ethereal Knives, Brutality, Cast On Critical Strike, Cyclone)", source: "Data/Skills/sup_str.lua:791,808-812; CoC EK Assa.xml lines 126-132", pob: full}
makes_redundant:
  - {provider: "Herald of Ash (buff)", when: "the build has no physical base damage on the skill", why: "the extra fire is a percentage of physical damage: measured +HoA = identical TotalDPS on the Worb Fireball (68,349) and the Bladefall Fireball (45,141), exactly 0", source: "skill-gem-analyst PoB runs; Data/Skills/act_str.lua:5733-5790"}
conflicts:
  - {with: "Brutality", effect: "Brutality deletes the added fire of Anger and Herald of Ash on the supported skill; on EK both do nothing to the main skill", source: "Data/Skills/sup_str.lua:808-812; skill-gem-analyst EK run"}
  - {with: "Zealotry, Bottled Faith and Watcher's Eye consecrated ground", effect: "use the same ground; stack additively per the vault Consecrated ground note", source: "vault Consecrated ground note (via skill-gem-analyst)"}
  - {with: "Zealotry vs attack skills", effect: "the spell bonuses do not affect Cyclone (an attack)", source: "skill-gem-analyst reading of Data/Skills/act_int.lua:21409-21416"}
conditions:
  - {text: "Herald of Ash burn needs a KILL by a hit while the buff is up; it burns enemies near the dead one (radius 10), base duration 4 s; overkill must be above 0; a boss fight has no kill before the boss, so the burn lands on adds only; hits that leave enemies under 10% life and then kill through culling strike have no overkill damage", source: "Data/Skills/act_str.lua:5764,5771; wiki Herald of Ash rev 1681840"}
  - {text: "Zealotry consecrated ground: 10% per hit versus rare or unique enemies; wiki gives 8 seconds duration (3.9.0: lasting 8 seconds, Non-Minion)", source: "Data/Skills/act_int.lua:21433; wiki Zealotry rev 1682036"}
  - {text: "Herald of Ash burn: wiki mean overkill = half the damage of a hit that kills at random; the burn is affected by increased/more Burning Damage and damage over time multipliers", source: "wiki Herald of Ash rev 1681840"}
uptime:
  Mapping:
    value: always
    config: {hoaOverkill: "hand-set; Herald of Ash burn needs kills (partial), Zealotry consecrated ground high (rare/unique packs hit often)"}
    reasoning: "Anger, Zealotry and the Herald of Ash physical-as-fire buff are always on while reserved; the Herald of Ash burn is partial (needs kills, overkill is hand-set)"
    source: "Data/Skills/act_str.lua:380-391,5733-5790; Modules/ConfigOptions.lua:489-492"
  Pinnacle Boss:
    value: always
    config: {conditionOnConsecratedGround: "Zealotry consecrated ground: take the frequency from the vault Consecrated ground note (the boss is unique, 10% per hit); PoB does not count it"}
    reasoning: "the buffs stay up while reserved; the Herald of Ash burn is none on a boss (no kill before the end, adds only)"
    source: "Data/Skills/act_int.lua:21433; vault Consecrated ground note (via skill-gem-analyst)"
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Herald_of_Ash (rev 1681840)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Zealotry (rev 1682036)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Anger (rev 1681684)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Skills/act_str.lua:375-441,5733-5800; act_int.lua:21403-21464; sup_str.lua:791,808-812; Modules/CalcOffence.lua:5841-5843; Modules/CalcPerform.lua:2050-2065; Modules/ConfigOptions.lua:489-492,1148 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Herald of Ash version row 3.25.0; Anger version row 3.14.0; Zealotry version row 3.9.0", kind: patch_notes, patch: "3.29"}
not_verified:
  - "why Anger = 0 in the Worb Fireball run (FireMin sum showed 119 but AverageHit was unchanged; the build has all damage as Cold, ColdAvg 10,787 unchanged); likely a cold-only build with fire converted or blocked, not run to the end"
  - "the +1.1% on EK for Anger and Herald of Ash is identical for both (15,310,049 vs 15,136,639 base); the analyst's reading is a reservation artifact (both push reserved mana to 100%), cause not isolated"
  - "Zealotry +21.5% on EK (FullDPS 15,136,639 -> 18,386,206; EK TotalDPS 7.73M -> 9.38M) versus 15% more on paper: the remainder (aura effect scaling and the Low-Mana side effect) was not isolated"
  - "the 25% of overkill value and the mean overkill (wiki: half the killing hit) are model inputs; PoB has no source of overkill"
  - "Zealotry consecrated ground frequency per boss: no PoB data; wiki gives only 10% per hit and 8 s duration"
  - "the 0.893 factor between gem reservation percent and the PoB reservation output is the build's efficiency, not researched"
  - "Watcher's Eye lines were not re-read this batch"
  - "measured: EK Assa (reserved 91.1%, unreserved mana 107): +Zealotry reservation 100%, unreserved -334; +Anger / +HoA -334 / -113. Fireball ratios come from added groups on builds that are not Fireball builds (Worb: Fireball 68,349 -> +Zealotry 80,648 (+18.0%, crit 42.3 -> 44.25%), +Anger 68,349, +HoA 68,349; Bladefall: 45,141 -> +Anger 56,717 (+25.6%, FireAvg 6,326 -> 7,948), +HoA 45,141)"
open_questions:
  - "Zealotry cast speed: the brief assumed Zealotry gives cast speed, but PoB act_int.lua:21403-21464 and wiki rev 1682036 list none. Is there a source for a cast speed effect that is not in these two?"
  - "Anger = 0 in Worb is unexplained (see not_verified): does the user's Worb build convert all fire or block the added fire?"
```
