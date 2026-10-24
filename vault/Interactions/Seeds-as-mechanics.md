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
  - {id: channelling, role: core, providers: ["Winter Orb + Focused Channelling (multiplierChannelling 0 in both samples -> PoB +0%; model: 3 s = +60%)"]}
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
