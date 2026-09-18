# R213 executed — the ink the page does not show

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-18. **Doc impact: increment** — one new term (`tab:UnshownInk`), one new property
(`tab:unshownText`), one new shape (`tab:UnshownInkCellShape`), one amended **published** shape
(`tab:WrappedCellShape`). Unchanged from the spec's own declaration.

Executes `docs/superpowers/plans/2026-09-17-the-ink-the-page-does-not-show.md` against spec § 8
(`specs/2026-09-17-the-ink-the-page-does-not-show-design.md`). Every invariant below is **cited**
from the plan or § 8, never re-derived.

---

## 1. What shipped, task by task

| task | what | class |
| --- | --- | --- |
| T1 | `tab:WrappedCellShape`'s proof-of-carriage widened from one property to two, as a **disjunct** | AXIOM (SHACL, closed world) |
| T2 | `tab:UnshownInk`, `tab:unshownText`, `tab:UnshownInkCellShape` (clause 1 only) | AXIOM |
| T3 | crossing A — the abstention in `celltype.grid_evidence` | PROCEDURAL |
| T4 | crossing B — the persisted cell, and O7's per-address refusal | PROCEDURAL |
| T5 | clause 2 as a producer-side guard at `feed._read_table` | PROCEDURAL |
| T6 | `ReadEmptyCells` (BAML, image input) + `unshownink.dispose`'s three refusals | NEURAL + AXIOM |

Commits on the branch, one per wave, each carrying its own `## FALSIFICATION` evidence in the
message (plan rule 4).

## 2. The three findings this execution made, which the plan did not have

### 2.1 The spec's § 8.4 enumerates FIVE minting sites. There are SIX.

```
$ git grep -n "_emit_entry_cell(" src/
src/iladub/etkl/holon.py:41    def _emit_entry_cell(...)
src/iladub/etkl/holon.py:154   assert_record_region
src/iladub/etkl/holon.py:214   assert_transposed_region
src/iladub/etkl/holon.py:314   assert_row_hier_region
src/iladub/etkl/holon.py:409   assert_matrix_region      <- NOT in § 8.4's list
```

plus `holon.py:628`'s inline hier emitter and `datagrid.py:691`. § 8.4 names
`holon.py:154,214,314`, `holon.py:628` and `datagrid.py:691` — it missed `assert_matrix_region`'s
own entry site. All six are wired. This is exactly the class of surprise O7's guard is insurance
against, and it was found by enumerating rather than by reading the list.

A second, smaller consequence: `assert_matrix_region`'s docstring said *"band is accepted for
signature symmetry with the other makers but is unused"*. It is now read (for `Band.unshown`), so
that note was corrected in place rather than left to go stale.

### 2.2 `datagrid.py`'s emitter is NOT wired, and that is stated rather than skipped

`emit_data_grid` takes `lines`, not a `Band`, and keys its IRI off a third counter
(`-r{r_i}c{k}`). There is no band in scope, so there is nothing to join a grid-space address to.
Measured consequence for the document this loop is about: gcap mints **0** cells of that shape —
all 406 `tab:EntryCell`s parse as `…-e{r}_{c}`, 0 unparsed
(`scripts/unshown_ink_seam_census.py --address`). Raised as a residue rather than papered over.

### 2.3 The first O7-null instrument was mis-specified, and said nothing

The first attempt compared each band's grid-cell set against a whole-**document** persisted table's
cell set, choosing the "best" table by intersection. A persisted table spans several bands and
pages, so every row read `DIFFER` — including on graincorp-capacity, where § 8.4 measured the two
spaces **identical**, 406/406. A census whose verdict is the same everywhere is measuring its own
join, not the corpus. It was discarded and replaced by § 3 below. (Recorded because the repo's own
lesson is *give every census a control*, and this one had none.)

## 3. O7's null EXISTS, and it fires on SIX of seven documents

**The plan required the null to be searched for and its absence recorded if it did not exist
(§ 4.3: "an absence is not a control"). It exists, and the result is stronger than the plan
expected — it refutes the generality of the identity § 8.4 measured.**

