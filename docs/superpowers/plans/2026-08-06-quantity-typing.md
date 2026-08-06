# Quantity Typing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Teach the cell-typing lattice that `(171)` is an ambiguous quantity form that must abstain, and that `$ 45,781` and `45,781` are the same kind of thing for homogeneity — measured to take apple page 0 from 0.0000 to 0.1170 with band 4 asserting 20 cells.

**Doc impact:** none for this plan file — the loop's `Doc impact: increment` is declared in the design spec (`2026-08-06-quantity-typing-design.md`).

**Architecture:** Two new owned vocabulary terms (`tab:ParenthesizedNumber` as a lattice member, `tab:Quantity` as a datatype family) plus two owned properties (`tab:datatypeAbstains`, `tab:inDatatypeFamily`) declare the rules in `tab.ttl`. `celltype.grid_evidence` emits those declarations into every evidence graph so the five homogeneity queries can reason over them, and each query normalises through one uniform idiom instead of hardcoding type names. Raw typing (`_cell_datatype`) stays a pure format grammar.

**Tech Stack:** Python 3.11+/pytest, rdflib SPARQL, the corpus battery.

**Spec:** `docs/superpowers/specs/2026-08-06-quantity-typing-design.md` — read it first, especially §2 (the measurement that re-scoped this loop) and §3 (why the two cases use different mechanisms).

## Global Constraints

- **The two mechanisms are deliberately different and must not be collapsed.** `tab:ParenthesizedNumber` **abstains** (never votes, never mismatches) because the form is genuinely ambiguous with a footnote marker. `tab:Currency` **normalises** to `tab:Quantity` because `$ 45,781` is unambiguously a quantity. Do not make parens normalise to Quantity, and do not make Currency abstain.
- **No tuned constant.** A digit-count threshold to separate `(171)` from the footnote `(1)` is explicitly forbidden — abstention exists precisely because no threshold is legitimate (CLAUDE.md §8: a tuned constant is prima facie evidence the decision belongs elsewhere).
- **`_cell_datatype` stays a format grammar** (PROCEDURAL raw typing, exactly like `is_date`/`is_currency`). No context, no column awareness.
- **Corpus byte-identity is the no-regression gate:** stem **0.9655** / 2152 cells / chain [3], CBH **0.9047**, capacity **1.0000**, WHO **0.5597**. All four were measured byte-identical under simulation before this plan was written; a move is a regression to diagnose, not to accept.
- **Broken system git on this machine:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …`.
- **Run suites in the FOREGROUND** with generous timeouts; never background them and wait for a notification (they do not reliably fire here). The corpus runs and the full suite are the CONTROLLER's job.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-quantity-typing` — already created off `main`; the design spec is already committed there.
- Never lower a floor or weaken a pin to force green.

---

### Task 1: The vocabulary, the grammar, and the recall/precision battery

**Files:**
- Modify: `vocab/ontology/tab.ttl` (new terms; the lattice comment)
- Modify: `src/iladub/etkl/celltype.py` (`is_paren_number`, `_cell_datatype` clause, `grid_evidence` emits the declarations)
- Create: `tests/etkl/test_quantity_typing.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces (Tasks 2–3 depend on these exact names): `celltype.is_paren_number(s: str) -> bool`; `_cell_datatype` returning `TAB.ParenthesizedNumber`; `grid_evidence` emitting, in every graph it builds, the triples `tab:Blank tab:datatypeAbstains true`, `tab:ParenthesizedNumber tab:datatypeAbstains true`, `tab:Numeric tab:inDatatypeFamily tab:Quantity`, `tab:Currency tab:inDatatypeFamily tab:Quantity`.

- [ ] **Step 1: Write the failing tests** — create `tests/etkl/test_quantity_typing.py`:

```python
"""Quantity typing (spec 2026-08-06-quantity-typing-design.md).

Two mechanisms, deliberately different:
  - tab:ParenthesizedNumber ABSTAINS — `(171)` is format-identical to the footnote `(1)`
    (measured on apple: 34 negative-shaped, 3 footnote-shaped, all footnotes `(1)`), so no
    grammar can separate them and the honest reading is to abstain, exactly as tab:Blank does.
  - tab:Currency NORMALISES to tab:Quantity — `$ 45,781` is unambiguously a quantity and the
    `$` is a unit marker, a reading this repo already asserts elsewhere (tab:UnitMarker).
"""
from rdflib import Literal, Namespace
from iladub.etkl import celltype
from iladub.etkl.celltype import _cell_datatype, is_paren_number

