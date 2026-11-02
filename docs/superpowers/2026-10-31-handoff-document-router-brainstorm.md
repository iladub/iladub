# Handoff 2026-10-31: the contract:01 rescope became a document router plus a synthetic contract set

**Serves:** maintenance — no criterion yet; this brainstorm decides what contract:01 becomes.

## 5. Next concrete action (written first; typed)

**Proposed** (the brainstorm is not finished; the owner has approved no written design): in a fresh
session, resume superpowers:brainstorming on **project 1, the synthetic contract set**, from the
owner answers in § 3. Play back the whole set as one chunk (forms, flavours, truth, storage, the
charter party), get the owner's corrections, then write
`docs/superpowers/specs/YYYY-MM-DD-synthetic-contract-set-design.md` and run the builder check.
Projects 2 (router) and 3 (contract:01) are brainstormed after it, one at a time.

What could refute this: the owner may want the router (project 2) designed before the set, or both
in one spec. Ask before writing; it costs one message.

## 1. Goal

Rescope contract:01 under decision 18 (nothing from hdc-contract; domain-agnostic). The brainstorm
widened it into three projects, in this order: the synthetic contract set, a document router, and
then contract compiling.

## 2. Where the primaries are

- `docs/superpowers/specs/2026-10-30-hdc-first-contract-compiler-design.md` § 2 decisions 16–18 and
  the "Consequence for contract:01" paragraph; § 11 O4 (GAFTA licence) and O5 (second domain).
- `docs/superpowers/specs/2026-10-30-contract-rung-design.md`: the contract:01 spec being rescoped.
- `docs/superpowers/2026-10-30-handoff-finish-contract-01-spec.md`: the handoff this one supersedes.
- GAFTA forms: the index at https://www.gafta.com/contracts, paged with `?page=2..6` (90 PDF links
  across pages 1–6). The survey copies were downloaded to a session scratchpad and **are gone**;
  fetch them again.
- USDA Food for Progress Charter Party (13 pp., OMB ICR 201404-0551-002):
  https://omb.report/icr/201404-0551-002/doc/47577601.pdf
- MSC DRYVOY/TANKVOY 2026 (https://www.msc.usff.navy.mil/Portals/43/Procurement/docs/): **deferred**
  by the owner. curl gets `Access Denied`; a browser download would be needed.

## 3. What was decided, and where

All of these are owner answers given in chat on 2026-10-31. **They are recorded nowhere but this
file**, so each is reversible until a design records it.

1. **A document router comes before the compilers.** It decides the document type and routes the
   document. The granularity of types is part of that decision.
2. **Mixed documents are split** and each part goes to its own compiler.
3. **The router proposes new types and the owner admits them.**
4. **First proof: route a GAFTA form and its tables correctly.**
5. **The examples are filled synthetically.** Real contracts come later.
6. **There are three flavours of each filled contract:** a fill inside the PDF, like a form; a Word
   document exported to PDF with the values inline; and **simulated** handwriting on the printed
   form, scanned.
7. **The second domain is a charter party,** and the **USDA charter party alone** for now. DRYVOY and
   BIMCO are deferred.

My calls (not the owner's): every playback chunk in the conversation marked these as mine or as guesses.
- PDFs stay out of `corpus/`, because the baseline snapshot sweeps it.
- Fills are written onto the real templates rather than retyped.
- The generator writes the truth and keeps it out of the router's sight.
- Agreement between the three flavours of one contract is a second oracle.
- Routing and part-splitting are NEURAL, disposed by an oracle.
- The type tree aligns its upper levels to DoCO/FaBiO.
- Simulated handwriting does not prove real scans (an anti-goal).
- The starting forms are GAFTA 48, 79B and 124.

## 4. Unverified or assumed

**The measurements** were run from the session scratchpad, with pdfplumber `find_tables()` and the
threshold rows ≥ 2 and cols ≥ 2. To reproduce, re-fetch the forms and re-run.
- Only 3 of the 90 GAFTA PDFs have ruled tables:
  - `124_2026` (Sampling Rules), p6, 7×6: a real metric table;
  - `79b_2026`, p1–2: a blank quality table **nested inside clause 6**;
  - `76_2026` (an addendum), p3, 2×2.
- Unruled tables were not searched for beyond a `Table|Schedule|Annex` line grep, which hit only
  No. 124.

**Not checked:**
- **The USDA charter party is public domain.** That rests on the US federal works rule only; the
  OMB filing is from 2014 and may be outdated.
- **GENCON's Part I box grid.** This came from memory and was not checked.
- **DRYVOY opens with an SF 1449 box form.** This came from search snippets only.
- **That "parts nest" and "the blank" is a part type.** Both are my reading of a single form,
  79B p1.
- The session ended 1.04× over the originating floor (logged `handoff`). Playback chunks written
  near the end may be weaker.
