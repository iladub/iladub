# Spec: the producer escalates a table whose cell an author's rule separates (R301)

**Serves:** maintenance. This is [[R301]], continuing
`docs/superpowers/2026-10-08-r301-guard-position-handoff.md` (PR #321), whose § 5.1 sent this
session to write the spec from five rulings, (a) to (e).

**Date:** 2026-10-08. **Branch:** `r301-producer-guard-spec`, cut from `main` at `cb21b49`.

**Doc impact: none.** No vocabulary term, shape or published query changes. The guard reads the
existing `tab:RuleSeparatedInkShape`. It mints `dec:` decisions with existing terms, and escalates
with a reason *string*. `holon._suggester_uri` derives a suggester IRI from that string, as it does
for every other reason. What changes is what the compiler emits for fed-h41 (§ 6). That is a
behaviour change of the reference implementation, not of the released vocabulary.

**Provenance of the rulings.**
- (a) Settled by measurement, G1 of the handoff above.
- (b) The predecessor's F4 (`2026-10-08-r301-guard-prototype-handoff.md`).
- (c) Already ruled by the maintainer on 2026-09-29: *the log is a boundary* (box-split spec
  § 10.7, R-1 remedy (a)).
- (d) Proposed here and approved in chat on 2026-10-08.
- (e) Ruled by the maintainer in chat on 2026-10-08. The ruling chose *"fix the ledger and guard
  adoption"* over keeping the double count and over deferring it.

The whole design was approved in chat before this file was written.

---

## 0. The concern, first

**fed-h41 aborts today.** Loop 3 shipped `tab:RuleSeparatedInkShape` as a membrane shape only. A
page-scope refusal raises `membrane.MembraneRefusal`, so fed-h41's two merged tables abort their
pages instead of escalating:
- p5 `#htable3`, whose label cell is `Total assets (0) 6,852,491`;
- p7 `#p7-datagrid`, which has 12 glued-sign cells.

**After this loop, fed-h41 compiles with validation on.** Each table is withdrawn and escalated,
its ink is booked once, the rest of each page stays asserted, and the document reads 0.8051 (§ 6).

**The score falls, from 0.8530 to 0.8051, and that is the correct direction.** 163 tokens that the
compiler asserted wrongly become escalations, and the rendered page confirms both misreads (R301,
loop 3). A reviewer who reads the drop as a regression has misread the oracle. The figure that
must not move is every other page of every other document.

## 1. The defect, measured (pointers, not restatements)

| finding | what it shows | where |
|---|---|---|
| F2 | A guard placed after adoption cannot see p5's refused table. Adoption keeps band 3's report verbatim while the graph holds the pass-1 escalation. | prototype handoff § 1 |
| F3 | p7 becomes an adoption candidate, and its refusal note states a false cause (`grid_idx` counts the appended region). | prototype handoff § 1 |
| F4 | `_band_subgraph` is the wrong closure for a withdrawal: it pulls `etkl:reader` in through `{t}-admission`. | prototype handoff § 1 |
| F5 | A withdrawal with no superseding decision makes `effective-chain.rq` lie. | prototype handoff § 1 |
| F7 | An appended region is reported with `ascii=""`. | prototype handoff § 1 |
| G1 | The guard placed before adoption gives p5 187/64, p7 0/137, document 2739/663. No other page moves. | position handoff § 1 |
| G3 | `build_ledger` double-counts a guard-escalated appended region: 274 tokens booked on a 137-token page. | position handoff § 1 |

## 2. The design

### 2.1 Where the guard runs: at every site that admits a table (rulings a, e)

`compile_tables` runs in this order. The **bold** steps are new.

1. Band compilation and `band_marks` differencing, as today.
2. `datagrid_fallback`, as today.
3. **`carry_from_pdf(graph, doc, pdf_path)`.**
4. **The guard (§ 2.2) over `graph`, `reports` and the totals.**
5. The adoption gate, `if datagrid_adopt and escalated_total > 0`. Inside it, after the new graph
   is emitted and **before** anything is installed (graph, reports or totals):
   **`carry_from_pdf` on the new graph, then the guard's select over it.** If the select returns
   any cell, the adoption is **refused whole**. The graph, reports and totals from before adoption
   stand, and the outcome is recorded (§ 2.5).
6. `carry_from_pdf`, score, validate, as today. G4 measured that `carry_rule_ink` is idempotent.

The reason for refusing adoption whole: the ledger is computed once over every grid it adopts
(R290), so withdrawing one grid out of an adoption would invalidate the ledger the gate compared
against. Adopting grid by grid is § 7.

**Invariant I1.** The graph that step 6 validates holds no cell that the guard's select returns.
Step 4 removes them from the band graph, and step 5 never installs a graph that holds one.

**The membrane stays the backstop (R89).** I1 is the producer's claim. `tab:RuleSeparatedInkShape`
still runs over every page graph, and a fixture that bypasses the guard must still be refused
(§ 5, O3). Nothing here weakens or exempts the shape.

### 2.2 The guard (ruling b)

**Classification (CLAUDE.md § 8).** The select is an **AXIOM**: a pure positive conjunctive pattern,
open world and evidence-positive (F6). It is read **from** `tab:RuleSeparatedInkShape`'s `sh:select`,
never copied, so the guard and the membrane cannot drift apart. Everything else here is PROCEDURAL
recording glue. It decides nothing, and it carries no constant.

For each owner table of a returned cell:

- **Exactly one report names it** (`RegionReport.table_uri`). The guard does four things, in order:
  1. Withdraw the table's extent, as defined below.
  2. Mint the refusal decision (§ 2.3).
  3. Escalate `{doc}#region{i}` through `holon.escalate_region`:
     - reason `RULE_SEPARATED_INK`;
     - text: the report's `ascii` (§ 2.4 for an appended region);
     - anchor: the report's anchor, or `tab:DataGrid` for a grid;
     - confidence `0.0`, as for the round-trip refusal precedent (`holon.py`, the `ILADUB.confidence`
       `0.0` site), because the reading was refuted and no confidence is claimed.
  4. Replace the report with `verdict="escalated"`, `cells=0`, `table_uri=None`,
     `tokens_escalated += tokens_asserted`, `tokens_asserted = 0`, and move the same count from
     `asserted_total` to `escalated_total`.
- **No report names it, or more than one does.** The guard does nothing, and the membrane refuses
  the page loudly. This is the backstop firing, not a silent pass. It is unreached on the corpus
  (§ 4, U3).

**Extent of a withdrawal.**
- **Roots:** every URIRef subject in the table's URI space (`t`, or anything starting `t-`), minus
  every root that `g` explicitly types `dec:DecisionHolon`.
- **Closure:** outgoing edges, followed **into blank nodes only**.

On p5 this is exactly the prototype's 113 triples (6 blank-node bboxes). On p7 it differs from
`_band_subgraph` only by `etkl:reader`'s 2 triples (F4). This is a new helper. `_band_subgraph`
is **not** changed, because its consumers (adoption's withdraw-or-refuse check and the pass-2
merge) were measured against its current form, and changing it is not this loop's subject.

### 2.3 The refusal decision (ruling c)

The 2026-09-29 ruling settles the shape: the log is a boundary.
- `{t}-admission` and every band judgement **stay** in the log. The extent above excludes them by
  construction.
- The guard is the **third writer** of `dec:supersedes`, beside section repair and adoption.

There is **one `dec:DecisionHolon` per withdrawn table**:

- It is minted in the region's own decision space. The plan measures the IRI convention:
  `decisionlog` mints `{page_doc}#region{idx}-d{n}`.
- Its option space is `admit` and `refuse`, and it chooses `refuse`. It is decided by the compile's
  existing reader agent.
- It carries the four properties `effective-chain.rq` requires of a superseding decision:
  `dec:regarding`, `dec:order`, `rdfs:label` and `dec:rationale`. The rationale names the rule and
  the cell or cells that cross it.
- It supersedes the **head** of the chain. The chain starts at the band's `verdict` judgement
  (`document._verdict_decision`) or, for an appended grid, at `{t}-admission`, and is walked as
  `document._effective_verdict` walks it (the 2026-09-14 lineage ruling: chain, never fan in).
  `dec:SupersededOnceShape`'s in-degree cap is untouched.
- **If no standing decision is found, the producer RAISES.** The docstring claims every branch
  records one `verdict` per band and every grid mints an admission. A missing one is a producer
  defect that must fail at the call site that built it, not a refusal to record silently (CLAUDE.md § Producer-side guards vs the membrane, R89).

### 2.4 Appended regions (rulings d, e)

**Text (d).** The fallback branch builds an appended region's report with `ascii=""` (F7). It
becomes `roundtrip.render_ascii` over the grid's **own** lines (`_lines[i] for i in grid.rows`).
That is the surface a band's escalation already carries, so it is provenance to the page and
invents nothing.

**Ledger (e).** **Invariant I2: `build_ledger` books every line of the page at most once.**

Today `booked_bands` enumerates `reports`, while `touched` enumerates `range(len(bands))`. An
appended region therefore can never be touched, and its ink enters the untouched term beside the
same lines the grid admits (G3: 137 + 137).

The remedy removes the asymmetry instead of special-casing the index. Every booked region,
whether a band or an appended region, is joined to the lines it covers:
- a band covers the lines inside its author bounds, as today;
- an appended region covers the lines its grid read.

A region is touched when adoption admits any line it covers. Its unadmitted lines become residue,
and only untouched regions keep their own token count. The one fact `build_ledger` cannot see today
is the appended region's line set, and the plan measures the cheapest exact way to carry it there.

### 2.5 Adoption's outcome is reported, not inferred (F3)

`CompilationReport` gains one field that records which of these happened:
- the adoption gate did not open;
- it adopted;
- the ledger refused;
- the guard refused.

The document driver's note then states the cause the page compile observed. It no longer infers
one from a missing region: F3's `no data grid region on the re-compile` was false on p7.

`grid_idx` becomes the **re-compile's band count**, not `len(pages[p].regions)`, which counts
appended regions as well (F3). The plan measures where the band count is available to the driver.

## 3. Classification (CLAUDE.md § 8)

| part | class | why |
|---|---|---|
| the select, read from `tab:RuleSeparatedInkShape` | AXIOM, derivation, open world | positive conjunctive pattern, evidence-positive (F6) |
| extent closure, withdrawal | PROCEDURAL | graph glue over triples already present, bounded by an `rdf:type` test and a node kind |
| refusal decision, escalation, report move | PROCEDURAL | records a judgement the select already made |
| ledger | PROCEDURAL | decidable exact arithmetic over a line join, with no tolerance |
| adoption refusal | AXIOM consumer | the same select, at the second admission site |

**No tuned constant anywhere.** The confidence `0.0` is cited from its precedent, not tuned.

## 4. Unverified, each assigned to the plan's first MEASURE

- **U1. PROPOSED. With I2, p7's `/adopt` ledger reads asserted 137, escalated 0.** The adoption gate
  then opens (`0 < 137`), and the adoption guard's select fires on the re-derived grid's 12 cells.
  If the ledger reads otherwise, § 2.4's join is wrong. If the select is silent, the re-derived grid
  is not the refused one and § 2.1 step 5 is unmotivated. Either way, stop and re-rule.
- **U2.** Keeping `{t}-admission` while its option IRIs lose their triples passes
  `dec:DecisionHolonShape`. This was read from `dec-shapes.ttl` (`optionSpace` minCount 2), never run.
- **U3.** No corpus table's owner maps to zero or several reports. On fed-h41 both map to exactly
  one (prototype). Loop 3's census found the predicate firing on 0 cells of the other 10 documents,
  so the guard is *inferred* to be the identity there. Run, don't infer: § 5, O4.
- **U4.** `document._verdict_decision` and `_effective_verdict` can be reached from `compile.py`
  without an import cycle (`document` imports `compile`). Measure before choosing where they live.

## 5. Oracles

| id | oracle | status |
|---|---|---|
| O1 | `compile_document(fed-h41, validate_shapes=True)` completes, and reads p5 187/64, p7 0/137, document 2739/663 (0.8051). p0–p4, p6 and p8–p10 are identical, region by region, to the `cb21b49` baseline. The adopted set is {2, 3, 5, 8, 10}. | asserted (G1); (c) and (d) change the graph, not the ledger |
| O2 | Refused cells in the document graph: 13 → 0. Each withdrawn table has exactly one refusal decision, and `effective-chain.rq` returns `escalated` for its region. | asserted |
| O3 | A synthetic fixture that bypasses the guard and carries one rule-separated cell is still refused by the membrane (R301's own close criterion, R89). | asserted |
| O4 | Every other corpus document (7 tuned + 3 held-out) compiles to byte-identical scores and region reports with and without the guard. Run serially, one document per process (memory: corpus runs are serial). | PROPOSED until run |
| O5 | I2 as a property: on every adopting page of the corpus, `ledger.asserted + ledger.escalated ≤` the page's token count. G3 violates it, so it fails today. | asserted to fail today |
| O6 | p7's adoption outcome reads *guard refused*, and the driver's note says so. | PROPOSED (U1) |

**Falsification, per pin (plan rule 4):**
- Delete the pre-adoption guard: O1 p5 reverts to 213/38, and O2 fails.
- Delete the adoption guard: O6 fails, and the membrane aborts p7 under I2.
- Revert I2: O5 fails on p7.
- Delete the refusal decision: O2's chain check fails.
- Feed the shape's fixture to the producer with the guard on: it escalates. With the guard off,
  O3 refuses it.

## 6. What changes for the corpus

| document | before | after |
|---|---|---|
| fed-h41 | `MembraneRefusal` with validation on; 0.8530 with it off | 0.8051 (2739/663) with validation on |
| every other document | unchanged | unchanged (O4) |

## 7. What is NOT done

- **Adopting grid by grid.** Adoption is refused whole when any grid it would install is refused.
  Raise a register row if a page with two grids, one refused, ever appears.
- **R300.** p3 `adopt#htable7` and p10 `adopt#htable3` stay dangling. p5 leaves R300's list as a
  side effect (G1).
- **`_band_subgraph` is unchanged** (§ 2.2).
- **Empty `tab:RuleSpan` nodes** on a page whose every cell was withdrawn (p7, G4) are left in
  place. They are harmless to the shape, which joins on a cell.
- **No new vocabulary.** If the plan finds that the refusal decision needs a term `dec:` lacks, it
  stops: that is a spec change.

**R301 closes** when O1 to O3 and O5 hold on `main`, with O4 run and recorded.

## 8. Addendum: S1–S3, ruled by the maintainer in chat on 2026-10-08

The plan's first measurements (`docs/superpowers/2026-10-08-r301-plan-seams-handoff.md`, PR #323)
found three places where this spec was wrong or left something open. The maintainer accepted all
three proposed remedies. **This section overrides any earlier sentence it contradicts.** The plan
cites this section and does not re-derive it.

**S1. The extent of a withdrawal (amends § 2.2).**
- The handoff measured that the roots rule `t`, or anything starting `t-`, also matches
  `…#p{n}-datagrid-2…` (a sibling grid, R290) and `…#p{n}-datagrid-residue…`.
- **Roots now exclude three kinds of subject:**
  - any root in the URI space of **another** report's `table_uri` `u`, meaning the root equals `u`
    or starts with `u-`;
  - any root in the residue's URI space, `{doc}#p{page}-datagrid-residue` or anything starting
    with that plus `-`;
  - as before, every root explicitly typed `dec:DecisionHolon`.
- The closure is unchanged: outgoing edges, followed into blank nodes only.

**S2. The refusal decision's identity (amends § 2.3).** The refusal is **not** minted through
`ReadingRecorder`/`BandRecorder`. A second `recorder.band(i)` restarts at `-d0` and overwrites the
band's existing decision, and the recorder is bound to the graph from before adoption. Instead the
refusal is written directly, and it has five fixed properties:
- **IRI:** `{doc}#region{i}-refusal`, deterministic and outside the `-d{n}` space.
- **`rdfs:label`:** `"refusal"`, never `"verdict"`. So `document._verdict_decision`, which returns
  the first `"verdict"` under `#region{i}-d`, still finds the original.
- **`dec:order`:** one past the superseded head's `dec:order`. **Interpretation for the plan,
  flagged rather than ruled:** a fallback-path `{t}-admission` head carries no `dec:order` (handoff
  M9), and there the refusal's order is `0`.
- **`dec:regarding`:** `{doc}#region{i}`, plus `dec:rationale` and `dec:decidedBy etkl:reader`.
- **Option space and choice:** two `dec:Option`s labelled `admit` and `refuse`, with
  `dec:chosen` → `refuse`.

`dec:supersedes` → the head, and the raise-on-missing-head rule of § 2.3 stand.

**S3. Oracle O2 (amends § 5).** `effective-chain.rq` returns `dec:chosen/rdfs:label`. So for each
withdrawn table's `{doc}#region{i}`, O2 now reads:
- the chain's **last row is the refusal**, with judgement `refusal` and chosen `refuse`;
- each withdrawn table has exactly one such decision;
- refused cells in the document graph go from 13 to 0.

The option is **not** relabelled to fit the oracle. "Returns `escalated`" in § 5 is withdrawn.
