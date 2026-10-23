"""Deterministic guide-check scoring and sorts."""

from guide_diff_common import CATEGORY_ORDER


def _pct(row: dict, key: str) -> float:
    value = ((row.get("result") or {}).get("delta") or {}).get(key)
    return value if isinstance(value, (int, float)) else 0.0


def score(row: dict) -> float:
    return max(_pct(row, "dpsPct"), _pct(row, "ehpPct"))


def _ties(row: dict) -> tuple:
    order = {name: index for index, name in enumerate(CATEGORY_ORDER)}
    return (order.get(row.get("category"), len(order)),
            str(row.get("label") or "").casefold(), str(row.get("id") or ""))


def _ids(rows: list[dict], key) -> list[str]:
    return [row["id"] for row in sorted(rows, key=lambda row: (-key(row), *_ties(row)))]


def rank_rows(rows: list[dict]) -> tuple[list[dict], dict]:
    """Return copied rows in best order and all three id sorts."""
    copied = [{**row, "sortScore": score(row)} for row in rows]
    sorts = {"best": _ids(copied, score),
             "dps": _ids(copied, lambda row: _pct(row, "dpsPct")),
             "ehp": _ids(copied, lambda row: _pct(row, "ehpPct"))}
    rank = {ident: index + 1 for index, ident in enumerate(sorts["best"])}
    by_id = {row["id"]: {**row, "rank": rank[row["id"]]} for row in copied}
    return [by_id[ident] for ident in sorts["best"]], sorts
