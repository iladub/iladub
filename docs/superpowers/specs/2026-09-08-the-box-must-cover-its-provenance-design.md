# Spec — [[R182]]: the box must cover its provenance

**Loop:** `r182-the-box-must-cover-its-provenance`, 2026-09-08.
**Runs action 5a of** `docs/superpowers/2026-09-07-r181-handoff.md`, which was typed **PROPOSED**
on two facts neither measured nor obviously true. Both are now measured. **One went the way the
handoff feared and one did not**, and the pair together make R182 buildable in one bounded loop
rather than the "materially bigger" one the handoff warned of.

**Doc impact: none.**

---

## 0. The gate classification (CLAUDE.md § 8)

Three changes, three classes, stated before any code:

| change | class | why |
| --- | --- | --- |
| emit `tab:sourceRegion` + `tab:sourcePage` on each `tab:HeaderSourceCell` | **PROCEDURAL** | raw extraction — copying four bounds and a page index off a `cells.SourceCell` already in scope. No decision, no constant. The predicates are dedicated rather than `tab:hasBBox`/`tab:onPage`, for the reason § 2.3 measured the hard way. |
| emit `prov:wasDerivedFrom` from a `tab:LabelCell` to the source cells its text was joined from | **PROCEDURAL** | the membership is **already decided** upstream — the role vector was NEURAL-proposed and oracle-disposed before `build_row_reading` runs, and `extra[col] → nodes[tgt]` records the join. This writes down a decision it does not take. |
| `tab:LabelCoversProvenanceShape` | **AXIOM (constraint → SHACL, closed world)** | the contract membrane: what may cross into the clean holon. A label whose box does not cover the ink it claims as provenance is a false provenance claim (CLAUDE.md § 6, § 7). |

No tuned constant appears in any of the three. The comparison is exact on the emitted `xsd:decimal`
bounds — the union is a `min`/`max` of the very numbers being compared, so no tolerance is needed
and **none is introduced**; see § 4.3 for why an `EPS` would be a defect here rather than a safety
margin.

---

## 1. The handoff's first question, ANSWERED: there is NO label→source edge

> *"Is there an edge from a `tab:LabelCell` to the `tab:HeaderSourceCell`s it was joined from?"*

**No — there is none, in either direction, at any hop.** Measured on the graph graincorp-stem p0
actually emits (`scripts/`-free probe, `compile_tables(…, 0, validate_shapes=False,
datagrid_fallback=False)`):

```
HeaderSourceCell=26 LabelCell=17 HeaderNode=35
--- predicates INTO a HeaderSourceCell (pred, subject types) ---
   tab:hasHeaderSourceCell                  tab:HierarchicalTable          26
--- predicates OUT of a HeaderSourceCell ---
   tab:sourceRow  26   rdf:type  26   tab:sourceText  26
--- one-hop edges between {LabelCell,HeaderNode} and HeaderSourceCell: 0 ---
--- predicates INTO a LabelCell ---
   tab:hasLabel                             tab:HeaderNode                 17
   tab:hasCell                              tab:HierarchicalTable          17
```

A `tab:HeaderSourceCell` is reachable **only** from the table, and a `tab:LabelCell` **only** from
its `tab:HeaderNode` and the table. The one path between them runs table → {17 labels} × {26 source
cells} — a cross-product, not a derivation. **A containment shape has no `sh:path` today**, which is
exactly what [[R181]] disposed as UNEXPRESSIBLE.

`prov:wasDerivedFrom` does exist in this area (`tab:RepeatedHeaderRow` in `vocab/ontology/tab.ttl`) and is **not** this
edge: it points a *repeated* header row on a continuation page at the originating page's source
cells. Same predicate, different subject class, different purpose. Reusing the predicate is
correct — it is what `prov:wasDerivedFrom` means — and reusing the *shape* would not be.

### 1.1 …but the derivation is available at the site [[R181]] already fixed

This is what makes the loop bounded rather than "materially bigger", and it is a measurement, not
a reading of intent:

* `build_row_reading` (`src/iladub/etkl/rowrole.py:132`) computes `extra[col] = [frags]` and
  resolves `tgt`, the index into `nodes`. **The pair `(tgt, frag)` is the derivation**, held in a
  local at the moment the union is taken.
* `source_cells` is built in the **same function**, as a flat enumeration of `header_rows`
  (`rowrole.py:212-213`), so a fragment's flat index `k` is derivable without re-deriving anything.
* Both URI schemes are keyed on `table_uri` and on those two indices, and nothing else:
  `assert_hier_region` mints `f"{table_uri}-hl{idx}"` for `idx` over `region.tree`
  (`src/iladub/etkl/holon.py:538`), and `emit_reading_evidence` mints `f"{table_uri}-hsc{k}"`
  (`rowrole.py:261`). `resolve_header_row_roles` passes `tree=nodes` to the first and
  `source_cells` to the second in adjacent lines (`rowrole.py:307-308`), so the two index spaces
  are the ones `build_row_reading` returned.

