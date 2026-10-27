---
type: interaction
status: draft
pob_refs: [ChaosInoculation, Life, ChaosDamageTaken, Condition:FullLife, Condition:LowLife, LowLifePercentage, StunThreshold, TotalEHP, ChaosMaximumHitTaken, ChaosDotEHP, LifeCostWarning, enemyIsBoss]
source: "poewiki Chaos Inoculation rev 1634768, Low life rev 1596639, Pain Attunement rev 1605415 (fetched 2026-10-26); PoB 2.67.2 ModParser.lua / CalcPerform.lua / CalcDefence.lua / Calcs.lua / ConfigOptions.lua / Data/ModCache.lua / TreeData 3_29; headless runs on EK, FR and the Fireball seed (scratchpad b3c/ci_fresh.py, ci_pa.py, ci_lifecost.py)"
last_confirmed_patch: "3.29.x"
---

Chaos Inoculation (CI) sets maximum Life to 1 and makes you immune to chaos damage. It is a pure defence switch: on EK, FR and the Fireball seed CombinedDPS and FullDPS are identical with and without it. Its value is a pool trade: you lose the Life pool and every Life modifier, you gain a chaos hit that can never kill you (chaos hits bypass energy shield, so without CI a chaos hit is paid from a Life pool of ~1300-1600). PoB shows the gain only where its enemy damage mix contains chaos: the Pinnacle preset does (6.8-9.2% of damage), the "None" (map) preset deals 100% physical, so there CI looks neutral or even negative. What PoB gets wrong or leaves out is listed at the end. Related: [[Skill cost from ES]] (FR pays all costs from ES; CI does not change them), [[Defences]] (ES, resistances, Effective HP), [[Receiving damage]] and [[Leech]] (life leech on a 1-Life pool was not checked).

