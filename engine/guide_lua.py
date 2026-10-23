"""Python calls into the guide-aware PoB Lua helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from pobhost import PobEngine, _lua_str


def ensure_loaded(engine: PobEngine) -> None:
    """Load audit.lua once; it also loads all guide helpers."""
    loaded = engine.run("return type(snapshotJSON)")
    if loaded != "function":
        engine.run("dofile(ENGINE_DIR .. '/audit.lua')")


def _call(engine: PobEngine, function: str, request: Any = None, *, decode: bool = True) -> Any:
    ensure_loaded(engine)
    argument = _lua_str(json.dumps(request)) if request is not None else ""
    result = engine.run(f"return {function}({argument})")
    return json.loads(result) if decode else result


def load_guide(engine: PobEngine, xml_path: str | Path, label: str = "Guide") -> dict:
    """Load an XML build as the lightweight comparison entry."""
    return _call(engine, "guideLoadJSON", {"xmlPath": Path(xml_path).as_posix(), "label": label})


def release_guide(engine: PobEngine) -> None:
    """Release the comparison entry and collect its large Lua heap."""
    result = _call(engine, "guideReleaseJSON", decode=False)
    if result != "ok":
        raise RuntimeError(f"guide release failed: {result}")


def snapshot(engine: PobEngine, which: str) -> dict:
    """Return snapshot schema v1 for the player or loaded guide."""
    return _call(engine, "snapshotJSON", {"which": which})


def tree_info(engine: PobEngine, ids: Iterable[int], remove_ids: Iterable[int] = ()) -> dict:
    """Return PoB path/depends data for player-tree node IDs."""
    return _call(engine, "treeInfoJSON", {"ids": list(ids), "removeIds": list(remove_ids)})


def probe(engine: PobEngine) -> dict:
    """Probe the installed PoB comparison APIs with a real tiny run."""
    return _call(engine, "probeJSON")


def guide_power(engine: PobEngine, categories: Iterable[str] | None = None) -> list[dict]:
    """Return PoB ComparePowerBuilder rows for the loaded guide."""
    request = {} if categories is None else {"categories": list(categories)}
    return _call(engine, "guidePowerJSON", request)


def evaluate_with(engine: PobEngine, request: dict) -> dict:
    """Evaluate nodes plus optional temporary item or gem changes."""
    return _call(engine, "evaluateJSON", request)


def apply_changes(engine: PobEngine, changes: list[dict], stats: list[str],
                  build_name: str | None = None) -> dict:
    """Apply persistent changes and return calculation context plus XML."""
    request = {"changes": changes, "stats": stats}
    if build_name is not None:
        request["buildName"] = build_name
    return _call(engine, "applyChangesJSON", request)
