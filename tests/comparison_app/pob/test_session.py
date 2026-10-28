"""The PoB session: paths checked before the boot, builds opened from XML text, and a build PoB cannot open fails
loudly. The first app showed the previous build's numbers under the new name instead (pob_headless.lua:78-85,
measured in task 102 area A: a bad root and a truncated file after Worb both "loaded")."""

import math
from pathlib import Path

import pytest

from comparison_app.errors import BuildLoadFailed, NoBuildLoaded, PobError, PobNotInstalled
from comparison_app.pob.session import BuildSummary, PobPaths, PobSession, check_paths

pytestmark = pytest.mark.pob

OLD_GAME_VERSION = '<PathOfBuilding><Build targetVersion="2_6" level="1"/></PathOfBuilding>'


def test_paths_must_be_absolute_and_hold_pob(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must be absolute"):
        check_paths(PobPaths(Path("relative"), tmp_path, tmp_path))
    with pytest.raises(PobNotInstalled, match=r"missing Launch\.lua, lua51\.dll"):
        check_paths(PobPaths(tmp_path, tmp_path.parent / "user", tmp_path.parent / "out"))


@pytest.mark.parametrize(
    ("user", "root"),
    [("install/user", "out"), ("user", "install"), ("user", "INSTALL/Builds"), ("user", ".")],
    ids=["user data inside", "write root is the install", "write root inside", "write root contains the install"],
)
def test_the_folders_pob_may_write_stay_out_of_its_install(tmp_path: Path, user: str, root: str) -> None:
    """The sandbox lets PoB write anywhere under these two folders (sandbox.lua:44-54)."""
    with pytest.raises(ValueError, match="outside its install"):
        check_paths(PobPaths(tmp_path / "install", tmp_path / user, tmp_path / root))


def test_a_summary_keeps_only_the_stats_pob_computed() -> None:
    summary = BuildSummary.from_wire({"buildName": "x", "level": 90, "stats": {"FullDPS": 1.5, "Life": math.inf}})
    assert (summary.build_name, summary.level, summary.main_skill) == ("x", 90.0, None)
    assert summary.stats == {"FullDPS": 1.5, "Life": math.inf}
    assert BuildSummary.from_wire({"stats": []}).stats == {}
    with pytest.raises(PobError, match="expected a number"):
        BuildSummary.from_wire({"stats": {"FullDPS": "high"}})


def test_worb_opens_as_saved(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    summary = pob_session.load_build(reference_xml["Worb"], "Worb")
    assert (summary.build_name, summary.class_name, summary.ascendancy) == ("Worb", "Witch", "Elementalist")
    assert (summary.level, summary.main_skill) == (98, "Winter Orb")
    # FullDPS as task 102 area A measured it (Worb base 7,176,019) on PoB 2.67.2
    assert round(summary.stats["FullDPS"]) == 7_176_019
    assert pob_session.summary() == summary


@pytest.mark.parametrize(
    ("xml", "message"),
    [
        ("<NotPoB/>", "'PathOfBuilding' root element missing"),
        ("worb-truncated", "unclosed element 'Build'"),
        (OLD_GAME_VERSION, "PoB opened a dialog instead of the build"),
    ],
    ids=["bad root", "truncated", "older game version"],
)
def test_a_build_pob_cannot_open_fails_and_leaves_none_open(
    pob_session: PobSession, reference_xml: dict[str, str], xml: str, message: str
) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    text = reference_xml["Worb"][:500] if xml == "worb-truncated" else xml
    with pytest.raises(BuildLoadFailed) as caught:
        pob_session.load_build(text, "broken")
    assert caught.value.message.endswith(message) and "Press" not in caught.value.message
    with pytest.raises(NoBuildLoaded):
        pob_session.summary()


def test_each_failed_load_reports_its_own_error(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    """PoB keeps its first error prompt until it is dismissed (Launch.lua:382); each load must see its own."""
    with pytest.raises(BuildLoadFailed, match="root element missing"):
        pob_session.load_build("<NotPoB/>", "first")
    with pytest.raises(BuildLoadFailed, match="unclosed element"):
        pob_session.load_build(reference_xml["Worb"][:500], "second")
    assert pob_session.load_build(reference_xml["CoC EK Assa"], "CoC EK Assa").build_name == "CoC EK Assa"


def test_a_refused_load_request_also_leaves_no_build_open(
    pob_session: PobSession, reference_xml: dict[str, str]
) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    with pytest.raises(PobError, match="needs the build's xml and name"):
        pob_session.load_build(None, "x")  # type: ignore[arg-type]
    with pytest.raises(NoBuildLoaded):
        pob_session.summary()