The discard R182's row names — *"`source_cells` currently projects `(row, cell.text)` and discards
the cell, the same discard [[R181]] was"* — is confirmed by reading those three lines, and it is
the only thing standing between the graph and the edge.

---

## 2. The handoff's second question, ANSWERED — and the answer was RIGHT ABOUT THE GATE AND WRONG ABOUT THE SYSTEM

**Read § 2.3 before acting on § 2 or § 2.1.** The measurements below are correct and were run on
the real artefacts; the *conclusion* drawn from them — that the R19 mechanism is dead — is
**REFUTED**, by this loop's own full suite, after the emission had already been written against it.
The section is kept as measured rather than rewritten, because the gap between what it measured and
what it concluded is the finding.

> *"Does putting `tab:hasBBox` on a `tab:HeaderSourceCell` RDFS-type it as a `tab:Cell` and trip
> `tab:WrappedCellShape` at the tiling gate?"*

**Not at the gate, and not at the document membrane — but yes elsewhere (§ 2.3).** As asked, about
the gate, the answer is No. Measured twice, on real artefacts rather than a synthetic stand-in — the first synthetic
attempt is reported in § 2.2 because it was *wrong in a way worth recording*.

**At the tiling gate.** `tiling.region_tiles` was wrapped during a graincorp-stem p0 compile to
capture the exact scratch region graph the oracle was handed; `tab:hasBBox` + `tab:onPage` were
added to **all 26** of its `tab:HeaderSourceCell`s and the gate re-run:

```
region_tiles calls captured: 1 (conforming: 1)
scratch#0: HeaderSourceCells=26  baseline conforms=True  with hasBBox+onPage conforms=True
```

**At document scope**, on the emitted page graph through `compile._validate` (both legs):

```
baseline doc-scope conforms=True legs=()  HeaderSourceCells=26
with hasBBox+onPage doc-scope conforms=True legs=()
```

### 2.1 WHY the membrane admits it — and the over-reach this section originally committed

