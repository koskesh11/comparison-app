"""Do the two main skills have the same settings? (compare/skill_settings.py, decision 011), on snapshot records."""

import pytest

from comparison_app.analysis.scenarios import Scenario
from comparison_app.compare.recalc import pick_target_skill, recalculate
from comparison_app.compare.skill_settings import Match, compare_settings
from comparison_app.compare.snapshot import ActiveSkill, Gem, Group, Snapshot, read_snapshot
from comparison_app.compare.target import open_target, release_target
from comparison_app.pob.session import PobSession


def gem(name: str, stages: float | None = None, count: float = 1) -> Gem:
    return Gem(name, False, True, 20, 20, count, 1, stages, None, None, None)


def group(
    index: int, skill: str, part: str | None = None, stages: float | None = None, max_stages: float | None = None
) -> Group:
    return Group(index, skill, True, True, None, 1, (gem(skill, stages),), (ActiveSkill(skill, 1, part, max_stages),))


def snapshot(main: int, *groups: Group) -> Snapshot:
    return Snapshot(main, main, groups, (), (), ("Default",), "Default")


def lightning_strike(main: int, melee_first: bool = True) -> Snapshot:
    """Lightning Strike set up twice, one group per part (decision 011's example)."""
    parts = ["Melee", "Projectile"] if melee_first else ["Projectile", "Melee"]
    return snapshot(main, *(group(index, "Lightning Strike", part) for index, part in enumerate(parts, start=1)))


def test_the_same_setup_shows_the_chain() -> None:
    result = compare_settings(
        snapshot(1, group(1, "Winter Orb", "Channelling", 13)), snapshot(1, group(1, "Winter Orb", "Channelling", 13))
    )
    assert (result.match, result.differing) == (Match.SAME, ())


def test_lightning_strike_twice_in_another_order_is_the_same_setup() -> None:
    result = compare_settings(lightning_strike(1), lightning_strike(2, melee_first=False))
    assert result.match is Match.SAME  # both mains are the melee group


def test_the_target_running_your_setup_in_another_group_offers_that_group() -> None:
    result = compare_settings(lightning_strike(1), lightning_strike(2))  # yours melee, the target's main projectile
    assert (result.match, result.differing, result.target_choices) == (Match.OTHER_GROUP, ("part",), ((1, 1),))


def test_different_settings_hide_the_chain() -> None:
    result = compare_settings(
        snapshot(1, group(1, "Winter Orb", stages=13)), snapshot(1, group(1, "Winter Orb", stages=5))
    )
    assert (result.match, result.differing) == (Match.SETTINGS_DIFFER, ("stages",))
    assert result.yours is not None and result.target is not None
    assert (result.yours.stages, result.target.stages) == (13, 5)  # both sides' values for the page


def test_stages_over_the_maximum_are_the_maximum() -> None:
    capped = snapshot(1, group(1, "Winter Orb", stages=13, max_stages=11))
    assert compare_settings(capped, snapshot(1, group(1, "Winter Orb", stages=11, max_stages=11))).match is Match.SAME


def test_an_unset_stage_count_is_the_skills_maximum() -> None:
    unset = snapshot(1, group(1, "Winter Orb", stages=None, max_stages=13))
    assert compare_settings(snapshot(1, group(1, "Winter Orb", stages=13)), unset).match is Match.SAME


def test_a_different_main_skill_warns_and_offers_the_targets_groups() -> None:
    target = snapshot(1, group(1, "Ethereal Knives"), group(2, "Winter Orb"))
    result = compare_settings(snapshot(1, group(1, "Winter Orb")), target)
    assert (result.match, result.target_choices) == (Match.DIFFERENT_SKILL, ((2, 1),))
    assert "Ethereal Knives" in result.message and "group 2 (skill 1)" in result.message


@pytest.mark.pob
def test_one_real_pair(pob_session: PobSession, reference_xml: dict[str, str], variant_xml: dict[str, str]) -> None:
    """CoC EK Assa against itself with Cyclone as main skill. Group 1 holds both skills, so the offer names the skill
    too (review 111, finding 1): picking it points the target at Ethereal Knives, in memory."""
    pob_session.load_build(reference_xml["CoC EK Assa"], "CoC EK Assa")
    yours = read_snapshot(pob_session)
    open_target(pob_session, variant_xml["Cyclone"], "Cyclone")
    try:
        target = read_snapshot(pob_session, "target")
        assert compare_settings(yours, yours).match is Match.SAME
        result = compare_settings(yours, target)
        assert (result.match, result.target_choices) == (Match.DIFFERENT_SKILL, ((1, 1),))
        picked = recalculate(pob_session, Scenario.PINNACLE_BOSS, pick_target_skill(result.target_choices[0]), "target")
        assert picked.chain.skill == "Ethereal Knives"
    finally:
        release_target(pob_session)
