---
type: interaction
status: draft
pob_refs: [InspirationCharges, InspirationChargesMax, InspirationCharge, overrideInspirationCharges, SupportInspiration, ManaCost, ManaPerSecondCost]
source: "PoB 2.67.2 sup_str.lua:4604-4690, CalcPerform.lua:1006,1095,1129, CalcSetup.lua:38, Data/Misc.lua:97, ConfigOptions.lua:939-941; wiki Inspiration Support rev 1681590, Channelling skill rev 1647943; headless Worb.xml (task 027 batch 4b)"
last_confirmed_patch: "3.29.x"
---

Inspiration support gives the supported skill less mana cost (L20: 34% less, but the gem has its own x1.2 cost multiplier, so the net is about 21% less: Worb Winter Orb 10 -> 8) and a stack of Inspiration charges (max 5). Each charge is 5% more elemental damage and 8% increased critical strike chance (L20); all charges are lost after 800 mana (L20) has been spent on the supported skills. PoB does not track mana spent: it assumes the charge count is the maximum (5) unless you set the config box, so its damage is the best case.
The less mana cost is real and PoB counts it; it also slows mana-spent mechanics (Arcane Surge) because the counter runs on the final, lower cost.

Pipeline: [[Damage calculation#More and less]], [[Damage calculation#Critical strike]] - 5%/charge is its own more multiplier on elemental damage (not in the increased pool); the crit part is increased crit chance per charge

```interaction
id: inspiration-charges
mechanic: "Supported skills spend mana -> +1 Inspiration charge (max 5, 10 s, refreshed on each gain); all charges are lost after a total of 800 mana (L20; 122 at L1) is spent on upfront costs and effects of supported skills; per charge 5% more elemental damage and 8% increased critical strike chance (L20); supported skills 34% less mana cost (L20) with the gem's own x1.2 cost multiplier, net about 21% less"
family: charge
pipeline_step: ["Damage calculation#More and less", "Damage calculation#Critical strike"]
pipeline_why: "per charge the gem gives its own more elemental damage multiplier and increased crit chance; PoB multiplies both by the charge count it assumes (maximum, or the config override)"
target: self
related: [arcane-surge, mana-cost-efficiency, reservation-efficiency, skill-cost-from-es, channelling]
pob:
  measured: partial
  how: "Less mana cost: full (statMap sup_str.lua:4615-4626 'support_inspiration_mana_cost_+%_final' -> ManaCost MORE; level table L20 = -34, threshold 800, 5% elemental, 8% crit, manaMultiplier 20, sup_str.lua:4663). Charge count: NOT from mana spent. CalcSetup.lua:38 sets InspirationChargesMax BASE = characterConstants maximum_righteous_charges (Data/Misc.lua:97 = 5) for every build with or without the gem; CalcPerform.lua:1095 output.InspirationCharges = Override('InspirationCharges') or Max; CalcPerform.lua:1129 modDB.multipliers.InspirationCharge = that count; the gem's two mods read that multiplier (sup_str.lua:4615-4620). The 800-mana loss threshold ('lose_all_righteous_charges_on_mana_use_threshold'), the 10 s duration and the 'spend mana to gain a charge' rule have no code (grep of Modules/ and Classes/ for Inspiration: only the 6 lines above plus Calcs.lua:635 display and ConfigOptions.lua:939)"
  config:
    - {var: overrideInspirationCharges, default: "unset = maximum (5)", ref: "Modules/ConfigOptions.lua:939-941 (type countAllowZero, shown only when ifMult InspirationCharge is used; OVERRIDE gated on Condition Combat)", class: c}
  unparsed: []
model:
  proposed_kind: inspiration_charge_average
  inputs: {from_pob: [ManaCost, Speed (uses per second, divide by Repeats for Spell Echo)], from_scenario: []}
  params: {threshold_L20: 800, max_charges: 5, duration_s: 10}
  formula: "LABELLED MODEL (not verified in game). Uses per cycle n = ceil(800 / ManaCost); average charges over a continuous cycle = 5 - 15 / n (ramp 0,1,2,3,4 then 5 after each reset; assumes the charge is gained after the use it belongs to, order not documented); a gap > 10 s without a gain loses all charges. Worb with Inspiration L20: ManaCost 8 -> n = 100 -> 4.85 charges (97% of the maximum; one cycle = 100 ticks / 9.568 = 10.5 s). Fireball seed (ManaCost 37 with Inspiration in the group, Spell Echo Repeats 2): n = 22 -> 4.32 charges. A lower ManaCost makes n larger and the average closer to 5; wiki: 'lower mana costs result in better usage of Inspiration Charges'. DPS value by PoB (Worb, Inspiration L20, Winter Orb): 0 charges 1,343,497.5, 3 charges 1,575,001.5, 5 charges 1,733,757.7 TotalDPS (re-run 2026-10-26, output keys TotalDPS, InspirationCharges)"
  calibration: "no norm found (wiki gives only the 100-mana example: 'the first 5 casts will average at 50% of the gem's potential and then the next 3 at 100%', i.e. 8 casts per 800-mana cycle); formula is a labelled model, not verified in game"
providers:
  - {kind: support, name: "Inspiration", slot: any, role: applies, target: self, text: "L20: 34% less mana cost (x1.2 own cost multiplier), +1 charge per mana spend (max 5), 5% more elemental damage and 8% increased crit chance per charge, charges lost after 800 mana spent; supports any skill, but minions, totems, traps and mines cannot gain charges", source: "PoB Data/Skills/sup_str.lua:4604-4690; wiki Inspiration Support rev 1681590", pob: partial}
  - {kind: unique, name: "Bitterdream", slot: weapon, role: applies, target: self, text: "Socketed Gems are Supported by Level 15 Inspiration (local: only the gems socketed in this item)", source: "PoB Data/Uniques/mace.lua:325-335; ModCache.lua:21025 (ExtraSupport SupportInspiration level 15)", pob: full}
  - {kind: unique, name: "Replica Bitterdream", slot: weapon, role: applies, target: self, text: "Socketed Gems are Supported by Level 15 Inspiration (local to the item's sockets)", source: "PoB Data/Uniques/mace.lua:337-352; ModCache.lua:21025", pob: full}
  - {kind: mod, name: "Skills Socketed in your Helmet / Gloves / Boots are Supported by level 20 Inspiration", slot: any, role: applies, target: self, text: "level 20 Inspiration on the skills socketed in that slot; the item or mod that carries the line is not identified here", source: "PoB Data/ModCache.lua:20348 (Helmet), 20183 (Gloves), 20019 (Boots), ExtraSupport SupportInspiration level 20", pob: full}
  - {kind: mod, name: "+1 to Level of Socketed Gems / +3 to Level of all Critical Support Gems (Critical Mastery)", slot: any, role: scales, target: self, text: "gem level 25 breakpoint: 6% more elemental damage per charge (L20 = 5%, L25 = 6%; sup_str.lua:4663,4677)", source: "wiki Inspiration Support rev 1681590 ('breakpoint at gem level 25'); PoB sup_str.lua:4663,4673", pob: full}
makes_redundant:
  - {provider: "Inspiration in a group whose skill casts rarely or costs a lot of mana", when: "the group casts less than one use per 10 s, or ManaCost x uses reaches 800 within seconds", why: "all charges are lost after 10 s without a gain and after 800 mana; PoB still shows 5 charges", source: "wiki Inspiration Support rev 1681590 (duration, threshold); PoB CalcPerform.lua:1095"}
conflicts:
  - {with: "Eldritch Battery, Whispers of Infinity, Lifetap, Blood Magic (cost paid from ES / life)", effect: "no charges: paying a mana cost without spending mana does not grant charges (Eldritch Battery named; the others follow the same 'spent mana' rule, inferred); PoB still shows the maximum charges and the damage", source: "wiki Inspiration Support rev 1681590 (cites GGG forum thread 3247463, Jadian, 2022-02-23)"}
  - {with: "Arcane Surge support on the same skill (Worb Winter Orb)", effect: "Inspiration's lower cost lowers the mana spent per tick, so the 400-mana Arcane Surge threshold takes longer: Worb 10 -> 8 mana per tick, first proc after 4.18 s -> 5.23 s of channelling; with a 4 s buff the uptime falls from 95.7% to 76.5% (model, see arcane-surge). Model-weighted Worb TotalDPS: 1,326,117 without Inspiration vs 1,611,975 with it (+21.6%), against PoB's naive +29.0% (1,343,498 -> 1,733,758)", source: "headless Worb.xml probes (batch 4b); arcane-surge model"}
  - {with: "Reservation efficiency", effect: "none: the less mana cost does not affect mana reservation", source: "wiki Inspiration Support rev 1681590 ('It does not affect mana reservations')"}
conditions:
  - {text: "charges come from mana spent on upfront costs and effects of supported skills; the counter is shared between all Inspiration-supported skills; the skill that pushes the total over the threshold resets the counter to 0 and removes all charges; charges apply to every Inspiration-supported skill, even ones that spend no mana (Righteous Fire)", source: "wiki Inspiration Support rev 1681590"}
  - {text: "charges last 10 s; gaining a charge refreshes all of them; no gain for 10 s loses all", source: "wiki Inspiration Support rev 1681590"}
  - {text: "channelling skills pay their cost on starting and on every channelling tick, so each Winter Orb tick counts as mana spent (ticks follow cast time and cast speed)", source: "wiki Channelling skill rev 1647943 ('Costs are paid when beginning to channel, as well as on each channelling tick'); wiki Cost ('Channelling skills pay an upfront cost each channelling tick')"}
  - {text: "PoB ManaCost with Inspiration L20 added to the Worb Winter Orb group (Brine King left out): 10 -> 8, i.e. net about 21% less, not 34%, because the gem's manaMultiplier 20 raises the base first (see mana-cost-efficiency); ManaPerSecondCost 95.68 -> 76.544 (ManaCost x Speed 9.568, CalcOffence.lua:5921-5944); the charge count does not change cost (8 at 0, 3 and 5 charges)", source: "headless probe probe_insp.py, re-run 2026-10-26 (output keys ManaCost, ManaPerSecondCost); sup_str.lua:4663; vault Mana cost and cost efficiency note"}
  - {text: "version history: 3.25.0 less instead of reduced mana cost (also quality); 3.23.0 quality = reduced mana cost; 3.15.0 120% cost multiplier, damage per charge 3-5%; 3.8.0 introduced charges. No 3.26-3.29 row. PoB 3.29 values agree with the wiki (L20: -34%, 800, 5%, 8%)", source: "wiki Inspiration Support rev 1681590 version history; PoB sup_str.lua:4663"}
uptime:
  Mapping:       {value: model, config: {overrideInspirationCharges: "leave unset only if the model average (4.85 Worb) is close to 5; else set to the rounded model value"}, reasoning: "continuous channelling keeps 4.85 of 5 charges on average (model); PoB's maximum overstates by 3%", source: "model above; CalcPerform.lua:1095"}
  Pinnacle Boss: {value: model, config: {overrideInspirationCharges: "set 0-2 if the boss is hit rarely (>10 s gap) or the rotation spends 800 mana per few seconds"}, reasoning: "phases without channelling lose all charges after 10 s; PoB cannot see that", source: "wiki Inspiration Support rev 1681590; model"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Inspiration_Support (rev 1681590)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Channelling_skill (rev 1647943)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.pathofexile.com/forum/view-thread/3247463", kind: forum, patch: "3.17"}
  - {ref: "PoB Data/Skills/sup_str.lua:4604-4690; Modules/CalcPerform.lua:1006,1026,1095,1129; CalcSetup.lua:38; Data/Misc.lua:97; ConfigOptions.lua:939-941; CalcOffence.lua:5915-5944", kind: pob, patch: "3.29"}
not_verified:
  - "order of 'charge gained' vs 'mana counted' inside one use (affects the 4.85 average by up to 1 charge)"
  - "whether Whispers of Infinity / Lifetap / Blood Magic follow the Eldritch Battery rule for Inspiration (wiki names only Eldritch Battery)"
  - "whether the wiki's 'mana spent' counter uses the cost after rounding (ManaCost 8 vs 7.92)"
  - "whether the leftover above the 800 threshold carries into the next cycle"
  - "Winter Orb tick rate vs PoB Speed 9.568 (PoB assumes one cost payment per cast time; wiki says ticks follow cast time; tick interval of the skill itself not probed)"
  - "alternative providers beyond Bitterdream / Replica Bitterdream / the three slot lines: wiki cargo query for modifiers granting SupportInspiration failed (HTTP non-JSON answer); tree grep of TreeData/3_29/tree.lua found no Inspiration-support node; the item that carries the 'Skills Socketed in your Helmet/Gloves/Boots are Supported by level 20 Inspiration' line is not identified"
  - "Fireball seed numbers (ManaCost 37, Repeats 2, n = 22) come from the batch-4b researcher probe, not re-run here"
open_questions: []
```
