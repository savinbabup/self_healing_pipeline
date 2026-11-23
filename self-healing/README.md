# Self-Healing CI/CD Pipeline

A small calculator app with a pipeline that fixes its own test failures.

## What it is

- `calc.py` — five calculator functions: power, add, subtract, multiply, divide.
- `test_calc.py` — tests for every function (not just power).
- `healer.py` — the doctor. When the tests fail, it works out which of five known bugs caused it, fixes `calc.py`, and checks the tests pass again. If several bugs are stacked in the file at once, it fixes them one at a time until the tests pass.
- `break.py` — breaks `calc.py` on purpose, so you can watch the pipeline heal it.
- `.github/workflows/self-healing-ci.yml` — runs the tests on every push and pull request.
- `.github/workflows/self-heal.yml` — runs when the tests fail. It runs the healer, opens a pull request with the fix, waits for the tests to pass, and merges it.

## How the loop works

1. Someone breaks the code — `python self-healing/break.py --bug xor` — and pushes it.
2. **Self-Healing CI** runs the tests. They fail.
3. **Self-Heal** starts. It checks out the failing commit and runs `healer.py`.
4. The healer finds the bug (here: `power()` uses `^` instead of `**`), fixes `calc.py`, and confirms the tests pass.
5. Self-Heal opens a pull request with the fix, runs CI on it, and merges it once the tests are green.
6. The code on `main` is healthy again — no human touched it.

## The five bugs the healer knows

| Bug | What goes wrong | How the healer spots it | The fix |
| --- | --- | --- | --- |
| `xor` | `power()` uses `^` (XOR) instead of `**` | `test_power_positive` fails: `assert 1 == 8` | `a ^ b` → `a ** b` |
| `power-offbyone` | `power()` is off by one in the exponent | `test_power_positive` fails: `assert 4 == 8` | `a ** (b - 1)` → `a ** b` |
| `add-sub` | `add()` subtracts instead of adding | `test_add` fails: `assert -1 == 5` | `a - b` → `a + b` in `add()` |
| `mul-add` | `multiply()` adds instead of multiplying | `test_multiply` fails: `assert 5 == 6` | `a + b` → `a * b` in `multiply()` |
| `div-guard` | `divide()` has no guard against zero | `test_divide_by_zero` fails with `ZeroDivisionError` | Add the `if b == 0: raise ValueError(...)` guard |

## Try it on your own computer (no GitHub needed)

```bash
pip install -r self-healing/requirements.txt
cd self-healing
python -m pytest test_calc.py -v        # all green
python break.py --bug xor                # break it on purpose
python -m pytest test_calc.py -v        # now it fails
python healer.py                          # the healer fixes it
python -m pytest test_calc.py -v        # green again
```

## Try it for real (on GitHub)

1. Push these files to the repo (including the two workflow files in `.github/workflows/`).
2. `python self-healing/break.py --bug xor`
3. `git add self-healing/calc.py`
4. `git commit -m "Break power on purpose" && git push`
5. Watch the Actions tab: **Self-Healing CI** fails, then **Self-Heal** opens a pull request and merges it once the tests pass.
6. `git pull` — `calc.py` is fixed.

## Honest limits

- The healer only knows the five bugs in the table. Anything else — a syntax error, a bug it has never seen, a broken test file — and it stops, prints `I can't diagnose this - needs a human`, and changes nothing.
- `break.py` refuses to break a file that is already broken, so bugs don't stack up by accident — heal or restore the file first, then break it again.
- It never heals its own fix: if the tests fail on a `self-heal/*` branch, it posts a comment on the pull request saying the fix didn't hold and asks a human to look.
- It attempts one heal per failed run. No infinite loops.
- The fix is only merged after CI passes on the pull request. If the checks fail, the pull request stays open for a human.
