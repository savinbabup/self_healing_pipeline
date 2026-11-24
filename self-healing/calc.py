"""Simple calculator module for the self-healing CI/CD demo.

These are the functions the pipeline tests. The healer (healer.py)
knows how to fix five specific ways these functions can be broken.
"""

def power(a, b):
    """Return a raised to the power of b."""
    return a ** b

def add(a, b):
    """Return a + b."""
    return a + b

def subtract(a, b):
    """Return a - b."""
    return a - b

def multiply(a, b):
    """Return a * b."""
    return a * b

def divide(a, b):
    """Return a / b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
