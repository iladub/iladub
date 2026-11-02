# The document router — split a PDF into documents and say which are contracts (design, 2026-11-02)

**Serves:** maintenance — project 2 of the three that the contract:01 rescope became (handoff
`docs/superpowers/2026-10-31-synthetic-contract-set-executed-handoff.md` § 8). No criterion exists for it yet.

**Topic:** contract · **Date:** 2026-11-02

**Doc impact: none.** It adds a router and one generated test document. Alignment to gist and FIBO
is new, but it lives in an `*-align` module or in the router's own owned terms, and no released page
changes. (If the plan finds an owned class must enter `etkl.ttl`, this becomes `increment`.)

**Status: DRAFT — awaiting the maintainer's review.** It writes up the 2026-11-02 brainstorm. Each
statement is marked **(owner)** if the owner decided it in chat, and **(call)** if it is the
author's call, open to correction.

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
- G4. **Meet the bar of § 6** on the synthetic set plus m4.

**Non-goals**

- The **trade name** (GAFTA sale contract, charter party, UN/CEFACT document code) — project 3
  (owner).
- **Tables and blanks inside a document** — project 3 (owner). Contract tables are small; the
  report-table machinery (etkl) is not brought in (owner).
- Clause-level reading of any kind — project 3.

**Anti-goals** (what makes it a failure even if it scores)

- A **wrong assertion**: a boundary or a type asserted and wrong. Refusing is allowed; asserting
  wrongly is not (§ 6 B3) (owner, approving the bar).
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

**Deciders, per CLAUDE.md § 8:** the ladder's classing (compiler design § 5) carries over unchanged:
exact rules are AXIOM, HDC and the models are NEURAL-class proposers, the owner is the last rung,
and every proposer has an oracle (the checklist above for Q-doctype; for Q-boundary, the plan must
name one — see § 8).

## 5. The trace

Each document's type and extent is one `dec:DecisionHolon` (call): `prov:used` its evidence lines,
`prov:wasAssociatedWith` the rung that decided (rule, HDC, Jev, model, owner), and a sentence in
domain words — e.g. *"contract: parties X and Y found (p1 l4, l6); commitment p1 l12"*. An admitted
new type is an `iladub:PromotionDecision`. Provenance to the page (CLAUDE.md principle 6).

## 6. The bar — when the router is done (owner, approving the proposal 2026-11-02)

Measured on the 40 PDFs: the 39 of the synthetic set plus **m4** (§ 7).

- **B1. Boundaries are line-exact.** A predicted start is correct when it falls between the last
  line of the previous document and the first line of the next — no distance tolerance.
- **B2. Types are right.** Contract-form and charter-party parts → `ContractDocument`. The rules
  part (GAFTA No. 124, unfilled) is **not** a contract, and is the first expected run of the
  new-type path: the router proposes, the owner admits or refuses.
- **B3. Zero wrong assertions.** Refusals are allowed, counted and reported. One wrong asserted
  boundary or type fails the bar.
- **B4. Flavours agree.** The form-fill, handwriting-scan and Word-export PDFs of one fill give the
  same documents and types.
- **B5. Learning is measured on documents it did not learn from.** Owner answers to gaps are taken
  on **fills 1 and 2** of each template only; **fill 3 and m4 are held out** and only measured. On
  the held-out set: B1–B4, plus a count of which rung decided each document. Rules written back from
  fills 1–2 deciding fill 3 without a model is the evidence the loop works.
- **B6. Every decision reads in domain words** and points at its page lines (§ 5).

## 7. m4 — the mid-page test document (owner: "generated m4 is fine")

The set's m1–m3 join their parts at page breaks only, so a mid-page start is untested. **m4** is one
more generated mixed document in which a second document **begins partway down a page** — e.g. a
contract with the rules it incorporates following directly after its last clause (call). Its truth
records the boundary as a page position, not only a page number. It is built by the existing
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
- The owner-answer interface (how a gap question reaches the owner and the answer is recorded).

## 9. Dependencies and open points for the owner

- **The decider ladder and HDC are unbuilt.** The router is its first user. Building the ladder
  here makes this loop larger than "a router"; deferring HDC keeps it smaller (call: the plan
  proposes, the owner rules).
- **Jev** was reached through hdc-contract's BAML client (compiler design § 4.2), and nothing comes
  from hdc-contract (decision 18). Whether Jev is reachable from iladub's own `baml_src/` is
  unverified.
- **Scans have no text** (§ 10, measured). Lines for 13 of the 40 PDFs come from OCR or a vision
  model; which one, and whether that is this loop's, is open.
- **α** (the declared risk tolerance per question, compiler design § 4.5) is unset for Q-boundary
  and Q-doctype.

## 10. Unverified or assumed

- That the FIBO checklist (two parties + one commitment) separates the set's contracts from its
  rules parts — read from the ontology, not measured on the PDFs.
- ~~That handwriting-scan PDFs yield extractable lines~~ **Measured 2026-11-02: they do not.**
  pypdfium2 text over all pages of `synthetic/out/gafta-48-1.*.pdf`: form-fill 42,345 chars (8 pp),
  word-export 38,973, handwriting-scan **0**. So 13 of the 40 PDFs (12 scans + m3's scanned part)
  need OCR or a vision reader before any line exists — see § 9.
- That the set's truth `syn:partType` values map one-to-one onto § 3's types (contract-form,
  charter-party → `ContractDocument`; rules → not) — the mapping is the router's scoring contract
  and the plan states it.
