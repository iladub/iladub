# Naming an implicit dimension at the membrane — design

**Date:** 2026-08-09 · **Status:** **BLOCKED at adversarial review, 2026-08-09** — see §9 ·
**Specimen:** `corpus/ag-trade/cbh-stem-2026-08-03.pdf` page 0 ·
**Third attempt.** Supersedes `2026-08-09-projection-names-the-dimension-design.md` (blocked —
its selection was circular) and `2026-08-09-two-regimes-and-the-author-split-design.md`
(retired — its slice was measured unnecessary). Every correction below is a named finding from
those reviews, not a rewording.

**Doc impact:** increment — wires an existing module at a new seam. No site page contradicted.

---

## 1. What this does, stated at its real strength

A document carries a dimension it never names. cbh splits its ship roster by port and prints the
port as a section caption instead of a column, so the holon holds an **unnamed** dimension whose
values are `GERALDTON, KWINANA, ALBANY, ESPERANCE` — alongside eight berth and maintenance
notices, **identically typed**.

Every structural attempt to separate the two failed, and each failure is recorded:

| attempt | outcome |
| --- | --- |
| keys centred, notices left-aligned | **refuted** — both centre on 595.1 |
| one per panel, distinct, full-width-centred | **refuted** — `PORT MAINTENANCE SHUTDOWN AM …` occurs once in four of five blocks, all distinct, centred *tighter* than the ports |
| round-trip disposal of a wrong key choice | **refuted** — a round trip cannot dispose an assignment its own recipe records |

The distinction is not structural. It is semantic, and the semantics arrives as an argument at
the membrane: **the contract**.

**The claim, at exactly its measured strength:** where a consumer's contract declares SKOS-schemed
fields, and some are absent from the holon, the holon's captions that any of those schemes admit
form a marker set, and whole-set membership over that set names the dimension — or quarantines.
Nothing here claims the mechanism reaches a contract whose labels were written independently of
the document; see §5, which is a **limit**, not a solved problem.

## 2. The correction that makes it non-circular

The blocked version selected captions using field `F`'s own scheme, then "verified" that `F`
admitted the selection. `F` admits it by construction, and the trigger had already named `F`, so
the cascade returned its own input.

**The trigger does not name a field.** It establishes only that *some* schemed field is absent
from the holon. Selection is then **contract-wide** — captions admitted by *any* schemed field —
and whole-set membership discriminates among them:

```text
contract-WIDE selection (no field named in advance):  4 of 12 captions
    GERALDTON   KWINANA   ALBANY   ESPERANCE
whole-set membership over that set  ->  ['port'],  ambiguity = 1
commodity admits all of S?  False        <- the discrimination is GENUINE
```

`commodity` was free to admit the set and did not. `port` is a **result**, not an input.

## 3. The slice

```text
1  TRIGGER   the contract has SKOS-schemed fields absent from the holon's column header
             paths. It names none of them.
2  LOOKUP    collect the holon's tab:SectionCaption values
3  SELECT    keep those admitted by ANY schemed field   [GUARD: if the set is empty, STOP —
                                                         quarantine, never call arm 2]
4  RESOLVE   splitkey.resolve_split_key_name over the selected set
5  RECORD    the dec:DecisionHolon persists; the projected column does NOT
```

**The step-3 guard is load-bearing, not defensive.** `all()` over an empty sequence is `True`,
so `_admitting_fields([])` returns *every* schemed field — measured:

```text
_admitting_fields([])  ->  ['port', 'commodity']
```

With a single-schemed-field contract that becomes an assertion of the dimension name from **zero
evidence**, violating §3 and §7. The guard is what stops the slice manufacturing that.

## 4. Premises — measured

