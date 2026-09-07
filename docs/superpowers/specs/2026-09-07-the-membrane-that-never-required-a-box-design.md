# The membrane that never required a box — design

**Residue:** [[R179]], raised 2026-09-07 by the loop that closed [[R177]].
**Written 2026-09-07.**

**Doc impact: none.**

---

## 0. Global constraint — the neurosymbolic gate (CLAUDE.md § Core design principles 8)

This loop's whole decision is a **constraint**: *what may cross into the clean holon*. That is the
**AXIOM / closed-world** half of the split — **SHACL**, at the membrane, never SPARQL derivation and
never Python. No procedural code is added by this loop, and the one Python edit it makes
(`_PHYSICAL_SHAPE_IRIS`) is the PROCEDURAL engine glue that already exists at
`src/iladub/etkl/tiling.py:45` — a list of shape IRIs, carrying no domain decision.

## 1. The residue, restated on its measurement

`tab:EntryCellPhysicalShape` (`vocab/shapes/tab-physical-shapes.ttl:13-19`) requires
`tab:cellText`, `tab:onPage` and `tab:hasBBox` on **every** `tab:EntryCell`. Nothing says the same
for `tab:LabelCell`:

```
$ grep -rn "LabelCell" vocab/shapes/*.ttl
vocab/shapes/tab-shapes.ttl:294:   FILTER NOT EXISTS { ?lc a tab:LabelCell ; tab:cellText ?lt . FILTER(CONTAINS(?lt, ?txt)) }
```

One hit, inside `tab:HeaderContentConservedShape`'s SPARQL body, and it constrains *content
conservation*, not geometry. So R177's 79 boxless label cells violated CLAUDE.md § Core design
principles 6 (provenance-to-the-page) for months **with the membrane silent** — a producer-side
repair is now the sole enforcement, on one emitter, pinned by one test module.

