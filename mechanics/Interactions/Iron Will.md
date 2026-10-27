---
type: interaction
status: draft
pob_refs: [IronWill, strDmgBonus, StrDmgBonusRatioOverride, Str, Damage, CombinedDPS, FullDPS, enemyIsBoss]
source: "poewiki Iron Will rev 1444411, Strength rev 1594712, Ignite rev 1598418, Version 3.16.0 rev 1650091 (fetched 2026-10-26); PoB 2.67.2 TreeData 3_29 tree.lua, Modules/CalcOffence.lua, CalcPerform.lua, ModParser.lua, Data/ModCache.lua, Data/SkillStatMap.lua, Data/Skills/sup_str.lua; headless runs on EK, Worb, FR and the Fireball seed (scratchpad b3c/D_run_*.json, D_if_*.json)"
last_confirmed_patch: "3.29.x"
---

Iron Will (keystone) makes the Strength bonus apply to all Spell Damage: 1% increased Spell Damage per 5 Strength (floor), added to the normal increased-damage pool of every spell, all damage types. It needs no config and no condition, so it is the safe, always-on Strength payoff for a spell build. The value is small and shrinks with the increased damage the build already has: +5.0% on EK (Str 179), +3.1% on Worb (Str 179), +3.0% on FR (Str 159), +1.5% on the Fireball seed (Str 74). It does not scale ignite, bleed or poison (hit-only spell modifier). The Iron Will support gem, the Repentance gloves and this keystone are the same flag and do not stack.

