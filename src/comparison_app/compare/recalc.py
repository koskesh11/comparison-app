"""Decision 011's button: your build recalculated in memory with the target's skill setting; your file never changes
(card 111; the Lua side is pob/lua/compare/changes.lua).

Every change kind is checked against a real change (M7, tests/comparison_app/compare/test_recalc_matches_apply.py):
the same setting edited into a copy of the build and loaded gives the same chain and output. A kind no reference build
can check is marked "not tested" with the reason, so the page can say so.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from comparison_app.analysis.chain import Chain, Which, parse_chain
from comparison_app.analysis.scenarios import BOSS_BOX, Scenario
from comparison_app.compare.skill_settings import Match, SkillSettings
from comparison_app.compare.snapshot import Gem, Snapshot
from comparison_app.pob import wire
from comparison_app.pob.endpoints import ChangeKind, Endpoint
from comparison_app.pob.session import PobSession

NOT_TESTED: Mapping[ChangeKind, str] = {
    ChangeKind.MINE_COUNT: "not checked against a saved build: no reference build has a mine skill",
    ChangeKind.MINION: "not checked against a saved build: no reference build has a skill with two minion types",
}
# skill_settings.SETTINGS -> the change that sets it, and where its value is on the target's main gem or group
SETTING_KINDS: Mapping[str, ChangeKind] = {
    "part": ChangeKind.SKILL_PART,
    "stages": ChangeKind.STAGE_COUNT,
    "mines": ChangeKind.MINE_COUNT,
    "minion": ChangeKind.MINION,
    "minion_skill": ChangeKind.MINION_SKILL,
    "count": ChangeKind.GEM_COUNT,
    "group_count": ChangeKind.GROUP_COUNT,
}
GEM_VALUES: Mapping[ChangeKind, str] = {
    ChangeKind.SKILL_PART: "part",  # the part's index, as PoB saves it
    ChangeKind.STAGE_COUNT: "stages",
    ChangeKind.MINE_COUNT: "mines",
    ChangeKind.MINION: "minion",
    ChangeKind.MINION_SKILL: "minion_skill",
    ChangeKind.GEM_COUNT: "count",
}


@dataclass(frozen=True)
class Change:
    kind: ChangeKind
    group: int  # 1-based socket group; not used by MAIN_GROUP
    gem: int | None  # 1-based gem in the group, for the gem kinds
    value: float | str | None  # None unsets the field, as an empty box in PoB


@dataclass(frozen=True)
class Recalculated:
    chain: Chain
    output: Mapping[str, float]  # every number of the sidebar's output after the changes (FullDPS, ...)
    not_tested: tuple[str, ...]  # why a change could not be checked against a saved build (NOT_TESTED)


def _main_gem(snapshot: Snapshot) -> tuple[int, int, Gem] | None:
    skill = snapshot.main_skill()
    group = snapshot.groups[snapshot.main_group - 1] if skill else None
    if skill is None or group is None or not skill.gem:
        return None
    return group.index, skill.gem, group.gems[skill.gem - 1]


def changes_to_match(settings: SkillSettings, yours: Snapshot, target: Snapshot) -> tuple[Change, ...]:
    """Your main skill's differing settings set to the target's, for SETTINGS_DIFFER (decision 011's button)."""
    mine, theirs = _main_gem(yours), _main_gem(target)
    if settings.match is not Match.SETTINGS_DIFFER or mine is None or theirs is None:
        return ()
    group, gem, _ = mine
    target_group = target.groups[theirs[0] - 1]
    changes = []
    for setting in settings.differing:
        kind = SETTING_KINDS[setting]
        value = getattr(theirs[2], GEM_VALUES[kind]) if kind in GEM_VALUES else target_group.group_count
        changes.append(Change(kind, group, gem if kind in GEM_VALUES else None, value))
    return tuple(changes)


def _wire(change: Change) -> dict[str, object]:
    item: dict[str, object] = {"kind": change.kind.value, "group": change.group}
    if change.gem is not None:
        item["gem"] = change.gem
    if change.value is not None:
        item["value"] = change.value
    return item


def recalculate(
    session: PobSession, scenario: Scenario, changes: Sequence[Change], which: Which = "own"
) -> Recalculated:
    """The chain and output with the changes in memory; the build is as it was afterwards (M6)."""
    request = {"boss": BOSS_BOX[scenario], "which": which, "changes": [_wire(change) for change in changes]}
    reply = wire.table(session.call(Endpoint.COMPARE_CHAIN_WITH, request))
    output = {key: wire.number(value) for key, value in wire.table(reply.get("output")).items()}
    reasons = dict.fromkeys(NOT_TESTED[change.kind] for change in changes if change.kind in NOT_TESTED)
    return Recalculated(
        parse_chain(reply.get("chain")), {k: v for k, v in output.items() if v is not None}, tuple(reasons)
    )
