"""Config-row evaluation and conditional zero-row re-tests."""

from display import fmt_pct
from guide_check_eval import config_applied, evaluate_change
from guide_check_result import build_result, is_zero


def evaluate_config(auditor, config_row: dict, base_ctx: dict) -> dict:
    change = config_row.get("change")
    built = {**config_row, "tickable": False,
             "note": "Only if this applies to you in game."}
    if not change:
        return {**built, "result": None}
    with config_applied(auditor, change.get("vars") or {}):
        ctx = auditor.base_context()
        result, _dims, _breaks = build_result(auditor, base_ctx, ctx)
    return {**built, "result": result}


def _changed_under(auditor, row: dict, base_ctx: dict) -> tuple[bool, dict]:
    ctx = evaluate_change(auditor, row["change"])
    result, dims, breaks = build_result(auditor, base_ctx, ctx)
    return not is_zero(result, dims, breaks), result


def _conditional_text(result: dict, labels: list[str]) -> str:
    delta = result["delta"]
    dps, ehp = delta.get("dpsPct"), delta.get("ehpPct")
    value, name = (dps, "DPS") if (dps or 0) >= (ehp or 0) else (ehp, "EHP")
    return f"PoB shows {fmt_pct(value)} {name} only with: {', '.join(labels)}"


def retest_zero_rows(auditor, rows: list[dict], config_rows: list[dict]) -> None:
    testable = [row for row in config_rows if row.get("change")]
    if not rows or not testable:
        return
    combined = {}
    for config in testable:
        combined.update(config["change"].get("vars") or {})
    with config_applied(auditor, combined):
        base_cfg = auditor.base_context()
        changed = [(row, result) for row in rows
                   for nonzero, result in [_changed_under(auditor, row, base_cfg)] if nonzero]
    responsible = _responsible(auditor, changed, testable)
    for row, result in changed:
        labels = responsible[row["id"]]
        delta = result["delta"]
        row["conditional"] = {"text": _conditional_text(result, labels),
                              "dpsPct": delta.get("dpsPct"), "ehpPct": delta.get("ehpPct"),
                              "settings": labels}


def _responsible(auditor, changed: list[tuple[dict, dict]],
                 config_rows: list[dict]) -> dict[str, list[str]]:
    labels = {row["id"]: [] for row, _result in changed}
    for config in config_rows:
        with config_applied(auditor, config["change"].get("vars") or {}):
            base = auditor.base_context()
            for row, _combined_result in changed:
                nonzero, _result = _changed_under(auditor, row, base)
                if nonzero:
                    labels[row["id"]].append(config["label"])
    fallback = [config["label"] for config in config_rows]
    return {ident: values or fallback for ident, values in labels.items()}
