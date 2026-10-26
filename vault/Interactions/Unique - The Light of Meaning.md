---
type: interaction
status: draft
pob_refs: [TotalDPS, FullDPS, EHP, JewelFunc]
source: "PoB 2.67.2 Data/Uniques/jewel.lua (Light of Meaning), ModParser.lua:6275-6340 and 6646-6651, PassiveTree.lua:668-672, CalcSetup.lua:848-871, ConfigOptions.lua:249, ItemsTab.lua:225-233, ItemSlotControl.lua:72-79; poewiki The Light of Meaning rev 1702343; vault Radius jewels; headless Worb probes (task 027 batch 2c, item-analyst-worb.md)"
last_confirmed_patch: "3.29.x"
---

The Light of Meaning is a random-modifier radius jewel (Large radius, Limited to 1). The seed has variant 10: "Passive Skills in Radius also grant 6% increased Cold Damage", granted to every allocated non-keystone node in the radius: 30 nodes x 6% = +180% increased Cold Damage, -16.16% TotalDPS in Pinnacle and Mapping alike when removed. The other 12 variants are parsed but gated off.
It joins the same additive Cold/Elemental damage pool as The Taming's 117% (Worb pool 1014%), and it moves with every tree change: the value is re-measured after any allocation in the radius. It cannot be rerolled (Divine Orbs do not reroll the modifier), so a generator can only take what the market has; the Cold Damage roll is about 1 in 13 per drop (derived from equal weights).
Pipeline: [[Damage calculation#Increased and reduced]] - the granted Cold Damage is ordinary increased damage on allocated nodes, additive with every other increased source

```interaction
id: unique-the-light-of-meaning
mechanic: "Unique package: a random-modifier radius jewel that grants a bonus stat (variant 10: 6% increased Cold Damage) to every allocated non-keystone passive in the Large radius - 30 nodes = +180% increased Cold Damage in Worb"
family: buff
pipeline_step: ["Damage calculation#Increased and reduced"]
pipeline_why: "the granted stat is increased Cold Damage on allocated passives, which sums into the additive increased pool (Cold + Elemental + Damage INC on hit 1014% in Worb)"
target: self
related: [radius-jewel, cluster-jewels, elemental-ailment-count, unique-the-taming, timeless-jewels]
pob:
  measured: full
  how: "Parse: the 13 variant lines parse as JewelFunc LIST {func, type = 'Other'} (ModParser.lua:6646-6651); no extra, no red line; only the selected variant (10, the 10th Variant label 'Cold Damage', file line {variant:10}) is active, the item's JewelFunc source is 'Item:21' only for it. Radius: data.jewelRadius index 3 'Large', outer 1800 (PoB = wiki 1500 x 1.2), 97 base-tree nodes in radius (71 Normal, 22 Notable, 4 Keystone); 31 allocated (23 Normal, 7 Notable, 1 Keystone = Bitter Frost); the line is added to every allocated non-keystone node = 30 nodes x 6% = +180% (Cold Damage INC on the skill 421 -> 241 with the jewel removed). The socket must be allocated (61419 is, CalcSetup.lua:848-849). Masteries, cluster-jewel nodes, ascendancy nodes and keystones are not granted (PassiveTree.lua:668-672, ModParser.lua:6275-6340). Whole-item removal Worb (Pinnacle / Mapping): TotalDPS 1,343,497.51 -> 1,126,437.92 (-16.16%) / 1,934,211.10 -> 1,621,714.00 (-16.16%), FullDPS 5,632,189.59 / 8,108,569.99; every other stat unchanged (Life, ES, Mana, res, charges, attributes, EHP, speed); the socket node stays allocated; no condition or multiplier flipped. The tree socket was emptied with build.itemsTab.slots['Jewel 61419']:SetSelItemId(0) (ItemSlotControl.lua:72-79; slot created at ItemsTab.lua:225-233); a jewel has no socket group, so there is no emptied-slot gem effect."
  config: []
  unparsed: []
model: null
providers:
  - {kind: jewel, name: "The Light of Meaning", variant: "10: Cold Damage (selected)", slot: "Tree socket 61419", role: scales, target: self, text: "Passive Skills in Radius also grant 6% increased Cold Damage: 30 nodes x 6% = +180%, -16.16% TotalDPS when removed", source: "PoB Data/Uniques/jewel.lua (Light of Meaning; line number not recorded in the evidence); ModParser.lua:6646-6651; w2.json", pob: full}
  - {kind: jewel, name: "The Light of Meaning", variant: "other 12 variants, measured in the same socket (w5.json)", slot: "Tree socket 61419", role: scales, target: self, text: "Global Crit Chance variant: TotalDPS 1,189,845 Pinnacle (-11.44%) / 1,711,820 Mapping; the other eleven variants give 1,126,438 (-16.16%) / 1,621,714 TotalDPS with a side effect each: EHP Pinnacle Energy Shield 89,752 (+16.8%), Armour 87,970 (+14.5%), Evasion 85,723 (+11.6%), Life 80,393 (+4.6%), Chaos Resistance 80,094 (+4.2%, chaos res 63 -> 75), Attributes 78,803; Mapping EHP Armour 209,810 (+158.5%), ES 112,964, Evasion 90,538, Life 85,142", source: "PoB Data/Uniques/jewel.lua (Light of Meaning); ModParser.lua:6646-6651; w5.json", pob: full}
package:
  seed: Worb
  slot: "Jewel 61419 (tree socket, Large radius)"
  base: "Prismatic Jewel, Limited to 1"
  xml_item_id: 21
  variant: "10: Passive Skills in Radius also grant 6% increased Cold Damage (13 variants exist, equally weighted per the wiki sample of 500 Prohibited Library jewels)"
  removal: "TotalDPS -16.16% Pinnacle and Mapping (single active line = same value per line) - in-memory removal via SetSelItemId(0); a jewel carries no gems, and the socket node stays allocated, so nothing else changes. Cold Damage variant is worth +19.3% DPS over any non-damage variant, which give +4% to +17% EHP (Pinnacle) at most"
  lost_with_item:
    - "+180% increased Cold Damage on 30 allocated non-keystone nodes in the Large radius (Cold Damage INC 421 -> 241)"
  downsides_that_are_the_point: []
  foulborn: "none: ModFoulbornMap grep = no hit; wiki Foulborn list rev 1702126: absent. A corrupted version exists (recipe 5x Squandered Prosperity)"
  obtainability: "poewiki The Light of Meaning rev 1702343 / cargo: release 3.25.0, drop_enabled 1, is_drop_restricted 1, drop_text 'Drops from The King in the Mists in the Crux of Nothingness.', drop_monsters Metadata/Monsters/LeagueAzmeri/VoodooKingBoss/VoodooKingBoss3; recipe 5x The Mayor; 13 modifiers 'appear to be equally weighted' (wiki, sample of 500 Prohibited Library jewels), so the Cold Damage roll is about 1 in 13 per drop (derived); not rerollable (Divine Orbs do not reroll the modifier); tag not_for_sale. Patch 3.29"
makes_redundant:
  - {provider: "A second Light of Meaning", when: "also socketed", why: "disabled by the Limited to 1 rule unless the 'Ignore Jewel Limits' config is set", source: "CalcSetup.lua:862-871; ConfigOptions.lua:249"}
conflicts:
  - {with: "The Taming and other Cold/Elemental Damage increased sources", effect: "same additive pool (1014% in Worb), so each further source is a shrinking share", source: "w3.json"}
  - {with: "Might of the Meek, Thread of Hope, cluster-jewel changes", effect: "change the set of nodes in radius or allocated, and therefore the node count the jewel reads", source: "item-analyst-worb.md"}
conditions:
  - {text: "The socket node must be allocated (61419 is allocated in Worb); keystones, masteries, cluster-jewel nodes and ascendancy nodes are not granted the stat", source: "CalcSetup.lua:848-849; PassiveTree.lua:668-672; ModParser.lua:6275-6340"}
  - {text: "Not usable in cluster-jewel sockets (no radius there); radius is 1500 base, Large", source: "poewiki The Light of Meaning rev 1702343"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "passive jewel, identical to Pinnacle (-16.16%)", source: "item-analyst-worb.md"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "passive jewel, always on", source: "item-analyst-worb.md"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/The_Light_of_Meaning (rev 1702343)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/jewel.lua, Modules/ModParser.lua, Modules/CalcSetup.lua, Classes/PassiveTree.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-worb.md (headless Worb probes, SC/out/w1.json, w2.json, w5.json)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: that the generator should prefer variant 10 (market availability and price)"
  - "NOT VERIFIED: stacking with another radius jewel overlapping the same nodes (not probed)"
open_questions:
  - "Should the generator re-measure the Light of Meaning after every tree allocation in its radius (30 of 97 nodes today)?"
```
