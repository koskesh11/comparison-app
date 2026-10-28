"""The config differences between two builds (compare/diff/context.py, decision 010)."""

from typing import Any

import pytest

from autobuilder.compare.diff.context import SCENARIO_NOTE, compare_config
from autobuilder.compare.snapshot import ConfigBox, CustomMods, Snapshot, read_snapshot
from autobuilder.compare.target import open_target, release_target
from autobuilder.pob.session import PobSession


def box(var: str, value: Any, order: int, state: str = "set", label: str | None = None) -> ConfigBox:
    return ConfigBox(var, "General", label or var, "check", value, None, state, order)


def snapshot(*boxes: ConfigBox, custom: tuple[CustomMods, ...] = (), sets: tuple[str, ...] = ("Default",)) -> Snapshot:
    return Snapshot(1, 1, (), boxes, custom, sets, sets[0])


def test_differences_come_in_pobs_list_order() -> None:
    yours = snapshot(box("chilled", True, 5), box("bandit", "Eramir", 2), box("same", 3, 9))
    target = snapshot(box("chilled", False, 5), box("same", 3, 9))
    report = compare_config(yours, target)
    assert [(each.var, each.target and each.target.value) for each in report.differences] == [
        ("bandit", None),  # at PoB's default in the target
        ("chilled", False),
    ]


def test_the_boss_box_is_set_by_the_scenario() -> None:
    report = compare_config(snapshot(box("enemyIsBoss", "Boss", 900)), snapshot(box("enemyIsBoss", "Boss", 900)))
    assert [(each.var, each.note) for each in report.differences] == [("enemyIsBoss", SCENARIO_NOTE)]


def test_a_box_a_build_cannot_use_says_so() -> None:
    report = compare_config(snapshot(box("cyclone", True, 3, "unusable")), snapshot())
    (difference,) = report.differences
    assert difference.note is not None and difference.note.startswith("your build cannot use it")


def test_an_unset_multiplier_looks_wrong_even_when_both_agree() -> None:
    unset = box("multiplierChannelling", None, 7, "unset", "Channeling for # seconds:")
    report = compare_config(snapshot(unset), snapshot(unset))
    assert report.differences == ()
    assert [(each.whose, each.box.var) for each in report.looks_wrong] == [
        ("yours", "multiplierChannelling"),
        ("target", "multiplierChannelling"),
    ]


def test_custom_modifiers_only_one_build_has() -> None:
    more = CustomMods("Default", True, "20% more Damage")
    report = compare_config(snapshot(), snapshot(custom=(more, CustomMods("Off", False, "1% more Damage"))))
    assert (report.custom_mods_yours, report.custom_mods_target) == ((), (more,))


def test_config_sets_are_named_when_a_build_has_several() -> None:
    assert compare_config(snapshot(), snapshot()).config_sets is None
    assert compare_config(snapshot(sets=("Boss", "Map")), snapshot()).config_sets == ("Boss", "Default")


@pytest.mark.pob
def test_one_real_pair(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    """Worb against CoC EK Assa: their General boxes differ in PoB's order; Worb is decision 010's example of a setting
    that looks wrong, Focused Channelling with no channelling time (ConfigOptions.lua:1274)."""
    pob_session.load_build(reference_xml["Worb"], "Worb")
    yours = read_snapshot(pob_session)
    open_target(pob_session, reference_xml["CoC EK Assa"], "CoC EK Assa")
    try:
        target = read_snapshot(pob_session, "target")
    finally:
        release_target(pob_session)
    report = compare_config(yours, target)
    general = [each.var for each in report.differences if each.section == "General"]
    assert general[:2] == ["bandit", "pantheonMinorGod"]  # pantheonMajorGod is the same in both
    assert [(each.whose, each.box.var) for each in report.looks_wrong] == [("yours", "multiplierChannelling")]