**This is the asymmetry to fix, and it is not cosmetic.** A `tab:LabelCell` is what a
`tab:HeaderNode` points at with `tab:hasLabel`; the ontology's own comment on that very property
says so (`vocab/ontology/tab.ttl:55-57`: *"Links a header node to the LabelCell carrying its surface
text + geometry."*). The vocabulary already asserts that a label carries geometry. Only the membrane
never checked.

## 2. The fork the residue names — taken, and one half of it REFUTED as unexpressible

R179's row and the R177 handoff § 5a both state the fork as: **(a)** `sh:minCount 1` on all labels,
with `span.build_reading`'s flank filler forced to stop being a `tab:LabelCell`; or **(b)** a
conditional shape *"firing only when the node it labels carries geometry"*.

### 2.1 (a) is REFUTED — it is a reading change wearing a membrane change's clothes

Option (a)'s cost is not in the shape; it is in what must be deleted to satisfy it. Four read sites, in three modules, read the label the filler emits:

```
$ grep -n "TAB.hasLabel" src/iladub/etkl/*.py
src/iladub/etkl/denormalization.py:72    lc = g.value(h, TAB.hasLabel)
src/iladub/etkl/denormalization.py:273   lc = g.value(h, TAB.hasLabel)
src/iladub/etkl/reshape.py:29            lc = g.value(h, TAB.hasLabel)
src/iladub/etkl/recipe.py:56             best_label = _text(g, g.value(h, TAB.hasLabel))
```

`reshape.py` is the **round-trip oracle** — the semantic disposer of the NEURAL proposals in
CLAUDE.md § 8. Removing an emission that the oracle reads changes what the oracle sees, and
therefore what it admits. A membrane loop that silently re-tunes the disposer is exactly the shape
of change this repo forbids folding into another one.

**(a) is not wrong on the merits and is not closed off** — an empty-text, boxless `tab:LabelCell`
carries nothing, and one could argue it should never be minted. It is *out of scope here* because it
is an emission decision with an oracle in its blast radius, and this residue is about the membrane.
Recorded as such in § 5.

### 2.2 (b) AS WRITTEN IS NOT EXPRESSIBLE — no `tab:HeaderNode` carries geometry

The condition both the row and the handoff prescribe — *"the node it labels carries geometry"* —
cannot be evaluated over the graph the emitters write. Measured:

```
$ grep -n "TAB.hasBBox" src/iladub/etkl/*.py
datagrid.py:682   holon.py:49,144,194,262,294,346,554,600   ruledroles.py:481
```

Ten write sites: eight onto an entry or a cell URI (`e_uri`, `lc`, `e`), one onto a
`tab:RepeatedHeader` (`ruledroles.py:481`, `u`) — and **none onto a header-node URI**, which is the
claim that matters. `assert_hier_region`'s header-node block
(`src/iladub/etkl/holon.py:522-555`) writes `rdf:type`, `tab:hasHeaderNode`, `tab:headerLevel`,
`tab:coversColumn`, `tab:hasLabel` and `tab:parentHeader` — and no geometry at all. The geometry
[[R177]] added lives on `headers.HeaderNode` as **Python dataclass fields**, and reaches RDF only
by being written onto the LabelCell. A SHACL shape cannot see it.

This is a defect in the residue's own prescription, found by measuring it, and it is the reason this
spec exists rather than a one-line shape.

### 2.3 (b′) — the expressible condition is the LabelCell's OWN non-empty text

```
tab:cellText is non-empty  ⇒  tab:hasBBox and tab:onPage are required
```

**Why this is the right predicate and not a proxy for the one we could not express.** There are
exactly two construction sites for a `headers.HeaderNode` in the whole source tree:

```
$ grep -rn "HeaderNode(" src/iladub/
src/iladub/etkl/headers.py:458   nodes.append(HeaderNode(lvl, covers, cell.text, None, cx,
                                     x0=cell.x0, top=cell.top, x1=cell.x1,
                                     bottom=cell.bottom, page=cell.page))
src/iladub/etkl/span.py:38       out.append(HeaderNode(0, (flank,), "", None))
```

The first is built from a `cells.SourceCell`, whose four bounds and `page` are **non-optional
typed fields** (`src/iladub/etkl/cells.py:19-27`) and whose text is the join of at least one `Word`
(`_cell_from`, `cells.py:96-104`, which takes `min`/`max` over `words` and so cannot be reached with
an empty list). The second is `span.build_reading`'s flank filler, whose text is the literal `""`
and which carries no geometry. Every other mutation of a node is a `dataclasses.replace`
(`headers.py:326,368,373,489`, `span.py:29,33,36`, `rowrole.py:182`), which preserves the fields it
does not name.

**Therefore, on this tree: a header node lacks geometry if and only if it is the flank filler, and
the flank filler is the only node whose text is empty.** The text test is not an approximation of
the geometry test — over the emitted graph the two partition the same one node, and the text test is
the half that survives serialisation.

**And it is the exact converse of a shape that already ships.** `tab:WrappedCellShape`
(`vocab/shapes/tab-physical-shapes.ttl:26-42`) says *bbox present ⇒ text non-empty*. This one says
*text non-empty ⇒ bbox present*. Together they make text and geometry co-present on a label cell, in
both directions, with the textless-and-boxless filler the single honest exemption — which is what
CLAUDE.md § Core design principles 7 requires of it.

## 3. The change

### 3.1 The shape

`tab:LabelCellPhysicalShape`, `sh:targetClass tab:LabelCell`, in
`vocab/shapes/tab-physical-shapes.ttl`. Two `sh:sparql` constraints, in `tab:WrappedCellShape`'s
style — one for `tab:hasBBox`, one for `tab:onPage`, **separately**, so a violation names which half
is missing. R177's falsification 2 is the evidence that this separation earns its keep: deleting the
`tab:onPage` triple failed exactly one pin, and would have been invisible under a merged constraint.

Each fires only on `$this tab:cellText ?t . FILTER(strlen(str(?t)) > 0)`, and each excludes a
cell that is also a `tab:EntryCell` — see § 4.3, which is the finding that forced it and the proof
that it costs nothing.

### 3.2 Where it must be REGISTERED — and why the file alone is a defect

Two registries, and they are not the same:

| registry | what it gates | reached by |
| --- | --- | --- |
| `vocab/shapes/tab-physical-shapes.ttl` | `compile`'s final whole-graph validation | automatic — `compile.py:556` loads the whole file |
| `tiling._PHYSICAL_SHAPE_IRIS` (`src/iladub/etkl/tiling.py:45`) | `region_tiles`, the per-region admission gate | **only by naming the IRI** — `_build_tiling_shapes` takes CBDs of a listed IRI set |

Adding the shape to the file **and not** to `_PHYSICAL_SHAPE_IRIS` is a defect, not a smaller
change: a violating region would pass the gate and then **crash** the final validation instead of
escalating. That is the loop-G lesson already recorded in the source, at `tiling.py:35-39` — *"a
physical-shape defect must refuse HERE, not crash compile.py's final whole-graph validation"* —
and R19 is the residue that bought it. The shape goes in both.

### 3.3 Gate classification (CLAUDE.md § 8)

**AXIOM — Constraint → SHACL, closed world.** The membrane deciding what may cross into the clean
holon. It is *not* a derivation: it infers nothing from the absence of a box, it refuses a cell that
claims text without saying where the text is. The one-line Python edit (§ 3.2) is the same
PROCEDURAL glue the eleven tiling IRIs already sit in.

## 4. Oracles

| # | oracle | falsifies |
| --- | --- | --- |
| **O1** | `scripts/unbooked_ink_fate_corpus.py` BEFORE and AFTER, whole-file `diff` of the per-page verdict lines, exactly as `2026-09-07-the-label-cell-that-cannot-be-found-design.md` § 4.1 does it | the prediction that the shape is a no-op on this corpus — i.e. some region asserts today *only because* nothing required a box on its labels |
| **O2** | the worked example (`examples/tables/hier-physical-conformant.ttl`, extended with a boxed label **and** a textless boxless one) conforms under `_vp` | the shape rejects an honest reading, or fails to exempt the filler |
| **O3** | the negative fixture (`tests/tab-label-nobox-leak.ttl`: a LabelCell with text and no box) **fails**, naming `LabelCellPhysicalShape` | the shape pins nothing |
| **O4** | a test asserting the shape IRI is in `tiling._PHYSICAL_SHAPE_IRIS` **and** that `region_tiles` returns `False` on a region graph carrying a textful boxless label | § 3.2's defect — shipping into the file only |
| **O5** | full `tests/etkl/` suite, corpus included | anything else |

**O1 is the one that can end the loop.** If the diff is not `IDENTICAL`, the shape has found a
second R177 on another emitter branch. **That is a better outcome than shipping the shape** and must
be reported as a finding — never worked around by weakening the shape until the corpus goes quiet.

### 4.1 RESULTS

| # | result |
| --- | --- |
| **O1** | **PASS — WHOLE-FILE IDENTICAL**, a stronger form than the predecessor's verdict-line diff. See § 4.2. |
| **O2** | **PASS.** `tests/test_tab.py::test_label_physical_conformant_passes` — the extended example carries three boxed labels and the textless boxless `ex:lUnit2`, and conforms under `_vp` (topology + physical shapes together). |
| **O3** | **PASS.** `tests/test_tab.py::test_label_missing_box_leak_fails` — `tests/tab-label-nobox-leak.ttl` is refused, and **both** messages appear, so neither half hides behind the other. |
| **O4** | **PASS.** `tests/etkl/test_label_physical_gate.py`, **5 passed** — three refusals/admissions at `region_tiles`, the flank-filler exemption, and the IRI-list pin. Falsification **F3** is the one that earns this oracle its place: with the shape in the file and out of `_PHYSICAL_SHAPE_IRIS`, `test_label_missing_box_leak_fails` **still passes** — the file-level negative test cannot see the gate defect at all. |
| **O5** | **FAILED on the first run — `3 failed, 897 passed, 2 skipped, 1 xfailed in 40:07`** — and that failure is § 4.3, the most useful thing this loop produced. **Second run after the repair: `903 passed, 2 skipped, 1 xfailed in 40:58`.** Reconciled by collection, not by arithmetic on a remembered figure: `pytest --collect-only` gives **896** on the stashed base tree (`git stash -u`) and **906** on this branch; the 10 are this loop's 8 gate pins plus **2 parametrised meta-tests that adopted the new leak fixture on their own** — `test_closure_equiv.py::test_both_closures_agree_on_every_committed_leak[tab-label-nobox-leak.ttl]` and `test_membrane_equiv.py::test_both_engines_refuse_every_committed_leak[tab-label-nobox-leak.ttl]`, both passing. So the fixture is checked under both closures and both SHACL engines without this loop asking. |

### 4.2 The corpus diff — O1 in full

Both runs are `PYTHONPATH=src python3 scripts/unbooked_ink_fate_corpus.py`, 7 documents / 27 pages,
BEFORE at `d2aa303` (the R177 merge) and AFTER on this branch:

```
$ diff BEFORE.txt AFTER.txt && echo WHOLE-FILE-IDENTICAL
WHOLE-FILE-IDENTICAL
```

Not only the same `score` / `asserted` / `escalated` on all 27 pages, but the same per-band ink
booking and the same orphan texts — every byte. The prediction of R177's handoff § 5a holds on this
corpus: **the shape is a no-op on what the tree already reads**, and it is a no-op for the reason
§ 2.3 gives — the only label the emitters write without a box is the one whose text is empty, and
the shape exempts exactly that one.

**The comparison method matters and is inherited deliberately.** R177's loop recorded that comparing
these runs by grepping `^page N` produces a false alarm, because every document has a page N. The
diff above is whole-file, in document order, which is the honest form.

### 4.3 What O5 found, and why the shape now excludes entry cells

The first full `tests/etkl/` run was **`3 failed, 897 passed, 2 skipped, 1 xfailed in 40:07`**. The
corpus said the shape was a no-op; the suite said it was not. The suite was right, and the three
failures are two different things.

**Two were fixture debt** — `test_conservation_shape.py::test_text_merged_into_a_label_is_conserved`
and `::test_graph_without_source_cells_is_unaffected`. Their `_label` helper minted a
`tab:LabelCell` carrying text and nothing else, because when it was written nothing required more.
That is precisely the graph [[R177]] repaired at the emitter and this shape now refuses, so the
helper was made faithful to what `assert_hier_region` actually writes. **No assertion in either test
changed**; the repair is in the fixture, and its docstring says why so the next reader does not
mistake it for a weakening.

**The third is a real interaction, and it is the R19 accident at a new site.**
`test_closure_equiv.py::test_both_closures_agree_on_a_mutated_real_page_graph` compiles the real
stem page, strips one `tab:EntryCell`'s `tab:onPage`, and requires the full RDFS closure and the
production `subclass_closure` to report the **identical** violation set. With the shape as first
written they diverged by exactly one:

```
only-full=[(sh:SPARQLConstraintComponent, <…doc#htable2-e0_0>, None)]   only-sub=[]
```

`htable2-e0_0` is an **entry cell**. It becomes a `tab:LabelCell` under full closure because
`tab:hasLabel` carries `rdfs:range tab:LabelCell` (`vocab/ontology/tab.ttl:55-57`) and
`src/iladub/etkl/rowgroups.py:93` points that property at the *source entry cell* carrying a derived
group's label — which that module's own docstring states outright (`rowgroups.py:24`: *"hasLabel
points at the SOURCE EntryCell that carries the group label"*). Strip its `onPage` and the new
constraint fires on a node that is a label only by inference.

This is the hazard `membrane.subclass_closure`'s docstring already names: *"A node no longer becomes
a `tab:Cell` merely by carrying `tab:hasBBox` — that inference is the R19 accident."* The production
closure drops domain/range typing for exactly this reason; the full closure is kept as the
equivalence oracle, and the oracle caught a shape that was not closure-neutral.

**The fix, and why it is not a weakening.** Both constraints now carry
`FILTER NOT EXISTS { $this a tab:EntryCell }`. Nothing is lost, and this is provable rather than
argued: `tab:EntryCellPhysicalShape` requires `sh:minCount 1` on `tab:cellText`, `tab:onPage` **and**
`tab:hasBBox` of every entry, **unconditionally** — strictly more than this shape asks of a label.
Any node the exclusion removes from this shape's target is already under a stronger one. That claim
is pinned, not asserted:
`test_label_physical_gate.py::test_an_entrycell_used_as_a_label_is_still_refused_when_it_has_no_box`
fails the moment it stops holding.

**And the methodological point, which is the reason this section is long.** O1 — the corpus diff the
residue and the handoff both prescribed as the disposal — came back **WHOLE-FILE IDENTICAL while the
shape was still defective**. It could not see this, because `compile`'s production path uses
`subclass_closure` and the divergence only exists under the other one. A corpus run is not a
substitute for the suite, and a loop that had shipped on O1 alone would have shipped a shape whose
meaning depends on which closure you validate under.

## 5. What is NOT done

- **Option (a) is not taken and not closed.** The flank filler stays a `tab:LabelCell` and stays
  boxless. Whether it should be minted at all is an *emission* question with `reshape`'s round-trip
  oracle in its blast radius (§ 2.1) — it needs its own loop and its own corpus diff.
- **No `sh:class tab:BBox` check on the label's box.** `tab:EntryCellPhysicalShape` has one; this
  shape deliberately checks presence only, to keep the diff of § 4.1 answering one question. The
  parity gap is stated here so it is a known omission and not an oversight.
- **`tab:Cell` is not touched.** Topology-only cells — including `examples/tables/hierarchical-conformant.ttl`,
  which carries no geometry at all and is validated against the topology shapes only
  (`tests/test_tab.py:58-61`) — are unaffected, because the shape targets `tab:LabelCell`.
- **[[R178]] is not closed by this loop** and is not touched by it.
- **The corpus claim is a corpus claim.** O1 says this shape moved no reading on 7 documents /
  27 pages. It does not say no document can be moved by it; `region_tiles` remains the mechanism.
