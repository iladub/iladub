# Handoff 2026-11-02: the document router spec is drafted; builder check sorted, owner questions open

**Topic:** contract · **Date:** 2026-11-02 ·
**Serves:** maintenance — project 2 of the contract:01 rescope; no criterion yet.

Written at ~64K working tokens (over the 50K originating floor). Part 5 is graded per action.

## 5. Next concrete action (written first; typed)

1. **Asserted** (mechanical): the owner answers the four questions in § 3b (asked in chat 2026-11-02;
   if answered there, the answers are in that session only until folded in).
2. **Asserted** (mechanical, fresh session): fold the answers and the § 3a calls into the spec
   (§ 6 bar, § 7 m4, § 9, § 10), set Status to APPROVED once the owner says so, take this PR out
   of draft.
3. **Proposed** (may fail): the plan (superpowers:writing-plans) can scope a first loop without the
   HDC rung. It fails if the owner's answer to Q1 demands an asserted share the rule + model + owner
   rungs cannot reach on held-out fill 3.

## 1. Goal

A design for the router: split a PDF into documents (page or mid-page starts) and say, per document,
FIBO `ContractDocument` or not, on the compiler's decider ladder, scored on the 39-PDF set plus m4.

## 2. Where the primaries are

- Spec: `docs/superpowers/specs/2026-11-02-document-router-design.md` (this branch).
- Ladder and calibrated check it reuses: `specs/2026-10-30-hdc-first-contract-compiler-design.md` § 4.2, 4.5.
- Set and truth: `specs/2026-10-31-synthetic-contract-set-design.md`; `examples/synthetic-contracts/`
  (PR #386 merged as 7cede2aa).
- FIBO evidence: re-fetch `https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/`
  (Accept: text/turtle); the scratchpad copy is not kept.

## 3. What was decided, and where

All owner decisions of the brainstorm are marked **(owner)** in the spec. Recorded nowhere else.

### 3a. Builder-check answers the author settled (to be marked **(call)** in the spec)

- **m3 is two documents** (two copies of one contract are two documents); follow its truth parts.
- **Learning/held-out split:** m1, m2 learn; m3 (built from fill 3) and m4 are held out; m4 is built
  from fill 3 and unfilled templates only.
- **"Line" for scoring:** B1 maps a predicted start line's position to the truth boxes (output-page
  coordinates already in the truth); m4's truth adds the boundary's y position. B4 compares documents
  by count, order and type, not by line identity.

### 3b. Owner questions (theirs; the answer changes what is built), most important first

- **Q1.** Does a refusal fail B1/B2, or is there a minimum share of documents that must be asserted
  (on held-out)? A router that refuses everything passes B3 as written.
- **Q2.** Are the 13 scan PDFs in this loop (OCR = PROCEDURAL, or a vision model = NEURAL with its
  own oracle), or is the bar restated for the 27 text PDFs + m-docs without scans?
- **Q3.** How many owner questions are acceptable in the learning pass, live or in one batch?
  Q-boundary per candidate line at cold start could mean thousands.
- **Q4.** May the router ever *assert* "not a contract", or is a rules document's only correct
  output a refused proposition with a proposed new type? And are the 9 filled No. 124 PDFs (sample
  label filled) rules documents too?
- **Q5 (lower).** Starting α per question (compiler design O2); the author would propose 0.1.

## 4. Unverified or assumed

- FIBO checklist separates contracts from rules on these PDFs — read, not measured.
- Jev is unreachable from iladub's `baml_src/` (builder: no Jev client there; Haiku and Sonnet exist) —
  not re-measured by the author.
- The scan measurement covers `gafta-48-1` only; the other scans are assumed alike.

## 6. Owner answers (appended 2026-11-02, same session)

- **Q2: scans are deferred to phase 2**, when OCR is done; once lines exist, the router logic is the
  same. The bar for this loop is restated without the 12 scan PDFs (m3's scan half: see the spec fold-in).
- **Q4: yes, the router may assert "not a contract" when the document actually is not one.** Author's
  reading, to confirm in the fold-in: asserted from positive evidence of another type (e.g. a rules
  document), never from a missing party (open world, spec § 3).
- **Q1: to be rediscussed.** **Q3: the owner did not follow it**; re-explained in chat.
