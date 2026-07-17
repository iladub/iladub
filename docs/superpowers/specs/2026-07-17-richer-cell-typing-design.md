# Richer Cell Typing — Date/Currency Body-Signals (Neurosymbolic Loop B2b) — Design

**Date:** 2026-07-17
**Status:** Design approved (scope + mechanism settled; generalized query + detectors feasibility-proven); ready for implementation plan.
**Governed by:** CLAUDE.md §8 (gate, open/closed split) + the B2a disambiguation roadmap (`docs/superpowers/specs/2026-07-16-typed-cell-evidence-graph-design.md` §9).
**Builds on (shipped):** loop B2a — the typed-cell evidence graph with the **open `tab:cellDatatype` lattice** (the seam this loop extends).

---

## 1. Goal

B2a lifted the type/orientation decisions to SPARQL but kept the **numeric-homogeneity** proxy, so only *numeric* columns signal the body — date/currency tables escalate. B2b is a **capability** loop: add **Date** and **Currency** as format-decidable **body-signal** types and generalize the decision queries from "all-Numeric" to **homogeneous non-Text**, gaining real recall on date and currency tables — **with zero numeric regression** (Numeric stays exactly `is_numeric`) and while keeping the conservative escalate-floor for genuinely ambiguous columns. This is a *behaviour change*, so its anti-overfit gate is a **desired-behaviour + no-numeric-regression + precision** battery (not a differential-vs-old-Python oracle). Body-signal set this loop: **{Numeric, Date, Currency}**; Boolean/Code and the knowledge/NEURAL disambiguation layers remain deferred (B2a §9 roadmap).

## 2. Gate compliance (CLAUDE.md §8)

