"""Do the two main skills have the same settings? (decision 011; card 110). Before the chain is shown.

A setup is one active skill as a group runs it: part, stages, mines, minion, minion skill, count, group count. Some
builds carry the main skill twice, one group per part (Lightning Strike melee and projectile), so each build's setups
of the main skill are compared as a set; pairing groups one by one could pair the wrong two (the first app's
guide_diff_gems.py:55-67). Rewrites guide_diff_gems.py :1-87, 110-134, 196-231.
"""

from dataclasses import dataclass
from enum import StrEnum

from comparison_app.compare.snapshot import ActiveSkill, Group, Snapshot

SETTINGS = ("part", "stages", "mines", "minion", "minion_skill", "count", "group_count")


class Match(StrEnum):
    SAME = "same"  # the main skills are set up alike: the chain is shown
    OTHER_GROUP = "other_group"  # the target runs your setup in another group: pick that group
    SETTINGS_DIFFER = "settings_differ"  # the chain is hidden until the settings match (decision 011)
    DIFFERENT_SKILL = "different_skill"  # the target's main skill is another skill: pick a group of the target's


@dataclass(frozen=True)
class Setup:
    group: int
    skill_index: int  # 1-based among the group's active skills, as PoB's mainActiveSkill counts them
    skill: str
    part: str | None
    stages: float | None  # as PoB applies it: unset is the maximum, more is cut to it (CalcActiveSkill.lua:649-651)
    mines: float | None
    minion: str | None
    minion_skill: float | None
    count: float | None
    group_count: float | None

    def settings(self) -> tuple[object, ...]:
        return tuple(getattr(self, name) for name in SETTINGS)


@dataclass(frozen=True)
class SkillSettings:
    match: Match
    yours: Setup | None
    target: Setup | None
    differing: tuple[str, ...]  # the settings that differ between the two main setups (names from SETTINGS)
    # (group, active skill) of the target the owner can pick (OTHER_GROUP, DIFFERENT_SKILL): a group can hold several
    # active skills (CoC EK Assa's group 1: Ethereal Knives and Cyclone), so the group alone does not name one
    target_choices: tuple[tuple[int, int], ...]
    message: str


def _setup(group: Group, index: int, skill: ActiveSkill) -> Setup:
    gem = group.gems[skill.gem - 1] if skill.gem and skill.gem <= len(group.gems) else None
    stages = gem.stages if gem and gem.stages is not None else skill.stages_max
    if stages is not None and skill.stages_max is not None:
        stages = min(stages, skill.stages_max)  # PoB applies at most the maximum (CalcActiveSkill.lua:651)
    return Setup(
        group.index,
        index,
        skill.name,
        skill.part,
        stages,
        gem.mines if gem else None,
        gem.minion if gem else None,
        gem.minion_skill if gem else None,
        gem.count if gem else None,
        group.group_count,
    )


def _main(snapshot: Snapshot) -> Setup | None:
    skill = snapshot.main_skill()
    if skill is None:
        return None
    group = snapshot.groups[snapshot.main_group - 1]
    return _setup(group, group.main_active_skill, skill)


def _setups(snapshot: Snapshot, name: str) -> list[Setup]:
    """Every setup of the skill in an enabled group."""
    return [
        _setup(group, index, skill)
        for group in snapshot.groups
        if group.enabled
        for index, skill in enumerate(group.skills, start=1)
        if skill.name == name
    ]


def _places(setups: list[Setup]) -> str:
    return ", ".join(f"group {setup.group} (skill {setup.skill_index})" for setup in setups)


def compare_settings(yours: Snapshot, target: Snapshot) -> SkillSettings:
    mine, theirs = _main(yours), _main(target)
    if mine is None or theirs is None:
        return SkillSettings(Match.DIFFERENT_SKILL, mine, theirs, (), (), "One of the builds has no main skill.")
    if mine.skill != theirs.skill:
        found = _setups(target, mine.skill)
        where = f" It has {mine.skill} in {_places(found)}." if found else ""
        message = f"The target's main skill is {theirs.skill}, yours is {mine.skill}.{where} Pick the target's skill."
        choices = tuple((setup.group, setup.skill_index) for setup in found)
        return SkillSettings(Match.DIFFERENT_SKILL, mine, theirs, (), choices, message)
    differing = tuple(name for name in SETTINGS if getattr(mine, name) != getattr(theirs, name))
    if not differing:
        return SkillSettings(Match.SAME, mine, theirs, (), (), "")
    same = [setup for setup in _setups(target, mine.skill) if setup.settings() == mine.settings()]
    if same:
        message = f"The target runs your {mine.skill} setup in {_places(same[:1])}, not as its main skill. Pick it."
        choices = tuple((setup.group, setup.skill_index) for setup in same)
        return SkillSettings(Match.OTHER_GROUP, mine, theirs, differing, choices, message)
    message = (
        f"{mine.skill} is set up differently ({', '.join(differing)}), so the chain would compare different things. "
        "Recalculate your build with the target's setting to see it."
    )
    return SkillSettings(Match.SETTINGS_DIFFER, mine, theirs, differing, (), message)
