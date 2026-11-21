"""Tests for app.parser (substrate repository)."""
import unittest

from app.parser import format_date, parse_date, parse_int


class ParseIntTests(unittest.TestCase):
    def test_parses_plain_integer(self):
        self.assertEqual(parse_int("42"), 42)

    def test_parses_negative_integer(self):
        self.assertEqual(parse_int("-7"), -7)

    def test_tolerates_whitespace(self):
        self.assertEqual(parse_int("  13  "), 13)

    def test_rejects_none(self):
        with self.assertRaises(ValueError):
            parse_int(None)

    def test_rejects_non_numeric(self):
        with self.assertRaises(ValueError):
            parse_int("abc")


class ParseDateTests(unittest.TestCase):
    def test_parses_iso_date(self):
        self.assertEqual(parse_date("2026-11-20"), (2026, 11, 20))

    def test_rejects_short_date(self):
        with self.assertRaises(ValueError):
            parse_date("2026-11")

    def test_rejects_impossible_month(self):
        with self.assertRaises(ValueError):
            parse_date("2026-13-01")

    def test_rejects_impossible_day(self):
        with self.assertRaises(ValueError):
            parse_date("2026-01-32")

    def test_round_trip(self):
        self.assertEqual(format_date(parse_date("2025-03-04")), "2025-03-04")


if __name__ == "__main__":
    unittest.main()
