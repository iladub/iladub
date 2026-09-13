# Evidence — the span the author drew: what was measured before the plan

**Serves:** prog:criterion:etkl:02 — the measurements the Layer A / Layer B plan rests on.

**Doc impact: none.** Measurements only; no term, no behaviour, no released assertion.

Every figure below was **run** on 2026-09-13 against `main` at `4e5ef50`, on branch
`span-donation-plan`. Where a probe was run by a measuring subagent of this session, its output is
reproduced verbatim and the reproduction recipe is given. Nothing here is reasoned from reading.

---

## 1. The relation refuses graincorp on ONE clause, and that clause is `?n`

`vocab/queries/grid-donation.rq:45-52` carries four clauses; the equal-column-count join is line 48
(`tab:leafColumnCount ?n`), with `?n` bound at call time to the **recipient's** `region.grid.ncols`
(`donation.py:76-83`, `:225`). Uniqueness is not in the query at all — it is Python, at
`donation.py:226`.

```
band3 kind: RECORD_TABLE grid.ncols: 16
donors_for(ev, 3, ncols=16) -> ()
donors_for(ev, 3, ncols=9)  -> (2,)
offer(...) -> None
```

Band 2 satisfies **earlier-than**, **wholly drawn** and **the R203 licence**. Only `?n` differs. The
identifier `same_ncols` appears nowhere in `src/` — `grep -rn "same_ncols" src/ scripts/` returns one
hit, in an instrument (`scripts/grid_agreement_census.py:108`).

## 2. The two shipped covering oracles CANNOT produce the reading — measured, not argued

A one-row donor makes `leaf_lvl = len(header_rows) - 1 = 0` (`headers.py:445`), so **every** node
takes the SPARQL leaf covering at `:453` and the spanning path `_covers_for_cell` (`:455`) is never
reached. `_tree_from_rows(donor_rows, recipient_grid)` is a **legal call** and returns a well-formed
tree — it simply covers one column per label:

```
A: shipped-builder tree | covered cols: [0, 1, 2, 4, 6, 8, 10, 12, 14] | uncovered: [3, 5, 7, 9, 11, 13, 15]
A: assert_hier_region -> 406 | triples: 5500 | region_tiles -> False

B: _covers_for_cell variant | covers: [(0,), (1,), (2,), (4,), (5, 6, 7), (8,), (10,), (12,), (14,)]
B: covered cols: [0, 1, 2, 4, 5, 6, 7, 8, 10, 12, 14] | uncovered: [3, 9, 11, 13, 15]
B: assert_hier_region -> 406 | triples: 5502 | region_tiles -> False
```

Both refusals are `tab:CoverageShape` and nothing else, verbatim from the same
`membrane.validate(g, tiling._TILING_SHAPES, tiling._ONT)` call `region_tiles` makes:

```
_:2 sh:sourceShape <https://w3id.org/iladub/tab#CoverageShape> ;
	sh:sourceConstraintComponent sh:SPARQLConstraintComponent ;
	sh:focusNode <urn:x#t-c9> ;
	sh:resultMessage "Leaf column is not covered by any header node of its table (coverage gap)." ;
	sh:resultSeverity sh:Violation ;
	a sh:ValidationResult .
```

**This refutes the spec's § 3.1 reuse assumption.** Both shipped oracles are *ink-overlap*
derivations; the reading the spec describes is an *interval* derivation over the boundaries the
author drew. Adding a coarser-donor clause to `grid-donation.rq` would not have produced it, because
donation asserts through `assert_record_region`, whose header emission is flat by construction —
one node per column, `tab:coversColumn` emitted once (`holon.py:112-120`).

## 3. Variant C — the drawn-interval covering, and it passes

The rule as computed (`_rule_boundaries`, `grid.py:40`; `recover_leaf_grid`, `cells.py:38`):

```python
d = [round(x, 2) for x in _rule_boundaries(d_band)]     # donor vector, 10 xs
b = [round(x, 2) for x in grid3.boundaries]             # recipient grid, 17 xs
EPS = 0.01
covers_of_interval = [tuple(j for j in range(len(b) - 1)
                            if d[i] - EPS <= b[j] and b[j+1] <= d[i+1] + EPS)
                      for i in range(len(d) - 1)]
```

