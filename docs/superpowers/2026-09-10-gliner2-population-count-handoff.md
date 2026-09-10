# Handoff — GLiNER2: count the population before pricing the model

**Topic:** the GLiNER2 spec on branch `only-a-refusal-admits-the-model` (unmerged, unpushed —
`docs/superpowers/specs/2026-09-10-only-a-refusal-admits-the-model-design.md` on that branch, read
it with `git show`, never `git checkout` in the main tree). Its probes live at
`/Volumes/WD Green/dev/git/iladub-gliner2-probes` (`4164a3f`).
**Written 2026-09-10 at 157K working tokens — 3.1× the originating floor**, so every action in
part 5 is graded, per CLAUDE.md § "The handoff's next action is TYPED". Parts 1-4 are pointers.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — measure the population placement A would touch, on the MANIFEST corpus, before running T1

The spec's first gate is T1 — *GLiNER2 is ≥10× cheaper than BAML per cell*. Cheap × zero is zero,
and nothing has counted the cells. The measurement is mechanical and already half-built:

1. **The corpus grounding leg runs with an ABSTAINING proposer.** `scripts/reach_probe.py:121-126`
   and `tests/test_corpus_stem.py:51-54` both hand `ground_document` a `FakeGroundingProposer`
   whose proposal has `field_iri=None`. So every cell `exact_field` refuses ends `proposed`, and
   **`FeedResult.proposed` per document is the raw population** placement A would be offered.
