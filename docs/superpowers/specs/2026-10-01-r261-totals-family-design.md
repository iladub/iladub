# Spec — a total printed beneath a table binds when a reader says so and the arithmetic holds

**Serves:** prog:criterion:etkl:03 — cbh is the unaccepted document whose one live escalation is the
totals family ([[R261]]).

**Date:** 2026-10-01. **Branch:** `r261-totals-spec`, cut from `main` at `ced805a`.

**Doc impact: increment.** § 4 adds one published `tab:` class (`tab:PrintedTotal`), one property
(`tab:totalOf`) and one shape (`tab:PrintedTotalShape`). No published term changes meaning:
`tab:SectionTotal` is untouched.

**Provenance of the design.** Approach (§ 0 R-c), the Note's fate (R-d) and design sections §§ 2–5
were presented and approved by the maintainer in chat on 2026-10-01. The start point is the handoff
`docs/superpowers/2026-10-01-r261-totals-family-spec-handoff.md` with its Addenda 1–2 (PRs
#286–#287), which carry P1 and P2. Code seams in § 3 were read at `ced805a` (read, not run; each is
a seam the plan re-measures, never a fact it may build on).

---

## 0. The concern, first — and the rulings this spec obeys

**The concern.** cbh's score gain from this loop is **almost entirely the Note being ignored, not
read.** Measured (Addendum 1, P2 § 3): the four port totals are booked 0/0 today, so binding them
moves cbh by about +4 asserted tokens (873/959 = 0.9103 → ≈ 877/963). The 86 escalated tokens are
`1,951,264` (1 token) plus the Note (85 tokens). Once `1,951,264` is carved out (§ 2), the Note is
expected to classify `NON_TABLE` → `ignored`, which **removes it from the denominator**. The score
then rises to ≈ 1.0 because a caveat the page asserts —

> *Note: Dates are based on Daily Transport capacity and assume total capacity is allocated to
> grade … The information provided is only an estimate based on information currently to hand …*

— is dropped as prose, exactly as every other prose band in the corpus already is. That is ruling
R-d below, taken knowingly. **The acceptance adjudication must repeat this sentence**, and a new
residue row records the Note as uncarried table context (§ 6, CLAUDE.md principle 5). This is the
trap recorded as *"roles → ignored games the score"*; it is disclosed here rather than avoided.

