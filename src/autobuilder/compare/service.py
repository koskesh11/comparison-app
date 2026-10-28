"""Your build against a target in one PoB (card 109, decision 009): both opened as saved, both read under the same
scenario, the chain side by side and the warnings that say where PoB's numbers here and the owner's PoB differ.

The target is PoB's CompareEntry beside your build (compare/target.py) and is released on every path.
"""

from dataclasses import dataclass

from autobuilder.analysis.chain import Chain, Which, read_chain
from autobuilder.analysis.scenarios import Scenario
from autobuilder.analysis.session import OpenedBuild, open_build
from autobuilder.analysis.skills import HeaderDps, header_dps, read_summary
from autobuilder.compare.chain_table import build_table
from autobuilder.compare.target import open_target, release_target
from autobuilder.compare.types import ChainTable
from autobuilder.pob.session import BuildSummary, PobSession

CALCS_ELSEWHERE = (
    "Your PoB Calcs tab is set to another skill than the sidebar's main skill. The chain here is the main skill's, so "
    "PoB's Calcs tab shows other numbers until you point it at the main skill."
)
TARGET_PARTY = (
    "The target has party buffs saved in PoB's Party tab. PoB's build comparison leaves them out, so the target's "
    "numbers here are without them."
)


@dataclass(frozen=True)
class Side:
    opened: OpenedBuild  # as saved
    summary: BuildSummary  # under the scenario
    dps: HeaderDps
    chain: Chain


@dataclass(frozen=True)
class Comparison:
    scenario: Scenario
    yours: Side
    target: Side
    table: ChainTable
    warnings: tuple[str, ...]


def _side(session: PobSession, opened: OpenedBuild, scenario: Scenario, which: Which) -> Side:
    summary = read_summary(session, scenario, which)
    return Side(opened, summary, header_dps(summary), read_chain(session, scenario, which))


def _warnings(yours: Side, target: Side) -> tuple[str, ...]:
    found = [CALCS_ELSEWHERE] if yours.opened.summary.calcs_on_main_skill is False else []
    if target.opened.summary.uses_party:
        found.append(TARGET_PARTY)
    found.extend(
        f"{name}: {side.dps.warning}" for name, side in (("You", yours), ("Target", target)) if side.dps.warning
    )
    return tuple(found)


def compare(session: PobSession, yours: tuple[str, str], target: tuple[str, str], scenario: Scenario) -> Comparison:
    """`yours` and `target` are (XML text, name). Your build stays open afterwards; the target does not."""
    opened_yours = open_build(session, *yours)
    opened_target = open_target(session, *target)
    try:
        mine = _side(session, opened_yours, scenario, "own")
        theirs = _side(session, opened_target, scenario, "target")
    finally:
        release_target(session)
    return Comparison(scenario, mine, theirs, build_table(mine.chain, theirs.chain), _warnings(mine, theirs))
