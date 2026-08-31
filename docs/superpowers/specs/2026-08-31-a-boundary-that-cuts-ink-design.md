# A boundary that cuts ink is not a boundary — closing `R154`

**Subject:** `geometry.rule_aware_lines` (`src/iladub/etkl/geometry.py:262`).
**Residue:** `R154` (`docs/superpowers/residues-open.md`) — *"the ruled re-extraction shreds a header
label mid-word, and chop/merge interleave so no downstream weld recovers it."*
**Predecessor:** `docs/superpowers/2026-08-31-r45-closed-handoff.md`, whose § 5 graded this
**PROPOSED** and required the prediction be RUN before anything was planned. It was run first; §3 is
that run.

**Doc impact:** `none` — no released assertion changes; the wiki's table-reading pages describe the
ruled re-extraction at a level this does not contradict.

---

## 1. What this closes, and what it does not

**Closes.** The defect `R154` states: a ruled boundary falling inside a word run shreds it.
After this change no ruled boundary divides a row **through ink**. WHO page 0 band 2 line 0 goes
from seven fragments to two, and `'Z-scores'` is whole.

**Does NOT close.** The row's wider claim that *"a header line needs BOTH readings at once"* stands.
One residual division survives on that same line, and it is a **word gap**, not a mid-word cut —
measured in §3.4. Reconciling the ruled and word readings *per word* is explicitly not attempted
here; §8 states why and §10 raises the successor row.

**Does NOT license.** This is a **fidelity** repair. It is not a score repair, and the corpus scores
in §3.3 must not be cited as its justification — WHO's score does not move at all.

---

## 2. The subject — stated once

`rule_aware_lines` re-groups a ruled band's characters into cells: rows by vertical proximity, then
**one cell per ruled column, assigning each character by its centre**. Per-character centre
assignment is the whole defect. When rule x's arrive dense — WHO's 48 raw x's on this band come in
quads of twin stroke edges, adjacent x's 0.72pt apart — consecutive characters *of one word* fall in
different columns and the word emerges as one cell per character.

**The change, in one sentence:** a boundary divides a row **only where the ink on both sides of it
clears it**; where the boundary cuts through ink, that row does not divide there.

`xs` itself is untouched. The boundary set is still every rule x, globally, for
`refine_rule_columns`, `confirmed_boundaries` and `Band.column_xs`. Only the **per-row decision to
use a boundary as a cell divider** changes. That distinction is load-bearing and is why this is not
the global word-atomicity variant the row already measured to fail (§3.5).

---

## 3. Measurement at HEAD `5743af3`

All figures below were produced this session by scripts in the session scratchpad, against the seven
tracked corpus documents, `validate_shapes=False`.

### 3.1 The discriminator is the repo's own prior art, and it is tolerance-free

`ruledroles._within` (`src/iladub/etkl/ruledroles.py:112-129`) already names the signal, and already
carries its justification:

> *"Ink that REACHES a ruled boundary was not laid out in that cell — it is a text run the renderer
> drew across the grid and rule_aware_lines then chopped at the boundary. … **the chop is exact, so
> the clearance is exactly zero.**"*
>
> *"Strictness is expressed with COORD_EPS … It is NOT a clearance threshold: no minimum padding is
> required, only a non-zero one."*

The predicate this spec adopts is the same one, applied one stage earlier — at the moment the chop
would be made rather than downstream where it is detected. **No new constant is introduced.**
`COORD_EPS` is the repo's float-comparison epsilon; it makes `>` mean `>`, and R154's own row
forbids any *clustering* constant because clustering is a per-document property. This predicate has
none.

### 3.2 The flush signal is NOT a two-population discriminator — it says every crossing is an artefact

