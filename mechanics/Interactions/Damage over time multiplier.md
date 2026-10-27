---
type: interaction
status: draft
pob_refs: [DotMultiplier, PhysicalDotMultiplier, FireDotMultiplier, ColdDotMultiplier, LightningDotMultiplier, ChaosDotMultiplier, DotMultiplierIsCritMultiplier, AilmentsAreNeverFromCrit, CritInPast8Sec, BleedDotMulti, PoisonDotMulti, IgniteDotMulti]
source: "poewiki Damage over time rev 1702687 (section Damage over time multiplier, fetched 2026-10-25), Receiving damage rev 1702582; PoB 2.67.2 Modules/CalcOffence.lua, CalcSetup.lua, CalcPerform.lua, ModParser.lua, Data/Misc.lua, Data/Uniques, TreeData/3_29/tree.lua (task 027)"
last_confirmed_patch: "3.29.x"
---

Damage over time multiplier ('DoT multi') is its own additive pool that scales ONLY damage over time: ignite, bleed, poison and DoT skills. It is not increased and not more, it does not touch hit damage, and it does not touch the hit-derived base of an ailment (that base is hit damage after conversion, see [[Conversion and gain as extra]]). Type lines (Physical, Fire, Cold, Chaos) scale only a DoT of that type, so poison uses Chaos DoT multi whatever its source damage was. Everyone has +50% for ailments from critical strikes. The order note [[Damage calculation]] (step Damage over time) holds the wiki quote and the PoB lines for the order; this note holds providers and traps.

