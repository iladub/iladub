# The document router — split a PDF into documents and say which are contracts (design, 2026-11-02)

**Serves:** maintenance — project 2 of the three that the contract:01 rescope became (handoff
`docs/superpowers/2026-10-31-synthetic-contract-set-executed-handoff.md` § 8). No criterion exists for it yet.

**Topic:** contract · **Date:** 2026-11-02

**Doc impact: none.** It adds a router and one generated test document. Alignment to gist and FIBO
is new, but it lives in an `*-align` module or in the router's own owned terms, and no released page
changes. (If the plan finds an owned class must enter `etkl.ttl`, this becomes `increment`.)

**Status: DRAFT — owner answers folded in (2026-11-02), awaiting the maintainer's approval.** It
writes up the 2026-11-02 brainstorm and the owner's answers to the handoff's questions
(`docs/superpowers/2026-11-02-document-router-spec-handoff.md` § 6). Each statement is marked
**(owner)** if the owner decided it in chat, and **(call)** if it is the author's call, open to
correction.

## 1. Intent

Until now iladub read reports and tables, and the caller chose the reader (`readers.read_document`
picks by file suffix, `src/iladub/readers.py:16-28`). Nothing says what a document *is*. The router
is the contract compiler's first step: given one PDF, it **finds the documents inside it** and
**says, for each, whether it is a contract** — so that later steps compile each document by what it
is (owner).

The router is semantic: its type words come from **existing ontologies**, not from a tree iladub
invents (owner: "we do not want to reinvent the wheel").

## 2. Goals, non-goals, anti-goals

**Goals**

- G1. **Split** a PDF into its documents. A document may start on a new page **or partway down a
  page** (owner: "real documents do that").
- G2. **Type** each document: it **is** a FIBO `ContractDocument`, or it is not (owner). A document
  that fits no known type gets a **proposed new type** that the owner admits or refuses (owner,
  2026-10-31 rescope).
- G3. **Decide with the existing decider ladder** of the HDC-first compiler design
  (`specs/2026-10-30-hdc-first-contract-compiler-design.md` § 4.2) — exact rule → HDC → Jev →
  small model → owner — with gap answers written back as owned rules (§ 4.4 there) (owner).
  **For the router, models decide** (owner, 2026-11-02): Jev, with Haiku as fallback, answers the
  gaps; the owner is not the cold-start decider. This **relaxes compiler design § 4.5 decision 12**
  (a model admitted only below a measured error ≤ α) for the router — see § 4.
- G4. **Meet the bar of § 6** on the text PDFs of the synthetic set plus m4.

**Scans are phase 2** (owner, 2026-11-02). The 12 handwriting-scan PDFs have no text (§ 10); once
OCR gives them lines, the router's logic is the same. This loop reads only PDFs with a text layer.

**Non-goals**

- The **trade name** (GAFTA sale contract, charter party, UN/CEFACT document code) — project 3
  (owner).
- **Tables and blanks inside a document** — project 3 (owner). Contract tables are small; the
  report-table machinery (etkl) is not brought in (owner).
- Clause-level reading of any kind — project 3.

**Anti-goals** (what makes it a failure even if it scores)

- A **wrong assertion**: a boundary or a type asserted and wrong. Refusing is allowed; asserting
  wrongly is not (§ 6 B3) (owner, approving the bar). **A refusal is not wrong** (owner,
  2026-11-02): we are in the open world here, and there is no minimum share of asserted documents.
  Strictness comes later, when SHACL is applied at the membrane.
- A **geometric heuristic with a tuned constant** deciding where a document starts (CLAUDE.md § 8).
- A **home-made type tree** where gist or FIBO already has the class (owner).
- Learning that only works on the documents it learned from (§ 6 B5; memory "no overfitting").

## 3. Vocabulary: what is reused, what is owned

