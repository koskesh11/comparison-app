---
type: interaction
status: draft
pob_refs: [EnemyCurseLimit, CurseLimitIsMaximumPowerCharges, PowerChargesMax]
source: "PoB 2.67.2 CalcPerform.lua:3216 / ModParser.lua:4086-4166; poewiki Curse (rev 1675786), Anathema (rev 1675513); item-analyst, skill-gem-analyst, tree-ascendancy-analyst (task 027)"
last_confirmed_patch: "3.29.x"
---

By default one curse can be active on an enemy (marks are separate). Anathema REPLACES the curse limit with your maximum power charges, so every "additional curse" item or node is wasted while it is worn, and zero max charges means no curses at all. Wiki and PoB disagree on the Moonstone Ring implicit at 3.29 (see not_verified); both are kept.

Pipeline: [[Damage calculation#Resistance, exposure and penetration]], [[Damage calculation#Damage taken]] - curses act through enemy resistance and damage taken; the limit only gates how many of those debuffs apply, so an extra curse is worth nothing when Anathema replaces the limit

```interaction
id: curse-limit
mechanic: "Enemy curse limit is 1 by default; +1 per 'additional Curse'; Anathema sets it to maximum Power Charges, overriding all other modifiers; limit 0 = curses do not apply"
family: buff
pipeline_step: ["Damage calculation#Resistance, exposure and penetration", "Damage calculation#Damage taken"]
pipeline_why: "curses act through enemy resistance and damage taken; the limit only gates how many of those debuffs apply, so an extra curse is worth nothing when Anathema replaces the limit"
target: enemy
related: [power-charges, coc-trigger]
pob:
  measured: full
  how: "CalcSetup.lua:632 (EnemyCurseLimit BASE 1); ModParser.lua:4086-4092 (additional curse), 4166 (flag CurseLimitIsMaximumPowerCharges); CalcPerform.lua:3216 'output.EnemyCurseLimit = modDB:Flag(nil, CurseLimitIsMaximumPowerCharges) and output.PowerChargesMax or modDB:Sum(...)'; slot processing 3226-3311; display CalcSections.lua:797-799"
  config: []
  unparsed:
    - "Anathema: (10-20)% chance to gain a Power Charge when you Cast a Curse Spell"
model: null
providers:
  - {kind: unique, name: "Anathema (Moonstone Ring)", slot: ring, role: abuses, target: enemy, text: "Your Curse Limit is equal to your maximum Power Charges; +(30-40) Int; (10-15)% inc Cast Speed; (10-20)% chance to gain a Power Charge when you Cast a Curse Spell", source: "PoB Data/Uniques/ring.lua:639-647; wiki Anathema rev 1675513; ModParser.lua:4166", pob: partial, variant: "Foulborn replaces the power-charge line with 'Curse Skills have (-30-30)% reduced/increased Skill Effect Duration' (jsonc:637); limit line stays, charge generator lost"}
  - {kind: ascendancy, name: "Ascendant/Occultist 12597", slot: tree, role: enables, target: enemy, text: "You can apply an additional Curse", source: "tree-ascendancy-analyst; TREE L19082; ModParser.lua:4086-4088", pob: full}
  - {kind: notable, name: "Unholy Authority 31344 (Occultist)", slot: tree, role: enables, target: enemy, text: "additional Curse; Hexes affect Hexproof", source: "tree-ascendancy-analyst; TREE L44510", pob: full}
  - {kind: notable, name: "Whispers of Doom 22535", slot: tree, role: enables, target: enemy, text: "You can apply an additional Curse", source: "tree-ascendancy-analyst; TREE L73135", pob: full}
  - {kind: unique, name: "Cospri's Will", slot: body, role: enables, target: enemy, text: "additional curse (variant 3)", source: "PoB Data/Uniques/body.lua:290", pob: full}
  - {kind: unique, name: "Windscream", slot: boots, role: enables, target: enemy, text: "additional curse; +50% Hex AoE (variant 3)", source: "PoB Data/Uniques/boots.lua:198", pob: full}
  - {kind: unique, name: "Vixen's Entrapment", slot: gloves, role: enables, target: enemy, text: "additional curse; also triggers a Socketed Curse Spell", source: "PoB Data/Uniques/gloves.lua:194", pob: full}
  - {kind: unique, name: "Doedre's Damning", slot: ring, role: enables, target: enemy, text: "additional curse (variant 2); Replica -1", source: "PoB Data/Uniques/ring.lua:453; wiki Curse", pob: full}
  - {kind: unique, name: "Doedre's Skin", slot: body, role: enables, target: enemy, text: "Hexes from Socketed Skills can apply 5 additional Curses (bypasses the limit)", source: "PoB Data/Uniques/body.lua:615; ModParser.lua:5347", pob: full}
  - {kind: unique, name: "Sentari's Answer", slot: shield, role: enables, target: enemy, text: "curse on block, ignores the limit", source: "PoB Data/Uniques/shield.lua:777-779", pob: full}
  - {kind: support, name: "Blasphemy", slot: any, role: scales, target: enemy, text: "hex becomes an aura; curse auras override on-hit/triggered curses when the limit is full; -25% curse effect final", source: "PoB sup_int.lua:364-412; wiki Curse rev 1675786", pob: partial}
  - {kind: support, name: "Power Charge On Critical", slot: any, role: sustains, target: self, text: "feeds charges but the limit reads MAX charges, not current", source: "skill-gem-analyst; CalcPerform.lua:3216", pob: full}
makes_redundant:
  - {provider: "additional-curse items and nodes (Unholy Authority, Whispers of Doom, Cospri's Will, Windscream, Vixen's Entrapment, Doedre's Damning, Ascendant/Occultist 12597)", when: "Anathema equipped", why: "the flag REPLACES the sum, so every +1 limit is wasted; the limit rises only with max Power Charges. Doedre's Skin and Sentari's Answer bypass the limit and stay useful", source: "CalcPerform.lua:3216; wiki Curse rev 1675786 ('overriding all other modifiers')"}
conflicts:
  - {with: "Anathema with 0 maximum Power Charges (CI/charge-less builds)", effect: "curse limit 0: casting a curse applies nothing", source: "wiki Curse rev 1675786"}
  - {with: "Hex Master (keystone)", effect: "Your Hexes have infinite Duration, 20% less Effect of your Curses", source: "tree-ascendancy-analyst; TREE L63127"}
conditions:
  - {text: "marks are limited to one per target even with additional curse limit and are not covered by the curse limit", source: "wiki Curse rev 1675786"}
  - {text: "theoretical maximum limit 10", source: "wiki Curse rev 1675786"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Static: Anathema reads max power charges (PowerChargesMax from tree/items), works without the usePowerCharges tick", source: "build-strategist table; CalcPerform.lua:3216"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "Static, same as Mapping", source: "build-strategist table"}
seeds: [FR]
sources:
  - {ref: "PoB CalcPerform.lua:3216-3218, ModParser.lua:4086-4166, CalcSetup.lua:632", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Curse (rev 1675786)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Anathema (rev 1675513)", kind: wiki, patch: "3.29"}
not_verified:
  - "READING CONFLICT wiki vs PoB (Anathema): wiki 3.29.0 says the Moonstone Ring implicit is now 7-10% increased Cast Speed (not affecting existing rings); PoB Data/Bases/ring.lua:81 has the new implicit but the Anathema entry (ring.lua:641-643) still declares +(15-25) max Energy Shield. A new Anathema has the cast speed implicit; PoB shows the old one"
  - "Whether PoB's Anathema limit uses max power charges at 3.29 total (formula read, not a headless run)"
  - "How PoB treats hex limits when Blasphemy auras exceed the limit (CalcPerform.lua:3226-3311 not traced)"
open_questions:
  - "Anathema implicit: should the generator trust PoB's old ES implicit or the wiki's cast speed implicit when evaluating a fresh Anathema?"
```