| # | Premise | Status |
| --- | --- | --- |
| P1 | Contract-wide selection yields the four port captions of twelve, and whole-set membership then returns exactly `port` while `commodity` does not admit the set | **MEASURED** (§2) |
| P2 | The empty selected set would assert from nothing without a guard | **MEASURED** — `_admitting_fields([]) -> ['port','commodity']` |
| P3 | The trigger fires for **two** of five fields (`port`, `commodity`), both schemed and absent; the three scheme-less fields never fire | **MEASURED** — which is why the trigger must not name a field |
| P4 | `splitkey.resolve_split_key_name` is implemented, requires a contract, has no production caller | **MEASURED** — test-only; `compile_tables` takes no contract |
| P5 | The holon carries 12 `tab:SectionCaption` values | **MEASURED** on a live compile |
| P6 | The roster panels require `section_repair_bands` to compile at all — a plain page-0 compile yields ONE table, the stock-at-port one, whose header paths are `Stock at Port (Main Storage Area)…` and `PORT MAINTENANCE SHU TDOWN DATES - 2026` | **MEASURED** — a dependency the blocked spec never named |
| P7 | The mechanism reaches a contract authored independently of the document | **NOT MEASURED, AND NOT CLAIMED** — see §5 |

## 5. The limit, stated as a limit

`ground.scheme_member` is **exact, case-sensitive string equality**:

```text
'GERALDTON' -> …#p-geraldton     'Geraldton' -> None     'geraldton' -> None
```

And the two contract fixtures in this repo label the same kind of concept in opposite
conventions, each matching its own specimen's rendering:

```text
cbh-terms.ttl    ['WA public ports', 'GERALDTON', 'KWINANA', 'ALBANY', 'ESPERANCE', 'BUNBURY']
stem-terms.ttl   ['Export ports', 'Mackay', 'Gladstone', …]
```

The control is decisive and goes against any generalisation claim: **the stem contract's port
scheme admits none of the CBH markers** (`admitting: []`).

So the reach of this mechanism is bounded by whether a contract author's labels match the
document's rendering. `cbh-contract.ttl` is a **fixture**, and its own comment says it declares
two schemed fields *"on purpose"* so the cascade can resolve CBH uniquely. **This spec therefore
claims the mechanism, not the coverage.** Whether label normalisation should be added to
`scheme_member` is a separate, independently measurable change and is out of scope.

This limit is stated because the previous version dressed a fixture measurement as evidence, and
that is the specific failure the reviews keep catching.

## 6. What this does NOT do

- **It does not close R54.** R54's live residual is `feed.table_records`' `caps[0][0]`, which is
  **per-table** and takes no contract; this slice's selection is document-wide and yields one
  name. R54 also requires a counterexample document before its scheme-membership path may be
  taken, and this spec provides none. The earlier version quoted R54 with that precondition
  deleted; the register's text is *"…once such a document exists in the corpus."*
- **It does not rejoin panels** — measured unnecessary (45/45 vessel rows already read as one
  grid).
- **It does not name a dimension without a contract.** Arm 3 quarantines; no web or memory search
  is wired, and any such suggester would propose, never assert.

## 7. Success criteria

- A projection over cbh whose contract declares `port` resolves it from the captions, asserted
  through one `dec:DecisionHolon` recording the membership evidence, **no LLM** (arm 2).
- The **same** run against a contract with no schemed field absent from the holon never looks and
  never names.
- An empty selected set quarantines with a reason and **never** reaches arm 2 — proven by a red
  test that fails if the guard is removed.
- Nothing is written into the holon graph, checked by `rdflib.compare.to_isomorphic` (not byte
  equality — `_emit_*` mints BNodes, so Turtle is not byte-stable).
- Corpus unchanged; stem's document compile stays `0.9654553611484971`.

## 8. Global constraints (carried, per CLAUDE.md)

