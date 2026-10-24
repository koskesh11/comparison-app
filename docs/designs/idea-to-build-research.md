# From a build idea to a verified interaction graph

Source: the worked example from 2026-10-24 ("Voltaxic Rift bow + Foulborn Three Dragons (chaos can shock and freeze),
autobomber in 3.29"). The user asked us to learn from it: how we got the information, how we verify it, and how
the app uses it. Goal: the app turns an idea like this into a full-scale build (task 021 generator).

## 1. Getting the information (what worked)
1. **Break the idea into parts.** Named items and skills (Voltaxic Rift, The Three Dragons Foulborn), plus the
   archetype word ("autobomber").
2. **Turn the archetype into mechanics.** The wiki has no "autobomber" page, so a web search found guides. They
   define it as a chain: Herald of Ice (shatter → explosion) with Herald of Thunder (kill a shocked enemy → storm),
   often with Inpulsa's Broken Heart. Guides are only used to find which mechanics to look up, never as the rule.
3. **Current item text from two sources.**
   - PoB `Data/Uniques/*.lua`, the "Variant: Current" lines.
   - The wiki item page: mechanics notes, legacy variants and version history. These give the patch a line
     changed in (Voltaxic lost "shock as though dealing 300% more damage" in 3.28).
4. **Mod scope from the wiki cargo tables.** Example call:
   `api.php?action=cargoquery&tables=mod_stats&fields=mod_stats.id&where=mod_stats._pageName="Modifier:<ModId>"`.
   - A stat id starting with `local_` affects only that weapon's hits.
   - Ids without it (`base_lightning_damage_%_to_convert_to_chaos`) are global. That decided that the heralds'
     storm and Inpulsa's explosions also become chaos.
5. **One rule page per mechanic, quoted.** Shatter: killed by a hit while frozen; unique bosses never shatter.
   Herald of Thunder: its storm "cannot shock" but can freeze with Three Dragons. Herald of Ice: cold secondary
   damage, on shatter, player only. Inpulsa: "cannot Shock", converted by global sources. Each rule is recorded
   with its patch (the version-history table).
6. **Numbers PoB already has come from the vault or PoB, not the wiki.** Example: shock and freeze thresholds
   against bosses (vault note "Foulborn Three Dragons", built from the PoB formula).
- Fetching: Bash `curl` to `https://www.poewiki.net/w/api.php?action=parse&page=<Page>&prop=wikitext&format=json`.
  Set `PYTHONIOENCODING=utf-8` when parsing. The WebFetch tool gets a bot-check page from poewiki.

## 2. Verifying it
- **Two sources per fact:** PoB data/source plus the wiki. If they disagree, report it; never pick one silently.
- **Patch check:** the version-history / legacy-variant table, plus PoB's variant list. A wiki section tagged
  "potentially outdated" counts as unverified.
- **Scope check:** the cargo stat id (local vs global) for every conversion, "can shock", "cannot X" or trigger
  line the chain depends on.
- **PoB test where PoB models it:** a headless swap in memory. Example: the shock/freeze flags, the conversion
  result, DPS.
- **Vault gap or model where PoB can't:** trigger chains (shatter → explode, kill shocked → storm) and crowd
  control.
- **Open list:** every link the sources don't settle is listed as "not verified", for an in-game test or the
  user. Examples: does a player on-kill explosion still go off on a shattered enemy? Do herald kills count for the
  other herald's trigger?

## 3. Using it: the interaction graph
Store the research as a graph, not prose. Every node and edge cites a source and a patch.
- **Nodes:** effect sources (items, skills, ascendancy nodes, passives). Each has the damage types it deals and the
  flags it sets: conversion (global or local), "X can shock/freeze/ignite", "cannot shock".
- **Edges:** triggers, e.g. `kill frozen enemy by hit → shatter → Herald of Ice explosion (cold)`.
  - An edge fires only if the source's damage type can apply the needed ailment under the current flags.
  - Example: with the Foulborn helmet the cold line "can Ignite but not Freeze or Chill" stays, so Herald of Ice
    explosions cannot freeze.
- **Check:** follow the edges from the player's own skill.
  - **Closed loop:** the archetype works on its own ("autobomber").
  - **Loop that needs the player's skill to restart:** "semi".
  - **Missing edge:** "breaks at X". Example: nothing but the bow shocks, and the explosions can't freeze.
  - Bosses are checked separately. They can't shatter, and ailment thresholds come from PoB.
- **Fixing a break:** search the catalogue for a node that adds the missing edge. Example: a second shock source,
  or cold that can freeze. Each candidate becomes a build variant.
- **Then the generator:** the chosen package goes to the generator for gems, tree, gear, tiers and PoB numbers.
  Chain links PoB can't measure are shown as labelled model or gap rows, never folded silently into DPS.
- **Output shape:** works / semi / breaks at X, a separate boss plan, the open list, and a source on every line.