| # | Ruling | When, by whom |
|---|---|---|
| R-a | **R47's fork: NEURAL + exact sum, as a conjunction.** A printed number binds as a table's total only when a NEURAL worker answers *yes* to a closed question **and** exact `Decimal` arithmetic holds. Rejected: the AXIOM ordinal-column filter (n = 2), accepting cbh as-is at 0.91, switching to bfs. | Maintainer, 2026-10-01 (recorded until now only in the handoff § 3 and user memory) |
| R-b | **The grand total `1,951,264` is in scope.** It is the only asserted content inside the 86-token hold, so a loop that defers it leaves the hold's own lifting condition unmet (Addendum 1, P2 § 2). | Reading of the hold's wording, Addendum 1; **confirmed by the maintainer** with this design, 2026-10-01 |
| R-c | **Approach A:** bind in-loop at the band dispatch in `compile_tables`, before `classify`. Rejected: B, a post-pass beside `_confirm_section_total` (ink is booked by then — the R73 defect-2 order — and band 9's supersession would sweep the unread Note with it); C, a SPARQL adjacency derivation (new vocabulary for one index comparison). | Maintainer, 2026-10-01 |
| R-d | **The Note's fate: normal classification, disclosed.** The carved remainder goes through `classify` like any band; if it reads `NON_TABLE` it is `ignored`. Rejected: keeping it escalated (honest, cbh stays ≈ 0.911, unaccepted); carrying it as table context in this loop (a second subject with no oracle). | Maintainer, 2026-10-01 |

R-a supersedes [[R261]]'s closure wording (*"an AXIOM derivation … confirmed by exact
arithmetic"*); R261 and [[R47]] receive ✎ amendments when the loop lands.

## 1. The goal

Carry cbh p0's totals family — the four port totals `374,904 / 737,289 / 660,363 / 178,708` and
their total `1,951,264` — as total cells with provenance to the page, under R-a's conjunction, then
adjudicate cbh (`etkl:03`; corpus 5/7 → 6/7). Nothing in the mechanism names cbh; on every other
corpus page it must be inert or correct (§ 5.3).

## 2. The mechanism (design § 1)

One binding step, run at the top of each band's iteration in `compile_tables`, **before**
`classify(band)`:

1. **Candidate.** A line of the band consisting of **exactly one numeric token**. The numeric parse
   is the one the compiler already uses for exact sums (`rows.py` `_numeric_token_sum` and its
   token parse) — the plan measures which function and reuses it; no second parser.
2. **Operands, two levels.**
   - **Table level:** the previous band (`idx − 1`) produced an asserted table. A candidate is
     *arithmetic-matched* to every column of that table whose exact `Decimal` sum equals its value.
   - **Total-of-totals level:** the operand is **the set of all `PrintedTotal`s bound so far on this
     page** (whole set, never a subset search — subsets breed spurious matches). Matched iff their
     exact sum equals the value.
   No match ⇒ nothing happens; the band flows on unchanged. Arithmetic runs **first**, so the worker
   is asked only on matches (5 table-level matches in the corpus at `5e33652`, census Addendum 1).
3. **Worker.** Asked only on a match; answers a closed `yes | no | cannot_tell` (§ 3.2).
4. **Bind** iff the worker says *yes* **and** the match holds. On a bind:
   - emit a `tab:PrintedTotal` (§ 4) with `tab:aggregates` to its operands;
   - record the decision via `brec.record("printed_total", ["total", "not_total"], …)`, rationale
     **derived from the arithmetic** (level, column or operand count, member count), never from
     model text;
   - **carve** the bound line out of the band and book its word asserted through the existing
     extent-exact `_book_recovered_ink`;
   - classify and dispatch **the remainder** as any band. An empty remainder emits no band.

On cbh this predicts: bands 2/4/6/8 bind at table level and carve to empty; band 9's line 0 binds at
total-of-totals level over those four; band 9's remainder (the Note) classifies on its own (R-d).

**Out of the candidate rule on purpose:** a total printed with a label (`Total 374,904`) is not a
lone numeric line and is not a candidate. The corpus has no such instance among its 24
table→following-band pairs; widening is § 6's, not this loop's.

## 3. Seams the plan must measure (read at `ced805a`, not run)

### 3.1 The binding site

- `compile_tables` (`compile.py`, `def` at :990): the per-page loop `for idx, band in
  enumerate(bands)` (:1047), `classify(band)` (:1081), `brec.record("kind", …)` (:1083), the lone-line
  donation hook (:1089–1097), the `NON_TABLE` → `emit_ignored_band` branch (:1099–1114), and the
  `KIND_NOT_SUPPORTED` else-branch (:1621–1636). In scope at the top of an iteration: `bands`,
  `graph`, `reports` (whose `table_uri` is set on asserted reports, `RegionReport` :766), `brec`,
  `asserted_total` / `escalated_total`.
- **MEASURE** that `reports[-1]` is band `idx − 1`'s report on every path (a `continue` that appends
  no report would silently pair a candidate with the wrong table).
- **MEASURE** how band indices mint region and band URIs before carving: a carve must not shift the
  index of any later band, nor mint a URI that collides.
- **MEASURE** the interaction with `donation.offer_single_line` (`donation.py:249`). The port-total
  bands reach it today (guard: `NON_TABLE`, one line, `donor_ev` always a Graph) and it returns
  `None` by inference from its query, not by observation. The binding step runs before it; the plan
  states which wins when both could fire.
- Band 9 and band 10 interleave in y (Addendum 1, P2 § 4). The carve removes a **line**, by
  identity, and must not assume a contiguous strip.

### 3.2 The worker

Copy `baml_src/header_lines.baml` + `src/iladub/etkl/headerlines.py`: a frozen reading dataclass,
a reader protocol, a fake reader, a process cache, a BAML reader, `RecordedPrintedTotalReader`
replaying `readings/printed_total/{question_key}.json` and writing only under
`ILADUB_RECORD_READINGS=1`, `default_reader()` live only under `BAML_LIVE=1`. The crop is the
probe's (`scripts/r261_total_question_probe.py` `crop`): the table band's last lines through the
candidate's band.

- **Output is a closed enum with no note field.** P1 measured the note leaking page values
  (`737,289`, `178,708`, `21`; Addendum 2 finding 1), and a closed answer cannot hold a free note to
  the never-quote rule.
- **Two wordings.** Table level: the probe's `PROMPT`, measured by P1 (Addendum 2): 4/4 *yes* ×3 on
  the true totals, *no* ×3 on who-wfa's `21`, no *yes* in 21 null asks. **n = 5 is the corpus, not a
  sample**; it is cited as such, never as a rate. Total-of-totals: **unprobed** (Addendum 2
  finding 4) — § 5.1.
- **Unmeasured, stated:** the worker's specificity on a large total-looking number that does not
  sum (Addendum 2 finding 2). Arithmetic refuses that case first, so it is never asked; the gap is
  in the evidence, not in the gate.

## 4. Vocabulary and membrane (design § 2)

