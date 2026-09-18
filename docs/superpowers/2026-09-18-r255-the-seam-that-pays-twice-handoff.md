# Handoff — the seam pays twice, and the second reading is not the wasted one

**Serves:** maintenance — [[R255]] is named by no `prog:blockedBy`, and neither are [[R256]] or
[[R257]]. **This is the first dated doc since 2026-09-17 to declare `maintenance` rather than
`etkl:02`, and § 2 records why that matters.**

**Topic:** [[R255]]'s mechanism is explained — the row's *"only the second one's result reaches the
graph"* is **REFUTED**: reading #1 reaches the graph through continuation recognition, because
`Band.unshown` feeds the header/body split recognition's evidence is built from. A **third**
reading exists on section-repaired pages, and it is the one an adoption is decided on. Nothing in
`src/`, `vocab/`, `baml_src/` or `tests/` changed.

**Date:** 2026-09-18. **Branch:** `r255-the-seam-that-pays-twice`, cut from `main` at `497156d`.

**Doc impact: none.**

**Written at an estimated ~70k working tokens** (session total ≈ 117k against a ≈ 46k baseline) —
**over the 50K originating floor**, read off the session rather than from plimslop's log. Part 5 is
graded per action below, which is what CLAUDE.md requires of a handoff authored over it.

---

## 5. The next concrete action

*(Part 5 first, per CLAUDE.md § "The handoff's next action is TYPED".)*

### 5a. **ASSERTED** — instrument the two readings and see whether they disagree. Mechanical.

**The action:** with `BAML_LIVE=1`, compile `ag-trade/graincorp-capacity-2026-08-04.pdf` once, with
a print at both `page_bands` call sites (`document.py:1437`, `compile.py:875`) recording, per
gridded band, the `unshown` set it attached — and a print of the `header_body_split` value
`leaf_block` derives in the recognition pass. **Tee the whole run to a file and grep the file**
(the previous loop lost two `note` fields and a traceback to a live `grep`; its handoff § 4.5).

Why it is asserted: the outcome is unknown but *doing it* is the work, and it is the one fact every
remedy's **urgency** depends on. § 5 of the evidence states plainly that the two readings
disagreeing at that seam is a **mechanism, never an observed effect** — the path is live and the
input is consumed, and no run has shown the split actually moving. If they never disagree on this
document, R255 is a cost row; if they do, it is a coherence row, and the remedy's shape changes.

### 5b. **PROPOSED** — the remedy fork, and the seam's own contract is the constraint

**The prediction:** of the four visible remedies, **only a per-page memo of the reading survives
the seam's contract**, and the other three weaken it.

`page_bands`' docstring (`compile.py:380-384`) says why the function exists: *"continuation
recognition must read the SAME bands the compile reads, or the recognized band and the compiled
table are two different things and the chain links the wrong URIs."* Grade each candidate against
that sentence, not against its cost:

| candidate | what it does to the contract |
| --- | --- |
| a flag suppressing the ask on the recognition call | **breaks it** — recognition would read bands the compile does not, at the exact field that moves the split |
| read `unshown` out of the recognition path | **breaks it** the same way, one layer down |
| pass the band list into `compile_tables` | preserves it for pass 1; says nothing about the pass-2 call at `document.py:1538` |
| memoise the reading per `(pdf_path, page_number)` | **strengthens** it — recognition and compile read the same *objects*, not merely the same construction path |

**Why it is PROPOSED and not asserted:** the memo's key is the open question. The pass-2 compile
passes `section_repair_bands=candidates`, so its partition is not the same input, and whether a
reading taken on partition A may be reused on partition B is a **design decision about what an
address means across a re-partition** — precisely the question `merge_bands`' docstring already
answers for run-merges (addresses are offset, exact integer arithmetic) and does *not* answer for
section repair. **Do not implement a cache before answering it.** A memo keyed too loosely reuses
an address in a row space that a different partition renumbers, which is the defect
`merge_bands` exists to prevent.

**What NOT to do.** Do not delete either call site. Both are load-bearing and both are documented
as such; the duplication was free for as long as `page_bands` was pure geometry, and what changed
is that [[R213]] put a **paid, non-deterministic** call inside a seam whose whole purpose was that
there be exactly one of it.

