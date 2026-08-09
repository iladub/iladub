# The projection names the dimension — design

**Date:** 2026-08-09 · **Status:** **BLOCKED at adversarial review, 2026-08-09** — see §7 ·
**Specimen:** `corpus/ag-trade/cbh-stem-2026-08-03.pdf` page 0 with
`examples/shipping/cbh-{contract,terms,shapes}.ttl` ·
**Supersedes:** `2026-08-09-two-regimes-and-the-author-split-design.md` (retired — its §0
architecture survives here; its §2 slice was measured unnecessary)

**Doc impact:** increment — wires an existing module at a new seam; no new owned terms expected
beyond the trigger's record. No site page contradicted.

---

## 1. The finding this rests on

cbh page 0's holon carries **twelve** section captions — four port names and eight berth or
maintenance notices — **identically typed**. Every structural attempt to separate them failed,
and each failure is recorded:

| attempt | outcome |
| --- | --- |
| keys are centred, notices are left-aligned | **refuted** — both centre on 595.1 |
| one per panel, distinct, full-width-centred | **refuted** — `PORT MAINTENANCE SHUTDOWN AM …` occurs once in four of five blocks, all four distinct, centred *tighter* than the ports |
| round-trip disposal of a wrong key choice | **refuted** — a round trip cannot dispose an assignment its own recipe records |

They failed because **the distinction is not structural.** It is semantic, and the semantics
lives in the contract:

```text
contract fields: ['client', 'commodity', 'id', 'port', 'volume']

field 'port' admits 4 of the holon's 12 captions:
    GERALDTON   KWINANA   ALBANY   ESPERANCE
```

**The contract selects the markers.** We never decide which caption is the key — we ask the
`port` scheme which captions it admits, and it returns exactly the four, rejecting all eight
notices. No positional rule, no `caps[0][0]`, no world knowledge on our side.

This is the closing path the residue register itself proposed for R54: *"promoting marker
selection from 'positionally-first caption' to 'the caption(s) that pass scheme-membership
filtering'."* It now has its measurement.

## 2. The slice

A projection requires a field the holon's data schema lacks. Look in the holon's metadata, let
the contract select the markers, resolve the name through the shipped cascade, record the
decision. Nothing is written into the holon.

```text
1  TRIGGER   contract field F is required by the projection and is not an attribute of
             the holon's data grid
2  LOOKUP    collect the holon's section captions (tab:SectionCaption)
3  SELECT    keep those F's scheme admits — the contract does the selecting
4  RESOLVE   splitkey.resolve_split_key_name over the selected set
5  RECORD    the dec:DecisionHolon persists; the projected column does NOT
```

Step 5 is decision 0.1(3) of the retired spec, which survives: the view is derived, only the
decisions are stored.

**Two outcomes, no third.** `KeyNameResolution.outcome` is `"asserted"` or `"quarantined"` —
the module's own docstring says *"there is no third epistemic state."* Either F resolves from
the metadata and the projection can supply it, or it does not and the projection reports F
unresolvable with the reason.

## 3. Premises — measured

```text
field 'port' admits exactly 4 of 12 captions      GERALDTON KWINANA ALBANY ESPERANCE
whole-set membership, PORT NAMES                  admitting fields: 1  ['port']  -> assert, no LLM
whole-set membership, MAINTENANCE NOTICES         admitting fields: 0            -> quarantine
whole-set membership, MIXED (3 ports + 1 notice)  admitting fields: 0            -> quarantine
whole-set membership, PORTS + a stray             admitting fields: 0            -> quarantine
```

| # | Premise | Status |
| --- | --- | --- |
| P1 | The contract's `port` scheme admits exactly the four port captions of twelve | **MEASURED** |
| P2 | Whole-set membership over the selected set yields exactly one admitting field | **MEASURED** — arm 2 asserts, no LLM |
| P3 | Pollution quarantines rather than misnames | **MEASURED** — every mixed set admits zero |
| P4 | `splitkey.resolve_split_key_name` is implemented, requires a contract, and has no production caller | **MEASURED** — test-only; `compile_tables` takes no contract |
| P5 | The holon carries the captions to look up | **MEASURED** — 12 `tab:SectionCaption` on a live cbh compile |
| P6 | A real consumer's contract would carry a scheme that cleanly admits four port names | **NOT MEASURED — the weak one.** `cbh-contract.ttl` is a demo contract authored in this repo, for this document. A scheme built to fit the specimen proves the mechanism, not the world |

**P6 is the one to attack.** Everything else is measured; this is the premise that decides
whether the mechanism generalises or merely closes on its own fixture.

## 4. Success criteria

- A projection over cbh requiring `port` resolves it from the metadata, asserted through one
  `dec:DecisionHolon` recording the membership evidence, with **no LLM** (arm 2).
- The same projection over a contract *without* a `port` field never looks, never names, and the
  holon is byte-identical between the two runs.
- A holon whose captions the scheme cannot admit yields `quarantined` with the reason, not a
  guessed name.
- **Nothing is written into the holon graph** by the projection — proven by comparing the holon
  before and after.
- R54's live residual (`feed.table_records`' `caps[0][0]`) is either replaced by scheme-selection
  or explicitly left, with the choice stated.
- Corpus unchanged; stem's document compile stays `0.9654553611484971`.

## 5. Out of scope

- **Rejoining panels.** Measured unnecessary: cbh's four panels already read as one grid
  (45/45 vessel rows, one decoration universe).
- **Naming a dimension with no contract.** Arm 3's BAML proposal exists and quarantines; wiring
  a web or memory search is not this slice and would propose, never assert.
- **R74** (the table-B leak) and **R75** (measure-only aggregate rows) — registered, separate.

