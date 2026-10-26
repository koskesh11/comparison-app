---
type: interaction-readme
status: draft
source: "task 027 format, designed by interactions-lead; the parse rule mirrors engine/vault.py"
last_confirmed_patch: "3.29.x"
---

# Interactions: one note per mechanic

This folder holds the mechanics that PoB computes only partly, only through a config tick, or not at all, with every provider (gem, support, unique, Foulborn mutation, tree node, ascendancy, tattoo, flask, jewel), what it needs, what it blocks, and how often it is up in each scenario. Only what PoB lacks is written here; PoB data is referred to by id, never copied. Seeds are described as sets of mechanics in [[Seeds-as-mechanics]]. Scenario keys are the note names in vault/Scenarios (`Mapping`, `Pinnacle Boss`).

Evidence behind every note (specialist files, cited as e.g. build-strategist.md): tasks/reports/027-evidence/ in the repo; validator: tasks/reports/027-evidence/validate.py <vault/Interactions> (run with plain python, not -I).

## File and frontmatter

File: `vault/Interactions/<Human title>.md` (for example `Freeze.md`, `Returning projectiles.md`), one note per mechanic. Frontmatter uses the same keys as the existing Rules and Models:

- `type: interaction`
- `status: draft` until the user verifies (then `verified_by: user, <date>`)
- `pob_refs: [...]` PoB variables and output keys the note depends on
- `source: "short list of the main sources"`
- `last_confirmed_patch: "3.29.x"`

Then 2 to 6 lines of plain prose (what it is, why it matters for building), then ONE fenced block named `interaction`. The block is parsed like the rule, model and gap blocks: regex `` ```interaction\n(.*?)``` `` with DOTALL, then `yaml.safe_load`. No engine code reads it yet (after task 021). This README has no such block on purpose; its example sits in a `yaml` fence so it is not loaded as a note.

## Block layout

```yaml
id: freeze                         # kebab-case, unique; other notes and seeds reference this id
mechanic: "Cold hits freeze: enemy action speed 100% less (bosses keep a 50% floor) for 0.06 s per 1% of ailment threshold, max 3 s"
family: ailment                    # ailment | trigger | charge | projectile | buff | resource | defence | uptime | pipeline
target: enemy                      # whom the mechanic is on: enemy | self
related: [chill, shatter, enemy-ailment-threshold]
pob:
  measured: partial                # full | partial | config | none
  how: "where PoB computes it and what it leaves out (file:line)"
  config:                          # every config input that gates the effect
    - {var: conditionEnemyFrozen, default: false, ref: "Modules/ConfigOptions.lua:1924", class: b}   # class: a = sourced by gear/gem, b = scenario, c = hand-set
  unparsed: []                     # red lines of providers, "<item>: <line>"
model:                             # only when measured != full AND a number is needed; else null
  proposed_kind: freeze_uptime     # proposed until engine/models.py KINDS has it (then "kind:")
  inputs: {from_pob: [], from_scenario: []}
  params: {}
  formula: "..."
  calibration: "source, or 'no norm found'"
providers:                         # one line per provider (flow style)
  - {kind: gem, name: "Winter Orb", slot: any, role: applies, target: enemy, text: "25% chance to Freeze", source: "Data/Skills/act_int.lua:21035", pob: full}
makes_redundant:
  - {provider: "Returning Projectiles (support)", when: "Nimis equipped", why: "...", source: "..."}
conflicts:
  - {with: "Elemental Focus (support)", effect: "supported skill cannot inflict ailments", source: "..."}
conditions:
  - {text: "hit >= 5% of the enemy ailment threshold (0.3 s minimum)", source: "..."}
uptime:                            # keys = vault/Scenarios note names
  Mapping:       {value: high, config: {conditionEnemyFrozen: true}, reasoning: "...", source: "..."}
  Pinnacle Boss: {value: model, config: {conditionEnemyFrozen: "model: only if duration >= 0.3 s"}, reasoning: "...", source: "..."}
seeds: [Worb]                      # seeds that use it: EK | Worb | FR | Fireball (see Seeds-as-mechanics)
sources:
  - {ref: "https://www.poewiki.net/wiki/Freeze (rev NNN)", kind: wiki, patch: "3.29"}
not_verified: ["..."]
open_questions: ["..."]            # questions only the user can answer
```

## Vocabulary

