<!-- Reference part of ../target-design.md: Section 4. Key interfaces. -->

## 4. Key interfaces

Plain words: these eight are the places where one part of the program hands something to another. If they are small and
typed, the rest can change freely. Signatures are the intended shape, not final code; a few fields are marked unsettled.
Records are frozen dataclasses: nobody edits one in place, a changed copy is made with `dataclasses.replace`.

### 4.1 `PobSession` (`pob/session.py`): one PoB instance, the only door to Lua

```python
class Calculator(Protocol):              # what analysis needs from PoB; tests pass a fake that implements it
    def call(self, endpoint: Endpoint, payload: Mapping[str, Any] | None = None) -> Any: ...
    def load_build(self, xml_path: Path) -> BuildSummary: ...
    def scenario(self, config: Mapping[str, ConfigValue]) -> AbstractContextManager[None]: ...
    def left_out(self, skills: Sequence[str]) -> AbstractContextManager[list[str]]: ...   # yields names really disabled
    def discarding_changes(self) -> AbstractContextManager[None]: ...

class PobSession:                        # one Lua state; not thread-safe; owned by one worker at a time
    def __init__(self, pob_dir: Path, userdata_dir: Path, write_roots: Sequence[Path], lua_dir: Path = LUA_DIR) -> None
    def load_build(self, xml_path: Path) -> BuildSummary    # resets every piece of session state inside Lua
    def call(self, endpoint: Endpoint, payload: Mapping[str, Any] | None = None) -> Any
    def scenario(...); def left_out(...); def discarding_changes(...)     # context managers, see below
    def close(self) -> None
```

