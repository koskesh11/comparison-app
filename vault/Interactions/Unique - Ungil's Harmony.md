---
type: interaction
status: draft
pob_refs: [CritChance, CritMultiplier, NoCritMultiplier, TotalDPS]
source: "PoB 2.67.2 Data/Uniques/amulet.lua:1167-1179, Modules/CalcOffence.lua:3204-3205, Modules/ModParser.lua:3563, Data/ModCache.lua lines per provider; poewiki Ungil's Harmony rev 1536199; vault note perfect-agony (headless FR / EK / Worb, 2026-10-26); b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Ungil's Harmony gives (250-350)% increased Global Critical Strike Chance and makes critical strikes deal no extra damage (flag NoCritMultiplier, CritMultiplier forced to 1 at CalcOffence.lua:3204-3205). For a build that is crit chance as a product: trigger rate (CoC), "crit recently" conditions, crit-gated ailments, or damage that is not a hit.
On a build that scales crit multiplier it is a pure loss. The vault perfect-agony note measured forcing the same flag at 82-91% of hit DPS lost where the crit multiplier was 5.92 on FR; that is an upper bound, not an Ungil-only delta.
Uniques are packages: every line is valued, including the downside that is the point (no crit multiplier).

Pipeline: [[Damage calculation#Critical strike]] - crit chance up, multiplier forced to 1

```interaction
id: unique-ungils-harmony
mechanic: "Unique package: 250-350% increased crit chance with no extra crit damage - crit chance as trigger / condition source, not as damage"
family: trigger
pipeline_step: ["Damage calculation#Critical strike"]
pipeline_why: "the item raises crit chance in the increased pool and sets the NoCritMultiplier flag, which forces the crit multiplier to 1 in the critical strike step"
target: self
related: [critical-strike-chance, critical-strike-multiplier, perfect-agony, coc-trigger, lucky-critical-strikes]
pob:
  measured: full
  how: "Data/ModCache.lua:23021 parses 'Your Critical Strikes do not deal extra Damage' to flag NoCritMultiplier (ModParser.lua:3563); Modules/CalcOffence.lua:3204-3205 `if skillModList:Flag(cfg,'NoCritMultiplier') then output.CritMultiplier = 1`. Crit chance is the generic CritChance INC (ModCache.lua:8469, 8828). Wiki rev 1536199: each hit still calculates crit multiplier normally including conditional stats but cannot deal extra damage. Removal delta not measured here (no headless run); vault bound from the perfect-agony note in the prose."
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Ungil's Harmony", variant: "Current", slot: amulet, role: sustains, target: self, text: "Implicit: +(16-24) to Dexterity and Intelligence", source: "Data/Uniques/amulet.lua:1167-1179", pob: full}
  - {kind: unique, name: "Ungil's Harmony", variant: "Current", slot: amulet, role: scales, target: self, text: "(250-350)% increased Global Critical Strike Chance", source: "Data/ModCache.lua:8469, 8828 (CritChance INC, tag Global)", pob: full}
  - {kind: unique, name: "Ungil's Harmony", variant: "Current", slot: amulet, role: sustains, target: self, text: "+(30-50) to maximum Life / Mana", source: "Data/ModCache.lua:1754", pob: full}
  - {kind: unique, name: "Ungil's Harmony", variant: "Current", slot: amulet, role: sustains, target: self, text: "40% increased Stun and Block Recovery", source: "Data/ModCache.lua:9401", pob: full}
  - {kind: unique, name: "Ungil's Harmony", variant: "Current", slot: amulet, role: blocks, target: self, text: "Your Critical Strikes do not deal extra Damage (also enables crit as a trigger / condition source)", source: "Data/ModCache.lua:23021; Modules/ModParser.lua:3563; Modules/CalcOffence.lua:3204-3205", pob: full}
package:
  seed: none
  slot: "Amulet"
  base: "Turquoise Amulet (req 23)"
  variant: "Current; a 'Pre 3.11.0' variant exists (then -25% crit multiplier, changed to 'no extra damage' in 3.11.0)"
  removal: "NOT MEASURED"
  downsides_that_are_the_point: ["crits deal no extra damage: the build must not need crit multiplier; on a hit build that scales crit multiplier it is a pure loss (vault perfect-agony note: the same flag inside Perfect Agony cost 82-91% hit DPS at crit multi 5.92 on FR, FullDPS 57,001,026 -> 8,652,487; upper bound, includes Perfect Agony's other effects, not re-run)"]
  foulborn: "none (not in ModFoulbornMap)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level null, req 23, release 1.3.0; poewiki rev 1536199 (3.25.0: no longer shows 100% in the character screen; Divine Orb updates only the chance); patch 3.29"
makes_redundant:
  - {provider: "crit multiplier nodes / gear", when: "Ungil's Harmony is worn", why: "the multiplier is forced to 1", source: "Modules/CalcOffence.lua:3204-3205"}
  - {provider: "Perfect Agony (flag half)", when: "Ungil's Harmony is worn", why: "the NoCritMultiplier flag is already set; no gain from a second source", source: "Modules/CalcOffence.lua:3204-3205"}
conflicts:
  - {with: "any crit-multiplier scaling (Assassin's Mark multiplier, power-charge crit multiplier)", effect: "no effect on damage", source: "Modules/CalcOffence.lua:3204-3205"}
  - {with: "Elemental Overload", effect: "no crits, so the crit chance line has no use", source: "b2c-item-analyst-leaguestart.md (partly)"}
conditions:
  - {text: "none; crit chance is a plain global INC and the flag is unconditional", source: "Data/ModCache.lua:8469, 23021"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "PoB uses output.CritChance with hit chance; no scenario field", source: "Modules/CalcOffence.lua:3204-3205"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same as Mapping", source: "Modules/CalcOffence.lua:3204-3205"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Ungil%27s_Harmony (rev 1536199)", kind: wiki, patch: "3.25"}
  - {ref: "PoB Data/Uniques/amulet.lua, Modules/CalcOffence.lua, Modules/ModParser.lua, Data/ModCache.lua", kind: pob, patch: "3.29"}
  - {ref: "vault/Interactions/Perfect Agony.md (headless FR / EK / Worb, 2026-10-26)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: an Ungil's-only delta (the 82-91% above includes Perfect Agony's other effects); removal delta not measured"
  - "NOT VERIFIED: which engine consumers read CritMultiplier directly for non-hit effects (e.g. shock effect); not grepped"
open_questions: []
```