The control is run in the form it actually takes: declare **every** populated grid address of
every gridded band unshown, compile the document through the real dispatch, and see whether
`_UnshownCarriage.refuse_unless_complete` fires. It fires exactly when an address in
`headers._grid_cells`' space reaches no minted `tab:EntryCell`.

```
$ ./.venv/bin/python scripts/unshown_ink_address_control.py
cbh-stem-2026-08-03.pdf             REFUSED     assert_record_region: 3 unshown address(es) …
graincorp-capacity-2026-08-04.pdf   NO REFUSAL  (address spaces agree on every carried region)
graincorp-stem-2026-07-31.pdf       REFUSED     assert_hier_region: 274 unshown address(es) …
apple-fy2026q3-statements.pdf       REFUSED     assert_hier_region: 22 unshown address(es) …
bfs-population-bilan-2023.pdf       REFUSED     assert_record_region: 12 unshown address(es) …
ons-index-of-services-2026-02.pdf   REFUSED     assert_record_region: 6 unshown address(es) …
who-wfa-boys-zscore-0-5.pdf         REFUSED     assert_matrix_region: 89 unshown address(es) …

O7 CONTROL: fired on 6 document(s), silent on 1
```

**What this establishes, and what it does not.**

- **It establishes that O7 is a live control, not a formality.** The plan's weakness 3 — *"O7's
  null may not exist in this corpus"* — is answered: it exists six times over, through four
  different makers (`assert_record_region`, `assert_hier_region`, `assert_matrix_region`).
- **It establishes that § 8.4's address identity is graincorp-capacity's alone.** § 8.4 said in
  terms that the identity is *empirical, not structural*, and warned that `regions.Cell` and
  `_grid_cells` are two cell notions differing 10.0% vs 95.4% in reach. Measured: on the other six
  documents they **do** disagree, at every scale from 3 addresses to 274. The one document the
  identity was measured on is the one document it holds for.
- **It does NOT establish that the carriage is broken.** It is fail-closed by construction: a
  disposal that supplied an address in a disagreeing region refuses that region rather than write
  the transcription onto the wrong cell. What it establishes is that the carriage **does not
  generalise beyond gcap today**, and that a future loop wanting unshown ink on another document
  must repair the address join first, not assume it.
- **It is the MAXIMAL probe.** Every populated address is declared, so the refusal fires wherever
  the spaces disagree *anywhere* in a region. A real disposal supplies a subset, and would refuse
  only if a disposed address landed in the disagreeing part. The probe measures the join, not the
  disposal.

Raised as a residue. The instrument ships so the figure can be re-run rather than re-read.

## 4. What the plan said would be measured, and what came back

### 4.1 T1's seam — which classes RDFS-close into `tab:Cell`

```
declared subclasses of tab:Cell: ['AggregationCell', 'EntryCell', 'LabelCell']
asserted in graincorp-capacity p0: {'LabelCell': 9, 'EntryCell': 406}
```

The amendment reaches all three under `inference="rdfs"`. 0 `AggregationCell`s and 0 bare
`tab:Cell`s on that page.

### 4.2 T3's shape — widened tuple vs side-map, measured not preferred

Widening `(r, c, text)` to a 4-tuple breaks **12** `for (r, c, t) in cells` unpack sites:
`celltype.py:150`, `unitmarker.py:59`, 2 in `scripts/`, 8 in `tests/`. The `unshown=` keyword
touches **0**. Side-map, 12–0.

### 4.3 T5's nine consumers — the disposition M2 asked for, per reader

