"""Decision 011's button (compare/recalc.py): which changes make your main skill match the target's, and the request
they become. M7 (test_recalc_matches_apply.py) checks each change kind against a saved build."""

from typing import Any

from comparison_app.analysis.scenarios import Scenario
from comparison_app.compare.recalc import NOT_TESTED, Change, changes_to_match, recalculate
from comparison_app.compare.skill_settings import compare_settings
from comparison_app.compare.snapshot import ActiveSkill, Gem, Group, Snapshot
from comparison_app.pob.endpoints import ChangeKind, Endpoint


def orb(
    stages: float | None, part: float, count: float = 1, group_count: float | None = None, max_stages: float = 11
) -> Snapshot:
    gem = Gem("Winter Orb", False, True, 20, 20, count, part, stages, None, None, None)
    support = Gem("Focused Channelling", True, True, 20, 20, 1, None, None, None, None, None)
    names = {1: "Channelling", 2: "Release"}
    group = Group(
        1,
        "Winter Orb",
        True,
        True,
        group_count,
        1,
        (support, gem),
        (ActiveSkill("Winter Orb", 2, names[part], max_stages),),
    )
    return Snapshot(1, 1, (group,), (), (), ("Default",), "Default")


def test_your_main_skill_is_set_to_the_targets_setting() -> None:
    yours, target = orb(stages=11, part=1), orb(stages=5, part=2, group_count=2)
    changes = changes_to_match(compare_settings(yours, target), yours, target)
    assert changes == (
        Change(ChangeKind.SKILL_PART, 1, 2, 2),  # the part's index, on your Winter Orb (group 1, gem 2)
        Change(ChangeKind.STAGE_COUNT, 1, 2, 5),
        Change(ChangeKind.GROUP_COUNT, 1, None, 2),
    )


def test_the_button_copies_the_targets_effective_stage_count() -> None:
    """Both stage boxes empty, but your Winter Orb has 13 stages at most (an enchant) and the target's 11: the empty
    boxes differ as PoB applies them, so the button sets 11, not "empty" again (review 111, finding 2)."""
    yours, target = orb(stages=None, part=1, max_stages=13), orb(stages=None, part=1, max_stages=11)
    settings = compare_settings(yours, target)
    assert (settings.differing, changes_to_match(settings, yours, target)) == (
        ("stages",),
        (Change(ChangeKind.STAGE_COUNT, 1, 2, 11),),
    )


def test_no_change_when_the_settings_match_or_the_skills_differ() -> None:
    same = orb(stages=11, part=1)
    assert changes_to_match(compare_settings(same, same), same, same) == ()
    other = Snapshot(1, 1, (), (), (), ("Default",), "Default")
    assert changes_to_match(compare_settings(same, other), same, other) == ()


class Session:
    """Stands in for PobSession: keeps the request, answers with an empty chain."""

    def __init__(self) -> None:
        self.requests: list[tuple[Endpoint, Any]] = []

    def call(self, endpoint: Endpoint, payload: Any) -> Any:
        self.requests.append((endpoint, payload))
        return {"chain": {"skill": "Winter Orb", "rows": [], "hits": [], "totals": {}}, "output": {"FullDPS": 5.0}}


def test_the_request_names_each_change_and_a_change_not_checked_says_why() -> None:
    session = Session()
    changes = [Change(ChangeKind.MINE_COUNT, 3, 1, None), Change(ChangeKind.GROUP_COUNT, 3, None, 2)]
    result = recalculate(session, Scenario.UBER_PINNACLE_BOSS, changes)  # type: ignore[arg-type]
    assert session.requests == [
        (
            Endpoint.COMPARE_CHAIN_WITH,
            {
                "boss": "Uber",
                "which": "own",
                "changes": [
                    {"kind": "gem.mine_count", "group": 3, "gem": 1},  # no value: the field is unset
                    {"kind": "group.count", "group": 3, "value": 2},
                ],
            },
        )
    ]
    assert (result.output, result.not_tested) == ({"FullDPS": 5.0}, (NOT_TESTED[ChangeKind.MINE_COUNT],))
