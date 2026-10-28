"""The config differences between your build and the target (decision 010; card 110), in PoB's own list order.

Rewrites the first app's guide_diff.py :1-24, 36-148, which worked defaults out by hand: here a box counts as set
when PoB says it is not at its default (GetDefaultState, ConfigTab.lua:941-948; pob/lua/compare/snapshot.lua), and a
box one build leaves unset is at PoB's default there. Placeholders are not compared: PoB derives them from the boss
box and other boxes, which are compared themselves. Not sorted by effect in milestone 1 (decision 019).
"""

from dataclasses import dataclass

from autobuilder.compare.snapshot import ConfigBox, CustomMods, Snapshot

SCENARIO_BOX = "enemyIsBoss"  # set for both builds by the scenario (decision 010; ConfigOptions.lua:2086)
SCENARIO_NOTE = "set by scenario"
SET_STATES = ("set", "unusable")


@dataclass(frozen=True)
class ConfigDifference:
    var: str
    section: str | None
    label: str
    yours: ConfigBox | None  # None: at PoB's default in your build
    target: ConfigBox | None
    note: str | None  # where it cannot change a build's numbers, or that the scenario sets it


@dataclass(frozen=True)
class LooksWrong:
    whose: str  # "yours" or "target"
    box: ConfigBox
    message: str


@dataclass(frozen=True)
class ConfigReport:
    differences: tuple[ConfigDifference, ...]  # PoB's list order; the scenario box first, as set by the scenario
    looks_wrong: tuple[LooksWrong, ...]  # settings that look wrong even when both builds agree (decision 010)
    custom_mods_yours: tuple[CustomMods, ...]  # Custom Modifiers blocks only your build has
    custom_mods_target: tuple[CustomMods, ...]
    config_sets: tuple[str, str] | None  # (your active set, the target's) when either build has several


def _set(snapshot: Snapshot) -> dict[str, ConfigBox]:
    return {box.var: box for box in snapshot.boxes if box.state in SET_STATES}


def _note(yours: ConfigBox | None, target: ConfigBox | None) -> str | None:
    cannot = [whose for whose, box in (("your", yours), ("the target's", target)) if box and box.state == "unusable"]
    if not cannot:
        return None
    return " and ".join(cannot) + " build cannot use it (PoB shows it in red), so there it changes no number"


def _differences(yours: Snapshot, target: Snapshot) -> tuple[ConfigDifference, ...]:
    mine, theirs = _set(yours), _set(target)
    found = []
    for var in mine.keys() | theirs.keys():
        box_yours, box_target = mine.get(var), theirs.get(var)
        if var != SCENARIO_BOX and (box_yours and box_yours.value) == (box_target and box_target.value):
            continue
        shown = box_yours or theirs[var]  # the var comes from one of the two
        note = SCENARIO_NOTE if var == SCENARIO_BOX else _note(box_yours, box_target)
        found.append(ConfigDifference(var, shown.section, shown.label, box_yours, box_target, note))
    first = [each for each in found if each.var == SCENARIO_BOX]
    rest = sorted((each for each in found if each.var != SCENARIO_BOX), key=_order)
    return (*first, *rest)


def _order(difference: ConfigDifference) -> int:
    box = difference.yours or difference.target
    return box.order if box else 0


def _looks_wrong(whose: str, snapshot: Snapshot) -> list[LooksWrong]:
    return [
        LooksWrong(whose, box, f"{box.label} is 0, but the build has modifiers that need it (PoB shows the box for it)")
        for box in snapshot.boxes
        if box.state == "unset"
    ]


def _custom(snapshot: Snapshot) -> set[CustomMods]:
    return {block for block in snapshot.custom_mods if block.enabled}


def compare_config(yours: Snapshot, target: Snapshot) -> ConfigReport:
    mine, theirs = _custom(yours), _custom(target)
    several = len(yours.config_sets) > 1 or len(target.config_sets) > 1
    return ConfigReport(
        _differences(yours, target),
        (*_looks_wrong("yours", yours), *_looks_wrong("target", target)),
        tuple(block for block in yours.custom_mods if block in mine - theirs),
        tuple(block for block in target.custom_mods if block in theirs - mine),
        (yours.active_config_set, target.active_config_set) if several else None,
    )
