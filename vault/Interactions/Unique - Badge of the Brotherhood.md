---
type: interaction
status: draft
pob_refs: [FrenzyChargesMax, FrenzyCharges, PowerChargesMax, ElusiveEffect, MovementSpeed, CooldownRecovery, ReqDex, TotalDPS, TotalEHP, usePowerCharges, useFrenzyCharges, buffElusive]
source: "CoC EK Assa.xml item id 29 (amulet, PoB 2.67.2, game 3.29), headless removal and per-line probes (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md); PoB Data/ModCache.lua, CalcPerform.lua:989-994, Data/ModFoulbornMap.jsonc:660-662; poewiki Badge of the Brotherhood rev 1674844, Ralakesh's Impatience rev 1674049, Elusive rev 1673493"
last_confirmed_patch: "3.29.x"
---

Badge of the Brotherhood is, for the EK seed, the item that lifts the maximum Frenzy charges from 3 to 7 (equal to the maximum Power charges); the amulet is crafted with the As The Mountain anoint (block) and its Dex and Int keep the body armour requirement met. The Frenzy line only pays when something counts the charges: Ralakesh's Impatience (Frenzy variant) in this build, because Inner Conviction turns all Frenzy gains into Power charges.
The two "lose a charge" lines are drawbacks PoB does not model; in this build the Frenzy one costs nothing (no real Frenzy charges), the Power one is a real, unmodelled cost.
A headless removal delta (FullDPS -21.1%) is a PoB number for 7 vs 3 charges at 4% more damage each, not a game fact: the charges must exist in game (see [[Unique - Ralakesh's Impatience]]).

Pipeline: [[Damage calculation#More and less]] - each Frenzy charge is a 4% more multiplier (Data/Misc.lua:74), so the charge maximum scales a more-pool.

```interaction
id: unique-badge-of-the-brotherhood
mechanic: "Unique package: Badge of the Brotherhood raises the maximum Frenzy charges to the maximum Power charges (3 -> 7 in the EK seed) and adds Dex/Int, a block anoint, Elusive effect per Power charge and a travel-skill cooldown line, at the cost of two unmodelled lose-a-charge drawbacks"
family: charge
target: self
pipeline_step: ["Damage calculation#More and less"]
pipeline_why: "the Frenzy charge maximum feeds the per-charge 4% more damage multiplier; the max-equals-Power line only changes how many charges that multiplier counts"
related: [frenzy-charges, power-charges, endurance-charges, fortify, cooldown-recovery-breakpoint, block, aura-conditional-uniques, abyss-jewel-effect, unique-ralakeshs-impatience]
pob:
  measured: partial
  how: "Max Frenzy = Max Power is the flag MaximumFrenzyChargesIsMaximumPowerCharges (ModCache.lua:23080, ModParser.lua:4165); CalcPerform.lua:989-994 replaces FrenzyChargesMax by PowerChargesMax (7). The current count only reaches 7 through a charge source: the config box useFrenzyCharges (ConfigOptions.lua:906, seed UNSET) or Ralakesh's 'Count as having maximum' flag. The two lose-charge lines are not parsed (ModCache.lua:7334 red; the Power one has no ModCache entry, live parse empty). Seed measurement (headless, in memory): whole removal FullDPS -21.107% (11,941,714), main TotalDPS -12.258% (6,781,085), Frenzy max/current 7 -> 3, TotalEHP 145,259 -> 104,154 (-28.3%)"
  config:
    - {var: usePowerCharges, default: false, ref: "Modules/ConfigOptions.lua:900", class: c}
    - {var: useFrenzyCharges, default: false, ref: "Modules/ConfigOptions.lua:906", class: c}
    - {var: buffElusive, default: false, ref: "Modules/ConfigOptions.lua:1060", class: b}
  unparsed:
    - "Badge of the Brotherhood: 25% chance to lose a Frenzy Charge when you use a Travel Skill (ModCache.lua:7334, red)"
    - "Badge of the Brotherhood: 22% chance to lose a Power Charge when you gain Elusive (no ModCache entry; live parse empty, remainder unparsed)"
model: null
providers:
  - {kind: unique, name: "Badge of the Brotherhood", variant: "no variants; seed not Foulborn", slot: amulet, role: scales, target: self, text: "Your Maximum Frenzy Charges is equal to your Maximum Power Charges", source: "Data/ModCache.lua:23080; ModParser.lua:4165; CalcPerform.lua:989-994", pob: full}
  - {kind: unique, name: "Badge of the Brotherhood", variant: "crafted enchant (anoint)", slot: amulet, role: enables, target: self, text: "Allocates As The Mountain (node 44191: +12% Chance to Block Attack Damage while Dual Wielding or holding a Shield, +3% to maximum Chance to Block Attack Damage; real here because the Phoenix Mark shield is equipped)", source: "live GrantedPassive parse, not in ModCache; spec.nodes[44191].sd (item-analyst-ek.md); removal of the line: TotalEHP 145,259 -> 114,183 (-21.4%)", pob: full}
  - {kind: unique, name: "Badge of the Brotherhood", variant: "no variants", slot: amulet, role: sustains, target: self, text: "+24 to Dexterity and Intelligence", source: "Data/ModCache.lua:1146; output.ReqDex 173 (CalcPerform.lua:2118-2160)", pob: full}
  - {kind: unique, name: "Badge of the Brotherhood", variant: "no variants", slot: amulet, role: scales, target: self, text: "10% increased Effect of Elusive on you per Power Charge (needs Elusive: Mistwalker node 28782 and config buffElusive)", source: "Data/ModCache.lua:3839; removal of the line: TotalEHP 145,259 -> 135,005 (-7.1%), MS x1.561 -> x1.484", pob: config}
  - {kind: unique, name: "Badge of the Brotherhood", variant: "no variants", slot: amulet, role: scales, target: self, text: "9% increased Cooldown Recovery Rate of Travel Skills per Frenzy Charge (Frostblink cooldown output 0.825 s with the line, 1.056 s without; Whirling Blades has no cooldown)", source: "Data/ModCache.lua:11833; headless eval (item-analyst-ek.md)", pob: full}
  - {kind: unique, name: "Badge of the Brotherhood", variant: "no variants", slot: amulet, role: blocks, target: self, text: "DRAWBACK: 25% chance to lose a Frenzy Charge when you use a Travel Skill", source: "Data/ModCache.lua:7334 (red, unparsed)", pob: none}
  - {kind: unique, name: "Badge of the Brotherhood", variant: "no variants", slot: amulet, role: blocks, target: self, text: "DRAWBACK: 22% chance to lose a Power Charge when you gain Elusive", source: "no ModCache entry; live parse of item.explicitModLines: modList empty, remainder unparsed", pob: none}
  - {kind: foulborn, name: "Badge of the Brotherhood", variant: "replaces: 9% increased Cooldown Recovery Rate of Travel Skills per Frenzy Charge", slot: amulet, role: scales, target: self, text: "2% increased Movement Speed per Frenzy Charge (MutatedUniqueAmulet57MovementVelocityPerFrenzyCharge). In-memory test: MS x1.561 -> x1.659, FullDPS/TotalDPS/EHP unchanged, Frostblink cooldown back to 1.056 s", source: "Data/ModFoulbornMap.jsonc:660-662, ModFoulbornMap.lua:66-68; wiki Badge of the Brotherhood rev 1674844 Foulborn table", pob: full}
package:
  seed: "CoC EK Assa.xml (PoB 2.67.2, game 3.29), item set 1"
  slot: Amulet
  base: "NOT VERIFIED (not in the evidence file)"
  xml_item_id: 29
  variant: "none (no variants); not Foulborn"
  removal: "FullDPS -21.107% (15,136,639 -> 11,941,714), main TotalDPS -12.258%, TotalEHP -28.3% - in-memory removal; PoB keeps the emptied slot's gems active, so the in-game loss is larger (an amulet has no sockets, so here nothing extra is lost)"
  lost_with_item:
    - "Frenzy charges max 7 -> 3 (current 7 -> 3)"
    - "As The Mountain anoint: +12% block and +3% max block (TotalEHP -21.4%)"
    - "Dex 181 -> 157 and Int 362 -> 338: body armour Cataclysm Shroud requirement UNMET (ReqDex 173, the only unmet requirement); condition DexHigherThanStr flips (UniqueItemInAmulet off)"
    - "ES 5189 -> 5130, Mana 1201 -> 1184 (unreserved 107 -> 104), Evasion 14082 -> 13758"
    - "Elusive effect +70% (7 Power charges x 10%): MS x1.561 -> x1.484"
  downsides_that_are_the_point:
    - "25% to lose a Frenzy Charge on a travel skill: costs nothing here, because Inner Conviction (node 12128, 'Gain Power Charges instead of Frenzy Charges') means the build never holds real Frenzy charges; the Badge only raises the maximum that Ralakesh's Impatience counts (wiki Ralakesh rev 1674049: 'the character will gain any stats that would normally be gained from having their maximum number of the given type of charge')"
    - "22% to lose a Power Charge when Elusive is gained: a real cost PoB does not model (PoB assumes 7 Power charges via usePowerCharges). Elusive cannot be refreshed while active (wiki Elusive rev 1673493), so with Mistwalker the gain happens once per Elusive cycle, not once per crit. Cycle length with the Elusive effect of this build: NOT VERIFIED"
  foulborn: "not Foulborn in the seed. A Foulborn copy swaps the 9% travel-skill cooldown line for 2% increased Movement Speed per Frenzy Charge (see provider). Trade-off from the in-memory test: +9.8 points of Movement Speed against -22% Frostblink cooldown recovery, no DPS change"
  obtainability: "poewiki Badge of the Brotherhood rev 1674844 (patch 3.29): Blight unique, introduced 3.8.0, 'Many unique items that were league-specific have now also been added to the core drop pool' (3.14.0 version row), drop_level 68; not drop-restricted. Foulborn copy is a mutation, its acquisition NOT VERIFIED. The As The Mountain anoint is a crafted blight enchant, recipe NOT VERIFIED"
makes_redundant:
  - {provider: "Ralakesh's Impatience Frenzy line (in PoB)", when: "config useFrenzyCharges is ticked", why: "PoB then counts 7 Frenzy charges without the boots (matrix: Ralakesh removed with the box ticked = base 15.137M), but PoB cannot see that Ralakesh is what makes them real in game", source: "headless matrix eval3b (item-analyst-ek.md)"}
conflicts:
  - {with: "Replica Badge of the Brotherhood", effect: "a different item (Endurance maximum = Frenzy maximum, Fortification); do not read its lines as this unique's", source: "Fortify and Endurance charges notes carry only the Replica"}
  - {with: "No Frenzy-count source (Ralakesh's Impatience Frenzy variant or useFrenzyCharges)", effect: "the Badge is worth 0 alone: FullDPS matrix in memory: base 15.137M; no Ralakesh and no tick 9.807M (Frenzy 0); no Ralakesh with tick 15.137M; no Badge with Ralakesh 11.942M (3 charges); no Badge and no Ralakesh 9.807M; no Badge, no Ralakesh, with tick 11.942M", source: "eval3b (item-analyst-ek.md)"}
conditions:
  - {text: "Power charge maximum 7 comes from the tree (Instability, Overcharge, Infused, Unstable Infusion each +1 per the spec dump); the Badge copies that maximum", source: "item-analyst-ek.md, Conflicts"}
  - {text: "Elusive effect line needs Elusive: Mistwalker (node 28782, Gain Elusive on Critical Strike) and the seed buffElusive ticked", source: "Data/ModCache.lua:3839; ConfigOptions.lua:1060"}
  - {text: "Dex floor shared with Circle of Guilt (+17) and the Darkness Enthroned abyss jewels (+19): base Dex 181 vs ReqDex 173 (8 spare); removing any one of the three leaves Cataclysm Shroud unmet; PoB shows no DPS change for that", source: "item-analyst-ek.md, Cross-item findings 1"}
uptime:
  Mapping:       {value: pob, config: {usePowerCharges: true, buffElusive: true}, reasoning: "no on-hit effect; the Frenzy maximum is permanent, the charges are assumed at max by config; Elusive is on whenever Mistwalker can apply it (CritChance 100, SkillTriggerRate 8.93/s) apart from the Elusive cycle gap, NOT VERIFIED", source: "item-analyst-ek.md, Uptime"}
  Pinnacle Boss: {value: pob, config: {usePowerCharges: true, buffElusive: true}, reasoning: "same as Mapping; the lose-Power drawback happens at most once per Elusive cycle x 22% (derived, unmodelled)", source: "item-analyst-ek.md, Uptime"}
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Badge_of_the_Brotherhood (rev 1674844)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ralakesh%27s_Impatience (rev 1674049)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Elusive (rev 1673493)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/ModCache.lua, Modules/CalcPerform.lua:989-994, Data/ModFoulbornMap.jsonc:660-662", kind: pob, patch: "3.29"}
  - {ref: "headless probes on CoC EK Assa.xml, PoB 2.67.2 (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: exact Elusive cycle length with +180% Elusive effect (wiki says duration scales with buff effect; roughly 14 s if effect x2.8 is a derivation, not a measurement)"
  - "NOT VERIFIED: how often travel skills (Whirling Blades, Frostblink) are used; irrelevant while no real Frenzy charges exist"
  - "NOT VERIFIED: current-league source of the As The Mountain anoint oils; Foulborn mutation acquisition; the amulet base type"
  - "Power charge gain sources allocated (Unstable Infusion 15% on crit / 30% non-crit, Disciple of the Forbidden 8% on kill) were not checked against the 22% loss rate"
open_questions:
  - "Do you want the generator to treat Badge + Ralakesh Frenzy + Inner Conviction as one required package, or to allow the useFrenzyCharges tick as a stand-in?"
```