| reader | verdict | why |
| --- | --- | --- |
| `feed.py:253` | **guarded** | the grounding site; T5's producer-side guard |
| `denormalization.py:168` | correct as-is | `_num("")` → `None`, the cell drops out of the value matrix |
| `document.py:787-790` | correct as-is | the literal count stays 1, so the chain-walk refusal does not fire; it carries `""` — the truthful answer |
| `recipe.py:37` via `grid_values`/`row_label` | correct as-is | returns `""`; a cell the page does not show has no value to key on |
| `row-group-key.rq` | correct as-is | already `FILTER(STR(?v) != "")` |
| `row-group-key-logical.rq` | correct as-is | same filter |
| `unpivot-inverse.rq:27` | correct as-is | `BIND(xsd:decimal(?v))` on `""` is unbound, so the solution drops |
| `unpivot-inverse-valueset.rq:21` | correct as-is | same `xsd:decimal` bind |
| `tab:EntryCellPhysicalShape` | correct as-is | `sh:minCount 1` is satisfied by an empty literal — **confirmed, not assumed**: the conformant example passes |

Eight of nine want the truth an empty `tab:cellText` tells them. That is the whole argument for
emptying rather than adding a skip per consumer (§ 8.2), and it holds on the enumerated population
rather than on the three the spec named.

### 4.4 The reshape round-trip — the one seam M2 named, measured

The seam: `unpivot-inverse.rq:27` reads the entry cell's text into the **reshaped** graph while
`recipe.grid_values` reads it off the **source** graph — the two sides of the shipped round-trip.
The plan said to measure it before and after emptying and to treat a divergence as a finding, not
a tolerance to widen.

