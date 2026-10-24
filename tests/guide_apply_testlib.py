"""Complete guide-check result fixtures built from real snapshot differences."""

import json
from pathlib import Path

import guide_diff


def fake_result(rows=None):
    fixtures = Path(__file__).resolve().parent / "fixtures" / "snapshots"
    player = json.loads((fixtures / "ek_player.json").read_text(encoding="utf-8"))
    guide = json.loads((fixtures / "pobb_guide.json").read_text(encoding="utf-8"))
    found = guide_diff.diff(player, guide, None)
    ranked = list(rows) if rows is not None else [
        {**row, "rank": index, "result": None, "chips": [], "locked": False}
        for index, row in enumerate(found["rows"], 1)
    ]
    locked_source = found["rows"][0]
    ranked += [
        {**locked_source, "id": "locked:unobtainable", "label": "Unavailable row",
         "rank": None, "result": None, "chips": ["unobtainable"], "locked": True,
         "lockReason": "unobtainable"},
        {**locked_source, "id": "locked:rule", "label": "Rule row",
         "rank": None, "result": None, "chips": ["breaks a rule"], "locked": True,
         "lockReason": "breaks a rule"},
    ]
    return {
        "state": "differences", "header": {}, "rows": ranked, "noChange": [],
        "config": found["config"], "notTested": found["notTested"],
        "counts": {"found": len(ranked), "tested": len(ranked),
                   "notTested": len(found["notTested"]), "noChange": 0},
        "sha": "sha", "playerPath": "player.xml", "perf": {},
        "sorts": {"best": [], "dps": [], "ehp": []},
    }
