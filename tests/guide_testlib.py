"""Shared real-PoB helpers for guide Lua integration tests."""

from __future__ import annotations

import base64
import json
import sys
import tempfile
import zlib
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
ENGINE_DIR = ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(TESTS_DIR))

import golden_common as gc  # noqa: E402
from pobhost import PobEngine  # noqa: E402


def decode_guide() -> Path:
    """Decode the checked-in pobb code below a disposable directory."""
    code = (TESTS_DIR / "fixtures" / "pobb_F8CiRC9KVADl.code.txt").read_text(encoding="utf-8").strip()
    xml = zlib.decompress(base64.urlsafe_b64decode(code)).decode("utf-8")
    path = Path(tempfile.mkdtemp(prefix="pob_guide_")) / "guide.xml"
    path.write_text(xml, encoding="utf-8", newline="\n")
    return path


def make_engine(build_key: str = "EK") -> PobEngine:
    """Boot PoB and load one of the real golden builds."""
    engine = PobEngine()
    engine.load_build(gc.build_path(gc.RAW_BUILDS[build_key]))
    return engine


def _nullable(value, kind) -> bool:
    return value is None or isinstance(value, kind)


def _validate_nodes(nodes: list[dict]) -> None:
    node_ids = [node["id"] for node in nodes]
    assert node_ids == sorted(node_ids) and all(isinstance(node_id, int) for node_id in node_ids)
    keys = {"id", "name", "type", "ascendancy", "cluster", "conquered", "modKeyEmpty",
            "mastery", "socket", "override"}
    for node in nodes:
        assert set(node) == keys
        assert isinstance(node["name"], str) and isinstance(node["type"], str)
        assert _nullable(node["ascendancy"], str) and _nullable(node["mastery"], int)
        assert all(isinstance(node[key], bool) for key in
                   ("cluster", "conquered", "modKeyEmpty", "socket"))
        override = node["override"]
        assert override is None or isinstance(override, dict)
        if override is not None:
            assert set(override) == {"name", "lines", "plain"}
            assert isinstance(override["name"], str) and isinstance(override["plain"], str)
            assert isinstance(override["lines"], list)
            assert all(isinstance(line, str) for line in override["lines"])


def _validate_items(items: list[dict]) -> None:
    slots = [item["slot"] for item in items]
    assert slots == sorted(slots) and len(slots) == len(set(slots))
    keys = {"slot", "name", "title", "base", "rarity", "variant", "raw", "mods", "corrupted",
            "flaskActive", "cluster", "timeless", "abyssJewels", "socketNode", "weaponSet",
            "socketAllocated"}
    for item in items:
        assert set(item) == keys
        assert all(isinstance(item[key], str) for key in ("slot", "name", "base", "rarity", "raw"))
        assert _nullable(item["title"], str) and _nullable(item["variant"], str)
        assert all(isinstance(line, str) for line in item["mods"])
        assert all(isinstance(item[key], bool) for key in ("corrupted", "cluster", "timeless"))
        assert _nullable(item["flaskActive"], bool) and _nullable(item["socketNode"], int)
        if item["slot"].startswith("Flask "):
            assert isinstance(item["flaskActive"], bool)
        assert _nullable(item["weaponSet"], int) and _nullable(item["socketAllocated"], bool)
        assert all(set(jewel) == {"slot", "name", "raw"} for jewel in item["abyssJewels"])


def _validate_groups(groups: list[dict]) -> None:
    for group in groups:
        assert set(group) == {"index", "label", "slot", "enabled", "fullDps", "mainActiveSkill",
                              "socketLimit", "source", "gems"}
        assert isinstance(group["index"], int) and isinstance(group["gems"], list)
        assert isinstance(group["label"], str) and _nullable(group["slot"], str)
        assert isinstance(group["enabled"], bool) and isinstance(group["fullDps"], bool)
        assert isinstance(group["mainActiveSkill"], int) and _nullable(group["socketLimit"], int)
        for gem in group["gems"]:
            assert set(gem) == {"name", "gemId", "isSupport", "level", "quality", "qualityId",
                                "enabled", "count", "skillPart", "family"}
            assert isinstance(gem["name"], str) and isinstance(gem["level"], int)
            assert isinstance(gem["quality"], int) and isinstance(gem["qualityId"], str)
            assert isinstance(gem["isSupport"], bool) and isinstance(gem["enabled"], bool)
            assert _nullable(gem["gemId"], str) and _nullable(gem["count"], int)
            assert _nullable(gem["skillPart"], int) and isinstance(gem["family"], str)


def validate_snapshot(data: dict) -> None:
    """Validate the stable snapshot-v1 shape used by the pure Python diff."""
    required = {"schema", "which", "label", "pobVersion", "className", "ascendancy", "level",
                "treeVersion", "mainSkill", "mainGroup", "sets", "points", "nodes", "groups",
                "items", "config", "handedness"}
    assert set(data) == required
    assert data["schema"] == 1 and data["which"] in {"player", "guide"}
    assert isinstance(data["label"], str) and isinstance(data["pobVersion"], (str, int, float))
    assert isinstance(data["className"], str) and _nullable(data["ascendancy"], str)
    assert isinstance(data["level"], int) and isinstance(data["treeVersion"], str)
    assert _nullable(data["mainSkill"], str) and isinstance(data["mainGroup"], int)
    assert set(data["sets"]) == {"item", "skill", "spec", "multiple"}
    assert all(_nullable(data["sets"][key], str) for key in ("item", "skill", "spec"))
    assert isinstance(data["sets"]["multiple"], bool)
    assert set(data["points"]) == {"used", "available"}
    assert all(isinstance(data["points"][key], int) for key in ("used", "available"))
    _validate_nodes(data["nodes"])
    _validate_items(data["items"])
    _validate_groups(data["groups"])
    variables = [entry["var"] for entry in data["config"]]
    assert variables == sorted(variables)
    for entry in data["config"]:
        assert set(entry) == {"var", "label", "type", "value"}
        assert all(isinstance(entry[key], str) for key in ("var", "label", "type"))
        assert isinstance(entry["value"], (bool, int, float, str))
    assert set(data["handedness"]) == {"weapon1TwoHanded", "weapon2"}
    assert all(isinstance(value, bool) for value in data["handedness"].values())


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
