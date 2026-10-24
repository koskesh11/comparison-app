"""Deterministic guide-check scoring and sorts."""

from audit import NO_WORSE_PCT
from guide_diff_common import CATEGORY_ORDER


def _pct(row: dict, key: str) -> float:
    value = ((row.get("result") or {}).get("delta") or {}).get(key)
    return value if isinstance(value, (int, float)) else 0.0


def score(row: dict) -> float:
    return max(_pct(row, "dpsPct"), _pct(row, "ehpPct"))


def is_tradeoff(row: dict) -> bool:
    """One axis goes down (same threshold as the row's "trade-off" chip)."""
    return min(_pct(row, "dpsPct"), _pct(row, "ehpPct")) < NO_WORSE_PCT


def _ties(row: dict) -> tuple:
    order = {name: index for index, name in enumerate(CATEGORY_ORDER)}
    return (order.get(row.get("category"), len(order)),
            str(row.get("label") or "").casefold(), str(row.get("id") or ""))


def _ids(rows: list[dict], key, pure_first: bool = False) -> list[str]:
    def order(row: dict) -> tuple:
        return ((is_tradeoff(row),) if pure_first else ()) + (-key(row), *_ties(row))
    return [row["id"] for row in sorted(rows, key=order)]


def rank_rows(rows: list[dict]) -> tuple[list[dict], dict]:
    """Return copied rows in best order and all three id sorts.

    "Best": pure gains first (no axis down) by the larger gain, then trade-offs by the larger gain."""
    copied = [{**row, "sortScore": score(row)} for row in rows]
    sorts = {"best": _ids(copied, score, pure_first=True),
             "dps": _ids(copied, lambda row: _pct(row, "dpsPct")),
             "ehp": _ids(copied, lambda row: _pct(row, "ehpPct"))}
    rank = {ident: index + 1 for index, ident in enumerate(sorts["best"])}
    by_id = {row["id"]: {**row, "rank": rank[row["id"]]} for row in copied}
    return [by_id[ident] for ident in sorts["best"]], sorts
