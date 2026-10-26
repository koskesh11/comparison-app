---
type: interaction
status: draft
pob_refs: [CritChance, CritMultiplier, NoCritMultiplier, TotalDPS]
source: "b5c-ia2.md; PoB 2.67.2 Data/Uniques/amulet.lua:1167-1179, Modules/CalcOffence.lua:3204-3205, Modules/ModParser.lua:3563, Data/ModCache.lua lines per provider; poewiki Ungil's Harmony rev 1536199; vault note perfect-agony (headless FR / EK / Worb, 2026-10-26); b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Ungil's Harmony gives (250-350)% increased Global Critical Strike Chance and makes critical strikes deal no extra damage (flag NoCritMultiplier, CritMultiplier forced to 1 at CalcOffence.lua:3204-3205). For a build that is crit chance as a product: trigger rate (CoC), "crit recently" conditions, crit-gated ailments, or damage that is not a hit.
On a build that scales crit multiplier it is a pure loss (hit damage x4 when the flag is lifted, see removal). In the four measured sample builds the no-crit-multiplier line is worth 0.0%: Perfect Agony (node 23407) is allocated in all four and sets the same flag. The 82-91% figure in the vault perfect-agony note belongs to Perfect Agony, not to Ungil's Harmony.
All four samples are CoC (Cast on Critical Strike) + Perfect Agony poison builds; there is no non-CoC sample. What the item gives them is crit chance for the CoC trigger rate and crit-gated poison, not damage per hit.
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
  how: "Data/ModCache.lua:23021 parses 'Your Critical Strikes do not deal extra Damage' to flag NoCritMultiplier (ModParser.lua:3563); Modules/CalcOffence.lua:3204-3205 `if skillModList:Flag(cfg,'NoCritMultiplier') then output.CritMultiplier = 1`. Crit chance is the generic CritChance INC (ModCache.lua:8469, 8828). Wiki rev 1536199: each hit still calculates crit multiplier normally including conditional stats but cannot deal extra damage. Measured on 4 CoC + Perfect Agony samples (package.removal, b5c-ia2.md): the flag line is 0.0% in all four because node 23407 sets NoCritMultiplier too (sources read with skillModList:Tabulate FLAG NoCritMultiplier: the item and Tree:23407)."
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
  removal: "PoB removal/swap delta on 4 samples, scenario Pinnacle (enemyIsBoss Pinnacle) unless marked, FullDPS = calcFullDPS combined, b5c-ia2.md; amulet has no sockets, so no gem group stays active. All four are CoC + Perfect Agony builds (no non-CoC sample); FullDPS is 88-99% 'Full Poison DPS' in all four, hit skills are 0.6-2.2%. Rows in the order 3.27/CoC/Assa Ice Noca Spraying.xml (main Frostbolt via Awakened Cast On Critical Strike; Lancing Steel of Spraying, Ice Nova of Frostbolts) / League Start ScourgeArrow Ice Spear.xml (Scourge Arrow of Menace feeding Ice Spear) / 3.28/Poison Assa CoC.xml (Cyclone main, not triggered; Ice Nova of Frostbolts via CoC) / 3.26/CoC/Poison CoC PF.xml (Vortex of Projection via Awakened CoC). Whole amulet removed: -7.9% / -43.9% / -23.9% / -31.2% (Mapping -8.0% / -38.0% / -25.4% / -31.1%); it mixes the lines and the anoint (Allocates Divine Judgement -6.4% of the -7.9%; Allocates Whispers of Doom -30.6% of the -43.9%). Only the 'Your Critical Strikes do not deal extra Damage' line removed: 0.0% in all four, both scenarios. Only the crit chance line removed: -1.7% / -11.3% / -18.9% / -31.2% (Mapping -1.7% / -11.2% / -19.0% / -31.1%), all through the CoC trigger rate and crit-gated poison (CritMultiplier is 1 in every row). Trigger rate in /s, base -> crit line removed (TriggerRateCap): 7.501 -> 7.386 (7.576), 5.932 -> 5.579 (6.061), 7.676 -> 5.380 (10.101), Ice Nova 7.39 -> 6.09 (no cap, main skill not triggered): near the cap crit chance matters little for the trigger and still gates poison; far below the cap the crit line is the trigger rate. Other lines (FullDPS, Pinnacle): +Dex/Int implicit 0.0% / -8.9% (Dex 351 -> 328, Int 156 -> 133, cause not isolated) (measured on the first two samples only), +Life/+Mana 0.0% (same two samples; TotalEHP -0.9% to -1.6%). Perfect Agony deallocated with the amulet kept: -56.2% / -52.1% / -54.5% / -55.1% (Mapping -55.9% / -48.4% / -50.9% / -52.0%); Perfect Agony off AND the no-extra-damage line removed: hit TotalDPS x4.06 (Frostbolt), x3.68 (Ice Spear), x4.44 (Cyclone), x4.64 (Vortex of Projection) but FullDPS still -50.8% / -50.8% / -41.6% / -49.6%, because the poison DoT multiplier that Perfect Agony supplies (CritPoisonDotMulti 4.06 vs 1.72 without it) is gone. Harness note: rows use PoB's rebuild order with wipeGlobalCache (b5c-ia2.md Method); several samples carry unmet gem requirements in base (3.28 Poison Assa CoC 5, 3.26 PF 6), so their absolute numbers are weaker evidence. Headless single-enemy deltas, not game facts."
  downsides_that_are_the_point: ["crits deal no extra damage: the build must not need crit multiplier; on a hit build that scales crit multiplier it is a pure loss (about x4 on hit damage of the triggered spells when the flag is lifted, b5c-ia2.md). Perfect Agony sets the same flag, so in a Perfect Agony build this line costs nothing extra (0.0% in all 4 samples); the 82-91% in the vault perfect-agony note is Perfect Agony's cost, not Ungil's"]
  foulborn: "none (not in ModFoulbornMap)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level null, req 23, release 1.3.0; poewiki rev 1536199 (3.25.0: no longer shows 100% in the character screen; Divine Orb updates only the chance); patch 3.29"
