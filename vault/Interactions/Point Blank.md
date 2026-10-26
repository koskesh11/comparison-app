---
type: interaction
status: draft
pob_refs: [PointBlank, projectileDistance, DistanceRamp, skillDist, Condition:HavePointBlank, TotalDPS, CombinedDPS, FullDPS, enemyIsBoss]
source: "poewiki Point Blank rev 1444227, Version 3.9.0 rev 1464805 (fetched 2026-10-26); PoB 2.67.2 TreeData 3_29 tree.lua, Modules/CalcOffence.lua, CalcActiveSkill.lua, ConfigOptions.lua, ModParser.lua, Classes/ModStore.lua, Data/ModCache.lua, Data/Skills/sup_dex.lua; headless runs on EK, Worb, FR and the Fireball seed (all 0.00%) plus two non-seed control builds (Toxic Rain attack, Ice Spear spell); scratchpad b3c/D_run_*.json, D_pb_*.json"
last_confirmed_patch: "3.29.x"
---

Point Blank (keystone) is a distance-based damage multiplier for projectile ATTACKS only: up to 30% more damage when the projectile has travelled 10 units or less, 0% at 35 units, up to 30% less from 120 units on (10 units = 1 metre). It does nothing for spells, so on every spell seed (EK Ethereal Knives, Worb Winter Orb, FR Forbidden Rite and the Cyclone attack, Fireball seed) PoB shows exactly 0.00% at every distance. On a real projectile attack PoB's number depends entirely on the config 'Projectile travel distance': unset, PoB assumes 40 units and Point Blank shows -2.1% (a loss), at 10 units or less +30.0%. A generator must set the distance from the intended play style, or the keystone is judged on a placeholder.

