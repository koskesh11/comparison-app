# PoB Autobuilder

A free, open-source, local tool that helps you improve Path of Exile 1 builds. It uses your own installed
[Path of Building Community](https://github.com/PathOfBuildingCommunity/PathOfBuilding) (PoB) as the calculation
engine, driven headless through PoB's own Lua runtime, so the numbers are PoB's numbers.

- Every suggestion comes with a reason ("why"), naming the PoB modifier sources behind it.
- Every number is traceable: it comes from PoB's output, or from a documented mechanics note in `vault/` for things
  PoB does not model.
- The core features work without any AI account.

## Status: early

| Part | State |
| --- | --- |
| Audit of an existing build: numbered, reasoned suggestions you can apply to a copy | Works today |
| Guide check: compare your build with an expert build from a pobb.in link | Early, in the GUI |
| Build generator: complete builds from scratch, starting from a seed | In progress, not usable yet |

Expect rough edges. Please open an issue when something looks wrong; include the build code if you can.

## Requirements and setup

- Windows with Path of Building Community installed (the code looks for it in `%APPDATA%\Path of Building Community`;
  set the `POB_DIR` environment variable if yours is elsewhere).
- 64-bit Python 3.10 or newer (the code uses `X | None` annotations and loads PoB's 64-bit `lua51.dll`). It is
  developed on Python 3.14; older versions are untested.
- Your builds are read from `Documents\Path of Building\Builds` in your user folder. A Documents folder moved by
  OneDrive is not detected yet.

```
pip install -r requirements.txt
```

Start the app by double-clicking `Start Autobuilder.bat` (or run `python server.py` inside `engine\`). It opens
http://127.0.0.1:8765 in your browser. Pick a build and run the audit.

## Safety and privacy

- PoB's install folder and your builds are only read. The app writes to `Documents\Path of Building\Builds\AutoBuilder\`
  (applied suggestions, imported builds) and to its own `engine\cache` and `engine\userdata`. One exception: PoB
  itself writes its timeless-jewel cache (`Data\TimelessJewelData`) in the PoB folder, as PoB's own GUI does.
- The server binds to `127.0.0.1` only and checks the Host and Origin headers of requests.
- Websites it contacts (from `engine/obtainability.py`, `engine/pobbin.py`, `gui/index.html`):
  - `pathofexile.com/api/trade/data/leagues`: the name of the current league.
  - `poe.ninja`: prices, to tell what is obtainable in the current league (cached for 24 hours).
  - `pobb.in`: only when you paste a pobb.in link into the guide check.
  - Google Fonts (`fonts.googleapis.com` and `fonts.gstatic.com`): your browser loads two font families when the
    page opens.
- No telemetry, no account, no API keys in the code.

## Layout

- `engine/` - Python server and optimizer, plus the Lua that talks to PoB (`pob_headless.lua`, `audit*.lua`).
- `gui/` - the local web app (a single `index.html`).
- `vault/` - Obsidian notes (Rules, Models, Scenarios, Gaps) for mechanics PoB does not model. Each note has a
  machine-readable block the engine reads.
- `tests/` - unit and integration tests. `tools/` - test runner and project scripts.

## Contributing

Fork the repo, make your change on a branch, open a pull request. Small, focused pull requests are easiest to review.

```
python tools/run_tests.py          # runs the tests affected by your change, in parallel
python tools/run_tests.py --all    # everything
```

Be aware: some tests need a local PoB install and the maintainer's own builds, so they fail or skip on a fresh
machine. Portable golden tests are pending. Please say in your pull request which tests you could run.

## License and credits

MIT, see `LICENSE`. Copyright (c) 2026 koskesh11.

- [Path of Building Community](https://github.com/PathOfBuildingCommunity/PathOfBuilding): driven by this tool, not
  included in this repo. It has its own license; see `LICENSE.md` in your PoB install folder.
- [poe.ninja](https://poe.ninja): price data.
- [Path of Exile Wiki](https://www.poewiki.net): the app does not contact it, but vault notes cite it. Its text is
  licensed CC BY-NC-SA 3.0 (https://www.poewiki.net/wiki/Path_of_Exile_Wiki:Copyrights); wiki-derived content keeps
  that license.
- Not affiliated with or endorsed by Grinding Gear Games. Path of Exile is a trademark of Grinding Gear Games.