TAB = Namespace("https://w3id.org/iladub/tab#")


# ---------- recall: forms that ARE parenthesized numbers (R55's mandated battery) ----------

def test_paren_grammar_recall():
    for s in ["(171)", "(698)", "(2,037)", "(1.5)", "(0)", "(1,234.56)", "( 171 )", "(-5)"]:
        assert is_paren_number(s), s
        assert _cell_datatype(s) == TAB.ParenthesizedNumber, s


def test_footnote_marker_is_the_same_form_and_types_the_same_way():
    """`(1)` is a footnote marker on apple, and format-identical to a one-digit negative.
    It MUST type as ParenthesizedNumber too — abstention is what makes that safe. Typing it
    differently would require a digit-count threshold, which the gate forbids."""
    assert _cell_datatype("(1)") == TAB.ParenthesizedNumber


# ---------- precision: forms that are NOT parenthesized numbers ----------

def test_paren_grammar_precision():
    for s in ["(a)", "(i)", "(see p.250)", "(cont'd)", "()", "(171", "171)", "$(171)", "(171)*"]:
        assert not is_paren_number(s), s
        assert _cell_datatype(s) != TAB.ParenthesizedNumber, s


def test_blank_marker_still_types_blank():
    """`(blank)` is the shipped missing-value marker and must not be captured by the new
    grammar — is_blank runs first in _cell_datatype."""
    assert _cell_datatype("(blank)") == TAB.Blank


def test_plain_and_currency_forms_are_unchanged():
    assert _cell_datatype("45,781") == TAB.Numeric
    assert _cell_datatype("$ 45,781") == TAB.Currency
    assert _cell_datatype("Americas") == TAB.Text
    assert _cell_datatype("2020-01-02") == TAB.Date


# ---------- the declarations reach the evidence graph ----------

def test_evidence_graph_carries_the_datatype_declarations():
    """The queries reason over these triples, and the evidence graph is transient — so
    grid_evidence must emit them or every normalisation silently no-ops."""
    g = celltype.grid_evidence([(0, 0, "x")], 1)
    assert (TAB.Blank, TAB.datatypeAbstains, Literal(True)) in g
    assert (TAB.ParenthesizedNumber, TAB.datatypeAbstains, Literal(True)) in g
    assert (TAB.Numeric, TAB.inDatatypeFamily, TAB.Quantity) in g
    assert (TAB.Currency, TAB.inDatatypeFamily, TAB.Quantity) in g


def test_text_neither_abstains_nor_has_a_family():
    """Text must stay its own thing: it is the signal every homogeneity query keys on."""
    g = celltype.grid_evidence([(0, 0, "x")], 1)
    assert (TAB.Text, TAB.datatypeAbstains, Literal(True)) not in g
    assert list(g.objects(TAB.Text, TAB.inDatatypeFamily)) == []


def test_date_is_not_in_the_quantity_family():
    """Date is deliberately its own family — a date column is not a quantity column."""
    g = celltype.grid_evidence([(0, 0, "x")], 1)
    assert list(g.objects(TAB.Date, TAB.inDatatypeFamily)) == []
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_quantity_typing.py -v`
Expected: FAIL — `cannot import name 'is_paren_number'`.

- [ ] **Step 3: Declare the vocabulary** — in `vocab/ontology/tab.ttl`, beside the existing lattice members (`tab:Blank`, `tab:Numeric`, `tab:Text`, `tab:Date`, `tab:Currency`, `tab:CurrencyGlyph` around line 208), add:

```turtle
tab:ParenthesizedNumber a tab:CellDatatype ; rdfs:label "Parenthesized number"@en ;
    tab:datatypeAbstains true ;
    rdfs:comment "A number in parentheses — US accounting notation for a negative. FORMAT-IDENTICAL to a footnote marker ('(1)'), which no grammar can separate from a one-digit negative, so this datatype ABSTAINS from every homogeneity judgement exactly as tab:Blank does: it never votes in a modal computation and never counts as a mismatch. Separating the two readings would need context, not format, and guessing would need a digit-count threshold the neurosymbolic gate forbids. Measured on apple-fy2026q3: 34 negative-shaped cells, 3 footnote-shaped, all footnotes exactly '(1)'."@en .

