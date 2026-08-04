---
title: Corpus harness — fetch, pin, measure, adjudicate
type: concept
sources:
  - docs/superpowers/specs/2026-08-02-real-document-generalization-design.md
  - tests/test_corpus.py
  - tests/corpus-manifest.ttl
  - tests/corpus-shapes.ttl
  - scripts/fetch_corpus.py
related: ["[[table-holon-compilation]]"]
confidence: high
updated: 2026-08-04
---

# Corpus harness — fetch, pin, measure, adjudicate

Where earlier loops read synthetic fixtures and one real document (the GrainCorp
shipping stem), the corpus harness (spec 2026-08-02 §4–§5) makes a small battery of
**real, pinned** documents a permanent part of the suite — the mechanism by which
"does this generalize to a real document" becomes a repeatable measurement instead
of a one-off campaign.

**The tracked manifest is the single oracle.** `tests/corpus-manifest.ttl` (a
repo-internal `cor:` namespace, not published) lists one `cor:Document` per corpus
document: its file path under gitignored `corpus/`, its source URL, family (`ag-trade`
/ `gov-stats` / `financial` / `health`), series name, and an **expected verdict**.
`tests/corpus-shapes.ttl` is a closed-world SHACL membrane over that register — it
guards the register's own integrity (e.g. `cor:CompilesAbove` requires a
`cor:scoreFloor`, any adjudicated verdict requires a pinned `cor:sha256` and a
recorded `cor:adjudication`) before a multi-minute compile ever trusts it. This is
the closed-world constraint half of the §8 gate, applied to the register rather than
to a reading decision: the membrane validates what may enter the battery, it derives
nothing about the documents themselves.

## Fetch → pin

`scripts/fetch_corpus.py` (justified PROCEDURAL — network, file I/O, checksum,
irreducible to AXIOM/NEURAL) downloads absent documents into gitignored `corpus/`
using a browser `User-Agent` (institutional CDNs/WAFs 403 bare `Python-urllib`) and
verifies each against its pinned `cor:sha256`. A **first fetch** of a fresh manifest
entry (no `cor:sha256` yet) keeps the file and **prints** the facts a human needs to
pin it — sha256, producer, page count, fetch date — but never writes them back. Pinning
the entry is a **deliberate, reviewed manifest edit**, not something the fetcher or the
battery ever does on its own. A later checksum **mismatch** (the URL now serves a
different edition) is reported and the file removed; the manifest is left untouched
until a human decides whether to re-pin the new edition.

## Measure

`tests/test_corpus.py` is the manifest-driven battery (pytest marker `corpus`,
excluded from the default run). For every manifest document present in `corpus/`, it
compiles through the public `compile_document` API (plus `ground_document` where the
manifest declares a contract) and asserts the manifest's expected verdict:

- **`cor:CompilesAbove`** — the document's score must be at or above the entry's
  `cor:scoreFloor`, and at least one region must assert.
- **`cor:SemanticEscalation`** — at least one region must escalate (the entry's
  `cor:ambiguity` names why, in prose).
- **`cor:Unadjudicated`** — no verdict is asserted; the gate is simply that
  `compile_document` returns **at all** — never crashes, never hangs. Whatever the
  compile prints (score, per-region verdicts, escalation reasons, wall time) is
  **adjudication evidence**, not a pass/fail claim by the test itself.

There is deliberately no `cor:Hold` or similar "parked" verdict: a document is either
adjudicated to a specific expectation (`CompilesAbove`/`SemanticEscalation`, both
requiring a pinned edition and a recorded `cor:adjudication`) or it is
`cor:Unadjudicated` and simply measured. Absent documents (not yet fetched, or
unpinned) **skip visibly** — `require_pinned_edition` raises `pytest.skip` with the
reason, and `test_corpus_coverage_report` prints an explicit `N/M present` count so a
partially-populated corpus is never silently mistaken for a clean run. An **edition
drift** (on-disk file no longer matches the pinned sha256) **fails rather than
skips** — measuring an unpinned edition would silently decouple the register from the
evidence.

## The budget's derivation-and-adjudication discipline

`BUDGET_S` in `tests/test_corpus.py` is **test infrastructure, not a tuned semantic
constant** (the same class as `tests/etkl/test_derivation_perf.py`'s budgets) — a
`SIGALRM` wall-clock ceiling per document compile, because under the fluent-reader
invariant a hang is a harness defect that must become a visible failure, not a stall.
Its value is **derived and re-derived, in the open**: it started this loop stale at
222 s (loop N's 180 s whole-stem compile + ~23% headroom, documented at the constant
itself), and the full battery run (2026-08-04) measured 254.1 s standalone / 270 s
in-battery / 232 s in the final run — all close to the ceiling. **François adjudicated
it to 320 s** at loop close. The discipline that makes this safe: a measurement that
disagrees with an expectation is *reported*, never silently absorbed by raising the
budget or lowering a floor inside the same loop that measured it.

## The never-auto-update rule

Nothing in this harness ever writes `tests/corpus-manifest.ttl` on its own — not the
fetcher (it prints pin values, never writes them), not the battery (it asserts against
the manifest, never edits it), not the loop that runs the battery. Every verdict
change — a fresh `cor:Unadjudicated` seed being promoted to `cor:CompilesAbove` with a
floor, or an escalation reason being named — is a human's reviewed commit. This is the
corpus register's instance of the repo-wide promotion discipline (assert only what you
can ground; a proposition becomes an assertion only via an accountable decision):
the battery's printed measurements are the evidence a human adjudicates over, exactly
as a `CandidateConcept` is evidence a `PromotionDecision` acts on.

## How a loop closes a corpus defect

Spec §5 is explicit: **each defect the battery reveals becomes its own loop** — the
harness's job is to surface real-document generalization gaps at low, repeatable cost,
not to fix them inline. A defect loop's definition of done is a **battery re-run**: the
document that used to crash, escalate on a non-semantic reason, or score below its
adjudicated floor must now measure differently, with the new measurement re-adjudicated
in a reviewed manifest commit — the same "re-run the battery, read the printed
evidence" loop this page describes, applied recursively to whatever the harness
surfaced. The 2026-08-04 full-battery run measured five such open defects this way
(residues R41–R45 in `docs/superpowers/residues.md`): an `IndexError` crash on a
financial-statements document (R41), a house-style merged-header escalation on an
Excel-print shipping stem (R42), and three gov-stats/health generalization gaps
(R43–R45) — each named by its measured symptom and location, deferred to its own loop,
never patched inline here.