Measured by supplying the 110 directly (the addresses are already established by set identity, so
this holds the worker's non-determinism out of the experiment):

```
[BASELINE]              triples=5859  EntryCell=406  unshownText=0    emptyCellText=0    grid_values=6  non-empty=6
[110 DECLARED UNSHOWN]  triples=5969  EntryCell=406  unshownText=110  emptyCellText=110  grid_values=6  non-empty=6

delta  triples=+110  EntryCell=0  unshownText=+110  grid_values=0  non-empty grid_values=0
```

**The two sides do not diverge, and the reason is that neither side reaches the 110.** gcap's
`grid_values` population is **6**, all of them outside the emptied set, so the round-trip is
untouched. That is a null with a known cause, not a passed prediction — on a document whose
reshaped population overlapped the unshown set the seam would still be unmeasured.

**What the same run DOES establish, and it is the loop's central claim:** the carriage works
end-to-end on the real document. Exactly 110 cells mint an empty `tab:cellText` and carry their
transcription, **no cell is lost** (406 `tab:EntryCell` before and after), the delta is exactly the
110 new `tab:unshownText` triples and nothing else, and `compile_document` returns rather than
raising — so the whole graph passes the membrane, including T1's widened guard on 110 cells that
would every one of them have been refused before it.

## 5. What this loop deliberately did NOT do

Cited from plan § 3: the two graphs are not unioned to give clause 2 a SHACL subject; RF5's grain
problem is untouched; the fourth case (ink the page shows, outside any cell) is unaddressed; the
enhancement prohibition stays **unenforceable from the answer alone** — do not claim a defector can
be detected, the control page that would close it does not exist.

Added here: `datagrid.py`'s emitter is not wired (§ 2.2), and no colour is read anywhere in `src/`.

## 6. The oracle runs

### O1 — not re-run, by instruction

§ 8.8: *"O1 and O2 are RUN and PASS, blind, and must not be re-run to establish anything."* O1 is
not re-run here.

### O2 — RE-RUN as a regression against § 8.7's changed ask, and it FAILED on the shipped client, then PASSED on a larger one

This is the run the plan asked for, and it is the reason to run it: **the ask is right and the
model first configured to answer it is not.** One region, gcap band 3, 27 x 16, 406 populated
cells, 110 of them the zeros the page does not show:

| client | `\|A\|` | of the 110 zeros | FALSE POSITIVES (cells with visible ink) | `(1, 6)` found |
| --- | --- | --- | --- | --- |
| `claude-haiku-4-5` | 148 | **68** | **79** | yes |
| `claude-sonnet-5` | 110 | **109** | **0** | yes |

Haiku's own `note` gives the mechanism away — it reported *"cells with dark backgrounds … that
show no visible text"*, i.e. it classified by **background** instead of reading the place. That is
the refuted colour instrument re-entering through the worker, which is RF7's failure mode exactly,
and the output shape caught nothing because the answer was well-formed and wrong.

Sonnet reproduces the blind runs' disposal **through the shipped prompt**, missing one cell
`(22, 2)` and inventing none, and independently returns `(1, 6)` — the one non-degenerate
null-control position. The client is pinned to it, with these figures recorded beside it in
`baml_src/clients.baml` so nobody downgrades it to save cost without re-running O2.

**A second, mundane defect the run surfaced:** the shared `Claude` client's `max_tokens 2000`
**truncates** this answer mid-array. The same crop returned a complete answer on one run and an
unparseable one on the next; the successful run used 3198 output tokens. A budget that sometimes
fits is a defect, not a tolerance.

### O2 end-to-end — BLOCKED, and this is the loop's honest limit

**With the disposal's addresses supplied, everything downstream works** (§ 4.4). **With the live
reader wired, `dispose` types 0**, and the cause is measured, not guessed:

```
DISPOSED with spanned = the 25 column-0 text-layer-empty positions : 109
DISPOSED with spanned = ()                                         :   0
```

§ 8.7 scopes refusal 3 to text-layer-empty positions **not inside a spanning cell's extent**,
because a reader who reads a span as occupied is reading correctly — and the prompt *tells* the
reader so. Nothing in the pipeline can hand that set over today: R211's span reading is a **header**
reading, and gcap's confounder is a body-column year label spanning **rows**. So the refusal demands
the reader report the 25 positions it was told are covered, and refuses the region.

This is **fail-closed and correct** — no claim, never a false one — and it means the live wiring
types nothing end-to-end until the spanned set exists. It stays behind the `BAML_LIVE` gate.
**This loop does not close end-to-end on live input**, and saying otherwise would be false. Raised
as a residue. No geometric rule was invented for `spanned`: the gate allows one geometric attempt,
and spending it unspecified at the end of a loop is worse than recording the blocker.

### O3 — the six-document null, reported as the WEAKER control the plan says it is

With the gate off, `Band.unshown` is `()` on every band, `grid_evidence`'s `unshown` defaults to
`None` and `_emit_entry_cell`'s `unshown_text` to `None` — so **nothing is emptied and the carriage
is the identity**. The null therefore holds **by construction**, not by prediction, and the plan
instructs that it be reported as such rather than as a passed oracle. Its pinned form is
`test_the_null_*` (three of them, at both crossings, one by graph isomorphism).

### O4 — the membrane's negative: PASSES

`tab:UnshownInkCellShape` refuses a cell that carries `tab:unshownText` and a non-empty
`tab:cellText`, with the falsification arm showing it RED when the clause is removed
(`tests/test_tab.py::test_unshown_cell_with_nonempty_celltext_fails`).

### O5 — gcap's score: the direction stated, and the measurement NOT taken

**Stated before any run, as required:** with the live wiring blocked (above), gcap's compiled output
under the shipped default is **unchanged** — measured, 5859 triples either way — so the score
**does not move at all**. That is the honest prediction for what ships, and it is confirmed by the
BASELINE row of § 4.4.

The interesting number — where the score goes when the 110 *are* carried — was **not measured**. It
needs the whole-corpus verdict snapshot run twice, and with the live path blocked the figure would
describe a configuration that does not ship. **Recorded as not taken, not as a null.** R155's
*score-rise-is-a-collapse* is the reason not to quote a movement nobody ran.

### O6 — the widened guard still refuses: PASSES, both arms

A bbox-carrying cell with neither property non-empty is still refused (`tab-wrapped-leak.ttl`,
unchanged), and so is one whose `tab:unshownText` is **empty** (`tab-unshown-empty-leak.ttl`) — the
arm that separates the **disjunct** § 8.3 required from the exemption it refused. Both shown RED
with their subjects removed.

### O7 — the address spaces are checked, not assumed: PASSES, and its NULL EXISTS

See § 3. The control fires on **six of seven** documents; only graincorp-capacity agrees.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
