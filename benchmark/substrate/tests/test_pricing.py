"""Tests for app.pricing (substrate repository)."""
import unittest

from app.pricing import compute_total, format_currency, line_total


class LineTotalTests(unittest.TestCase):
    def test_multiplies_quantity_by_price(self):
        self.assertEqual(line_total(3, 2.5), 7.5)

    def test_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            line_total(-1, 10.0)

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            line_total(1, -0.01)


class ComputeTotalTests(unittest.TestCase):
    def test_sums_line_items(self):
        self.assertEqual(compute_total([(2, 5.0), (1, 2.5)]), 12.5)

    def test_empty_order_is_zero(self):
        self.assertEqual(compute_total([]), 0.0)

    def test_rounds_to_two_places(self):
        self.assertEqual(compute_total([(1, 0.005)]), 0.01)


class FormatCurrencyTests(unittest.TestCase):
    def test_renders_two_decimals(self):
        self.assertEqual(format_currency(3), "3.00")


if __name__ == "__main__":
    unittest.main()