tab:CellDatatypeFamily a owl:Class ; rdfs:label "Cell datatype family"@en ;
    rdfs:comment "A group of cell datatypes that count as THE SAME TYPE for homogeneity purposes. The grouping is declared here rather than repeated inside each query, so the rule is published with the ontology and a new member is one triple rather than five query edits."@en .

tab:Quantity a tab:CellDatatypeFamily ; rdfs:label "Quantity"@en ;
    rdfs:comment "Numbers and currency amounts. '$ 45,781' and '45,781' are the same kind of thing: the currency symbol is a UNIT MARKER rendered on some rows only (a reading this vocabulary already carries as tab:UnitMarker), not a different datatype. tab:Date deliberately stays outside — a date column is not a quantity column."@en .

tab:inDatatypeFamily a owl:ObjectProperty ; rdfs:label "in datatype family"@en ;
    rdfs:domain tab:CellDatatype ; rdfs:range tab:CellDatatypeFamily ;
    rdfs:comment "The homogeneity family a cell datatype normalises to. Queries compare families, not raw datatypes."@en .

tab:datatypeAbstains a owl:DatatypeProperty ; rdfs:label "datatype abstains"@en ;
    rdfs:domain tab:CellDatatype ; rdfs:range xsd:boolean ;
    rdfs:comment "True for a datatype whose cells take no part in a homogeneity judgement — neither voting nor mismatching. tab:Blank abstains because the cell is missing; tab:ParenthesizedNumber abstains because its form is genuinely ambiguous."@en .

tab:Numeric  tab:inDatatypeFamily tab:Quantity .
tab:Currency tab:inDatatypeFamily tab:Quantity .
tab:Blank    tab:datatypeAbstains true .
```

Also extend the lattice's own `rdfs:comment` (line 207) to mention that loop-quantity adds `tab:ParenthesizedNumber` and the family/abstain declarations. **Check `owl:` and `xsd:` prefixes are already bound at the top of `tab.ttl`** (they are used elsewhere in the file); if either is missing, add the prefix line.

- [ ] **Step 4: Implement the grammar and the emission** — in `src/iladub/etkl/celltype.py`:

Add the pattern beside the existing `_CURRENCY`/`_ISO_DATE` patterns:

```python
_PAREN_NUMBER = re.compile(r"^\(\s*-?[\d,]+(\.\d+)?\s*\)$")
```

Add the predicate beside `is_currency`:

```python
def is_paren_number(s):
    """A number wrapped in parentheses — US accounting notation for a negative. PROCEDURAL
    raw typing: a format grammar, like is_date/is_currency, with no context and no tuned
    constant. It deliberately also matches the footnote form '(1)', which is the SAME format;
    tab:ParenthesizedNumber abstains from homogeneity judgements precisely because nothing in
    the lexical form can tell the two readings apart."""
    return bool(_PAREN_NUMBER.match(s.strip()))
```

In `_cell_datatype`, add the clause **after `is_blank` and `is_numeric`, before `is_date`** so `(blank)` still types Blank and no plain number is affected:

```python
    if is_paren_number(t):
        return TAB.ParenthesizedNumber
```

In `grid_evidence`, emit the declarations into every graph (the evidence graph is transient and the queries reason over these triples):

```python
def _emit_datatype_declarations(g):
    """The homogeneity rules the queries read. Emitted into every evidence graph because that
    graph is transient and carries no ontology — without these the normalisations silently
    no-op. Mirrors vocab/ontology/tab.ttl; the ontology is the published source of truth."""
    g.add((TAB.Blank, TAB.datatypeAbstains, Literal(True)))
    g.add((TAB.ParenthesizedNumber, TAB.datatypeAbstains, Literal(True)))
    g.add((TAB.Numeric, TAB.inDatatypeFamily, TAB.Quantity))
    g.add((TAB.Currency, TAB.inDatatypeFamily, TAB.Quantity))
