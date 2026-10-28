"""Your build against a target in one PoB (card 109, decision 009): both opened as saved, both read under the same
scenario, the chain side by side and the warnings that say where PoB's numbers here and the owner's PoB differ. The
chain is shown only when both main skills are set up alike (decision 011); the config differences come with it
(decision 010).

The target is PoB's CompareEntry beside your build (compare/target.py) and is released on every path.
"""

from dataclasses import dataclass

from comparison_app.analysis.chain import Chain, Which, read_chain
from comparison_app.analysis.scenarios import Scenario
from comparison_app.analysis.session import OpenedBuild, open_build
from comparison_app.analysis.skills import HeaderDps, header_dps, read_summary
from comparison_app.compare.chain_table import build_table
from comparison_app.compare.diff.context import ConfigReport, compare_config
from comparison_app.compare.skill_settings import Match, SkillSettings, compare_settings
from comparison_app.compare.snapshot import Snapshot, read_snapshot
from comparison_app.compare.target import open_target, release_target
from comparison_app.compare.types import ChainTable
from comparison_app.pob.session import BuildSummary, PobSession

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
    snapshot: Snapshot  # skill settings and config, as saved


@dataclass(frozen=True)
class Comparison:
    scenario: Scenario
    yours: Side
    target: Side
    settings: SkillSettings
    table: ChainTable | None  # None until both main skills are set up alike (decision 011); settings says why
    config: ConfigReport
    warnings: tuple[str, ...]


def _side(session: PobSession, opened: OpenedBuild, scenario: Scenario, which: Which) -> Side:
    summary = read_summary(session, scenario, which)
    chain = read_chain(session, scenario, which)
    return Side(opened, summary, header_dps(summary), chain, read_snapshot(session, which))


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
    try:
        opened_target = open_target(session, *target)
        mine = _side(session, opened_yours, scenario, "own")
        theirs = _side(session, opened_target, scenario, "target")
    finally:
        release_target(session)
    settings = compare_settings(mine.snapshot, theirs.snapshot)
    table = build_table(mine.chain, theirs.chain) if settings.match is Match.SAME else None
    config = compare_config(mine.snapshot, theirs.snapshot)
    return Comparison(scenario, mine, theirs, settings, table, config, _warnings(mine, theirs))
