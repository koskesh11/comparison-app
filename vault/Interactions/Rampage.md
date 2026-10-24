---
type: interaction
status: draft
pob_refs: [multiplierRampage, "Condition:Rampage", max_rampage_stacks]
source: "wiki Rampage rev 1702497; PoB 2.67.2 ConfigOptions.lua, CalcSetup.lua, ModParser.lua, Data/Misc.lua; headless probe on the Worb day-1 snapshot (2026-10-24); user statement 'always active' in mapping"
last_confirmed_patch: "3.29.x"
---

Rampage grants 2% increased Damage and 1% increased Movement Speed per 20 consecutive kills (cap 1000 = +100% damage, +50% movement speed). The counter resets to 0 when no kill happens within 5 seconds, so it is a mapping bonus and nothing on a lone boss. PoB shows 0 until the user types a kill count (config gap).

```interaction
id: rampage
mechanic: "Consecutive-kill counter (kills incl. minions and proxies); 2% increased Damage and 1% increased Movement Speed per 20 stacks, cap 1000; resets to 0 if no kill within 5 s; kills at cap renew the timer"
family: buff
target: self
related: [flask-uptime]
pob:
  measured: config
  how: "Condition:Rampage from the mod word (ModParser.lua:889, 4020, 6056); stacks only via config; damage/movement speed mods CalcSetup.lua:625-626 (limit 1000/20); floors the multiplier m_floor(base/div + 0.0001) (ModStore.lua:403); tier effects (13 tiers at 15..520 kills) not modelled; headless on the Worb day-1 snapshot TotalDPS: 0 -> 639,063; 100 -> 646,776 (+1.2%); 500 -> 677,629 (+6.0%); 1000 -> 716,162 (+12.1%)"
  config:
    - {var: multiplierRampage, default: 0, ref: "ConfigOptions.lua:994-995", class: c}
  unparsed: []
model:
  proposed_kind: rampage_stacks
  inputs: {from_pob_config: [multiplierRampage], from_scenario: [kills_per_streak_K]}
  params: {cap: 1000, reset_s: 5, kills_per_streak_K: null}
  formula: "avg_stacks = K/2 if K <= 1000 else 1000 - 500000/K (linear build-up then cap, time-average over one streak); feed multiplierRampage = floor(avg_stacks), replaces any hand-set value. Examples: K 2000 -> 750, K 500 -> 250"
  calibration: "no community norm found for mapping stacks (searched); K is a scenario input"
providers:
  - {kind: unique, name: "Bisco's Leash", slot: belt, role: enables, target: self, text: "Rampage; 1% increased Rarity per 15 Rampage Kills; +(10-15) all Attributes; +(20-40)% Cold Resistance", source: "PoB Data/Uniques/belt.lua:129-140 (variant Current); wiki Bisco's Leash 3.25.0", pob: config}
  - {kind: unique, name: "Wyrmsign", slot: gloves, role: enables, target: self, text: "Gain Rampage while at Maximum Endurance Charges; Lose all Endurance Charges when Rampage ends", source: "PoB Data/Uniques/gloves.lua:673-674", pob: config}
  - {kind: unique, name: "Sinvicta's Mettle", slot: axe, role: enables, target: self, text: "Rampage; 2% increased Area per 25 Rampage Kills; Gain a Frenzy Charge on every 50th Rampage Kill", source: "PoB Data/Uniques/axe.lua:395-397", pob: config}
  - {kind: unique, name: "The Dancing Dervish / Duo", slot: sword, role: applies, target: self, text: "Melee Hits count as Rampage Kills", source: "PoB Data/Uniques/sword.lua:772-776, 790-794", pob: none}
  - {kind: unique, name: "Flesh and Spirit / Null and Void / Shadows and Dust (legacy)", slot: gloves, role: enables, target: self, text: "League: Rampage", source: "PoB Data/Uniques/gloves.lua:549-556, 740-748, 1078-1092", pob: config}
makes_redundant: []
conflicts:
  - {with: "Mageblood", effect: "Bisco's Leash and Mageblood are both belts: one slot, you cannot have the rampage belt and the flask belt", source: "build-strategist.md; PoB Data/Uniques/belt.lua"}
conditions:
  - {text: "no Rampage stacks while an active killstreak exists but no source of Rampage is on the character (3.25.0; Dancing Dervish excepted)", source: "wiki Rampage rev 1702497"}
  - {text: "a boss fight without adds gives no new kills; stacks reset 5 s after the last kill", source: "wiki Rampage rev 1702497"}
uptime:
  Mapping:       {value: high, config: {multiplierRampage: "model: stacks parameter (open question), not auto 1000"}, reasoning: "user: Rampage is 'always active' in mapping. SUPPORTED for Condition:Rampage (the belt grants it); full +100% needs 1000 consecutive kills with gaps under 5 s, so the stack count is a parameter", source: "user statement 2026-10-24; wiki Rampage rev 1702497; ConfigOptions.lua:994-995"}
  Pinnacle Boss: {value: none, config: {multiplierRampage: 0}, reasoning: "no kills on a lone boss, counter resets after 5 s; partial only if the fight has add phases", source: "wiki Rampage rev 1702497"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Rampage (rev 1702497, 2026-09-20)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/ConfigOptions.lua:994-995; Modules/CalcSetup.lua:625-626; Data/Misc.lua:105-107; Classes/ModStore.lua:403", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/belt.lua:129-140", kind: pob, patch: "3.29"}
not_verified:
  - "any community norm for rampage stacks in mapping (searched, none found)"
  - "tier effects at 15..520 kills are not in PoB"
  - "that 3.29 changed nothing since 3.25.0 (wiki history lists nothing)"
  - "kills per second a Worb build sustains"
open_questions:
  - "Rampage stack count for the Mapping scenario: a fixed number (strategist suggests 300-500) or 1000?"
```
