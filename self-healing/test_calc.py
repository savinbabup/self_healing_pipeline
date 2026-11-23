"""Pytest suite for calc.py.

Tests every operation, not just power — the original demo only ever
tested power, so a broken add() or multiply() would have slipped through.
"""

import pytest

from calc import add, divide, multiply, power, subtract


def test_power_positive():
    assert power(2, 3) == 8


def test_power_negative_exponent():
    assert power(2, -2) == 0.25


def test_power_zero_exponent():
    assert power(5, 0) == 1


def test_add():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-2, -3) == -5


def test_subtract():
    assert subtract(5, 3) == 2


def test_subtract_negative_result():
    assert subtract(3, 5) == -2


def test_multiply():
    assert multiply(2, 3) == 6


def test_multiply_by_zero():
    assert multiply(5, 0) == 0


def test_divide():
    assert divide(6, 3) == 2


def test_divide_fraction():
    assert divide(5, 2) == 2.5


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)
