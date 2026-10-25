---
type: interaction
status: draft
pob_refs: [ProjectileCount, Repeats, RepeatCount, dpsMultiplier, TotalDPS, AverageHit, ManaCost, Speed, repeatMode, enemyRadius]
source: "poewiki Greater Multiple Projectiles Support rev 1681576, Multiple Projectiles Support rev 1681577, Spell Echo Support rev 1681738, Greater Spell Echo Support rev 1682292, Fireball rev 1698987 (fetched 2026-10-26); PoB 2.67.2 Data/Skills sup_dex/sup_int/act_int.lua, CalcOffence.lua, ConfigOptions.lua; skill-gem-analyst measured runs (Fireball L20/20 added in memory to Worb.xml and Assa CoC Bladefall.xml, nothing saved)"
last_confirmed_patch: "3.29.x"
---

Greater Multiple Projectiles (GMP, +4 projectiles, 26% less Projectile Damage at L20), Multiple Projectiles (LMP, +2, 6% less) and Spell Echo (repeat once, 54% more cast speed at L20) are the supports that change how many hits a projectile spell lands per second. PoB counts the damage penalty and the cast speed; it does NOT count the extra projectiles as extra hits on one target (it multiplies DPS by ProjectileCount only for SequentialProjectiles skills, Fireball is not one), so GMP looks like a pure -26% loss in PoB while the real boss damage depends on how many projectiles land. Spell Echo's gain is entirely the cast speed (a repeat is part of the original cast and costs nothing). Ratios below come from added Fireball groups on builds that are not Fireball builds: use the ratios, not the absolute numbers.

