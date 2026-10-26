---
type: interaction
status: draft
pob_refs: [TotalDPS, FullDPS, HitSpeed, Speed, ProjectileCount, PierceCount, ChainCountMax, ForkCountMax]
source: "PoB 2.67.2 Data/Uniques/wand.lua:209-218, Data/ModCache.lua:3783/20428/18714, CalcSetup.lua:1605-1608, Calcs.lua:254-255; poewiki Mystic Refractor rev 1675478; vault Winter Orb projectile overlap; headless Worb probes (task 027 batch 2c, item-analyst-worb.md)"
last_confirmed_patch: "3.29.x"
---

Mystic Refractor is a package: +3 projectiles (the point of the item) plus a Pagan Wand body with 3 sockets (B-B-W), in Worb the carrier of the Frostbite curse. PoB credits the +3 projectiles 0.00% because it counts one hit per volley (ProjectileCount only 6 -> 3); the vault overlap model says 4.43 hits on a lone boss with 6 projectiles against 3 with 3 (x1.48, floor x1.33). The price of the unique comes from the model, not from the PoB delta.
The downside "projectiles cannot continue after colliding" is moot for Winter Orb (the wiki lists Winter Orb as not colliding); it only costs if the build adds pierce, fork, chain or return ([[Returning projectiles]]). Whole-item removal in PoB is -6.18% (Pinnacle and Mapping alike) but PoB keeps the emptied slot's gems; the in-game loss includes the socket group (Frostbite -37 cold resistance on the enemy): -37.88% Pinnacle / -25.06% Mapping for the group alone.
Pipeline: [[Damage calculation#Hit rate]] - extra projectiles change how many Winter Orb impacts land per volley on one target; the 44% projectile damage and the cast speed enter the normal pools

```interaction
id: unique-mystic-refractor
mechanic: "Unique package: +3 projectiles for Winter Orb (more impacts per volley on one boss, priced from the vault overlap model, PoB shows 0.00%) on a 3-socket wand that also carries the Frostbite group"
family: projectile
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#Increased and reduced"]
pipeline_why: "projectile count sets the number of impacts per volley (hits per cast on one target); projectile damage and cast speed are ordinary increased and speed mods"
target: self
related: [projectile-hits-single-target, returning-projectiles, curse-application, penetration, chance-on-hit-uptime]
pob:
  measured: partial
  how: "Item parse: every line parses, extra = nil on all five (modLine.modList; implicit Speed INC 10 flags 16 ModCache.lua:3783; ProjectileCount BASE 3 ModCache.lua:20428; Projectile Damage INC 44 live parse; ProjectileSpeed INC 48 live parse; CannotPierce/Chain/Fork/Split FLAG flags 1024 ModCache.lua:18714). PoB counts ProjectileCount 6 -> 3 but one hit per volley, so the +3 projectiles line is 0.00% DPS. Whole-item removal Worb (Pinnacle / Mapping): TotalDPS 1,343,497.51 -> 1,260,404.11 (-6.18%) / 1,934,211.10 -> 1,814,582.90 (-6.18%), FullDPS 6,302,020.54 / 9,072,914.51; Speed 9.57 -> 9.15, HitSpeed 6.45 -> 6.30, ProjectileCount 6 -> 3; no unmet requirement. PoB keeps the socket groups of an emptied slot (CalcSetup.lua:1605-1608), so the removal delta is not a game fact. Winter Orb gem count 5 is hand-set (Calcs.lua:254-255); the model replaces it, it does not stack."
  config: []
  unparsed: []
model:
  proposed_kind: projectile_overlap_hits
  inputs: {from_pob: [ProjectileCount, AreaOfEffectRadiusMetres], from_scenario: []}
  params: {ref: "Models/Winter Orb projectile overlap", spacing_m: 1.4, enemy_radius_m: 0.5, aoe_radius_m: 2.6}
  formula: "6 projectiles at +-0.7/2.1/3.5 m, window 3.1 m: 4 inner always + outer two each 0.214 = 4.43 hits (golden rounded down 4); 3 projectiles at 0/+-1.4 m: 3 hits. Ratio 4.43/3 = x1.48, floor 4/3 = x1.33. Combined with PoB -6.18%: without the wand 0.9382 x 3/4.43 = x0.635 (about -36%), floor form x0.704 (about -30%)."
  calibration: "spacing 1.4 m calibrated in the vault model, not measured in game; derived from the vault model"
providers:
  - {kind: unique, name: "Mystic Refractor", variant: "Current (no Variant lines in the file)", slot: Weapon 1, role: scales, target: self, text: "implicit: 10% increased Cast Speed", source: "Data/Uniques/wand.lua:213; ModCache.lua:3783", pob: full}
  - {kind: unique, name: "Mystic Refractor", slot: Weapon 1, role: scales, target: self, text: "Skills fire 3 additional Projectiles (rolled 3 of (2-3)); PoB 0.00%, model x1.33-x1.48 hits on a lone boss", source: "Data/Uniques/wand.lua:214; ModCache.lua:20428", pob: partial}
  - {kind: unique, name: "Mystic Refractor", slot: Weapon 1, role: scales, target: self, text: "48% increased Projectile Speed ((10-50) since 3.29.0); no effect on Winter Orb (0.00%)", source: "Data/Uniques/wand.lua:216; live parse", pob: full}
  - {kind: unique, name: "Mystic Refractor", slot: Weapon 1, role: scales, target: self, text: "44% increased Projectile Damage ((30-50)); -3.95% TotalDPS in Worb", source: "Data/Uniques/wand.lua:217; live parse", pob: full}
  - {kind: unique, name: "Mystic Refractor", slot: Weapon 1, role: blocks, target: self, text: "Projectiles cannot continue after colliding with targets (no pierce, fork, chain, split, return); moot for Winter Orb (PierceCount / ChainCountMax / ForkCountMax = 0, delta 0.00%), wiki: no effect on projectiles that do not collide, such as Winter Orb", source: "Data/Uniques/wand.lua:218; ModCache.lua:18714; poewiki Mystic Refractor rev 1675478", pob: full}
package:
  seed: Worb
  slot: Weapon 1
  base: "Pagan Wand, 3 sockets B-B-W"
  xml_item_id: 1
  variant: "none in the file (Current snapshot; the seed rolled 48% projectile speed = the 3.29.0 range, legacy variant Pre 3.29.0 (10-20)% exists at wand.lua:209)"
  removal: "TotalDPS -6.18% in Pinnacle and Mapping (per line: cast speed -2.33%, projectile damage -3.95%, +3 projectiles 0.00%, projectile speed 0.00%, cannot-continue 0.00%; 0.9767 x 0.9605 = 0.9382) - in-memory removal; PoB keeps the emptied slot's gems active (CalcSetup.lua:1605-1608), so the in-game loss is larger: disabling the socket group (Arcane Surge L1 + Frostbite L20 + Frostblink L20) alone is -37.88% Pinnacle / -25.06% Mapping (Frostbite = enemy cold resistance -37), wand removed AND group lost = -41.73% / -29.69%"
  lost_with_item:
    - "Weapon 1 socket group: Arcane Surge L1, Frostbite L20, Frostblink L20 (any 3-socket replacement wand keeps Frostbite)"
    - "conditions UsingWand, UsingOneHandedWeapon, UniqueItemInWeapon off, Unarmed on; multipliers WandItem 1 -> 0, SocketedGemsInWeapon 3 -> 0, UniqueItem 3 -> 2"
    - "the vault-model hit count (x1.48 / floor x1.33) PoB does not credit"
  downsides_that_are_the_point:
    - "Projectiles cannot continue after colliding: costs nothing for Winter Orb (no collision), only if the build adds pierce, fork, chain or return"
  foulborn: "none: PoB Data/ModFoulbornMap.jsonc and .lua name grep = no hit; wiki Foulborn unique item rev 1702126: not listed"
  obtainability: "poewiki Mystic Refractor rev 1675478 / cargo items: release 3.26.0, drop_enabled 1, is_drop_restricted 0, tags include not_for_sale; random drop, no boss or league restriction; version history 3.29.0 projectile speed (10-20)% -> (10-50)%, a Divine Orb can update existing items. Patch 3.29"
makes_redundant:
  - {provider: "Other projectile-count sources (Ascendant / Deadeye extra projectile, Greater Volley)", when: "stacked on the Refractor", why: "they feed the same overlap model; 6 projectiles already give the 2.6 m window an almost full overlap", source: "vault Projectile hits single target providers; Models/Winter Orb projectile overlap"}
  - {provider: "Returning projectiles (support)", when: "Winter Orb", why: "Winter Orb cannot return (wiki), so the Refractor's cannot-return costs nothing", source: "poewiki Mystic Refractor rev 1675478"}
conflicts:
  - {with: "Pierce, fork, chain, split or return sources", effect: "disabled by 'cannot continue after colliding' (only matters for skills that collide)", source: "Data/Uniques/wand.lua:218; ModCache.lua:18714"}
conditions:
  - {text: "Passive item, no config gate; the Winter Orb gem count 5 is hand-set (Calcs.lua:254-255) and the overlap model replaces it", source: "Calcs.lua:254-255"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "passive item, always on; PoB delta identical (-6.18%)", source: "Data/Uniques/wand.lua:213-218"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "passive item, always on; impacts on a lone boss from the vault overlap model (4.43 hits with 6 projectiles, 3 with 3)", source: "Models/Winter Orb projectile overlap"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Mystic_Refractor (rev 1675478)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/wand.lua, Data/ModCache.lua, Modules/CalcSetup.lua, Modules/Calcs.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-worb.md (headless Worb probes, SC/out/w1.json, w2.json)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: in-game impact count with 3 vs 6 projectiles (the model spacing is calibrated, not measured)"
  - "NOT VERIFIED: drop level (not given on the wiki)"
open_questions:
  - "Should the generator price the Refractor from the overlap model (about -30% to -36% without it) instead of the PoB delta (-6.18%)?"
```
