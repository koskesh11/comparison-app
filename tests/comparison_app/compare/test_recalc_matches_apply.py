"""M7: the "recalculate with the target's skill setting" button (decision 011) changes in PoB exactly what a real
change to the build does.

Runs once per ChangeKind member: apply the change in memory and recalculate, then edit the same setting into a copy
of the build's XML, the attribute PoB saves (SkillsTab.lua:447-513, the Build element's mainSocketGroup), load it and
recalculate; the chain and the sidebar's output must match, and must differ from the build as saved (a change that
changes nothing proves nothing). A kind no reference build can check is skipped with its NOT_TESTED reason, which the
app shows next to the result.
"""

import json
import xml.etree.ElementTree as ET  # the committed reference builds, not outside input

import pytest

from comparison_app.analysis.scenarios import Scenario
from comparison_app.compare.recalc import NOT_TESTED, Change, Recalculated, recalculate
from comparison_app.pob.endpoints import ChangeKind
from comparison_app.pob.session import PobSession

pytestmark = pytest.mark.pob

ATTRIBUTES = {
    ChangeKind.SKILL_PART: "skillPart",
    ChangeKind.STAGE_COUNT: "skillStageCount",
    ChangeKind.MINE_COUNT: "skillMineCount",
    ChangeKind.MINION: "skillMinion",
    ChangeKind.MINION_SKILL: "skillMinionSkill",
    ChangeKind.GEM_COUNT: "count",
    ChangeKind.GROUP_COUNT: "groupCount",
    ChangeKind.MAIN_ACTIVE_SKILL: "mainActiveSkill",
    ChangeKind.MAIN_GROUP: "mainSocketGroup",
}
GROUP_KINDS = {ChangeKind.GROUP_COUNT, ChangeKind.MAIN_ACTIVE_SKILL}
# kind -> (build, change): Worb's Winter Orb is group 2 gem 2; CoC EK Assa's group 1 holds Ethereal Knives and Cyclone;
# Stone Golem is CoC EK Assa with Summon Stone Golem (group 7, gem 4) as main skill.
CASES = {
    ChangeKind.SKILL_PART: ("Worb", Change(ChangeKind.SKILL_PART, 2, 2, 2)),
    ChangeKind.STAGE_COUNT: ("Worb", Change(ChangeKind.STAGE_COUNT, 2, 2, 5)),
    ChangeKind.GEM_COUNT: ("Worb", Change(ChangeKind.GEM_COUNT, 2, 2, 3)),
    ChangeKind.MAIN_GROUP: ("Worb", Change(ChangeKind.MAIN_GROUP, 1, None, 1)),
    ChangeKind.GROUP_COUNT: ("CoC EK Assa", Change(ChangeKind.GROUP_COUNT, 1, None, 2)),
    ChangeKind.MAIN_ACTIVE_SKILL: ("CoC EK Assa", Change(ChangeKind.MAIN_ACTIVE_SKILL, 1, None, 2)),
    ChangeKind.MINION_SKILL: ("Stone Golem", Change(ChangeKind.MINION_SKILL, 7, 4, 2)),
}


def saved_copy(xml: str, change: Change) -> str:
    """The build with the change made the way PoB saves it."""
    root = ET.fromstring(xml)  # noqa: S314 - the committed reference builds, not outside input
    if change.kind is ChangeKind.MAIN_GROUP:
        element = root.find("Build")
    else:
        skills = root.find("Skills")
        assert skills is not None
        sets = {each.get("id"): each for each in skills.findall("SkillSet")}
        active = sets.get(skills.get("activeSkillSet"))
        groups = (skills if active is None else active).findall("Skill")
        group = groups[change.group - 1]
        element = group if change.kind in GROUP_KINDS else group.findall("Gem")[(change.gem or 0) - 1]
    assert element is not None
    element.set(ATTRIBUTES[change.kind], str(change.value))
    return ET.tostring(root, encoding="unicode")


def shown(result: Recalculated) -> tuple[object, str]:
    return result.chain, json.dumps(result.output, sort_keys=True)


@pytest.mark.parametrize("kind", list(ChangeKind))
def test_in_memory_change_matches_a_saved_change(
    pob_session: PobSession, reference_xml: dict[str, str], variant_xml: dict[str, str], kind: ChangeKind
) -> None:
    if kind in NOT_TESTED:
        pytest.skip(NOT_TESTED[kind])
    if kind not in CASES:
        pytest.fail(f"write the M7 case for {kind} in CASES, or its reason in recalc.NOT_TESTED")
    name, change = CASES[kind]
    xml = {**reference_xml, **variant_xml}[name]
    pob_session.load_build(xml, name)
    as_saved = shown(recalculate(pob_session, Scenario.PINNACLE_BOSS, []))
    in_memory = shown(recalculate(pob_session, Scenario.PINNACLE_BOSS, [change]))
    pob_session.load_build(saved_copy(xml, change), f"{name}, {kind}")
    saved = shown(recalculate(pob_session, Scenario.PINNACLE_BOSS, []))
    assert in_memory != as_saved, f"{kind} changed nothing on {name}: pick a case where it matters"
    assert in_memory == saved