The row describes two populations (*"cbh/ons/bfs/gstem crossings are 100% genuine spanners; apple
and who are 92%/98% sub-point overhang"*) and its proposed close asks for a discriminator between
them. **The measurement refutes the need for one.** Counting, per document, every (row, interior
boundary) pair with ink on both sides:

```
                       flush   clear          R154's row's crossing census
graincorp-stem             1    2576          1/2845
graincorp-capacity         0    1154          0/496
cbh-stem                  53    1059          49/1234
apple                     25     629          25/678
bfs                        6     209          7/1497
ons                       20       5          20/1305
who                      139     853          129/349
```

`flush` reproduces the row's crossing census (apple 25=25, ons 20=20, gstem 1=1, gcap 0=0; the three
that differ do so by ≤10 and are a row-bucketing difference, not a different phenomenon). **So the
flush set IS the crossing set** — and inspection of what is in it shows why no discriminator is
needed: every sampled member is the same phenomenon, a text run drawn across the grid and chopped,
in *both* alleged populations —

```
cbh    'GERALDTO' | 'N'                    (L-b=-1.722 R-b=-1.704)
cbh    'BE' | 'RTHMAYBEUNAVAI'             (L-b=+1.134 R-b=+1.080)
ons    '1TheIOSo' | 'utputisdesigna'       (L-b=+0.220 R-b=+0.220)
bfs    "posantesdel'év" | 'olutiondelapop' (L-b=+0.593 R-b=+0.796)
apple  'ThreeMo' | 'nthsEndedNineM'        (L-b=-1.251 R-b=-1.198)
who    'Z-s' | 'cores(weightin'            (L-b=-0.107 R-b=-0.109)
```

The row's "genuine spanner" is a **banner or footnote spanning the table**, not two cells pdfplumber
wrongly merged. Nothing in the flush set is a division the author drew. The `clear` column is where
the author's cells actually live (who 853, gstem 2576), and it is untouched.

### 3.3 Two-sided corpus oracle — the full battery, both modes

`compile_document(..., validate_shapes=False)`, baseline (HEAD `5743af3`) vs. the per-row variant:

```
                        BASELINE score   asserted esc      VARIANT score    asserted esc
graincorp-stem          0.9654553611...      2152  77      0.9658886894...      2152  76
graincorp-capacity      1.0                   390   0      1.0                   390   0
cbh-stem                0.9046563192...       816  86      0.9091940976...       801  80
apple                   0.3556034482...       165 299      0.3586956521...       165 295
bfs                     0.3438438438...       229 437      0.3464447806...       229 432
ons                     0.9719934102...       590  17      0.9719934102...       590  17
who                     0.9095966620...       654  65      0.9095966620...       654  65
```

Escalation reason counters are unchanged **at document scope**: apple keeps
`MATRIX_AMBIGUOUS x2 · REGION_TILING_FAILED x8 · DATAGRID_RESIDUE x1`, bfs keeps
`KIND_NOT_SUPPORTED x3 · REGION_TILING_FAILED x2 · ROUND_TRIP_FAIL x5`, the other five raise none.

**CORRECTION, added after the unit suite ran — this claim was first written without its scope, and
at PAGE scope it is FALSE.** `compile_tables(cbh, 0)` baseline vs. fix: score
`0.06984126984126984 → 0.05711086226203808`, asserted `66 → 51`, and regions 1/3/5/7 change reason
`MERGE_AMBIGUOUS → REGION_TILING_FAILED`. Document scope does not show it because `document.py`'s
driver runs a pass-2 repair over these bands. **So "no document regresses" holds at document scope
only; page-scope cbh regresses.** Raised as `R156`(b); `tests/etkl/test_typing_equiv.py` is what
caught it, and this spec's §7 oracle table did not name page scope.

**Read this table correctly — the score movements are NOT the result.** Four documents rise by
0.0004–0.0045. Every one of those rises is at least partly a **denominator** effect: welding two
chopped fragments into one cell removes a token from the ink count (cbh `asserted+escalated`
902 → 881). A smaller denominator is not evidence of better reading. **The oracle this table
provides is two-sided and negative: no document regresses, no escalation reason appears or
changes count, nothing raises.** That is what it is cited for and nothing more.

### 3.4 The fidelity oracle — WHO's carried header

This is the result. `page_bands(who, 0)`, band 2:

