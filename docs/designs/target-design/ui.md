<!-- Reference part of ../target-design.md: Section 6. The UI module tree. -->

## 6. The UI module tree and where the analyzer view slots in

Plain words: the browser still loads plain files, with no build step. [ES modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
let each file import what it needs. `index.html` becomes an empty shell. One file talks to the server, one file rounds
numbers, and each view draws one part of the screen. The analyzer, your scaling vectors side by side, is a folder of its
own, so it can grow without touching the rest.

```
web/
  index.html                  shell: sidebar, main area, one <script type="module" src="/js/main.js">, the API token
  css/       tokens.css  base.css  analyzer.css  progress.css
  fonts/     Cinzel and IBM Plex Sans, 5 woff2 files served by the app itself
  js/
    main.js                   start-up; the one place that decides which view is shown
    api.js                    every fetch call; startAnalysis(); pollJob() with retry, errors and cancel
    store.js                  a tiny state store (get, set, subscribe); no DOM nodes in state
    lib/
      dom.js                  $ and h(): elements are built with textContent only
      format.js               the one number-formatter family (same rounding as Python)
      safe.js                 arr / obj / str / fin: safe reads of untrusted data
    views/
      sidebar.js              build list, search, scenario, left-out skills
      start.js                choose your build, paste a target link or code, press Analyze
      progress.js             stage list and progress bar
      analyzer/
        index.js              composes the result from the parts below
        header.js             build name, scenario, league, banners
        tiles.js              the key-number tiles with the PoB values underneath (they stay, decision of round 2)
        reservation.js        which reserving skills do you run
        vectors.js            NEW: the scaling vectors side by side
        drilldown.js          the differences under one vector (replaces the separate ranked list)
        checks.js             config, sustainability and rule findings
```

Where the new analyzer slots in. `vectors.js` is a table. Rows are the vectors from the catalogue in `analysis/vectors.py`
(base damage split into the skill's own base, added flat and conversion or gain-as; increased; more; crit chance and
multiplier; penetration; enemy modifiers; speed; projectiles; later the defence vectors, which reuse the same component
with another catalogue group). Columns are yours, the target's, the gap, and later the value of the next step. Opening a
row calls `drilldown.js` for that vector: one line per difference worth 3 % of DPS or more, largest first, then one
collapsed group for everything smaller with its combined total. A difference that moves several vectors is shown under the
one it moves most (unsettled, Appendix A). With no target pasted, the same screen shows only your side: tiles, vectors
and checks. `alternatives.js` and a chat view are the two later slots.

Rules that keep it small:

- Imports go downward: `main.js` -> `views/*` -> `lib/*`. `lib` imports nothing. A view never calls `fetch` (only `api.js`
  does) and never touches another view's DOM. `tests/web/test_ui_modules.py` checks that every import resolves.
- No global state objects. Today's `state` (6 fields) and `G` (23 fields, several holding DOM nodes) and the way the two
  apps switch each other off by writing into each other's state are replaced by one store per view and one `view` value
  owned by `main.js`.
- Safety is kept and extended: text only through `h()` and `textContent`; no HTML sinks; no inline `<script>` or `style`
  attribute. `h()` sets styles through the element's `style` object, which a strict policy allows.
  `tests/web/test_ui_safety.py` now scans every `web/js/**/*.js` instead of slicing `index.html` between two text markers.
- The server sends a strict [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP):
  `default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; connect-src 'self';
  base-uri 'none'; form-action 'none'; frame-ancestors 'none'`. Today it can only send `frame-ancestors`, because the page
  is one inline script. The two Google Fonts hosts, and the privacy note about them, go away. (Whether the browser accepts
  every style path under `style-src 'self'` is verified by hand in step 19.)
- One formatter family. The two near-identical families of today (`fmtNum`, `fmtBig`, `fmtPct`, `fmtMargin` and
  `gPct`, `gBig`, `gMargin`, `gPlain`) become one; the zero cut-offs come from `/api/meta`, not from constants in the page.
  The Python and JS rounding rules are one rule, proved by the shared `tests/fixtures/format_cases.json`.
- The old audit report and the guide check disappear as separate screens: their key-number tiles, reservation panel and
  difference rows are reused inside `views/analyzer/`. Roughly 300 lines of suggestion and apply code are gone with the freeze.

