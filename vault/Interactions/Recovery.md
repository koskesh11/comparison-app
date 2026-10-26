---
type: interaction
status: draft
pob_refs: [LifeRegen, ManaRegen, EnergyShieldRegen, RageRegen, RegenRecovery, EnergyShieldRecharge, NetLifeRegen, TotalNetRegen, lifeRegenMode]
source: "poewiki Recovery rev 1618351; PoB 2.67.2 CalcDefence.lua, ConfigOptions.lua, TreeData/3_29/tree.lua; b1-tree-ascendancy-analyst.md (task 027 batch 1)"
last_confirmed_patch: "3.29.x"
---

Recovery is every positive change to a resource: regeneration, energy shield recharge, leech, recoup, flasks and gain on hit or kill (wiki rev 1618351, no version table). When recovery and loss happen at once over time, recovery is calculated first; instant recovery is limited by the recoverable maximum, and over-time recovery by the same maximum in every 33 ms server frame. PoB computes regeneration per resource (base x increased x more x recovery rate) and the ES recharge, but keeps recovery out of EHP and max hit (the vault gap EHP ignores recovery). Leech has its own note: [[Leech]].
Pipeline: [[Receiving damage#Recovery]] and [[Defences#Recovery and leech]] - recovery works over time outside the hit order, so judge it by duration against incoming damage, not by pool size.
Impact EK: the build is not read in this batch, no claim. Impact Fireball: at 3,000 life 1% life regeneration is 30 life/s, against ES recharge of 33.3% x 1,100 = about 366 ES/s once it starts after the 2 s delay (rate from Data/Misc.lua:66, arithmetic only). Recovery does not help the single-hit max hit goal, only the survival of sustained damage, and the points do not show in TotalDPS or max hit.

```interaction
id: recovery
mechanic: "Recovery is every positive change to a resource (regeneration, ES recharge, leech, recoup, flasks, gain on hit or kill); over-time recovery is capped per 33 ms frame at the recoverable maximum and is calculated before loss over time in the same frame"
family: resource
pipeline_step: ["Receiving damage#Recovery", "Defences#Recovery and leech"]
pipeline_why: "recovery is over-time and outside the hit order; recovery rate mods multiply the pooled total, and PoB keeps it out of EHP, so it is judged by duration against incoming damage"
target: self
related: [leech, energy-shield-hybrid, mind-over-matter]
pob:
  measured: partial
  how: "regeneration per resource (Mana, Life, ES, Rage) CalcDefence.lua:1235-1296 (BASE x (1+inc) x more x RecoveryRateMod, output <Resource>Regen, RegenRecovery = regen - degen + recovery, line about 1280); recovery rate mods :1212-1217; ES recharge :1343-1400; Zealot's Oath converts life regen to ES regen :1267-1275 and EnergyShieldRechargeAppliesToLife (Eternal Youth) :1343-1352; net values NetLifeRegen / TotalNetRegen :3439-3525; per-resource multiplication :1286-1287. Not in EHP: CalcDefence.lua:2904-2966"
  config:
    - {var: lifeRegenMode, default: "not read", ref: "Modules/ConfigOptions.lua:212 (burst average or full; shown only when the build has a burst regen condition)", class: b}
    - {var: conditionEnergyShieldRechargeRecently, default: false, ref: "Modules/ConfigOptions.lua:1432", class: b}
    - {var: conditionEnergyShieldRechargePastTwoSec, default: false, ref: "Modules/ConfigOptions.lua:1435", class: b}
    - {var: conditionLeeching, default: "see Leech note", ref: "Leech note", class: b}
  unparsed: []
model: null
providers:
  # Witch tree, d = points from the Witch start by raw tree adjacency (not PassiveSpec node.path)
  - {kind: notable, name: "Quick Recovery 21330", slot: tree, role: applies, target: self, text: "7% increased Life; regenerate 0.8% of Life per second (d9)", source: "TreeData/3_29/tree.lua:41054", pob: full}
  - {kind: notable, name: "Shaper 63976", slot: tree, role: applies, target: self, text: "40% increased mana regeneration rate; regenerate 1% of Life per second (d11)", source: "TreeData/3_29/tree.lua:46792", pob: full}
  - {kind: notable, name: "Growth and Decay 9864", slot: tree, role: applies, target: self, text: "+12% to Damage over Time Multiplier; regenerate 1% of Life per second (d13)", source: "TreeData/3_29/tree.lua:75174", pob: full}
  - {kind: notable, name: "Sanctity 26866", slot: tree, role: applies, target: self, text: "20% increased Armour; 10% increased ES; regenerate 1% of Life per second (d13)", source: "TreeData/3_29/tree.lua:34213", pob: full}
  - {kind: notable, name: "Vampirism 11784", slot: tree, role: applies, target: self, text: "recover 3% of Life on kill; 12% of damage taken recouped as Life (d8)", source: "TreeData/3_29/tree.lua:58320", pob: none}
  - {kind: notable, name: "Infused Flesh 37403", slot: tree, role: applies, target: self, text: "18% of damage taken recouped as Life (d12)", source: "TreeData/3_29/tree.lua:49589", pob: none}
  - {kind: notable, name: "Trial of the Faith 45657", slot: tree, role: applies, target: self, text: "regenerate 5% of ES and 5% of Life over 1 second when stunned (d13)", source: "TreeData/3_29/tree.lua:32242", pob: none}
  - {kind: keystone, name: "Zealot's Oath 63425", slot: tree, role: applies, target: self, text: "Life regeneration is applied to Energy Shield instead (d11)", source: "TreeData/3_29/tree.lua:26691; Modules/CalcDefence.lua:1267-1275", pob: full}
  - {kind: notable, name: "Unnatural Calm 50029", slot: tree, role: scales, target: self, text: "15% increased ES recharge rate (d9); see energy-shield-hybrid", source: "TreeData/3_29/tree.lua:40707", pob: full}
  - {kind: notable, name: "Essence Infusion 23690", slot: tree, role: scales, target: self, text: "30% increased ES recharge rate, 15% faster start (d10); see energy-shield-hybrid", source: "TreeData/3_29/tree.lua:42057", pob: full}
  - {kind: notable, name: "Foresight 3452", slot: tree, role: scales, target: self, text: "10% increased ES recharge rate (d11); see energy-shield-hybrid", source: "TreeData/3_29/tree.lua:52186", pob: full}
makes_redundant: []
conflicts:
  - {with: "Ghost Reaver 24426", effect: "Cannot Recharge Energy Shield", source: "TreeData/3_29/tree.lua:80291"}
  - {with: "Vaal Pact", effect: "life is recovered only from leech (see the Leech note)", source: "b1-tree-ascendancy-analyst.md"}
  - {with: "Zealot's Oath 63425", effect: "no life regeneration, regeneration goes to ES instead", source: "TreeData/3_29/tree.lua:26691"}
conditions:
  - {text: "over-time recovery is capped per 33 ms frame at the recoverable maximum; recovery rate mods multiply the pooled total and are multiplicative with more specific rate modifiers", source: "wiki Recovery rev 1618351; PoB multiplies per resource: Modules/CalcDefence.lua:1286-1287"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "regeneration has no condition; ES recharge works only after 2 s undamaged; use PoB's <Resource>Regen as the rate", source: "Modules/CalcDefence.lua:1235-1296; wiki Energy shield rev 1673450"}
  Pinnacle Boss: {value: partial, config: {}, reasoning: "regeneration always; recharge mostly down in boss damage phases", source: "Modules/CalcDefence.lua:1235-1296; wiki Energy shield rev 1673450"}
seeds: [Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Recovery (rev 1618351; no version table)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:1212-1217,1235-1296,1343-1400,2904-2966,3439-3525; Modules/ConfigOptions.lua:212,1432,1435; Data/Misc.lua:66 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua lines in the provider rows (PoB 2.67.2)", kind: pob, patch: "3.29"}
not_verified:
  - "Whether the generator should add regeneration and recharge to a survival model (project decision)"
  - "The Regeneration wiki page lists passives by cargo queries that did not render in wikitext, so the passive list comes from the tree only"
  - "Recoup and flask recovery were not read; the PoB parse status of Vampirism, Infused Flesh and Trial of the Faith (pob: none) was not checked"
  - "The default of lifeRegenMode and the conditionLeeching row were not read in this batch"
  - "Path costs d are raw tree adjacency, not PassiveSpec node.path"
open_questions:
  - "Should recovery be modelled at all next to max hit and EHP, given PoB leaves it out of both? Project decision for the user"
```