- **§8 gate.** Steps 3–4 are AXIOM (scheme membership over the contract's SKOS graph). **The
  trigger is AXIOM too, not glue** — "is field F among the holon's header paths" is a
  label-matching judgement over RDF, and the blocked version misclassified it as procedural.
- **§3 epistemics.** Arm 2 asserts only what the contract grounds; everything else quarantines,
  and confidence never promotes.
- **§1 knowledge-first.** The contract is the knowledge module *passed as an argument* — which is
  why the naming is decidable here and nowhere else.
- **No overfitting.** §5 is the honest statement of where the fixture ends and the world begins.
- **Source ownership.** `tab:`/`dec:`/`iladub:` are ours.

---

## 9. Adversarial review — BLOCKED (2026-08-09), and the structural diagnosis

The review credited four prior blockers as genuinely fixed (the empty-set guard, the R54
misquote, the R54-residual disclaimer, and byte-identity → `to_isomorphic`). Two blockers stand,
both re-verified by the controller.

### 9.1 BLOCKING — the tautology was relocated, not removed

`_admitting_fields(S) = {i : A_i ⊇ S}`, and `S = ⋃ A_i` puts every `A_i ⊆ S`, so it reduces to
`{i : A_i = S}`. Verified:

```text
A[port]      = ['GERALDTON','KWINANA','ALBANY','ESPERANCE']
A[commodity] = []
S = union    = ['ALBANY','ESPERANCE','GERALDTON','KWINANA']
S == A[port] exactly: True    -> port admits S BY CONSTRUCTION
```

§2 says `commodity` *"was free to admit the set and did not."* It was not free: a field admitting
nothing contributes nothing to the union, which is precisely what makes the survivor's admission
an identity. With N schemed fields there is **no confirming direction** — a new field either
leaves the answer unchanged (`A_new ⊊ S`), forces ambiguity 2 (`A_new = S`, where the *proposer's
ranking* decides the name), or forces ambiguity 0 (`A_new ⊄ S`, quarantine).

The mechanism's true strength is weaker and should be stated as such: **exactly one schemed field
admits any caption at all, so the contract disambiguates by exclusion.**

### 9.2 BLOCKING — and my fix for 9.1 opened a silent misname

With the port labels title-cased (so `port` matches nothing) and a rival schemed field matching
the notice captions:

```text
port admits: []
contract-WIDE selection S = ['BERTH MAY BE UNAVAILABLE…', 'PORT MAINTENANCE SHUTDOWN…']
whole-set admitting = ['advisory']   ambiguity = 1   -> asserted, NO LLM
```

The document's real dimension is *port*; the mechanism names it **`advisory`**, confidently, via
arm 2. §3/§7 violation. Under the *previous* field-scoped selection a mismatched `port` selected
nothing and the run ended — **contract-wide selection is what created this path.** §5 therefore
states the wrong failure mode: it is quarantine when *nothing* matches, and a confident wrong
name when something *else* does.

### 9.3 The structural diagnosis — one pattern, four attempts

Every attempt on this problem has failed the same way: **proposal and disposal came from the same
source.**

| attempt | proposer | disposer | why it failed |
| --- | --- | --- | --- |
| author-split | structure | the round trip | a round trip cannot dispose what its own recipe records |
| projection v1 | field F's scheme | field F's scheme | circular by construction |
| naming v2 (this) | the union of all schemes | the same union | identity, per §9.1 |

Nothing could be *wrong in a detectable way*, which is why each version passed its own test and
died at review.

### 9.4 The independent disposal, measured

A dimension's values must address the row groups **one-to-one**. That constraint comes from the
structure, not from the contract, so it can refute a name the contract proposed:

```text
row groups (one per reprinted header): 4

RESOLVED PORT SET    group 0<-GERALDTON  1<-KWINANA  2<-ALBANY  3<-ESPERANCE
                     4 values over 4 groups   -> BIJECTIVE      admit

RESOLVED NOTICE SET  group 0<-4 notices  1<-1  2<-2  3<-1
                     8 values over 4 groups   -> NOT bijective  refuse
```

It refutes §9.2's misname directly, and it is the first disposal in this line of work that is
independent of whatever proposed the answer. The association is caption-precedes-its-header — the
off-by-one an earlier review found, now used rather than tripped over.

**The next attempt must pair a contract proposal with this structural disposal.** Not a reworded
§2 — a different shape: the contract proposes, the structure disposes, and the two do not share a
source.
