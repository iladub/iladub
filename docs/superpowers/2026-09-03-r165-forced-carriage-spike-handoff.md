# Handoff — R165's forced-carriage spike was run and refuted; the successor is a band-split question, not a carriage one

**Topic:** the R161 handoff's part 5 (PROPOSED) — *forced carriage of band 2's header onto apple p0
band 3 makes it pass `CoverageShape`*. RUN on all three apple pages. **Refuted on the mechanism**;
R165's diagnosis confirmed; `R166` raised on the way.

**Part 5 was written first, under the 50K originating floor** (this session's working figure was
~45K when this file was started; the status line was not read, the figure is the model's own
estimate). Per `CLAUDE.md` § "The handoff's next action is TYPED", part 5 is graded per action.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

Read `docs/superpowers/2026-09-03-r165-forced-carriage-spike.md` § 2–3 for the readings, not this
file. Re-run the instrument if the compile has changed since `5d7e47d`:

```
PYTHONPATH=. .venv/bin/python scripts/forced_carriage_spike.py corpus/financial/apple-fy2026q3-statements.pdf 0
```

### PROPOSED — the prediction the successor must RUN before designing anything

**Prediction:** apple p0 compiles as **one matrix table** — under band 2's `Three Months Ended /
Nine Months Ended` column header, with every section heading (`Operating expenses:`, `Earnings per
share:` …) read as a row header the way `mtable2` already reads `Net sales:` as `rh0` — if bands 2–7
are handed to `compile_tables` as **one band** instead of six. If it does, R165's fix is in
`page_bands`' band split (do not cut at a section heading inside one `tab:ruleXsSignature`), and no
carriage seam is involved at all. If it does not — if the matrix reader refuses the 30-odd-line band,
or `classify_matrix` cannot find the header once section headings sit inside the body — then the
matrix reader is the subject, and the second design (a carried block built from the matrix
column-header tree) is the fallback to spike next.

**Cost to check:** one spike, minutes — build the merged band from `page_bands`' six (`Band` is
a lines container; MEASURE how `page_bands` constructs one and whether `is_matrix_candidate` /
`classify_matrix` take a `Band` alone) and call `assert_matrix_region` + `region_tiles` on it
directly, the way `compile.py:826-835` does.

**Why proposed, not asserted:** nobody has fed the matrix reader a band with section headings
*between* body rows; `mtable2` has them (`Net sales:`, `Cost of sales:`) but only ever inside a
band that `page_bands` had already cut short. The prediction rests on the `rh0..rh8` reading of
band 2 and on the shared rule signature — not on any run.

### PROPOSED — what the spec must rule, together

R165's fix re-opens **R160** (apple p1's lost datagrid adoption) and subsumes **R166** (p0 band 4
and p2 band 6 asserting a data row as their header): a one-band reading of the statement reads
those two bands under the real column header, so whatever the spec decides about R165 decides
R166 too. One spec, three rows. Do not fix R166 on its own first — that fixes a symptom.

---

## 1. Goal

Run the falsifying spike R165's remedy rested on, before anything was designed on it; record the
outcome in the register; measure the false-assertion the previous handoff left unverified.

## 2. Where the primaries are

| where | what to establish there |
| --- | --- |
| `scripts/forced_carriage_spike.py` | the instrument: per-page census (verdict, `header_reading`, `-lc0` label text, escalated bands' `header_rows_of`), the hand-built reading, the forced compile |
| `docs/superpowers/2026-09-03-r165-forced-carriage-spike.md` | the readings pasted verbatim (§ 2), the three refusals (§ 3), the two candidate designs (§ 4), R166's measurement (§ 5) |
| `tests/test_forced_carriage_spike.py` | `synthetic_reading` pinned; the seam's refusal of a section-heading header row pinned beside its falsifying twin (a redrawn block matches) |
| `docs/superpowers/residues-open.md` (`R165`, `R166`) · `residues.md` | R165's "what would close it" struck and rewritten; R166's full row |
| `src/iladub/etkl/ruledroles.py:384` (`carried_roles_for`) · `:486` (`resolve_ruled_header_rows`) | the seam matches a REDRAWN block, row by row, ending on the leaf; `if not header_rows or not reading.rows: return None` |
| `src/iladub/etkl/compile.py:826-860` (matrix branch) · `:873-898` (loop L + the only `carried=` call site) | why band 2 mints no `CarriedHeaderReading`: the matrix branch returns a `RegionReport` without one |
| `src/iladub/etkl/compile.py:270` (`page_bands`) | the seam the PROPOSED successor would touch — not read by this session beyond its signature |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The forced-carriage prediction is REFUTED; R165's carriage remedy is struck | `residues-open.md` R165 last cell; evidence doc § 3 |
| R165's diagnosis (no column header) is CONFIRMED at the mechanism | evidence doc § 3.3; R165 row |
| R166 raised: data row asserted as header on p0 band 4 / p2 band 6 | `residues-open.md` R166; `residues.md` index; evidence doc § 5 |
| R165 + R160 + R166 are one spec | R165 and R166 rows; this file § 5 |
| The successor's first spike is the one-band matrix prediction | **this file § 5 only** — nowhere else; reversible |

## 4. Unverified or assumed

- **The one-band matrix prediction in § 5 has NOT been run.** It is the successor's first act.
- Neither candidate design in the evidence doc § 4 was tried or costed.
- The p1 hand-built reading took `ASSETS:` as its leaf (band 2's third line on p1 is a section
  heading); harmless to the result, noted in the evidence doc § 6.
- Whether any other corpus document's record-table reader asserts a first data line as header was
  not censused; R166 is apple-only.
- The working-token figure is the model's estimate; the status line was not read.
- Suite: only `tests/test_forced_carriage_spike.py`, `tests/test_residue_register_integrity.py` and
  `tests/test_doc_governance.py` were run locally (recorded in the commit); no `src/` file changed.