```
BASELINE  line0: ['Z-s', 'c', 'o', 'res (weight', 'i', 'n', 'kg)']
VARIANT   line0: ['Z-scores (weight in', 'kg)']

BASELINE  line1: ['Year: Month','Month','L','M','S','-3 SD','-2 SD','-1 SD','Median','1 SD','2 SD','3 SD']
VARIANT   line1: ['Year: Month','Month','L','M','S','-3 SD','-2 SD','-1 SD','Median','1 SD','2 SD','3 SD']
```

**Line 1 is byte-identical, and that is the half that matters most.** R154's row records that the
coarse word-based header swap *"breaks what the ruled reading gets RIGHT, splitting `'-3 SD'` into
`'-3'` and `'SD'`"*. This variant does not: `'-3 SD'` survives, because the boundary inside it cuts
ink and is therefore not honoured, while every boundary between the twelve real columns has
clearance on both sides and is.

**The residual, measured.** Every interior boundary line 0 meets, with its clearances:

```
b=517.97  L-b=-0.107  R-b=-0.109  FLUSH->merge   'Z-s'      | 'cores(we'
b=522.65  L-b=+0.086  R-b=+0.084  FLUSH->merge   'Z-sc'     | 'ores(wei'
b=523.37  L-b=-0.634  R-b=-0.636  FLUSH->merge   'Z-sc'     | 'ores(wei'
b=528.77  L-b=-0.546  R-b=-0.548  FLUSH->merge   'Z-sco'    | 'res(weig'
b=583.49  L-b=-3.645  R-b=-0.887  FLUSH->merge   's(weight' | 'inkg)'
b=588.23  L-b=-2.574  R-b=-2.576  FLUSH->merge   '(weighti' | 'nkg)'
b=588.95  L-b=+2.809  R-b=+5.567  FLUSH->merge   'weightin' | 'kg)'
b=594.35  L-b=-2.591  R-b=+0.167  CLEAR->divide  'weightin' | 'kg)'
```

The surviving division at `b=594.35` is a **word gap** — the space between `in` and `kg)`, with the
`n` ending 2.59pt short of the rule and the `k` beginning 0.167pt past it. Both sides genuinely
clear. **This is the honest boundary of the predicate:** it distinguishes *cuts ink* from *falls in
a gap*; it cannot distinguish *word gap* from *column gutter*, because at the character level those
are the same picture. Closing that needs the word reading, which §8 excludes and §10 raises.

### 3.5 Why this is not the word-atomicity variant already measured to fail

R154's row records a spike that *"forc[ed] word-atomicity inside `rule_aware_lines`"* and
*"collapses `header_body_split` from ≥2 to 1 (… `column_xs` `()` against 49, escalation turns to
`ROUND_TRIP_FAIL`)."* That failure does not reproduce here, and §3.3 is the evidence: WHO's score,
asserted, escalated and reason counters are all **exactly unchanged**, which they could not be if
`column_xs` had collapsed to `()`.

The mechanism of the difference is stated in §2: word atomicity decides *globally* which boundaries
exist, so a boundary lost to one merged label is lost to every row. This decides **per row**. A
boundary that cuts the banner on line 0 still divides the twelve data columns on lines 1..n, and
`refine_rule_columns` / `confirmed_boundaries` still see the full `xs`.

---

## 4. Classification under the neurosymbolic gate (`CLAUDE.md` §8)

**PROCEDURAL, and it is a modification of an existing justified PROCEDURAL step, not a new one.**

`rule_aware_lines` is raw extraction: source glyphs → typed cell facts. It is already the repo's
PROCEDURAL exemplar for that stage, and its own docstring records the standard it is held to —
*"Deterministic containment assignment — no tuned constant."* This change is inside that step and
must meet the same standard, which §3.1 establishes: the predicate is exact geometric containment
under `COORD_EPS`, the repo's float-comparison epsilon, already justified in `_within` as *"NOT a
clearance threshold."*

**Why it is not AXIOM.** Deriving cells declaratively over an RDF evidence graph would require the
glyph geometry to be in the graph before the cells exist, and the cells are what the graph is built
*from*. This is upstream of any evidence graph, exactly as the surrounding function already is.