- **AXIOM — derivation (open world) → SPARQL.** The generalized decision queries recover the boundary/count/orientation from the typed-cell evidence graph. No SHACL, no tuned constant.
- **PROCEDURAL (justified; Python = reference language):** `is_numeric` (unchanged) + the new `is_date`/`is_currency` — raw datatype detection by **format-decidable grammars** (regex + range checks). A date/currency regex is a *format spec*, not a tuned tolerance (same character as `is_numeric`'s float-parse). The evidence-graph emitter + query runner (`celltype.py`) — engine glue. No decision logic.
- **Not a differential oracle:** behaviour intentionally changes (date/currency columns now split). Correctness is pinned by three batteries (§7), of which the numeric one *is* the B2a differential oracle (unchanged).

## 3. Architecture — extend the lattice + detectors + generalize the queries (feasibility-proven 2026-07-17)

The evidence-graph shape is **unchanged** (B2a's open lattice) — B2b only enriches the type at the single classification point and generalizes the query clauses. No re-architecting.

**Classification (celltype, PROCEDURAL) — order matters (Numeric first ⇒ untouched):**
```
cellDatatype(t) = tab:Numeric   if is_numeric(t)        # unchanged: % and commas stay Numeric
                = tab:Date       elif is_date(t)
                = tab:Currency   elif is_currency(t)
                = tab:Text       else
```
Date/Currency are only ever assigned to cells `is_numeric` calls non-numeric (former Text) — so the **Numeric bucket is byte-identical**, guaranteeing no numeric regression.

**Detectors (conservative, high-precision — proven):**
- `is_date`: a full date shape with a **4-digit year** and valid month(1–12)/day(1–31) ranges — ISO `YYYY[-/]MM[-/]DD`, `DD[-/]MM[-/]YYYY`, and `D Mon YYYY` month-name forms. The 4-digit-year + range requirement excludes `"1-2"`, `"3-4"`, `"99-99-9999"`, `"2024-13-01"` (→ Text). *(Precision-proven.)*
- `is_currency`: a recognized symbol (`$ € £ ¥`) adjacent to a numeric body (leading or trailing), e.g. `$1,000`, `€20.50`. A bare `$` → Text.

**Query generalization — "all-Numeric" → "homogeneous ∧ non-Text" (proven):** today a data column is `NOT EXISTS { a cell != tab:Numeric }`. Replace every such clause (all four `.rq`) with:
```sparql
# column/row-scope is a DATA (body-signal) column/row iff: no Text cell AND type-homogeneous.
FILTER NOT EXISTS { ?xt <scope> ; tab:cellDatatype tab:Text }                         # no free-Text cell
FILTER NOT EXISTS { ?a <scope> ; tab:cellDatatype ?at . ?b <scope> ; tab:cellDatatype ?bt . FILTER(?at != ?bt) }   # homogeneous
```
This **subsumes** the numeric case (all-Numeric → homogeneous, no Text → data — verified identical), **adds** pure Date/Currency columns, and **escalates** mixed-type columns. It never enumerates the type set — `tab:Text` is the sole non-signal marker, so B2c/Boolean/etc. extend the lattice without touching the queries again.

## 4. The four decisions (all generalized identically)

- `header-body-split.rq` — MIN body-start row where some column is a data column (homogeneous non-Text) from there. *(Proven: numeric no-regression, date/currency recall, dash-not-date→None.)*
- `stub-data-split.rq` — leading text-stub count; data columns = the homogeneous-non-Text contiguous suffix.
- `looks-transposed.rq` — a typed **structured** body ROW (cols≥1 homogeneous non-Text) but no typed structured COLUMN.
- `transpose-coherent.rq` — every value row homogeneous in a single type (col≥1). **Nuance:** this makes coherence *type-exact* (a Date+Currency row is now incoherent) rather than the old binary "all-numeric-or-all-not" — a stricter, more correct coherence, and it **must** generalize together with `looks_transposed` (else a currency-transposed table would be detected but wrongly rejected). The precision battery guards this.

## 5. Components

| Unit | Responsibility | Gate |
| --- | --- | --- |
| `src/iladub/etkl/celltype.py` (modify) | classify into `Numeric`/`Date`/`Currency`/`Text` (add `is_date`/`is_currency` detectors) | PROCEDURAL |
| `vocab/queries/{header-body-split,stub-data-split,looks-transposed,transpose-coherent}.rq` (modify) | generalize the "all-Numeric" clause to "homogeneous non-Text" | AXIOM |
| `vocab/ontology/tab.ttl` (modify) | add `tab:Date`, `tab:Currency` individuals of `tab:CellDatatype` | owned vocab |
| `tests/etkl/test_celltype.py` (modify) | detector precision tests + the three decision batteries (§7) | test |

The detectors live in `celltype.py` (not `headers.py`) to keep `is_numeric` unchanged and colocate the typing family; `celltype.py` already imports `is_numeric`.

## 6. Data flow

Unchanged from B2a except the type value: `is_numeric`/`is_date`/`is_currency` → `cellDatatype ∈ {Numeric, Date, Currency, Text}` → `grid_evidence` → the generalized `.rq` → the four functions' unchanged signatures.

## 7. Testing — three batteries (NOT a differential oracle; behaviour changes)

- **(1) No-numeric-regression = the B2a differential oracle, unchanged.** Every B2a numeric fixture (the frozen `_ref_*` battery) must return **exactly** what it did — the generalized query provably subsumes numeric, and Numeric typing is untouched. This is the hard no-regression gate.
- **(2) Desired-behaviour (recall).** New fixtures: a **pure-date** column table splits at the date column; a **currency** table splits; `stub_data_split` with date/currency data columns; `looks_transposed`/`transpose_is_coherent` over a currency/date-typed transposition. Assert the *new* correct answers.
- **(3) Precision (no over-typing / over-splitting).** `is_date` rejects `"1-2"`, `"3-4"`, `"99-99-9999"`, `"2024-13-01"`; `is_currency` rejects bare `$`; a **free-text** column is not a body-signal; a **mixed-type** column (Date+Currency, or Date+Numeric where no homogeneous suffix exists) escalates. `"1-2"/"3-4"`-column → `header_body_split` None. Detector-level unit tests for every grammar decision.
- **Behavioural suites** (`test_headers`, `test_rowheaders`, `test_orientation`, `test_matrix`, `test_hierarchical`, `test_segment`, end-to-end compile) stay green — a genuinely-numeric fixture must not change; a fixture that *starts* asserting a date/currency table (new recall) is a deliberate, reviewed change, not a regression (investigate each).

## 8. Source ownership / conventions

- `tab:Date`/`tab:Currency` are owned `tab:` individuals in the standalone `tab.ttl`. The `.rq` reference only `tab:` + standard SPARQL. No HGA/FnO term as a subject.

## 9. Honest gaps & scope boundaries

- **In scope:** Date + Currency body-signals; the homogeneous-non-Text query generalization; the three-battery gate.
- **Out of scope:** Boolean and Code/Id (Code/Id is the least format-decidable — belongs with the knowledge/NEURAL layer, not cheap AXIOM typing); `regions.classify` (B2c); the **knowledge-first** and **NEURAL propose→oracle→dispose** disambiguation layers (B2a §9 roadmap) for genuinely free-text/categorical columns — those still escalate (the floor). `is_numeric` unchanged.
- **Conservative by construction:** only same-exact-type homogeneous non-Text columns signal the body; a mixed column takes the first homogeneous suffix (identical to B2a) — it does not over-split. Genuinely ambiguous columns escalate (credibility over completeness).
- **Transpose-coherence is now type-exact** (§4) — the one behaviour subtlety; guarded by precision battery (3) + the behavioural suite.

## 10. Settled design decisions (for the implementation plan)

- **Body-signal set: {Numeric (unchanged), Date, Currency}.** Boolean/Code deferred.
- **Numeric = `is_numeric` byte-identical** (detectors apply only to non-numeric cells) → no numeric regression; the B2a differential oracle is the no-regression gate.
- **Query generalization: "homogeneous ∧ non-Text"** (proven), applied to all four `.rq`; `tab:Text` is the sole non-signal marker (future types need no query change).
- **Detectors: conservative format grammars** (4-digit-year dates + range checks; symbol-adjacent currency) — proven high-precision.
- **Anti-overfit = three batteries** (no-regression + recall + precision), not a differential oracle.

**Resume pointer:** design committed on `main`. **Next action:** invoke `superpowers:writing-plans` → task-by-task plan (detectors + lattice + detector precision tests → generalize the four `.rq` + the three decision batteries → supersession/gate) → subagent-driven execution. **After B2b:** B2c (`regions.classify`), then the knowledge-first + NEURAL disambiguation layers and loop two.