Pipeline: [[Receiving damage#Immunity and avoidance]] - CI is a 'cannot take chaos damage' effect: PoB applies it as ChaosDamageTaken MORE -100, so the chaos taken-multiplier is 0 and the chaos maximum hit is infinite; the pool it removes is [[Receiving damage#Life]], which becomes 1.

How PoB applies it (read from source): the line parses to flag ChaosInoculation plus ChaosDamageTaken MORE -100 (Data/ModCache.lua:17646, Modules/ModParser.lua:2250-2253). CalcPerform.lua:82-86 then sets output.Life = 1 (skipping the base x increased x more computation) and Condition:FullLife = true; Condition:LowLife is never set by CI. Chaos resistance is not changed (the sheet shows 'Immune', BuildDisplayStats.lua:218) but the taken-multiplier is 0 (CalcDefence.lua:1925-1940), so resistance, penetration and reduction no longer matter. The stun threshold reads BASE Life only, 'Life before Chaos Inoculation' (CalcDefence.lua:2165-2167).

Measured (headless, in memory, nothing saved; each cell is a fresh engine; 'without CI' = node 11455 deallocated, so the Life nodes the seed already has stay; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle):

| Seed | scenario | Life | ES | TotalEHP | Physical max hit | Chaos max hit | Stun threshold | CombinedDPS |
|---|---|---|---|---|---|---|---|---|
| EK with CI | None | 1 | 5189 | 71911 | 7538 | infinite | 1267 | 14370752 |
| EK without CI | None | 1318 | 5189 | 49609 | 5760 | 922 | 1318 | 14370752 |
| EK with CI | Pinnacle | 1 | 5189 | 145259 | 7538 | infinite | 1267 | 15084434 |
| EK without CI | Pinnacle | 1318 | 5189 | 68837 | 5760 | 922 | 1318 | 15084434 |
| FR with CI | None | 1 | 17116 | 102318 | 38594 | infinite | 1317 | 194967 |
| FR without CI | None | 1594 | 17116 | 111841 | 42185 | 3163 | 1594 | 194967 |
| FR with CI | Pinnacle | 1 | 17116 | 273342 | 33307 | infinite | 1317 | 166643 |
| FR without CI | Pinnacle | 1594 | 17116 | 82184 | 36406 | 2729 | 1594 | 166643 |

- TotalEHP change from CI: EK +45.0% (None) and +111.0% (Pinnacle); FR -8.5% (None) and +232.6% (Pinnacle). Hits to kill (TotalNumberOfHits) EK 38.3 -> 55.6 (None), 7.0 -> 14.7 (Pinnacle); FR 86.4 -> 79.1 (None), 8.3 -> 27.7 (Pinnacle).
- Why None differs: the enemy damage the EHP uses at None is 100% physical (PhysicalEnemyDamage 1294, ChaosEnemyDamage 0 on EK and FR); at Pinnacle the total is 9860 with chaos 896 (EK) and 665.9 (FR). CI can only help against a chaos share, and it costs the Life pool against everything else; ES is 5189 / 17116 so the trade depends on how large the ES is compared with the lost Life.
- The physical max hit rises on EK (5760 -> 7538, ES beats the 1318 Life) and falls on FR (36406 -> 33307, Pinnacle): the seed's own Life nodes are lost on FR (Life increased 21% from Written in Blood 10%, Life and Energy Shield 5%, Watcher's Eye 6%).
- Conditions that flip: Condition:FullLife only. A scan of the player modDB for mods gated on LowLife / FullLife found none on EK or FR, so nothing else changes on the seeds. DPS is therefore unchanged.
- Costs: FR ESCost 6, ESPerSecondCost 45.1 with and without CI (CI does not change cost routing).
- Fireball seed (NOT VIABLE, keystone only, path cost not included; the seed has no CI): without CI Life 2333, ES 1394, TotalEHP 7806 (None) / 12065 (Pinnacle), chaos max hit 3681; with CI Life 1, TotalEHP 2350 / 4412 (-69.9% / -63.4%), CombinedDPS 390510 / 285468 unchanged, stun threshold 3030 -> 2038 (the 992 difference equals 2333 Life minus 1341 base Life, i.e. the seed's +74% Life increase; the common 697 was not decomposed). A low-ES build loses EHP with CI at both presets.

PoB vs the wiki (conflicts kept visible):
- Pain Attunement / low-life effects: the wiki says low life never takes effect with CI (1 Life counts as full life), except with Coward's Legacy (Low life rev 1596639, Chaos Inoculation rev 1634768). PoB agrees by default: Fireball seed with CI and Pain Attunement (node 31703) CombinedDPS 285468.27 = without the node. But PoB derives Low Life from life reservation in CalcPerform.lua:570: with CI, Life 1, the line 'Reserves 1% of Life' reserves ceil(1 x 1%) = 1 and PoB sets LowLife while FullLife stays true: Pain Attunement then adds +26.5% (CombinedDPS 361063.49). The wiki says a CI build cannot cast or reserve with Life at all (Blood Magic section), so that number would be a phantom.
- Life cost: with CI a skill that costs Life shows LifeCost 78 against Life 1 and raises LifeCostWarning (Calcs.lua:407-421, Build.lua:2022-2030), measured on the Fireball seed with the custom line 'Skills Cost Life instead of Mana'. The warning is shown but DPS is unchanged.
- Stun threshold: the wiki says Life increases still count for the stun and ailment threshold because they apply before CI; PoB reads BASE Life only (CalcDefence.lua:2165-2167): EK 1267 instead of 1318 (-3.9%), FR 1317 instead of 1594 (-17.4%). PoB has no ailment threshold on the player (only StunThreshold).
- Flat Life regeneration: EK shows LifeRegenRecovery 116 with Life 1 (Stone Golem flat regen, not capped to the pool).

```interaction
id: chaos-inoculation
mechanic: "Maximum Life becomes 1 and you are immune to Chaos Damage; counts as full life, never low life (wiki); chaos resistance and penetration no longer matter; stun and ailment thresholds use the Life you would have had (wiki); Life reservation and Life costs become unusable (wiki)"
family: defence
target: self
related: [skill-cost-from-es, defences, receiving-damage, max-res-equalise]
pipeline_step: ["Receiving damage#Immunity and avoidance", "Receiving damage#Life"]
pipeline_why: "CI removes the Life pool (Life = 1) and cancels chaos hits through ChaosDamageTaken MORE -100, so the chaos taken-multiplier is 0 and the chaos max hit is infinite; chaos normally bypasses ES, so this is what lets an ES pool be the whole defence; the Life pool step then only has 1 Life behind it."
pob:
  measured: full
  how: "ModParser.lua:2250-2253 (flag ChaosInoculation + ChaosDamageTaken MORE -100), Data/ModCache.lua:17646; CalcPerform.lua:82-86 sets output.Life = 1 and Condition:FullLife = true; chaos taken-multiplier 0 via CalcDefence.lua:1925-1940; stun threshold from BASE Life CalcDefence.lua:2165-2167; BuildDisplayStats.lua:218 prints 'Immune'. Measured headless on EK and FR (CI node 11455 on/off, enemyIsBoss None and Pinnacle) and on the Fireball seed (keystone only, path cost not included): DPS unchanged; TotalEHP EK +45.0% None / +111.0% Pinnacle, FR -8.5% None / +232.6% Pinnacle; chaos max hit infinite (EK 922, FR 2729-3163 without CI). Not modelled: low life stays false unless Life is reserved (then PoB sets LowLife with CI, CalcPerform.lua:570), no ailment threshold on the player, Life increase ignored in the stun threshold, flat Life regen not capped to 1 Life."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086; decides the chaos share of the enemy damage the EHP uses (None: 0 chaos on EK and FR; Pinnacle: 665.9-896 of 9860)", class: b}
    - {var: conditionLowLife, default: false, ref: "Modules/ConfigOptions.lua:177 (a tick forces Condition:LowLife even with CI; by code, not measured)", class: c}
    - {var: conditionFullLife, default: false, ref: "Modules/ConfigOptions.lua:174 (not needed with CI: CalcPerform.lua:86 sets it)", class: c}
  unparsed:
    - "Midnight Bargain and Replica Midnight Bargain: 'Cannot be used with Chaos Inoculation' (Data/Uniques/wand.lua:155, 176); Data/ModCache.lua:14596-14597 has no mod for it, so PoB does not enforce the restriction"
model: null
providers:
  - {kind: keystone, name: "Chaos Inoculation 11455", slot: tree, role: enables, target: self, text: "Maximum Life becomes 1, Immune to Chaos Damage (seeds EK and FR allocate it)", source: "TreeData/3_29/tree.lua:74126-74130; Data/ModCache.lua:17646; Modules/ModParser.lua:2250-2253", pob: full}
  - {kind: tattoo, name: "Chaos Inoculation tattoo (Hinekora keystone tattoo)", slot: tree, role: enables, target: self, text: "Maximum Life becomes 1, Immune to Chaos Damage; Limited to 1 Keystone Tattoo", source: "Data/TattooPassives.lua:327-342", pob: full}
  - {kind: unique, name: "Impossible Escape (Viridian Jewel)", slot: jewel, role: enables, target: self, text: "Passive Skills in radius of Chaos Inoculation can be Allocated without being connected to your tree (path-free CI); PoB generates a CI variant", source: "Data/Uniques/Special/Generated.lua:639-645; Data/ModCache.lua:18515", pob: full}
  - {kind: keystone, name: "Zealot's Oath 63425", slot: tree, role: sustains, target: self, text: "Life Regeneration is applied to Energy Shield instead (wiki lists it as a CI partner); PoB moves flat and percent regen to ES", source: "Modules/CalcDefence.lua:1267-1277; Modules/ModParser.lua:2255; wiki Chaos Inoculation rev 1634768", pob: full}
  - {kind: unique, name: "Whispers of Infinity", slot: amulet, role: sustains, target: self, text: "Skills Cost Energy Shield instead of Mana or Life; FR wears it with CI: ESCost 6, 45.1 ES/s, identical with and without CI", source: "vault Skill cost from ES; Modules/CalcOffence.lua:1763-1790; headless FR", pob: full}
  - {kind: keystone, name: "Pain Attunement 31703", slot: tree, role: blocks, target: self, text: "30% more Spell Damage when on Low Life: dead with CI (Low Life never true) unless Life is reserved in PoB or Coward's Legacy is worn in the game", source: "TreeData/3_29/tree.lua:62454-62458; Data/ModCache.lua:8399; wiki Low life rev 1596639; headless Fireball seed", pob: full}
  - {kind: unique, name: "Coward's Legacy", slot: belt, role: abuses, target: self, text: "You count as on Low Life while you are Cursed with Vulnerability: the only way to get Low Life with CI (wiki); PoB flags Condition:LowLife only while AffectedByVulnerability, FullLife stays true", source: "Data/Uniques/belt.lua:189-197; Modules/ModParser.lua:4133; Data/ModCache.lua:22840; wiki Low life rev 1596639", pob: partial}
  - {kind: unique, name: "Midnight Bargain / Replica Midnight Bargain", slot: wand, role: blocks, target: self, text: "Cannot be used with Chaos Inoculation; Reserves 30% of Life (PoB parses the reservation, not the restriction)", source: "Data/Uniques/wand.lua:144-157, 166-178; Data/ModCache.lua:14596-14597, 19769", pob: partial}
  - {kind: keystone, name: "Blood Magic / Lifetap Support / Arrogance Support", slot: any, role: blocks, target: self, text: "Life costs and Life reservation: the wiki says affected skills cannot be cast with CI; PoB shows LifeCostWarning (LifeCost 78 vs Life 1) but keeps DPS", source: "wiki Chaos Inoculation rev 1634768 (Blood Magic section); Modules/Calcs.lua:407-421; Modules/Build.lua:2022-2030; headless Fireball seed", pob: partial}
  - {kind: support, name: "Damage on Full Life Support", slot: any, role: abuses, target: self, text: "attacks only: more damage while on full life (34% at gem level 20); always on with Chaos Inoculation, which PoB treats as full life by itself", source: "PoB Data/Skills/sup_str.lua:1707 (skill, requires Attack), :1718 (Damage MORE, condition FullLife), :1747 (level 20 value 34); Modules/CalcPerform.lua:84-86 (CI sets FullLife); Modules/ConfigOptions.lua:175 (conditionFullLife)", pob: full, payoff_of: [conditionFullLife]}
makes_redundant:
  - {provider: "Chaos resistance (gear, tree, jewels) and chaos resistance penetration or reduction", when: "CI allocated", why: "the chaos taken-multiplier is 0 (PoB) / chaos damage is immune (wiki: penetration and reduction have no effect); EK's Ralakesh's Impatience +17 chaos res (Item:26) and FR's Withering Presence +60 chaos res (Tree:25309, node 44324) add nothing; Withering Presence's 15% more Chaos Damage and Withered stay useful", source: "Modules/CalcDefence.lua:1925-1940; headless EK/FR chaosRes sources; TreeData/3_29/tree.lua:44324-44334; wiki Chaos Inoculation rev 1634768"}
  - {provider: "Maximum Life nodes and mods (increased, flat, Strength-to-Life)", when: "CI allocated", why: "Life is set to 1 and skips the increased/more computation (CalcPerform.lua:84-85); PoB's stun threshold reads BASE Life only, so even the stun use of increased Life is not counted (wiki: it still counts in the game); FR has 21% increased Life (Written in Blood, Life and Energy Shield, Watcher's Eye) and EK 4% that CI wastes", source: "Modules/CalcPerform.lua:84-85; Modules/CalcDefence.lua:2165-2167; headless FR/EK lifeInc sources; wiki Chaos Inoculation rev 1634768"}
  - {provider: "Flat Life regeneration, Life flasks, Life reservation relief", when: "CI allocated", why: "the pool is 1 Life; PoB still prints LifeRegenRecovery 116 on EK (Stone Golem) with Life 1, so the displayed regen overstates the value", source: "headless EK Life regen sources and output; Modules/CalcDefence.lua:1255-1285"}
conflicts:
  - {with: "Pain Attunement and other Low Life effects", effect: "never active with CI in the game (1 Life = full life); in PoB also inactive unless Life is reserved: 'Reserves 1% of Life' gave LowLife true and +26.5% CombinedDPS on the Fireball seed (285468 -> 361063), a phantom against the wiki", source: "wiki Low life rev 1596639; wiki Pain Attunement rev 1605415; Modules/CalcPerform.lua:562-571; headless Fireball seed"}
  - {with: "Life costs, Blood Magic, Lifetap Support, Arrogance Support, Life reservation", effect: "wiki: such skills cannot be cast; PoB: LifeCostWarning only", source: "wiki Chaos Inoculation rev 1634768; Modules/Build.lua:2022-2030"}
  - {with: "Midnight Bargain", effect: "wiki-style restriction 'Cannot be used with Chaos Inoculation' is not enforced by PoB", source: "Data/Uniques/wand.lua:155; Data/ModCache.lua:14596"}
  - {with: "Skin of the Lords", effect: "PoB leaves CI out of the generated Skin of the Lords keystone variants ('to prevent infinite loop'), so that route to CI cannot be modelled; Impossible Escape does list it", source: "Data/Uniques/Special/Generated.lua:606-609, 639-645"}
conditions:
  - {text: "CI counts as Full Life always (1 of 1) and never as Low Life (50% or less of maximum Life) except with Coward's Legacy; PoB sets Condition:FullLife (CalcPerform.lua:85-86) and sets LowLife only from reserved Life or config", source: "wiki Chaos Inoculation rev 1634768, Low life rev 1596639; Modules/CalcPerform.lua:77-86, 570-571"}
  - {text: "stun and elemental ailment chance and duration use maximum Life before CI, including increased Life modifiers (wiki citing an old forum thread); PoB's StunThreshold uses BASE Life only and has no player ailment threshold", source: "wiki Chaos Inoculation rev 1634768; Modules/CalcDefence.lua:2165-2167"}
  - {text: "chaos damage cannot inflict poison on a CI character, physical hits still can", source: "wiki Chaos Inoculation rev 1634768"}
  - {text: "CI shows a benefit only when the enemy deals chaos damage: PoB's EHP enemy mix has chaos 0 at None and 6.8-9.2% at Pinnacle (EK 896 and FR 665.9 of 9860)", source: "headless EK/FR/Fireball output (ChaosEnemyDamage, totalEnemyDamageIn); Modules/CalcDefence.lua:1735-1812"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (env.enemyLevel 85 in the headless run)"}, reasoning: "permanent while allocated; PoB's None preset has no chaos in the enemy damage, so the EHP gain is only the ES-vs-Life pool swap: EK +45.0% (49609 -> 71911), FR -8.5% (111841 -> 102318), Fireball seed -69.9%; real map monsters that deal chaos hits or chaos damage over time are not in this number (not verified)", source: "headless EK/FR/Fireball seed; Modules/CalcDefence.lua:1735-1812"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; env.enemyLevel 84 in the headless run)"}, reasoning: "use PoB's TotalEHP and max hits: EK +111.0% (68837 -> 145259), FR +232.6% (82184 -> 273342), Fireball seed -63.4%; chaos max hit infinite versus 922 (EK) and 2729 (FR) without CI; DPS unchanged", source: "headless EK/FR/Fireball seed"}
seeds: [EK, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Chaos_Inoculation (rev 1634768; last version-history row 3.14.1)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Low_life (rev 1596639)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Pain_Attunement (rev 1605415)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/ModParser.lua:2250-2255, 4133; Modules/CalcPerform.lua:77-86, 562-571; Modules/CalcDefence.lua:1255-1285, 1735-1812, 1925-1940, 2165-2167; Modules/Calcs.lua:407-421; Modules/Build.lua:2022-2030; Modules/BuildDisplayStats.lua:218; Modules/ConfigOptions.lua:174, 177, 2086; Data/ModCache.lua:8399, 14596-14597, 17646, 18515, 22840; Data/TattooPassives.lua:327-342; Data/Uniques/wand.lua:144-178; Data/Uniques/belt.lua:189-197; Data/Uniques/Special/Generated.lua:606-609, 639-645; TreeData/3_29/tree.lua:44324-44334, 62454-62458, 74126-74130", kind: pob, patch: "3.29"}
  - {ref: "headless runs EK, FR, Fireball seed (scratchpad b3c/ci_fresh.py, ci_pa.py, ci_lifecost.py; evidence b3c/pob-coverage-auditor-A.md)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether the game still applies increased Maximum Life to the stun and ailment threshold under CI: the wiki cites an early forum thread; the page's last version-history row is 3.14.1"
  - "whether Life reservation under CI makes the character Low Life in the game: the wiki says Low Life never takes effect with CI except Coward's Legacy and that Life-reserving skills cannot be cast; PoB sets LowLife from a reservation as small as 1% (measured on the Fireball seed)"
  - "chaos damage share of real map monsters (hits and damage over time): PoB's None preset has 0 chaos, so the Mapping EHP change of CI is not a prediction for maps"
  - "ChaosDotEHP is infinite with CI in PoB (null in the output); whether every chaos damage over time source in the game is blocked was not checked beyond the wiki sentence 'immune to chaos damage'"
  - "wiki-listed CI partners Ghost Reaver, Divine Shield, Ghost Dance, Wicked Ward were not checked in PoB (CalcPerform.lua:906 touches Ghost Reaver only for leech on full life)"
  - "life leech and Life recovery effects on a 1-Life pool, and CI-only Life flask rules, were not checked (see [[Leech]])"
  - "the Chaos Inoculation tattoo and Impossible Escape routes were read from data files only; allocation in PoB with a hash override was not run"
  - "Coward's Legacy needs the Vulnerability curse on yourself; PoB's flag condition AffectedByVulnerability was read, the combined CI + Coward's Legacy output was not run"
  - "ConfigOptions conditionLowLife with CI forces Condition:LowLife by code reading (ConfigOptions.lua:177-178); not measured"
  - "enemy level 85 (None) and 84 (Pinnacle) are env.enemyLevel from the headless run; why None is one level higher was not traced"
open_questions:
  - "Should the generator treat CI as a pool-choice decision made early (and then drop Life nodes and gear, chaos resistance and the Life-based rules), or keep increased Life for the stun threshold the wiki describes?"
  - "Should the audit reject a CI + Life reservation + Pain Attunement build as a phantom of PoB's Low Life rule?"
```
