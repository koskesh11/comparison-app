"""The damage chain of one build as typed records (decisions 009, 023; the Lua side is pob/lua/analysis/chain.lua).

Every row, cell text and source is PoB's own: a row of a Calcs tab section in PoB's order, a cell's text as the Calcs
tab shows it, the raw numbers behind that text, and the sources PoB's hover popup lists. A number PoB did not compute
is None.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from comparison_app.analysis.scenarios import BOSS_BOX, Scenario
from comparison_app.pob import wire
from comparison_app.pob.endpoints import Endpoint
from comparison_app.pob.session import PobSession

Which = Literal["own", "target"]  # the build open in PoB, or the target beside it (compare/target.py)


@dataclass(frozen=True)
class Value:
    key: str  # the PoB output key the text shows, or "mod" for a sum of modifiers
    value: float | None
    precision: int  # the decimals PoB shows it at (the cell format's {p:...})


@dataclass(frozen=True)
class SourceText:
    lines: tuple[str, ...]  # PoB's breakdown lines, colour codes removed


@dataclass(frozen=True)
class SourceTable:
    label: str | None
    columns: tuple[tuple[str, str], ...]  # (key, label) as PoB's popup names them
    rows: tuple[Mapping[str, Any], ...]  # text per column key; mod rows also carry `value` and `sourceId`


@dataclass(frozen=True)
class Cell:
    column: str | None  # the damage type column of Skill Hit Damage ("Cold", "All Types"); None in one-column rows
    text: str
    values: tuple[Value, ...]
    sources: tuple[SourceText | SourceTable, ...]


@dataclass(frozen=True)
class Row:
    section: str  # PoB's Calcs section id: HitDamage, Speed, Crit, HitChance
    label: str
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class Hit:
    """One hit of the main skill: once for a spell, per attacking hand for an attack (PoB keeps those per hand)."""

    hand: str | None  # "MainHand" or "OffHand" for an attack, None otherwise
    by_type: Mapping[str, float]  # average non-crit hit per damage type; types with no hit are left out
    average_hit: float | None  # crits included
    crit_effect: float | None


@dataclass(frozen=True)
class Chain:
    skill: str
    part: str | None
    rows: tuple[Row, ...]
    hits: tuple[Hit, ...]
    totals: Mapping[str, float]  # TotalDPS, Speed, CritChance, ... (both hands combined) and FullDPS (the sidebar's)


def _source(data: object) -> SourceText | SourceTable:
    item = wire.table(data)
    if item.get("kind") == "text":
        return SourceText(tuple(str(line) for line in item.get("lines") or ()))
    columns = tuple((str(column["key"]), str(column["label"])) for column in item.get("columns") or ())
    rows = tuple(wire.table(row) for row in item.get("rows") or ())
    return SourceTable(wire.text(item.get("label")), columns, rows)


def _value(data: object) -> Value:
    item = wire.table(data)
    return Value(str(item["key"]), wire.number(item.get("value")), int(item.get("precision") or 0))


def _cell(data: object) -> Cell:
    item = wire.table(data)
    values = tuple(_value(value) for value in item["values"])
    sources = tuple(_source(source) for source in item.get("sources") or ())
    return Cell(wire.text(item.get("column")), str(item["text"]), values, sources)


def _numbers(data: object) -> dict[str, float]:
    numbers = {key: wire.number(value) for key, value in wire.table(data).items()}
    return {key: value for key, value in numbers.items() if value is not None}


def _hit(data: object) -> Hit:
    item = wire.table(data)
    by_type = {key: value for key, value in _numbers(item.get("byType")).items() if value != 0}
    average, effect = wire.number(item.get("AverageHit")), wire.number(item.get("CritEffect"))
    return Hit(wire.text(item.get("hand")), by_type, average, effect)


def parse_chain(data: object) -> Chain:
    item = wire.table(data)
    rows = tuple(
        Row(str(row["section"]), str(row["label"]), tuple(_cell(cell) for cell in row.get("cells") or ()))
        for row in (wire.table(raw) for raw in item.get("rows") or ())
    )
    hits = tuple(_hit(hit) for hit in item.get("hits") or ())
    return Chain(str(item["skill"]), wire.text(item.get("part")), rows, hits, _numbers(item.get("totals")))


def read_chain(session: PobSession, scenario: Scenario, which: Which = "own") -> Chain:
    """The chain of the open build or the target beside it, under the scenario; both are unchanged afterwards (M6)."""
    return parse_chain(session.call(Endpoint.ANALYSIS_CHAIN, {"boss": BOSS_BOX[scenario], "which": which}))
