#!/usr/bin/env python3
"""Self-healing doctor for calc.py.

Run it after the tests fail:

    python healer.py

It runs the pytest suite itself, reads the failures, and fixes only the
five failure patterns it knows. If the failure is anything else — a
syntax error, a bug it has never seen, a broken test file — it prints
"I can't diagnose this - needs a human", changes nothing, and exits
non-zero.

Exit code 0 means a fix was applied and the tests pass afterwards.
Anything else means no fix was applied.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CALC_FILE = BASE_DIR / "calc.py"
TEST_FILE = BASE_DIR / "test_calc.py"
DIAGNOSIS_FILE = BASE_DIR / "diagnosis.txt"
FIX_FILE = BASE_DIR / "fix.txt"

CANT_DIAGNOSE = "I can't diagnose this - needs a human"


# One entry per failure pattern the healer knows. "broken" and "fixed"
# are exact strings in calc.py — the healer only ever replaces the
# exact broken text with the exact fixed text, nothing else.
PATTERNS = [
    {
        "key": "xor",
        "failed_test": "test_power_positive",
        "output_must_contain": "assert 1 == 8",
        "broken": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ^ b',
        "fixed": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ** b',
        "diagnosis": "power() used ^ (XOR) instead of **",
        "fix": "Replaced `a ^ b` with `a ** b` in calc.py",
    },
    {
        "key": "power-offbyone",
        "failed_test": "test_power_positive",
        "output_must_contain": "assert 4 == 8",
        "broken": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ** (b - 1)',
        "fixed": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ** b',
        "diagnosis": "power() was off by one in the exponent",
        "fix": "Replaced `a ** (b - 1)` with `a ** b` in calc.py",
    },
    {
        "key": "add-sub",
        "failed_test": "test_add",
        "output_must_contain": "assert -1 == 5",
        "broken": 'def add(a, b):\n    """Return a + b."""\n    return a - b',
        "fixed": 'def add(a, b):\n    """Return a + b."""\n    return a + b',
        "diagnosis": "add() was implemented as subtraction",
        "fix": "Replaced `a - b` with `a + b` in add() in calc.py",
    },
    {
        "key": "mul-add",
        "failed_test": "test_multiply",
        "output_must_contain": "assert 5 == 6",
        "broken": 'def multiply(a, b):\n    """Return a * b."""\n    return a + b',
        "fixed": 'def multiply(a, b):\n    """Return a * b."""\n    return a * b',
        "diagnosis": "multiply() was implemented as addition",
        "fix": "Replaced `a + b` with `a * b` in multiply() in calc.py",
    },
    {
        "key": "div-guard",
        "failed_test": "test_divide_by_zero",
        "output_must_contain": "ZeroDivisionError",
        "broken": 'def divide(a, b):\n    """Return a / b."""\n    return a / b',
        "fixed": 'def divide(a, b):\n    """Return a / b."""\n    if b == 0:\n        raise ValueError("Cannot divide by zero")\n    return a / b',
        "diagnosis": "divide() had no guard against dividing by zero",
        "fix": 'Added the zero guard to divide() in calc.py (raises ValueError("Cannot divide by zero"))',
    },
]


def run_pytest():
    """Run the test suite and return (exit_code, combined_output)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", TEST_FILE.name, "-v"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def failed_tests(output):
    """Test names that pytest reported as FAILED."""
    names = set(re.findall(r"test_calc\.py::(\w+) FAILED", output))
    names |= set(re.findall(r"FAILED test_calc\.py::(\w+)", output))
    return names


def cant_diagnose():
    print(CANT_DIAGNOSE)
    return 1


def main():
    code, output = run_pytest()

    if code == 0:
        print("All tests pass — nothing to heal.")
        return 1

    if "SyntaxError" in output or "ERROR collecting" in output:
        print("The test run broke before any test could run (a syntax or collection error).")
        return cant_diagnose()

    failed = failed_tests(output)
    source = CALC_FILE.read_text()

    for pattern in PATTERNS:
        if pattern["failed_test"] not in failed:
            continue
        if pattern["output_must_contain"] not in output:
            continue
        if pattern["broken"] not in source:
            continue
        if source.count(pattern["broken"]) != 1:
            continue
        # All checks agree: apply the exact fix.
        CALC_FILE.write_text(source.replace(pattern["broken"], pattern["fixed"]))
        # Drop cached bytecode so the verification run below compiles
        # the fixed file (same one-character/size trap as in break.py).
        shutil.rmtree(BASE_DIR / "__pycache__", ignore_errors=True)
        DIAGNOSIS_FILE.write_text(pattern["diagnosis"] + "\n")
        FIX_FILE.write_text(pattern["fix"] + "\n")
        print(f"Diagnosis: {pattern['diagnosis']}.")
        print(f"Fix: {pattern['fix']}.")
        code_after, _ = run_pytest()
        if code_after == 0:
            print("Tests pass after the fix.")
            return 0
        print("The fix was applied but the tests still fail — needs a human.")
        return 1

    return cant_diagnose()


if __name__ == "__main__":
    sys.exit(main())
