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

## RESUME POINT (2026-10-27, owner going to sleep)

1. Start of the next session = the first daily review meeting. Nothing has run overnight yet; the experiment runner
   doesn't exist. So: a short recap, then continue.
2. Continue the design walkthrough. The owner chooses between:
   - (a) designing `compare/vectors.py` together (the vector catalogue: own base / flat / conversion split, defence
     vectors, which difference belongs to which vector; needs his game knowledge);
   - (b) touring the remaining folders (`analysis/`, `pob/`, `app/`, `web/`).
   Then: section 9's open questions (product questions only, asked neutrally) and the yes/no on the migration order
   (target-design/migration.md).
3. The 3.30 patch notes come when the owner has them: check them against the mechanics notes, exam and glossary.
4. Still uncommitted (the owner hasn't asked for a commit):
   - docs/designs/codebase-strategy.md, design-audit-2026-10-26.md, target-design.md, target-design/;
   - vault/Exam.md, vault/Glossary.md.
5. Not built yet: an independent review of the target design (planned before any code moves).

## Target layout (proposed; an engineering review checks it before the first move)

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

## Order of work

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