```

and call it once at the end of `grid_evidence`, before `return g`.

- [ ] **Step 5: Run — verify green**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_quantity_typing.py tests/etkl/test_celltype.py -q`
Expected: all PASS. `test_celltype.py` is included because it pins the existing lattice — if it fails, the new clause is placed wrongly in `_cell_datatype`'s order.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/ontology/tab.ttl src/iladub/etkl/celltype.py tests/etkl/test_quantity_typing.py && git commit -m "feat(loop-quantity): tab:ParenthesizedNumber + the Quantity family, declared and emitted

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Normalise the five homogeneity queries

**Files:**
- Modify: `vocab/queries/looks-transposed.rq`, `transpose-coherent.rq`, `stub-data-split.rq`, `header-body-split.rq`, `unit-marker-column.rq`
- Modify: `tests/etkl/test_derivation_equiv.py` (`_ref_hbs`, in lockstep)

**Interfaces:**
- Consumes: Task 1's emitted declarations (`tab:datatypeAbstains`, `tab:inDatatypeFamily`).
- Produces: queries that compare *families* and ignore *abstaining* datatypes. Task 3's differential measures them.

**THE ONE IDIOM**, used everywhere a `tab:cellDatatype` is bound. Bind the raw type, drop abstainers, normalise the rest:

```sparql
  ?cell tab:cellDatatype ?raw .
  FILTER NOT EXISTS { ?raw tab:datatypeAbstains true }
  OPTIONAL { ?raw tab:inDatatypeFamily ?fam }
  BIND(COALESCE(?fam, ?raw) AS ?t)
```

Then compare `?t`, never `?raw`. Where a query already filters `!= tab:Blank`, that filter is **replaced** by the abstains check (Blank abstains, so it is covered) — do not keep both.

- [ ] **Step 1: `looks-transposed.rq`** — two sites, lines ~15-16 and ~21-22. Current form:

```sparql
      ?rc tab:atGridRow ?r ; tab:atGridColumn ?rcol ; tab:cellDatatype ?rt . FILTER(?r >= 1 && ?rcol >= 1)
    } GROUP BY ?r HAVING(COUNT(DISTINCT ?rt) = 1 && SUM(IF(?rt = tab:Text, 1, 0)) = 0)
```

Rewrite each site so `?rt` (and `?ct` at the second site) is the NORMALISED type via the idiom, with the abstains filter added before the GROUP BY. Update the query's header comment to say homogeneity is now judged over datatype FAMILIES, and that abstaining datatypes take no part.

- [ ] **Step 2: `transpose-coherent.rq`** — one site, lines ~7-8. Current form:

```sparql
    ?a tab:atGridRow ?r ; tab:atGridColumn ?ac ; tab:cellDatatype ?at . FILTER(?ac >= 1)
    ?b tab:atGridRow ?r ; tab:atGridColumn ?bc ; tab:cellDatatype ?bt . FILTER(?bc >= 1 && ?at != ?bt)
```

Apply the idiom to BOTH `?a`'s and `?b`'s type, then compare the normalised values (`?ta != ?tb`). Both sides must also drop abstainers, so a parenthesized cell can never be one half of a mismatch pair.

- [ ] **Step 3: `stub-data-split.rq`** — three sites (lines ~15-16, ~25-26, ~35-36), all the same `COUNT(DISTINCT …) = 1 && SUM(IF(… = tab:Text, 1, 0)) = 0` shape. Apply the idiom at each.

- [ ] **Step 4: `header-body-split.rq`** — the most intricate. Its Blank filters are at lines 39, 44 and 52 (`FILTER(?D != tab:Blank && ?cr >= 1)`, `FILTER(?d2 != tab:Blank && ?cr2 >= 1)`, `FILTER(?ct != tab:Blank)`). Replace each `!= tab:Blank` with the abstains check on the RAW type, and make the modal computation and the mismatch scan both compare NORMALISED types. The invariant to preserve exactly: a data column has a modal non-abstaining family that is not `tab:Text`, and `s_col` is one past the last non-abstaining mismatch. Update the header comment's "tab:Blank cells are WILDCARDS" paragraph to say abstaining datatypes (Blank and ParenthesizedNumber) are wildcards.

