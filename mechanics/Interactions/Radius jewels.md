---
type: interaction
status: draft
pob_refs: [JewelData, JewelFunc, nodesInRadius, radiusJewelList, extraRadiusNodeList, PassiveSkillEffect, AllocatedPassiveSkillHasNoEffect, intuitiveLeapLikesAffecting]
source: "PoB 2.67.2 Modules/Data.lua:583-630, Classes/PassiveTree.lua:655-686, Classes/Item.lua:690-700, Modules/ModParser.lua:5201-5219 / 6151-6168 / 6231-6340 / 6378-6440 / 6480 / 6555-6580 / 6643, Modules/CalcSetup.lua:134-199 / 281-300 / 848-935, Classes/PassiveSpec.lua:1065-1090 / 1132-1200, Data/Uniques/jewel.lua; poewiki Jewel rev 1699308, The Light of Meaning rev 1702343, Thread of Hope rev 1553029; headless Worb and EK probes (task 027 batch 4c)"
last_confirmed_patch: "3.29.x"
---

A radius jewel changes the passives around its socket. Its value is the number and kind of nodes inside the radius, so it depends on the tree, not only on the jewel. The socket must be allocated. PoB applies four kinds: 'Passive Skills in Radius also grant X' (added to every allocated node: Light of Meaning), per-attribute and threshold lines (Self / Threshold), conversions (Brute Force Solution, Healthy Mind, Energy From Within, Might of the Meek) and allocation without a path (Thread of Hope, Intuitive Leap).
Worb seed: The Light of Meaning, Large radius, selected variant 10 = 6% increased Cold Damage per allocated node in radius (30 nodes -> +180% increased Cold Damage; removing it: TotalDPS 1,343,497.51 -> 1,126,437.92, -16.2%). The Worb seed note is [[Seeds-as-mechanics]]. Skill-modifier lines on radius uniques that PoB does not parse are listed in [[Radius jewel skill lines]].

