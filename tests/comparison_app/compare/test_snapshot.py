"""The skill settings and config of a build as PoB has them (compare/snapshot.py, pob/lua/compare/snapshot.lua)."""

from collections.abc import Iterator

import pytest

from comparison_app.compare.snapshot import ActiveSkill, CustomMods, Snapshot, read_snapshot
from comparison_app.compare.target import open_target, release_target
from comparison_app.pob.session import PobSession

pytestmark = pytest.mark.pob

CHILLED = '<Input name="conditionEnemyChilled" boolean="true"/>'


@pytest.fixture
def session(pob_session: PobSession) -> Iterator[PobSession]:
    yield pob_session
    release_target(pob_session)


def with_input(xml: str, line: str) -> str:
    assert xml.count(CHILLED) == 1
    return xml.replace(CHILLED, CHILLED + line)


def box(snapshot: Snapshot, var: str) -> tuple[object, object, str]:
    (found,) = [each for each in snapshot.boxes if each.var == var]
    return found.value, found.placeholder, found.state


def test_worbs_settings_are_pobs(session: PobSession, reference_xml: dict[str, str]) -> None:
    session.load_build(reference_xml["Worb"], "Worb")
    snapshot = read_snapshot(session)
    assert (snapshot.main_group, snapshot.calcs_skill_number) == (2, 1)
    assert snapshot.main_skill() == ActiveSkill("Winter Orb", 2, "Channelling", 11)  # PoB's maximum; Worb saves 13
    orb = snapshot.groups[1].gems[1]
    assert (orb.name, orb.part, orb.stages, orb.count, orb.support) == ("Winter Orb", 1, 13, 5, False)
    assert snapshot.groups[1].gems[0].support is True  # Increased Critical Strikes
    assert box(snapshot, "conditionEnemyChilled") == (True, None, "set")
    assert box(snapshot, "enemyLevel") == (None, 84, "default")  # the boss box's placeholder (ConfigOptions.lua:2086)
    assert (snapshot.config_sets, snapshot.custom_mods) == (("Default",), ())


def test_a_box_the_build_cannot_use_is_pobs_red_box(session: PobSession, reference_xml: dict[str, str]) -> None:
    """Worb has no Cyclone, so the Cyclone box CoC EK Assa sets is one PoB draws red (ConfigTab.lua:701-703)."""
    session.load_build(with_input(reference_xml["Worb"], '<Input name="channellingCycloneCheck" boolean="true"/>'), "W")
    assert box(read_snapshot(session), "channellingCycloneCheck") == (True, None, "unusable")


def test_custom_modifiers_are_read(session: PobSession, reference_xml: dict[str, str]) -> None:
    """A legacy customMods input becomes the first block (ConfigTab.lua:926-933)."""
    session.load_build(with_input(reference_xml["Worb"], '<Input name="customMods" string="20% more Damage"/>'), "W")
    assert read_snapshot(session).custom_mods == (CustomMods("Default", True, "20% more Damage"),)


def test_the_targets_snapshot_is_the_same_builds_own(session: PobSession, reference_xml: dict[str, str]) -> None:
    session.load_build(reference_xml["CoC EK Assa"], "CoC EK Assa")
    yours = read_snapshot(session)
    session.load_build(reference_xml["Worb"], "Worb")
    open_target(session, reference_xml["CoC EK Assa"], "CoC EK Assa")
    assert read_snapshot(session, "target") == yours
