# Handoff 2026-10-30: the owner's redirect — model the contract once, then compile against the model

## 1. Goal

Brainstorm (superpowers:brainstorming) the owner's redirect below with the owner, and decide what it
changes in the contract-rung spec and in the hdc-contract companion spec. Do this before either spec
goes further.

## 2. Where the primaries are

- **The owner's words** (2026-10-30, verbatim, typos kept):
  > I am pretty sure contracts have their own structure, GAFTA included. What if we mode first these
  > contracts so they have theri own ontologies we record and we reuse later. Instead for trying to
  > recompile it eache time, we do it once this is contract sematnic modeling, iladub will then reuse
  > the gafta ontologies to make it a holon. this is where I can see ponteial for hdc, if we have
  > already the semantic model of the clauses for Gafta, cna we use hdc, jev and eventually haiku to
  > compile the pdf based on the semantic model in turtle or jsonld (prefered). Iladub will see the
  > pdf, recognize this is a contract, pick a contract ontology and then compile the pdf accordingly,
  > and finally make it a holon
- **The owner's follow-up** (2026-10-30, same session, verbatim, typos kept):
  > Lets take it in a fresh session, I think we should try for this lane to onboard hdc and eventually
  > jev and small models like haiku or event small models that can runs on a regular machine (4-9b
  > parameters). I am keen to use small but highly available small models since the dependencies on
  > vendors is closed to zero. The idea is to simplify the neur-symbolic steps to compile a semantic
  > mode. The experience with etkl and tables is that building a compiler is getting too complex awith
  > risks also for human to lose the understandings of how this works as machine and human logical
  > start to diverge, and this is also something I want to avoid, humans and machine must have a
  > lingua franca, simple enough so iladub maintenance become easier as well as efficiency for
  > compiling. Now we hare facing challenges with how: long and unefficient compiling time. This goes
  > a bit against the original idea but the first concenr is not zero llm, it is only where no other
  > choice or to catalyze rule compilation we own totally.
- **The spec this may supersede:** `docs/superpowers/specs/2026-10-30-contract-rung-design.md`
  (this branch, uncommitted edits to § 3, § 5, § 6 and § 10). § 3 M-e to M-r hold the measured
  structure of the GAFTA corpus. Establish there what a GAFTA form's structure looks like
  (numbered clauses, headings set in capitals, a preamble, a signature/footer tail) and where it
  varies (M-o: period-less numbers, sentence case, in 13 of 80 forms).
- **The previous review handoff:** `docs/superpowers/2026-10-30-contract-rung-spec-review-handoff.md`
  (§ 4b holds what the last session did; items 4–9 are still open).
- **The rulings the redirect touches:** hdc-contract
  `docs/superpowers/2026-10-30-handoff-rescope-specs.md` § 3 (untracked in that checkout). Read
  rulings 2, 4, 5 and 9 against the redirect.
- **What already exists as a GAFTA semantic model:** hdc-contract `ontology/gco-concepts.ttl`
  (37 `gco:ClauseType` SKOS concepts), `ontology/gco*.ttl`, and `alignments.ttl`. Establish whether
  it is a clause-*type* vocabulary only, or already models a form's structure (it has no per-form
  model that I know of — unverified).
- **HDC side:** hdc-contract `src/hdcc/hdc/text.py:108` (`PrototypeClassifier`) and
  `hdc/codebook.py`. This is what "use HDC to compile against the model" would build on.
- **iladub's document recognition:** how iladub picks a compiler today (`readers.py`, `m4.py`
  `compile_offer`). Establish whether "recognise this is a contract, pick an ontology" has a
  precedent.

## 3. What was decided, and where it is recorded

- The first message was a question. The follow-up gives **direction from the owner**, recorded only
  in this file and in memory `tiny-semantic-architecture`. Read the quote; the points below are my
  summary of it:
  - **This lane brings in HDC first**, then Jev, then small models: Haiku, or local 4-9B models
    that run on a regular machine. The aim is close to zero vendor dependency.
  - **Simplicity over cleverness.** The etkl/table compiler grew too complex, to the point where
    human and machine logic diverged. Humans and the machine need a **lingua franca** simple enough
    to keep iladub maintainable. Compiling is currently slow and inefficient.
  - **"Zero LLM" is relaxed, not dropped.** Use a model only where there is no other choice, or to
    *catalyse* rules that the project then fully owns. Read this against ruling 4 and against
    contract:01 being model-free.
- The § 5 rewrite of the contract-rung spec (strict contiguity, untuned segmenter, `ctr:preamble`)
  is recorded only in the uncommitted spec on this branch. The owner has not reviewed it.

## 4. Unverified or assumed

My reading of the redirect, which the owner has not confirmed:

- **Two phases.**
  - *Modelling* happens once per contract family (GAFTA), and yields a recorded ontology in JSON-LD
    (preferred) or Turtle.
  - *Compiling* happens per PDF. iladub recognises a contract, selects the family ontology, fills it
    from the PDF, and emits a holon.
- **Possible conflicts with earlier rulings:**
  - **Ruling 4 and contract:01, "model-free":** the follow-up softens this. Models are allowed
    where there is no other choice, or to catalyse owned rules. Still open: is the per-PDF compile
    model-free once the rules exist, with models only proposing rules? Or do models run on every
    PDF? "Catalyse rules we own" points to the former. Not confirmed.
  - **Ruling 2, the repo split:** where do HDC, Jev and Haiku sit if they compile? Today they are
    hdc-contract's arbitration engine.
  - **Ruling 5:** is the ingest still ported into iladub?
- **Possibly the same thing:** "the semantic model of a GAFTA form" may be what the § 5 segmenter
  plus the `gco` scheme already is, implicitly. Making it explicit may mean writing the structure
  (clause slots per form number, expected headings) into the ontology instead of the regexes.
  Under that reading, compiling a known form becomes matching against the model, and the 13 refused
  forms (M-o) become model gaps, not extractor failures.
- **Per-form or per-family?** GAFTA forms differ (Nos. 48 and 64 have different clause lists). The
  ontology may be per form number or per family. Not checked.
- **What "recognise this is a contract" decides on** has not been designed. It could be a
  classifier, Jev, or a declared document type.

- **Local 4-9B models** are not yet in either repo's model layer. Whether BAML or Jev can route
  to them was not checked.
- **"Lingua franca"** is undefined. One candidate is JSON-LD rules and models that a human can read
  and edit. Another is the § 5 rule table itself.
- **Compile time** is named as a problem but was not measured in this session.

## 5. Next concrete action

In a fresh session, invoke superpowers:brainstorming with the owner on § 2's verbatim redirect,
starting from § 4's two open conflicts (ruling 4 and ruling 2), before editing either spec.
