# PoB comparison app

A local tool for Path of Exile 1 that compares your build with a target build, for example a guide you are following.
Both builds are calculated by your own installed
[Path of Building Community](https://github.com/PathOfBuildingCommunity/PathOfBuilding) (PoB), so every number is
PoB's number.

It walks the damage of your main skill step by step, the way PoB's Calcs tab does (added damage, increased, more,
effective DPS, crits, speed), puts the target's numbers next to yours, shows the gap at each step and lists where
every number comes from: which item, passive or gem.

**See the idea:** the approved [damage chain mockup](https://koskesh11.github.io/comparison-app/docs/mockup/damage-chain.html)
(Worb against a guide build, real PoB 2.67.2 numbers, Pinnacle Boss). It is a clickable design, not the app.

## Status: work in progress, no app to click yet

Milestone 1 is being built. Working today, in code and tests:

- Load your build plus a target: one of your PoB builds, a pobb.in link or a pasted PoB code.
- The damage chain of the main skill, read from PoB's own Calcs tab, with PoB's own text and sources.
- The target opened next to your build in the same PoB, the two chains side by side, the gap per step, small gaps
  grouped, and warnings where the comparison could mislead (for example party buffs in the target).
- A check that both main skills are set up alike (same part, stages, mines, minion) before the chain is compared.

Next: config differences between the two builds, a button that recalculates your build with the target's setting,
then the local server and the web page. The order and the reasons are in [docs/ROADMAP.md](docs/ROADMAP.md) and
[docs/decisions/](docs/decisions/README.md).

## How it works

- PoB runs headless through its own Lua runtime; the app never computes a game number itself.
- Your PoB install and your builds are only read. The app writes only to `Documents\Path of Building\Builds\AutoBuilder\`.
  PoB itself may write its timeless-jewel cache, as its own GUI does.
- The only website the app contacts is pobb.in, and only when you paste a pobb.in link.
- No account, no telemetry, no API keys.

## Requirements and setup (developers)

- Windows with Path of Building Community installed (looked for in `%APPDATA%\Path of Building Community`; set
  `POB_DIR` if yours is elsewhere).
- 64-bit Python 3.12 or newer (developed on 3.14).

```
python -m venv .venv
.venv\Scripts\python -m pip install --group dev
python tools/install_hooks.py
python tools/check.py          # the fast checks; --full adds types, tests and coverage
```

Some tests need a local PoB install and are skipped without one. Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Layout

- `src/comparison_app/` - the app: `pob/` (PoB and its Lua), `analysis/` (one build), `compare/` (two builds),
  `intake/` (loading builds), `app/` (presentation).
- `tests/comparison_app/` - its tests; the two reference builds are in `tests/comparison_app/fixtures/builds/`.
- `docs/` - roadmap, decisions, architecture, how a report is judged, the mockup.
- `mechanics/` - notes on game mechanics (an Obsidian vault).
- `tools/` - the checks and the merge script.
- `engine/`, `gui/` - the first version of the project, frozen and kept as reference.

## License and credits

MIT, see [LICENSE](LICENSE). Copyright (c) 2026 koskesh11.

- [Path of Building Community](https://github.com/PathOfBuildingCommunity/PathOfBuilding): driven by this tool, not
  included here. It has its own license; see `LICENSE.md` in your PoB install folder.
- [Path of Exile Wiki](https://www.poewiki.net): mechanics notes cite it; its text is licensed CC BY-NC-SA 3.0.
- Not affiliated with or endorsed by Grinding Gear Games. Path of Exile is a trademark of Grinding Gear Games.
