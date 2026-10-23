"""Unit tests for display-only truncation helpers."""

import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from display import fmt, fmt_compact, fmt_pct, trunc  # noqa: E402


class DisplayTests(unittest.TestCase):
    def test_truncates_toward_zero_without_float_noise(self):
        self.assertEqual(trunc(7.5757575757576, 2), 7.57)
        self.assertEqual(trunc(0.29, 2), 0.29)
        self.assertEqual(fmt(0.29, 2), "0.29")
        self.assertEqual(trunc(-1.99, 1), -1.9)
        self.assertEqual(trunc(float("inf"), 2), float("inf"))

    def test_fixed_format_sign_thousands_and_zero(self):
        self.assertEqual(fmt(1050.952, 1, sign=True, thousands=True), "+1,050.9")
        self.assertEqual(fmt(-0.04, 1), "0.0")
        self.assertEqual(fmt(-0.04, 1, sign=True), "0.0")
        self.assertEqual(fmt(1234567.891, 0, thousands=True), "1,234,567")

    def test_compact_format_strips_trailing_zeroes(self):
        self.assertEqual(fmt_compact(7.5757575757576), "7.57")
        self.assertEqual(fmt_compact(0.1666e6 / 1e6), "0.16")
        self.assertEqual(fmt_compact(56830000.5 / 1e6), "56.83")
        self.assertEqual(fmt_compact(24.0), "24")
        self.assertEqual(fmt_compact(-0.001), "0")

    def test_percent_and_missing_value(self):
        self.assertEqual(fmt_pct(-25.00000001), "-25.0%")
        self.assertEqual(fmt_pct(None), "n/a")


if __name__ == "__main__":
    unittest.main()