Pipeline: [[Damage calculation#More and less]] - the GMP/LMP less is a Damage MORE flagged Projectile (hits only, not ailments); [[Damage calculation#Hit rate]] - Spell Echo is a Speed MORE (cast); the projectile count itself is a hit-count multiplier outside the per-hit chain (see [[Projectile hits single target]])

Impact (a) EK: none for this id. The sample has no GMP, LMP or Spell Echo; its Ethereal Knives is triggered by Cast on Critical Strike, and Spell Echo excludes Triggered skills (sup_int.lua:6259). Not applicable. Impact (b) Fireball Elementalist: the 252k last-run TotalDPS is a PoB number where GMP only costs -26% (PoB shows ProjectileCount 5 but dpsMultiplier 1). Under the user-verified 0.6 norm for a lone boss the model gives hits = floor(0.6 x projectiles) per cast, so PoB understates GMP by about x3 and makes it look like a loss. GMP is then a gain only when enough projectiles land: P=2 gives 1 hit (loss), P=3 gives 1, P=4 gives 2 hits x0.747 = 1.49 gain, P=5 gives 3 hits. Spell Echo is the PoB-visible +55% (cast speed) and does not depend on the model; it costs +40% mana and one link. The seed pin of GMP at -26% / 5 projectiles is consistent with sup_dex.lua:2194.

```interaction
id: spell-projectile-supports
mechanic: "Greater Multiple Projectiles: +4 projectiles, 26% less Projectile Damage (L20); Multiple Projectiles: +2 projectiles, 6% less (L20); Spell Echo: repeat once, 54% more Cast Speed (L20), repeats cost nothing; the Greater version takes priority over the non-Greater one (3.28.0)"
family: projectile
pipeline_step: ["Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "GMP/LMP less is Damage MORE flagged Projectile (sup_dex.lua:2160-2163), Spell Echo is Speed MORE flagged Cast (sup_int.lua:6262-6269 = hit rate); the projectile count acts outside the per-hit chain as a hit-count multiplier that PoB does not apply to a non-sequential skill (CalcOffence.lua:803-806)"
target: self
related: [projectile-hits-single-target, returning-projectiles, coc-trigger]
pob:
  measured: partial
  how: "damage penalty and cast speed counted: GMP statMap Damage MORE Projectile (Data/Skills/sup_dex.lua:2160-2163), number_of_additional_projectiles 4 at 2169, L1 -35 at 2175, L20 -26 at 2194, L21 -25, L40 -18 at 2214, manaMultiplier 50; LMP sup_dex.lua:3194 (L1 -15, L20 -6 at 3239, +2 projectiles, manaMultiplier 30). ProjectileCount comes from SkillStatMap number_of_additional_projectiles (Data/SkillStatMap.lua:1408-1409), shown at CalcOffence.lua:1089-1096, but DPS is multiplied by it ONLY for SequentialProjectiles skills (CalcOffence.lua:803-806, dpsMultiplier = Sum ProjectileCount); Fireball is not sequential, dpsMultiplier = 1, so the extra explosions on one target are NOT counted. Spell Echo: RepeatCount from base_spell_repeat_count (SkillStatMap.lua:293-295), Repeats = 1 + RepeatCount (CalcOffence.lua:808-817), no DPS multiplier for non-trap/mine spells (CalcOffence.lua:900-902 is trap/mine only), so the cast speed is the whole gain; PoB applies the Greater-takes-priority rule (measured: GMP+LMP = GMP alone). Quality of both projectile supports: projectile_damage_+% 0.5 per 1% (20% quality = +10% increased projectile damage, sup_dex.lua qualityStats)"
  config:
    - {var: repeatMode, default: AVERAGE, ref: "Modules/ConfigOptions.lua:951-962 (defaultIndex 2, shown only with ifCond alwaysFinalRepeat; changes crit/damage per repeat for Greater Spell Echo and crit, not the repeat count)", class: b}
    - {var: enemyRadius, default: Medium, ref: "Modules/ConfigOptions.lua:777-800 (preset)", class: b}
    - {var: gem count, default: 1, ref: "Calcs.lua:254-255 (hand-set gem count)", class: c}
  unparsed: []
model:
  proposed_kind: projectile_hit_fraction
  inputs: {from_pob: [ProjectileCount], from_scenario: []}
  params: {hit_fraction_numerator: 6, hit_fraction_denominator: 10}
  formula: "hits per cast on a lone boss = projectiles * 6 // 10 (integer math, round down; 5 projectiles -> 3 hits, 3 -> 1, 4 -> 2, 2 -> 1, base 1 -> 1); DPS gain vs no support = hits x PoB ratio (GMP alone: 3 x 0.747 = x2.24, unrounded the same because 5 x 0.6 = 3.0 exactly)"
  calibration: "0.6 is the user-verified norm in vault Models/Projectiles hitting a single target (hit_fraction 0.6, 'FR, Fireball and other skills with an AoE explosion'); its measured case is Forbidden Rite + Greater Volley, not Fireball with 5 projectiles (see open_questions)"
providers:
  - {kind: support, name: "Greater Multiple Projectiles Support", slot: any, role: scales, target: self, text: "+4 projectiles, 26% less Projectile Damage (L20), mana cost x1.5; wider minimum spread than LMP (angle not documented as a number)", source: "Data/Skills/sup_dex.lua:2148-2214; wiki Greater Multiple Projectiles Support rev 1681576", pob: partial}
  - {kind: support, name: "Multiple Projectiles Support", slot: any, role: scales, target: self, text: "+2 projectiles, 6% less Projectile Damage (L20), mana cost x1.3", source: "Data/Skills/sup_dex.lua:3194,3239; wiki Multiple Projectiles Support rev 1681577", pob: partial}
  - {kind: support, name: "Spell Echo Support", slot: any, role: scales, target: self, text: "repeat once, 54% more Cast Speed (L20), mana cost x1.4; cannot support Triggered, Totem, Trap, Mine, Vaal or instant skills", source: "Data/Skills/sup_int.lua:6252-6259 (excludeSkillTypes incl. Triggered at 6259), L20 row 6299; wiki Spell Echo Support rev 1681738", pob: full}
  - {kind: support, name: "Greater Spell Echo Support", slot: any, role: scales, target: self, text: "2 repeats, 10-27% more Spell Damage and 20-37% increased AoE per repeat, 56-81% more Cast Speed, mana cost x1.6; max gem level 15, level req 72", source: "Data/Skills/sup_int.lua:6322-6370 (L1 {10,20,56}, L15 {27,37,81}); wiki Greater Spell Echo Support rev 1682292 (exceptional support, added as a gem in 3.28.0)", pob: full}
  - {kind: unique, name: "Mystic Refractor", slot: Weapon 1, role: scales, target: self, text: "Skills fire (2-3) additional Projectiles; cannot continue after colliding", source: "Data/Uniques/wand.lua:214,218 (via vault Projectile hits single target)", pob: partial}
  - {kind: ascendancy, name: "Deadeye (node 34567)", slot: tree, role: scales, target: self, text: "Skills fire an additional Projectile (not Elementalist)", source: "TreeData/3_29/tree.lua:20154 (via vault Projectile hits single target)", pob: partial}
  - {kind: notable, name: "Split Shot (node 7069)", slot: tree, role: scales, target: self, text: "additional projectile node", source: "TreeData/3_29/tree.lua:82616 (via vault Projectile hits single target)", pob: partial}
  - {kind: keystone, name: "Kineticism (node 40561)", slot: tree, role: blocks, target: self, text: "no pierce, fork or chain (the evidence marks it not relevant to GMP)", source: "TreeData/3_29/tree.lua:85655 (via vault Projectile hits single target)", pob: partial}
makes_redundant:
  - {provider: "Multiple Projectiles Support", when: "Greater Multiple Projectiles Support is linked to the same skill", why: "only the Greater applies (3.28.0); never socket both; measured in PoB: GMP+LMP = GMP alone, 51,040 on the Worb Fireball", source: "wiki Greater Multiple Projectiles Support rev 1681576 version row 3.28.0; skill-gem-analyst PoB run"}
conflicts:
  - {with: "Spell Echo Support vs triggered Fireball", effect: "Spell Echo (and Greater) exclude Triggered skills, so a Cast on Critical Strike or Cast while Channelling triggered Fireball cannot take Echo; GMP can (Fireball is Triggerable). Totem, Trap, Mine, Vaal and instant skills are excluded too", source: "Data/Skills/sup_int.lua:6259; Data/Skills/act_int.lua:5795"}
  - {with: "GMP / LMP less multiplier vs ailments", effect: "the less Projectile Damage hits only hit damage, not ailments (wiki: it 'doesn't decrease the damage of ailments'); PoB agrees, ignite cfg flags are Dot|Ailment only and the support's mod needs ModFlag.Projectile. Extra projectiles do not add ignites: one ignite on the boss, so the hit-count gain is hit damage only", source: "wiki Greater Multiple Projectiles Support rev 1681576; Modules/CalcOffence.lua:4992-4998"}
conditions:
  - {text: "Fireball must be hit-damage based (Explosion part); Fireball (3.29): 5% base crit, 480% damage effectiveness at L20, base radius 1.8 m at L20, 25% ignite chance, 20 mana at L20, skillTypes include Projectile, Multicastable, Triggerable", source: "Data/Skills/act_int.lua:5788-5849 (skillTypes 5795, ignite constantStat 5816, L20 row 5849); wiki Fireball rev 1698987 version row 3.29.0"}
  - {text: "shotgun rule: each enemy can only be hit directly by one projectile per cast; if an enemy is in range of the explosion of more than one projectile of the same cast and those projectiles each exploded on different enemies or a wall, it takes full damage from each explosion", source: "wiki Fireball rev 1698987"}
  - {text: "a repeat is part of the original cast, needs no cost or cooldown, normally has the same crit roll; the time for the original cast and the repeat is two times the tooltip value (so only the cast speed bonus is a net gain)", source: "wiki Spell Echo Support rev 1681738"}
  - {text: "3.26.0: Spell Echo no longer causes supported skills to deal 10% less damage; 3.28.0: Greater versions do not work alongside their non-Greater version, the Greater takes priority", source: "wiki Spell Echo Support rev 1681738; wiki Greater Multiple Projectiles Support rev 1681576"}
uptime:
  Mapping:
    value: always
    config: {repeatMode: AVERAGE}
    reasoning: "Spell Echo cast speed is always on while the skill is cast; for GMP the projectiles spread over a pack, each enemy gets its own direct hit plus overlapping explosions (geometry, not modelled, see vault Fireball explosion overlap)"
    source: "Data/Skills/sup_int.lua:6262-6269; vault Models/Fireball explosion overlap.md (via skill-gem-analyst)"
  Pinnacle Boss:
    value: model
    config: {enemyRadius: "scenario preset; no PoB config for projectiles that hit the boss (only ShrapnelBallistaProjectileOverlap, ConfigOptions.lua:627, one skill)"}
    reasoning: "model: hits = projectiles * 6 // 10 per cast: GMP alone 5 -> 3 hits; LMP alone 3 -> 1 hit (no gain, still 6% less); base 1 projectile -> 1 hit; Spell Echo needs no model (counted by PoB)"
    source: "vault Models/Projectiles hitting a single target.md (hit_fraction 0.6, user-verified); skill-gem-analyst arithmetic"
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Greater_Multiple_Projectiles_Support (rev 1681576)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Multiple_Projectiles_Support (rev 1681577)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Spell_Echo_Support (rev 1681738)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Greater_Spell_Echo_Support (rev 1682292)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Fireball (rev 1698987)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Skills/sup_dex.lua:2148-2214,3194-3239; sup_int.lua:6252-6370; act_int.lua:5788-5849; Modules/CalcOffence.lua:803-817,900-902,1089-1096,4992-4998; Modules/ConfigOptions.lua:777-800,951-962; Data/SkillStatMap.lua:293-295,1408-1409 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Spell Echo Support version rows 3.26.0 and 3.28.0; Greater Multiple Projectiles Support version row 3.28.0", kind: patch_notes, patch: "3.29"}
not_verified:
  - "GMP spread angle in degrees: not in PoB data (grep of Data/Skills/sup_dex.lua and Modules for spread shows only the Volley x_dist 80 line already in the vault model)"
  - "Greater Spell Echo obtainability at league start (exceptional support gem, level req 72, max level 15)"
  - "Fireball radius: vault Fireball model says base radius 9 and predates 3.29; wiki rev 1698987 says 1.8 m at L20 and PoB L20 row 18 = 1.8 m"
  - "measured PoB ratios (Worb base + Fireball L20/20, Explosion part): Fireball alone TotalDPS 68,349 (ProjectileCount 4 = 1 + Mystic Refractor 3, ManaCost 20); +GMP 51,040 (x0.747, count 8, cost 30); +LMP 64,837 (x0.949, count 6, cost 26); +Spell Echo 106,192 (x1.554, Speed 2.98 -> 4.59, Repeats 2, cost 28); GMP+Echo 79,297; Greater Spell Echo (L15) 158,491 (x2.32, Repeats 3, cost 32); AverageHit GMP 17,120 vs 22,926; part 1 (Projectile) has the same GMP loss. Own runs of the analyst, scripts not saved in the vault"
  - "combined numbers GMP + Echo: x3.48 = hand model x3 hits x 0.747 x 1.554 (PoB alone shows 1.16 of base); mana cost 41 vs 20 (2.05x). The x3 hit count is the hand model, not a PoB output"
open_questions:
  - "Hit fraction for GMP Fireball: the vault Fireball model (Fireball explosion overlap) says 1 overlap on a boss, while the verified FR norm (Projectiles hitting a single target) is about 0.6 of projectiles hit. Which applies to GMP Fireball? The 0.6 case was measured with Forbidden Rite + Greater Volley, not Fireball with 5 projectiles; the two readings are not resolved here."
  - "Should the generator apply the hit-count model (hits = projectiles * 6 // 10) on top of PoB's number for GMP, given PoB understates it by about x3?"
```
