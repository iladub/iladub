# Handoff — R161 is measured and closed: apple's escalated bands are header-less continuations, not unrecognized sections

**Topic:** `R161` — *why loop Q's section repair never fires on apple p0/p2*. The measurement the row
asked for was RUN, with a committed instrument. It closes R161 and raises `R165`, the successor.

**Part 5 was written before parts 1–4, past the 50K originating floor** (this session's working figure
is estimated at 80–90K; treated as over — logged as a handoff). Per `CLAUDE.md` § "The handoff's next
action is TYPED", part 5 is graded per action.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

**Read the evidence doc, not this file, for the readings:**
`docs/superpowers/2026-09-03-r161-section-repair-measured.md`. Re-run the instrument if anything
about the compile has changed since `4cfee38`:

```
PYTHONPATH=. .venv/bin/python scripts/section_repair_census.py corpus/financial/apple-fy2026q3-statements.pdf
```

### PROPOSED — the prediction the successor loop must RUN before designing anything

**Prediction:** on apple p0, handing band 3 the header reading band 2 asserted — through the seam
that already exists, `compile_tables(..., carried_header_roles={3: <band 2's reading>})`
(`src/iladub/etkl/compile.py:570`, loop M's page-to-page carriage) — makes band 3 pass
`CoverageShape` and assert. **If it does, the successor loop is an intra-page continuation licence
plus the existing carriage; if it does not, the coverage gap is not "missing header" and the loop
this handoff imagines is not the loop to run.** Cost to check: one forced-carriage spike, minutes.
What `<band 2's reading>` has to be is the first thing to MEASURE: `document.py:1435` builds it
from a page-level `continuation-of.rq` match, and nothing on the same page has ever produced one.

**Why proposed, not asserted:** nobody has ever driven `carried_header_roles` from a band on the same
page; the reading object it expects may carry page-scoped assumptions (origin agreement across a
page break). The prediction rests on the coverage message alone.

### PROPOSED — the maintainer's choice, and what it touches

R165's fix will re-open **R160**: apple p1's lost datagrid adoption was masking the same defect
(p1 bands 3, 5, 7 refuse on the same coverage gap). A fix that asserts the section bands under a
carried header changes which reader has authority on p1, so R160 and R165 are one design decision
with two faces, and should be specified together, not in sequence.

---

## 1. Goal

Measure why `sectiongraph.section_candidates` recognizes no section on apple's eight
`REGION_TILING_FAILED` bands, as R161's closing condition required; size the successor from what the
measurement finds, not from the row's framing.

## 2. Where the primaries are

| where | what to establish there |
| --- | --- |
| `scripts/section_repair_census.py` | the instrument: band census, section evidence graph + groups, and the SHACL shapes that refused each band, per page |
| `docs/superpowers/2026-09-03-r161-section-repair-measured.md` | the readings, pasted verbatim, and the three-way diagnosis |
| `docs/superpowers/residues-closed.md` (`~~R161~~`) · `residues-open.md` (`R165`) | the closure evidence and the successor's full row |
| `src/iladub/etkl/sectiongraph.py:103` (`_leading_box_y`) · `:48` (`_header_box_text`) | why apple emits the signature half but not the header-box half of the section identity |
| `vocab/queries/section-repeat.rq` | the identity is `headerBoxText` AND `ruleXsSignature`, verbatim — a repeated *shape with the same printed header*, which apple's sections are not |
| `src/iladub/etkl/document.py:1435-1466` · `compile.py:570` | loop M's page-to-page carriage — the seam the successor would reuse, never yet driven intra-page |
| `tests/test_section_repair_census.py` | the instrument's report parser, pinned and falsified (severity filter inverted → 1 failed) |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| R161 CLOSED — the measurement is the closing condition, and it was run | `residues.md` index line; `residues-closed.md` row |
| Section repair is the WRONG instrument for apple — not a recall defect in it | evidence doc § 4; R165's "why deferred" column |
| The eight refusals are one defect: `CoverageShape` on header-less section bands | evidence doc § 3; R165 |
| R165 raised; its fix and R160 are one design decision | R165 row; this file § 5 — **nowhere else yet** |
| The instrument is committed, not left in a scratchpad | `scripts/section_repair_census.py` |

## 4. Unverified or assumed

- **The forced-carriage prediction in § 5 has NOT been run.** It is the successor's first act.
- **p0 band 4 and p2 band 6 ASSERT with no header of their own** (`Operating income 35,695 …` and
  `Increase in cash …` are their first lines). What they asserted as a header row was not inspected.
  If a data row was read as a header, that is a false assertion inside the membrane — a §7 defect
  worth a row of its own once measured. Not raised, because not measured.
- The degenerate `_leading_box_y` candidate (a 0.96pt inter-cell gap read as a header box) is
  described, not fixed; whether it costs recall on any *repeated-section* document is not measured.
  `R48` is the standing row for that class.
- The working-token figure is an estimate; the status line was not read.
- `-m "not corpus"` suite: only the register-integrity, doc-governance and the new test were run
  (recorded in the commit); no `src/` file changed.
