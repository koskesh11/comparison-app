---
type: interaction
status: draft
pob_refs: [DamageTakenFromManaBeforeLife, sharedMindOverMatter, ManaUnreserved, PhysicalMaximumHitTaken, TotalEHP]
source: "poewiki Mana before Life rev 1700557, Mind Over Matter rev 1492420, Energy shield rev 1673450; PoB 2.67.2 CalcDefence.lua, ModParser.lua, TreeData/3_29/tree.lua, Data/Uniques, Data/TattooPassives.lua; b1-tree-ascendancy-analyst.md, b1-pob-coverage-auditor.md M2 (task 027 batch 1)"
last_confirmed_patch: "3.29.x"
---

Mind over Matter (keystone, 40% since 3.19.0, wiki rev 1492420) makes mana pay a share of the damage left after energy shield, hits and damage over time, capped at 100% in total; if mana runs out the rest goes to life. PoB counts it fully, but with the whole unreserved mana pool (not the current mana), so it is a snapshot like the Guard gap, and reservations shrink it. It does not touch ailment or stun thresholds, and the same mana pays the skill costs.
Pipeline: [[Receiving damage#Mana before life]] - mana is taken after energy shield and before life (PoB order aegis, ward, ES, MoM, life, CalcDefence.lua:282-345); it enlarges the hit pool in [[Defences#Effective HP]].
Impact EK: the EK build has Life 1 with Chaos Inoculation and PoB shows no pool gain with the keystone (M2: max hits and TotalEHP identical, reason not looked up), so no measured value for EK. Impact Fireball: arithmetic only (formula CalcDefence.lua:2352-2356, no PoB run): Life 3,000 and 40% needs 2,000 unreserved mana for +2,000 pool; with ES 1,100 the hit capacity before mitigation is 6,100 (4,100 without); with only 1,000 unreserved mana it is 5,100. The 7,000 physical max hit goal needs the keystone, at least 2,000 unreserved mana and mitigation on top, and competes with the Fireball mana cost.

```interaction
id: mind-over-matter
mechanic: "A share of the damage taken (after energy shield, hits and DoT) is taken from mana before life, summed over sources and capped at 100%; the Mind Over Matter keystone gives 40%"
family: defence
pipeline_step: ["Receiving damage#Mana before life", "Defences#Effective HP"]
pipeline_why: "mana pays its share of the damage left after energy shield (wiki: damage taken to ES has no interaction with this stat) and before life, so it enlarges the hit pool; it does not change ailment or stun thresholds"
target: self
related: [energy-shield-hybrid, recovery, skill-cost-from-es]
pob:
  measured: full
  how: "sharedMindOverMatter = min(sum DamageTakenFromManaBeforeLife, 100) CalcDefence.lua:2350; per-type variants capped at 100 minus shared :2391; pool = life + min(unreserved mana, life/(1-MoM) - life) via calcMoMEBPool using output.ManaUnreserved :2351-2358; applied in the hit simulation after ES :313-345; max hit and EHP use the pool :2364-2420, 3476, 3718; parse ModParser.lua:414-416, 4722-4723. No config box gates it (grep MoM|ManaBeforeLife in ConfigOptions.lua, CalcPerform.lua, CalcSetup.lua returned nothing)"
  config: []
  unparsed:
    - "The Aylardex: 1% of Damage is taken from Mana before Life per Power Charge (parse not checked)"
model: null
providers:
  - {kind: keystone, name: "Mind Over Matter 34098", slot: tree, role: applies, target: self, text: "40% of Damage is taken from Mana before Life (7 points from the Witch start by raw tree adjacency, not PassiveSpec node.path)", source: "TreeData/3_29/tree.lua:40251-40262; wiki Mind Over Matter rev 1492420", pob: full}
  - {kind: tattoo, name: "Tattoo of Mind Over Matter", slot: tree, role: applies, target: self, text: "keystone tattoo, same 40%; Limited to 1 Keystone Tattoo", source: "Data/TattooPassives.lua:1743-1756", pob: none}
  - {kind: ascendancy, name: "Divine Guidance 922 (Hierophant)", slot: tree, role: applies, target: self, text: "30% increased maximum Mana; 10% of Damage is taken from Mana before Life; Transfiguration of Mind", source: "TreeData/3_29/tree.lua:15895-15910", pob: full}
  - {kind: ascendancy, name: "Ascendant: Hierophant option 42144", slot: tree, role: applies, target: self, text: "25% increased maximum Mana; 8% of Damage is taken from Mana before Life", source: "TreeData/3_29/tree.lua:17880-17895", pob: full}
  - {kind: unique, name: "The Ivory Tower (Saint's Hauberk)", slot: body, role: applies, target: self, text: "Chaos Damage is taken from Mana before Life (chaos only)", source: "Data/Uniques/body.lua:1056; ModParser.lua:4722; wiki Energy shield rev 1673450", pob: full}
  - {kind: unique, name: "Mind of the Council (Harlequin Mask)", slot: helmet, role: applies, target: self, text: "30% of Lightning Damage is taken from Mana before Life", source: "Data/Uniques/helmet.lua:1636; ModParser.lua:415; wiki Mana before Life rev 1700557", pob: full}
  - {kind: foulborn, name: "Mind of the Council (Harlequin Mask)", slot: helmet, role: applies, target: self, text: "30% of Physical Damage is taken from Mana before Life", source: "Data/ModFoulborn.lua:296; ModParser.lua:4723; wiki Mana before Life rev 1700557", pob: full, variant: "replaces: 30% of Lightning Damage is taken from Mana before Life"}
  - {kind: unique, name: "The Aylardex", slot: amulet, role: scales, target: self, text: "1% of Damage is taken from Mana before Life per Power Charge", source: "Data/Uniques/amulet.lua:193", pob: partial}
  - {kind: mod, name: "Delve body armour mod", slot: body, role: applies, target: self, text: "(5-10)% of Damage is taken from Mana before Life (listed as legacy-only on the wiki)", source: "Data/ModJewel.lua:376-377; wiki Mana before Life rev 1700557", pob: full}
  - {kind: mod, name: "Veiled / crafted while Focused mods", slot: any, role: applies, target: self, text: "(18-22)% / (11-15)% of Damage is taken from Mana before Life while Focused (slot not read)", source: "Data/ModVeiled.lua:149; Data/ModMaster.lua:612", pob: none}
makes_redundant: []
conflicts:
  - {with: "Eldritch Battery 56075", effect: "makes Mind Over Matter take from energy shield first and removes the ES stun avoidance (Eldritch Battery is batch 4)", source: "TreeData/3_29/tree.lua:67095; wiki Energy shield rev 1673450"}
  - {with: "Chaos Inoculation 11455", effect: "life is 1, so a 40% share is taken from mana while the rest is lethal; forbidden by the Fireball seed; in the EK measurement (Life 1) PoB shows no pool gain", source: "b1-pob-coverage-auditor.md M2; b1-tree-ascendancy-analyst.md"}
  - {with: "Mana reservation", effect: "PoB uses ManaUnreserved, so reserved mana does not count toward the pool", source: "Modules/CalcDefence.lua:2351"}
  - {with: "Sources above 100% in total", effect: "the share is capped at 100%, extra sources do nothing", source: "Modules/CalcDefence.lua:2350; wiki Mana before Life rev 1700557"}
conditions:
  - {text: "needs mana above 0 when hit; mana recovery is needed so rapid hits or DoT do not drain the pool and block skill use", source: "wiki Mana before Life rev 1700557"}
  - {text: "unreserved mana must be at least k/(1-k) of unreserved life: 66.7% at 40%, 100% at 50%", source: "wiki Mana before Life rev 1700557 table"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "keystone without a condition; effective only while current mana is above 0", source: "TreeData/3_29/tree.lua:40251-40262; wiki Mana before Life rev 1700557"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "the pool is drained by every hit and by skill costs (Fireball spends the same pool) while PoB uses the full unreserved mana for max hit and EHP, so the number is a snapshot", source: "Modules/CalcDefence.lua:2351"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Mana_before_Life (rev 1700557)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Mind_Over_Matter (rev 1492420; 3.19.0 30 to 40%, 3.0.0 applies to DoT)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Energy_shield (rev 1673450)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:282-345,2350-2420,3476,3718; Modules/ModParser.lua:414-416,4722-4723 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "b1-pob-coverage-auditor.md M2: Worb (Life 4,306, ES 2,318, Mana 1,359) with the 40% line as a config custom mod (node 34098 cannot be allocated headless): Phys 16,310 to 16,645 (+335), ele 47,619 to 48,661 (+1,042), Chaos 16,866 to 17,434 (+568), TotalEHP 76,837 to 78,443 (+1,606); EK identical (sharedMindOverMatter 40, no pool gain)", kind: pob, patch: "3.29"}
not_verified:
  - "Current-mana behaviour in a fight: PoB uses the whole unreserved mana pool with no cost drain (from CalcDefence.lua:2351 only, no PoB run)"
  - "Why PoB shows no gain with Chaos Inoculation (EK, Life 1); reason not looked up"
  - "Neither measured build is the Fireball one; the Fireball numbers are arithmetic, not a PoB run"
  - "Slots of the Veiled and Master mods, the tattoo parse, the per Power Charge parse"
  - "Whether PoB TotalEHP over-credits Mind Over Matter when mana is also the skill resource (design of the EHP, not tested)"
  - "Keystone distance 7 is raw tree adjacency, not PassiveSpec node.path; the EK (Assassin) start is far from the keystone (wiki: Witch/Templar 7, Shadow 16) and whether the EK build has any mana share is not read"
  - "Cloak of Defiance lost its 10% line in 3.19.0 (wiki rev 1700557) while PoB Data/Uniques/body.lua:1214 still has it in variants 1, 3 and 4; not listed as a provider"
open_questions:
  - "Fireball seed: how much unreserved mana should the generator assume next to the skill cost, given PoB's snapshot of the full pool?"
  - "No Fireball entry exists in the seeds vocabulary (EK | Worb | FR), so seeds is empty; which short name should the Fireball seed get?"
```