- `call` does not build Lua source. It looks up `Rpc.endpoints[name]` in the Lua state, pushes the request as one string
  with `lua_pushlstring`, runs `lua_pcall`, and reads the answer with `lua_tolstring` (the
  [Lua 5.1 C API](https://www.lua.org/manual/5.1/manual.html) that `lua51.dll` exports). There is no escaping, because
  nothing is pasted into code. An unknown name raises `UnknownEndpoint`; a Lua error becomes `PobError` carrying the first
  line and a reference to the traceback in the log. The typed result comes from `pob/wire.py` (`parse_context(raw)`).
- `Endpoint` (`pob/endpoints.py`) is a `StrEnum` of the 26 names plus an **effect** for each: `READ`, `TEMPORARY`
  (changes PoB and undoes it before returning), `SETUP` (changes calc setup until its paired restore), `PERSISTENT`
  (changes the loaded build; only valid inside `discarding_changes()`), `REPLACE` (`build.load`). `call` refuses a
  `PERSISTENT` endpoint outside that context manager, so the unwritten call order of today becomes a checked rule.
- The fixed order, now written in code: `load_build` -> `left_out` -> `scenario` (twice: the scenario's config, then the
  source-gated config) -> `call(...)`. `discarding_changes()` runs a persistent what-if; on exit it reloads the same
  file and replays the recorded `left_out` and `scenario` steps. Today that is `restore_player()` plus `load_audit_hooks()`.
- `os.chdir(pob_dir)` still happens once per process (PoB loads its modules relative to its folder), so every path we
  pass is absolute (`Settings` enforces it) and the Python write guard stays. Moving each engine into its own OS process
  is an option for later; with `PobSession` in place it changes one module (an ADR, not part of this plan).

### 4.2 `BuildSession` (`analysis/session.py`): a build calculated under a scenario

```python
@dataclass(frozen=True)
class SessionSetup:
    scenario: str | None = "Pinnacle Boss"   # None = the build exactly as its author saved it (used for target builds)
    left_out: tuple[str, ...] = ()
    include_drafts: bool = False             # do unverified (draft) notes change the numbers?

class BuildSession:                                  # use as `with BuildSession.open(...) as session:`; leaving the block undoes the setup
    @classmethod
    def open(cls, calc: Calculator, build_path: Path, setup: SessionSetup, notes: MechanicsNotes) -> "BuildSession"
        # loads the file, hashes it, applies the setup in the fixed order, evaluates once. No network, no league data.
    build_path: Path;  source_sha256: str;  summary: BuildSummary;  setup: SessionSetup
    def evaluate(self, *, remove_nodes: Sequence[int] = (), add_nodes: Sequence[int] = (), parts: bool = False) -> CalcContext
    def base_context(self) -> CalcContext             # the build as set up; cached
    def vector(self, ctx: CalcContext | None = None) -> MetricVector
    def key_numbers(self) -> KeyNumbers               # tiles, reservations, DPS steps, sources (analysis/report.py)
    def findings(self) -> list[Finding]               # rule, sustainability and config checks
    def without_models(self) -> "BuildSession"        # a view with Model notes named but not applied (compare needs it)
    def is_stale(self) -> bool                        # has the file changed on disk since it was opened?
    @property
    def calc(self) -> Calculator                      # for modules that call further endpoints
```

It replaces `Auditor` (audit problem 3). What changes: no league download in the constructor (league data is passed to
`compare`, and is `None` when offline, which the availability code already treats as "unknown"); no suggestion search;
no attribute swapping from outside (`models_not_applied` becomes `without_models()`); no `suggestions` or
`source_sha256` overwritten by the server. A comparison opens **two** sessions: yours with the scenario, and the target
with `scenario=None`, each on its own pooled engine.

`MechanicsNotes` (returned by `mechanics.load_notes`) is a frozen bundle of `rules`, `models`, `scenarios`, `gap_patterns`,
`overrides` and `statuses`; draft notes are filtered out by `include_drafts` when the session opens.

### 4.3 `Finding` (`analysis/findings.py`): what a check returns

```python
class Severity(StrEnum): NOTE = "note"; WARNING = "warning"; PROBLEM = "problem"

@dataclass(frozen=True)
class Source:                                # where a number or a claim comes from
    kind: Literal["pob", "mechanics", "config"]
    ref: str                                 # PoB output key, mechanics note name, or PoB config variable

@dataclass(frozen=True)
class Finding:
    check: str                               # stable id, e.g. "sustain.mana", "rule.reservation_fits", "config.channelling_time"
    subject: str                             # what it is about: a skill, a slot, a resource
    stat: str                                # the PoB output key or note key that was checked
    actual: float | None
    limit: float | None
    gap: float | None                        # distance to passing, in the stat's own unit; None when unknown
    severity: Severity
    sources: tuple[Source, ...]
    worsened: bool = False                   # an already-broken rule made worse (replaces the WORSE_MARK text)
```

It replaces `"[Rule name] message"` strings, `rule_name()` and the `WORSE_MARK` text search. `app/present/report.py` is the one
place that writes the sentence (for example "Total mana cost 12.3/s is above your regeneration 10.1/s"); the browser sorts, groups and
filters on the fields, and the later chat box explains from them.

### 4.4 `MetricVector` (`analysis/metrics.py`): the one way to hold and compare numbers

```python
class Unit(StrEnum): PERCENT = "percent"; PER_SECOND = "per_second"; COUNT = "count"; MULTIPLIER = "multiplier"

@dataclass(frozen=True)
class Part:                                  # one modifier PoB applied in this build: where it comes from, what it adds
    source: str                              # "Tree: <node>", "Item: <name>", "Gem: <name>" (as in the 2026-10-26 prototype)
    value: float
    condition: str = ""                      # PoB's own tags, e.g. "Condition:AffectedByArcaneSurge"

@dataclass(frozen=True)
class Metric:
    key: str                                 # catalogue id: "dps", "ehp", "phys_max_hit", "mana_margin", "inc_damage_cold", ...
    value: float | None                      # None = PoB gave no number (infinity and NaN arrive as null)
    unit: Unit
    parts: tuple[Part, ...] = ()             # scaling vectors only: the modifiers that add up to `value`

@dataclass(frozen=True)
class MetricVector:
    metrics: Mapping[str, Metric]
    def get(self, key: str) -> float | None
    def delta(self, before: "MetricVector") -> "VectorDelta"      # self is the "after"

@dataclass(frozen=True)
class MetricChange:                          # one metric, before to after
    key: str; before: float | None; after: float | None
    absolute: float | None; percent: float | None                 # percent is None when before is 0 or None
    direction: Literal["up", "down", "flat"]                      # "flat" below thresholds.ZERO_PCT
VectorDelta = Mapping[str, MetricChange]
```

Words: a *scaling vector* (as in `mechanics/Glossary.md`) is one category such as "increased" or "crit multiplier"; a
`MetricVector` is the whole set of measured values of one build, one entry per outcome and per scaling vector.

It replaces the two metric models of today: the audit's `dims` (`dps`, `ehp`, `physMaxHit`, `manaFrom`, `manaTo`, ...)
and the guide check's `base` / `after` / `delta` (`dpsPct`, `ehpPct`, `manaMargin`, `maxHit`). The thresholds live in
`analysis/thresholds.py` and travel to the browser in `GET /api/meta`, so the 0.1 % rule exists once. The catalogue in
`analysis/vectors.py` lists the outcomes (DPS, EHP, max hit, margins) and the scaling vectors; the browser gets labels
and units from `GET /api/meta` instead of repeating them.

Where the scaling-vector data comes from: the hand-made comparison of 2026-10-26 (Worb against `pobb.in/v8XfQn1yFnAs`)
already read it from PoB. Its Lua script, `scaling.lua` (95 lines, kept in the working session's scratch folder, not in the repo),
reads `build.calcsTab.mainEnv` and calls PoB's own `ModStore:Tabulate` for the main skill: per damage type the base
min/max and hit average, then increased, more, penetration, the enemy's taken-increased and taken-more, and the enemy's
resistance; plus speed, crit chance and crit multiplier. Every row is `{value, stat, source, cond}`. That script becomes
`pob/lua/analysis/vectors.lua` and its shape is the response of the `analysis.vectors` endpoint (4.8). In the prototype
Worb has 72 rows of increased damage that apply to its Cold hits and the target 43; the comparison then grouped them by source. Splitting
"base damage" into the skill's own base, added flat damage and conversion / gain-as (owner, round 3) needs more than
that script reads, so those three vectors are unsettled (Appendix A).

### 4.5 `Settings` (`app/settings.py`): every folder, port and limit, resolved once

```python
@dataclass(frozen=True)
class Settings:
    host: str;  port: int                  # 127.0.0.1 and 8765; the server never binds elsewhere
    pob_dir: Path                          # env POB_DIR, else PoB's default install folder; must hold Launch.lua
    builds_dir: Path                       # env AUTOBUILDER_BUILDS_DIR, else PoB's Builds folder under Documents
    imports_dir: Path                      # where imported target builds are saved (open question 7)
    data_dir: Path                         # <project>/userdata: api-token, build_settings.json, logs/, cache/, pob/engine-N/
    mechanics_dir: Path;  web_dir: Path    # <project>/mechanics and <project>/web
    engine_pool_size: int                  # 2: your build and the target
    job_keep: int;  job_run_limit_s: int   # 20 finished jobs kept; a running job older than 900 s is given up (as today)
    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> "Settings"   # the only code that reads os.environ
    def validate(self) -> None             # absolute paths, PoB present, Builds folder exists; one friendly message each
```

- Documents is looked up with the Windows Known Folder API (`SHGetKnownFolderPath`, through `ctypes`; see
  [Microsoft's reference](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)),
  so a Documents folder moved by OneDrive is found; the README says it is not detected today. The project folder is found
  by walking up to `pyproject.toml`; `AUTOBUILDER_HOME` overrides.
- It replaces the path constants in `pobhost.py`, `server.py`, `vault.py`, `build_settings.py`, `obtainability.py`,
  `optimize.py`, `runlog.py` and `engine_pool.py`, and the third copy in `tests/golden_common.py`.

### 4.6 `AppState` (`app/state.py`): what every handler receives

```python
@dataclass
class AppState:                            # built once in app/main.py; nothing else holds global state
    settings: Settings
    api_token: str                         # per run; also written to data_dir/api-token as today
    pool: EnginePool                       # leases PobSession objects
    jobs: JobStore
    capability: Capability                 # the start-up probe: (available, pob_version, reason) for the comparison
    clock: Callable[[], float] = time.monotonic
```

`AppServer`, a small subclass of `ThreadingHTTPServer`, carries the state; handlers read `self.server.state`. Tests build a
state from fakes (`tests/helpers/fakes.make_state()`), so `mock.patch.object(server, "API_TOKEN", ...)` and the
`SimpleNamespace` stand-ins in `test_server_errors.py` and `test_guide_gate2.py` disappear. Concurrency model, written
down for the first time: **one job runs at a time** (the job store's rule), and a job leases up to two sessions (yours and
the target). The global `engine_lock` of today becomes that rule (unsettled, Appendix A2).

### 4.7 The job store (`app/jobs.py`)

```python
class JobStatus(StrEnum): RUNNING = "running"; DONE = "done"; ERROR = "error"

@dataclass(frozen=True)
class JobError:  kind: str; message: str; reference_id: str | None     # kind is the stable id the browser switches on

@dataclass(frozen=True)
class Job:
    id: str;  kind: JobKind;  build: str;  status: JobStatus
    stage: Stage;  stages: tuple[Stage, ...];  done: int | None;  total: int | None     # progress, no label strings
    error: JobError | None;  report: dict | None                       # report = the JSON the browser renders
    started_at: float;  finished_at: float | None

class JobStore:                            # thread-safe; Job objects are replaced, never edited
    def __init__(self, *, keep: int = 20, run_limit_s: float = 900.0, clock: Callable[[], float] = time.monotonic)
    def start(self, kind: JobKind, build: str) -> tuple[Job, bool]      # (job, created); a second start returns the running job
    def get(self, job_id: str) -> Job | None
    def reporter(self, job_id: str) -> ProgressReporter                 # callable(stage, done=None, total=None)
    def finish(self, job_id: str, report: dict) -> None
    def fail(self, job_id: str, error: JobError) -> None
    def sweep(self) -> None                # drop the oldest finished jobs beyond `keep`; give up stuck running jobs
```

In `api.js`, "cancel" means "stop waiting": it does not stop PoB, and the job ends at its own time limit.

Fixes: the job dict that never forgets (audit problem 10); the two `StaleAudit` classes; the progress label that was the
API contract (`label != "Testing differences"`); two pollers; the stuck-job rule that lives only in `guide_routes.py` now
applies to every job. `Stage` (in `progress.py`) is `QUEUED, FETCHING, LOADING, MEASURING, TESTING, RANKING, CHECKING,
DONE` (the list may change); `GET /api/meta` sends the browser each stage's id and its text, so the words live in Python only.

### 4.8 The Lua endpoint registry (`pob/lua/rpc.lua`, `pob/endpoints.py`)

Plain words: every function Python may call inside PoB is listed once, in one table, with a note on what it changes.
Today there are 36 global `*JSON` functions in 9 files, glued by `dofile` chains, one of them (`evaluateJSON`) silently
replaced by a second definition in another file. The registry replaces that with 26 named endpoints (22 survive the
freeze, 4 are new or split out).

A Lua file registers an endpoint; the handler keeps today's contract (request JSON text in, JSON text out), so most
function bodies move unchanged:

```lua
-- pob/lua/analysis/state.lua
Rpc.register("analysis.disable_skills", "setup", function(requestText)    -- name, effect, handler
    local names = dkjson.decode(requestText).names or {}
    ...                                                                    -- body unchanged from disableSkillsJSON
    return dkjson.encode(disabled)
end)
```

`Rpc.register` refuses a name that is already taken. `loader.lua` loads the files in one fixed order. Python names the
endpoint with `Endpoint.ANALYSIS_DISABLE_SKILLS`. `docs/ARCHITECTURE.md` carries this same table, and
`tests/pob/test_rpc_registry_matches_docs.py` fails when Lua, `Endpoint` and the table disagree.

Effects: **read** changes nothing; **temporary** changes PoB and undoes it before returning, also on error; **setup**
changes the calculation setup until its paired restore runs (never saved into the build file); **persistent** changes the
loaded build and is only allowed inside `discarding_changes()`; **replace** swaps the whole build.

| Name (today's function) | Effect | Request | Response | State it touches |
|---|---|---|---|---|
| `build.load` (`loadBuildFromFile` + `summaryJSON`) | replace | `{path}` | `BuildSummary {pobVersion, buildName, className, ascendancy, level, mainSkill, stats}` (16 stat keys) | replaces the loaded build; clears the calc cache, remembered config, left-out gems and the loaded target |
| `analysis.evaluate` (`evaluateJSON`) | read | `{removeNodes[], addNodes[], stats[], extraSkills[{group,index}], fast?, partVariants?}` | `CalcContext {skills[], supports[], keystones[], skillDPS[], usedTogether[], byPart?}` | none (node what-ifs are a calc override); resets the calc cache |
| `analysis.set_config` (`setConfigJSON`) | setup | `{config{var: value}}` | previous values `{var: {value}}` | config tab inputs, calc only; remembers the originals |
| `analysis.restore_config` (`restoreConfig`, now an endpoint) | setup | none | `{}` | puts the remembered config back |
| `analysis.disable_skills` (`disableSkillsJSON`) | setup | `{names[]}` | names really disabled | `gem.enabled = false`; remembers the gems |
| `analysis.restore_skills` (`restoreSkills`, now an endpoint) | setup | none | `{}` | re-enables the remembered gems |
| `analysis.capability_keys` (`capabilityKeysJSON`) | read | none | `string[]` | none |
| `analysis.equipped_titles` (`equippedTitlesJSON`) | read | none | `string[]` | none |
| `analysis.reservations` (`reservationsJSON`) | read | none | `{skills[{name,pool,amount,percent}], mana, manaUnreserved, life, lifeUnreserved}` | none |
| `analysis.other_skills` (`otherSkillsJSON`) | temporary | `{stats[]}` | `rows[{group,index,name,label,includeInFullDPS,out,triggered,reactive,reactiveBy}]` | switches the main skill per row, restores it |
| `analysis.consecrated_sources` (`consecratedSourcesJSON`) | read | none | `{lines[{kind,name,line}]}` | none |
| `analysis.gear_mods` (`auditWastedModsJSON`) | temporary | none | one row per mod line `{slot,item,line,kind,rarity,crafted,unsupported,changed,otherSkills,conditions,sample}` | evaluates temporary item copies; kept only if open question 1 says yes |
| `analysis.why` (`whyJSON`) | read | `{removeIds[], addIds[]}` | `[{type,stat,source,from,to}]` | two temporary calc environments |
| `analysis.gem_stat_diff` (`gemStatDiffJSON`) | read | `{name, from{level,quality}, to{level,quality}}` | `[{stat,from,to,fromText,toText}]` | none |
| `analysis.vectors` (new) | read | `{}` (main skill) | `{skill, stats, types{Cold: {minBase,maxBase,hitAverage,critAverage,inc[],more[],pen[],takenInc[],takenMore[],resist[]}}, speedInc[], speedMore[], critBase[], critInc[], critMore[], critMulti[]}`, rows `{value,stat,source,cond}` | none; reads `mainEnv` with `Tabulate` (shape from the 2026-10-26 prototype; the base-damage split is unsettled) |
| `compare.probe` (`probeJSON`) | temporary | none | `{compareTab, comparePowerBuilder, compareEntry, pobVersion, fields[], tinyRows}` | builds a tiny temporary compare entry; restores |
| `compare.load_target` (`guideLoadJSON`) | setup | `{xmlPath, label}` | `{ok, treeVersion, ascendancy}` or `{ok: false, error}` | holds the target build inside PoB (about 195 MB) until released |
| `compare.release_target` (`guideReleaseJSON`) | setup | none | `"ok"` | drops the target and forces garbage collection |
| `compare.snapshot` (`snapshotJSON`) | read | `{which: "own" \| "target"}` | `Snapshot v1 {groups, items, nodes, config, sets, points, handedness, ...}` | none |
| `compare.tree_info` (`treeInfoJSON`) | read | `{ids[], removeIds[]}` | `{nodes{id: {name,type,path?,depends?,pathDist}}}` | none |
| `compare.target_power` (`guidePowerJSON`) | temporary | `{categories?[]}` | `[{category,name,nodeId,slotName,impact,impactPercent,pathDist,perPoint}]` | temporarily swaps the compare tab's primary build; restores; resets the calc cache |
| `compare.evaluate_change` (the `evaluateJSON` override in `guide.lua`, now its own endpoint) | temporary | `analysis.evaluate` request plus `{repItem?, gemChange?}` | `CalcContext` | applies a temporary item or gem change, then undoes it |
| `compare.apply_changes` (`applyChangesJSON`, `save: false` only) | persistent | `{changes[], stats[], extraSkills[]}` | `{ctx}` | changes the loaded build in place; only inside `discarding_changes()` |
| `compare.swap_config` (`guideConfigSwapJSON`) | setup | `{values{}, clear[]}` | previous `{values, clear[]}` | config inputs; the caller swaps back with the returned values |
| `compare.mod_needs` (`modNeedsJSON`) | read | `{lines[]}` | `[{text, conditions[{var,on,skill}], flags[]}]` | a temporary calc environment |
| `compare.curse_state` (`curseStateJSON`) | read | `{gemIds[]}` | `{limit, slots[], curse{}, mark{}, limitBypass}` | a temporary calc environment |

Not in the table: the 14 frozen endpoints (section 2), and `loadBuildFromFile` (merged into `build.load`). Two traps this
design removes: `evaluateJSON` no longer exists twice (reading `audit.lua` gave the wrong picture of what ran), and
`applyChangesJSON` can no longer be called by accident outside a context that reloads the build afterwards.

### 4.9 Four conventions the interfaces rely on

- **Errors.** `errors.py` holds domain errors with no HTTP in them. `app/errors.py` holds one explicit table from error class to
  status and a stable `kind` that the browser switches on. A `ValueError` or `KeyError` that escapes from domain code is a bug:
  it becomes a 500 with a reference id (today `classify` turns any `ValueError` into a 400, which can show a bug as "invalid request").

| Error | Status | `kind` sent to the browser |
|---|---:|---|
| `InvalidInput`, `BadLink`, `Unreadable`, `TooLarge`, `TargetUnreadable` | 400 | its own class name; the page shows the message next to the link field |
| `Unauthorized`, `Forbidden` (HTTP layer only) | 401, 403 | same |
| `StaleBuild` | 409 | `StaleBuild` (was `StaleAudit`) |
| `Unavailable` (PoB too old for the comparison) | 503 | `Unavailable` |
| `FetchFailed` (pobb.in or league data unreachable) | 502 | `FetchFailed` |
| `PobError` (a Lua failure) | 500 | `EngineError`, message limited to the first Lua line |
| anything else | 500 | `EngineError`, "internal error (ClassName)", reference id in the log |

- **Logging.** Domain code uses `logging.getLogger(__name__)`. `app/logging_setup.py` attaches the JSON-lines handler (with its
  redaction) to the `autobuilder` logger, and the job id and build name reach every record through a `contextvars` value set
  by `app/runner.py`, so domain functions never pass them around. Today there are two logging paths and five calls that
  never reach the file (audit problem 10).
- **Wire format.** JSON keys stay camelCase as today. `app/present/report.py` maps records to JSON by hand (no automatic
  converter, so every shape is visible and tested). Missing and infinite numbers are `null`. The page reads responses only
  through `lib/safe.js`.
- **Limits and writes.** Request bodies are capped at 64 KB, and at 300 KB for a request that carries a pasted PoB code (the
  code itself is limited to 256 KB, the inflated XML to 4 MB, as in the importer today). The app writes only under
  `userdata/` and the imports folder (open question 7); PoB itself still writes its timeless-jewel cache in its own
  folder, as the README says.

