"""Numbers as the app shows them (decision 020). The browser's formatter passes the same cases
(tests/autobuilder/fixtures/number_cases.json, M4).

- `pob`: a value from PoB, as PoB's Calcs tab writes it: `floor(value * 10^p + 0.5) / 10^p` (Common.lua:709-715),
  Lua's `tostring` (14 significant digits, so trailing zeros drop) and thousands separators (CalcFormat.lua:12-14,
  Common.lua:803+, PoB's default separators). inf, -inf and NaN are spelled as PoB spells them.
- `floor`: a number the app works out itself, rounded down where the game rounds down (for example "4 hits").
- A value PoB did not compute shows as MISSING, never as 0.
"""

import math
import re

MISSING = "—"
RULES = ("pob", "floor")
LEADING_NUMBER = re.compile(r"(-?)(\d+)(\.?\d*)")


def _lua_tostring(value: float) -> str:
    """Lua 5.1's tostring for a number: "%.14g"."""
    return "%.14g" % value  # noqa: UP031 - the exact printf format Lua uses


def _thousands(text: str) -> str:
    match = LEADING_NUMBER.search(text)
    if match is None:
        return text
    minus, digits, fraction = match.groups()
    grouped = f"{int(digits):,}"
    return text[: match.start()] + minus + grouped + fraction + text[match.end() :]


def show(value: float | None, *, rule: str, precision: int) -> str:
    if rule not in RULES:
        raise ValueError(f"unknown number rule {rule!r}; expected one of {RULES}")
    if value is None:
        return MISSING
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    scale = 10**precision
    rounded = math.floor(value * scale + (0.5 if rule == "pob" else 0)) / scale
    return _thousands(_lua_tostring(rounded + 0.0))