The R19 mechanism is not merely dodged **at the membrane** — there, it no longer operates.
*(This paragraph originally read "it no longer exists". That is the sentence § 2.3 refutes, and it
is left visible rather than silently corrected: the error was generalising from the membrane to the
repo, and a reader needs to see the step that was skipped.)* `membrane.subclass_closure`
supplies both engines a **subclass-only** closure and deliberately does not materialise
domain/range typing (`src/iladub/etkl/membrane.py:458-465`, verbatim: *"A node no longer becomes a
`tab:Cell` merely by carrying `tab:hasBBox` — that inference is the R19 accident, and dropping it
closes that hazard at its root"*). `_validate_pyshacl` runs `inference="none"` and takes the same
payload (`membrane.py:111-125`), so **neither engine** types by domain any more.

**Consequence for the two sites the handoff and the register cite as the live reason to fear this.**
`compile.py`'s `_emit_unit_markers` docstring and `tab:markerRegion`'s comment in `vocab/ontology/tab.ttl` both said `tab:markerRegion` exists
*because* `tab:hasBBox`'s domain "would RDFS-type the marker as `tab:Cell` and trip
`tab:WrappedCellShape` at the gate". As a statement of **why the property was introduced** that is
history and stays true. As a statement of a **live hazard** it is stale: the hazard was closed by
the subclass-only-closure loop (spec `2026-08-06-subclass-only-closure-design.md`), and nothing
updated those two comments. **This loop does not touch `tab:markerRegion`** — see § 5 — but it
records the staleness so the next reader does not pay for it a third time.

### 2.2 The synthetic probe that could not answer this, and why it is reported

The first attempt built a minimal graph containing one `HeaderSourceCell` and ran `region_tiles`
on it. It returned `conforms=False` **for the baseline, with no `hasBBox` at all** — the eleven
tiling invariants refuse a graph with no table in it, so the probe had no valid control and its
"with `hasBBox`" arm would have been read as a false positive. It also tripped
`membrane.audit_literals` by minting `xsd:decimal` from Python `int`s (R92). Recorded because the
correct instrument is the one used above — **capture the artefact the gate is really given, do not
reconstruct one** — and because a synthetic baseline that fails is the shape of a measurement that
looks like an answer and is not.

### 2.3 REFUTED — the full suite found 26 nodes the membrane admitted, and the R19 mechanism is alive

`tab:hasBBox` was emitted on every `tab:HeaderSourceCell` on the strength of § 2. The targeted
tests passed, the tiling gate passed, the doc-scope membrane passed, and the **whole-corpus verdict
diff was whole-file identical on 27 pages.** The full suite then failed:

```
FAILED tests/etkl/test_closure_equiv.py::test_both_closures_agree_on_a_real_page_graph
FAILED tests/etkl/test_closure_equiv.py::test_both_closures_agree_on_a_mutated_real_page_graph
2 failed, 1512 passed, 7 skipped, 1 xfailed in 3556.98s (0:59:16)

AssertionError: full=False sub=True on the real stem page
AssertionError: violation-set divergence on the mutated real page:
  only-full=[(sh:SPARQLConstraintComponent, doc#htable2-hsc0, None),
             (sh:SPARQLConstraintComponent, doc#htable2-hsc1, None), … ]  only-sub=[]
```

**The mechanism, exactly.** `tests/etkl/test_closure_equiv.py` compares two closures over the same
real page graph: `membrane.rdfs_closure` (owlrl, FULL RDFS) against `membrane.subclass_closure`.
The full leg materialises `tab:hasBBox rdfs:domain tab:Cell`, so every `tab:HeaderSourceCell`
became a `tab:Cell`; a `HeaderSourceCell` carries `tab:sourceText`, **not** `tab:cellText`, so
`tab:WrappedCellShape`'s drop-continuation guard fired on **26** of them. The subclass-only leg saw
none of it. That divergence is the precise failure the differential exists to detect (R59, R61):
*a shape lost sight of its focus node.*

**Why § 2's measurements did not catch it, and this is the transferable part.** They asked
*"does the MEMBRANE refuse this?"* and answered correctly. The claim written down was *"the R19
mechanism is closed at its root."* Those are different claims, and the gap between them is one
unexamined quantifier: `subclass_closure` is what the **membrane** uses, and `rdfs_closure` still
exists and is still exercised. **Two conforming validations are not a survey of the consumers of
an inference.** The `enumerating-before-claiming` discipline applies to *"nothing types by domain
any more"* exactly as it applies to a claim about call sites — and `grep -rn "rdfs_closure"
src/iladub/` was never run.

**Why the corpus guard could not catch it either, and why that matters more than the miss.** The
guard ran, on all 27 pages, and reported *whole-file identical*. It compiles through the
**membrane** — the one leg that is blind to this by construction. A guard that exercises only the
consumer you already measured cannot falsify a claim about the consumers you did not enumerate.
This is the sharpest available instance of R181's own warning that the corpus run is a guard and
not an oracle.

**The enumeration that should have been run, run now.** `grep -rn "rdfs_closure" src tests scripts`
returns three consumers besides its own definition: `tests/etkl/test_closure_equiv.py` (the
differential that caught this), `tests/etkl/test_membrane.py` (five tests pinning the retained
reference closure — `:97` is literally
`test_rdfs_closure_materializes_subclass_and_domain_types`), and
`scripts/measure_dec_membrane.py`, whose own docstring at `:18` states the decisive thing:

> `RDFS = membrane.rdfs_closure` — what a **CONSUMER** applying our published axioms sees

**That is the principled argument, and it outranks the test failure.** `vocab/ontology/tab.ttl`
publishes `tab:hasBBox rdfs:domain tab:Cell` under CC-BY. Any downstream consumer running a
stock RDFS reasoner over our published graph — which is the entire point of publishing FAIR
axioms — derives `HeaderSourceCell ⊑ Cell` and can then legitimately refuse our own emission.
The membrane's decision not to materialise domain typing is a **local engineering choice about
one validator**; it does not and cannot bind anyone downstream. So emitting `tab:hasBBox` on a
node that is not a `tab:Cell` would have been a **false assertion in the published graph**
(CLAUDE.md § 7), and it would have been false whether or not any test caught it. The closure
differential is the instrument; the contract is the reason.

**The remedy, and the reversal it forces.** The geometry now rides `tab:sourceRegion` and
`tab:sourcePage`, minted with `rdfs:domain tab:HeaderSourceCell` — **the exact pattern
`tab:markerRegion` already uses, for the exact reason its comment already gave.** So: the two
comments this spec declared stale are restored (with this evidence added to them), the residue
raised to collapse `tab:markerRegion` is **withdrawn before it was ever acted on**, and the
precedent this loop was about to retire turns out to be the thing that saved it. The label side
keeps `tab:hasBBox`, because a `tab:LabelCell` genuinely *is* a `tab:Cell`.

---

## 3. The third question, unasked and answered anyway: the shape is expressible AND both engines agree

The two questions § 5a prescribed do not cover the one that would sink the loop latest and
cheapest: **can the constraint be written at all on this repo's graph?** The repo's bboxes are
**blank nodes** (`holon.py:24-32`, `BNode()`), **no existing shape reads bbox coordinates in
SPARQL** (`grep tab:x0 vocab/shapes/*.ttl` → nothing), and rudof's blank-node `sh:sparql`
incapacity is on record (R88/R94). A shape that cannot be evaluated on the default engine is
unexpressible for a second reason, and the loop would have found out after building the graph
change.

Measured, on the exact col-7 numbers from `2026-09-07-the-box-that-covers-the-join-design.md` § 2 —
the union box `(376.32, 67.83, 417.58, 86.31)` against the leaf-only box `(376.32, 81.03, 417.58,
86.31)`, with one source cell at `(376.32, 67.83, 417.58, 73.11)`:

```
rudof     union-box: conforms=True   leaf-only box: conforms=False
pyshacl   union-box: conforms=True   leaf-only box: conforms=False
```

**Both engines evaluate the blank-node traversal, and both refuse exactly the pre-[[R181]] box.**
The shape is expressible, the disposal mechanism works, and the engines agree — established
*before* a line of emission code is written.

---

## 4. The oracle

### 4.1 The disposal R182's row prescribes, and why it has power

> *"a shape that FAILS on today's graincorp-stem p0 emission with the [[R181]] union reverted, and
> passes with it."*

It has power because the **population is known and non-empty**: all 7 joined labels on
graincorp-stem p0 have a fragment whose `top` is strictly above the leaf line's `81.03` (5 also
extend `x1` beyond the leaf's) — the full table is
`2026-09-07-the-box-that-covers-the-join-design.md` § 2.

**What reverting actually does, corrected from what this section first claimed.** It does NOT
report 7 doc-scope violations. The shape sits at the **region gate**, so a reading whose label
misses its provenance is refused *there*: `region_tiles` returns False and
`resolve_header_row_roles` returns `None`, escalating the band with the graph untouched. Measured —
with the union reverted, `test_the_real_emission_conforms` fails not on the shape's verdict but on
its precondition, `assert out is not None, "the fixture must resolve, or this file tests nothing"`.
That is a *stronger* disposal than the row asked for and a *different* one, and saying "7
violations" would have been an unmeasured claim about a scope the shape never reaches.

### 4.2 What the corpus run is, and is not

A whole-corpus verdict diff is a **guard**, not evidence the shape generalises. Measured on THIS
emission rather than carried forward from R181's population: across all 27 corpus pages, **1 page
emits a label→source edge at all, carrying 8 of them** — graincorp-stem p0, the 8 fragments landing
on its 7 labels. On the other 26 the constraint is vacuous by construction. The diff answers *"did
adding a shape refuse a page that used to pass?"* — worth running, and never to be quoted as
coverage.

### 4.3 No tolerance, deliberately

`unbooked_ink_fate.py` carries `EPS = 0.01` because it compares a **word's** measured extent against
a **cell's** rounded box — two independently rounded quantities. This shape compares a label box
against the very source boxes it is the `min`/`max` of, both rounded by the same
`Decimal(str(round(v, 2)))` writer (`holon.py:28-31`). The union of rounded values is exactly the
rounded value of the union for `min`/`max`, so equality is exact and an `EPS` would only widen the
shape's blind spot. **A tolerance here would be prima facie evidence the decision belongs elsewhere**
(CLAUDE.md § 8).

### 4.4 Falsification, per CLAUDE.md § Plan authoring discipline rule 4

Every pin ships with its falsification: revert the union in `build_row_reading`, show the new
shape test **failing**; restore; show it green. The pins are **CI-runnable** — the synthetic
`caption_and_wrap_band` fixture in `tests/etkl/test_rowrole_reading.py` needs no corpus, which is
the [[R173]] datum § 5c of the predecessor handoff asked to be recorded.

---

## 5. What this loop deliberately does NOT do

* **It does not touch `tab:markerRegion`, and it must not.** § 2.1 first ruled its rationale stale;
  § 2.3 refuted that. The property is doing live work, `tab:sourceRegion` is now its sibling, and
  both comments have been restored and strengthened with this loop's evidence. The residue raised
  to collapse it was **withdrawn before anything was built on it** — the register carries the
  withdrawal rather than the row, so a later reader meets the correction and not the proposal.
* **It does not emit geometry on `tab:RegionCaption`.** Captions are the other half of
  `emit_reading_evidence` and the same discard applies to them, but no shape and no residue asks
  for it, and [[R178]] settled the caption population separately.
* **It does not make `tab:hasBBox` on a `tab:HeaderSourceCell` mandatory.** The shape conditions on
  the edge existing, so a source cell nothing was derived from is not required to carry a box —
  requiring it would infer from absence, which is the open/closed-world split (CLAUDE.md § 8).
* **It does not extend the shape to `assert_record_region` or the transposed maker.** Those mint
  labels from single `cells.SourceCell`s with no join, so the constraint is vacuously true there;
  it is targeted at `tab:LabelCell` regardless, and vacuous truth is the correct outcome, not a gap.