| need | source | status |
| --- | --- | --- |
| upper level: a document, an agreement | **gist** (`gist:Content`, `gist:Agreement`, `gist:Contract`) — already iladub's upper anchor | (owner) |
| "this document records a contract" | **FIBO FND** `Contracts/ContractDocument` (⊑ `LegalDocument`, `records some Contract`) | verified 2026-11-02, below |
| what makes a contract a contract | FIBO `Contract`: `hasContractParty` min 2 `ContractParty`; `hasContractualElement` some `ContractualElement`; `WrittenContract` adds principal party + counterparty, `isEvidencedBy some ContractDocument` | verified 2026-11-02 |
| the routing decision itself | **owned**: a `dec:DecisionHolon` per document (§ 5) | (call) |
| an admitted new type | **owned** term, anchored by `rdfs:subClassOf` to gist (or FIBO where it fits) | (call) |

**FIBO verification (2026-11-02).** The live module
`https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/` was fetched (text/turtle,
66,206 bytes; copyright 2013–2026 EDM Council / 2013–2025 OMG) and parsed: the restrictions in the
table are read from it. **Licence: MIT** (its `dcterms:license`). FIBO has **no trade-contract
types** (no sale of goods, no charter party) — consistent with the trade name going to project 3.

**Alignment, not import** (call), as with HGA: owned terms point at gist/FIBO by `rdfs:subClassOf`
/ `seeAlso`; FIBO is not loaded into the compile graph, and no reasoner is run.

**FIBO's restrictions are open-world** (`min 2` cannot conclude "not a contract" from a missing
party). The router therefore uses them as a **checklist in SPARQL over evidence found on the page**
(CLAUDE.md § 8, derivation is open-world), never as reasoner classification (call).

**UN/CEFACT is not used here** (owner: trade name → project 3). Recorded for project 3: the
document-name code list UNCL1001 is real and in use (Peppol requires it, version D.17A), but the
JSON-LD site `vocabulary.uncefact.org` returns 403 to scripted fetches, and `github.com/uncefact/vocab`
has had no commit since 2024-07-18, declares no licence, and has an empty `json-ld-outbound/`.

## 4. What the router does

Input: one PDF. Output: an RDF graph (Turtle) with one **document** per part found, each carrying:

- its **extent**: start (page + the first line of the document) and end (page + last line);
- its **type**: `ContractDocument`, an admitted owned type, or **refused** (left a proposition with
  its reason);
- the **routing decision** that produced the type and extent (§ 5), with its evidence lines.

Two named questions, both on the ladder (G3):

- **Q-boundary: does a new document start at this line?** Answered per candidate line, so a
  mid-page start is the same question as a page-top start (call).
- **Q-doctype: what kind of document is this extent?** Answer: a type from § 3, or "none of these"
  (→ the gap path → a proposed new type).

**The contract checklist is Q-doctype's oracle for `ContractDocument`** (call): an answer
"contract" is admissible only when the evidence names **at least two parties** and **at least one
commitment**, each a line that is on the page (verbatim check) — FIBO's `Contract` restrictions read
as a checklist. A proposer that names evidence not on the page is refused.

**"Not a contract" may be asserted** (owner, 2026-11-02), when the document actually is not one.
It is asserted **only from positive evidence of another kind of document** — lines on the page,
verbatim-checked, that the proposer cites (e.g. a heading naming rules for sampling) — **never from
a missing party or a missing commitment** (call: open world, § 3; absence of a checklist item
supports a refusal, not a negative). "Not a contract" and the document's own type are two
statements: the first may be asserted while the second is still a proposed new type awaiting
admission (G2). How the negative is written in RDF (an owned outcome on the decision, not
`owl:complementOf`) is the plan's.

**Deciders, per CLAUDE.md § 8:** the ladder's classing (compiler design § 5) carries over: exact
rules are AXIOM, HDC and the models are NEURAL-class proposers, and every proposer has an oracle
(the checklist above for Q-doctype; for Q-boundary, the plan must name one — see § 8). What changes
for the router (owner, 2026-11-02):

- **Models decide.** A model answer that passes its oracle is the decision — no owner rung after
  it, and no gate on a measured error below α. Decision 12 of compiler design § 4.5 is relaxed **for
  the router only**; the compiler's later steps are not ruled by this.
- **Jev first, Haiku as fallback.** Jev is not reachable from iladub's `baml_src/` today (measured
  2026-11-02: `grep -ri jev baml_src/` → nothing; Haiku and Sonnet clients exist), and nothing comes
  from hdc-contract (decision 18). Making Jev reachable is the plan's first MEASURE seam; until it is,
  Haiku decides.
