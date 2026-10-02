# Spec — a total printed beneath several totals binds when a reader names its role and the arithmetic holds

**Serves:** prog:criterion:etkl:03 — loop (b) of the [[R261]] totals family: cbh p0's grand total
`1,951,264`, the only asserted content left inside cbh's 86-token hold.

**Date:** 2026-10-02. **Branch:** `r261-grand-total-spec`, cut from `r261-grand-total-probe` at
`dfc8be9` (PR #291, which carries the P4/P4b evidence this spec stands on).

**Doc impact: increment.** § 4 moves the total-of-totals level from *reserved* to *used* in the
comments of `tab:aggregates` and `tab:totalOf`, and adds one constraint to `tab:PrintedTotalShape`. No class or property is added; no published term changes
meaning.

**Provenance of the design.** §§ 2–6 were presented in sections and approved by the maintainer in
chat on 2026-10-02 (*"looks right"*). Until this file, the only record was the handoff
`docs/superpowers/2026-10-02-r261-grand-total-write-spec-handoff.md` part 3. The question, its
population, its decision rule and the derived-crop ruling come from
`docs/superpowers/2026-10-02-r261-grand-total-role-probe.md` (P4/P4b). Seams in § 7 were measured
at `dfc8be9` by a subagent; each states RUN or READ.

This spec **extends** the table-level spec `specs/2026-10-01-r261-totals-family-design.md` and
**replaces its § 2 step 2's second bullet** (the total-of-totals level as first sketched), which P3
refuted as worded (R261 evidence § 6). Everything else in that spec stands and is cited, not
restated.

---

## 0. The concerns, first — and the rulings this spec obeys

**Concern 1 — [[R287]]: the worker's protection beyond the arithmetic is thin.** On the derived
crop this loop uses, the worker called an in-table cell (`22,858`, ESPERANCE's last Volume value)
`table_total` ×3 (P4b § 4). That binds nothing, since only `total_of_totals` binds. But what the
worker adds over the exact sum rests on **n = 1 target and 4 nulls**, and **no corpus document
offers the coincidence class** it exists to catch: a lone number equal to the sum of a page's bound
totals that is *not* a grand total. The conjunction is therefore exercised in the corpus only on
the side where both halves agree. The CI fixture (§ 6.2) pins the other side synthetically; the
corpus cannot.

**Concern 2 — the Note is ignored, not read.** Once `1,951,264` is carved from band 9, the Note
that shares the band classifies `NON_TABLE` → `ignored` (§ 7 S5: the classification was RUN on the
carved remainder; the dispatch to `emit_ignored_band` was READ). cbh's score then rises because a caveat the page asserts leaves the denominator — the
table-level spec's § 0 concern and ruling R-d, unchanged. **Lifting cbh's hold is the maintainer's
call, not this loop's.** The loop delivers the cell dump and this paragraph; it does not
adjudicate.

| # | Ruling | When, by whom |
|---|---|---|
| R-a … R-d | Table-level rulings: worker AND exact sum; grand total in scope; bind at band dispatch, carve, reclassify the remainder; the Note's fate is normal classification, disclosed. | Maintainer, 2026-10-01 — table-level spec § 0 |
| R-e | **Spec on the DERIVED crop.** The `22,858` miss is stated first (concern 1) and recorded as [[R287]], not tuned away by a narrower crop now. Rejected: a column-scoped crop measured first; a ruling instead of a worker (exact sum alone, or leave the grand total unbound). | Maintainer, 2026-10-02 — P4b evidence § 5 |
| R-f | **Operands are the TABLE-LEVEL PrintedTotals only** (those carrying `tab:totalOf`) — the whole set, never a subset, at least 2. This refines the 2026-10-01 wording *"every PrintedTotal bound on the page"*: a bound grand total never sums into a later one. Identical on cbh. | Maintainer, 2026-10-02 — design § 1 |
| R-g | **No adjacency requirement on the candidate.** Any lone-numeric line in a later band on the page is a candidate; the arithmetic and the worker decide. Adjacency would be a position heuristic (CLAUDE.md § 8). | Maintainer, 2026-10-02 — design § 1 |
| R-h | **No new class.** A grand total is a `tab:PrintedTotal` without `tab:totalOf` whose `tab:aggregates` point at PrintedTotals. Its level follows from its links; nothing stores it as a label. | Maintainer, 2026-10-02 — design § 3 |

## 1. The goal

Bind cbh p0's `1,951,264` as a `tab:PrintedTotal` aggregating the four bound port totals, when the
exact `Decimal` sum of the page's table-level PrintedTotals equals it **and** the worker answers
`total_of_totals` on the derived crop. Carry it into the document graph through R7's pass-2
adoption. Nothing in the mechanism names cbh; on every other corpus page it must be inert (§ 6.3).

## 2. The mechanism — a second level in `_bind_printed_totals`

The totals level sits **beside** the table level inside `compile._bind_printed_totals`, **not gated
by it**. Today the function returns at its first guard unless the previous report is `asserted` with
a `table_uri` (`compile.py:1027`). On cbh r2 band 9's previous report is band 8's carved
PrintedTotal band (`asserted`, `table_uri None`), so band 9 is never tried (§ 7 S1, RUN). The totals
level must run on exactly the bands that guard turns away.

Per band, per candidate line (`totals.candidate_lines` — the table level's lone-numeric rule,
reused, no second parser):

1. **Table level first.** A line it binds is not asked at the totals level.
2. **Totals level.** Operands = every table-level PrintedTotal bound in this page's graph so far
   (R-f). `totals.match_totals(value, operands)` — written for this, unwired today — returns the
   operand URIs iff ≥ 2 operands and their exact sum equals the value. No match ⇒ the worker is not
   asked and nothing happens.
3. **Worker** (§ 3), asked only on a match. Binds only on `total_of_totals`.
4. **On a bind** — the table level's bind, unchanged in kind: emit the PrintedTotal (no
   `tab:totalOf`; `tab:aggregates` → the operands); record `brec.record("printed_total",
   ["total", "not_total"], …)` with a rationale **derived from the arithmetic only** (*"totals level:
   the N table-level PrintedTotals on this page sum exactly to V"*), never from model text; carve the
   line; book its word asserted; reclassify the remainder. An empty remainder emits no band.

On cbh the prediction is: bands 2/4/6/8 bind at table level as today; band 9's line 0 matches the
four, the worker answers `total_of_totals`, it binds and carves; band 9's remainder (the Note)
classifies on its own (concern 2).

## 3. The worker — `AskTotalRole`

A sibling module (working name `src/iladub/etkl/totalrole.py`) and BAML function `AskTotalRole`. It
**mirrors** `printedtotal.py`'s reader stack — frozen reading, reader protocol, fake reader, process
cache, BAML reader, recorded reader replaying `readings/total_role/{key}.json` and writing only under
`ILADUB_RECORD_READINGS=1`, live only under `BAML_LIVE=1` — rather than sharing it. Two questions,
two stacks; a shared stack would couple a measured instrument to an unmeasured one.

- **Answer:** closed `table_total | total_of_totals | other | cannot_tell`, **no note field** (the
  P1 leak, table-level spec § 3.2).
- **Wording:** P4b's, verbatim from `scripts/r261_grand_total_role_probe.py` `PROMPT`, with only its
  `Reply with JSON only` line replaced by `ctx.output_format`. Whether that substitution preserves
  P4b's answers is plan Task 1 (§ 6.1).
- **Crop:** the DERIVED one (R-e) — the union of each operand total's table band through its own
  line, plus the candidate line, as `derived_box` computes it in the probe. **Production draws the
  red box** on the candidate word.
  - **Derived from the graph, not from `bands[j].lines`.** By the time band 9 is reached, the carve
    has emptied the operand total bands (bands 2/4/6/8 keep only `top`/`bottom`). The table bands
    1/3/5/7 are intact, and each operand PrintedTotal carries its `tab:hasBBox` (§ 7 S1, RUN). The
    operand's table band is found **through its `tab:totalOf` link and our own URI minting**, as
    `_printed_total_bands` finds a band through its decision URI. It is never found as `j − 1`. The
    total line's extent is the PrintedTotal's box.
  - **The seam the plan must measure** is how a `tab:totalOf` table URI maps back to its band
    index in `compile_tables`' scope. Measure it; do not assume `htable{k}` ⇒ band `k`.
  - **The crop is built from r2's section-repaired bands**, as P4b's was. Those bands differ from
    pass 1 (band 1: 13 lines in r2, 18 in pass 1; § 7 S1), so the measured instrument *is* the r2
    crop. The 4 pt margin, 150 dpi render, 2 px stroke and 2 pt pad are the
  measured instrument's parameters, carried unchanged as `crop_table`'s 4 pt / 150 dpi are
  (`printedtotal.py:125-145` docstring) — rendering parameters of the image a reader sees, not a
  tolerance on any decision.
- **The drawn box is ink not on the page.** It is a pointer, like the value string in the prompt.
  It is never stored, never compared, and never reaches the graph.
- **Recorded-readings key:** sha256 of the question name, the value, and a listing of every cropped
  line (each operand table band's lines, then that operand's `tab:cellText`) with the candidate line
  last — text facts, **never the PNG** (as `printedtotal.question_key`,
  `printedtotal.py:158`). The listing covers every operand table band, so a recording moves when any
  word of any operand table moves.

## 4. Vocabulary and membrane

- **`tab:aggregates`** (`tab.ttl:157`) and **`tab:totalOf`** (`tab.ttl:176-185`): both comments
  today mark the total-of-totals level *RESERVED* (rulings R9/R4 of the table-level plan). Both move
  to *used*. The grand total is a PrintedTotal **without** `tab:totalOf` that aggregates
  PrintedTotals. `tab:totalOf` keeps `sh:maxCount 1 ; sh:class tab:Table` unchanged: a grand total
  carries no `totalOf` at all, so it never meets that constraint.
- **Already satisfied, measured (READ, `tab-shapes.ttl:533-538`):** `tab:aggregates sh:minCount 2`
  holds for a grand total of ≥ 2 operands. Today the shape puts no `sh:class` or `sh:node` on
  `tab:aggregates`, which is why the new constraint below is needed.
- **`tab:PrintedTotalShape`** (`vocab/shapes/tab-shapes.ttl`) gains one constraint, two halves:
  1. a PrintedTotal **without** `tab:totalOf` may aggregate **only** PrintedTotals;
  2. a PrintedTotal **with** `tab:totalOf` may aggregate **no** PrintedTotal.
  Each half ships a negative test that must fail (CLAUDE.md § Serialization). Both are closed-world
  constraints on what crosses the membrane (AXIOM/SHACL), never a derivation.
- **The arithmetic stays producer-side** — the sole enforcement, the R89 case, for the reason the
  table-level spec § 4 measured (cell text is `xsd:string`; membrane arithmetic reopens [[R92]]).

## 5. R7 extension — adopting the pass-2 grand-total band

cbh's tables assert only in section-repair pass 2, so table-level totals reach the document graph
only through R7 (`document._printed_total_bands`), which adopts a pass-2 band by its PrintedTotal's
`tab:totalOf` link into `adopted_tables`. A grand total has no `tab:totalOf`; without this extension
it is bound in pass 2 and never reaches the document graph.

**The extension:** `_printed_total_bands` also adopts a pass-2 band whose PrintedTotal
`tab:aggregates` a PrintedTotal that is `tab:totalOf` an adopted table — a graph link, not
adjacency. The existing refusal disjuncts (`document.py:1640`; the second is [[R286]]'s untested
one) apply unchanged.

## 6. Oracles, tests, acceptance

### 6.1 Plan Task 1 — the BAML-rendered question reproduces P4b (a proposition; it may fail)

Ask `AskTotalRole` through BAML on P4b's 6 cases on the derived crop, `REPEAT=3`, Haiku 4.5. **It
holds iff** `1,951,264` gets `total_of_totals` ×3 **and** no other case gets `total_of_totals`.
(`22,858` → `table_total` is R287's known miss and is outside the rule.) **If it fails, the wording
is not re-tuned:** the grand total goes back to the maintainer as a ruling (exact sum over admitted
totals alone, or unbound), and the loop stops short of binding.

### 6.2 CI tests — synthetic fixture, fake reader

Fixture: two tables each with a printed total, a lone grand-total line, and prose. The conjunction
is pinned from both sides:

| worker | arithmetic | expected |
|---|---|---|
| `total_of_totals` | holds | bound |
| `total_of_totals` | fails | **not** bound — the worker cannot bind alone |
| `table_total` / `other` / `cannot_tell` | holds | **not** bound — the arithmetic cannot bind alone |
| — (one table total bound) | — | the worker is **not asked** (`match_totals` needs ≥ 2) |

Plus: a bound grand total is not an operand of a later one (R-f); the remainder is classified on its
own; R7 adopts the pass-2 grand-total band by the `tab:aggregates` link; both shape halves fail
their negative tests. **Every task carries a `## FALSIFICATION` block** — delete each half of the
conjunction, the R-f filter and the R7 link, and show its test fail.

### 6.3 Corpus sweep (local; CI skips the corpus)

One test file per process, from a `.sh` under bash, serially. Predicted mover: **cbh only.** Any
other document moving is a finding, not a pin to update.

### 6.4 cbh

Pins that move are re-read, never re-pinned blindly (table-level spec § 5.4 names them). **Dump the
cells**, state concern 2 beside the dump, and hand the hold to the maintainer.

## 7. Seams — measured at `dfc8be9`

Measured by a subagent on `corpus/ag-trade/cbh-stem-2026-08-03.pdf`. It used the recorded-readings
reader with `BAML_LIVE` unset, so no API was called, and scratch scripts outside the tree, run as
`PYTHONPATH="$PWD" .venv/bin/python`. Everything was RUN unless marked READ. These are seams the
plan re-measures. They are not facts to build on.

**S1 — where the bind runs, and what it sees at band 9 (RUN).**
- **Call site:** `compile.py:1142`, in the band loop at `:1134`.
- **It runs in three compiles of p0:** pass 1, the section-repair pass `r2`
  (`section_repair_bands={1,3,5,7}`), and the datagrid-adopt compile (`document.py:1760`).
- **Indices are the same in pass 1 and r2:**
  - table bands 1/3/5/7;
  - port-total bands 2/4/6/8;
  - band 9 = `1,951,264` plus the Note;
  - band 10 = the PORT summary table;
  - band 11 = the ALB date box.
- **The port totals bind only in r2.** In pass 1 and in adopt the previous report is `escalated`.
  The final graph holds exactly `r2#printedtotal{2,4,6,8}-l0`, which reached it through R7.
- **⇒ the totals level is inert in pass 1 and in adopt.** No table-level operands exist there, so
  `match_totals` sees fewer than 2 and returns `None`.

**S2 — band 9's pass-1 record (RUN).**
- **The record:** `UNSUPPORTED_TABLE`, escalated, `KIND_NOT_SUPPORTED`, `table_uri None`;
  `#region9` carries a `CandidateConcept`.
- **Withdrawal:** `_remove_escalation_record` (`document.py:1003`) would withdraw it.
- **What it leaves standing:** `#region9-source` (`SourceRegion`, page, derivation). Every R7
  adoption does that today, so it is not new to this loop and stays out of scope.
- **The refusal check:** `document.py:1640` passes for band 9. Its pass-1 `table_uri` is `None` and
  no `IgnoredBand` exists. This confirms that § 5's extension is the only thing missing.

**S3 — [[R284]] exposure (RUN).**
- **`donors_for`** is called on p0 only for bands 10 and 11, in every pass, and returns `()` both
  times.
- **`donor_ev`** (`compile.py:1121`) is built from the uncarved bands and never mentions band 9.
- **⇒ no new R284 exposure on cbh.** R284 stays open, untouched.

**S4 — the carve on band 9 (RUN).**
- **The geometry:**
  - band 9 spans y 683.5–761.5;
  - its line 0, `1,951,264`, sits at y 683.5–689.5;
  - its Note lines sit at y 732.7–761.5;
  - band 9's extent encloses bands 10 (y 691.6–730.1) and 11;
  - no band-9 line overlaps a band-10 line in y.
- **The existing carve applies unchanged.** It removes the line by index at `compile.py:1072` and
  `_replace` keeps `top`/`bottom`. This is the interleave case its docstring names (`:1018-1023`).
  The carved word stays inside the band's extent for `build_ledger`.

**S5 — the remainder's class (RUN, then READ).**
- **RUN:** lines 1–4 classify `NON_TABLE` ("fewer than 2 columns") in pass 1 and in r2.
- **READ:** a multi-line `NON_TABLE` skips `offer_single_line` and reaches `emit_ignored_band`
  (`compile.py:1208-1227`).
- **⇒ concern 2's prediction holds:** the Note becomes `ignored`.

## 8. What is not done

- Labelled grand totals (`Total 1,951,264`); partial-set subtotals; cross-page grand totals.
- Reading the Note (table-level spec § 6's residue row covers it).
- [[R287]]'s column-scoped crop.
- [[R284]] and [[R286]] beyond what § 7 measures; neither is closed here.

## 9. Classification (CLAUDE.md § 8)

| decision | class | why |
|---|---|---|
| a line is one numeric token | PROCEDURAL | `totals.candidate_lines`, reused; raw extraction, exact |
| the table-level totals' sum equals the value | PROCEDURAL | decidable exact `Decimal` arithmetic (`match_totals`) |
| which totals are operands | PROCEDURAL | a graph fact: carries `tab:totalOf`, bound on this page |
| *what role does this number play* | NEURAL | a reader's judgement; disposed by the arithmetic, and vice versa |
| the crop and its red box | PROCEDURAL | raw extraction (page → pixels), measured instrument parameters, decides nothing |
| what may cross into the holon | AXIOM (SHACL) | `tab:PrintedTotalShape`, closed world |
| which pass-2 band R7 adopts | PROCEDURAL | a graph link (`tab:aggregates` → `tab:totalOf`), not a position |

No tuned constant appears in this design.
