# Rulings — B2, B3, B7, P1 (`holon:05`)

**Date:** 2026-08-25 · **Decides:** findings **B2**, **B3**, **B7** and **P1** of
`docs/superpowers/2026-08-25-holon-05-adversarial-review.md` · **`main` @ `7c36945`** (merge of PR #119)
· **Shape: mechanical** — this file records four decisions taken in conversation; it authors no design.
The design consequences are carried by the spec revision, which cites this file rather than restating it.

Companion to `docs/superpowers/2026-08-25-holon-05-b1-ruling.md`, which decided **B1**. Together the two
files close items 1, 2, 3, 6 and 8 of the review's closing list. **All four options below were chosen by
the maintainer from the review's own options-with-costs, and are recorded here and nowhere else —
therefore reversible.**

---

## B2 — the verdict fact becomes an owned activity node

**Chosen: record the validation *act*, not the graph's status.** Mint
`etkl:MembraneValidation ⊑ prov:Activity`, carrying `prov:used <doc>`, the conformance boolean, and
**the leg identity `_validate` already returns and the previous design discarded**
(`conforms, text, legs = _validate(...)`, `document.py:1624`).

Not `sh:ValidationReport` (B2): a node typed `sh:ValidationReport` with `sh:conforms false` and **zero**
`sh:result` contradicts SHACL Rec §3.6, and §2.3 measured both engines discarding the report graph — so
the `sh:result` that would make it well-formed is not available and cannot be added without the report
plumbing §9 scopes out. It is also the honest answer to the **stored-label** objection: an activity
record is immutable and stays true; a claim about the current state of a mutable graph, stored inside
that graph, goes stale the moment anything is added to it.

**Costs accepted:** a **second** new owned term this loop (with `etkl:CompiledDocumentHolon` from B1),
and `prov:` entering the mint path.

**Settles:** §4.2's subject, §6's PROCEDURAL justification (the *classification* was never in doubt —
an engine verdict is not derivable from the evidence graph — only the subject), and target 1 of the
handoff. **Does not settle:** B6's datatype pinning, which applies to the conformance literal whatever
node carries it.

---

## B3 — the `Weakened` amendment is carried in full

**Chosen: carry the semantic amendment completely**, and state it as what it is — an amendment to the
health model, not a one-comment tweak. After B1's ruling the set is **four** artifacts, amended in one act:

1. `etkl:Weakened`'s `rdfs:comment` (already planned in §4.6)
2. `etkl:MembraneHealth`'s `rdfs:comment` — it contradicts the design too
3. `docs/holonic-interaction.md`'s planned-work bullet — the criterion's own `prog:source`
4. `tests/arc-manifest.ttl`'s `prog:statement` for `holon:05`, a verbatim join of (3)

**Amending a criterion's statement in the loop that closes it gets its own comment in the manifest
saying so.** Not amending: `etkl:CleanDocumentHolon`'s comment — B1 removed it from the set, because the
loop no longer claims the compile graph is one.

**Per B8, the new wording says *held propositions*, never *everything that reached the boundary*.**
`graincorp-stem` scores `0.9655` with 77 escalated tokens and still reads `Intact`: **`score` and
`membraneHealth` are two different signals**, and a *published* `rdfs:comment` that blurs them will be
read as "fully read" when it means "nothing is held at the membrane."

**Rejected: scoping `Weakened` out** as an underivable residue. More honest about the vocabulary as
published, but it ships a three-valued property with one unmintable value, and the criterion asks for
three — so `holon:05` could not flip to `prog:met true` and the loop would not close.

---

## B7 — site constraint restated, plus a shape; the shared IRI stays a residue

**Chosen: two things, and no signature change.**

1. **§4.3's site constraint is restated with subject-IRI collision as its real reason.** The previous
   spec justified *"one document's graph, never a union"* as closed-world scoping. The stronger reason
   is that `_DOC` is **one IRI shared by every document**, so a union puts two health values on one
   subject — the review measured exactly that (`Compromised` **and** `Intact`, three triples, one `?doc`).
2. **A minimal `MembraneHealthShape` ships** — `sh:maxCount 1` on `etkl:membraneHealth`,
   `sh:in (etkl:Intact etkl:Weakened etkl:Compromised)` — with the conforming example **and** the
   negative test CLAUDE.md § Serialization requires. It is **validated in the test, NOT loaded into the
   compile membrane**: loading it would re-open §2.1's safety argument *and* be vacuous anyway, because
   health is minted **after** validation runs.

**`owl:FunctionalProperty` is explicitly the wrong instrument** and is not adopted: inference is off
(`membrane.py:124-125`, `inference="none"`), so it would do nothing; and under a reasoner it would
*entail `owl:sameAs`* between two health values rather than refuse them — failing upward, which is B6's
class of defect.

**Rejected: threading a real `doc_uri` through `compile_document`.** Measured while ruling: `compile_tables`
and `page_doc_uri` **already take** a `doc_uri` (`compile.py:572`, `document.py:268`), `compile_document`
does **not** (`document.py:1165`), and only 5 files hardcode the literal — so the fix is smaller than the
review implied. It is still a **URI-identity change inside a health-reporting loop**, putting every
compiled URI in the corpus in scope. **Residue, not this loop.**

**This answers the review's standing observation** — *"the thing that reports the membrane's health is
outside every membrane"* — with a shape rather than a silence, without pretending the shape closes the
identity defect underneath it.

---

## P1 — the promotion clause's residual becomes a machine tripwire

**Chosen: both halves of P1, and the registry extension is IN SCOPE.**

1. **O3 is not fixture-only.** §5.6's consequence — *"it cannot be pinned on real input … the plan must
   build the graph by hand"* — is withdrawn. The causal claim behind it stands (the `promote.py` emitters
   are proposer-driven, so a bare compile yields `promoted = 0`); the consequence conflated *corpus
   document* with *real execution path*. `tests/etkl/test_rowrole_integration.py:106` compiles with a
   proposer at the default `validate_shapes=True` and asserts the promotion in the committed graph, and
   document scope with a proposer was measured at **`promoted=2, held=0` in 2.6 s**. O3 uses that vehicle.
2. **The narrowed residual — *unexercised on the corpus sweep* — is registered, not prosed.** The
   vacuity registry already owns this exact question for shapes, with a **bidirectional** tripwire that
   fails the suite if a registered-idle clause later goes live. This loop introduces the first AXIOM `.rq`
   with the same property. R106's own row says *"the rule that catches it is prose"*; a prose residue here
   would be its second instance.

**Cost accepted:** the registry extension is new machinery in a loop that already mints two terms and a
shape. If the extension turns out to need more than parameterising the existing population, the fallback
is a register row — **and the spec must say which, from a measurement, before the plan is written.**

---

## The next concrete action

Revise `docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md` from the review's
closing list, items 2 onward, citing this file and the B1 ruling rather than re-deriving them. Items 4,
5, 7, 9 and 10 of that list need no ruling — they are corrections the revision applies directly.
