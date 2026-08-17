# M-C — the module-level skip-guard census R101 asks for

**Date:** 2026-08-17 · **Tree:** `main` @ `c83febc`, clean · no tracked file modified

R101's closing condition begins: *"An enumeration of every module-level skip guard in `tests/`,
each classified **intended** or **accidental** against the CI install line."* This is it.

## The install line, quoted

`.github/workflows/ci.yml:22` — the only one:

```
run: pip install -e ".[baml,dev,docs,etkl]"
```

with `baml-cli generate` at `:24` and `pytest -q` at `:26` — **no `-m` filter, no `addopts`, and
no `conftest.py` anywhere in the repo** (`find . -name conftest.py` → empty). That last fact
matters: the `pytest.mark.corpus` markers gate nothing.

## The headline numbers

| figure | value |
| --- | --- |
| module-scope guards | **45 files, 390 collected tests** (of 1227 collected, 164 files) |
| inert — dependency installed directly | 35 files / 330 tests |
| actually skipping in CI on a missing dependency | **2 files / 3 tests, reported as 2 skip lines** |
| actually skipping in CI on absent corpus | 3 files / 19 tests, **19 skip lines** (proportional) |
| `corpus`-marked but **not** skipped by the marker | 4 files / 36 tests — they run |
| unclassifiable | 1 file / 2 tests |
| **accidental in R101's sense, today** | **none** |

R101's row cites *"48 test modules reference `importorskip` and 8 carry a module-level
`pytestmark`"*. **Both figures verified correct.** Refinements the row could not state: of the
48, **37 evaluate one at import time**, 11 are function-body only, 1 does both; all 8
`pytestmark` files carry a genuine module-level assignment and the two sets are **disjoint**.

**77% of the `importorskip` surface is import-time.** The module-level construct is not a
minority pattern here — it is the default idiom for every `pdfplumber`/`reportlab` module.

## The mechanism, confirmed from pytest 9.0.3's source

`_pytest.outcomes.importorskip` raises `Skipped(reason, allow_module_level=True)`. **So any
`importorskip` evaluated during module import collapses the whole module to one skip — including
one written inside a decorator expression**, because decorators evaluate at import time.

That is the case the census turns up and **R101's row does not anticipate it.**

## Finding 1 — `test_datagrid.py` is R101's shape in a costume

`tests/etkl/test_datagrid.py:218,252,265,298,338,344,382` carry seven decorators of the form:

```python
@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
```

The `reason` string and the per-test placement both assert *"this guards 7 tests."* Measured
end to end with an import-blocking plugin:

```
$ python3 -m pytest tests/etkl/test_datagrid.py -q -p blocker
59 passed in 106.52s

$ BLOCK_MODS=reportlab python3 -m pytest tests/etkl/test_datagrid.py -q -rs -p blocker
SKIPPED [1] tests/etkl/test_datagrid.py:218: could not import 'reportlab'
1 skipped in 0.47s
```

**59 → 1.** It guards 59 tests — 15% of the entire module-guarded surface, the largest module in
the repo — and reports one line. Two aggravations:

- It is inert only because `reportlab` sits in `dev` (`pyproject.toml:72`). A **PDF-generation**
  dependency living in the **dev-tooling** extra is the same incidental placement that made
  R101's original instance, and nothing records that 59 tests depend on it.
- `pytest.importorskip(...) is None` is always `False` when the import succeeds, so the
  `skipif` half of every one of the seven decorators is **dead code**. The only live behaviour
  is the import-time side effect — i.e. the opposite of what the decorator appears to say.

## Finding 2 — `rapidocr`'s exclusion is inferred, never stated

`tests/etkl/test_ocr_rapid.py:3` and `test_ocr_end_to_end.py:3` guard on `rapidocr`, which lives
in the `ocr` extra CI does not install. Verified: `BLOCK_MODS=rapidocr,onnxruntime` → `2 skipped`
for 3 tests.

`grep -rn "ocr" .github/ docs/superpowers/residues*.md README.md` finds **no statement anywhere**
that CI deliberately omits `ocr`. The structural argument for "intended" is that a whole extra is
omitted and its deps are heavy native wheels — **but that is exactly the evidence available for
`pandas` before R101, and it was wrong there.**

The contrast worth copying: `pyproject.toml:49-53`, where the `etkl` extra now carries a comment
naming its CI consequence. That is the **only** guard in the repo whose intent is written down.

## Finding 3 — one guard that cannot be classified

`tests/etkl/test_ocr_render.py:3`, `pytest.importorskip("pypdfium2")`, 2 tests. `pypdfium2` is
declared only in `ocr` (`pyproject.toml:67`) and `demo` (`:59`), neither installed by CI — so by
the repo's *declared* dependency graph this guard should fire. It does not, because

```
python3 -c "import importlib.metadata as md; md.requires('pdfplumber')"
→ ['pdfminer.six==20260107', 'Pillow>=12.2.0', 'pypdfium2>=5.9.0']
```

It is inert **on an undeclared transitive edge**, and it is the one guard in the census that
silently changes class if an upstream package changes its own dependencies. Flagged rather than
forced into a bucket.

## What degrades proportionally, and why that is the contrast

Not every guard collapses. `tests/etkl/test_membrane_equiv.py:19` (`pytestmark` on `pyrudof`)
reports **31** skip lines, and the three corpus-existence `pytestmark` guards report 19 between
them. **`pytestmark = pytest.mark.skipif(...)` is applied per collected test and stays
proportional; `importorskip` at import time collapses.** Any registry R101 builds should record
which construct a module uses, because the two have different failure signatures and only one is
invisible in the CI summary.

## Incidental, outside the survey's scope

`src/iladub/readers.py` is the only source file referencing the `readers` extra's deps
(`openpyxl`, `python-docx`, `bs4`, `pdfminer`), and grepping `tests/` for any of them returns
nothing. **That subsystem has no tests to skip** — a coverage gap of a different kind, and one no
skip census would ever surface. Not raised as a residue here; recorded so it is not lost.

## Caveats

- Test counts are collected node IDs (parametrized cases included) from a local environment
  where every guarded dep is present. `defs` differs from node count in three modules; both are
  in the agent's full table.
- "Intended (inert)" means the dependency is installed so the guard never fires. That is *not*
  the same as "safe" — it is the class `test_datagrid.py` sits in, and Finding 1 is what that
  class costs when the placement changes.