**Measured:** cell text is a string in the graph (`tab:value` range `xsd:string`, `tab.ttl:167`;
`tab:cellText`, :121). Only `tab:BaseFact`'s `tab:measureValue` is `xsd:decimal` (:164). The
membrane therefore **cannot** re-check the sum without parsing `"374,904"` in SPARQL, which would
reopen the float/Decimal engine split ([[R92]]–[[R94]]). The arithmetic is a **producer-side
PROCEDURAL check that is the sole enforcement of that property** — the R89 case where a producer
guard is not a duplicate. The code and this spec say so.

New terms (`tab.ttl`, CC-BY-4.0):

- **`tab:PrintedTotal`** — a total printed **outside** its table's grid, bound only when a reading
  worker answers *yes* and exact `Decimal` arithmetic over its operands holds.
- **`tab:totalOf`** (`tab:PrintedTotal → tab:Table`) — table level only.
- Operands reuse **`tab:aggregates`**: column cells at table level, bound `PrintedTotal`s at
  total-of-totals level. Its comment is amended to name this third usage.

**Superclass — a seam, not an answer.** `tab:AggregationCell ⊑ tab:EntryCell` is the natural
parent. Under `inference="rdfs"` every shape targeting either class would bind a cell that has no
row and no column. The plan **enumerates those shapes first**; if any demands a grid position,
`PrintedTotal` does not subclass `AggregationCell`.

**`tab:PrintedTotalShape`** (closed-world membrane): exactly one `tab:cellText`; `tab:aggregates`
`sh:minCount 2` (a one-member "total" is not a total); `tab:totalOf` `sh:maxCount 1`; a box and a
page, as every carried cell has (CLAUDE.md principle 6; the R179 lesson); **produced by a decision holon** —
the plan measures how existing decision-produced nodes link to their `dec:DecisionHolon` and uses
that link. **Every constraint ships a negative test that must fail.**

## 5. Oracles, tests, acceptance (design § 3)

### 5.1 Before the wording is fixed — P3 (a proposition; it may fail)

Plan task 1 probes the total-of-totals wording on `1,951,264` plus a null control, 3 repeats, Haiku
4.5, the closed output. **If it does not answer *yes*, the grand total is not bound**: the loop
records that and stops short of acceptance. It does **not** reword until it passes.

### 5.2 CI tests (synthetic fixture, fake reader)

Fixture: a table, a lone total line, a lone total-of-totals line, a prose remainder. The conjunction
is pinned from both sides:

| worker | arithmetic | expected |
|---|---|---|
| yes | holds | bound |
| yes | fails | **not** bound — the worker cannot bind alone |
| no | holds | **not** bound — arithmetic cannot bind alone (who-wfa's `21`) |
| cannot_tell | holds | not bound |

Plus: the total-of-totals binds only over totals already bound, never over raw cells; the carved
remainder is classified on its own; an empty remainder emits no band. Every task carries a
`## FALSIFICATION` block — delete each half of the conjunction and show its test fail.

### 5.3 Corpus sweep (local; CI skips the corpus)

One test file per process, from a `.sh` under bash, serially. Predicted movers: **cbh only**. Any
other document moving is a finding. who-wfa must not move: its `21` is refused by the worker.

### 5.4 Pins that move — re-read, never re-pinned blindly

- `tests/etkl/test_escalation_furnish.py::test_corpus_cbh_furnishes_exactly_one_request_for_its_one_live_escalation_the_residue`
  — live count 1 → 0; the residue is re-read.
- cbh's `cor:adjudication` hold in `tests/corpus-manifest.ttl`.

### 5.5 Acceptance of cbh

Adjudicated, not scored. **Dump the cells before accepting** (2026-09-28). The adjudication text
states § 0's concern: ≈ 85 of the gained tokens are the Note **ignored, not read**. Corpus 5/7 →
6/7 only if the adjudication holds.

## 6. What is not done

- Labelled totals (`Total 374,904`); subset sums; row-axis totals.
- Reading the Note, or any note, as context on a table. **A new residue row** records cbh's Note as
  uncarried table context (principle 5) when the loop lands.
- Membrane-side arithmetic (§ 4).
- [[R262]] (lossy escalation surface text): untouched.
- Register on landing: R261 closes (✎ R-a); R47 ✎ the ruling; [[R77]] (the label-less total gate)
  re-read and closed or amended as measured.

## 7. Classification (CLAUDE.md § 8)

| decision | class | why |
|---|---|---|
| a line is one numeric token | PROCEDURAL | raw extraction over tokens; exact, no tolerance |
| a column's / the bound totals' sum equals the value | PROCEDURAL | decidable exact `Decimal` arithmetic |
| the previous band is an asserted table | PROCEDURAL | an index fact of the band list, not a reading judgement |
| *is this number the total of what is above it* | NEURAL | a reader's judgement (who-wfa's `21` sums and is not a total); disposed by the arithmetic oracle, and vice versa |
| what may cross into the holon | AXIOM (SHACL) | `tab:PrintedTotalShape`, closed world |

No tuned constant appears anywhere in this design.
