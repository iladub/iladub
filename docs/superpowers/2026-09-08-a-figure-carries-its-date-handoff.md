# Handoff — the R187 spec is written, and it refutes the oracle it was given

**Topic:** action **5b′** of `docs/superpowers/2026-09-08-two-loops-handoff.md` is taken. [[R187]]'s
spec exists; **no code was written**. The handoff's own named oracle is **refuted by measurement**,
four residues are raised ([[R189]]–[[R192]]), and the predecessor's eighth-time-carried action **5d
is discharged — all four of its capability figures are wrong.**

**Written 2026-09-08**, under the originating floor, **part 5 first**.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — write the plan from the spec, then execute it

Mechanical, and the reason it is asserted rather than proposed is that **the design decisions are
already taken and measured in the spec**, not left to the plan: the §8 classification (§2), the
register's shape (§3.1), the block scope (§3.2), the uniqueness rule with its one measured false
positive (§3.3), the disposition table (§3.4), the interfaces and the three seams (§6).

The plan takes exactly **one** open decision — spec §3.1's **arm A** (extend
`tests/corpus-manifest.ttl`) vs **arm B** (a new `tests/docgov-figures.ttl`). The spec recommends A
and says why; neither arm touches a Contract-class file, so **this is not the maintainer's to rule**
and must not be escalated as if it were.

**Bootstrap the register from spec §1.4, not from any older table.** Those seven readings were taken
in this session at `9eb5cd0`; the 2026-09-05 re-baseline everyone has been citing is wrong on four
of its seven rows.

### 5b. PROPOSED — that the HARD gate is shippable at all

**This is the one item resting on a prediction rather than a run.** Spec §3.4 gives the wiki class a
hard fail. That survives only if spec §5's **O3** — a hand census of every figure occurrence in the
tracked tree — finds no unexplained false positive. One is already located and already has a remedy
(`1.0000` vs `graincorp-capacity`'s `1.0`, §3.3, disposed of by marking one reading of seven
`cor:notQuotable`). **A second unexplained one drops the disposition to warning**, and the spec says
so in O3's own text.

**It fails cheaply and early:** O3 runs before any gate is wired, on an instrument that already
emits, so the refutation costs one census and not a day of building. Run O3 first.

**The hazard, named while it is cheap** — and it is the mirror of the hazard the predecessor named.
That handoff warned *"if the new gate fires on 9 of 12 pages, it has not been narrowed, it has been
promoted."* The correct gate here is **deliberately wider than the two pages [[R187]] names** (spec
§0), so "it fires on more than two" is **not** evidence of a defect. The discriminator is O3 alone:
*a firing that denotes no reading is a defect; a firing that denotes a real undated reading is the
instrument working.*

### 5c. PROPOSED — that [[R192]] is worth a loop, and that its population is bigger than n=1

R192 says a handoff asserts current state in the one class every doc-governance gate exempts, and
its evidence is **one line propagated across eight files**. My reasoning is that the shape recurs —
part 5 of a handoff is by construction a claim about the tree as it stands — but that is reasoning,
not a census.

**The check is cheap and must run before any spec:** how many Evidence documents restate a corpus
figure they did not themselves measure? If the answer is "the capability line and nothing else",
R192 is one bad sentence, not a class, and the right remedy is to stop copying it.

### 5d. ASSERTED — the capability line must not be carried into a ninth handoff

It is measured now (spec §1.4) and **all four figures are wrong**: `graincorp 0.9654`→`0.9659`,
`apple 0.6289`→`0.71875`, `WHO 0.9096`→`0.9156`, and `bfs 0.9401` — which was never a reading of the
shipped tree at all, but the score under **C3, reverted at `51bdd23`**. Quote spec §1.4 or
re-measure; do not quote the line.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the spec | `docs/superpowers/specs/2026-09-08-a-figure-carries-its-date-design.md` | §0 why the given oracle is refuted, §1.4 the seven readings, §2 the §8 classification, §3 the design, §5 the replacement oracle, §6 interfaces + seams |
| the corpus baseline | spec §1.4 | the only current reading of the seven document scores; **dated, and stale within days by construction** |
| the instrument being extended | `tests/test_doc_governance.py` (66 lines), `tests/docgov_extract.py` (231), `vocab/queries/docgov-*.rq`, `vocab/shapes/doc-governance-shapes.ttl` | 4 passed, 2 warnings, ~25 s. Nothing in it changed this loop |
| the four new rows | [[R189]] [[R190]] [[R191]] [[R192]] in `residues-open.md` | read the row, never the index line |
| what this loop is answering | `docs/superpowers/2026-09-08-two-loops-handoff.md` §5b′ and `…-two-loops-sequenced.md` §2, §3 | §3 is [[R188]]'s invariant, derived once — cite it, do not re-derive |

## 2. What changed

One branch, `a-figure-carries-its-date`, three files: the new spec, four appended register rows, four
appended index lines. **No file under `src/`, `tests/` or `vocab/` changed** — this loop wrote a
spec and took measurements, nothing else. `pytest tests/test_doc_governance.py` re-run after the
spec was staged: **4 passed, 2 warnings**.

## 3. What was decided, and where that decision is recorded

- **The page scope is refuted as [[R187]]'s detector.** Spec §0 and §1.2. Recorded nowhere else. The
  ground is a table: 3 of the 8 flagged pages carry no decimal at all, and the page carrying two
  superseded scores is not flagged.
- **The gate registers DATED READINGS, never a current value.** Spec §3.1, and [[R190]] carries the
  price. Ground: a current-value register goes stale silently, which is [[R188]]'s shape.
- **`staleAgainstCode` is neither deleted nor promoted.** Spec §4.3. It is refuted as *this*
  detector, not as itself.
- **The wiki repair ships WITH the gate, not before it.** Spec §3.5. Ground: R187's own deferral
  column — rewriting a loop's measured figures in place destroys the record rather than dating it.
  **This is why no wiki page was touched this loop despite four stale figures being measured.**
- **The maintainer's "struck, not replaced" ruling is NOT inherited into `docs/wiki/**`.** Spec §4.6
  and §8. The predecessor handoff §6 extends it in one sentence; the CLAUDE.md text it cites is
  about the Evidence class. The design does not depend on the extension.

## 4. Unverified or assumed

- **Spec §1.4 is a reading, and it is already the kind of claim this loop exists to police.** Four of
  seven moved in three days. Anything quoting it later must say `@ 9eb5cd0, 2026-09-08`.
- **The corpus ran on this machine, one process per document, and was not repeated.** No second run
  confirms any of the seven figures; `lru_cache`-in-one-process effects were avoided by construction
  (separate processes) but not measured.
- **`bfs 0.9401`'s provenance is inferred from two documents, not from the diff.** The C3 handoff
  states the figure and states the revert at `51bdd23`; I did not check out that commit.
- **O3 has NOT been run.** The false-positive census is the spec's own gate on its own hard
  disposition, and this loop names it without running it. 5b is proposed for exactly that reason.
- **`corpus-harness.md`'s `254.1` and `grounding-membrane.md`'s `0.00005` are assumed non-readings**
  by inspection.
- **The full suite was not run.** `tests/test_doc_governance.py` (4 passed, 2 warnings) and seven
  `compile_document` calls. CI is the check that has not reported.
- **[[R191]] refutes a sentence in a document that is now append-only Evidence**, so the refuted
  sentence stays where it is. A reader of `the-two-counts` §2 gets the wrong count unless they also
  read R191.
