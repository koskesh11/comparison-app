"""The damage chain (decisions 009, 023): PoB's Calcs rows, cell text and popup sources for the main skill.

The Worb numbers are the approved mockup's (decision 009; PoB 2.67.2, Pinnacle Boss), so the chain shows what the owner
approved. A PoB update may move them: re-measure, keep the shape of the test.
"""

import math

import pytest

from comparison_app.analysis.chain import Cell, Chain, Hit, SourceTable, SourceText, parse_chain, read_chain
from comparison_app.analysis.scenarios import Scenario
from comparison_app.app.present.numbers import show
from comparison_app.pob.endpoints import Endpoint
from comparison_app.pob.session import PobSession

WIRE = {
    "skill": "Winter Orb",
    "rows": [
        {
            "section": "HitDamage",
            "label": "Total Increased",
            "cells": [
                {
                    "column": "Cold",
                    "text": "628%",
                    "values": [{"key": "mod", "value": 628, "precision": 0}],
                    "sources": [
                        {"kind": "text", "lines": ["Base damage:"]},
                        {
                            "kind": "table",
                            "columns": [{"key": "displayValue", "label": "Value"}],
                            "rows": [{"value": 39}],
                        },
                    ],
                },
                {"text": "x 0", "values": [{"key": "ColdEffMult", "precision": 3}], "sources": []},
            ],
        }
    ],
    "hits": [{"byType": {"Cold": 45549.9, "Fire": 0}, "AverageHit": 222512.2, "CritEffect": 4.885}],
    "totals": {"TotalDPS": 1435203.8, "Life": math.inf},
}


def test_the_wire_becomes_typed_records() -> None:
    chain = parse_chain(WIRE)
    assert (chain.skill, chain.part, chain.hits, chain.totals) == (
        "Winter Orb",
        None,
        (Hit(None, {"Cold": 45549.9}, 222512.2, 4.885),),
        {"TotalDPS": 1435203.8, "Life": math.inf},
    )
    (row,) = chain.rows
    cold, single = row.cells
    assert (row.section, row.label, cold.column, cold.text, cold.values[0].value) == (
        "HitDamage",
        "Total Increased",
        "Cold",
        "628%",
        628.0,
    )
    assert cold.sources == (
        SourceText(("Base damage:",)),
        SourceTable(None, (("displayValue", "Value"),), ({"value": 39},)),
    )
    assert (single.column, single.values[0].value) == (None, None)


def cell(chain: Chain, label: str, column: str | None = None) -> Cell:
    (row,) = [row for row in chain.rows if row.label == label]
    (found,) = [cell for cell in row.cells if cell.column == column]
    return found


@pytest.mark.pob
def test_worbs_chain_shows_the_mockups_numbers(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    chain = read_chain(pob_session, Scenario.PINNACLE_BOSS)
    assert (chain.skill, chain.part) == ("Winter Orb", "Channelling")
    shown = {
        ("Added Min", "Cold"): "40",
        ("Added Max", "Cold"): "61",
        ("Total Increased", "All Types"): "386%",
        ("Total Increased", "Cold"): "628%",  # 386 + 628 = the mockup's 1,014 %
        ("Total More", "All Types"): "95%",
        ("Effective DPS Mod", "Cold"): "x 3.599",
        ("Skill Hit Damage", "Cold"): "36,416 to 54,684",
        ("Crit Chance", None): "93.39%",
        ("Crit Multiplier", None): "x 5.16",
        ("Hit Rate", None): "6.45",
    }
    assert {key: cell(chain, *key).text for key in shown} == shown
    (hit,) = chain.hits
    assert (hit.hand, list(hit.by_type)) == (None, ["Cold"])


@pytest.mark.pob
def test_an_attack_has_its_hit_per_hand(pob_session: PobSession, variant_xml: dict[str, str]) -> None:
    """PoB keeps an attack's hit per hand (output.MainHand, CalcOffence.lua:2017, 2179); the top level has none."""
    pob_session.load_build(variant_xml["Cyclone"], "Cyclone")
    chain = read_chain(pob_session, Scenario.PINNACLE_BOSS)
    assert chain.skill == "Cyclone"
    (hit,) = chain.hits  # one weapon attacks: no OH rows in PoB's Calcs tab
    assert (hit.hand, list(hit.by_type)) == ("MainHand", ["Physical"])
    assert hit.average_hit == cell(chain, "MH Average Hit", "All Types").values[0].value
    assert hit.crit_effect == cell(chain, "MH Crit Effect Mod").values[0].value
    assert hit.average_hit is not None and hit.average_hit > 0


@pytest.mark.pob
def test_sources_are_pobs_popup_rows(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    increased = cell(read_chain(pob_session, Scenario.PINNACLE_BOSS), "Total Increased", "Cold")
    (table,) = [source for source in increased.sources if isinstance(source, SourceTable)]
    taming = [row for row in table.rows if row.get("sourceName") == "The Taming, Prismatic Ring"]
    assert [row["value"] for row in taming] == [39, 39, 39]  # one per ailment on the enemy: the mockup's 3 x 39
    assert all(row["sourceId"].startswith("Item:") for row in taming)


@pytest.mark.pob
@pytest.mark.parametrize("name", ["Worb", "CoC EK Assa", "Cyclone"])
def test_the_calcs_tab_on_the_main_skill_gives_the_sidebars_numbers(
    pob_session: PobSession, reference_xml: dict[str, str], variant_xml: dict[str, str], name: str
) -> None:
    """Decision 023's premise: pointed at the main skill, the Calcs tab's calculation equals the sidebar's."""
    pob_session.load_build({**reference_xml, **variant_xml}[name], name)
    chain = read_chain(pob_session, Scenario.PINNACLE_BOSS)
    sidebar = pob_session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": "Pinnacle"})["stats"]
    for key in ("TotalDPS", "CritChance", "Speed", "HitChance", "FullDPS"):
        assert chain.totals[key] == sidebar[key], key


@pytest.mark.pob
@pytest.mark.parametrize("name", ["Worb", "CoC EK Assa", "Cyclone"])
def test_every_cells_numbers_are_its_text(
    pob_session: PobSession, reference_xml: dict[str, str], variant_xml: dict[str, str], name: str
) -> None:
    """A cell's raw numbers, shown with PoB's rule and the cell's precision, are its text, in order (a missing output
    shows as 0, CalcFormat.lua:28-32). Card 109 groups the raw numbers: a wrong one must not hide behind right text."""
    pob_session.load_build({**reference_xml, **variant_xml}[name], name)
    wrong = []
    for row in read_chain(pob_session, Scenario.PINNACLE_BOSS).rows:
        for found in row.cells:
            rest = found.text
            for value in found.values:
                shown = show(0.0 if value.value is None else value.value, rule="pob", precision=value.precision)
                at = rest.find(shown)
                if at < 0:
                    wrong.append((row.label, found.column, found.text, value))
                    break
                rest = rest[at + len(shown) :]
    assert wrong == []


@pytest.mark.pob
def test_the_scenario_changes_the_chain(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    pinnacle = cell(read_chain(pob_session, Scenario.PINNACLE_BOSS), "Effective DPS Mod", "Cold").values[0].value
    standard = cell(read_chain(pob_session, Scenario.STANDARD_BOSS), "Effective DPS Mod", "Cold").values[0].value
    assert pinnacle is not None and standard is not None and standard > pinnacle
