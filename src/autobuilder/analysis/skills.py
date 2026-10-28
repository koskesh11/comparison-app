"""Which DPS the header shows, PoB's Full DPS list and a change in percent (rewrites the first app's engine/scoring.py
:1-43; task 102 area B verdict: typed NoMainSkill instead of a bare StopIteration, no nan or inf change).

The header shows PoB's FullDPS. A build with no skill group in Full DPS ("Include in Full DPS" unticked) has FullDPS 0;
then it shows the main skill's CombinedDPS and says so.
"""

import math
from dataclasses import dataclass

from autobuilder.analysis.scenarios import BOSS_BOX, Scenario
from autobuilder.errors import NoMainSkill
from autobuilder.pob.endpoints import Endpoint
from autobuilder.pob.session import BuildSummary, PobSession, SkillDps


@dataclass(frozen=True)
class HeaderDps:
    key: str  # the PoB output key shown: FullDPS or CombinedDPS
    value: float | None
    warning: str | None


def read_summary(session: PobSession, scenario: Scenario, which: str = "own") -> BuildSummary:
    """The summary of the open build or the target under the scenario; both are unchanged afterwards (M6)."""
    reply = session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": BOSS_BOX[scenario], "which": which})
    return BuildSummary.from_wire(reply)


def header_dps(summary: BuildSummary) -> HeaderDps:
    full = summary.stats.get("FullDPS")
    if full is not None and full > 0:
        return HeaderDps("FullDPS", full, None)
    if summary.main_skill is None:
        raise NoMainSkill("the build has no main skill in its sidebar")
    warning = (
        "No skill group is in Full DPS ('Include in Full DPS' unticked): "
        f"the DPS shown is the main skill {summary.main_skill} only"
    )
    return HeaderDps("CombinedDPS", summary.stats.get("CombinedDPS"), warning)


def skill_rows(summary: BuildSummary) -> tuple[SkillDps, ...]:
    """PoB's Full DPS list, the biggest share (dps x count) first."""
    return tuple(sorted(summary.skill_dps, key=lambda row: (-row.dps * row.count, row.name, row.part or "")))


def change_pct(new: float, old: float) -> float | None:
    """The change from old to new in percent; None where it has no number (old 0, inf or NaN, new not finite)."""
    if old == 0 or not math.isfinite(old) or not math.isfinite(new):
        return None
    return 100 * (new - old) / old