Pipeline: [[Damage calculation#Increased and reduced]] - radius effects become ordinary mods on the nodes before PoB sums the pools, so they act where the stat they add acts (the Light of Meaning Cold Damage variant is 6% per node in the increased pool)

```interaction
id: radius-jewel
mechanic: "Jewel in an allocated socket affects passives within a radius of the socket (PoB units: Small 960, Medium 1440, Large 1800, Very Large 2400, Massive 2880; Thread of Hope-type 'Variable' jewels use the rings 960-1320, 1320-1680, 1680-2040, 2040-2400, 2400-2880). Kinds: 'Passive Skills in Radius also grant X' (allocated nodes), per-attribute and threshold lines, conversion/transform, and allocation without a connecting path"
family: buff
pipeline_step: ["Damage calculation#Increased and reduced"]
pipeline_why: "radius effects are added to the node mod lists before PoB sums the pools, so they act at the step of the stat they add; the Worb Light of Meaning variant adds Cold Damage INC per allocated node"
target: self
related: [timeless-jewels, cluster-jewels, forbidden-jewels, coc-trigger]
pob:
  measured: partial
  how: "Radii: Data.lua:603-628 table 3_16 (used for trees above 3_15, Data.lua:583-601) = wiki radii x1.2 (wiki Jewel rev 1699308: 800/1200/1500/2000/2400, rings 800-1100 ... 2000-2400). Node lists: PassiveTree.lua:655-686 precomputes socket.nodesInRadius[radiusIndex] for base-tree nodes only (excludes blighted, proxy, mastery and group-less nodes; cluster-jewel nodes are not in the base tree); Item.lua:690-700 maps 'Radius: Large' to the index, Thread of Hope-type 'Variable' takes the index from 'Only affects Passives in X Ring' (ModParser.lua:5210-5219). Apply: CalcSetup.lua:848-849 skips jewels in unallocated sockets; 875-935 puts each jewel function in env.radiusJewelList (types Other / Self / SelfUnalloc / Threshold: ModParser.lua:6151, 6378, 6409, 6480, wrapped 6555-6580); 'Other' functions run per allocated node in buildModListForNode (CalcSetup.lua:144-152, skip nodes with conqueredBy, ModParser.lua:6555-6567) before PassiveSkillEffect scaling (CalcSetup.lua:182-190); Self/Threshold run in the second pass (192-199) and Threshold/SelfUnalloc also scan unallocated nodes (extraRadiusNodeList, 281-290, 900, 927). 'also grant' lines skip Keystone, Socket and ClassStart nodes (ModParser.lua:6275-6340). Path-free allocation: ModParser.lua:5201-5219 sets JewelData intuitiveLeapLike; PassiveSpec.lua:1169-1182 flags every Normal/Notable/Keystone node in the radius except Socket, ClassStart and ascendancy nodes. MEASURED 2026-10-26 Worb.xml (Brine King off, Winter Orb count 5), Light of Meaning socket 61419, Large (index 3, outer 1800), selected variant 10: 97 nodes in radius, 31 allocated (23 Normal, 7 Notable, 1 Keystone); with the jewel TotalDPS 1,343,497.51, FullDPS 6,717,487.57, Life 4306, TotalEHP 76,836.94, Cold Damage INC 421; socket emptied in memory: TotalDPS 1,126,437.92 (-16.2%), FullDPS 5,632,189.59, Cold INC 241 (-180 = 30 non-keystone nodes x 6), Life/ES/Mana/TotalEHP unchanged; same jewel with variant 1 (+5 maximum Life per node) in memory: Life 4627, TotalEHP 80,392.98 (+4.6%), TotalDPS 1,126,437.92 (so the variant is a DPS vs EHP trade: -16.2% DPS for +4.6% EHP). Thread of Hope Large Ring put into EK socket 61419 in memory: radiusIndex 8 (1680-2040), intuitiveLeapLike true, 34 nodes in the ring all flagged path-free (24 Normal, 9 Notable, 1 Keystone), 0 flagged outside the ring; actually allocating an unconnected node was not probed"
  config: []
  unparsed:
    - "Ring of Blades: With at least 40 Dexterity in Radius, Ethereal Knives fires Projectiles in a circle (ModCache.lua:22578 {nil, leftover}; the jewel was removed from the game in 3.20.0, wiki Ring of Blades rev 1553488, so it is not a provider)"
    - "62 more threshold/flavour lines on radius uniques have extra (unparsed) text in PoB's DB, e.g. Hazardous Research, Dead Reckoning, Steel Spirit, Combat Focus, The Blue/Red/Green Dream/Nightmare 'also grant an equal chance to gain a ... Charge on Kill'; list and patterns: [[Radius jewel skill lines]] (two of the 62 are line-wrap artifacts 'Passage' of Thread of Hope and Intuitive Leap); the only seed jewel among them is Militant Faith ('4% reduced Duration of Curses on you per 10 Devotion', other specialist) - Ring of Blades above is the only line that names an EK skill"
model: null
providers:
  - {kind: jewel, name: "The Light of Meaning (Worb: variant 10, 6% increased Cold Damage)", slot: jewel, role: scales, target: self, text: "Large radius, Limited to 1; 'Passive Skills in Radius also grant 6% increased Cold Damage' on each allocated non-keystone node; 13 random variants (wiki: equally weighted, not rerollable with a Divine Orb, no radius in cluster-jewel sockets, ignores cluster-jewel passives)", source: "Builds 3.29/Worb.xml:540-575, 736-738; PoB Data/Uniques/jewel.lua:354-; poewiki The Light of Meaning rev 1702343 (introduced 3.25.0)", pob: full, variant: "Selected Variant 10 (Cold Damage); the unique DB entry's first variant is Life"}
  - {kind: jewel, name: "Militant Faith (EK: Large radius timeless jewel)", slot: jewel, role: enables, target: self, text: "Radius: Large; conquers passives in radius (own note by another specialist, not drafted here)", source: "PoB Data/Uniques/jewel.lua (Militant Faith, Radius: Large); COMMON.md seed list", pob: partial}
  - {kind: jewel, name: "Thread of Hope", slot: jewel, role: enables, target: self, text: "Radius: Variable (Small to Very Large ring, Massive from Uber Sirus); -(20-10)% to all Elemental Resistances; 'Passive Skills in Radius can be Allocated without being connected to your tree'; sockets cannot be allocated with it, masteries are not reachable", source: "PoB Data/Uniques/jewel.lua:760-775; ModParser.lua:5205-5219; PassiveSpec.lua:1169-1182; poewiki Thread of Hope rev 1553029 (3.9.0, Massive ring 3.18.0)", pob: partial}
  - {kind: jewel, name: "Intuitive Leap", slot: jewel, role: enables, target: self, text: "Small radius: allocate passives in radius without a connecting path", source: "PoB Data/Uniques/jewel.lua (Intuitive Leap, Radius: Small); ModParser.lua:5205", pob: partial}
  - {kind: jewel, name: "Impossible Escape", slot: jewel, role: enables, target: self, text: "Passives in radius of a chosen keystone can be allocated without a path (generated item per keystone)", source: "PoB Data/Uniques/Special/Generated.lua:649; ModParser.lua:5201-5204; PassiveSpec.lua:1077-1090", pob: partial}
  - {kind: jewel, name: "Unnatural Instinct", slot: jewel, role: scales, target: self, text: "Small radius, Limited to 1: allocated Small passives grant nothing; unallocated Small passives in radius grant all their bonuses", source: "PoB Data/Uniques/jewel.lua (Unnatural Instinct); ModParser.lua:6250, 6420", pob: full}
  - {kind: jewel, name: "Might of the Meek", slot: jewel, role: scales, target: self, text: "Large radius: 50% increased Effect of non-Keystone Passive Skills in radius; Notable passives in radius grant nothing", source: "PoB Data/Uniques/jewel.lua:450-454; ModParser.lua:6231-6246, 6238", pob: full}
  - {kind: jewel, name: "Brute Force Solution / Careful Planning / Efficient Training / Fertile Mind", slot: jewel, role: scales, target: self, text: "Large radius: one attribute from passives in radius is transformed into another (e.g. Strength -> Intelligence)", source: "PoB Data/Uniques/jewel.lua (those four); ModParser.lua:6152-6157", pob: full}
  - {kind: jewel, name: "Healthy Mind", slot: jewel, role: scales, target: self, text: "Large radius, Limited to 1: increases and reductions to Life in radius apply to Mana at 200% of their value", source: "PoB Data/Uniques/jewel.lua (Healthy Mind); ModParser.lua:6163", pob: full}
  - {kind: jewel, name: "Energy From Within", slot: jewel, role: scales, target: self, text: "Large radius: increases and reductions to Life in radius apply to Energy Shield", source: "PoB Data/Uniques/jewel.lua (Energy From Within); ModParser.lua:6158", pob: full}
makes_redundant: []
conflicts:
  - {with: "a jewel socket added by a cluster jewel", effect: "no radius there (wiki); PoB: spec.nodes[59585].nodesInRadius is nil in the EK build (probe error 'attempt to index field nodesInRadius (a nil value)' on a Reckless Defence socket; that this socket is cluster-added was not checked separately)", source: "poewiki Jewel rev 1699308 (Radius), The Light of Meaning rev 1702343; PassiveTree.lua:655-686; headless probe 2026-10-26"}
  - {with: "second Light of Meaning", effect: "Limited to 1: the second copy is disabled unless the 'Ignore Jewel Limits' config is ticked", source: "CalcSetup.lua:862-871; ConfigOptions.lua:249"}
conditions:
  - {text: "the socket must be allocated; the Light of Meaning bonus counts allocated nodes in radius, so its value moves with every tree change (Worb: 30 non-keystone nodes of 97 in radius)", source: "CalcSetup.lua:848-849; headless Worb probe 2026-10-26"}
  - {text: "node kinds counted: base-tree Normal and Notable nodes; keystones, sockets, class starts, masteries, blighted/proxy nodes, cluster-jewel passives and ascendancy passives are not (PoB excludes the first group in PassiveTree.lua:668-672 and ModParser.lua:6275-6340; wiki lists masteries, cluster, ascendancy)", source: "PassiveTree.lua:668-672; ModParser.lua:6275-6340; poewiki Jewel rev 1699308 (Radius)"}
  - {text: "PoB radii are the wiki radii x1.2 (Large 1800 vs wiki 1500); both are the same set of nodes", source: "Data.lua:615-628; poewiki Jewel rev 1699308"}
  - {text: "Thread of Hope: the socket must be connected; flagged nodes are only the ring (inner-outer), sockets are excluded (PoB flags Normal/Notable/Keystone; wiki: sockets cannot be allocated with it)", source: "PassiveSpec.lua:1169-1182; poewiki Thread of Hope rev 1553029; headless probe 2026-10-26"}
  - {text: "a radius jewel can sit in a socket whose radius covers the seed's unallocated nodes: Threshold and SelfUnalloc jewels read those too (extraRadiusNodeList)", source: "CalcSetup.lua:281-290, 900, 927"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "passive/equipment effect: permanent while the socket is allocated", source: "CalcSetup.lua:848-849"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same", source: "CalcSetup.lua:848-849"}
seeds: [Worb, EK]
sources:
  - {ref: "PoB Modules/Data.lua:583-630; Classes/PassiveTree.lua:655-686; Modules/CalcSetup.lua:134-199, 281-300, 848-935; Modules/ModParser.lua:5201-5219, 6151-6340, 6378-6440, 6555-6580; Classes/PassiveSpec.lua:1065-1090, 1132-1200", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Jewel (rev 1699308, Radius section)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/The_Light_of_Meaning (rev 1702343; introduced 3.25.0)", kind: wiki, patch: "3.25.0"}
  - {ref: "https://www.poewiki.net/wiki/Thread_of_Hope (rev 1553029; 3.9.0, 3.18.0, 3.24.0)", kind: wiki, patch: "3.24.0"}
  - {ref: "https://www.poewiki.net/wiki/Ring_of_Blades (rev 1553488; removal_version 3.20.0)", kind: wiki, patch: "3.20.0"}
not_verified:
  - "Light of Meaning-type bonuses on nodes conquered by a timeless jewel: PoB skips them (ModParser.lua:6555-6567); the game behaviour was not checked"
  - "Might of the Meek scaling Light of Meaning bonuses: PoB applies PassiveSkillEffect after the first-pass radius functions (CalcSetup.lua:144-190, code-read); game behaviour not checked"
  - "two radius jewels overlapping the same nodes: how PoB and the game stack them was not probed"
  - "allocating an unconnected node inside a Thread of Hope ring and the resulting mods (only the path-free flag was probed)"
  - "Militant Faith and the Worb/EK cluster jewels are other specialists' notes; not re-checked here"
  - "which Light of Meaning variant the generator should choose: the roll is random and not craftable (wiki), so a generator can only take what the trade market has"
open_questions:
  - "Light of Meaning is on Cold Damage (variant 10) in the Worb file while the DB default is Life: the variant costs 16.2% DPS vs +4.6% EHP in PoB. Is the Cold Damage roll intended (for example bought for DPS)? Only the user can say"
```

## Owner, 2026-10-28: which points a jewel costs (draft, to verify)
For tree suggestions that move at most 20 points (grilling 2026-10-28, docs/history), the owner says:
- Nodes Unnatural Instinct grants without allocating them cost no points (PoB text: "Grants all bonuses of Unallocated
  Small Passive Skills in Radius", Data/Uniques/jewel.lua:787-792).
- Where Unnatural Instinct's radius overlaps The Light of Meaning's (especially Scion's start area), the nodes Unnatural
  Instinct grants there also cost no points, and get The Light of Meaning's bonus.
- Might of the Meek raises the effect of non-keystone passives in radius, but they must still be allocated, so they cost
  points (jewel.lua:450-454).
- Intuitive Leap and Thread of Hope let nodes be taken without a path, but every node taken costs a point
  (jewel.lua:334-337, 776-781).

Open check: this note records that PoB's Light of Meaning bonus counts *allocated* nodes in radius
(CalcSetup.lua:848-849, above). Whether PoB gives the bonus to nodes Unnatural Instinct grants unallocated is not
measured; if PoB's numbers disagree with the owner's second point, ask him (decision 013).
