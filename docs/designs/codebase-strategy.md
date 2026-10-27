# Codebase strategy (2026-10-26)

Why this exists: the public feedback on 2026-10-26 was that the repo has no visible structure, the docs don't say what
the app is or why it is built this way, and AI process files bury the code. This page records the owner's decisions and
the order of the clean-up.

## Decisions (owner, 2026-10-26)

1. **The app is a build analyzer first.** You load your build and a target build. Path of Building calculates both, and
   the app shows how each one scales (increased, more, crit, penetration, enemy modifiers, speed, projectiles) and where
   the gap between them comes from. Every number is PoB's. The build generator comes back later, built on top of the
   analyzer.
2. **The generator work is frozen** on its branch (`task-035-fireball-starter`, about 26,000 lines). It is not merged.
3. **The AI workflow files are not published.** That covers `tasks/`, `docs/studio/`, `.claude/` and the agent tooling.
   They stay on the developer's machine (commit 4caf626).
4. **Restructure, don't rewrite.** The working code moves into clear folders a step at a time, with every test passing
   after each step. Only the UI is rewritten, as part of the analyzer redesign.

The strategy review (step 0) was skipped: the owner made these four scope decisions directly.

## Grilling session (owner, 2026-10-26), round 1

These answers revise decision 1 and the audience:
- **Audience: the owner only.** The community audience is dropped.
- **Compare against one target build AND many builds** (e.g. top builds of the same skill).
- **Each build keeps its own settings.** The settings differences are pointed out. Later, the tool explains why a box is
  checked, once the knowledge base is big enough.
- **The main view is the scaling vectors side by side.** There is no verdict line.
- **The process is light:** Claude, the tests and one code review per step. The full process applies only to game logic.
- **Contributors:** maybe later; the code is made easy to join along the way.
- **Platform:** Windows and the browser, as today.
- **Rename** `vault/` to `mechanics/`.

## Grilling session, round 2

- **Private for good.** The docs are written for the owner, Claude and the owner's developer friends.
- **Settings differences:** list every setting that differs, sorted by how much it changes the numbers. Also flag
  settings that look wrong even when both builds agree (e.g. Focused Channelling with no channelling time).
- **The knowledge base grows from comparisons and the owner's corrections.** Claude drafts the notes, the owner verifies
  them, and the analyzer explains settings with verified notes. The 164 interaction notes are the starting point.
- **Defence vectors too**, after damage.
- **Main skill first.** Other skills, minions and damage over time come later.
- **Item, tree and gem differences become the drill-down** under each vector, replacing the separate ranked list.
- **Frozen with the generator:** the audit suggestions and both apply-and-save buttons. The key-number tiles stay.
- **Open:** AI inside the app (Q9), to discuss further.

## Grilling session, round 3 (no suggested answers, per the owner)

- **The job:** decide what to change, see why my build is weaker, and check whether the guide's config boxes are correct
  for how the game actually works.
- **Why not PoB by hand:** "I don't want two PoBs open side by side going line by line. The tool should point out all
  the vectors, and where each comes from, right away."