- `family`: ailment, trigger, charge, projectile, buff, resource, defence, uptime, pipeline (the three order-of-operations notes [[Damage calculation]], [[Receiving damage]], [[Defences]]; they carry `steps:` and `pipeline_step: [self]`).
- `target` (note and provider): `enemy` or `self`. A line such as Berek's Pass "+5000 Armour while Frozen" is target `self`, not a freeze payoff on enemies.
- `pob.measured`: full (PoB computes it), partial, config (only through a config tick or a hand-set value), none.
- `pob.config[].class`: a = sourced by gear or gem, b = scenario, c = hand-set.
- provider `kind`: unique, foulborn, gem, support, keystone, notable, mastery, ascendancy, tattoo, runegraft, mod, flask, jewel. Optional keys: `variant` (the item variant, or for a Foulborn / mastery option the replaced line), `requires: [...]`.
- provider `role`: enables, applies, scales, abuses, sustains, blocks.
- provider `pob`: full (PoB parses and counts it), partial, config (counted only with a config tick), none (unparsed or not modelled).
- `uptime[scenario].value`: always, high, partial, low, none, pob (use PoB's own number), model (the `model:` above decides).
- `sources[].kind`: pob, wiki, patch_notes, forum, github, discovery (poe.ninja or guides are discovery only and never decide).

## Pipeline step

The three pipeline notes ([[Damage calculation]] outgoing, [[Receiving damage]] incoming order, [[Defences]] per-layer formulas and caps) are the foundation for judging whether an interaction works. Every heading in them is one named step in the wiki order and can be linked, e.g. [[Damage calculation#More and less]].

Every other interaction note names where it acts in that order:

- In the block: `pipeline_step: ["Damage calculation#More and less", ...]` (note#heading, plain strings, no brackets) and `pipeline_why: "one line: why it acts there"`. The pipeline notes themselves use `pipeline_step: [self]` and a `steps:` list of `{id, heading, wiki_order, pob_ref, pob_status}`.
- In the prose: a line `Pipeline: [[Damage calculation#More and less]] - why`.

Examples of why it matters: increased vs more (additive pool vs own multiplier), taken-as vs conversion (defender-side shift vs offensive conversion), armour not against DoT, block after all mitigation.

## Writer rules

- Never write bare yes/no/on/off as a value: YAML reads them as booleans. Use the vocabulary words (measured and provider pob: full | partial | config | none; seeds: EK | Worb | FR | Fireball) or quote the string.
- Every provider, condition and uptime line has a source (PoB file:line, wiki revision, patch note, forum or GitHub URL). No source: put the claim in `not_verified`.
- Foulborn: name the replaced original line in `variant`. A mutation REPLACES a line (PoB loads Data/ModFoulbornMap.jsonc; texts in Data/ModFoulborn.lua).
- Conflicting readings (wiki vs PoB vs user) stay visible as params or readings plus an `open_questions` entry; never pick one silently.
- PoB already computes it: write "use PoB's number" (for example the flask tooltip uptime) and do not re-model it.
- The freeze note lists all providers found. Other notes list the seed providers plus at most 12 alternatives; the rest is in tasks/reports/027-research.md.
- Round down ([[Models round down]]); every number traces to PoB or a vault note; paths in `source` are relative to `%APPDATA%\Path of Building Community` unless a URL is given.
- Nothing here is verified until the user says so: new or changed notes stay `status: draft`.

## How to parse

```python
import re, yaml
BLOCK = re.compile(r"```interaction\n(.*?)```", re.DOTALL)
data = yaml.safe_load(BLOCK.search(text).group(1))   # required keys: id, mechanic, family, target, pob, providers, uptime, sources, not_verified
```

Validator (scratchpad of task 027): `python -I validate.py vault/Interactions` checks frontmatter, one parseable block, required keys, provider role and source, uptime values and unique ids.

Unique package notes (task 027 batch 2c): file "Unique - <Name>.md", id `unique-<kebab>`. Besides the usual keys the ```interaction``` block carries a top-level `package:` key {seed, slot, base, xml_item_id, variant, removal, lost_with_item, downsides_that_are_the_point, foulborn, obtainability}: the unique is valued as one package (every line, incl. downsides that are the point), measured by an in-memory removal on its seed. PoB keeps an emptied slot's gems active (CalcSetup.lua:1605-1608), so `removal` excludes the socket group; the note says so where it matters.

## Notes (158 ids)

Written so far: [[Freeze]] (freeze), [[Chill]] (chill, with Bonechill and chill effect), [[Shatter]] (shatter), [[Shock]] (shock), [[Damage type can ailment]] (damage-type-can-ailment), [[Elemental ailment count]] (elemental-ailment-count), [[Exposure]] (exposure), [[Enemy ailment threshold]] (enemy-ailment-threshold, new id from the coverage audit).

Other notes of task 027 (written in parallel; ids): coc-trigger, frenzy-charges, power-charges, spell-impale, curse-limit, skill-cost-from-es, max-res-equalise, golem-buffs, arcane-surge, projectile-hits-single-target, returning-projectiles, rampage, flask-uptime, channelling, consecrated-ground, fight-length ([[Fight length]]).

Batch 1 (task 027): armour-phys-max-hit ("Armour and physical max hit"), spell-suppression ("Spell suppression"), block ("Block"), max-resistances ("Max resistances"), mind-over-matter ("Mind over Matter"), elementalist-aegis-bastion ("Primal Aegis and Bastion of Elements"), energy-shield-hybrid ("Energy shield and hybrid"), recovery ("Recovery"), spell-projectile-supports ("Spell projectile supports"), elemental-overload ("Elemental Overload"), herald-ash-zealotry-anger ("Herald of Ash, Zealotry and Anger"), penetration ("Penetration"). Batches 2-4: see the overnight line below.

Batch 1c (task 027): offensive-utility-flasks ("Offensive utility flasks"), defensive-utility-flasks ("Defensive utility flasks"), life-mana-flasks ("Life and mana flasks"), elemental-ailment-immunity ("Elemental ailment immunity"), bleed-poison-cb-immunity ("Bleed, poison and corrupted blood immunity"), stun ("Stun"). Herald of Ash overkill is a section of herald-ash-zealotry-anger; Fireball is a section of [[Seeds-as-mechanics]].

All 24 ids: freeze, chill, shatter, shock, damage-type-can-ailment, elemental-ailment-count, exposure, enemy-ailment-threshold, coc-trigger, frenzy-charges, power-charges, spell-impale, curse-limit, skill-cost-from-es, max-res-equalise, golem-buffs, arcane-surge, projectile-hits-single-target, returning-projectiles, rampage, flask-uptime, channelling, consecrated-ground, fight-length.

Overnight 2026-10-26 (task 027 batches 1b-4d, merged by the orchestrator): absolution ("Absolution"), abyss-jewel-effect ("Abyss jewels"), accuracy-hit-chance ("Accuracy and hit chance"), acrobatics ("Acrobatics"), animate-guardian ("Animate Guardian"), arcanist-brand ("Arcanist Brand"), ascendancy-assassin ("Assassin ascendancy"), ascendancy-elementalist ("Elementalist ascendancy"), ascendancy-hierophant ("Hierophant ascendancy"), ascendancy-inquisitor ("Inquisitor ascendancy"), ascendancy-occultist ("Occultist ascendancy"), assassins-mark ("Assassin's Mark"), aura-conditional-uniques ("Aura-conditional uniques"), aura-effect ("Aura effect and aura count"), avatar-of-fire ("Avatar of Fire"), bleed ("Bleed"), blind ("Blind"), brands ("Brands"), call-to-arms ("Call to Arms"), cast-on-melee-kill ("Cast on Melee Kill"), cast-when-damage-taken ("Cast when damage taken"), cast-while-channelling ("Cast while Channelling"), chance-on-hit-uptime ("Chance on hit uptime"), chaos-inoculation ("Chaos Inoculation"), clear-mechanics ("Clear - chain, pierce, fork and area"), cluster-jewels ("Cluster jewels"), conversion-gain-as-extra ("Conversion and gain as extra"), cooldown-recovery-breakpoint ("Cooldown recovery breakpoints"), crimson-dance ("Crimson Dance"), critical-strike-chance ("Critical strike chance"), critical-strike-multiplier ("Critical strike multiplier"), culling-strike ("Culling strike"), curse-application ("Curse application and effect"), damage-calculation ("Damage calculation"), damage-over-time-multiplier ("Damage over time multiplier"), defences ("Defences"), determination-grace ("Determination and Grace"), eldritch-battery ("Eldritch Battery"), elemental-equilibrium ("Elemental Equilibrium"), endurance-charges ("Endurance charges"), es-recovery-keystones ("Energy shield recovery keystones"), flat-physical-damage-reduction ("Flat physical damage reduction"), forbidden-jewels ("Forbidden Flame and Flesh"), fortify ("Fortify"), glancing-blows ("Glancing Blows"), guard-skills ("Guard skills"), heralds ("Heralds"), hollow-palm-technique ("Hollow Palm Technique"), ignite ("Ignite"), impale ("Impale"), inspiration-charges ("Inspiration charges"), intimidate-unnerve ("Intimidate and Unnerve"), iron-reflexes ("Iron Reflexes"), iron-will ("Iron Will"), item-triggers ("Item triggers"), leech ("Leech"), life-reservation ("Life reservation"), lucky-critical-strikes ("Lucky critical strikes"), maim-hinder ("Maim and Hinder"), mana-cost-efficiency ("Mana cost and cost efficiency"), minions ("Minions"), onslaught ("Onslaught"), pain-attunement ("Pain Attunement"), perfect-agony ("Perfect Agony"), physical-taken-as-elemental ("Physical damage taken as elemental"), point-blank ("Point Blank"), radius-jewel ("Radius jewels"), raise-spectre ("Spectre"), receiving-damage ("Receiving damage"), reservation-efficiency ("Reservation and reservation efficiency"), scorch-brittle-sap ("Scorch, Brittle and Sap"), spellslinger ("Spellslinger"), supreme-ego ("Supreme Ego"), timeless-jewels ("Timeless jewels"), totems ("Totems"), traps-and-mines ("Traps and mines"), trigger-rate-cap ("Trigger rate cap and cooldown"), vaal-pact ("Vaal Pact"), warcries ("Warcries"), wither ("Wither").

Batch 1d finish 2026-10-26 (task 027): ascendancy-deadeye ("Deadeye ascendancy"), ascendancy-pathfinder ("Pathfinder ascendancy"), ascendancy-warden ("Warden ascendancy", PoB tree id Raider), ascendancy-slayer ("Slayer ascendancy"), ascendancy-gladiator ("Gladiator ascendancy"), ascendancy-champion ("Champion ascendancy").

Batches 3d + 4e finish 2026-10-26 (task 027, merged by the orchestrator): ascendancy-necromancer ("Necromancer ascendancy"), pantheon-and-bandits ("Pantheon and bandits"), map-modifiers ("Map modifiers"), crafting-methods ("Crafting methods and obtainability"). New gap notes: "Unparsed item lines (task 027 batch 3)", "Pantheon lines PoB drops", "Map thorns damage taken", "Map mods PoB lists as no-ops", "Crafting spawn chance and cost" (vault/Gaps).

Batch 5a 2026-10-26 (task 027): ascendancy-juggernaut ("Juggernaut ascendancy"), ascendancy-berserker ("Berserker ascendancy"), ascendancy-chieftain ("Chieftain ascendancy"), ascendancy-ascendant ("Ascendant ascendancy").

Batch 5b 2026-10-26 (task 027): ascendancy-guardian ("Guardian ascendancy"), ascendancy-trickster ("Trickster ascendancy"), ascendancy-saboteur ("Saboteur ascendancy").

Batch 2c finish 2026-10-26 (task 027, merged by the orchestrator; files "Unique - <Name>.md"): unique-anathema, unique-badge-of-the-brotherhood, unique-circle-of-guilt, unique-entropic-devastation, unique-eye-of-malice, unique-foulborn-three-dragons, unique-kalandras-touch, unique-mageblood, unique-mystic-refractor, unique-nyctas-lantern, unique-ralakeshs-impatience, unique-tabula-rasa, unique-the-light-of-meaning, unique-the-squire, unique-the-taming, unique-ungils-harmony, unique-whispers-of-infinity, unique-willclash. Seeds: EK 4, FR 4, Worb 4; league start 6 (NOT MEASURED headless: Tabula Rasa, The Squire, Nycta's Lantern, Kalandra's Touch, Ungil's Harmony, Willclash).

## Backlog of candidate mechanics (no note yet)

- ailment-effect-from-crit: Critical Mastery 9986 "50% increased Effect of non-Damaging Ailments you inflict with Critical Strikes" (in Worb); removed by Elemental Overload ("Ailments never count as being from Critical Strikes").
- elusive: Assassin Mistwalker and Badge of the Brotherhood (EK seed).
- rage: Berserker and Ascendant Rage (PoB takes Rage from multiplierRage, ConfigOptions.lua:1073, and does not model the gain cooldown or the decay; source tasks/reports/027-evidence/b5a-taa-jb.md).