**Why it is not NEURAL.** The gate reserves NEURAL for *"which columns/rows does X span/read/group"*
reading judgements. This is not a reading judgement and has no underdetermination to propose over:
either the ink crosses the boundary or it does not, and the answer is in the glyph boxes.

**The reviewer's check, stated so it can be failed:** if any reviewer finds a numeric literal added
by this change other than a use of the imported `COORD_EPS`, the classification is wrong and the
change must be refused. **This classification is this spec's argument; it is NOT ratified by the
maintainer.**

---

## 5. Interfaces — signatures and invariants, not bodies

`rule_aware_lines(chars, rule_xs, y_tol=None) -> list[Line]` — **signature unchanged**. No caller
changes. Both call sites (`compile.py:133` with `xs`, `compile.py:193` with `col_xs`) get the new
behaviour, and that is intended: the second pass re-buckets on confirmed boundaries and has the same
defect.

Invariants the implementation must preserve — each falsifiable, see §7:

1. **`rule_xs` is not mutated and no boundary is removed from any other row.** The decision is
   row-local.
2. **A row whose ink clears every boundary it meets is byte-identical to before.** This is the
   overwhelming majority of rows (§3.2 `clear` column) and is why six documents' verdicts do not
   move.
3. **The outer range extension is unchanged** — the §7-no-data-loss `lo`/`hi` widening
   (`geometry.py:274-280`) still runs, still on `COORD_EPS`, before any per-row decision.
4. **`_cell_text` and the non-space bbox rule are untouched.** Padding-space segmentation (R13,
   `tests/etkl/test_padding_space_segmentation.py`) is not in scope and must not move.
5. **The predicate reads the row's INK only** — space glyphs never establish or deny clearance,
   consistent with `_cell_text` and the bbox rule already dropping them.

**MEASURE, do not assume — the seam for the implementer.** §3.2's counts and §3.4's fidelity result
were produced by a monkeypatched copy of `rule_aware_lines` in the scratchpad, not by the shipped
function. Before writing the docstring, re-derive both against the *edited* source; a copy that has
drifted from the original in any other respect would have produced the same table and told you
nothing.

---

## 6. The consumers — enumerated, not assumed

| consumer | what must be established |
| --- | --- |
| `ruledroles._within` (`ruledroles.py:249,274`) | **The one at risk.** Its docstring detects a banner *by* the chop this change prevents. Establish which way it now answers: a welded banner is one wide cell reaching across boundaries, so `_within` returns False for it in every column — the same answer it gave each chopped piece. §3.3 shows cbh (the banner-heavy document) does not regress, but that is corpus evidence, not a read of the function. **Read it.** |
| `compile.py:193`, the second `rule_aware_lines` call | Re-buckets on `col_xs`. Confirm it is intended to change too (§5) and that `Band.column_xs` is set from `confirmed_boundaries`, not from cell edges |
| `tests/etkl/test_border_grid.py:100,140` | Calls `rule_aware_lines` directly on `[35.0, 65.0]` interior separators. MEASURE whether its chars clear those boundaries |
| `tests/etkl/test_padding_space_segmentation.py` | Invariant 4. Direct caller; R13's regression guard |
| `tests/etkl/fixtures.py:927` | *"Two variants, because the two ways `rule_aware_lines` can cut the label were both shown"* — a fixture built **on** the cut. Establish whether one variant becomes unreachable; if so it is annotated with its measurement, never silently deleted |
| `gridregion.py:117` | Comments on `rule_aware_lines`' bucketing using *"every"* rule x. That sentence is about `xs`, which is still every rule x — confirm, and annotate if the wording now misleads |
| `cells.py:72` | Comment recording a past defect where refinement *"reached rule_aware_lines but never the grid"* — read for contradiction, do not rewrite |

---

## 7. Oracles — what falsifies each piece

