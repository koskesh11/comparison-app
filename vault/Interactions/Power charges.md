---
type: interaction
status: draft
pob_refs: [usePowerCharges, overridePowerCharges, PowerChargesMax, PowerCharges, SupportPowerChargeOnCritical]
source: "PoB 2.67.2 ConfigOptions.lua / CalcPerform.lua; item-analyst, skill-gem-analyst, tree-ascendancy-analyst (task 027); tasks/reports/021-gate1.md N9"
last_confirmed_patch: "3.29.x"
---

Power charges count in PoB only when usePowerCharges is ticked (then max, or the override); gain on kill or crit is not parsed, except that the Power Charge On Critical gem is recognised. Max charges (PowerChargesMax) come from tree and items and feed other mechanics, e.g. [[Curse limit]] with Anathema, and [[Frenzy charges]] with Badge of the Brotherhood.

```interaction
id: power-charges
mechanic: "Power charges (crit chance / spell damage scaling per charge); PoB counts max charges only when usePowerCharges is ticked, gain is not modelled"
family: charge
target: self
related: [frenzy-charges, curse-limit, arcane-surge]
pob:
  measured: config
  how: "ConfigOptions.lua:900-905 -> CalcPerform.lua:987, 1046-1056; gain on kill/crit unparsed (parseMod returns no mods); only 'Power Charge On Critical' gem name recognised (ModParser.lua:2034). Minions: minionsUsePowerCharges (ConfigOptions.lua:976-990)"
  config:
    - {var: usePowerCharges, default: false, ref: "ConfigOptions.lua:900-905", class: b}
    - {var: overridePowerCharges, default: max, ref: "ConfigOptions.lua:900-905", class: c}
  unparsed:
    - "Anathema: (10-20)% chance to gain a Power Charge when you Cast a Curse Spell"
    - "Tulborn/Tulfall: Gain a Power Charge on Killing a Frozen Enemy"
    - "10% chance to gain a Power Charge on Kill (generic)"
model: null
providers:
  - {kind: unique, name: "Grand Spectrum (Cobalt)", slot: jewel, role: enables, target: self, text: "+1 to Minimum Power Charges per Grand Spectrum (variant 5); 25% inc crit chance per Grand Spectrum (variant 3); count + colours pinned, 3 needed", source: "PoB Data/Uniques/jewel.lua:225-226; Item.lua:2466, ModParser.lua:1463; 021-gate1 N9", pob: full}
  - {kind: unique, name: "Badge of the Brotherhood", slot: amulet, role: scales, target: self, text: "Max Frenzy = Max Power, so each +max power charge also raises Frenzy", source: "PoB Data/Uniques/amulet.lua:217", pob: full}
  - {kind: unique, name: "Anathema", slot: ring, role: applies, target: self, text: "(10-20)% chance to gain a Power Charge when you Cast a Curse Spell; curse limit = max power charges", source: "PoB Data/Uniques/ring.lua:646-647", pob: none}
  - {kind: support, name: "Power Charge On Critical", slot: any, role: applies, target: self, text: "54% (L20) chance per crit; 4% more damage per power charge; the only support that gives charges from a spell like Winter Orb", source: "PoB sup_int.lua:5593-5636, statMap 5604-5606", pob: partial}
  - {kind: mastery, name: "Caster Mastery effect 33089", slot: tree, role: applies, target: self, text: "Gain a Power Charge each second while Channelling a Spell (Worb node 14113)", source: "tree-ascendancy-analyst; TREE L31305", pob: none}
  - {kind: unique, name: "Ralakesh's Impatience (Power Current)", slot: boots, role: enables, target: self, text: "Count as having maximum number of Power Charges", source: "PoB Data/Uniques/boots.lua:935 (variant 5)", pob: full, variant: "Power Current"}
  - {kind: ascendancy, name: "Unstable Infusion 4242 (Assassin)", slot: tree, role: applies, target: self, text: "15% on crit, 30% on non-crit; +1 Maximum Power Charges", source: "tree-ascendancy-analyst; TREE L83536", pob: none}
  - {kind: notable, name: "Forbidden Power 62504 (Occultist)", slot: tree, role: scales, target: self, text: "+1 Max, 6% inc Damage and AoE per charge, a charge per 200 mana spent (FR seed)", source: "tree-ascendancy-analyst; TREE L44271", pob: partial}
  - {kind: unique, name: "Malachai's Loop", slot: shield, role: scales, target: self, text: "+2 Max Power Charges; 20% chance on Hit; (12-16)% inc Spell Damage per charge", source: "PoB Data/Uniques/shield.lua:669-674 (variant 4)", pob: partial}
  - {kind: unique, name: "Voll's Protector", slot: body, role: applies, target: self, text: "Gain a Power Charge for each Enemy you hit with a Critical Strike; 50% reduced max mana", source: "PoB Data/Uniques/body.lua:1154-1155", pob: none}
  - {kind: unique, name: "Skyforth", slot: boots, role: applies, target: self, text: "25% chance to gain a Power Charge on Critical Strike; no Life Regeneration", source: "PoB Data/Uniques/boots.lua:608-610", pob: none}
  - {kind: unique, name: "Tulborn / Tulfall", slot: wand, role: applies, target: self, text: "Gain a Power Charge on Killing a Frozen Enemy (Foulborn Tulborn removes it)", source: "PoB Data/Uniques/wand.lua:392-395, 413; Foulborn jsonc:617", pob: none}
makes_redundant:
  - {provider: "kill-based power charge generation", when: "Ralakesh Power Current worn or Grand Spectrum minimum charges", why: "'counts as maximum' / minimum charges make the charges always present for DPS", source: "boots.lua:935; jewel.lua:226"}
conflicts:
  - {with: "Rashkaldor's Patience variant 1", effect: "'Cannot gain Power Charges' line exists in variant 1 only, not in Current", source: "item-analyst; PoB amulet.lua:939-943"}
conditions:
  - {text: "Anathema reads PowerChargesMax, not the current count, so it works without the config tick", source: "CalcPerform.lua:3216-3218"}
  - {text: "Power Charge On Critical charges still count only if usePowerCharges is ticked", source: "pob-coverage-auditor (ModParser.lua:2034)"}
uptime:
  Mapping:       {value: high, config: {usePowerCharges: true}, reasoning: "Kill/crit/curse-cast sources keep charges up in maps; tick only when a gain source or 'counts as max' exists", source: "build-strategist table"}
  Pinnacle Boss: {value: partial, config: {usePowerCharges: "true for crit-based sources, 'count as max', or Power Charge On Critical with high crit; kill-based = none"}, reasoning: "Crit-based sources work on a boss, kill-based do not", source: "build-strategist table"}
seeds: [EK, FR, Worb]
sources:
  - {ref: "PoB ConfigOptions.lua:900-905, CalcPerform.lua:987, 1046-1056", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills/sup_int.lua:5593", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N9", kind: discovery, patch: "3.29"}
not_verified:
  - "PoB EnableCharges config interplay (stat exists on the tree)"
  - "Whether Worb PCoC (Power Charge On Critical) charges are reflected: PoB counts them only through the config tick"
open_questions:
  - "Worb: is usePowerCharges to be assumed on in both scenarios because PCoC + Caster Mastery give charges on crit/channel? (suggested yes, derived from sources)"
```
