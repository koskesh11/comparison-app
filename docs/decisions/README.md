# Decisions

One file per decision that is in force: why the project is built and run the way it is. Current state lives in
[../ROADMAP.md](../ROADMAP.md); code rules that a program can check live in the checks, not here.

## Format

`NNN-short-title.md`, numbered in order of writing. Each record has: date, who decided (the owner or Claude), status,
scope (which folders, data or work it governs), then Context, Decision, Consequences. "Grilling round N" names the
session in which the owner made the call.

## Changing a decision

- A new decision that contradicts an old one: write a new record, set the old one's status to
  `superseded by NNN` and leave its text alone.
- Before writing a record, search the other records, CLAUDE.md and the checks for what it contradicts, and give the
  record its scope, so a rule never reaches further than the decision it comes from.

## Index

| No. | Decision | Scope |
|---|---|---|
| [001](001-analyzer-first.md) | The app is a build analyzer first | product |
| [002](002-generator-frozen.md) | The generator is frozen, not merged | engine/, branches, tags |
| [003](003-private-working-files.md) | Working files stay private | tasks/, .claude/, CLAUDE.md, docs/history/ |
| [004](004-carry-over-into-src.md) | Carry code over into src/, checked at the door | src/, engine/ |
| [005](005-audience.md) | Audience: the owner; publishing is open | product, docs |
| [006](006-checks-enforce-code-rules.md) | Programs enforce the code rules | src/, checks |
| [007](007-reviews.md) | Fresh AI reviewers, only where decided | reviews |
| [008](008-way-of-working.md) | One Claude session works with the owner | how work runs |
| [009](009-damage-chain-comparison.md) | The comparison is PoB's damage chain | analyzer, UI |
| [010](010-scenario.md) | The scenario sets only the boss box | analyzer |
| [011](011-skill-settings-must-match.md) | Skill settings must match | analyzer |
| [012](012-build-import-and-external-data.md) | Builds are pasted; one request per link | importer, data |
| [013](013-numbers-and-knowledge.md) | Every number is PoB's or a verified note's | analyzer, mechanics notes |
| [014](014-reference-builds.md) | Worb and CoC EK Assa are the reference builds | tests, fixtures |
| [015](015-what-a-flaw-is.md) | What the analyzer calls a flaw | analyzer, later rankings |
| [016](016-in-app-chat.md) | The in-app chat runs on the owner's subscription | chat (ranking item 5) |
| [017](017-analyzer-checklist.md) | Failure modes 1-9 live in docs/analyzer-checklist.md | analyzer output, reviews |
| [018](018-m1-builds-as-saved.md) | Milestone 1 uses both builds exactly as saved | analyzer M1, src/ tests |
| [019](019-worth-column-after-m1.md) | The worth column and the config ranking come after milestone 1 | analyzer M1 |
| [020](020-pob-numbers-shown-as-pob-shows-them.md) | PoB's numbers are shown the way PoB shows them | number formatting |
| [021](021-the-checks-and-their-tools.md) | The checks and their tools | src/, tests, hook, merge |
| [022](022-mapping-keeps-pinnacle.md) | The Mapping scenario keeps the boss box at Pinnacle | scenario picker |
| [023](023-chain-reads-the-calcs-tab.md) | The chain reads PoB's Calcs tab, pointed at the main skill | damage chain |
| [024](024-gap-size-without-the-worth-column.md) | The size of a chain gap, before the worth column exists | damage chain |