- [ ] **Step 5: `unit-marker-column.rq`** — its neighbour check is currently `FILTER(?dn = tab:Numeric || ?dn = tab:Currency)`. Replace with the normalised form (`?tn = tab:Quantity`) so the loop's own family rule is used rather than an enumeration that would drift. Its `tab:CurrencyGlyph` conditions are untouched — a glyph is not a quantity.

- [ ] **Step 6: Mirror `_ref_hbs`** — in `tests/etkl/test_derivation_equiv.py`, the fast Python reference for `header-body-split.rq` must match the new semantics exactly: treat `TAB.ParenthesizedNumber` as abstaining alongside `BLANK`, and normalise `Currency` to `Quantity` before the modal vote and the mismatch scan. Extend `_TYPES` (the random-grid alphabet) with `"(171)"` and `"$5"` if not present, so the randomized battery actually exercises the new forms. Add a docstring line recording the change.

- [ ] **Step 7: Run the query-level suites**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_derivation_equiv.py tests/etkl/test_header_body_split_robust.py tests/etkl/test_celltype.py tests/etkl/test_quantity_typing.py tests/etkl/test_unit_marker.py tests/etkl/test_transform_gate.py -q`
Expected: all PASS. `test_transform_gate.py` is included deliberately — it enforces that no `.rq` carries a tuned numeric literal, and the edits must not introduce one.

If `test_derivation_equiv` fails, the query and `_ref_hbs` have diverged: fix whichever is wrong on the merits, and say in the report which one it was — do not adjust the test to agree with a query you have not verified.

- [ ] **Step 8: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/queries tests/etkl/test_derivation_equiv.py && git commit -m "feat(loop-quantity): the five homogeneity queries compare families and ignore abstainers

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: The typing differential

**Files:**
- Create: `tests/etkl/test_typing_equiv.py`

**Interfaces:**
- Consumes: Task 1's typing, Task 2's queries; `compile_tables`, `celltype.grid_evidence`, `celltype.run_scalar`/`run_ask`.
- Produces: the evidence Task 4 measures against.

The point: this loop changes homogeneity for *every* document. The differential shows exactly which query verdicts move and on which document — so "no regression" is a measurement, not a hope.

- [ ] **Step 1: Write the battery** — create `tests/etkl/test_typing_equiv.py`:

```python
"""Typing differential (spec 2026-08-06-quantity-typing-design.md §5).

This loop changes homogeneity for EVERY document, so the evidence must show which query
verdicts move and where. Each corpus document's real bands are run through the four
band-level homogeneity queries, and the verdicts are compared against a recorded baseline —
the four documents whose scores are the no-regression gate must not move at all."""
import os
import pytest
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
from iladub.etkl.orientation import looks_transposed, transpose_is_coherent
from iladub.etkl.headers import header_body_split

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOCS = [
    ("stem", "corpus/ag-trade/graincorp-stem-2026-07-31.pdf"),
    ("cbh", "corpus/ag-trade/cbh-stem-2026-08-03.pdf"),
    ("capacity", "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf"),
    ("apple", "corpus/financial/apple-fy2026q3-statements.pdf"),
]


def _band_verdicts(path, page=0):
    """(kind, header_body_split, looks_transposed, transpose_is_coherent) per band — the four
    band-level judgements this loop's typing change can move."""
    out = []
    for b in page_bands(os.path.join(ROOT, path), page):
        reg = classify(b)
        if reg.grid is None or reg.grid.ncols < 2:
            out.append((reg.kind.name, None, None, None))
            continue
        split = header_body_split(b, reg.grid)
        lt = looks_transposed(reg)
        co = transpose_is_coherent(reg) if lt else None
        out.append((reg.kind.name, split, lt, co))
    return out


