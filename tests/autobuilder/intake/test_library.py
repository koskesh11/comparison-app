"""Your builds list: one check decides what is listed and what may be opened (the fix to server.py:43-57)."""

import os
from pathlib import Path

import pytest

from autobuilder.errors import InvalidInput, Unreadable
from autobuilder.intake.library import Library

BUILD = '<PathOfBuilding><Build level="1"/></PathOfBuilding>'


@pytest.fixture
def builds(tmp_path: Path) -> Path:
    root = tmp_path / "Builds"
    (root / "3.29" / "Ninja Builds").mkdir(parents=True)
    (root / "Top.xml").write_text(BUILD, encoding="utf-8")
    (root / "3.29" / "Ninja Builds" / "CoC.xml").write_text(BUILD, encoding="utf-8")
    (root / "notes.txt").write_text("not a build", encoding="utf-8")
    os.utime(root / "Top.xml", (1, 1))
    (tmp_path / "Outside.xml").write_text(BUILD, encoding="utf-8")
    return root


def test_builds_are_listed_newest_first_with_their_folder(builds: Path) -> None:
    listed = Library(builds).builds()
    assert [(build.path, build.name, build.folder) for build in listed] == [
        ("3.29/Ninja Builds/CoC.xml", "CoC", "3.29/Ninja Builds"),
        ("Top.xml", "Top", ""),
    ]


def test_every_listed_build_opens_and_nothing_outside_does(builds: Path) -> None:
    library = Library(builds)
    assert [library.read(build.path) for build in library.builds()] == [BUILD, BUILD]
    for outside in ("../Outside.xml", str(builds.parent / "Outside.xml"), "notes.txt", "missing.xml", "3.29"):
        with pytest.raises(InvalidInput, match="inside the Path of Building Builds folder"):
            library.read(outside)


def test_a_link_out_of_the_folder_is_neither_listed_nor_opened(builds: Path) -> None:
    link = builds / "Linked.xml"
    try:
        link.symlink_to(builds.parent / "Outside.xml")
    except OSError:
        pytest.skip("this Windows account may not create symbolic links")
    library = Library(builds)
    assert "Linked.xml" not in [build.path for build in library.builds()]
    with pytest.raises(InvalidInput):
        library.read("Linked.xml")


def test_a_file_that_is_not_a_pob_build_is_unreadable(builds: Path) -> None:
    (builds / "Broken.xml").write_text("<html/>", encoding="utf-8")
    with pytest.raises(Unreadable):
        Library(builds).read("Broken.xml")


@pytest.mark.owner
def test_every_build_in_the_owners_folder_is_listed_and_reads(owner_builds: Path) -> None:
    library = Library(owner_builds)
    listed = library.builds()
    assert listed
    assert all(library.read(build.path).startswith(("<?xml", "<PathOfBuilding", "\ufeff")) for build in listed)
