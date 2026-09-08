# Design — the axiom binds the emitter: ruling R61's 60 DISAGREE nodes

**Residue:** [[R61]] — *"Emitter-typing is now an unenforced invariant."* Open since 2026-08-06,
blocked on one modelling decision it could never take. [[R182]] supplied the argument that takes it.

**Doc impact: increment.** Four terms enter the published CC-BY vocabulary — `tab:Column` and
`tab:PageLocated` (abstract supertypes, nothing targets either) and `tab:colX0`/`tab:colX1` — and
four axioms change meaning (`hasLabel` range, `atColumn` range, `onPage` domain,
`universeSource` domain+range). None is site-visible today because nothing is released yet, so
this queues for the next release rather than blocking anything.

---

## 1. What was blocked, and what unblocks it

R61's row has been re-measured three times and each time the count moved (14 → 14 → 32) while the
row stayed open, because closing it required a decision the row itself declined to take: *is the
ontology wrong about these properties, or is the emitter?* The row records the deadlock explicitly —
*"Either the ontology is wrong about those two properties or the emitter is — a MODELLING decision."*

[[R182]] § 2.3 settles the **direction** of that decision, and it is worth restating in one line
because everything below follows from it:

> `vocab/ontology/tab.ttl` publishes these axioms under CC-BY. Any consumer running a stock RDFS
> reasoner over our published graph — which is the entire point of publishing FAIR axioms — derives
> them. **The membrane's tolerance is not a defence, and neither is a shape's carve-out.**

So a DISAGREE node is a **false assertion in a published graph** (CLAUDE.md § Core design
principles 7), whether or not any validator we run happens to look. That makes all 60 in scope, not
only the 32 the probe calls live — *live* measures our exposure, not the claim's truth.

**The rubric, taken from R182's own remedy rather than invented here:**

- The node genuinely **IS** of the declared class → keep the property; ensure the type is explicit.
  (*"The label side keeps `tab:hasBBox`, because a `tab:LabelCell` genuinely* is *a `tab:Cell`."*)