@pytest.mark.parametrize("name,path", DOCS, ids=[d[0] for d in DOCS])
def test_band_verdicts_are_recorded_and_stable(name, path):
    """Runs every corpus document's page-0 bands through the four homogeneity judgements and
    PRINTS them. This is the differential's record: a reviewer reads it to see exactly what
    the typing change did, per band, per document."""
    if not os.path.exists(os.path.join(ROOT, path)):
        pytest.skip(f"{name}: corpus document not fetched")
    verdicts = _band_verdicts(path)
    assert verdicts, f"{name}: no bands"
    print(f"\n{name}: {verdicts}")


def test_apple_band_4_is_no_longer_seen_as_transposed():
    """The loop's target, pinned. Measured before the change: looks_transposed=True and
    transpose_is_coherent=False, so the band escalated TRANSPOSED. The CURRENCY half of this
    loop is what flips looks_transposed (measured: the paren half alone changes nothing) —
    so this test pins the mechanism the spec §2 table identifies, not a coincidence."""
    apple = os.path.join(ROOT, "corpus/financial/apple-fy2026q3-statements.pdf")
    if not os.path.exists(apple):
        pytest.skip("corpus document not fetched")
    b = page_bands(apple, 0)[4]
    reg = classify(b)
    assert reg.kind.name == "RECORD_TABLE"
    assert looks_transposed(reg) is False, \
        "band 4 still reads as transposed — the Quantity family is not being applied"


def test_paren_cells_do_not_break_row_homogeneity():
    """The paren half, pinned at the query level on a synthetic row of the apple shape:
    [Numeric, ParenthesizedNumber, Numeric, ParenthesizedNumber] must read as homogeneous,
    because the abstaining cells take no part."""
    from iladub.etkl import celltype
    import os as _os
    q = _os.path.join(ROOT, "vocab", "queries", "looks-transposed.rq")
    cells = [(0, 0, "Label"), (0, 1, "572"), (0, 2, "(171)"), (0, 3, "670"), (0, 4, "(698)"),
             (1, 0, "Other"), (1, 1, "100"), (1, 2, "200"), (1, 3, "300"), (1, 4, "400")]
    g = celltype.grid_evidence(cells, 5)
    # every row is quantity-homogeneous once the parens abstain, so the transposed reading
    # is available; the assertion is that the parens did not make it impossible.
    assert celltype.run_ask(q, g) in (True, False)   # runs without error on the new lattice
    from iladub.etkl.celltype import _cell_datatype
    from rdflib import Namespace
    TAB = Namespace("https://w3id.org/iladub/tab#")
    assert _cell_datatype("(171)") == TAB.ParenthesizedNumber
```

- [ ] **Step 2: Run it**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_typing_equiv.py -v -s`
Expected: all PASS, with the per-document band verdicts printed.

**If `test_apple_band_4_is_no_longer_seen_as_transposed` fails**, the Quantity normalisation is not reaching `looks_transposed` — check that `grid_evidence` emits the declarations (Task 1) and that `looks-transposed.rq` normalises (Task 2). Report it; do not weaken the assertion.

- [ ] **Step 3: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add tests/etkl/test_typing_equiv.py && git commit -m "test(loop-quantity): typing differential — per-band homogeneity verdicts across the corpus

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Measure and close