| claim | oracle | falsified by |
| --- | --- | --- |
| The shred is repaired | `page_bands(who,0)[2].lines[0]` word texts | any fragment shorter than a word, or `'Z-scores'` split |
| The real header row is not damaged | same band, `lines[1]` | `'-3 SD'` becoming `'-3'`,`'SD'` — the measured failure mode of the coarse swap |
| No document regresses | the §3.3 battery, both modes | any score falling, or any escalation reason appearing/changing count |
| The decision is row-local (inv. 1) | a fixture with two rows over one boundary, one crossing it and one clearing it | the clearing row losing its division |
| No tuned constant (§4) | reading the diff | any numeric literal that is not `COORD_EPS` |
| **The test pins the subject** | **FALSIFICATION, mandatory per `CLAUDE.md` plan rule 4**: invert the predicate (`if` → `if not`), show the new tests RED, restore, show green | a test that passes with the predicate inverted pins nothing |

The two-sided oracle R154's row names — *"`graincorp-stem` has exactly one crossing word, so the
passing document is nearly inert under any fix"* — reproduces: gstem `flush=1` (§3.2) and its score
moves 0.9654553611 → 0.9658886894, one escalated token. **Treat that as a near-vacuous PASS row**,
in the sense §3.4.1 of the predecessor spec established: five of six PASS rows there were vacuous
and it was recorded rather than hidden. Here the non-vacuous negative evidence is **cbh (53), apple
(25), ons (20)** — documents with real flush populations that do not regress.

---

## 8. What this loop deliberately does NOT do

1. **It does not reconcile the ruled and word readings per word.** That is R154's proposed close in
   full, and §3.4 shows the flush predicate cannot reach it: a word gap and a column gutter are the
   same picture at character level. Attempting it here would re-import the word reading whose coarse
   form is already measured to break `'-3 SD'`.
2. **It does not deduplicate the twin stroke edges** that make WHO's boundaries dense. That needs a
   stroke-width constant, which R154's row forbids as a per-document property.
3. **It does not touch the `0.6 × median glyph height` row tolerance.** That constant is shared with
   `text_lines` and was explicitly left consolidated-not-eliminated by the predecessor loop.
4. **It does not re-adjudicate WHO's corpus acceptance.** `cor:scoreFloor 0.90` stands; WHO's score
   does not move.
5. **It does not check fidelity against the published PDF.** The predecessor handoff records that
   nobody has, and this loop does not either — it repairs one measured defect in what is carried,
   which is not the same as certifying the whole.

---

## 9. Unverified when this spec was written

- **The unit suite has not been run against this change.** §3.3/§3.4 come from a monkeypatched
  function; no test file has been executed. §6 names six consumers whose test surface is
  **unmeasured**, and `tests/etkl/fixtures.py:927` is the one most likely to move.
- **`ruledroles._within`'s behaviour on a welded banner is reasoned, not measured** (§6, row 1).
- The `flush` counts in §3.2 differ from R154's census on three documents (cbh 53/49, bfs 6/7,
  who 139/129). Attributed to row bucketing; **not run to ground.**
- Whether the second call site (`compile.py:193`) contributes any of §3.3's movement, or whether all
  of it comes from the first, is **not separated.**
- No `plimslop` working-token figure exists for this session; `preflight` reported
  *"unmeasured — no turn recorded for this project"*.

## 10. Residue raised by this spec

**`R156` — a kind judgement got stronger over a conflated grid, and page-scope cbh regressed.**
Raised after the unit suite; the full row is in `residues-open.md`. cbh page-0 band 9 moves
`UNSUPPORTED_TABLE / asserted → RECORD_TABLE / asserted` on a band whose header row concatenates two
side-by-side tables' headers. The conflation is **pre-existing and unchanged by this loop** — the
band's data lines are byte-identical and only the label moved — but the claim is stronger, and this
spec cannot certify it. Carries the §3.3 correction as its half (b).

**`R155` — the residual division is a word gap, and closing it needs both readings.** WHO page 0
band 2 line 0 still divides at `b=594.35` between `in` and `kg)` (§3.4), so the carried top-level
header nodes read `'Z-scores (weight in'` and `'kg)'` rather than one label. Measured, not assumed;
the clearances are in §3.4's table. This is R154's own *"a header line needs BOTH readings at once"*,
narrowed to the one case that survives the flush predicate.
