"""Parsing helpers for the benchmark substrate repository.

Deliberately small and dependency-free so that both benchmark arms
(with and without the XP kit) operate on identical, deterministic code.
"""
from __future__ import annotations

from typing import Tuple


def parse_int(raw: object) -> int:
    """Parse an integer, tolerating surrounding whitespace and a sign."""
    if raw is None:
        raise ValueError("raw must not be None")
    return int(str(raw).strip())


def parse_date(raw: object) -> Tuple[int, int, int]:
    """Parse an ISO date (YYYY-MM-DD) into a (year, month, day) tuple."""
    parts = str(raw).strip().split("-")
    if len(parts) != 3:
        raise ValueError(f"invalid date: {raw!r}")
    year, month, day = (int(part) for part in parts)
    if not 1 <= month <= 12:
        raise ValueError(f"invalid month: {raw!r}")
    if not 1 <= day <= 31:
        raise ValueError(f"invalid day: {raw!r}")
    return year, month, day


def format_date(value: Tuple[int, int, int]) -> str:
    """Render a (year, month, day) tuple back to ISO form."""
    year, month, day = value
    return f"{year:04d}-{month:02d}-{day:02d}"
