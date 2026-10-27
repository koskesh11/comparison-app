---
type: interaction_seeds
status: draft
pob_refs: []
source: "lead draft SEEDS-draft.md (task 027); seed pins (wt-021 vault/Inbox/Seed unique pins.md, Seeds/EK CoC Ethereal Knives.md); tasks/reports/021-gate1.md rows; task 027 evidence files"
last_confirmed_patch: "3.29.x"
---

Each seed build as a set of mechanics: which mechanic is the core of the build, which only scales or sustains it, and which it breaks without (enabler). Mechanic ids match the notes in this folder (`id:` in each note's interaction block). `uncovered` = mechanics the seed uses that have no note yet. The blocks are `seed_mechanics`, not loaded by the engine. This note has no `interaction` block on purpose.

Roles: core = the build is built around it; support = scales or sustains the core; enabler = the core breaks without it.

Seed 1 - EK CoC Ethereal Knives (Shadow / Assassin). Sample: 3.29/Ninja Builds/CoC EK Assa.xml.

```seed_mechanics
name: EK
sample: "3.29/Ninja Builds/CoC EK Assa.xml"
mechanics:
  - {id: coc-trigger, role: core, providers: ["Cyclone L1 + Cast On Critical Strike -> Ethereal Knives (cap 10.10/s)", "Like Clockwork via Forbidden Flame + Forbidden Flesh"]}
  - {id: spell-impale, role: core, providers: ["Entropic Devastation: Critical Strikes with Spells inflict Impale (ImpaleDPS 49% of total)", "Watcher's Eye Pride (+2 hits)"]}
  - {id: frenzy-charges, role: support, providers: ["Ralakesh's Impatience (counts as max)", "Badge of the Brotherhood (max Frenzy = max Power)"]}
  - {id: power-charges, role: support, providers: ["Assassin / Badge of the Brotherhood", "config usePowerCharges"]}
  - {id: projectile-hits-single-target, role: support, providers: ["Ethereal Knives projectiles (no model yet -> open)"]}
  - {id: flask-uptime, role: support, providers: ["2 Surgeon's flasks (35%, 32% charge on crit)"]}
uncovered:
  - "elusive (Assassin Mistwalker, Badge)"
  - "abyss-jewel-effect (Darkness Enthroned)"
  - "cast-when-damage-taken curse (Vulnerability)"
  - "CI without Whispers: skill-cost-from-es is NOT used here (EK pays mana; Clarity WE -10 cost)"
```

Seed 2 - Worb (Witch / Elementalist). Sample: 3.29/Worb.xml; day-1 snapshot tasks/reports/021-fixtures/worb-day1-poeninja.xml.

```seed_mechanics
seed: Worb
name: "Worb"
sample: "3.29/Worb.xml"
mechanics:
  - {id: channelling, role: core, providers: ["Winter Orb + Focused Channelling (multiplierChannelling 0 in both samples -> PoB +0%; boss 3 s = +60%, maps 0.5 s = +0% in PoB, user 2026-10-25)"]}
  - {id: projectile-hits-single-target, role: core, providers: ["Mystic Refractor (Skills fire (2-3) additional Projectiles; sample roll 3)", "vault Models/Winter Orb projectile overlap (count 5 hand-set; golden 4 hits)"]}
  - {id: freeze, role: core, providers: ["Winter Orb 3.29 base 25% + crits", "Cold Mastery 26782 (frozen seconds)", "modeler: Worb.xml crits freeze 0.533 s on a Pinnacle boss"]}
  - {id: chill, role: support, providers: ["cold hits"]}
  - {id: exposure, role: support, providers: ["Frost Bomb", "Cold Mastery 13267", "Heraldry"]}
  - {id: elemental-ailment-count, role: support, providers: ["The Taming (sample ticks chilled + frozen + shocked; shock source of Worb NOT identified)"]}
  - {id: enemy-ailment-threshold, role: support, providers: ["PoB boss ailment threshold (CalcOffence.lua:5333-5342)"]}
  - {id: arcane-surge, role: support, providers: ["Arcane Adept / mana-spend trigger"]}
  - {id: golem-buffs, role: support, providers: ["4 golems (limit rule)"]}
  - {id: power-charges, role: support, providers: ["PCoC", "Caster mastery 33089 (Power Charge each second while channelling)"]}
  - {id: rampage, role: support, providers: ["Bisco's Leash (day-1 variant)"]}
  - {id: shatter, role: support, providers: ["Herald of Ice (day-1 variant)"]}
uncovered:
  - "radius jewel (Light of Meaning)"
  - "mana sustain"
  - "Ice Bite / Frostbite (day-1 variant; Ice Bite is not in the Winter Orb link group)"
```

Seed 3 - FR CoC + Foulborn Three Dragons (Witch / Occultist). Sample: Builds/AutoBuilder/FR CoC Occu Three Dragons v4.xml.

```seed_mechanics
name: FR
sample: "Builds/AutoBuilder/FR CoC Occu Three Dragons v4.xml"
mechanics:
  - {id: coc-trigger, role: core, providers: ["Cyclone L20 + Cast On Critical Strike -> Forbidden Rite of Soul Sacrifice (rate 7.524 vs cap 7.5758)"]}
  - {id: damage-type-can-ailment, role: core, providers: ["Foulborn The Three Dragons (mutation set: Chaos can Freeze, Chaos can Shock)"]}
  - {id: shock, role: core, providers: ["chaos hits via that mutation (PoB adds no DPS until conditionEnemyShocked + effect are set)"]}
  - {id: freeze, role: core, providers: ["chaos hits via that mutation"]}
  - {id: projectile-hits-single-target, role: core, providers: ["Forbidden Rite part 2 (user-verified 0.6 hit fraction, vault Models/Projectiles hitting a single target)"]}
  - {id: flask-uptime, role: support, providers: ["Mageblood"]}
  - {id: consecrated-ground, role: support, providers: ["Bottled Faith (enemy-side config conditionEnemyOnConsecratedGround)"]}
  - {id: curse-limit, role: support, providers: ["Anathema (limit = max power charges)"]}
  - {id: power-charges, role: support, providers: ["Anathema", "Grand Spectrum (min charges)"]}
  - {id: frenzy-charges, role: support, providers: ["Grand Spectrum (min charges)"]}
  - {id: skill-cost-from-es, role: support, providers: ["Whispers of Infinity + CI"]}
  - {id: max-res-equalise, role: support, providers: ["Melding of the Flesh"]}
  - {id: enemy-ailment-threshold, role: support, providers: ["PoB boss ailment threshold (CalcOffence.lua:5333-5342)"]}
uncovered:
  - "runegrafts / tattoos (021 N1/N2)"
  - "Vile Bastion / Void Beacon (Occultist)"
  - "brand-attached config (dead var, 021 N12)"
```

Seed 4 - Fireball Elementalist (Witch / Elementalist). Sample: none (goals only; draft seed vault/Seeds/Fireball Elementalist.md on branch task-035-fireball-starter; measured on the scrapped build Builds/AutoBuilder/Scrapped/Fireball Elementalist - league_start (NOT VIABLE).xml, Fireball L20 effective quality 30, Pinnacle boss). User goal: 500k hit DPS (TotalDPS), 4-6 projectiles, life + ES hybrid, phys max hit 7,000.

```seed_mechanics
seed: Fireball
name: "Fireball Elementalist"
sample: null
mechanics:
  - {id: spell-projectile-supports, role: core, providers: ["Greater Multiple Projectiles (pinned: 5 projectiles for the 4-6 goal, 26% less Projectile Damage at L20)", "Fire Penetration / Added Fire Damage / Inspiration / Controlled Destruction candidates in the Fireball group"]}
  - {id: projectile-hits-single-target, role: core, providers: ["Fireball + GMP on a lone Pinnacle boss = 1 hit per cast, x1.0 on PoB TotalDPS (tasks/reports/027-batch1b.md; vault Models/Fireball explosion overlap)"]}
  - {id: ignite, role: support, providers: ["Fireball gem 25% on hit, 100% on crit = 40.86% per hit: IgniteDPS 33,468.58 of FullDPS 285,468.27 at Fireball L20 (b1c-pob-fireball.md); FullDPS keeps only the best ignite"]}
  - {id: penetration, role: support, providers: ["Fire Penetration support (candidate, not pinned)"]}
  - {id: shock, role: support, providers: ["Shaper of Storms 27038: hits always shock (config conditionEnemyShocked ticked; PoB never sets Shocked from hits)"]}
  - {id: golem-buffs, role: support, providers: ["Golem Commander 34506 + Liege of the Primordial 56461: 4 golems (Flame, Lightning, Stone, Chaos); Lightning Golem Wrath config summonLightningGolemEnableWrath"]}
  - {id: herald-ash-zealotry-anger, role: support, providers: ["Aura group candidates Herald of Ash / Zealotry / Anger (pin false, reservation vs ManaUnreserved >= 0); Herald of Ash overkill burn: lone boss = 0, pack scenario only (hoaOverkill)"]}
  - {id: elemental-overload, role: support, providers: ["keystone candidate (not pinned by the seed): PoB assumes 100% uptime, the note's model gives 70% at 5% crit and 1 hit per cast"]}
  - {id: mind-over-matter, role: enabler, providers: ["main route to the max-hit goals (seed: Mind over Matter is not forbidden); needs unreserved mana"]}
  - {id: energy-shield-hybrid, role: enabler, providers: ["user hybrid: Life > 3,000 and ES > 1,100; Chaos Inoculation and Eldritch Battery forbidden"]}
  - {id: armour-phys-max-hit, role: support, providers: ["armour toward PhysicalMaximumHitTaken >= 7,000 at a 4,100 pool (note: about 24.8k armour alone)"]}
  - {id: flat-physical-damage-reduction, role: support, providers: ["flat physical damage reduction toward the 7,000 goal"]}
  - {id: physical-taken-as-elemental, role: support, providers: ["phys taken as elemental toward the 7,000 goal"]}
  - {id: guard-skills, role: support, providers: ["guard skill absorb for the max hit (one guard only; PoB keeps the first guard in pairs() order)"]}
  - {id: determination-grace, role: support, providers: ["Determination (armour) / Grace; competes for reservation with the aura group"]}
  - {id: max-resistances, role: support, providers: ["75% elemental resistance goal; max resistance lifts the elemental max hits (16,000 goal)"]}
  - {id: elementalist-aegis-bastion, role: support, providers: ["Bastion of Elements 4917: declined by the user 2026-10-25 (kept Shaper of Storms)"]}
  - {id: block, role: support, providers: ["Titanium Spirit Shield in the seed rares"]}
  - {id: spell-suppression, role: support, providers: ["no ascendancy node; gear and tree only"]}
  - {id: endurance-charges, role: support, providers: ["when-hit uptime assumption (note)"]}
  - {id: recovery, role: support, providers: ["life regeneration and ES recharge for sustained damage, not for the single-hit max hit goal"]}
uncovered:
  - "Fireball part 2 'Explosion' (skill_part 2): which part represents the directly hit boss (seed VERIFY); not in TotalDPS at part 1"
  - "Fireball 1 + E model for walls, adds and Mapping (GMP spread angle not verified, batch 1b)"
  - "Heart of Destruction Convergence (conditionConvergence): PoB makes it a permanent 30% more, real uptime <= 50% and only vs unique enemies; left unticked"
  - "Mastermind of Discord 61259: path node only, no exposure source on Fireball"
  - "Chaos resistance 0% goal (Amethyst Ring implicits, Chaos Golem)"
```

User examples (not in a seed): returning-projectiles (Nimis, Returning Projectiles support), rampage (Bisco's Leash), flask-uptime.

```seed_mechanics
name: "User examples (no seed)"
sample: null
mechanics:
  - {id: returning-projectiles, role: core, providers: ["Nimis", "Returning Projectiles (support)"]}
  - {id: rampage, role: core, providers: ["Bisco's Leash"]}
  - {id: flask-uptime, role: core, providers: ["Mageblood"]}
uncovered: []
```