Pipeline: [[Damage calculation#Damage over time]] - DoT multi is applied as (1 + multi/100) next to (1 + increased) x more in the damage-over-time step, after the ailment base is fixed from the hit; it never reaches the hit steps ([[Damage calculation#Critical strike]], [[Damage calculation#More and less]]), so a hit-only build gains nothing from it.

```interaction
id: damage-over-time-multiplier
mechanic: "Damage over Time Multiplier: all DoT multi lines add into one pool that multiplies only damage over time and ailment damage, separately from increased and more; type lines (Physical, Fire, Cold, Chaos) apply only to a DoT of that type (poison is always Chaos); characters get +50% (minions and monsters +30%) for ailments from critical strikes; it never scales hit damage or the hit-derived ailment base"
family: pipeline
target: self
related: [conversion-gain-as-extra, damage-type-can-ailment, shock, freeze]
pipeline_step: ["Damage calculation#Damage over time", "Damage calculation#Ailments from hits"]
pipeline_why: "Wiki Damage over time rev 1702687: 'DoT multi is a damage multiplier that only affects damage over time. Different sources of DoT multi are additive with each other, but are independent from other increases or modifiers to damage over time'; PoB multiplies base x (1 + inc) x more x (1 + DoT multi/100) x enemy taken multiplier (CalcOffence.lua:5847), and the ailment base comes from the hit first (Ailments from hits)"
pob:
  measured: full
  how: "DotMultiplier plus the type multiplier are summed and applied as (1 + sum/100): bleed (CalcOffence.lua:4531, + PhysicalDotMultiplier), poison (4832, + ChaosDotMultiplier), ignite (5149, + FireDotMultiplier), Decay (5725), burning ground (5762), generic DoT skills per type (5845, damageType..DotMultiplier incl. Cold and Lightning). A skill DotMultiplier override replaces the sum (Perfect Agony, 4185-4192). For ailments from crits a separate multiplier is built with the Condition CriticalStrike true (CritBleedDotMulti 4522-4527, CritPoisonDotMulti 4824-4827, CritIgniteDotMulti 5141-5144; skillCond set at 4196), which is where the base +50% lives (CalcSetup.lua:604, value 50 from Data/Misc.lua:90; minions 30 from CalcPerform.lua:1181, Data/Misc.lua:167). 'AilmentsAreNeverFromCrit' (Elemental Overload, ModParser.lua:2237) forces the non-crit multiplier (4520-4523). DotMultiplier and the typed DotMultiplier stats are read only inside ailment and DoT blocks (grep of CalcOffence.lua: the matches before line 4180 are BonusCritDotMultiplier, a different stat at 3046-3264; no read in the hit damage steps). Conditions 'if you've dealt a Critical Strike in the past 8 seconds' are set true whenever the skill has crit chance above 0 (CalcOffence.lua:3273-3275), so those lines count as always up"
  config: []
  unparsed: []
model: null
providers:
  - {kind: mod, name: "Base +50% DoT multi for ailments from critical strikes", slot: base, role: scales, target: self, text: "every character: +50% to Damage over Time Multiplier for Ailments from Critical Strikes (minions and monsters +30%)", source: "Data/Misc.lua:90,167; Modules/CalcSetup.lua:604; wiki Damage over time rev 1702687", pob: full}
  - {kind: keystone, name: "Perfect Agony", slot: tree, role: scales, target: self, text: "Damage over Time Multiplier for Ailments is equal to Critical Strike Multiplier; Critical Strikes do not deal extra Damage; Non-Critical Strikes cannot inflict Ailments", source: "TreeData/3_29/tree.lua:80922 (node 23407); Modules/ModParser.lua:2324; Modules/CalcOffence.lua:4185-4192", pob: full}
  - {kind: notable, name: "Acrimony", slot: tree, role: scales, target: self, text: "+15% to Damage over Time Multiplier", source: "TreeData/3_29/tree.lua:39701", pob: full}
  - {kind: mod, name: "Damage Over Time Multiplier (small passive)", slot: tree, role: scales, target: self, text: "+6% to Damage over Time Multiplier", source: "TreeData/3_29/tree.lua:39658-39661", pob: full}
  - {kind: unique, name: "Fleshrender", slot: Sword, role: scales, target: self, text: "+(20-40)% to Damage over Time Multiplier", source: "Data/Uniques/sword.lua:95-102", pob: full}
  - {kind: unique, name: "Skysunder", slot: Sword, role: scales, target: self, text: "+(20-40)% to Damage over Time Multiplier", source: "Data/Uniques/sword.lua:430-437", pob: full}
  - {kind: unique, name: "Eyes of the Greatwolf", slot: Amulet, role: scales, target: self, text: "+(12-18)% to Damage over Time Multiplier", variant: "variant 33 (Damage over Time Multiplier)", source: "Data/Uniques/amulet.lua:440-485", pob: full}
  - {kind: unique, name: "Qotra's Regulator", slot: Shield, role: scales, target: self, text: "+(40-60)% to Damage over Time Multiplier if you've dealt a Critical Strike in the past 8 seconds (PoB treats it as up whenever crit chance is above 0)", source: "Data/Uniques/shield.lua:1268-1275; Modules/CalcOffence.lua:3273-3275; Modules/ModParser.lua:1791", pob: full}
  - {kind: unique, name: "Cane of Unravelling", slot: Staff, role: scales, target: self, text: "+(40-55)% to Chaos Damage over Time Multiplier (variants 2-5): scales poison and chaos DoT only", variant: "variants 2-5", source: "Data/Uniques/staff.lua:168-180", pob: full}
  - {kind: unique, name: "The Bane of Hope", slot: Bow, role: scales, target: self, text: "+(28-35)% to Physical Damage over Time Multiplier: scales bleed and physical DoT only", source: "Data/Uniques/bow.lua:34-42", pob: full}
  - {kind: unique, name: "Blackflame", slot: Ring, role: scales, target: self, text: "+(8-12)% to Fire Damage over Time Multiplier: scales ignite and fire DoT only", source: "Data/Uniques/ring.lua:119-126", pob: full}
  - {kind: unique, name: "Rime Gaze", slot: Helmet, role: scales, target: self, text: "+(16-22)% (variants 4-5) or +50% (variant 6) to Cold Damage over Time Multiplier: dead for a hit-only cold build, because the wiki's table of damaging ailments lists only bleed, ignite and poison (chill and freeze deal no damage over time)", variant: "variants 4-6", source: "Data/Uniques/helmet.lua:728-740; wiki Damage over time rev 1702687 (type multi only for the DoT's own type)", pob: full}
makes_redundant: []
conflicts:
  - {with: "Elemental Overload (keystone)", effect: "Ailments never count as being from Critical Strikes: the +50% base for ailments from critical strikes (and the Perfect Agony link to crit multiplier) is never used, PoB takes the non-crit multiplier", source: "TreeData/3_29/tree.lua:39954 (node 22088); Modules/ModParser.lua:2237; wiki Damage over time rev 1702687"}
  - {with: "Perfect Agony (keystone)", effect: "Non-Critical Strikes cannot inflict Ailments: the build must crit almost every hit that is meant to apply the ailment", source: "TreeData/3_29/tree.lua:80922"}
  - {with: "hit-only skills with no ailment (Winter Orb style cold hits)", effect: "every DoT multi line is dead: nothing in the build deals damage over time", source: "Modules/CalcOffence.lua (DotMultiplier read only in ailment and DoT blocks)"}
conditions:
  - {text: "DoT multi only affects the actual damage type the DoT deals: poison scales with Chaos DoT multi only, never with Physical or Lightning DoT multi, even if the base damage was physical or lightning", source: "wiki Damage over time rev 1702687 'Damage over time multiplier'; PoB CalcOffence.lua:4832"}
  - {text: "Sources of DoT multi are additive with each other and independent of increased and more; the DoT multiplier of a typed line (Fire) adds to the generic line", source: "wiki Damage over time rev 1702687; PoB CalcOffence.lua:5149,5845"}
  - {text: "Damage over time does not hit: no crit, no double damage, no luck. Conditional hit modifiers (against Chilled, Hindered) cannot apply to it. Attack, spell and projectile damage modifiers do not scale it unless the skill says so", source: "wiki Damage over time rev 1702687 'Interactions' and 'Damage scaling'"}
  - {text: "Flat added damage does not apply directly to damage over time, only through the hit-derived base of ailments; conversion cannot convert DoT", source: "wiki Damage over time rev 1702687 'Damage scaling'"}
  - {text: "Version history: 3.0.0 damage over time reworked; 3.15.0 DoT Multiplier weapon prefixes became suffixes (item crafting only)", source: "wiki Damage over time rev 1702687 version history"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "a static multiplier on the DoT; only conditional lines (crit in past 8 s) need a condition, which PoB sets true for any build with crit chance above 0; whether the DoT itself is up on the target is the ailment's own uptime (ignite, bleed, poison notes)", source: "Modules/CalcOffence.lua:3273-3275"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same static mechanic. A boss changes the enemy side only: DoT is not mitigated by armour or evasion, resist and damage-taken still apply (DoT effective multiplier, CalcOffence.lua:5832)", source: "wiki Damage over time rev 1702687; Modules/CalcOffence.lua:5821-5832"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Damage_over_time (rev 1702687, fetched 2026-10-25), sections Damage over time multiplier, Interactions, Damage scaling, Version history (3.0.0, 3.15.0)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Receiving_damage (rev 1702582)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:3273-3275,4185-4196,4520-4531,4822-4832,5141-5149,5725,5845-5847; Modules/CalcSetup.lua:604; Modules/CalcPerform.lua:1181; Data/Misc.lua:90,167; Modules/ModParser.lua:740-744,1791,2237,2324 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "Data/Uniques/{sword,amulet,shield,staff,bow,ring,helmet}.lua; TreeData/3_29/tree.lua:39658-39701,39954,80922", kind: pob, patch: "3.29"}
not_verified:
  - "that the seeds (EK, Worb, FR) have a DoT-multi source: none was read; EK is hit-based with Impale and the Worb and FR damage is hits, so the likely answer is no use"
  - "whether the +30% minion and monster value (Data/Misc.lua:167) is used for minion ailments in PoB beyond the single CalcPerform.lua:1181 line"
  - "Acrimony and the 'Damage Over Time Multiplier' small passive: only the stat lines were read, not whether they sit in a cluster that needs a different path"
  - "unique stat ranges come from PoB item text; variants named in the provider lines were not matched to the wiki's current versions"
  - "burning ground and Decay multiplier lines (CalcOffence.lua:5725,5762) were read as code only, no wiki comparison"
open_questions:
  - "Should the generator treat DoT multi as dead (no value) for a build whose skills have no ailment or DoT, instead of reporting a PoB change of 0%?"
```
