"""Pricing rules for the benchmark substrate repository."""
from __future__ import annotations

from typing import Iterable, Tuple


def line_total(quantity: int, unit_price: float) -> float:
    """Return the total for a single line item."""
    if quantity < 0:
        raise ValueError("quantity must not be negative")
    if unit_price < 0:
        raise ValueError("unit_price must not be negative")
    return round(quantity * unit_price, 2)


def compute_total(items: Iterable[Tuple[int, float]]) -> float:
    """Sum every line item into an order total."""
    return round(sum(line_total(quantity, price) for quantity, price in items), 2)


def format_currency(amount: float) -> str:
    """Render an amount using two decimal places."""
    return f"{amount:.2f}"