- **Whose numbers:** in the Worb case, the guide author's (his channelling time was right).
- **Worth it in a month if:** the app points out ALL the flaws, not just the obvious ones (owner's correction).
- **What a flaw is (owner's example):** "If I'm missing flat damage on Fireball compared to the aspired Fireball PoB,
  point it out: you're missing flat on Fireball, and this is how to fix it." A flaw is a gap in a scaling vector
  against the target build, together with how to close it.
  - Design consequence (Claude): "base damage" splits into the skill's own base, added flat damage, and conversion or
    "gain as". They are separate vectors.
- **Budget:** not a constraint. Show where each gap comes from and how to fix it; offer alternatives when the fix is too
  expensive.
- **What a fix may cost (owner's examples):**
  - Fine: crit multi from an essence-crafted ring that drops resistances below max, because resistances can be found
    elsewhere.
  - Too much: Nimis, used for the return-projectile shotgun, at 90+ divines ("with that money I could make an entire
    build that clears the entire game").
- **Ordering:** gaps under 3% go into one expandable group. Bigger gaps are listed by DPS gain, largest first. The same
  rules apply to defensive values.
- **Over-investment is a flaw.** Example to flag: "you have 1000% increased damage but only 10% more."

## Grilling session, round 4

- **Prices:** unique prices come from poe.ninja's documented economy data; rare prices don't matter much. The owner
  wants a chat box where he can say that some mods on one or more items are unobtainable (too hard to craft).
- **Alternatives may use any vector**, not only the missing one. Example: missing 200% increased spell crit chance from
  wand and shield → find an interaction that makes up the DPS, or another stat such as cast speed, or +1 gem levels on
  the shield if the guide lacks them.
- **Expensive and build-defining items:** show how close the build gets without the item. Build-enabling items (e.g.
  Cast when Stunned for Chieftain needs specific jewels) that the owner can't afford make the build unobtainable for
  him. Gaps PoB can't calculate go to the knowledge base, case by case with the owner.
- **The 3% rule is per difference:** a single difference (e.g. crit multi on the target's rings) worth ≥3% DPS between
  the two builds gets its own row; everything under 3% is grouped. The group header shows its combined total (Claude's
  default).
- **Marginal value for every vector:** the tool shows what the next step of each vector buys, so every imbalance shows
  up.

## Grilling session, round 5 (the owner's game knowledge, verbatim in substance)

- **Flaw checks: "do the mechanics actually work as advertised?"** Example: a creator's Pconq Assassin league starter
  claimed 24M DPS, which was impossible:
  - at his attack speed he couldn't sustain his life flasks;
  - the mapping setup was toggled while bossing, so on-death buffs were active in the boss setting.
- **Why each of the guide's boxes is correct (owner's reasoning):**
  - **Unnerved:** the glove implicit gives the chance. 6 Winter Orbs at over 4 casts/s means well over 1 hit per second,
    so about 10% chance keeps the boss unnerved all the time. In general: uptime = hit rate × chance, against the
    duration.
  - **Ignited:** a little fire damage anywhere is enough.
  - **Scorched ground:** run over the boss every few seconds. It changes how you play, which is acceptable.
  - **Endurance charges:** probably the small cluster Enduring Composure (charges when hit), and he gets hit all the time
    with no evasion or dodge.
- **Boxes the tool can't judge:** ask the owner, up to about 1 minute per comparison.
- **Many builds:** the owner asked what the fetch limit is (answered in chat).
- **Drop condition:** the tool gives wrong answers.
- **Chat box:** plain words (AI), plus questions and what-ifs.
- **Budget:** "I wouldn't give you a build I can't afford." Target builds are affordable by definition.
- **Alternatives:** close as much of the gap as possible. "The point is to give alternative scaling vectors. Many people
  just stack stats because they're rich in-game." The owner expects alternative scaling-vector recommendations.
- **Build-enabling items:** PoB knows most mechanics. Over time the knowledge base should recognise build-enabling
  pieces from the items, gems, jewels, supports and config a build uses. Whatever it doesn't know, the owner explains
  in the chat box.

## Grilling session, round 6

- **Import:** "I don't care how the PoB gets from ninja into PoB, as long as it gets into our app." DECISION (Claude,
  terms): the owner pastes a PoB code (poe.ninja's "Copy PoB" button) or a link, and the app imports it. No automatic
  fetching from poe.ninja, because its terms forbid third-party use.
- **Alternatives don't need to make up all the lost DPS.** Show different ways to scale. Example: the target pushes crit
  multi to enormous heights, which may be expensive, so offer another vector, such as cast speed or a unique-item + skill
  gem interaction.
- **Build-enabling items:** expect not to understand most interactions at first. The owner explains each time, and the
  knowledge base grows until it can spot them. A good test: remove the unique and see what breaks.
- **Sustainability checks:**
  - **Flask charge balance.** Poisonous Concoction uses life flask charges on every throw. If it spends more than it
    gains, it isn't sustainable.
  - **Charge generation.** Frenzy charges checked, but the only source is "on kill" → not true on bosses.
  - There are many rabbit holes like these; work through them one by one, later.
- **On-hit effects** (maim, intimidate, unnerve, curse on hit): uptime = hits per second × chance, against the duration.
  11 hits/s at 10% is effectively always on; 1 hit/s at 10% is once every 10 s. The tool must do this calculation to
  check a setting.
- **Owner's answers are knowledge, not rules.** "I can be wrong, and PoE is full of niche cases; only rarely is
  something an actual rule." Store the answer together with its build context and the reasoning ("understand why I gave
  the answer"), not as a universal rule.
- **What a wrong answer looks like:** the owner knows a different vector works (e.g. cast speed instead of crit multi on
  rings), and the tool says nothing can be done. "If you don't learn from these mistakes and there's no evolution in the
  app, there's no point in keeping it."
- **Chat box:** the owner only. It runs on his Claude subscription, never an API key.

## Grilling session, round 7

- **How the owner judges learning:** he uses the app often. If there's no improvement in 6 months and the same mistakes
  keep coming back, it isn't learning. Design consequence (Claude): every correction is logged, so a repeated mistake
  can be detected.
- **Correction:** the owner withdrew the "cultist thing" sentence in his Q26 answer (a dictation error). It was never
  recorded here.
- **The fight is always a pinnacle boss.** Each build's other boxes stay its own and are judged against a pinnacle boss
  fight.
- **Many builds:** compare as many builds as possible with each other: what each build does well in one department and
  badly in another, and take the best option out of many.
- **First version:** scaling vectors, alternatives, sustainability checks ("that'd be amazing").
- Standing preference, not re-asked: every number comes from PoB or a mechanics note. The AI only explains and proposes.

## Grilling session, round 8

- **Many builds:** no request to poe.ninja. The owner pastes them.
- **Combining the best of many builds:** discussed case by case with Claude in the VS Code chat, debating and finding a
  middle ground. It is not automated.
- **Teaching before a chat box exists:** here in VS Code (Claude Code chat). The owner dictates by voice: "the easiest
  and fastest way".
- **Chat box in the app: yes, ideally with speech-to-text** (the owner talks, his words appear as text). Technical
  choice (Claude): a microphone button using the browser's built-in speech recognition. Chrome sends the audio to
  Google to transcribe. Windows voice typing (Win+H) already works in any text box today. The chat runs on the owner's
  Claude subscription (`claude -p`, no API key).

## Grilling session, round 9: the owner's two biggest concerns

1. **Software design (concern no. 1).** Developers who answered the Reddit post said the setup is bad. The 1,300-line
   single HTML file is one example, and the owner thinks it represents the whole project. He has no design experience,
   relies on Claude, and wants to go through the design questions together and fix it.
2. **Real learning (concern no. 2).** Extend the knowledge beyond conversations with the owner, and add pattern
   recognition: builds plus the owner's corrections should actually make the system smarter, not just get written down.
   The same goes for interactions. First step: the system learns on its own from builds, the PoE wiki, poedb and PoB
   itself, i.e. how skills, items, uniques and ascendancy nodes interact.
   - A software design audit of main is running (architect agent → docs/designs/design-audit-2026-10-26.md).

## Grilling session, round 10

- **Design:** Claude proposes a best-practice design and shows a plan before designing. The owner relies on Claude for
  this.
- **Developer friends:** not asked yet; unknown whether they will touch anything.
- **Proper design first.** Weeks with few new features are fine "as long as it works".
- **Teaching:** treat it as a learning experience. Claude teaches software design and development without going deep
  into the technical details. The owner wants to understand the design side.
- **Learning:** "I expect you to learn from everything we say." The owner asked how Claude actually works: does it
  remember by itself, or does it have to write things to a file and read them back? (Answered in chat.) That answer
  decides what "smarter" means.
- **Source conflicts** (wiki vs poedb vs PoB): ask the owner.
- **Overnight experiments** on the owner's PC: fine.

## Grilling session, round 11

- **Strong form for everything**, built in the knowledge base and checks rather than as loose notes. Account for the
  owner's mistakes too: what he says is taken as given but never as a 100% rule. When something conflicts, or PoB's
  numbers don't add up with what he said, question him.
- **Self-learned findings:** when an experiment finds something interesting, audit the owner about it. Sit down, have a
  meeting, ask about the finding, and talk it through so he can give a precise answer.
- **Learning targets (the owner's examples; mechanics NOT yet verified):**
  1. **To spot early:** Fireball is a projectile that explodes, so it has a projectile part and an area part. How does
     it interact with Far Shot (more damage the further the projectile travels) and pierce (flies through enemies and
     keeps gaining Far Shot damage)? A unique helmet grants Far Shot. Which parts does each modifier affect?
  2. **For later:** Forbidden Rite of Soul Sacrifice deals chaos damage based on the energy shield it uses, so defence
     scales offence (e.g. ~17,000 ES with Chaos Inoculation for chaos immunity). Add the Foulborn Three Dragons helmet:
     chaos damage can shock, ignite or freeze, with two of those mods possible at once. Shock is a damage multiplier
     (enemy takes increased damage) and freeze is a defensive layer. For comfort, run it with Cyclone and Cast on
     Critical Strike, which keeps you moving through mobs. The owner has not PoB'd it; it's an idea.
  - **Expectation:** in roughly 9 months the system comes up with ideas like no. 2 by itself.

## Grilling session, round 12

- **Review meetings: once a day,** at the first VS Code session after the owner boots his PC.
- **Exam:** yes. Keep expanding it so learning becomes measurable. The two examples above are its first questions.
- **What can't be measured:** the owner explains it briefly, using one agreed vocabulary for the whole project.
  - Example: "comfort" (Cyclone) = never standing still, plus permanent phasing, so you walk through enemies.
  - If the owner strays from an agreed term, Claude says it doesn't understand and reminds him.
  - Terms live in a glossary in the knowledge base.
- **PoB vs the owner's word:** judged case by case. No general rule.
- **Naming decision (Claude):** one word, "mechanics", for both the data folder (`vault/` → `mechanics/`) and the code
  package that loads it.
- **Design audit saved:** docs/designs/design-audit-2026-10-26.md.
- **League 3.30 starts 13 November 2026.** No hard deadline: "let's see how far we get". The owner will provide the 3.30
  patch notes. Claude checks every mechanics note, exam question and glossary term against them, and flags results that
  rely on 3.29 rules until PoB updates.
- **Target design written and split:** docs/designs/target-design.md (main, 279 lines) plus target-design/*.md. A
  walkthrough with the owner is in progress: lesson 1 (layers), lesson 2 (folders), intake/, league/, compare/.

## Grilling session, round 13 (2026-10-27, first daily review; nothing ran overnight)

- **The vectors are the terms of the damage calculation, whatever the source.** Indigon's "increased damage per mana
  spent" and 600 % increased spell damage from gear are both just "increased". What counts: increased, more, increased
  damage taken, flat damage, penetration, resistance reduction, and so on.
- **The view, for now, is a table:** one row per term. Columns: my build | the target build | the difference | where the
  difference comes from (the list of sources). "Just to see precisely how it looks."
- **"No effect" values stay**, listed in a table of their own, all of them; the rules come later. Overcapped resistances
  are not useless: some mods scale with overcap (e.g. body armours with crit chance per overcapped lightning resistance).
- **One-to-one comparison first.** The multi-build comparison comes right after and is high on the agenda.
- **Scenario picker like PoB's:** Standard Boss, Pinnacle Boss, Uber Pinnacle Boss, plus Mapping. (PoB's box "Is the
  enemy a Boss?" offers No / Standard Boss / Guardian/Pinnacle Boss / Uber Pinnacle Boss, default Pinnacle:
  Modules/ConfigOptions.lua:2086.)
- **Different config settings between the two builds are pointed out in the UI** ("the target has other settings than
  yours").
- **Test builds:** "yes, make it public" (meaning to be confirmed in round 14).
- Decided by Claude: imported targets stay in `Builds\AutoBuilder\imports` (the owner opens them in PoB); the frozen
  features are kept as the git tag plus one README sentence.

## Grilling session, round 14

- **Test builds:** EK, Worb and copies of these builds may be committed. The repo stays completely private.
- **Rows come from the official damage calculation:** PoB's Calcs tab and its breakdowns, cross-checked against the PoE
  wiki's damage calculation page. Claude derives them and checks that PoB covers everything the wiki lists.
- **The model is PoB's Calcs tab, "Skill Hit Damage" section** (owner's screenshots of his Fireball, skill part
  Projectile): the app compares that page for both builds and shows the differences. Hit damage only. The visual design
  is Claude's proposal; the owner reviews it.
  - Fact (Claude): the Calcs row "Total Increased" shows generic Damage under "All Types" (308 %) and the type's own
    plus elemental under the type (Fire 426 %). The hit multiplies by 1 + (308 + 426) / 100 = 8.34, as the hover shows;
    "More" multiplies 1.27 × 1.40 = 1.778 (Modules/CalcSections.lua:164-178). Added damage is scaled by damage
    effectiveness, the skill's base is not: 1,883 + 308 × 4.80 = 3,361.4.
- **Sources:** for every value that differs, all sources one click away. Example: mine adds 308–471 fire, the target
  adds 1,000–2,000: why does the target have so much more?
- **Difference column:** both the raw gap and what it is worth in DPS (PoB recalculation).
- **Scenario:** sets only "Is the enemy a Boss?" for both builds; every other box stays each build's own and is checked
  against the scenario. Default: Pinnacle Boss.
- **Draft notes:** only verified notes change numbers. A draft is shown next to the number as "if this note is right: X".

## Grilling session, round 15 (2026-10-27)

- **Q1 layout: yes, the damage chain.** "Then we fix other things along the way." The design test is whether a human
  can understand it. The owner asked for an example with real data.
- **Example built** (Claude, 2026-10-27): a clickable mockup with real PoB 2.67.2 numbers, Worb vs pobb.in/v8XfQn1yFnAs,
  Pinnacle Boss, Winter Orb part 1: https://claude.ai/artifact/Reo6j5waAVyfGARJ9Bmtpj. The data comes from PoB's own
  hover breakdown, `actor.breakdown[damageType]` (CalcOffence.lua:3360-3610), dumped by a scratch script (chain.lua).
  The steps multiply to ×2.06; PoB's totals give ×2.07 (2,967,940 / 1,435,204), and the 0.3 % gap sits in the summed
  increased rows. Findings it showed: Focused Channelling counts 0 % on Worb (no channelling time set; target 3 s)
  = +60 %; Winter Orb gem level 22 vs 24 = +19 %; Worb has more increased (1,014 % vs 886 %); the target counts the
  enemy as Ignited, Scorched and Unnerved; Eye of Malice turns −27 % into −40 % enemy resistance in PoB.
- **Mockup verdict (owner):** "This looks fantastic. This is exactly how I envisioned it to look like." Functionally
  right ("functional, it's exactly what I wanted it to be"); colors and visual design get reworked later.

## Grilling session, round 16 (2026-10-27, owner on lunch break)

- **Row order:** yes. PoB's calculation order, with the biggest-first chips on top.
- **Skill parts and skill settings** (Fireball projectile / explosion, Bladefall blade count): compare with the settings
  saved in the two PoBs, exactly as they are. Do not model situations such as a boss next to a wall, where a pierced
  projectile hits the wall and the explosion shotguns. How these skills behave gets discussed later. OPEN (round 17):
  when the two settings differ, does each build keep its own and the difference gets flagged, or is your build
  recalculated with the target's setting?
- **No throwaway prototype.** "I wouldn't want you to do work that gets thrown away." The chain is built for real, in
  the new structure. The mockup and its scratch script are the reference.
- **Folder tour: later today.** Also later today, together: an architecture review of the whole project. Go through
  every file (how it's written, the logic behind it), look at it critically, and decide how much a restructure makes
  sense.
- **Skill settings must match (round 17, owner):** "You cannot just compare pineapples to beans." If the skill's own
  settings differ (Fireball on projectile vs explosion, Bladefall blade count), flag it immediately and tell the user
  that the skill settings differ. Example to detect: Lightning Strike (or Smite) can double hit at the right distance,
  so some PoBs carry the main skill twice, one copy set to the strike part and one to the projectile part. That must be
  flagged too. From a skill-setup point of view both builds have to be the same.
- **After the flag (round 18, owner: "for now, we can do that"):** the chain is hidden; one button recalculates your
  build in memory with the target's skill setting (your file is never changed). This will change as interactions and
  knowledge grow. In about nine months Claude should make these calls on its own, so the rule gets evaluated over time.
- **Owner's expectation:** Claude knows what good software looks like (e.g. a clean pipeline) and gives him
  instructions on it. Where Claude doesn't know something, it says where he is wrong and why. He pasted a conversation
  with another AI (layers, separation of concerns, one-way dependencies, anti-corruption layer for PoB, strangler fig,
  architecture tests, CI). Claude's assessment: standard knowledge and right for us, except the parts that assume we
  own the math (PoB is the math), millions of calculations per second, CQRS, and swapping PoB out (YAGNI). Root cause
  admitted: the rules were known but never enforced by tools, so feature pressure won. Fix: enforce them with tests and
  CI (import rules, size limits, linter, type checker).
- **What "sound" means (owner, round 18):** a way to enforce all these rules and practices in this project at all
  times, always. The software will grow, especially when build creation starts in about six months, with agents
  running at the same time. Clean architecture, development and data design are paramount. When the app is good
  enough, the owner presents it to the community: "I don't want to be called a shit developer again."
- **Fact (2026-10-27):** today nothing enforces them. There is no .github/workflows, no pre-commit config, no
  pyproject/linter/type-checker config and no git hooks; only Claude's own hooks (guard_readonly.py). OPEN (round 19):
  how enforcement works. Once settled, write the rule into tools/make_agents.py (project rule on rule changes).

## Grilling session, round 19 (2026-10-27, owner back to work mid-round)

- **Q1 (tools enforce):** the owner is not confident. "Rules are rules", with no exceptions in Claude's logic; can a
  situation occur that breaks a rule set for everything? He asked for an alternative. Claude's answer (given in chat,
  not yet discussed): checks are defaults, not laws. Every check gets a written escape hatch: an exemption in the code
  with its reason (as linters do with `# noqa`), listed and counted, and every new exemption is checked in review. Limits
  (e.g. 800 lines) can be changed by decision. The weaker alternative is "warn, don't block". Recommendation: block by
  default, exemptions allowed only with a written reason.
- **Q2 (where it blocks):** the owner expects slower development and much higher token use, and asked for an
  alternative. Claude's answer: the checks are programs, not AI. They cost no tokens; tokens are spent only when an
  agent fixes a failure, which is cheaper now than later. Alternative: fast checks (linter, imports, sizes: seconds)
  on commit; slow ones (type checker, full tests, about 70 s) only when merging into main, through a local merge
  script. GitHub checks wait until before going public. Recommendation: that alternative.
- **Q3 (ratchet):** the owner asked whether it is normal and best practice; he doesn't know it. Claude's answer: it is
  a technique, not a tool, and the standard way to adopt checks in existing code. Examples: SonarQube's "Clean as You
  Code" (only new code must pass), PHPStan's and detekt's baseline files. Today's violations go on a list, a check
  fails only on new ones, and the list may only shrink.
- **Q4 (checklist + cold review):** yes.

## Grilling session, round 20 (2026-10-27)

- **Q2 (fast checks on commit, full checks in a local merge script, GitHub checks before going public):** yes.
- **Q3 (ratchet):** yes.
- **No human reviewer exists.** "I don't have a friend that does it right now. I have nobody participating in this
  project. No developer." The cold review is done by a fresh AI reviewer with no project history. It gets only the repo
  and must explain the structure and run the tests. Never plan around a developer friend again.
- **Q1 (block by default, written exemptions):** the owner asked what "limits change only when you decide" means.
  Re-asked in round 21.
- **Q5 (review format):** the owner asked whether Claude has enough context to judge each file. Answered and re-asked in
  round 21.
- Tests folder (owner's question): 47 tracked files in one flat folder: 30 tests, 5 helpers, 4 scripts that are not
  tests (pin_golden, record_guide_snapshots, perf_baseline, spike_guide_compare) and 7 data files. Test names carry
  process words (gate2, gate4_*). The golden tests need PoB and the owner's builds.
- **Restart? (owner, round 20):** "I'm getting the impression that it might be a good idea to restart this whole project
  new and fresh." Claude's view: not from zero, because the PoB bridge, the write guards, the server security and the
  importer are the parts the 2026-10-26 audit says to keep, each paid for with bugs. Proposed alternative: a new repo
  with the target layout and every check on from the first commit, porting in only what the analyzer needs (about
  2,000 of the 9,280 engine lines, with their tests). The rest stays in the old repo as reference and is ported only
  when a feature needs it. OPEN (round 21).

## Grilling session, round 21 (2026-10-27)

- **Limits are Claude's to manage (owner):** "I am not sure if there is any cases or circumstances where a file should be
  more than 400 lines. This is an architectural question ... something I would expect you to manage and give me
  recommendations on." Claude's rule: hand-written source never goes over 400 lines, with no exemptions; a file that
  needs more is doing two jobs and gets split. Only files we don't write are exempt, each listed with its reason:
  vendor files (engine/_SimpleGraphic.def.lua, 516 lines, PoB's runtime API definitions; HeadlessWrapper.upstream.lua),
  generated files and data (golden.json, fixtures). Claude changes limits and reports the change.
- **Owner's concern about the review:** can Claude handle 9,280 engine lines (399 KB, roughly 110,000 tokens) at once,
  when the context between every line matters? Claude's answer: loading it is possible, but attention to detail drops
  when a context is that full, so the review does not depend on it. Strategy: (1) a map built by tools, not by reading
  (imports, the calls across files, the Python-Lua calls, each file's public functions); (2) one reviewer per area
  (about 1,000-2,500 lines) with the map and the neighbours' interfaces; (3) a cross-area pass over the map and the area
  reports, not the code; (4) every verdict cites file:line and is checked by re-opening the lines. OPEN (round 22).
- **Owner asked what a new repo adds.** Claude's answer, which revises its round 20 recommendation: the benefit is
  "carry over only what's needed, checked at the door", and that works in this repo too (a new `src/` folder where
  every check applies; `engine/` frozen as reference, deleted file by file, and an import rule stops `src/` importing
  it). A new repo adds only a clean history and no old branches or worktrees. The history can be made clean once, when
  going public. Same repo keeps the studio tooling, worktrees, the engine\cache junction and the golden tests working
  without re-pointing. OPEN (round 22): carry over yes/no, and where.

## Grilling session, round 22 (2026-10-27)

- **Decision 4 changes (Q6a, yes):** carry over only what the analyzer needs; every piece passes all checks on the way in.
- **Q6b:** in this repo, with a full backup first (owner: "make a clone of this entire project ... with a date stamp. So
  we have a backup if anything goes wrong"). Done in task 044: `old-project-2026-10-27/`, read-only, ignored by git.
- **Q5 (review method: map, one reviewer per area, cross-area pass, claims checked):** yes.
- Decided by Claude: the ratchet (Q3) is only needed if old code is checked; `engine/` is frozen and unchecked, `src/`
  is clean from its first file, so no baseline list is kept.
- Fact for the importer: PoB itself downloads pobb.in builds from `pobb.in/pob/<id>` (Modules/BuildSiteTools.lua:29);
  pobb.in's robots.txt (fetched 2026-10-27) disallows `/pob/` and `/*/raw$` for crawlers alike. OPEN (round 23).

## Grilling session, round 23 (2026-10-27)

- **Q7 (old app frozen and runnable, features come back only when the analyzer needs them):** yes. The owner asked how
  hard bringing an old feature back is; answer in round 24's message (port with its tests, cost depends on how tied it is
  to `Auditor` and the Lua string protocol).
- **Q8 (first milestone):** yes, "those four points are exactly valid": loads your build plus a target (pobb.in link or
  pasted code), shows the damage chain like the mockup, flags skill-setting and config differences, all checks green and
  the cold AI review passes.
- **Later requirement (owner, with a screenshot of mockup row 8 "Critical strikes"):** item detail behind a source. The
  row "Crit multi: Cobalt Jewels (2)" shows only the gap (— vs 34). Hovering it should show the target's actual jewels
  (the items and their mods), because the owner has no crit-multi Cobalt Jewels and wants to see what the target uses.
  Not part of milestone 1.
- **Q9 (pobb.in import: PoB's own address `pobb.in/pob/<id>`, one request per pasted link, never bulk, pasted codes
  accepted):** yes.
- **New request: one folder per project.** "Take the entirety of this project, everything that is inside pob
  autobuilder folder, and put it into a new folder inside pob autobuilder. Excluding the old project ... call this
  project comparison app or something like that ... a clean distinction between this project that we are advancing
  with and the old project." Task 045 moves the repo to `Desktop\pob-autobuilder\comparison-app\`, next to
  `old-project-2026-10-27\` (result and evidence in tasks/archive/045-move-into-comparison-app.md).

## Grilling session, round 24 (2026-10-27, in comparison-app)

- **Merge the frozen generator?** Claude's evaluation: no, now or later. Task 035 stopped mid-gates (early GATE 2 NOT
  PASS: 2 HIGH, 17 MEDIUM); the generated Fireball wears a 173-Str body armour at 74 Str (PoB reports requirements, the
  generator never read them); 13 code files over 400 lines; it added a second way of calling PoB (a JSON bridge on top
  of `pobhost.run`, which evaluates Lua source built as text). What must be right first is the PoB access layer, which
  the analyzer and a later generator both sit on. Owner: not now; first do the grilling decisions, then go through the
  code that is not frozen.
- **Owner confirmed the summary** ("do whatever we discuss in this grilling session first"). Task 101 wrote the rules
  into tools/make_agents.py, tagged the frozen heads (`frozen/generator-035`, `-t14`, `-tree`, round 13's "git tag")
  and parked the 9 tasks that waited for the generator (038's PoB recalculation finding goes into the carry-over review).
- **Open for the owner:** "private for good" (rounds 2, 14) vs presenting it to the community when good enough
  (round 18). The rules keep the "before going public" steps planned and leave the decision to him.

## Grilling session, round 25 (2026-10-27): order of work after milestone 1

The owner's ranking ("this is the order in which I want you to structure whatever we do after milestone 1"):
1. Alternative scaling vectors, the marginal value of each vector, build-enabling items.
2. Defence vectors, other skills, minions, damage over time.
3. Sustainability checks (flask charges, charge sources) and on-hit uptime (hits/s × chance against the duration).
4. Hovering a source shows the target's actual items and mods (the Cobalt Jewels example, round 23).
5. The in-app chat box on the owner's Claude subscription: speech-to-text, and typed text too.
6. Comparing many builds (revises round 13, where it came right after the one-to-one comparison).

The exam and the glossary are ongoing and not ranked. Written into tools/make_agents.py (Project facts, task 101).

## Grilling session, round 26 (2026-10-27): what we use from the old project's way of working

Trigger: in task 102 Claude dispatched the old studio's review-lead and engineering-lead without explaining them. Owner:
"Right now, everything goes on hold. The old structure with the old departments, I was not aware that you're going to
reuse that." Root: `.claude/settings.json` (`"agent": "orchestrator"`) starts every session as the old studio's
orchestrator (30 roles generated by tools/make_agents.py); it came along with the move into comparison-app and task 101
kept it without asking. Also came along: 343 skills linked into `.claude/skills/` by tools/link_skills.py (from the
superpowers, ECC and skills-CLI plugin folders), the read-only guard hook, the lessons files (docs/studio/learnings/),
tools/run_tests.py and tools/token_usage.py. All of these are git-ignored; there is no CLAUDE.md.

- **Q1 (who does the work): (b).** One Claude session works directly with the owner. Fresh AI reviewers are started only
  where the owner decided: the per-area review (round 21) and the cold review at milestones. No departments, no
  orchestrator hierarchy.
- **Q2 (no hidden agents): yes.** Any new kind of agent or role needs the owner's yes once; every agent Claude starts is
  named in the message before it runs (which, what for, time box).
- **Q3 (read-only guard hook): yes, keep it** (blocks edits to the PoB install and Documents\Path of Building).
- **Q4 (task 102's partial results): yes.** The map, the six area reports and the layout/checks draft stay as input;
  the cross-area pass and the line re-check resume after this grilling, done the Q1 way.
- Q5-Q11 (rules file, lessons, task files/gates, reviewer role, worktrees, skills, tools) were withdrawn unanswered:
  the owner set a principle first (round 27).

## Grilling session, round 27 (2026-10-27): "a fresh run"

- **Owner's statement:** "To be honest, I want to get rid of the structure that we had in the old project. This is a
  fresh run. Keep that in mind. And grill on that statement."
- **Q1 (what "structure" covers):** Claude evaluates whether anything old can be used at all, the AI studio included
  (rules, lessons, task process, skills, worktrees, old planning docs). Owner: "I'm not keen in keeping any of it."
- **Q2 (nothing old carries by default; archived, not deleted):** yes.
- **Q3 (project memory):** keep "short answers". The 19-slide deck "can be deleted entirely ... It's very outdated."
  Whether "rules live only in tools/make_agents.py" makes sense: Claude decides from a design standpoint.
- **Q4 (machine-wide setup: ECC rules, superpowers, global agents, own skills):** Claude evaluates how much sense keeping
  them makes.
- **Owner's goal for the restructuring:** "my first and foremost biggest goal with this restructuring is to have good
  design. This also holds true for rules and decisions and how everything is located. And how things will be accessed."
- Evaluation written: docs/designs/old-project-evaluation-2026-10-27.md (round 28 asks on it).

## Grilling session, round 28 (2026-10-27): on the evaluation

- **Q1 (drop the old way of working except a fresh reviewer, the task card + log + resume point, dated decisions, the
  guard hook; triage the 56 lessons once):** owner asked "is that good design?" Answered and re-asked in round 29.
- **Q2 (eight old rules come back: evidence rule, failure modes 1-9 as the analyzer-output checklist, PoB install and
  builds read-only, trade-offs not verdicts, every number traceable, PoE rounds down, Worb + CoC EK Assa as reference
  builds, PoE wiki via curl):** yes.
- **Q3 (one home per kind of rule: checks; ARCHITECTURE + decisions/; ROADMAP; short private CLAUDE.md; settings deny +
  hook; mechanics/; tasks/; private history. The strategy doc becomes history):** yes.
- **Q4 (ECC rules/agents stay installed, the checks and CLAUDE.md override them here; superpowers and the sales,
  marketing, cowork plugins off for this project if Claude Code allows it per project, checked first; only grilling
  by default):** yes.

## Grilling session, round 29 (2026-10-27)

- Claude's answer to "is that good design?": the fresh reviewer, dated decision records and the guard hook are; the
  task file and the lessons triage as first proposed were not (task files grew into 400-line histories; routing facts
  to CLAUDE.md keeps a lessons store under another name).
- **Q1 (revised):** yes. Keep a fresh reviewer, the task card with one overwritten resume point and a short log (done
  tasks move to tasks/done/), dated decision records, the guard hook. No lessons store: every correction goes to the
  home of its kind (game fact -> mechanics/ note, code rule -> check, design choice -> decision record, how Claude works
  -> CLAUDE.md); a tool fact gets fixed, not written down. The 56 old lessons are routed that way once, then archived.
  Everything else is dropped.
- **Q2 (reviewer role):** yes. One read-only reviewer definition in the project, the evidence rule in every brief; the
  cold reviewer gets a clean copy of the repo only.
- **Q3 (order):** yes. (1) restructure the way of working, (2) task 102 resumes with fresh reviewers in the new role,
  (3) the checks for src/.
- Decided by Claude: the archived studio goes to docs/history/ (the private history home from round 28 Q3), not a new
  top-level folder.

## RESUME POINT (current, 2026-10-27 after round 29)

The owner confirmed the shared understanding of rounds 26-29 ("yes"). Next: task 103 (tasks/103-fresh-run-way-of-working.md),
then task 102 resumes, then the checks for src/. Already done: `"agent": "orchestrator"` removed from .claude/settings.json
(sessions start as plain Claude; deny rules and the guard hook kept); the old deck deleted; project memory reset to
"short answers".

## RESUME POINT (superseded, 2026-10-27 after round 25)

0. The owner restarts the session (the new rules load only in a new session).
1. Carry-over review of the code that is not frozen, with the round 21 method: first a tool-built map of engine/ (imports,
   cross-file calls, Python-Lua calls, public functions), then the carry-over set for milestone 1 with one reviewer per
   area, the cross-area pass, claims re-checked. Inputs: docs/designs/design-audit-2026-10-26.md, task 038 (PoB
   recalculation order), the round 24 note on the two PoB call formats.
2. Then the checks for src/ (linter, import rule, size check, pre-commit hook, local merge script, architecture
   checklist) and the src/ folder names (the "Target layout" below predates src/ and says knowledge/ where round 12 says
   mechanics/).

## RESUME POINT (superseded, 2026-10-27 after round 23)

0. Open VS Code / Claude Code in `C:\Users\7800x3D\Desktop\pob-autobuilder\comparison-app` (task 045 moved the repo).
1. The grilling frontier is empty after round 23 (enforcement, review method, carry-over in this repo, old app frozen,
   milestone 1, pobb.in import: all settled). The summary was sent to the owner; waiting for his confirmation that it is
   a shared understanding. Nothing below runs before that yes.
2. After the frontier is empty and the owner confirms: write the enforcement rules into tools/make_agents.py with
   source tags (checks block; limits are Claude's, no exemptions for hand-written code; only vendor/generated/data
   exempt with reasons; fast checks on commit, full checks in a local merge script, GitHub checks before going public;
   architecture checklist on every merge; cold AI review at each milestone and before going public; never write into
   `old-project-*`), run `python tools/make_agents.py .`, tell the owner to restart.
3. Then the review of the carry-over set (method from round 21), then the first moves into `src/`.

## RESUME POINT (superseded, 2026-10-27, owner at work)

1. Round 19: get the owner's yes/no on Claude's answers to Q1 (block by default, written exemptions), Q2 (fast checks on
   commit, full checks at merge through a local script, GitHub later) and Q3 (ratchet). Q4 is answered (yes).
2. Then write the enforcement rules into tools/make_agents.py with source tags and run `python tools/make_agents.py .`
   (tell the owner to restart the session afterwards).
3. Later today: the folder tour, then the file-by-file architecture review with the owner, which decides the
   restructure. Start from docs/designs/design-audit-2026-10-26.md and target-design.md.
4. The mockup: https://claude.ai/artifact/Reo6j5waAVyfGARJ9Bmtpj (private; the owner may share it with a friend via
   Share). Its data script: chain.lua and run_chain.py in session scratchpad 41a1396e-.../scratchpad.
5. This file is uncommitted (rounds 13-19).
- **Priority restated:** "I am still very keen on the architecture and the development design." The Reddit developers
  called the project "utterly garbage" and "horrid". The goal: the software is sound from a developer and architecture
  standpoint, with a clear structure and good development ethics. OPEN (round 17): how we know it is sound (done-when).

## RESUME POINT (2026-10-27, after the round 15 mockup)

0. NEXT (later on 2026-10-27): ask the round 17 question (skill setting differences, see round 16; recommended: each
   build keeps its own setting and the difference shows in the settings box with its worth). Then the folder tour and
   the file-by-file architecture review with the owner, which decides the restructure. The items below are older;
   round 15 is answered.
1. Original round 15 text (answered in rounds 15 and 16):
   - Q1 Layout: a "damage chain", one row per step of PoB's hover breakdown (base from gem, added per type,
     x damage effectiveness, increased all+type, more all x type, effective DPS mod (pen / res / taken), crit,
     casts per second), columns You | Target | Gap | Worth (PoB) | sources drawer; one chain per damage type,
     types under 3 % folded; small gaps grouped. Alternative: PoB Calcs mirror with "you / target" in every cell.
     [yes, damage chain]
   - Q2 Skill part (Fireball: Projectile / Explosion): compare the part the owner's build has selected on both
     builds, flag when the target saved another part, switch to compare the other. [yes]
   - Q3 Throwaway prototype of the table with real numbers before the restructure: Worb vs the guide
     (pobb.in/v8XfQn1yFnAs, hand-compared 2026-10-26). [yes]
   - Q4 Skip the folder tour; explain each folder at its migration step. [yes]
2. Decided by Claude in round 15: a different main skill on the target -> warn and let the owner pick the target's
   skill group.
3. After the grilling: the independent review of the target design (before any code moves), then the yes/no on the
   migration order (target-design/migration.md); fold rounds 13-15 into target-design (scenario picker with 4 entries,
   draft notes off, "no effect" table kept, one-to-one first, vector table instead of the vector catalogue).
4. The 3.30 patch notes come when the owner has them: check them against the mechanics notes, exam and glossary.
5. Uncommitted: this file (rounds 13-15). The owner hasn't asked for a commit.

## Target layout (proposed 2026-10-26; superseded in part: rounds 21-22 carry code into src/ instead of moving files, round 12 names the knowledge folder mechanics/)

```
app/        local web server and its API (today: engine/server.py and the *_routes.py files)
pob/        the bridge to Path of Building: runs PoB's own Lua engine headless (pobhost.py, pob_headless.lua, Lua helpers)
analysis/   what PoB says about one build: key numbers, scaling vectors, where each modifier comes from (audit*, scaling)
compare/    one build against another: the differences, each measured on your build (guide_check*, guide_diff*)
knowledge/  notes on mechanics PoB doesn't model (today: vault/), plus their loader
web/        the UI, split into small files (today: one 1,343-line gui/index.html)
tests/      tests, mirroring the folders above
docs/       README, ARCHITECTURE (one diagram), DECISIONS (why Python, why local, why mechanics notes)
```

## Order of work (2026-10-26; superseded by rounds 21-24, see the current RESUME POINT)

1. Write ARCHITECTURE.md and DECISIONS.md for the code as it is today. No code changes.
2. Move files into the target folders one area at a time. Tests pass after every step, and the app is tried by hand.
3. Rename "vault" to "knowledge" (mechanics notes) in the code, docs and UI.
4. Analyzer feature: the scaling-vector comparison becomes a proper report. The hand-made comparison of 2026-10-26
   (Worb vs pobb.in/v8XfQn1yFnAs) is the reference. It comes with the redesigned UI: one line per difference, effect
   first.
5. Rewrite the README (what the app does, why it's built this way, a screenshot). Then decide whether to go public again.

## Not now

- Generator work, new mechanics notes, pricing.

## Facts for the "many builds" branch (data-sources check, 2026-10-26)

- **poe.ninja.** Its builds and character endpoints return full PoB exports to anyone, but its API page calls them
  internal and "not available for third-party use" (https://poe.ninja/docs/api). GGG's developer docs treat using
  undocumented endpoints as a Terms 7i breach. About 40 research requests were made while checking this; none are in
  the app.
- **GGG's official API** returns only your own characters, and it currently takes no new applications.
- **pobb.in** has no list or search API. Its robots.txt disallows `/*/raw`, which engine/pobbin.py:96 fetches. This
  needs review.
- **Compliant paths:** the owner pastes links or codes himself, or poe.ninja gives written permission.

## Facts for the "AI inside the app" branch (Claude Code docs check, 2026-10-26)

- **Subscription use works.** `claude -p "<prompt>"` runs on the owner's subscription login, with no API key needed as
  long as ANTHROPIC_API_KEY is unset. `--bare` needs a key, and the docs say it will become the `-p` default.
- **Limits:** it shares the Pro/Max 5-hour and weekly limits with Claude and Claude Code.
- **Terms:** limits assume ordinary individual use, and products are pointed to API keys. A personal script is likely
  fine (inferred). Anything the developer friends can trigger should use an API key.
- **Output and runtime:** JSON output is available (`--output-format json`). Calls take seconds (inferred). `-p` runs
  the working folder's hooks, so it should run from a controlled folder.

## Open technical items

- Git history still contains the workflow files, and the old task branches on GitHub still have them. That's fine while
  the repo is private; clean up the history before going public.
- Merging the frozen branch later would conflict with the untracked folders. Port pieces of it instead of merging.
- Finding from 2026-10-26: in PoB, Focused Channelling counts 0% unless the config sets a channelling time. In the
  owner's Worb, Winter Orb DPS went from 1.44M to 2.30M with 3 s set. The analyzer must flag config gaps like this one.
