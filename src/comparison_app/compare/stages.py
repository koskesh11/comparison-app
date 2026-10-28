"""Build stages, PoB's loadouts (decision 026; the Lua side is pob/lua/compare/stages.lua).

A stage is a tree, an item set, a skill set and a config set with one title. The list and the active stage are PoB's
own (Modules/Build.lua:771-895). A build saved with its four sets from different stages has no active stage; the
comparison refuses it until a stage is picked or the build is fixed in PoB.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from comparison_app.analysis.chain import Which
from comparison_app.errors import MixedStages
from comparison_app.pob import wire
from comparison_app.pob.endpoints import Endpoint
from comparison_app.pob.session import PobSession

PARTS = ("tree", "items", "skills", "config")


@dataclass(frozen=True)
class Stages:
    titles: tuple[str, ...]  # as PoB lists them; one title means no dropdown
    active: str | None  # None: the saved sets are not one stage (decision 026's mixed build)
    parts: Mapping[str, str]  # the active title of each of the four sets

    def mixed(self) -> bool:
        return self.active is None


def _stages(data: object) -> Stages:
    item = wire.table(data)
    parts = wire.table(item.get("parts"))
    titles = tuple(str(title) for title in item.get("stages") or ())
    return Stages(titles, wire.text(item.get("active")), {part: str(parts.get(part, "")) for part in PARTS})


def read_stages(session: PobSession, which: Which = "own") -> Stages:
    return _stages(session.call(Endpoint.BUILD_STAGES, {"which": which}))


def set_stage(session: PobSession, stage: str, which: Which = "own") -> Stages:
    """Puts the loaded build on a stage for the comparison's reads; the file is never written (decision 026)."""
    return _stages(session.call(Endpoint.BUILD_SET_STAGE, {"which": which, "stage": stage}))


def mixed_message(whose: str, stages: Stages) -> str:
    """Which parts come from which stage: "tree '90 self cast'; items, skills and config '90'"."""
    by_title: dict[str, list[str]] = {}
    for part in PARTS:
        by_title.setdefault(stages.parts[part], []).append(part)
    pieces = []
    for title, parts in by_title.items():
        names = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
        pieces.append(f"{names} '{title}'")
    return (
        f"{whose} build mixes stages: {'; '.join(pieces)}. Pick a stage to compare, or fix it in PoB "
        "(choose one loadout) and save."
    )


def ensure_stage(session: PobSession, whose: str, stage: str | None, which: Which = "own") -> Stages:
    """The stage the comparison reads: the one picked, or the saved one; a mixed saved build is refused."""
    if stage is not None:
        return set_stage(session, stage, which)
    stages = read_stages(session, which)
    if stages.mixed():
        raise MixedStages(mixed_message(whose, stages))
    return stages