- The node genuinely is **NOT** → **EMITTER**: move to a property properly domained on the node's
  actual class (R182's `tab:sourceRegion`/`tab:sourcePage`, following `tab:markerRegion`).
- The **class was mis-declared** — the axiom is narrower than the property's real extension →
  **AXIOM**: correct it, preferring an abstract supertype the ontology's own idiom already uses
  (`tab:Cell` is exactly this: *"Abstract supertype; a cell is either a LabelCell or an EntryCell."*).

## 2. The measurement this rules over

`PYTHONPATH=src python3 scripts/probe_domain_range_agreement.py`, 27 corpus pages, reproduced
2026-09-08 at the head of this branch:

```
total violating nodes: 74
  UNTYPED : 0        DISAGREE : 60        ONT-VISIBLE : 2        OUTSIDE-MEMBRANE : 12
  UNTYPED/DISAGREE on a class an sh:sparql shape targets: 32   <-- the live hazard
```

**UNTYPED is 0, and has been since 2026-08-18.** R61's headline — *emitter-typing is unenforced* —
describes a failure mode the corpus has never exhibited. The row already says so. This spec does not
re-open that; it rules the 60 that remain and then **wires the probe as a gate**, which is what the
headline was actually asking for and what the row says it could not have while the probe exits 1.

## 3. The seven rulings

Each row states the property, the nodes, the node's **actual** type, the site measured, and the
ruling. Every `file:line` here was read at the head of this branch.

| # | rule | n | live | actual type | site | ruling |
|---|------|---|------|-------------|------|--------|
| 1 | `hasLabel range LabelCell` | 18 | **yes** | `EntryCell` | `rowgroups.py:93` | **AXIOM** → range `tab:Cell` |
| 2 | `x0 domain BBox` | 12 | no | `GridColumn`,`MeasureColumn` | `datagrid.py:635` | **EMITTER** → `tab:colX0` |
| 3 | `x1 domain BBox` | 12 | no | `GridColumn`,`MeasureColumn` | `datagrid.py:636` | **EMITTER** → `tab:colX1` |
| 4 | `atColumn range LeafColumn` | 12 | **yes** | `GridColumn` | `datagrid.py:672` | **AXIOM** → range `tab:Column` (new supertype) |
| 5 | `onPage domain Cell` | 2 | **yes** | `DataGrid`,`UniformGrid` | `datagrid.py:624` | **AXIOM** → domain `tab:PageLocated` (new supertype) |
| 6 | `universeSource domain ColumnUniverse` | 2 | no | `DataGrid` | `datagrid.py:625` | **AXIOM** → domain/range were transposed |
| 7 | `columnFamily range CellDatatypeFamily` | 2 | no | `tab:Text` (a `CellDatatype`) | `tab.ttl:239` | **AXIOM** → missing declaration |

### 3.1 — `hasLabel` (18, live). AXIOM: widen range to `tab:Cell`.

`rowgroups.py`'s module docstring states the emission is deliberate: *"hasLabel points at the SOURCE
EntryCell that carries the key — provenance to the page (§6) with no text duplication."* The node
genuinely is an `EntryCell`, and `tab:Cell`'s own comment makes `LabelCell`/`EntryCell` an exclusive
reading, so typing it both would contradict the published prose. The **range** is the narrow thing.

**Why this widening costs nothing, measured — this is the load-bearing check.** R61's sharp warning
is that a lost typing appears as a score *improvement*. Widening a range can only cause that if some
genuine `LabelCell` depended on the range for its type. It does not: **all seven `hasLabel` emission
sites in `holon.py` (`:145,195,263,295,367,390,555`) mint a cell that is explicitly typed**
`TAB.LabelCell` — six at `:140,190,252,284,336,539`, with `:367`/`:390` going through the `_label`
helper which types at `:336`. So no node loses a type it needs, and no node gains a target set: the
18 already carry `tab:EntryCell ⊑ tab:Cell`, so they are already inside
`tab-physical-shapes.ttl:27`'s `sh:targetClass tab:Cell`.

**R179's carve-out is NOT deleted.** `tab:LabelCellPhysicalShape`'s
`FILTER NOT EXISTS { $this a tab:EntryCell }` becomes non-load-bearing under this ruling. CLAUDE.md
§ *Producer-side guards vs the membrane* permits deletion only on *provable total coverage*, which
is not established for the `rdfs_closure` consumer this loop is explicitly about. It stays, gains a
comment, and gains the test R61's row says it lacks (*"nothing pins that carve-out as load-bearing"*).

### 3.2 — `x0`/`x1` (24, not live). EMITTER: mint `tab:colX0`/`tab:colX1`.

A `tab:GridColumn` has a horizontal **interval**, not a rectangle — it has no `y0`/`y1` and could not
satisfy a box shape. It is genuinely not a `tab:BBox`, so this is R182's case exactly, and takes
R182's remedy: a property properly domained on the node's actual class.

**The move is free, measured:** `grep -rn "hasGridColumn" src tests scripts vocab` returns the
emission site (`datagrid.py:634`) and the declaration (`tab-datagrid.ttl:81`) and **nothing else** —
no reader anywhere navigates grid → column → `x0`. This also closes the emission that **R92's**
close-out independently flagged; R61's row notes *"one emitter, two residues; decide it once."*

### 3.3 — `atColumn` (12, live). AXIOM: new abstract supertype `tab:Column`.

**The obvious ruling here is wrong, and measuring is what shows it.** `tab:GridColumn`'s comment
calls it *"a transient leaf column"*, which invites `tab:GridColumn rdfs:subClassOf tab:LeafColumn`.
That would be a **defect**: `tab-shapes.ttl:15` and `:128` target `tab:LeafColumn` and require
`?tbl tab:hasLeafColumn $this`. A grid column is `tab:hasGridColumn` of a *grid*, never
`tab:hasLeafColumn` of a *table*, so the subclass edge would drag 12 nodes into two shapes they
cannot satisfy. The class comment is loose prose; the shapes are the operative definition.

So: mint `tab:Column` as the abstract supertype the ontology lacked, with
`tab:LeafColumn ⊑ tab:Column` and `tab:GridColumn ⊑ tab:Column`, and widen `atColumn`'s range to it.
Nothing targets `tab:Column`; `atColumn` keeps its name, so its twelve readers
(`feed.py:220`, `denormalization.py:167,236,254,280`, `document.py:793`, `recipe.py:82,94`, …) are
untouched.

### 3.4 — `onPage` (2, live). AXIOM: new abstract supertype `tab:PageLocated`.

A `tab:DataGrid` is genuinely measured on a page; `onPage`'s comment (*"the page the **cell** was
measured on"*) is the narrow thing. Mint `tab:PageLocated`, with `tab:Cell ⊑ tab:PageLocated` and
`tab:DataGrid ⊑ tab:PageLocated`. Nothing targets it, so it is inert for shape reach.

### 3.5 — `universeSource` (2, not live). AXIOM: the declaration is transposed.

`tab-datagrid.ttl:261` declares `rdfs:domain tab:ColumnUniverse` and **no range**. The emitter
(`datagrid.py:625`) writes `grid → tab:DecorationUniverse|tab:AlignmentUniverse`. The property means
*"which universe sourced this grid's columns"*: domain `tab:DataGrid`, range `tab:ColumnUniverse`.
An authoring slip, not a modelling question.

### 3.6 — `columnFamily` (2, not live). AXIOM: a declaration is missing.

`tab.ttl:239` declares `tab:Text a tab:CellDatatype` only, while `tab:Quantity` (`:255`) is declared
`a tab:CellDatatypeFamily` — which is why the probe reports `tab:Quantity` ONT-VISIBLE and `tab:Text`
DISAGREE on the same property. `tab-datagrid.ttl:177` already asserts the intent in prose:
*"tab:Text IS a legal family. This is the correction that made the definition universal."* Add the
declaration the prose already claims. `tab:Text` is genuinely both a datatype and its own family.

## 4. What this loop does NOT do

- **It does not touch `UNTYPED`.** It is 0 and has been for three weeks; nothing is built for it.
- **It does not delete R179's carve-out** (§ 3.1), and it does not re-litigate R179.
- **It does not rule the 12 OUTSIDE-MEMBRANE or the 2 ONT-VISIBLE nodes.** Both classes never gate,
  by the probe's own definition, and both are correct as they stand.
- **It mints no new SHACL shape.** Three new classes are added (`tab:Column`, `tab:PageLocated`) plus
  two properties (`tab:colX0`, `tab:colX1`); none is a shape target, deliberately.

## 5. The falsifying oracle

The corpus verdict diff is a **guard, not an oracle** — R182 § 2.3 is the case that proves it, having
reported *whole-file identical on 27 pages* over a live defect. The oracle for a change to published
RDFS axioms is the **closure differential**, which is the instrument that caught R182:

1. **`tests/etkl/test_closure_equiv.py`** — `membrane.rdfs_closure` (full RDFS, *the consumer's
   view*) against `membrane.subclass_closure` (*the membrane's view*). Any ruling that makes a shape
   gain or lose a focus node diverges here. **This is the falsification target and it must be run.**
2. **The probe itself** — `DISAGREE` must go **60 → 0** and the live count **32 → 0**.
3. **The corpus verdict diff** on 27 pages — expected whole-file identical; a *change* is a
   falsification, including a score **rise** (R61's own warning).
4. **The full suite** — R182's defect surfaced only in the full run, at ~60 minutes.

**Per-ruling falsification (CLAUDE.md § Plan authoring 4).** Each of the seven gets a test that
fails when its subject is inverted. The one that needs stating, because it is the one R61 asks for:
the R179 carve-out test must **fail with the carve-out deleted** — that is what pins it as
load-bearing and is the only proof the ruling in § 3.1 did not silently make a shape blind.

## 6. What closes R61

The row's headline is *"an unenforced invariant"* and its stated closure condition is a corpus-wide
probe wired as a gate. Once § 3 takes the count to 0, the probe **exits 0 and becomes a CI test** —
which is the half the row says is blocked *"on this row's own decision, not on anything separate."*

Until that gate exists, the count moves without anyone noticing: it went 14 → 32 on 2026-09-07 when
R179 shipped a shape, and **nothing recorded it, because nothing runs the probe.** That is R61's own
finding turned on itself, and it is the reason the gate is the closure condition rather than the
rulings alone.