```
interval 0 [   42.36,   108.72] -> cols (0,)
interval 1 [  108.72,   210.24] -> cols (1,)
interval 2 [  210.24,   296.88] -> cols (2, 3)
interval 3 [  296.88,   383.52] -> cols (4, 5)
interval 4 [  383.52,   470.16] -> cols (6, 7)
interval 5 [  470.16,   556.80] -> cols (8, 9)
interval 6 [  556.80,   643.44] -> cols (10, 11)
interval 7 [  643.44,   730.08] -> cols (12, 13)
interval 8 [  730.08,   816.36] -> cols (14, 15)
partition sizes: [1, 1, 2, 2, 2, 2, 2, 2, 2]
all cols covered: True | dupes: [] | missing: []
eps=0.01 vs eps=0.0 identical: True
```

**The tolerance is INERT.** `eps=0.01` and `eps=0.0` give identical maps, because every donor x
appears verbatim in the recipient vector at 2dp — the single rounding site is
`sectiongraph._distinct_rule_xs` (`:188`), applied to the boundary vector at `:306`. A tolerance that
decides nothing is the only kind §8 permits here, and the plan pins it as inert rather than tuning it.

The tree, the gate and the region membrane:

```
node2 level=0 covers=(2, 3) parent=None text='Mackay' bbox=(239.16,94.55,268.26,102.47) page=0
node4 level=0 covers=(6, 7) parent=None text='Fisherman Islands' bbox=(392.37,94.55,460.23,102.47) page=0
   ... 9 nodes, all level=0, all parent=None
region_round_trips(reg, recipient) -> True
assert_hier_region -> 406 | triples: 5507
region_tiles -> True
```

## 4. The full page membrane accepts donor-sourced label geometry

Built with the repo's own builder, `compile._build_membrane()` (`compile.py:588`), validated with the
same call `compile._validate` makes (`compile.py:668-675`):

```
TAB shape files: ('tab-shapes.ttl', 'tab-physical-shapes.ttl') | DEC: ('dec-shapes.ttl', 'iladub-shapes.ttl', 'escalation-shapes.ttl')
== LEG tab: conforms = True
== LEG dec: conforms = True
```

So no shape refuses a hierarchical region whose **label bboxes come from the donor band** (tops
94.55–102.95, above every recipient row) while its entry cells come from the recipient.

**Scope limit, stated rather than glossed:** this validates the region graph alone (5507 triples,
`urn:x#t`), not a whole compiled document with captions, unit markers, decision holons and adjacent
bands. Whether a full document compile routing a spanning donation through this path conforms
end-to-end is **UNVERIFIED** — no code path constructs it, so there is nothing to compile. That is
the executing loop's Task 3 measurement, not a claim made here.

## 5. `region_round_trips` never sees the donor, and is largely vacuous here

`roundtrip.py:34-80`. `region.body_line` is read at `:52` and nowhere else; with `body_line = 0` the
slice `band.lines[:0]` is empty, so `header_tops` is empty and `header_hits` (`:69`) is always 0. The
gate degenerates to *"every recipient word sits in exactly one `region.rows` band"*.

```
region_round_trips(reg, recipient_band) -> True
region_round_trips(reg, donor_band)     -> False
```

**No check compares tree labels against words in `band.lines`** — `region.tree` is never
dereferenced. And `assert_hier_region` references `band` exactly **once**, at `holon.py:542`, the call
to this gate; after it, the band is untouched. So a tree sourced from a different band than `band` is
cross-checked nowhere.

## 6. The ink ledger does not move

`assert_hier_region` returns **406**, exactly the figure `tests/etkl/test_run_merge_seam.py:163` pins
for `("graincorp-capacity-2026-08-04", 0)`. Under the existing record path the donor's words are
never iterated — `_book_recovered_ink` (`compile.py:276`, called at `:1041-1043`) iterates the
**recipient's** `band.lines` and uses row-0 cell bboxes only as containment boxes.

