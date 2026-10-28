"""Which DPS the header shows, PoB's Full DPS list, a change in percent (analysis/skills.py)."""

import math

import pytest

from autobuilder.analysis.scenarios import Scenario
from autobuilder.analysis.skills import change_pct, header_dps, read_summary, skill_rows
from autobuilder.compare.target import open_target, release_target
from autobuilder.errors import NoMainSkill
from autobuilder.pob.session import BuildSummary, PobSession, SkillDps


def summary(
    stats: dict[str, float], main_skill: str | None = "Cyclone", rows: tuple[SkillDps, ...] = ()
) -> BuildSummary:
    return BuildSummary("2.67.2", "b", "Shadow", "Assassin", 95, main_skill, stats, skill_dps=rows)


def test_the_header_shows_full_dps_when_pob_has_it() -> None:
    assert header_dps(summary({"FullDPS": 10.0, "CombinedDPS": 3.0})) == header_dps(summary({"FullDPS": 10.0}))
    assert header_dps(summary({"FullDPS": 10.0})).key == "FullDPS"


def test_without_full_dps_the_header_shows_the_main_skill_and_says_so() -> None:
    shown = header_dps(summary({"FullDPS": 0.0, "CombinedDPS": 3.0}))
    assert (shown.key, shown.value) == ("CombinedDPS", 3.0)
    assert shown.warning is not None and "Cyclone" in shown.warning
    with pytest.raises(NoMainSkill):
        header_dps(summary({"FullDPS": 0.0}, main_skill=None))


def test_the_full_dps_list_is_biggest_share_first() -> None:
    rows = (SkillDps("A", None, 1, 10.0), SkillDps("B", None, 3, 5.0), SkillDps("C", "part", 1, 10.0))
    assert [row.name for row in skill_rows(summary({}, rows=rows))] == ["B", "A", "C"]


@pytest.mark.parametrize(("new", "old", "change"), [(15.0, 10.0, 50.0), (1.0, 0.0, None), (1.0, math.inf, None)])
def test_a_change_without_a_number_is_none(new: float, old: float, change: float | None) -> None:
    assert change_pct(new, old) == change
    assert change_pct(math.nan, 1.0) is None


@pytest.mark.pob
def test_the_targets_summary_is_the_same_builds_own(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    pob_session.load_build(reference_xml["CoC EK Assa"], "CoC EK Assa")
    yours = read_summary(pob_session, Scenario.PINNACLE_BOSS)
    assert yours.skill_dps and header_dps(yours).key == "FullDPS"
    pob_session.load_build(reference_xml["Worb"], "Worb")
    open_target(pob_session, reference_xml["CoC EK Assa"], "CoC EK Assa")
    try:
        target = read_summary(pob_session, Scenario.PINNACLE_BOSS, "target")
    finally:
        release_target(pob_session)
    # PoB's sidebar sorts the build's own list (Build.lua:1934), an entry's stays in calculation order
    assert (target.stats, skill_rows(target)) == (yours.stats, skill_rows(yours))