Pipeline: [[Damage calculation#Increased and reduced]] - the keystone adds one INCREASED Damage line (value floor(Str/5), flag Spell, source 'Strength') into the skill's increased pool (CalcOffence.lua:540-542), so its worth is 1/(1+total increased) per point and falls as the build stacks more increased damage; contrast [[Damage calculation#More and less]].

Measured (headless, in memory, nothing saved; Iron Will added as the custom line 'Iron Will' = keystone only, path cost not included; '+50 Str' = custom line '+50 to Strength'; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle; Worb with Aspect of the Brine King left out, Winter Orb gem count 5 as in the file):

| Seed | Str / bonus | metric | scenario | base | with Iron Will | delta | with IW and +50 Str | +50 Str on top of IW |
|---|---|---|---|---|---|---|---|---|
| EK | 179 / 35 | CombinedDPS | Pinnacle | 15,084,434 | 15,839,714 | +5.01% | 16,055,767 | +1.36% |
| EK | 179 / 35 | CombinedDPS | None | 14,370,752 | 15,087,439 | +4.99% | 15,292,450 | +1.36% |
| Worb | 179 / 35 | CombinedDPS | Pinnacle | 1,343,498 | 1,385,752 | +3.15% | 1,397,749 | +0.87% |
| Worb | 179 / 35 | CombinedDPS | None | 1,934,211 | 1,995,045 | +3.15% | 2,012,316 | +0.87% |
| FR | 159 / 31 | FullDPS | Pinnacle | 57,001,026 | 58,698,362 | +2.98% | 59,246,127 | +0.93% |
| FR | 159 / 31 | FullDPS | None | 67,300,152 | 69,304,221 | +2.98% | 69,950,951 | +0.93% |
| Fireball (not a validator seed) | 74 / 14 | CombinedDPS | Pinnacle | 285,468 | 289,741 | +1.50% | 296,423 | +2.31% (includes the build's own Str line, see below) |
| Fireball (not a validator seed) | 74 / 14 | CombinedDPS | None | 390,510 | 395,999.9 | +1.41% | 404,992 | +2.27% |

- Value per Strength, read from the +50 Str column: one increased point (5 Str) is worth +0.136% DPS on EK, +0.087% on Worb, +0.093% on FR, +0.10% on the Fireball seed (Iron Will points measured against Str +50 alone, 24 points: +2.54% Pinnacle, +2.38% None), i.e. about +0.027%, +0.017%, +0.019%, +0.02% DPS per Strength at today's Str. The Strength must come from gear or tree; its own price is not in these numbers.
- Where the points go: EK increased Damage on the main skill 304 -> 339 (+35) -> 349 with +50 Str; Worb 386 -> 421; the DPS gain is smaller than 35/(1+3.04) because elemental and type-specific increased lines sit in the same pool.
- FR: the main skill Cyclone is an attack, so CombinedDPS is unchanged by Iron Will (+0.00%); the gain is in the Cast On Critical Strike spell Forbidden Rite (+2.99%) inside FullDPS. EK: Ethereal Knives +4.92%, Full Impale DPS +5.10%, Cyclone 0%.
- Fireball: Str +50 alone is already +1.27% because the build has a second Strength-scaling line (Tree:4492, Damage INC per lowest attribute, Str is its lowest attribute); the two add (inc 347 -> 381 with both, +14 from Iron Will at Str 74 and +10 from the other line at Str 124).
- With The Iron Fortress line ('Strength's Damage Bonus instead grants 3% increased Melee Physical Damage per 10 Strength', custom line, StrDmgBonusRatioOverride 0.3): the bonus becomes floor(Str x 0.3), Str 179 -> 53 (not 35). Iron Will + that line: EK +7.58% (Pinnacle) / +7.55% (None) CombinedDPS, Worb +4.76%, FR +4.52% (FullDPS); the line alone changes EK by 0.00% and Worb by 0.00% (spell builds), FR Cyclone +0.10% (melee physical).

```interaction
id: iron-will
mechanic: "Keystone: Strength's Damage bonus applies to all Spell Damage as well. The Strength bonus is 1% increased Melee Physical Damage per 5 Strength (floor); Iron Will adds the same number as increased Damage (all types) with the Spell flag. Same keyword as the Iron Will support gem, Repentance and Doon Cuebiyari's support: they do not stack (wiki). Modifiers to the Strength bonus (The Iron Fortress: 3% per 10 Strength) carry over. Hit-specific: ailment damage (ignite, bleed, poison) is not scaled"
family: buff
target: self
related: [damage-calculation, ignite, spell-impale]
pipeline_step: ["Damage calculation#Increased and reduced"]
pipeline_why: "CalcOffence.lua:540-542 adds Damage INC floor(Str/5) with ModFlag.Spell to the skill's mod list when the IronWill flag is set; it is one more line in the increased pool (sum of all increases, then multiplied with the more-product), so each point is worth 1/(1+total increased) of the base."
pob:
  measured: full
  how: "Keystone = ModCache.lua:17274 (Keystone LIST + Condition:HaveIronWill); effect = ModCache.lua:21889 / ModParser.lua:2225 (flag IronWill); actor.strDmgBonus = floor((Str + DexIntToMeleeBonus) / 5), or floor(... x StrDmgBonusRatioOverride) when an override like The Iron Fortress is set (CalcPerform.lua:522-526); CalcOffence.lua:540-542: Flag(IronWill) -> NewMod('Damage','INC', strDmgBonus, 'Strength', ModFlag.Spell). The support gem sets the same flag through stat strong_casting (Data/SkillStatMap.lua:1227-1229) on the supported skill only. Measured on EK, Worb, FR, Fireball: table above. NOT modelled / not tested: minion spells (the bonus is built from the player's actor), Iron Will on attack skills (flag Spell only), exact in-game rounding when Strength changes in a fight."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (enemy level 84; None = 85)", ref: "headless env.enemyLevel; Modules/ConfigOptions.lua:2086", class: b}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Iron Will", slot: tree, role: applies, target: self, text: "Strength's Damage bonus applies to all Spell Damage as well (central tree, west of the Scion start; distance 8 from Scion, 10 from Templar and Marauder)", source: "TreeData/3_29/tree.lua:45328, 45332; Data/ModCache.lua:17274, 21889; wiki Iron Will rev 1444411", pob: full}
  - {kind: support, name: "Iron Will Support", slot: any, role: applies, target: self, text: "supported spell skill gets the same effect; 0-40% increased Spell Damage by gem level, manaMultiplier 10 (110% cost); does not stack with the keystone", source: "Data/Skills/sup_str.lua:3138-3175; Data/SkillStatMap.lua:1227-1229; wiki Iron Will rev 1444411", pob: full}
  - {kind: unique, name: "Repentance", slot: Gloves, role: applies, target: self, text: "Iron Will (keystone line; variant 1 also (0-30)% reduced Spell Damage)", source: "Data/Uniques/gloves.lua:762-773; Modules/ModParser.lua:5287; wiki cargo items", pob: full}
  - {kind: unique, name: "Doon Cuebiyari", slot: Sceptre, role: applies, target: self, text: "Socketed Gems are Supported by Level 30 Iron Will", source: "Data/Uniques/mace.lua:468-476; Data/ModItemExclusive.lua:3969", pob: full}
  - {kind: unique, name: "Skin of the Lords", slot: Body Armour, role: applies, target: self, text: "Random keystone list includes Iron Will (added to the Skin pool in 3.16.0)", source: "wiki cargo items query 2026-10-26; wiki Version 3.16.0 rev 1650091", pob: partial}
  - {kind: tattoo, name: "Iron Will tattoo (Hinekora keystone tattoo)", slot: tree, role: applies, target: self, text: "keystone tattoo of Iron Will", source: "Data/TattooPassives.lua:1263-1280", pob: partial}
  - {kind: mod, name: "Crucible weapon tree node", slot: weapon, role: applies, target: self, text: "WeaponTreeKeystoneIronWill: Iron Will spawns on wand, staff, sceptre, dagger, claw weapon trees", source: "Data/Crucible.lua:1368", pob: partial}
  - {kind: unique, name: "The Iron Fortress", slot: Body Armour, role: scales, target: self, text: "Strength's Damage Bonus instead grants 3% increased Melee Physical Damage per 10 Strength (0.3 per Str instead of 0.2) and +(60-120) Strength; Iron Will inherits the larger number (measured: Str 179 -> bonus 53)", source: "Data/Uniques/body.lua:160-168; Data/ModCache.lua:21886; Modules/CalcPerform.lua:522-526; wiki Iron Will rev 1444411", pob: full}
  - {kind: unique, name: "Iron Heart", slot: Body Armour, role: scales, target: self, text: "same Strength's Damage Bonus line; PoB data marks it 'No longer obtainable'", source: "Data/Uniques/body.lua:149-157", pob: full}
makes_redundant:
  - {provider: "Iron Will Support (gem)", when: "the keystone is allocated or Repentance is worn", why: "all three set the same IronWill flag (a boolean), a second source adds nothing; the gem would only keep its own spell_damage_+% line", source: "wiki Iron Will rev 1444411 ('will not stack'); Modules/CalcOffence.lua:540; Data/SkillStatMap.lua:1229"}
conflicts:
  - {with: "builds that take no Strength", effect: "value scales with Strength: Str 74 gave +1.5%, Str 179 gave +5.0% (EK); with low Strength the keystone is dead weight", source: "headless Fireball vs EK rows"}
  - {with: "ailment-based damage (ignite, bleed, poison)", effect: "Spell Damage modifiers are hit-specific; ailment DPS is not scaled", source: "wiki Ignite rev 1598418; PoB flags Spell (CalcOffence.lua:541)"}
conditions:
  - {text: "1% increased Spell Damage per 5 Strength; the Strength bonus is 1% increased melee physical damage per 5 Strength (every 5 Strength)", source: "wiki Iron Will rev 1444411; wiki Strength rev 1594712; Modules/CalcPerform.lua:526"}
  - {text: "applies to all spell damage, not just physical (the PoB line has no damage type, only the Spell flag)", source: "wiki Iron Will rev 1444411; Modules/CalcOffence.lua:541"}
  - {text: "keyword Iron Will does not stack with other sources (support gem, Repentance); effects that change the Strength bonus (The Iron Fortress) also change the Iron Will bonus", source: "wiki Iron Will rev 1444411; headless: Iron Will + Iron Fortress line = bonus 53 at Str 179"}
  - {text: "introduced as a keystone in 3.16.0; before it was an item keyword since 2.1.0", source: "wiki Iron Will rev 1444411 (Version history)"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "a passive keystone with no condition and no config; PoB computes it from the Strength total", source: "Modules/CalcOffence.lua:540-542; headless 4 seeds"}
  Pinnacle Boss: {value: always, config: {enemyIsBoss: "Pinnacle (level 84)"}, reasoning: "same; enemy level changes the base DPS only (EK +5.01% at Pinnacle vs +4.99% at None)", source: "headless EK/Worb/FR/Fireball, Pinnacle and None rows"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Iron_Will (rev 1444411)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Strength (rev 1594712)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ignite (rev 1598418)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.16.0 (rev 1650091): Skin of the Lords keystone pool incl. Iron Will", kind: patch_notes, patch: "3.16.0"}
  - {ref: "wiki cargo passive_skills: stat text 'Strength's Damage bonus applies to all Spell Damage as well', is keystone = 1 (global passive stat, not an item-local mod)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:45328-45332; Data/ModCache.lua:17274, 21886, 21889; Modules/ModParser.lua:2225, 5287; Modules/CalcOffence.lua:540-542; Modules/CalcPerform.lua:522-528; Data/SkillStatMap.lua:1227-1229; Data/Skills/sup_str.lua:3138-3175", kind: pob, patch: "3.29"}
not_verified:
  - "whether the Iron Will bonus reaches minion spells (PoB builds actor.strDmgBonus per actor; minion actors were not tested)"
  - "whether in the game the bonus also scales spell damage over time that is not an ailment; PoB scales it through the Spell flag, the wiki says 'all spell damage'"
  - "the unique items that carry the item-exclusive Iron Will mods KeystoneIronWillUnique_1 and VillageIronWill (Data/ModItemExclusive.lua:5227, 8156) were not traced"
  - "the Skin of the Lords keystone pool is read from the wiki (3.16.0 note and cargo), not from the PoB uniques file"
  - "tattoo and Crucible providers were not run headless"
open_questions: []
```
