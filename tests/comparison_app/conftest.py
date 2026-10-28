"""Shared fixtures for the src/ tests (docs/ARCHITECTURE.md, "Tests").

- pob_session: one Path of Building per test run (S6), with its user data and write root in a temporary folder. The PoB
  install and the owner's builds are listed before and after; any change outside Builds/AutoBuilder fails the run (S1;
  PoB's own timeless-jewel cache is allowed). Every test marked `pob` runs on one xdist worker (`--dist loadgroup`), so
  a parallel run boots PoB once.
- reference_xml: the two reference builds (decision 014), committed byte for byte under fixtures/builds.
- No network: outside tests/comparison_app/intake every socket refuses to connect (S2).
"""

import os
import socket
import xml.etree.ElementTree as ET  # the committed test builds, not outside input
from collections.abc import Iterator
from pathlib import Path

import pytest

from comparison_app.pob.session import PobPaths, PobSession, open_session

POB_OWN_WRITES = ("Data/TimelessJewelData/",)
OUTPUT_FOLDER = ("AutoBuilder/",)
REFERENCE_BUILDS = Path(__file__).parent / "fixtures" / "builds"
REFERENCE_FILES = {"Worb": "Worb.xml", "CoC EK Assa": "CoC EK Assa.xml"}
VARIETY_FILES = {name: f"{name}.xml" for name in ("Elemental Hit Slayer", "Phys Dot Elementalist", "Winter Orb")}
# The four sets of a PoB stage (loadout), switched together by title (Modules/Build.lua:359-416; decision 026)
STAGE_SETS = (
    ("Tree", "Spec", "activeSpec"),
    ("Items", "ItemSet", "activeItemSet"),
    ("Skills", "SkillSet", "activeSkillSet"),
    ("Config", "ConfigSet", "activeConfigSet"),
)


def pob_install() -> Path:
    appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    return Path(os.environ.get("POB_DIR", Path(appdata) / "Path of Building Community"))


def builds_folder() -> Path:
    return Path.home() / "Documents" / "Path of Building" / "Builds"


def listing(root: Path, allowed: tuple[str, ...]) -> dict[str, tuple[int, int]]:
    """Size and modification time of every file under root, except the allowed prefixes."""
    if not root.exists():
        return {}
    files = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if path.is_file() and not name.startswith(allowed):
            stat = path.stat()
            files[name] = (stat.st_size, stat.st_mtime_ns)
    return files


def changed(before: dict[str, tuple[int, int]], after: dict[str, tuple[int, int]]) -> list[str]:
    return sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))


@pytest.hookimpl(tryfirst=True)  # before xdist's own hook, which turns the marker into the group
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if item.get_closest_marker("pob"):
            item.add_marker(pytest.mark.xdist_group("pob"))


@pytest.fixture(scope="session")
def pob_dir() -> Path:
    if not (pob_install() / "Launch.lua").is_file():
        pytest.skip(f"needs Path of Building in {pob_install()}")
    return pob_install()


@pytest.fixture(scope="session")
def pob_paths(pob_dir: Path, tmp_path_factory: pytest.TempPathFactory) -> PobPaths:
    root = tmp_path_factory.mktemp("pob")
    (root / "AutoBuilder").mkdir()
    return PobPaths(pob_dir, root / "user", root / "AutoBuilder")


@pytest.fixture(scope="session")
def pob_session(pob_paths: PobPaths) -> Iterator[PobSession]:
    roots = ((pob_paths.pob_dir, POB_OWN_WRITES), (builds_folder(), OUTPUT_FOLDER))
    before = [listing(folder, allowed) for folder, allowed in roots]
    previous = Path.cwd()
    with open_session(pob_paths) as opened:
        yield opened
    os.chdir(previous)
    for (folder, allowed), old in zip(roots, before, strict=True):
        touched = changed(old, listing(folder, allowed))
        assert not touched, f"PoB tests changed files in the read-only folder {folder}: {touched[:10]}"


@pytest.fixture(scope="session")
def owner_builds() -> Path:
    """The owner's PoB Builds folder, read only; tests that use it are marked `owner`."""
    if not builds_folder().is_dir():
        pytest.skip(f"needs the owner's builds in {builds_folder()}")
    return builds_folder()


@pytest.fixture(scope="session")
def reference_xml() -> dict[str, str]:
    return {name: (REFERENCE_BUILDS / file).read_text(encoding="utf-8") for name, file in REFERENCE_FILES.items()}


def _edited(xml: str, old: str, new: str) -> str:
    assert xml.count(old) == 1, f"the reference build changed: {old!r} is not there once"
    return xml.replace(old, new)


@pytest.fixture(scope="session")
def variant_xml(reference_xml: dict[str, str]) -> dict[str, str]:
    """CoC EK Assa with another main skill: an attack (Cyclone, the second active skill of group 1) and a minion
    (Summon Stone Golem, group 7, a group the saved Calcs tab is not on, whose gem saves no skillMinionCalcs)."""
    assa = reference_xml["CoC EK Assa"]
    return {
        "Cyclone": _edited(assa, 'slot="Body Armour" mainActiveSkill="1"', 'slot="Body Armour" mainActiveSkill="2"'),
        "Stone Golem": _edited(assa, 'mainSocketGroup="1"', 'mainSocketGroup="7"'),
    }


@pytest.fixture(autouse=True)
def no_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if "intake" in request.path.parts:
        return

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise OSError("tests do not use the network (S2); only tests/comparison_app/intake may")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture(scope="session")
def variety_xml() -> dict[str, str]:
    """The owner's variety builds (decision 014, extended 2026-10-28): dual wield, several damage types, minions."""
    return {name: (REFERENCE_BUILDS / file).read_text(encoding="utf-8") for name, file in VARIETY_FILES.items()}


def stages(xml: str) -> list[tuple[str, str]]:
    """Each stage of a build as its own build: (title, XML with that stage's four sets active), in the tree's order.
    A stage is a title all four sets share, as PoB pairs them (Modules/Build.lua:359-416)."""
    root = ET.fromstring(xml)  # noqa: S314 - the committed test builds
    titles: set[str | None] | None = None
    for parent, child, _ in STAGE_SETS:
        node = root.find(parent)
        found = {each.get("title") or "Default" for each in node.findall(child)} if node is not None else set()
        titles = found if titles is None else titles & found
    result = []
    tree = root.find("Tree")
    for spec in tree.findall("Spec") if tree is not None else []:
        title = spec.get("title") or "Default"  # PoB's name for an untitled set
        if not titles or title not in titles:
            continue
        copy = ET.fromstring(xml)  # noqa: S314 - the committed test builds
        for parent, child, active in STAGE_SETS:
            node = copy.find(parent)
            assert node is not None
            kids = node.findall(child)
            index = next(i for i, kid in enumerate(kids) if (kid.get("title") or "Default") == title)
            node.set(active, str(index + 1) if parent == "Tree" else str(kids[index].get("id")))
        result.append((str(title), ET.tostring(copy, encoding="unicode")))
    return result