2. **Filter it to oracle-bearing fields** — a field with an `admissibleScheme` or a SHACL value
   constraint (`src/iladub/ground.py:107-115`, `_grounds_to`'s docstring). Spec § 3.1 says A
   abstains without loading the model when this set is empty, so the count that matters is the
   refused cells whose *column* binds to such a field, not the raw figure.
3. Report per document: `proposed`, `proposed on oracle-bearing fields`, and the number of distinct
   surface strings among them (a model classifies strings; ten identical cells are one call).

**Why asserted:** the instrument exists (`reach_probe.py --doc <cor:file>` runs exactly this leg),
the abstaining proposer is the shipped test fixture, and the outcome is a number on disk. Nothing
about GLiNER2 needs to be installed or loaded.

**The bound is already known and it is small.** `tests/corpus-manifest.ttl` gives a `cor:contract`
to **2 of 7** documents — `ag-trade/graincorp-stem-2026-07-31.pdf` (`:25-35`) and
`ag-trade/cbh-stem-2026-08-03.pdf` (`:60-69`). The other five (graincorp-capacity, ons, bfs, apple,
who) carry none, their grounding leg is never exercised
(`tests/test_corpus.py::test_grounding_where_contracted` does not parametrize them — the manifest
says so at `:57`), and **placement A has no population on them at all**. Whatever the count is, it is
a count over two one-page shipping stems.

### 5b. PROPOSED — the count is in the dozens, and the GLiNER2 thread closes on it

Prediction: across the two contracted documents, refused cells on oracle-bearing fields number
**under 100, and under 30 distinct strings**. If so, BAML's per-call cost is irrelevant at this
volume, a cheaper tier in front of it buys nothing, and the right disposal is a register row
recording the count and **no dependency**. The spec's T1-T8 are then never run, and § 6.6's
"refuted" ending is reached without loading a model.

**Why proposed:** the number has not been taken. Two ways it fails: (i) the stems' body columns
(grade, port, vessel) are scheme-bound and refuse at volume — then the population is real and T1/T3
are worth a spike on placement **A only**; (ii) `_grounds_to` admits more by exact match than
expected and the refused set is smaller still. Either way the number, not the prediction, decides.

### 5c. PROPOSED — B and C should not survive the count whatever it says

Recorded here so the spec review does not re-derive it. **B (cell splitting):** the fused cells this
repo has measured are fused for a *geometric* reason — bfs p6 bands 3/7, one cell spanning
`72.6 → 424.1` because the band's own rule grid cut at 3 columns ([[R205]]). The page says where the
split is, in drawn rules; a text model re-deriving it from the string is CLAUDE.md § 0's neolegacy
pattern. B is defensible only on *textual* fusion (`ETA/ETC 12/03`), which needs its own population
count and has none. **C (record extraction over escalations):** every escalation studied in
[[R160]]–[[R205]] is structural with an author-drawn answer being closed by AXIOMs, and no live
promotion path consumes what C would emit. **Why proposed:** both rest on this corpus; a document
whose fusion is textual, or whose escalations are not structural, reopens them.

**Also to carry into the review, either way:** τ (spec § 2.2) is a tuned constant admitted into the
NEURAL tier's *routing*; the routing-not-truth defence holds but wants a register row, not a
footnote. The code pin is a fork (`adsharma/GLiNER2@f26b0ae`) while the model is upstream
(`fastino/gliner2.5-base-v1`), and the architecture doc the record-mode tutorial cites is absent at
that SHA (spec § 4.2).

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the spec under review | branch `only-a-refusal-admits-the-model`, `docs/superpowers/specs/2026-09-10-only-a-refusal-admits-the-model-design.md` | § 1 the placement rule; § 2.2 how abstention is manufactured (τ + sentinel); § 6 the eight targets and their order; § 6.6 that the spec may refute itself |
| the probes | `/Volumes/WD Green/dev/git/iladub-gliner2-probes/probes/*.py` + `HANDOFF.md` | they establish ONE thing — spatial ASCII and line text tokenise identically (`probe_tokens`) — and **no probe ever loaded the model** |
| the population instrument | `scripts/reach_probe.py:100-140` | the grounding leg with the abstaining proposer; `--doc` runs one document |
| the corpus's contract coverage | `tests/corpus-manifest.ttl:25-35, :60-69` | the two contracted entries; `:57` and `:90` record why the others have none |
| the oracle-bearing rule | `src/iladub/ground.py:107-115` | which fields a proposal can ever be admitted on |
| the seam A would use | `src/iladub/ground.py:194-199`, `src/iladub/propose_ground.py:16-33` | `proposer.propose_grounding` after `exact_field` returns `None`; `GroundingProposal(field_iri=None)` is the shipped abstain |
| the ruling this handoff sits beside | `docs/superpowers/2026-09-10-the-grid-the-author-drew-handoff.md` | the R201 thread, paused; its part 5 is the other next loop |

## 2. What changed

Nothing in the tree. This file only.

## 3. What was decided, and where that decision is recorded

- **Nothing about GLiNER2 is decided.** The spec is unreviewed; the maintainer asked for a read and
  got one in conversation (2026-09-10, this session). The read is: A conditionally, gated by the
  count; B restricted to textual fusion; C dropped. **Recorded nowhere but here and part 5c** —
  reversible.
- **The count comes before T1.** Recorded here only.
- The spec branch stays unpushed until the maintainer says otherwise; the reason its author gave
  (this session owned the tree) no longer holds — R201 is merged (PR #190) and the tree is idle.

## 4. Unverified or assumed

- **The count itself.** 5b is a prediction; nothing in this session ran `reach_probe.py` or
  `ground_document` on either stem.
- **That the abstaining proposer's `proposed` equals A's population** assumes `exact_field` is the
  only path that binds without a proposal. `ground.py:190-199` reads that way; not traced further.
- **"Oracle-bearing" was read off `_grounds_to`'s docstring**, not off the two contracts. Which of
  `stem-contract.ttl` / `cbh-contract.ttl`'s fields carry a scheme or a value constraint is
  unmeasured — that is step 2 of 5a.
- **The spec's own corpus is a different one** — `doc-to-markdown/sample_documents/` (CBH, Bunge,
  GrainCorp, Cargill; spec § 6.5). The manifest corpus is what the tests run and what this handoff
  measures against. Reconciling the two is the spec review's problem, not the count's.
- **The probe repo's "PID 20264 hazard"** (a running loop owning the iladub tree) was this session.
  It is over.
