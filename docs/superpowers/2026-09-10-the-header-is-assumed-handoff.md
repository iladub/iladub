# Handoff — the header row is assumed: R166 is 12 bands, and no in-band signal can separate them

**Topic:** [[R166]], widened. Branch `r166-the-header-is-assumed`, off `4905355`.
**Written 2026-09-10, LATE in the session** — past the originating floor, so every action in
part 5 is graded, per CLAUDE.md § "The handoff's next action is TYPED".

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — do NOT re-run the search for an in-band signal

The question *"what decidable format signal separates a data row from a header row inside one
band?"* is **answered: none, and two of the three candidate marks are unavailable by construction
rather than merely absent** (spec § 3). A future loop that proposes a type-contrast rule, a
numeric-label rule, or a blank-corner rule is redoing measured work — and the numeric-label form
was already refuted twice before this loop (the nil-glyph handoff § 5b, and R166's own row).

**Why asserted:** the outcome is on disk and re-runnable in one command
(`PYTHONPATH=. .venv/bin/python scripts/header_row_census.py`), and the two impossibility
arguments are pinned by `tests/etkl/test_header_row_is_assumed.py`, which runs in CI with no
`corpus/` ([[R173]]).

### 5b. ASSERTED subject, PROPOSED remedy — the next subject is bfs p6, and its cheap check is ALREADY RUN

The subject is asserted: the measurement is on disk and reproducible. The remedy is a fork with no
arm yet chosen, and the arm this handoff was drafted to recommend was refuted before it shipped.

bfs page 6 is **one table split into six bands**: band 2 carries the real header
(`Grandes régions | Total | 0-19 ans | …`), and bands 4, 5, 6, 8, 9 are its data, each asserting
its own first row (a regional subtotal) as a header — **5 of the corpus's 11 false headers, 40 of
its 73 numeric label cells, on one page, with the true header present on the same page.** apple p2
band 6 has no header anywhere on its page; bfs p6 does. That makes bfs the instance to design
against.

**The prediction this handoff first carried was RUN before it shipped, and is REFUTED.**
`scripts/forced_carriage_spike.py corpus/gov-stats/bfs-population-bilan-2023.pdf 6 2 4` at
`4905355`: band 2 reports `header_reading=None`, exactly as apple's does, and
`carried_roles_for(<hand-built reading>, band 4's header rows, band 4's grid)` returns `None`, so
the forced compile changes nothing (`asserted tokens: baseline=276 forced=276`). The reason is
**more general than the one the apple spike recorded**: a `CarriedHeaderReading` is minted at
exactly one site, `ruledroles.py:549`, inside the hierarchical (loop-L) assert path — so the
*whole* record-table branch mints none, matrix or flat. The seam was never available to either
half of R166.

**So the next action is a DESIGN FORK, not a spike.** Three arms, and the loop's first job is to
choose between them with the maintainer if it cannot choose alone:

1. **Escalate the branch** — 5c below. Honest, loses no correct reading on this corpus, costs the
   scores.
2. **Merge the six bands and re-enter classification from the top** — bfs p6 is one table split
   into 12 bands (5 asserting a false header, and note **band 3 — the grand-total row
   `Total 8 962 258 …` — is `ignored` outright, 0 cells**, as is band 7 `Zurich …`). [[R165]]'s
   run machinery does not reach them: its disposal chain runs `is_matrix_candidate` →
   `classify_matrix` (`scripts/band_run_census.py:85-95`) and these are record tables.
3. **Extend the carriage seam to mint a reading from a record-table assertion** — the arm the
   refutation above opens rather than closes, and the one that would make band 2's labels
   available to bands 4–9. Nothing has costed it.

### 5c. PROPOSED — the "escalate all twelve" arm is shippable, and it costs the whole branch

Spec § 4 declines it this loop. It remains the honest §7 reading — **11 of 12 label rows are false
and the 12th's body is false, so refusing the branch outright loses no correct reading on this
corpus** — and that is a stronger argument than it first sounds. What makes it a plan's work and
not a fix: it moves 111 label cells plus every entry beneath them from asserted to escalated,
re-baselines every corpus score and every adoption pin, and leaves the *replacement* (5b) unbuilt,
so it must not be taken as a substitute for 5b. **If 5b is refuted, this is the arm to plan.**

**Why proposed:** the "loses no correct reading" claim rests on twelve readings this loop MADE, by
comparing each label row against the row beneath it and the page text. They are printed in spec
§ 2 so they can be re-judged; a reader who disagrees with one of them changes the arithmetic.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the census, the ruling and every measurement | `docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md` | § 1 the real mechanism; § 2 the twelve-band table; § 3 why no in-band signal can exist; § 4 what was deliberately not done |
| the loop record | `docs/superpowers/2026-09-10-the-header-is-assumed.md` | the falsification table — read **F2a**, the inversion that did not fire and found the two-clause structure |
| the instrument | `scripts/header_row_census.py` | that its band re-identification is CHECKED (`aligned=no` fired once, bfs p5 band 13) |
| the pins | `tests/etkl/test_header_row_is_assumed.py` | one DETECTOR (RED when the class is fixed — invert it, don't delete it) and one impossibility pin |
| the amended row | [[R166]] in `residues-open.md` | the widened population and the closed arms |
| the successors | [[R201]], [[R202]] | R201: bfs p6 as the cross-band instance. R202: the region↔band pairing this loop's instrument checked and found broken twice |

## 2. What changed

No compiler behaviour. One instrument, one test module (2 tests), three documents, three register
rows (R166 amended, R201 and R202 raised).

## 3. What was decided, and where that decision is recorded

- **R166 is a corpus-wide class, not an apple defect.** Spec § 2. R166's row is amended in place.
- **The in-band arms are closed by construction.** Spec § 3, pinned by the second test.
- **This loop ships no behavioural change.** Spec § 4, argued from blast radius, not from budget.
- **The record-table branch's header is decided in Python, at `classifygraph.py:53`.** Spec § 1.
  Recorded nowhere else; if this file and the spec are lost, the next reader will re-find it via
  `classify-kind.rq` and mis-attribute the decision to the query.

## 4. Unverified or assumed

- **The twelve judgements in spec § 2 are READINGS, not derivations.** They are mine, made from
  the printed label/row1 pairs plus `pdfplumber.extract_text` on the page. The census prints the
  evidence for each so any of them can be overturned.
- **`aligned=no` on bfs p5 band 13 IS explained** — it is the transposed reading, whose labels are
  grid column 0, so line 0 is correctly not where they came from. What is *not* explained is the
  other symptom the same check surfaced: **2 of 26 asserted regions have no positional band at
  all** (ons p7 band 16, p8 band 9, both 276 cells). Whether `res.regions` and `page_bands` can
  disagree in a way that matters elsewhere is unmeasured, and every instrument in this repo that
  indexes bands positionally — `scripts/forced_carriage_spike.py` included — assumes they cannot. Raised
  as [[R202]].
- **The 73 numeric-label figure counts `headers.is_numeric` after removing thin-space group
  separators**, so bfs's `1 736 124` counts as numeric. bfs p5 band 13's nine labels are whole
  joined data rows and count as **0** numeric although every one of them is data — the figure is
  therefore a floor, not an exact count.
- **No wall-clock or score measurement was taken.** Nothing in this loop changes a score, so no
  before/after pair exists to compare against a future one.
