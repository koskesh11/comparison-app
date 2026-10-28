"""The skill settings and config of the build or the target as PoB has them (compare.snapshot; card 110).

Typed from pob/lua/compare/snapshot.lua. A setting PoB has not set is None, never a guessed default: PoB leaves
skillPart unset on a gem whose skill has one part (SkillsTab.lua:502), so None and 1 mean the same there.
"""

from dataclasses import dataclass
from typing import Any

from autobuilder.analysis.chain import Which
from autobuilder.pob import wire
from autobuilder.pob.endpoints import Endpoint
from autobuilder.pob.session import PobSession


@dataclass(frozen=True)
class Gem:
    name: str
    support: bool
    enabled: bool
    level: float | None
    quality: float | None
    count: float | None
    part: float | None  # skillPart, the sidebar's
    stages: float | None  # skillStageCount
    mines: float | None  # skillMineCount
    minion: str | None  # skillMinion
    minion_skill: float | None  # skillMinionSkill


@dataclass(frozen=True)
class ActiveSkill:
    name: str
    gem: int | None  # the gem it comes from, 1-based in the group's gem list
    part: str | None  # the part's name as PoB shows it


@dataclass(frozen=True)
class Group:
    index: int  # 1-based, as PoB numbers socket groups
    label: str
    enabled: bool
    full_dps: bool  # "Include in Full DPS"
    group_count: float | None  # counted in Full DPS (Calcs.lua:119-120)
    main_active_skill: int
    gems: tuple[Gem, ...]
    skills: tuple[ActiveSkill, ...]


@dataclass(frozen=True)
class ConfigBox:
    var: str
    section: str | None
    label: str
    type: str | None
    value: Any  # None when only a placeholder is set
    placeholder: Any
    state: str  # PoB's: "set" (usable), "unusable" (set, the build cannot use it), "default" (only a placeholder)


@dataclass(frozen=True)
class CustomMods:
    title: str | None
    enabled: bool
    text: str


@dataclass(frozen=True)
class Snapshot:
    main_group: int
    calcs_skill_number: int | None
    groups: tuple[Group, ...]
    boxes: tuple[ConfigBox, ...]  # every config box not at PoB's default, in PoB's list order
    custom_mods: tuple[CustomMods, ...]
    config_sets: tuple[str, ...]
    active_config_set: str

    def main_skill(self) -> ActiveSkill | None:
        group = self.groups[self.main_group - 1] if 0 < self.main_group <= len(self.groups) else None
        if group is None or not 0 < group.main_active_skill <= len(group.skills):
            return None
        return group.skills[group.main_active_skill - 1]


def _gem(data: object) -> Gem:
    item = wire.table(data)
    return Gem(
        str(item.get("name") or item.get("nameSpec") or ""),
        bool(wire.flag(item.get("support"))),
        wire.flag(item.get("enabled")) is not False,
        wire.number(item.get("level")),
        wire.number(item.get("quality")),
        wire.number(item.get("count")),
        wire.number(item.get("skillPart")),
        wire.number(item.get("skillStageCount")),
        wire.number(item.get("skillMineCount")),
        wire.text(item.get("skillMinion")),
        wire.number(item.get("skillMinionSkill")),
    )


def _group(index: int, data: object) -> Group:
    item = wire.table(data)
    fields = wire.table(item.get("fields"))
    skills = tuple(
        ActiveSkill(str(skill["name"]), int(skill["gem"]) if skill.get("gem") else None, wire.text(skill.get("part")))
        for skill in (wire.table(raw) for raw in item.get("skills") or ())
    )
    return Group(
        index,
        wire.text(fields.get("label")) or wire.text(fields.get("displayLabel")) or "",
        wire.flag(fields.get("enabled")) is not False,
        wire.flag(fields.get("includeInFullDPS")) is True,
        wire.number(fields.get("groupCount")),
        int(wire.number(fields.get("mainActiveSkill")) or 1),
        tuple(_gem(gem) for gem in item.get("gems") or ()),
        skills,
    )


def _box(data: object) -> ConfigBox:
    item = wire.table(data)
    return ConfigBox(
        str(item["var"]),
        wire.text(item.get("section")),
        str(item.get("label") or item["var"]),
        wire.text(item.get("type")),
        item.get("value"),
        item.get("placeholder"),
        str(item["state"]),
    )


def parse_snapshot(data: object) -> Snapshot:
    item = wire.table(data)
    config = wire.table(item.get("config"))
    custom = tuple(
        CustomMods(wire.text(block.get("title")), wire.flag(block.get("enabled")) is not False, str(block["text"]))
        for block in (wire.table(raw) for raw in config.get("customMods") or ())
    )
    number = wire.number(item.get("calcsSkillNumber"))
    return Snapshot(
        int(wire.number(item.get("mainSocketGroup")) or 1),
        int(number) if number is not None else None,
        tuple(_group(index, group) for index, group in enumerate(item.get("groups") or (), start=1)),
        tuple(_box(box) for box in config.get("rows") or ()),
        custom,
        tuple(str(title) for title in config.get("sets") or ()),
        str(config.get("activeSet") or "Default"),
    )


def read_snapshot(session: PobSession, which: Which = "own") -> Snapshot:
    return parse_snapshot(session.call(Endpoint.COMPARE_SNAPSHOT, {"which": which}))
