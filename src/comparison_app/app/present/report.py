"""The report the page draws: a Comparison mapped to JSON by hand, so every shape is visible and tested (interfaces.md
4.9; M5: tests/comparison_app/test_golden_has_all_keys.py checks KEYS against fixtures/golden_report.json).

Keys are camelCase. A missing or non-finite number is null; the page shows PoB's text, and formats raw numbers with
the shared rules (decision 020, M4). The sentences come from where the values are compared (S8): compare/service.py,
compare/skill_settings.py, compare/diff/context.py, compare/stages.py.
"""

import math
from collections.abc import Iterable, Mapping
from typing import Any

from comparison_app.analysis.chain import Cell, SourceTable, SourceText
from comparison_app.compare.diff.context import ConfigDifference, ConfigReport, LooksWrong
from comparison_app.compare.service import Comparison, Side
from comparison_app.compare.skill_settings import Setup, SkillSettings
from comparison_app.compare.snapshot import ConfigBox, CustomMods
from comparison_app.compare.types import ChainTable, Pair, Step


def number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        return None
    return float(value)


def _source(source: SourceText | SourceTable) -> dict[str, Any]:
    if isinstance(source, SourceText):
        return {"kind": "text", "lines": list(source.lines)}
    rows = [{key: number(value) if key == "value" else value for key, value in row.items()} for row in source.rows]
    return {
        "kind": "table",
        "label": source.label,
        "columns": [list(column) for column in source.columns],
        "rows": rows,
    }


def _cell(cell: Cell | None) -> dict[str, Any] | None:
    if cell is None:
        return None
    return {
        "text": cell.text,
        "values": [{"key": v.key, "value": number(v.value), "precision": v.precision} for v in cell.values],
        "sources": [_source(source) for source in cell.sources],
    }


def _pair(pair: Pair) -> dict[str, Any]:
    return {"column": pair.column, "yours": _cell(pair.yours), "target": _cell(pair.target)}


def _step(step: Step) -> dict[str, Any]:
    return {
        "section": step.section,
        "label": step.label,
        "hand": step.hand,
        "gap": number(step.gap),
        "derived": step.derived,
        "factors": [[column, number(mine), number(theirs)] for column, mine, theirs in step.factors],
        "cells": [_pair(pair) for pair in step.cells],
    }


def _table(table: ChainTable | None) -> dict[str, Any] | None:
    if table is None:
        return None
    return {
        "steps": [_step(step) for step in table.steps],
        "small": {"steps": [_step(step) for step in table.small.steps], "total": number(table.small.total)},
        "noEffect": [_step(step) for step in table.no_effect],
        "chips": [{"label": step.label, "hand": step.hand, "gap": number(step.gap)} for step in table.chips],
        "shares": {kind: number(share) for kind, share in table.shares.items()},
    }


def _side(side: Side) -> dict[str, Any]:
    summary = side.opened.summary
    return {
        "name": side.opened.name,
        "sha256": side.opened.sha256,
        "className": summary.class_name,
        "ascendancy": summary.ascendancy,
        "level": number(summary.level),
        "pobVersion": summary.pob_version,
        "skill": side.chain.skill,
        "part": side.chain.part,
        "dps": {"key": side.dps.key, "value": number(side.dps.value), "warning": side.dps.warning},
    }


def _setup(setup: Setup | None) -> dict[str, Any] | None:
    if setup is None:
        return None
    return {
        "group": setup.group,
        "skillIndex": setup.skill_index,
        "skill": setup.skill,
        "part": setup.part,
        "stages": number(setup.stages),
        "mines": number(setup.mines),
        "minion": setup.minion,
        "minionSkill": number(setup.minion_skill),
        "count": number(setup.count),
        "groupCount": number(setup.group_count),
    }


def _settings(settings: SkillSettings) -> dict[str, Any]:
    return {
        "match": settings.match.value,
        "message": settings.message,
        "differing": list(settings.differing),
        "targetChoices": [{"group": group, "skill": skill} for group, skill in settings.target_choices],
        "yours": _setup(settings.yours),
        "target": _setup(settings.target),
    }


def _value(value: object) -> object:
    return number(value) if isinstance(value, int | float) and not isinstance(value, bool) else value


def _box(box: ConfigBox | None) -> dict[str, Any] | None:
    if box is None:
        return None
    return {"value": _value(box.value), "placeholder": _value(box.placeholder), "state": box.state}


def _difference(difference: ConfigDifference) -> dict[str, Any]:
    return {
        "var": difference.var,
        "section": difference.section,
        "label": difference.label,
        "note": difference.note,
        "yours": _box(difference.yours),
        "target": _box(difference.target),
    }


def _looks_wrong(item: LooksWrong) -> dict[str, Any]:
    return {"whose": item.whose, "var": item.box.var, "label": item.box.label, "message": item.message}


def _mods(blocks: Iterable[CustomMods]) -> list[dict[str, Any]]:
    return [{"title": block.title, "text": block.text} for block in blocks]


def _config(config: ConfigReport) -> dict[str, Any]:
    return {
        "differences": [_difference(item) for item in config.differences],
        "looksWrong": [_looks_wrong(item) for item in config.looks_wrong],
        "customModsYours": _mods(config.custom_mods_yours),
        "customModsTarget": _mods(config.custom_mods_target),
        "configSets": list(config.config_sets) if config.config_sets else None,
    }


def report(comparison: Comparison) -> dict[str, Any]:
    return {
        "scenario": comparison.scenario.value,
        "yours": _side(comparison.yours),
        "target": _side(comparison.target),
        "settings": _settings(comparison.settings),
        "table": _table(comparison.table),
        "config": _config(comparison.config),
        "warnings": list(comparison.warnings),
    }


def key_paths(value: object, prefix: str = "") -> set[str]:
    """Every key path in a report: "a.b" for objects, "a[]" for list items; sources' rows keep their own keys."""
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found.add(path)
            if not path.endswith(".rows"):  # a source table's rows carry PoB's own column names
                found |= key_paths(item, path)
    elif isinstance(value, list):
        for item in value:
            found |= key_paths(item, f"{prefix}[]")
    return found
