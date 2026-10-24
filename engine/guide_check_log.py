"""Privacy-limited runlog event for a completed guide check."""

import json
from collections import Counter
from pathlib import Path

import runlog


def _node_rows(result: dict, powers: list[dict]) -> list[dict]:
    by_id = {value.get("nodeId"): value for value in powers}
    rows = []
    for row in result["rows"] + result["noChange"]:
        info = row.get("info") or {}
        if row.get("category") != "tree-add" or (info.get("pathNodes") or 0) <= 0:
            continue
        power = by_id.get(info.get("node") or (row.get("change") or {}).get("target"))
        if power:
            rows.append({"id": row["id"], "shown": row["result"]["delta"]["dpsPct"],
                         "nodeAlone": power.get("impactPercent") or 0})
    return rows


def log_check(result: dict, guide_path, player_name: str, *, source=None, job_id=None,
              node_powers=None) -> None:
    all_rows = result["rows"] + result["noChange"] + result["notTested"]
    categories = Counter(row.get("category") for row in all_rows)
    node_alone = _node_rows(result, node_powers or [])
    counts, perf = result["counts"], result["perf"]
    payload = {"source": source or None,
               "bytes": {"player": Path(result["playerPath"]).stat().st_size,
                         "guide": Path(guide_path).stat().st_size},
               "rowsPerCategory": dict(sorted(categories.items())),
               "found": counts["found"], "tested": counts["tested"],
               "notTested": counts["notTested"], "noChange": counts["noChange"],
               "settings": counts["settings"], "timeLimit": perf["timeLimit"],
               "seconds": perf["seconds"], "nodeAlone": node_alone}
    runlog.log_event("INFO", "guide_check", json.dumps(payload, sort_keys=True),
                     job_id=job_id, build=player_name)
