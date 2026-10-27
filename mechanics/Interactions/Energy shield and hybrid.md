---
type: interaction
status: draft
pob_refs: [EnergyShieldRecharge, EnergyShieldRechargeDelay, EnergyShieldRegen, conditionEnergyShieldRechargeRecently, conditionEnergyShieldRechargePastTwoSec, TotalEHP]
source: "poewiki Energy shield rev 1673450; PoB 2.67.2 CalcDefence.lua, Data.lua, Data/Misc.lua, ConfigOptions.lua, TreeData/3_29/tree.lua; b1-tree-ascendancy-analyst.md (task 027 batch 1)"
last_confirmed_patch: "3.29.x"
---

Life and energy shield are two pools in sequence: energy shield takes the hit before life (chaos damage bypasses it), recharges after a delay of 200/(100 + r) s (2 s by default) with no damage taken, and life does not recharge. PoB counts the pool in the hit simulation and max hit pools and computes the recharge rate and delay, but leaves recharge out of EHP and max hit (the vault gap EHP ignores recovery) and has no "interrupted by damage" rule; the recharge conditions are config-driven. A hybrid build spends passive points on both pools.
Pipeline: [[Receiving damage#Energy shield]] - ES absorbs after aegis and ward and before mana and life, and chaos bypasses it; [[Defences#Energy shield]] has the recharge numbers and [[Defences#Effective HP]] the pool.
Impact EK: the Assassin build is not read in this batch; whether it has ES is not verified. Impact Fireball (Witch start): the hybrid target of Life 3,000 + ES 1,100 is a 4,100 raw pool for non-chaos hits (3,000 for chaos, plain sum, arithmetic only). Melding (d10) gives 7% increased Life and 3% of Life as extra ES; Resourcefulness (d12), Written in Blood and Purity of Flesh (d13) cover both pools. Roughly 10-13 points for a hybrid notable versus the same points on one pool; Mind over Matter stacks on top ([[Mind over Matter]]). Chaos Inoculation is forbidden by the Fireball seed and is not researched here.

```interaction
id: energy-shield-hybrid
mechanic: "Energy shield takes non-chaos damage before life and recharges after 200/(100+r) s (2 s default) without damage; hybrid builds invest in both life and energy shield"
family: defence
pipeline_step: ["Receiving damage#Energy shield", "Defences#Energy shield", "Defences#Effective HP"]
pipeline_why: "ES absorbs after aegis and ward and before mana and life; chaos bypasses it; the recharge rate and delay come from the Defences numbers and the pool adds to the hit pool in EHP"
target: self
related: [mind-over-matter, recovery, elementalist-aegis-bastion, skill-cost-from-es]
pob:
  measured: partial
  how: "pool in the hit simulation CalcDefence.lua:322-332 and in max hit pools; recharge rate EnergyShieldRecharge and delay EnergyShieldRechargeDelay CalcDefence.lua:1343-1400 (base Data.lua:255-256, 2 s delay; rate base Data/Misc.lua:66 = 2000 per minute = 33.3%/s); ES regen EnergyShieldRegen :1235-1296. Not counted: recharge in EHP/max hit (existing gap EHP ignores recovery; CalcDefence.lua:2904-2966), the interrupted-by-damage rule and the recharge-start condition (only through the two config flags)"
  config:
    - {var: conditionEnergyShieldRechargeRecently, default: false, ref: "Modules/ConfigOptions.lua:1432", class: b}
    - {var: conditionEnergyShieldRechargePastTwoSec, default: false, ref: "Modules/ConfigOptions.lua:1435", class: b}
  unparsed: []
model: null
providers:
  # Witch tree, global stats; d = points from the Witch start by raw tree adjacency (not PassiveSpec node.path)
  - {kind: notable, name: "Melding 18865", slot: tree, role: applies, target: self, text: "7% increased maximum Life; gain 3% of maximum Life as extra maximum Energy Shield (the hybrid node; d10)", source: "TreeData/3_29/tree.lua:62374", pob: full}
  - {kind: notable, name: "Resourcefulness 41989", slot: tree, role: applies, target: self, text: "10% increased maximum ES; 5% increased maximum Life; +8% to Spell Suppression (d12)", source: "TreeData/3_29/tree.lua:74892", pob: full}
  - {kind: notable, name: "Written in Blood 18769", slot: tree, role: applies, target: self, text: "10% increased ES; 10% increased Life; +10 Strength (d13)", source: "TreeData/3_29/tree.lua:75265", pob: full}
  - {kind: notable, name: "Purity of Flesh 58218", slot: tree, role: applies, target: self, text: "8% increased ES; 10% increased Life; +8% to Chaos Resistance (d13)", source: "TreeData/3_29/tree.lua:27338", pob: full}
  - {kind: notable, name: "Sanctity 26866", slot: tree, role: applies, target: self, text: "20% increased Armour; 10% increased ES; regenerate 1% of Life per second; +10 Strength and Intelligence (d13)", source: "TreeData/3_29/tree.lua:34213", pob: full}
  - {kind: notable, name: "Deep Wisdom 27929", slot: tree, role: applies, target: self, text: "+20 maximum ES; +20 maximum Mana; +20 Intelligence (d5)", source: "TreeData/3_29/tree.lua:51190", pob: full}
  - {kind: notable, name: "Arcane Focus 42795", slot: tree, role: applies, target: self, text: "20% increased maximum ES; 10% faster start of ES recharge; +10 Intelligence (d8)", source: "TreeData/3_29/tree.lua:55728", pob: full}
  - {kind: notable, name: "Essence Surge 62577", slot: tree, role: applies, target: self, text: "+30 maximum ES; 20% faster start of ES recharge (d9)", source: "TreeData/3_29/tree.lua:60341", pob: full}
  - {kind: notable, name: "Unnatural Calm 50029", slot: tree, role: scales, target: self, text: "18% increased maximum ES; 15% increased ES recharge rate; +1% maximum Lightning Resistance (d9)", source: "TreeData/3_29/tree.lua:40707", pob: full}
  - {kind: notable, name: "Essence Infusion 23690", slot: tree, role: scales, target: self, text: "15% faster start of ES recharge; 30% increased ES recharge rate (d10)", source: "TreeData/3_29/tree.lua:42057", pob: full}
  - {kind: notable, name: "Foresight 3452", slot: tree, role: applies, target: self, text: "+20 maximum ES; 14% increased ES; 10% increased ES recharge rate (d11)", source: "TreeData/3_29/tree.lua:52186", pob: full}
  - {kind: keystone, name: "Ghost Reaver 24426", slot: tree, role: blocks, target: self, text: "Cannot Recharge Energy Shield", source: "TreeData/3_29/tree.lua:80291", pob: full}
makes_redundant: []
conflicts:
  - {with: "Eldritch Battery 56075", effect: "50% less ES Recharge Rate (Eldritch Battery is batch 4)", source: "TreeData/3_29/tree.lua:67095"}
  - {with: "Wicked Ward 23950", effect: "40% less ES Recharge Rate", source: "TreeData/3_29/tree.lua:61729"}
  - {with: "The Agnostic 19732", effect: "removes all energy shield", source: "TreeData/3_29/tree.lua:21439"}
  - {with: "Solipsism 60247", effect: "Intelligence gives no energy shield", source: "TreeData/3_29/tree.lua:55147"}
  - {with: "Zealot's Oath 63425", effect: "life regeneration is applied to ES instead (see recovery)", source: "TreeData/3_29/tree.lua:26691"}
  - {with: "Chaos Inoculation 11455", effect: "life is 1; forbidden by the Fireball seed, no research done", source: "b1-tree-ascendancy-analyst.md"}
conditions:
  - {text: "recharge starts after 200/(100 + r) s (2 s by default) with no damage taken; damage to ES or to the status ES protects (normally life) interrupts it; chaos damage bypasses ES unless a source removes the bypass; 50% chance to ignore stun while ES is above 0", source: "wiki Energy shield rev 1673450"}
uptime:
  Mapping:       {value: high, config: {conditionEnergyShieldRechargePastTwoSec: "scenario tick, see Config"}, reasoning: "recharge works between packs once 2 s pass undamaged", source: "wiki Energy shield rev 1673450; Modules/ConfigOptions.lua:1435"}
  Pinnacle Boss: {value: low, config: {conditionEnergyShieldRechargePastTwoSec: "scenario tick, see Config"}, reasoning: "recharge is mostly interrupted in boss damage phases, but ES still works as a first buffer against each hit", source: "wiki Energy shield rev 1673450"}
seeds: [Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Energy_shield (rev 1673450; 3.16.0 recharge rate, 3.5.0)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:322-332,1235-1296,1343-1400,2904-2966; Data.lua:255-256; Data/Misc.lua:66; Modules/ConfigOptions.lua:1432,1435 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua lines in the provider rows (PoB 2.67.2)", kind: pob, patch: "3.29"}
not_verified:
  - "Path costs d are raw tree adjacency from the Witch start, not PassiveSpec node.path"
  - "Whether Melding is the best hybrid node for the build (no PoB run)"
  - "Hybrid hit-pool arithmetic for Life 3,000 + ES 1,100: ES first gives 4,100 for non-chaos hits, plain sum, no PoB run"
  - "The provider list comes from a search for nodes that mention Energy Shield or Recharge; Life-only nodes are not listed; item sources of ES are out of scope"
  - "Whether the EK build has energy shield (build not read in this batch)"
open_questions:
  - "Fireball seed: which hybrid split of the 10-13 points between Life and ES, and is recharge worth points given that PoB leaves it out of EHP and max hit?"
```