### 5c. **After R255** — the arc, and it has not moved in five loops

The maintainer's direction, taken 2026-09-18: close R255, then return to **`etkl:05` (bfs) through
[[R44]]** — reach 5, the highest in `arc-dependency-landscape.md` § 3, and its instruments
(`scripts/r238_label_identity.py`, `r239_*.py`) are already built. R44's own triage says its three
escalation reasons have **no shared root cause**, so it is three bounded sub-loops, not one.

**Do not re-open [[R234]] on the strength of its 2026-09-15 "THIS IS THE NEXT SUBJECT" ruling.** It
is population zero (0/191 bands), one specimen, and its own row records the remedy as moot unless a
second specimen lands.

---

## 1. Where the primaries are

| | |
| --- | --- |
| evidence | `docs/superpowers/2026-09-18-r255-the-seam-that-pays-twice-evidence.md` — the four-hop chain with a site per hop, § 2 |
| the rows | [[R255]] **amended** (its second clause refuted), [[R256]] and [[R257]] **raised** — `residues.md` + `residues-open.md` |
| the seam | `src/iladub/etkl/compile.py:377-507` (`page_bands`, and the R213 block at `:479-507`) |
| the two callers | `src/iladub/etkl/document.py:1437` (recognition), `src/iladub/etkl/compile.py:875` (compile), `src/iladub/etkl/document.py:1538` (the pass-2 third reading) |
| the consumption hop | `src/iladub/etkl/headers.py:111-112` → `celltype.grid_evidence` → `vocab/queries/header-body-split.rq` |
| prior loop | `docs/superpowers/2026-09-18-the-grain-of-the-ask-handoff.md` — its § 5a is still unrun and still worth running |

## 2. What was decided, and where it is recorded

- **R255 stays OPEN, amended.** Its cost claim holds; its *"only the second reaches the graph"*
  claim is refuted in the row itself.
- **[[R256]] raised** — the section-repair adoption compares two *different* readings of the same
  page, so under `BAML_LIVE` it is not a controlled A/B. Recorded in the register.
- **[[R257]] raised** — **13 dated docs from 2026-09-17/18 declare `Serves: prog:criterion:etkl:02`,
  and that criterion has carried `prog:met true ; prog:metOn "2026-09-13"` since 2026-09-13.** Five
  loops' declared purpose was a met criterion, and none of [[R250]]–[[R255]] is named by any
  `prog:blockedBy`, so the whole thread gates nothing on the arc. The `Serves:` strip checks that
  the IRI exists in the manifest; it does not check that the criterion is unmet, which is why the
  drift was invisible. **No lint is proposed in this loop** — see the row for why that is a
  judgment and not an omission.
- **No remedy for R255 is chosen**, deliberately. It is a design decision and this session is over
  the originating floor.

## 3. What is UNVERIFIED, and must not be asserted

- **That readings #1 and #2 have ever actually disagreed.** Mechanism, not observation. This is
  § 5a's whole subject.
- **That the two partitions are always identical.** Measured identical on one document only, and
  the recognition call and the compile call do not pass the same arguments.
- **Every frequency and cost figure.** No live run was made in this loop.
- **[[R251]]–[[R254]] are untouched.**
- **The previous loop's § 5a and § 5b are untouched** — regime (iii)'s cause is still unestablished
  and the rephrased ask is still uncommitted at n = 2.

## 4. Traps this loop paid for

1. **A `grep` whose hits all look like one module family is not an enumeration.** The draft of § 2
   asserted that the recognition pass provably never consumes `unshown`, because every `.unshown`
   hit read as a compile-path module. `headers.py:112` is on **both** paths, and only opening the
   file said so. The claim was load-bearing for the whole finding and was one hop from shipping
   inverted — `enumerating-before-claiming` exists for exactly this and was not run.
2. **A residue row can be wrong in its second clause while right in its first**, and the first
   clause is the one that gets quoted. R255's cost claim was repeated in a handoff before its
   mechanism was ever read.
3. **The `Serves:` line is checked for existence, not for metness** — see [[R257]]. A conformant
   declaration pointed five loops at finished work.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