Pipeline: [[Damage calculation#More and less]] - Point Blank is a MORE modifier on Damage with flags Attack and Projectile and a DistanceRamp tag (CalcOffence.lua:1082-1083), so it multiplies with the other more-modifiers and with [[Projectile hits single target]]-style projectile counts without changing them; the wiki treats Point Blank and Far Shot as separate multiplicative terms.

Measured (headless, in memory, nothing saved; keystone added as the custom line 'Point Blank' = keystone only, path cost not included; config projectileDistance 5 / 40 / 120; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle; Worb with Aspect of the Brine King left out, Winter Orb gem count 5 as in the file):

| Seed | main skill (flags) | PoB value of Point Blank: CombinedDPS and FullDPS x Pinnacle and None x distance unset / 5 / 40 / 120 = 16 cells |
|---|---|---|
| EK | Ethereal Knives (projectile, spell) | 0.000% in all 16 cells |
| Worb | Winter Orb (projectile, spell) | 0.000% in all 16 cells |
| FR | Cyclone (melee attack, no projectile flag); triggered Forbidden Rite (spell) | 0.000% in all 16 cells |
| Fireball (not a validator seed) | Fireball (projectile, spell) | 0.000% in all 16 cells |

The flag is set (skillModList Flag PointBlank = true) and skillDist follows the config, but the Damage MORE line carries ModFlag.Attack, so a spell never matches it: the skill's Damage more product is unchanged (EK 1.395, Worb 1.9488, Fireball seed 0.74, with and without the keystone), while the Toxic Rain control below shows the line when the skill is an attack.

Controls with a real projectile attack and a projectile spell (not seeds; read-only user builds opened headless, nothing saved): 3.28/Toxic Rain.xml (Toxic Rain, projectile attack; TotalDPS is the hit part, 2,608.9 at Pinnacle base) and League Start ScourgeArrow Ice Spear.xml (Ice Spear, projectile spell).

| Toxic Rain, projectileDistance | Point Blank more line | TotalDPS Pinnacle (level 84) | delta | TotalDPS None (level 85) | delta |
|---|---|---|---|---|---|
| keystone off | none | 2,608.9 | 0 | 3,780.7 | 0 |
| unset (PoB placeholder 40) | -1.76% | 2,553.6 | -2.12% | 3,700.7 | -2.12% |
| 0, 5 or 10 | +30.00% | 3,391.7 | +30.01% | 4,915.0 | +30.00% |
| 22 | +15.60% | 3,020.7 | +15.78% | 4,377.4 | +15.78% |
| 35 | 0 | 2,608.9 | 0.00% | 3,780.7 | 0.00% |
| 77 | -14.82% | 2,210.5 | -15.27% | 3,203.4 | -15.27% |
| 120 or more | -30.00% | 1,825.5 | -30.03% | 2,645.6 | -30.02% |

- Ice Spear (projectile spell) with Point Blank: 31,670.6 -> 31,670.6 at Pinnacle and 68,655.1 -> 68,655.1 at None, distance 5: 0.000%. Confirms attack-only on a skill that has the projectile flag.
- The deltas differ slightly from the raw line (-2.12% DPS for a -1.76% line) because PoB rounds each layer's more-product to the nearest percent (Classes/ModList.lua:147, ModDB.lua:196): the skill-layer line x0.9824 becomes x0.98, so the control build's total more product goes 1.12 -> 1.0976; at 22 units 1.156 becomes 1.16.
- Ramp as coded: {{10,1},{35,0},{120,-1}} x 30% (CalcOffence.lua:1083); the wiki table is 1.3 at 0 and 10, 1.0 at 35, 0.7 at 120+, linear in between: they agree, including the 15.6% at 22 units.

```interaction
id: point-blank
mechanic: "Keystone: Projectile Attack Hits deal up to 30% more Damage at the start of their travel, less as the projectile travels farther: x1.30 at 0-10 units, x1.00 at 35, x0.70 at 120+ (10 units = 1 m; linear between; total path length, not distance from the caster). Attacks only (also projectile parts of melee attacks such as Lightning Strike); spells are not affected. Point Blank Support does not stack with it. PoB: Damage MORE 30 with flags Attack+Projectile and a DistanceRamp tag; distance comes from the config 'Projectile travel distance' (default placeholder 40 units = -1.76%)"
family: projectile
target: enemy
related: [projectile-hits-single-target, returning-projectiles, damage-calculation]
pipeline_step: ["Damage calculation#More and less"]
pipeline_why: "CalcOffence.lua:1081-1084 adds Damage MORE 30 (source 'Point Blank', flags Attack and Projectile, tag DistanceRamp) to the skill's mod list for projectile skills when the PointBlank flag is set; ModStore.lua:598-615 scales the value by the ramp at cfg.skillDist, so it is one more factor in the more-product, evaluated per skill at the configured distance, before crit and enemy mitigation."
pob:
  measured: config
  how: "Keystone = ModCache.lua:18583 (Keystone LIST + Condition:HavePointBlank); effect = ModCache.lua:18684 / ModParser.lua:2315 (flag PointBlank). CalcOffence.lua:1081-1087: for skillFlags.projectile, NewMod('Damage','MORE',30,'Point Blank', Attack|Projectile, DistanceRamp {{10,1},{35,0},{120,-1}}); Far Shot is the mirror line (+100% ramp {10,-0.2},{25,0},{70,0.6}). skillCfg.skillDist = effectiveRange only in effective mode (CalcActiveSkill.lua:455-460, CalcSetup.lua:574), effectiveRange = config projectileDistance or placeholder (ConfigOptions.lua:1790, defaultPlaceholderState 40; melee skills use meleeDistance). ModStore.lua:598-615 evaluates the ramp (no skillDist -> the line is skipped). Measured: 0.000% on EK, Worb, FR and the Fireball seed; Toxic Rain attack: +30.0% at <= 10, -2.1% at the placeholder 40, -30.0% at >= 120. NOT modelled: per-hit distance (one number per skill), pierce/fork/chain/return path length (wiki: total distance travelled), Rain of Arrows style area splash distance, a fight where the distance changes."
  config:
    - {var: projectileDistance, default: "unset = placeholder 40 units (4 m)", ref: "Modules/ConfigOptions.lua:1790 (shown when the build has a DistanceRamp tag and a projectile skill); Modules/CalcActiveSkill.lua:459", class: c}
    - {var: enemyIsBoss, default: "Pinnacle (enemy level 84; None = 85)", ref: "headless env.enemyLevel; Modules/ConfigOptions.lua:2086", class: b}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Point Blank", slot: tree, role: applies, target: enemy, text: "Projectile Attack Hits deal up to 30% more Damage to targets at the start of their movement, dealing less Damage as the projectile travels farther (south-east edge of the tree; distance 8 from Scion, 10 from Ranger and Shadow)", source: "TreeData/3_29/tree.lua:68886, 68890; Data/ModCache.lua:18583, 18684; wiki Point Blank rev 1444227", pob: config}
  - {kind: support, name: "Point Blank Support", slot: any, role: applies, target: enemy, text: "supports ranged attacks; keystone_point_blank -> same PointBlank flag, plus its own increased Projectile Damage (0-46% by gem level, 38% at level 20); does not stack with the keystone", source: "Data/Skills/sup_dex.lua:3508-3556; wiki Point Blank rev 1444227", pob: full}
  - {kind: unique, name: "Grelwood Shank", slot: Sword, role: applies, target: enemy, text: "Point Blank (keystone line) with Skills fire 2 additional Projectiles if you've been Hit Recently and Iron Reflexes while stationary", source: "Data/Uniques/sword.lua:148-160; wiki cargo items", pob: config}
  - {kind: unique, name: "Skin of the Lords", slot: Body Armour, role: applies, target: enemy, text: "Random keystone list includes Point Blank (wiki cargo items query)", source: "wiki cargo items query 2026-10-26 (stat text lists the random keystones)", pob: partial}
  - {kind: tattoo, name: "Point Blank tattoo (Hinekora keystone tattoo)", slot: tree, role: applies, target: enemy, text: "keystone tattoo of Point Blank", source: "Data/TattooPassives.lua:1885-1900", pob: partial}
  - {kind: mod, name: "Crucible weapon tree node", slot: weapon, role: applies, target: enemy, text: "WeaponTreeKeystonePointBlank (keystone) and WeaponTreeSupportPointBlank (Socketed Gems are Supported by Level 10 Point Blank)", source: "Data/Crucible.lua:1345, 2177-2178", pob: partial}
  - {kind: mod, name: "Socketed Gems are Supported by Level 20 Point Blank", slot: item mod, role: applies, target: enemy, text: "item mods that socket the support (levels 10, 20, 35; boots/gloves/helmet variants too)", source: "Data/ModCache.lua:20055, 20219, 20384, 20961, 21258, 21558", pob: full}
makes_redundant:
  - {provider: "Point Blank Support (its keystone part)", when: "the keystone is allocated", why: "both set the same PointBlank flag; a second source adds nothing (the wiki: 'a skill either has Point Blank or does not'); the gem keeps its own increased Projectile Damage", source: "wiki Point Blank rev 1444227; Data/Skills/sup_dex.lua:3518-3520"}
conflicts:
  - {with: "spell builds (EK, Worb, FR, Fireball seed)", effect: "no effect at any distance: the more line carries the Attack flag; allocating the keystone there is a wasted point", source: "headless: 0.000% on four seeds; Ice Spear control 0.000%; wiki Point Blank rev 1444227 ('It does not affect spells')"}
  - {with: "long-range play / Far Shot", effect: "beyond 35 units the multiplier is below 1; at 120+ it is x0.70; Far Shot (separate keystone) is the opposite ramp and multiplies with it", source: "wiki Point Blank rev 1444227; Modules/CalcOffence.lua:1083-1087"}
conditions:
  - {text: "damage scales with the TOTAL distance the projectile has travelled (a returning or chaining projectile keeps counting), not with the distance to the caster; projectile speed does not matter", source: "wiki Point Blank rev 1444227"}
  - {text: "attack projectiles only; includes projectile portions of melee attacks (Lightning Strike, Molten Strike); not spells; Rain of Arrows style splash is measured from where the arrow was fired to the target", source: "wiki Point Blank rev 1444227"}
  - {text: "values since 3.9.0: 30% more at close range (was 50%), up to 30% less far away (was 50% less)", source: "wiki Version 3.9.0 rev 1464805 (patch 3.9.0, 2019-12-13): 'The Point Blank keystone now causes projectiles to deal 30% more damage to very close enemies (from 50%), dealing up to 30% less damage based on the distance the projectile travels before it hits (from 50% less)'"}
  - {text: "Chin Sol's 'more damage at close range' is a different, multiplicative effect", source: "wiki Point Blank rev 1444227"}
uptime:
  Mapping:       {value: partial, config: {projectileDistance: "set to the real engagement distance; 10 or less = +30%, 35 = 0, unset = 40 = -1.76%"}, reasoning: "the bonus exists only for hits that land within 3.5 m of the firing point; in maps the distance varies per pack and PoB holds one number per skill; no source for a typical map distance. Zero on spell skills", source: "Modules/CalcOffence.lua:1083; Modules/ConfigOptions.lua:1790; headless Toxic Rain control"}
  Pinnacle Boss: {value: pob, config: {projectileDistance: "set by the user to the boss fight distance", enemyIsBoss: "Pinnacle (level 84)"}, reasoning: "use PoB's number only with an explicit projectileDistance; a ranged boss fight at normal bow range is beyond 35 units and Point Blank is neutral or negative there; the +30% needs the boss inside about 1 m of the muzzle. Zero on spell skills", source: "headless Toxic Rain control, Pinnacle rows; wiki Point Blank rev 1444227"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Point_Blank (rev 1444227)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.9.0 (rev 1464805): keystone values 30% / 30%", kind: patch_notes, patch: "3.9.0"}
  - {ref: "wiki cargo passive_skills: stat text 'Projectile Attack Hits deal up to 30% more Damage to targets at the start of their movement, dealing less Damage to targets as the projectile travels farther', is keystone = 1 (global passive stat, not an item-local mod)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:68886-68890; Data/ModCache.lua:18583, 18684; Modules/ModParser.lua:2315; Modules/CalcOffence.lua:1081-1087; Modules/CalcActiveSkill.lua:455-460; Modules/ConfigOptions.lua:1790; Classes/ModStore.lua:598-615; Classes/ModList.lua:122-154; Modules/CalcSetup.lua:570-586; Data/Skills/sup_dex.lua:3508-3556", kind: pob, patch: "3.29"}
not_verified:
  - "the game distance behind '35 units' and '120 units' (the wiki table says units; PoB's config tooltip says 10 units = 1 metre; no second source)"
  - "typical hit distance of a ranged attack in maps and on pinnacle bosses: no source found, so the generator has no default for projectileDistance"
  - "whether PoB's single distance per skill is right for piercing, chaining, forking or returning projectiles (the wiki says total travelled distance counts); PoB has no such path model"
  - "the unique items behind the item-exclusive mod ids KeystonePointBlankUnique__1/__2 and VillagePointBlank (Data/ModItemExclusive.lua:5181, 6146, 8153) were not traced; Grelwood Shank is the one found in Data/Uniques"
  - "tattoo, Crucible and Skin of the Lords providers were not run headless"
  - "the two control builds (Toxic Rain, Ice Spear) are not validator seeds: their numbers show how PoB treats an attack and a projectile spell, not what the seeds would gain"
open_questions:
  - "What projectile distance should the generator assume for a projectile-attack build on maps and on a pinnacle boss, since PoB's placeholder (40 units) turns Point Blank into a small loss?"
```