## 6. Global constraints (carried, per CLAUDE.md)

- **§8 gate.** Steps 3–4 are AXIOM (scheme membership over the contract's SKOS graph); the
  trigger and lookup are PROCEDURAL glue over existing data.
- **§3 epistemics.** Arm 2 asserts only what the contract grounds; anything else quarantines,
  and confidence never promotes.
- **§1 knowledge-first.** The contract is the knowledge module *passed as an argument* — which
  is precisely why the naming is decidable here and nowhere else.
- **Source ownership.** `tab:`/`dec:`/`iladub:` are ours; `hproj:` only as an alignment object.

---

## 7. Adversarial review — BLOCKED (2026-08-09)

Four blockers. All re-verified by the controller.

### 7.1 BLOCKING — the selection makes the resolution tautological

§1's *"the contract selects the markers"* is true as a sentence and does not earn the
verification it appears to. `_admitting_fields(S, …)` is `all(scheme_member(m, F.scheme) for m
in S)`. If `S := {c : F admits c}` then **F admits S by construction** — S was built from that
exact predicate:

```text
select with F=port -> S = [GERALDTON, KWINANA, ALBANY, ESPERANCE]
whole-set admitting over S -> ['port']
```

And step 1 has already *named* F, since the trigger is "contract field F is required." So the
cascade returns its own input, and `ambiguity_score = 1` restates the question rather than
answering it. On cbh there are only two schemed fields, so the entire discriminating power is
one bit against one alternative.

The honest description of the slice is weaker than §1's: *the projection names the dimension and
the contract confirms no other schemed field collides.*

### 7.2 BLOCKING — the empty selected set asserts from nothing

`all()` over an empty sequence is `True`, and the SELECT step is what first makes an empty
marker set reachable in ordinary operation:

```text
_admitting_fields([]) -> ['port', 'commodity']
```

With a single-schemed-field contract that becomes an **assertion of the dimension name from zero
evidence** — a full `PromotionDecision` + `GroundedNode`, arm `unique-admitting-field`. That is a
§3 and §7 violation manufactured by this slice's own new step, and §4's third success criterion
("a holon whose captions the scheme cannot admit yields quarantined") is refuted by it.

It is not an edge case: `tab:SectionCaption` exists on **one of three** ag-trade documents (cbh
12, stem 0, capacity 0), so the empty path is the majority case.

### 7.3 BLOCKING — P1 measures the fixture's label casing, not a capability

`ground.scheme_member` is **exact, case-sensitive string equality**:

```text
'GERALDTON' -> …#p-geraldton     'Geraldton' -> None     'geraldton' -> None
```

And the two sibling term files in the same directory label the same kind of concept in opposite
conventions, each matching its own specimen's rendering:

```text
cbh-terms.ttl    ['WA public ports', 'GERALDTON', 'KWINANA', 'ALBANY', 'ESPERANCE', 'BUNBURY', …]
stem-terms.ttl   ['Export ports', 'Mackay', …]
```

The cross-contract control is decisive: the **stem contract's port scheme admits none of the CBH
markers** (`admitting: []`). So "port admits 4 of 12" holds because the fixture author typed the
labels in ALL CAPS after seeing the page. Under the repo's own sibling convention it is 0 of 12.
**P1 is not independent of P6; it collapses into it.** `cbh-contract.ttl`'s own comment says it
declares two schemed fields *"on purpose"* so the cascade can resolve CBH's markers uniquely —
the fixture is documented as built to make this succeed.

### 7.4 BLOCKING — R54 was misquoted, and the deleted clause is the one that forbids this

R54's actual text: *"a counterexample document … **OR** promoting marker selection from
'positionally-first caption' to 'the caption(s) that pass scheme-membership filtering' **once
such a document exists in the corpus**."* §1 quoted the second disjunct and **deleted its
precondition**. R54's why-deferred is explicit: *"no measured document does this … so fixing
blind remains the overfitting risk CLAUDE.md's 'No overfitting' rule forbids."*

This spec provides no counterexample document and proposes precisely the blind fix the register
names as forbidden — while quoting the register in a way that made it look sanctioned. That is
the most serious finding here, and it is a process failure, not a technical one.

### 7.5 Also — the slice cannot reach R54's live residual

`caps[0][0]` lives in `feed.table_records(graph)`, which takes **no contract**, and the defect is
**per-table**. This slice's selection is document-wide and yields one name. Naming the dimension
`port` cannot stop `caps[0][0]` returning a notice on a document that draws its notice first, so
§4's criterion 5 resolves to "explicitly left" and §1's "closing path" framing is unearned.

### 7.6 The trigger has no premise and no §8 classification

§3 lists no premise for step 1, and §6 calls it "PROCEDURAL glue." Measured on the fixture,
`id` also fires the trigger and declares **no scheme**, so SELECT returns `[]` and it falls
straight into §7.2. And `'Other Port/s'` *is* a grid column, so "is F an attribute of the data
grid" is a label-matching judgement — AXIOM-shaped, not glue.

**What survives:** P4 (splitkey is test-only, contract-requiring; `compile_tables` takes none),
P5 (12 captions on a live compile), the exactness of the per-caption selection (no substring
matching — 4 of 12, no other field admits any caption), and §5's scope exclusions.

### 7.7 The pattern, recorded

This is the fourth spec blocked at this gate in three days, and the second today. The common
shape: a mechanism that works on the specimen, presented as measured, where the measurement is
of a fixture built from that specimen. The gate is doing its job — but the cost is now visible,
and the corpus's demo contracts should be treated as **fixtures, not evidence**, wherever a
premise depends on their content rather than their structure.
