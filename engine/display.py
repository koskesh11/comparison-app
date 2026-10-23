"""Display-only number formatting with Path of Exile-style truncation."""

import math

FLOAT_NOISE_DIGITS = 6


def trunc(value: float, digits: int = 0) -> float:
    """Truncate toward zero after removing insignificant binary float noise."""
    if not math.isfinite(value):
        return value
    scale = 10 ** digits
    return math.trunc(round(value * scale, FLOAT_NOISE_DIGITS)) / scale


def fmt(value: float, digits: int = 0, *, sign: bool = False,
        thousands: bool = False) -> str:
    """Render a truncated value with fixed decimals and optional sign/grouping."""
    value = trunc(value, digits)
    if value == 0:
        value = 0.0
        sign = False
    spec = ("+" if sign else "") + ("," if thousands else "") + f".{digits}f"
    return format(value, spec)


def fmt_compact(value: float, digits: int = 2) -> str:
    """Render a truncated value without trailing decimal zeroes."""
    return fmt(value, digits).rstrip("0").rstrip(".") if digits else fmt(value)


def fmt_pct(value: float | None, digits: int = 1, *, sign: bool = True) -> str:
    """Render a percentage or ``n/a`` for a missing value."""
    return "n/a" if value is None else fmt(value, digits, sign=sign) + "%"