makes_redundant:
  - {provider: "crit multiplier nodes / gear", when: "Ungil's Harmony is worn", why: "the multiplier is forced to 1", source: "Modules/CalcOffence.lua:3204-3205"}
  - {provider: "Perfect Agony (flag half) / Ungil's no-crit-multiplier line", when: "both present", why: "either source sets NoCritMultiplier; removing only Ungil's line changes nothing in 4 of 4 samples (0.0% FullDPS), because node 23407 sets it too", source: "b5c-ia2.md Result 1 (flag sources read with Tabulate FLAG NoCritMultiplier); Modules/CalcOffence.lua:3204-3205"}
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
  - {ref: "vault/Interactions/Perfect Agony.md (headless FR / EK / Worb, 2026-10-26): its 82-91% bound is the Perfect Agony flag, not Ungil's", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b5c-ia2.md (4 CoC + Perfect Agony samples, removal rows)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: an Ungil's-only hit-damage cost on a non-CoC, non-Perfect-Agony build: no such sample exists among the 4 (all CoC + Perfect Agony); only the x3.7-x4.6 hit TotalDPS ratio with Perfect Agony deallocated is measured"
  - "NOT VERIFIED: cause of the -8.9% on ScourgeArrow when only the +Dex/Int implicit is removed (Dex 351 -> 328, Int 156 -> 133) while main TotalDPS moves -0.5%; not isolated"
  - "NOT VERIFIED: the CoC source skill PoB picks per sample and the real CoC mechanics beyond TriggerRateCap / EffectiveSourceRate (CalcTriggers.lua:761-781, 884); poison stack counts come from config ticks (multiplierPoisonOnEnemy / AppliedRecently), not from hit rate"
  - "NOT VERIFIED: which engine consumers read CritMultiplier directly for non-hit effects (e.g. shock effect); not grepped"
open_questions: []
```