- **The owner admits new types**, and only that (G2): an admitted type is an
  `iladub:PromotionDecision`. The owner answers no Q-boundary or Q-doctype question.
- **α gates nothing in this loop** (call). With models deciding, the model's error is *measured* on
  the learning set against the truth and reported per question, not used as an admission gate.
  B3 (§ 6) is the hard gate.

## 5. The trace

Each document's type and extent is one `dec:DecisionHolon` (call): `prov:used` its evidence lines,
`prov:wasAssociatedWith` the rung that decided (rule, HDC, Jev, model, owner), and a sentence in
domain words — e.g. *"contract: parties X and Y found (p1 l4, l6); commitment p1 l12"*. An admitted
new type is an `iladub:PromotionDecision`. Provenance to the page (CLAUDE.md principle 6).

**Decidability is traced** (owner, 2026-11-02: "models decide and decidability must be traced").
Because a model's answer is final here, the holon must say *which* model decided — the rung and the
model identifier (e.g. Jev's version, or the Haiku model id) — and the oracle that admitted it. A
refusal is a decision holon too, with the reason the ladder stopped (call — unlike grounding, where
a refusing concept mints no holon; here the refusal is the router's output and B3 counts it).

## 6. The bar — when the router is done (owner, approving the proposal 2026-11-02)

Measured on the **27 text PDFs** (owner, 2026-11-02: scans are phase 2), counted from the set's
truth:

| set | PDFs | count |
| --- | --- | --- |
| learning | fills 1–2 of the 4 templates × form-fill, word-export; **m1**, **m2** | 16 + 2 = 18 |
| held out | fill 3 of the 4 templates × form-fill, word-export; **m4** (§ 7) | 8 + 1 = 9 |
| phase 2 | the 12 handwriting-scan PDFs; **m3** (its second component is `gafta-48-3` handwriting-scan, `examples/synthetic-contracts/mixed/m3.ttl`) | 13 |

The split is a (call): m1 is built from `gafta-48-1` and m2 from `gafta-79b-2` / `usda-ffp-cp-2`, so
both are learning documents; m4 is built from fill 3 and unfilled templates only, so it is held out.
m3, when its scan half has lines, is **two documents** (call: two copies of one contract are two
documents; its truth has parts `a.contract-form` and `b.contract-form`).

- **B1. Boundaries are line-exact.** A predicted start is correct when it falls between the last
  line of the previous document and the first line of the next — no distance tolerance. A predicted
  start line is placed by its position on the output page against the truth boxes (output-page
  coordinates, already in the truth); m4's truth adds the boundary's y position (call).
- **B2. Types are right.** Contract-form and charter-party parts → `ContractDocument`. Rules parts
  → **not** a contract, asserted only from positive evidence (§ 4), and the first expected run of
  the new-type path: the router proposes, the owner admits or refuses. Rules parts are the No. 124
  PDFs **filled or not** (6 in this loop, 3 scans in phase 2) and m1's second component (unfilled
  No. 124) — (call, measured: each of the 9 No. 124 truth files and m1's has exactly one part
  `syn:partType "rules"`, with the filled sample-label blanks *inside* it, so a filled No. 124 is one
  rules document, not a rules document plus a form).
- **B3. Zero wrong assertions.** Refusals are allowed, counted and reported, and **a refusal is not
  wrong** (owner, 2026-11-02): no minimum asserted share. One wrong asserted boundary, type or
  "not a contract" fails the bar. A router that refuses everything passes B3; the refusal count
  is reported, and the membrane's SHACL is where strictness enters later.
- **B4. Flavours agree.** The form-fill and Word-export PDFs of one fill give the same documents
  and types, compared by count, order and type, not by line identity (call). The handwriting-scan
  flavour joins in phase 2.
- **B5. Learning is measured on documents it did not learn from.** Model answers to gaps are
  written back as owned rules from the **learning set only**; on the **held-out set** write-back is
  off and the router is only measured. On the held-out set: B1–B4, plus a count of which rung
  decided each document. Rules written back from the learning set deciding held-out documents
  without a model is the evidence the loop works.
- **B6. Every decision reads in domain words** and points at its page lines, and names the rung
  and model that decided (§ 5).

## 7. m4 — the mid-page test document (owner: "generated m4 is fine")

The set's m1–m3 join their parts at page breaks only, so a mid-page start is untested. **m4** is one
more generated mixed document in which a second document **begins partway down a page** — e.g. a
contract with the rules it incorporates following directly after its last clause (call). It is built
from **fill 3 and unfilled templates only**, so it stays held out (§ 6). It has a text layer (no
handwriting-scan component). Its truth records the boundary as a page position (page + y on the
output page), not only a page number. It is built by the existing
generator (`scripts/synthetic_contracts/`, spec `2026-10-31-synthetic-contract-set-design.md`
§ 4.4–4.5), extended as needed; its fill and truth are committed like the others.

## 8. What is left to the builder

- **Q-boundary's oracle.** Q-doctype has the contract checklist; Q-boundary needs a named oracle
  before any proposer is written ("no oracle, no worker"). The plan proposes one (candidate: the two
  sides of a boundary must each pass Q-doctype as *different* documents, or as the same type with a
  restart signal the proposer cites verbatim) and states its falsifier.
- **Which rungs exist for this loop.** The ladder is designed, not built (no decider code in `src/`
  as of 2026-11-02; no `torchhd` dependency). The HDC rung requires the HDC skill first (compiler
  design § 4.8, decision 17). The plan decides whether the router ships with rule + model + owner
  rungs and HDC enters later, or waits for the skill — see § 9.
- Where the router lives in `src/` and how it is called.
- The candidate lines for Q-boundary (every line, or lines the extraction marks as starting a
  block) — raw extraction is PROCEDURAL, the choice among candidates is not.
- The new-type admission interface (how a proposed type reaches the owner and the admission is
  recorded as an `iladub:PromotionDecision`). No other owner interface is needed (§ 4).
- **First MEASURE seam: Jev from iladub.** Add a Jev client to iladub's own `baml_src/` (not
  hdc-contract's) and show one call answering; until then Haiku decides (§ 4).
- The RDF form of an asserted "not a contract" (§ 4).

## 9. Dependencies and open points for the owner

- **The decider ladder and HDC are unbuilt.** The router is its first user. Building the ladder
  here makes this loop larger than "a router"; deferring HDC keeps it smaller (call: the plan
  proposes, the owner rules). With models deciding and no minimum asserted share (§ 6 B3), a first
  loop with rule + model rungs and no HDC can meet the bar — the handoff's worry that Q1 might
  demand more is gone.
- ~~**Jev** reachability~~ → settled as § 8's first MEASURE seam (owner: Jev, Haiku fallback).
- ~~**Scans**~~ → phase 2 (owner, 2026-11-02; § 2).
- ~~**α**~~ → gates nothing in this loop (§ 4, call).
- **Open, for approval:** the (call)s of this fold-in, chiefly: "not a contract" only from positive
  evidence (§ 4); a refusal minting a decision holon (§ 5); filled No. 124 is one rules document
  (§ 6 B2); the learning / held-out split (§ 6).

## 10. Unverified or assumed

- That the FIBO checklist (two parties + one commitment) separates the set's contracts from its
  rules parts — read from the ontology, not measured on the PDFs.
- ~~That handwriting-scan PDFs yield extractable lines~~ **Measured 2026-11-02: they do not.**
  pypdfium2 text over all pages of `synthetic/out/gafta-48-1.*.pdf`: form-fill 42,345 chars (8 pp),
  word-export 38,973, handwriting-scan **0**. So 13 of the 40 PDFs (12 scans + m3's scanned part)
  need OCR or a vision reader before any line exists — phase 2 (§ 2). The measurement covers
  `gafta-48-1` only; that the other scans are alike is assumed, and moot for this loop.
- That models deciding without an error gate (§ 4) yields zero wrong assertions (B3) — the oracles
  are the only guard; untested until the loop runs.
- That the set's truth `syn:partType` values map one-to-one onto § 3's types (contract-form,
  charter-party → `ContractDocument`; rules → not) — the mapping is the router's scoring contract
  and the plan states it.
