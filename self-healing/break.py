#!/usr/bin/env python3
"""Break calc.py on purpose — the demo trigger for the self-healing pipeline.

    python break.py --bug xor

Injects exactly one named bug into calc.py. The healer (healer.py)
knows how to fix each one. Run it only on a healthy calc.py — if the
file is already broken, it refuses and changes nothing.
"""

import argparse
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CALC_FILE = BASE_DIR / "calc.py"

BUGS = {
    "xor": {
        "correct": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ** b',
        "broken": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ^ b',
        "message": "Broke power(): it now uses ^ (XOR) instead of **, so power(2, 3) returns 1 instead of 8.",
    },
    "add-sub": {
        "correct": 'def add(a, b):\n    """Return a + b."""\n    return a + b',
        "broken": 'def add(a, b):\n    """Return a + b."""\n    return a - b',
        "message": "Broke add(): it now subtracts instead of adding, so add(2, 3) returns -1 instead of 5.",
    },
    "mul-add": {
        "correct": 'def multiply(a, b):\n    """Return a * b."""\n    return a * b',
        "broken": 'def multiply(a, b):\n    """Return a * b."""\n    return a + b',
        "message": "Broke multiply(): it now adds instead of multiplying, so multiply(2, 3) returns 5 instead of 6.",
    },
    "div-guard": {
        "correct": 'def divide(a, b):\n    """Return a / b."""\n    if b == 0:\n        raise ValueError("Cannot divide by zero")\n    return a / b',
        "broken": 'def divide(a, b):\n    """Return a / b."""\n    return a / b',
        "message": "Broke divide(): the zero guard is gone, so divide(1, 0) raises ZeroDivisionError instead of ValueError.",
    },
    "power-offbyone": {
        "correct": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ** b',
        "broken": 'def power(a, b):\n    """Return a raised to the power of b."""\n    return a ** (b - 1)',
        "message": "Broke power(): it is off by one in the exponent, so power(2, 3) returns 4 instead of 8.",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Inject one named bug into calc.py.")
    parser.add_argument("--bug", required=True, choices=sorted(BUGS),
                        help="which bug to inject")
    args = parser.parse_args()

    bug = BUGS[args.bug]
    source = CALC_FILE.read_text()
    # Refuse if ANY function is already broken, not just the one about
    # to be broken — stacking a second bug on a broken file leaves two
    # failures at once, so check the whole file is healthy first.
    for name, known in BUGS.items():
        if source.count(known["correct"]) != 1:
            print(f"calc.py is already broken ({name} is not in its correct state) — restore it first, then break it.")
            return 1
    CALC_FILE.write_text(source.replace(bug["correct"], bug["broken"]))
    # Drop any cached bytecode for calc.py, so the next test run
    # compiles the broken file instead of reusing a stale .pyc: a
    # one-character break can leave the file the same size, and a .pyc
    # is only rechecked by size and whole-second mtime.
    shutil.rmtree(BASE_DIR / "__pycache__", ignore_errors=True)
    print(bug["message"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