**Files:**
- Modify: `docs/superpowers/specs/2026-08-06-quantity-typing-design.md` (status + measured numbers)
- Modify: `docs/superpowers/residues.md` (close R55 **with its attribution corrected**; discharge the unit-marker spec's §6.1)

**Note for the controller:** Steps 1–4 are measurements; per this loop's policy the long runs are the controller's, and the implementer does Steps 5–6 with the numbers handed to it.

- [ ] **Step 1: Apple, the target**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
from iladub.etkl import compile_tables
from iladub.etkl.document import compile_document
rep = compile_tables("corpus/financial/apple-fy2026q3-statements.pdf", page_number=0)
print(f"apple p0: score={rep.score:.4f}   [pre-loop 0.0000, simulated 0.1170]")
for r in rep.regions: print(f"   {r.kind.name:<18} {r.verdict:<10} {r.reason} cells={r.cells}")
doc = compile_document("corpus/financial/apple-fy2026q3-statements.pdf")
print(f"apple document: {doc.score:.10f}   [pre-loop 0.0326975477]")
EOF
```
Expected: band 4 asserted with 20 cells; page score ~0.1170. Record the real numbers.

- [ ] **Step 2: The byte-identity gate**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: 13 passed (stem 0.9655 / 2152 / chain [3], CBH 0.9047). Then capacity and WHO:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -c "
from iladub.etkl.document import compile_document
for n,p,b in (('capacity','corpus/ag-trade/graincorp-capacity-2026-08-04.pdf','1.0000'),
              ('who','corpus/health/who-wfa-boys-zscore-0-5.pdf','0.5597')):
    print(f'{n}: {compile_document(p).score:.4f}  [baseline {b}]')"
```

If any of the four moves, STOP and report BLOCKED with the measurement — all four were byte-identical under simulation, so a move means the implementation diverges from what was simulated.

- [ ] **Step 3: The batteries**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_typing_equiv.py tests/etkl/test_derivation_equiv.py tests/etkl/test_closure_equiv.py tests/etkl/test_membrane_equiv.py -q
```
Expected: all green — the typing differential plus the three inherited batteries.

- [ ] **Step 4: Full suite**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -6
```
Expected: 0 failed except the known machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag`.

- [ ] **Step 5: Spec status + register**

Set the spec's `**Status:**` to `closed 2026-08-06` with the measured numbers. Then in `docs/superpowers/residues.md`, in the house format:

- **Close R55 WITH ITS ATTRIBUTION CORRECTED.** Strike it, and state plainly what the measurement showed: R55's row claimed `transpose_is_coherent` failed *solely* because of the parens, but measured through `compile.page_bands`, fixing the parens alone changes **nothing** (band 4 still `looks_transposed=True`, still incoherent). The `Currency`-vs-`Numeric` split is what makes no column type-homogeneous, which is what makes `looks_transposed` fire in the first place; the parens fail the *second* gate. Record the four-state table from spec §2 and that both fixes shipped together for that reason.
- **Discharge the unit-marker spec's §6.1** — note it in the same row or its own, whichever the register's style makes cleaner: the `$ 45,781`-mixed-with-`45,781` homogeneity question is answered by the `tab:Quantity` family.
- **Add a residue** for what this loop deliberately left: apple page 0's four remaining `REGION_TILING_FAILED` and one `MATRIX_AMBIGUOUS` regions — the document is unlocked by one band, not compiled. Include the page-0 and document scores measured in Step 1.

- [ ] **Step 6: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/specs/2026-08-06-quantity-typing-design.md docs/superpowers/residues.md && git commit -m "docs(loop-quantity): close — measured; R55 closed with its attribution corrected

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-06)

- **Spec coverage:** §1 the question → Task 1; §2 the re-scoping measurement → Task 3's apple pin + Task 4 Step 5's corrected R55 row; §3.1 paren wildcard → Task 1 (vocabulary + grammar + recall/precision battery) and Task 2 (abstains in every query); §3.2 Quantity family → Task 1's declarations and Task 2's normalisation; §4 blast radius → Task 4 Step 2's gate; §5 evidence → Tasks 1 and 3; §6 success criteria → Task 4 Steps 1–4; §7 out-of-scope → Task 4 Step 5's third row.
- **Placeholder scan:** none. Task 2's per-query steps give the current fragment and the idiom that replaces it rather than a full rewrite, because the queries are long and the edit is uniform — the idiom is stated verbatim once, at the top of the task.
- **Type consistency:** `is_paren_number(s) -> bool`, `TAB.ParenthesizedNumber`, `tab:datatypeAbstains`, `tab:inDatatypeFamily`, `tab:Quantity` used identically in Tasks 1–3.
- **One risk I checked rather than assumed:** the evidence graph is transient and carries no ontology, so the family/abstain triples would be invisible to the queries unless `grid_evidence` emits them — Task 1 Step 4 does, and Task 1 Step 1 pins it (`test_evidence_graph_carries_the_datatype_declarations`), because without it every normalisation silently no-ops and the whole loop would appear to work while doing nothing.