"The donor band is ignored" is **document-dependent**, and the plan must not generalise it:

```
graincorp p0: band 2  NON_TABLE ignored  tok_a=0 tok_e=0  reason "fewer than 2 lines"  (9 words)
bfs p6:       band 2  RECORD_TABLE asserted  tok_a=15  (the shipped donation's donor)
```

## 7. Label-to-interval assignment — two rules, agreeing on one donor only

```
2a. INK-CENTER: 'Year' cx=76.04 -> 0 | 'Elevation Period' 159.76 -> 1 | 'Mackay' 253.71 -> 2
    'Gladstone' 340.08 -> 3 | 'Fisherman Islands' 426.30 -> 4 | 'Carrington' 512.73 -> 5
    'Port Kembla' 599.09 -> 6 | 'Geelong' 685.57 -> 7 | 'Portland' 772.30 -> 8
2b. ORDINAL: {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8}
AGREE ON ALL 9: True | disagreements: []
```

**This is one donor, 9 labels, one page.** Agreement here is not evidence that the two rules agree
generally, and the plan treats the choice as a decision with a named falsifier, not as a settled fact.

## 8. What Layer B will find, and what it must not disturb

- The shape Layer B looks for is exactly what variant C produces: **7 nodes with `covers` > 1 and
  ZERO `tab:parentHeader` triples** (all nine promoted to level 0 by `holon.py:570`'s orphan rule).
- **No code in `src/` computes "has no child header node."** `feed._header_path` (`:489-538`) reads
  every fact the condition needs but stores only the forward pointer (`parent[h]`, `:521`) and
  computes the deepest-covering node per column (`:524-529`).
- One row ⇒ one record is hard-coded at five sites: `feed.py:445-448`, `:449-450`, `:457-463`,
  `:474-475`, and `ground_document` `:631-636`. The per-record cell list at `:459` is flat and
  **drops the column**, which is the fact a split needs.
- The precedent seam exists: `_inject_group_keys` (`:235`) and `_inject_section_captions` (`:341`)
  already append concepts into `rows[row]` between `_read_table` and the record-id computation, at
  `:412-413`.
- The coverage predicate is `tab:coversColumn` (`tab.ttl:58`). **`tab:covers` (`tab.ttl:400`) is a
  decoy** — domain `tab:HeaderCell`, range `tab:GridColumn`, both transient and "never asserted into
  a holon".
- `src/iladub/splitkey.py` does **not** split records — it resolves a dimension's *name*, and
  `resolve_split_key_name` has **zero production call sites**.

## 9. The oracle Layer B must reuse, and the pin that constrains how

`marker_field` (`ground.py:96-117`) is gated by one line, `:113` (`if not concept.is_section_marker:
return None`), and admits on **unique** scheme membership (`:115-116`, `len(admitting) == 1`); zero
and several are indistinguishable to the caller.

`is_section_marker` is set at exactly **one** production site (`feed.py:368`, scoped to
`tab:SectionCaption` at `:329`) and read at exactly **one** (`ground.py:113`), plus one script and 10
test-assertion sites. Its declaring comment claims both facts, and the enumeration confirms them.

**The constraining pin:** `tests/test_corpus_stem.py:263` asserts that **no** record may carry a
furniture-sourced `is_section_marker` concept. So widening the flag's *meaning* fights an existing
negative pin, while routing a new population to the *same* oracle does not.

## 10. The proposer is asked a question with a blank subject

`ProposeGrounding(surface_text, value, field_labels)` (`ground_propose.baml:8`), called at
`propose_ground.py:51` with `concept.text`, `concept.value` and field local names. For an unlabelled
leaf, `header.get(col, "")` (`feed.py:227`) is empty, so the prompt at `ground_propose.baml:11`
renders *"A document field reads  = 845870."*

**The repo has declared page-level context slots twice and left both dead:**

| function | slot | production value |
| --- | --- | --- |
| `ProposeDimensionName` (`reshape_propose.baml:7`) | `table_title: string?` | hard-coded `None`, `reshape.py:207` |
| `ProposeSplitKeyName` (`split_key_name.baml:8`) | `context: string` | never passed; `resolve_split_key_name` has no production caller |

That is both the precedent and the caution: a declared slot nobody fills is how the last two attempts
died.

`baml_client` is **gitignored** (`.gitignore:29-30`) and regenerated in CI on every PR
(`.github/workflows/ci.yml:23-24`, before `pytest`), so a signature change cannot ship stale — the
risk is local only. A drift pin exists for exactly one function, `ProposeHeaderRowRoles`
(`tests/etkl/test_rowrole_proposer.py:37-89`); **there is none for `ProposeGrounding`.**

## 11. The seam's cost, measured both ways

| route | sites touched |
| --- | --- |
| a defaulted parameter on `ground_concept` | **2** production call sites (`federate.py:50`, `feed.py:636`); 24 test call sites keep working |
| a fifth field on `SurfaceConcept` | 5 `src/` + 35 `tests/` construction sites, and `__eq__`/`__hash__` change at 3 comparing sites (`test_federation.py:69-70`, `:83`) |

`SurfaceConcept` is frozen and only `is_section_marker` is defaulted (`ground.py:48`).

## 12. The contract can carry its licence pointer for free

`load_contract` (`ground.py:68-77`) is a pure forward traversal from the first subject carrying
`etkl:targetClass`; it enumerates no predicates and validates nothing. **Measured** — the shipped stem
contract, then the same file plus 7 extra triples (`prov:wasDerivedFrom`, `dcterms:license`, an
invented `etkl:derivedFromBandText`, a typed `etkl:IgnoredBand` node):

```
IDENTICAL to baseline: True
```

Two adjacent facts: **no test validates a contract file against a shape**, and
`grep -rn "sh:closed" vocab/shapes/ tests/*.ttl` returns **nothing**.

**Where such a pointer may point, by declared range:** `dec:consideredEvidence` is
`rdfs:subPropertyOf prov:used` with range `prov:Entity` (`dec.ttl:54-56`). `etkl:IgnoredBand` is a
bare `owl:Class` with **no `rdfs:subClassOf`** (`etkl.ttl:190`) — it is *not* a `prov:Entity`. Its
source region is (`iladub:SourceRegion ⊑ prov:Entity`, `iladub.ttl:70-72`), and the carrier mints it
at `{doc}#ignored{idx}-source` (`holon.py:511, :520`). So the evidence link targets the **region
node**, not the band node.

## 13. What is pinned on graincorp-capacity today

| pin | what it says |
| --- | --- |
| `tests/corpus-manifest.ttl:46-73` | `cor:Unadjudicated`, **no `cor:scoreFloor`**, no `cor:contract`/`terms`/`shapes` |
| `tests/test_corpus.py::test_expected_verdict` | for `Unadjudicated`, *compile returning at all* is the whole gate — no score assertion |
| `tests/test_corpus.py::test_grounding_where_contracted` | parametrizes `[e for e in ENTRIES if e["contract"]]` — **2 of 7**; graincorp is not skipped, it is never parametrized. Ends `assert grounded, "a contracted document must ground SOMETHING"` |
| `tests/etkl/test_run_merge_seam.py:163` | `("graincorp-capacity-2026-08-04", 0): 406` |
| `tests/etkl/test_vacuity_registry.py:67` | graincorp is in the registry's corpus; a shape idle and unregistered fails, **and a registered shape that has gone live fails too** |
| `tests/arc-manifest.ttl:210-219` | `etkl:02`, `prog:blockedBy "R166"` at `:215`, `prog:met false` |

## 14. Reproduction

The probes in §§ 1–7 were run in-session against `corpus/ag-trade/graincorp-capacity-2026-08-04.pdf`
page 0 (donor = band 2, recipient = band 3) using `page_bands`, `recover_leaf_grid`,
`_rule_boundaries`, `logical_rows`, `assert_hier_region`, `region_tiles` and
`compile._build_membrane`. `corpus/` is gitignored, so a fresh worktree must symlink it first or
every one of these skips green.
