"""Translate guide changes into temporary or restored PoB evaluations."""

from __future__ import annotations

import json
from contextlib import contextmanager

import guide_lua
from pobhost import ENGINE_DIR, _lua_str


def _request(auditor, extra: dict | None = None) -> dict:
    values = {"removeNodes": [], "addNodes": [], "stats": auditor.keys,
              "extraSkills": auditor.extra_request()}
    if auditor.multi_part:
        values["partVariants"] = True
    values.update(extra or {})
    return values


def _item(change: dict) -> dict:
    value = {"slot": change.get("slot"), "raw": change.get("raw"),
             "jewels": change.get("abyssJewels") or []}
    if change.get("flaskActive") is not None:
        value["flaskActive"] = change["flaskActive"]
    return value


def _simple_extra(change: dict) -> dict | None:
    kind = change.get("type")
    if kind == "alloc":
        return {"addNodes": change.get("nodes") or []}
    if kind == "dealloc":
        return {"removeNodes": change.get("nodes") or []}
    if kind == "item":
        return {"repItem": _item(change)}
    if kind in {"gemLevel", "addSupport", "replaceSupport", "addGroup"}:
        return {"gemChange": change}
    if kind != "compound":
        return None
    changes = change.get("changes") or []
    items = [value for value in changes if value.get("type") == "item"]
    allocations = [value for value in changes if value.get("type") == "alloc"]
    if len(items) <= 1 and len(items) + len(allocations) == len(changes):
        nodes = sorted({node for value in allocations for node in value.get("nodes") or []})
        result = {"addNodes": nodes}
        if items:
            result["repItem"] = _item(items[0])
        return result
    return None


@contextmanager
def models_not_applied(auditor):
    """Spec 5B: vault Models are named, not applied. Rows show PoB's own number; the models stay readable."""
    kept = auditor.models
    auditor.models, auditor.named_models = [], kept
    try:
        yield
    finally:
        auditor.models = kept


def named_models(auditor, ctx: dict) -> list[dict]:
    """The main skill's vault Models with the hits they would give (for the note only, never in a number)."""
    from models import apply_models
    modelled = apply_models(getattr(auditor, "named_models", []), ctx, auditor.equipped)
    return auditor.main_models(modelled)


def restore_player(auditor) -> None:
    auditor.engine.load_build(auditor.build_path)
    auditor.load_audit_hooks(list(auditor.disabled_skills))
    auditor.engine.run("collectgarbage('collect'); collectgarbage('collect')")


def _apply_path(auditor, change: dict) -> dict:
    request = _request(auditor)
    request["changes"] = change.get("changes") if change.get("type") == "compound" else [change]
    command = "return applyChangesJSON(" + _lua_str(json.dumps(request)) + ")"
    try:
        result = json.loads(auditor.engine.run(command))
        return auditor.adjust(result["ctx"])
    finally:
        restore_player(auditor)


def evaluate_change(auditor, change: dict) -> dict:
    extra = _simple_extra(change)
    if extra is None:
        return _apply_path(auditor, change)
    return auditor.adjust(guide_lua.evaluate_with(auditor.engine, _request(auditor, extra)))


def _score(auditor, ctx: dict, base_ctx: dict) -> float:
    dims = auditor.dimensions(ctx, base_ctx)
    return max(dims.get("dps") or 0, dims.get("ehp") or 0)


def evaluate_options(auditor, row: dict, base_ctx: dict) -> tuple[dict, dict]:
    options = (row.get("info") or {}).get("options") or []
    if len(options) <= 1:
        change = options[0] if options else row["change"]
        return evaluate_change(auditor, change), change
    values = []
    for index, change in enumerate(options):
        ctx = evaluate_change(auditor, change)
        values.append((bool(auditor.breaks(ctx)), -_score(auditor, ctx, base_ctx), index, ctx, change))
    if any(not value[0] for value in values):
        values = [value for value in values if not value[0]]
    _, _, _, ctx, change = min(values, key=lambda value: value[:3])
    return ctx, change


def _swap(engine, values: dict) -> dict:
    engine.run("if guideConfigSwapJSON == nil then "
               "dofile(ENGINE_DIR .. '/guide_check_config.lua') end")
    request = {"values": {key: value for key, value in values.items() if value is not None},
               "clear": sorted(key for key, value in values.items() if value is None)}
    result = engine.run("return guideConfigSwapJSON(" + _lua_str(json.dumps(request)) + ")")
    return json.loads(result)


@contextmanager
def config_applied(auditor, variables: dict):
    restore = _swap(auditor.engine, variables)
    try:
        yield
    finally:
        values = dict(restore.get("values") or {})
        values.update({key: None for key in restore.get("clear") or []})
        _swap(auditor.engine, values)


def lua_mb(engine) -> float:
    value = engine.run("collectgarbage('collect'); collectgarbage('collect'); "
                       "return tostring(collectgarbage('count') / 1024)")
    return float(value)
