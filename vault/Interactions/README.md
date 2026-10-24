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
family: ailment                    # ailment | trigger | charge | projectile | buff | resource | defence | uptime
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
seeds: [Worb]                      # seeds that use it: EK | Worb | FR (see Seeds-as-mechanics)
sources:
  - {ref: "https://www.poewiki.net/wiki/Freeze (rev NNN)", kind: wiki, patch: "3.29"}
not_verified: ["..."]
open_questions: ["..."]            # questions only the user can answer
```

## Vocabulary

- `family`: ailment, trigger, charge, projectile, buff, resource, defence, uptime.
- `target` (note and provider): `enemy` or `self`. A line such as Berek's Pass "+5000 Armour while Frozen" is target `self`, not a freeze payoff on enemies.
- `pob.measured`: full (PoB computes it), partial, config (only through a config tick or a hand-set value), none.
- `pob.config[].class`: a = sourced by gear or gem, b = scenario, c = hand-set.
- provider `kind`: unique, foulborn, gem, support, keystone, notable, mastery, ascendancy, tattoo, runegraft, mod, flask, jewel. Optional keys: `variant` (the item variant, or for a Foulborn / mastery option the replaced line), `requires: [...]`.
- provider `role`: enables, applies, scales, abuses, sustains, blocks.
- provider `pob`: full (PoB parses and counts it), partial, config (counted only with a config tick), none (unparsed or not modelled).
- `uptime[scenario].value`: always, high, partial, low, none, pob (use PoB's own number), model (the `model:` above decides).
- `sources[].kind`: pob, wiki, patch_notes, forum, github, discovery (poe.ninja or guides are discovery only and never decide).

## Writer rules

- Never write bare yes/no/on/off as a value: YAML reads them as booleans. Use the vocabulary words (measured and provider pob: full | partial | config | none; seeds: EK | Worb | FR) or quote the string.
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

## Notes (23 ids)

Written so far: [[Freeze]] (freeze), [[Chill]] (chill, with Bonechill and chill effect), [[Shatter]] (shatter), [[Shock]] (shock), [[Damage type can ailment]] (damage-type-can-ailment), [[Elemental ailment count]] (elemental-ailment-count), [[Exposure]] (exposure), [[Enemy ailment threshold]] (enemy-ailment-threshold, new id from the coverage audit).

Other notes of task 027 (written in parallel; ids): coc-trigger, frenzy-charges, power-charges, spell-impale, curse-limit, skill-cost-from-es, max-res-equalise, golem-buffs, arcane-surge, projectile-hits-single-target, returning-projectiles, rampage, flask-uptime, channelling, consecrated-ground.

All 23 ids: freeze, chill, shatter, shock, damage-type-can-ailment, elemental-ailment-count, exposure, enemy-ailment-threshold, coc-trigger, frenzy-charges, power-charges, spell-impale, curse-limit, skill-cost-from-es, max-res-equalise, golem-buffs, arcane-surge, projectile-hits-single-target, returning-projectiles, rampage, flask-uptime, channelling, consecrated-ground.

## Backlog of candidate mechanics (no note yet)

- inspiration-charges: Inspiration support (righteous charges, -34% mana cost, loses charges at 800 mana spent; PoB takes the charge count from config, not from mana spent; interplay with arcane-surge).
- brittle-sap-scorch: the secondary elemental ailments (Brittle, Sap, Scorch) and their sources (Galesight, Watcher's Eye, Leadership's Price, Secrets of Suffering); they count in elemental-ailment-count.
- ailment-effect-from-crit: Critical Mastery 9986 "50% increased Effect of non-Damaging Ailments you inflict with Critical Strikes" (in Worb); removed by Elemental Overload ("Ailments never count as being from Critical Strikes").
- elusive: Assassin Mistwalker and Badge of the Brotherhood (EK seed).
- abyss-jewel-effect: Darkness Enthroned (EK seed).
- radius-jewel: Light of Meaning (Worb seed) and other radius jewels.
