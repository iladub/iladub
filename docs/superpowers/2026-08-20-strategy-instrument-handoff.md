# Handoff — the strategy instrument: the map, and the graph that makes selection strategic

**Date:** 2026-08-20 · **Branch:** none yet (start from `main`) · **Shape: originating** ·
**Status: design decided in conversation, SPEC NOT WRITTEN.**

> Written at 95,341 tokens — 1.9× the originating floor — which is why this is a handoff and the
> spec is the next session's first act. Preflight logged (`handoff`).

## Goal

One line: **give the arc a "you are here", and give the register a dependency predicate**, so the
gauge strip already in the status line stops printing `arc ?/4` and starts naming what to do next.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/2026-08-20-strategy-instrument-brief.md` | the ask in the maintainer's words, and its own § CORRECTION — read it as the origin, not as measurement (three of its figures are corrected below) |
| `scripts/cockpit.py` (215 lines, `e62ad77`) + `tests/test_cockpit.py` | the surface. `arc()` at `:128` is the hole this loop fills; its docstring already says *"When an objectives artifact gains state, teach this to read it."* `residues()` at `:94` carries a measured defect (below) |
| `docs/superpowers/specs/2026-07-31-documentation-governance-design.md` + `tests/docgov_extract.py` (224) + `vocab/queries/docgov-*.rq` (48 total) + `vocab/shapes/doc-governance-shapes.ttl` (148) | **the pattern to copy** for the extractor half. Note: there is NO `dg:` ontology file — the namespace is declared in exactly two places, and the graph is built in memory at test time, never persisted |
| `tests/corpus-manifest.ttl` (115) + `tests/corpus-shapes.ttl` (56) + `tests/test_corpus_manifest.py` | **the opposite pattern**, for the state half: the graph IS the tracked artifact, hand-written, with dated `cor:adjudication` blocks; code validates and never writes it (`docs/wiki/concepts/corpus-harness.md:89-93` states the never-auto-write rule) |
| `docs/narrative/scope-evolution.md` (145 lines) | the four rungs (`### 1..4` under `## The arc`) and the capability ladder at `:106-126` — which has **two** rungs, not four, and mentions no corpus or `tab:` work |
| `docs/superpowers/2026-08-17-loop-split-decision.md` | Loop 1 DONE; Loops 2 (R97–R100) and 3 (R101) untouched. This loop is **not** one of them |

## What was decided, and where that decision is recorded

**All four decisions below are recorded NOWHERE BUT THIS FILE.** They are the maintainer's live
answers in the originating session, not settled repo policy — reversible, and worth re-asking if
the spec finds them awkward.

1. **The ask is all three — map, then trend, then selection — in that order**, built as one thin
   vertical slice rather than three layers. Maintainer's choice, asked directly.
2. **The surface is the status line**, i.e. the cockpit strip that already exists. (The maintainer
   chose "at session start, automatically"; the cockpit is strictly better than a session-start
   block — always visible, and it costs no context. Treat the answer as satisfied, not overridden.)
3. **A rung gets its state by ASSERT + MEMBRANE**, not by derivation alone and not by adjudication
   alone: a tracked TTL carries the asserted position, dated, with rationale; a SPARQL derivation
   over evidence must support it or the membrane refuses. Chosen over "derived only" (says nothing
   about stages 3–4, where there is no crisp oracle) and "adjudicated only" (no denominator, which
   is half the original complaint).
4. **Slice 1 = map + dependency edges.** The persisted tally history was explicitly deferred (it
   accrues only over future loops and shows nothing today).

### The design as it stood at the end of the session

Not a spec — the shape a spec would have to defend or replace:

- **`prog:` is repo-internal and unpublished**, exactly as `dg:` and `cor:` are. Shapes in
  `vocab/shapes/`, derivations in `vocab/queries/`, state in a tracked TTL the maintainer edits.
- **The non-circularity device, and the part most worth keeping:** the same hand authors both the
  criteria and the position, so they are not independent by construction. The membrane fixes it
  with dates — a rung's criteria carry `prog:declaredOn`, which **must precede** its `prog:reachedOn`.
  *You must say what done means before you may claim it.* Without that clause the instrument is a
  mirror. **This is asserted, not tested** — nobody has checked that the four rungs can be given
  criteria that predate any honest claim to have reached them.
- **A criterion is a pointer to an oracle that already exists and is already green** — an artifact
  path plus a test node id. "Met" is evidence-positive and monotone (open-world derivation, CLAUDE.md
  §8's AXIOM/derivation form). Nothing is inferred from absence.
- **The load-bearing edge is residue → criterion → rung**, not only residue → residue. That is what
  makes selection *strategic* rather than adjacency: closing R99 matters because it unblocks a
  criterion of the current rung, and a query can say so. Residue→residue edges (6 of them, measured)
  become a structured field in the full rows; criterion→residue edges are authored in the state TTL.
- **SPARQL is the authority; the cockpit is a fast second reader; a test pins them equal.** The
  strip must not touch rdflib (its performance contract), so it recomputes position and frontier
  from cheap file reads — and an agreement test makes drift between the two readers a failure.
  *That test would have caught the `residues()` defect below on the day it shipped.*
- Rendered target: `arc 3/4 ·5/8` (rung, and criteria met on that rung — the denominator that was
  missing), and a `▸` slot that names the frontier instead of the newest brief's filename.

**Falsifying oracle, named before the design:** assert a position the criteria do not support →
refuse; point a criterion at an artifact that does not exist → refuse; remove the state file → the
gauge returns to `?`, never a guess (the existing `test_cockpit` honesty test must survive intact).

## Measured this session — three corrections to the brief, and one defect

Two survey agents; every figure below is from a command, not from reading.

1. **`scripts/cockpit.py:94` has a defect, in the commit that introduced it.** The regex
   `R(\d+) \((?:raised at )?(\d+)/(\d+) closed\)` cannot match the struck form `~~R102~~ (18/92
   closed)`, so all **6** snapshots in `residues-closed.md` are invisible. The trend is computed
   against R101 (18/91) and prints `▲2.6`; the newest snapshot, R104 (18/94), gives **▲3.19**.
2. **The register's own prose is stale and self-inconsistent.** `residues.md:40` says *"94 rows, 20
   closed"*; measured today `awk -F'|' '/^\| R[0-9]/ {print $3}' … | sort | uniq -c` → **21 closed,
   73 open**. The convention example at `:25` writes `R97 (17/87 closed)` where the row at
   `residues-open.md:77` reads `(18/87 closed)`. Snapshot coverage: **13 of 94 rows (13.8%)**, all
   of them R92–R104, none of the 81 rows before the convention landed.
3. **"Corpus adjudication history accumulates" is true of the mechanism, misleading about the
   history.** `grep -c "cor:adjudication"` → 4, of which **3 are entries**, all on ONE of 7
   documents, dated 2026-08-02/03/03; `git log -- tests/corpus-manifest.ttl` → 11 commits, all
   2026-08-02..04, untouched for 16 days. The other 6 documents are `cor:Unadjudicated`.
4. **Dependency language: 14 matching lines** (10 open, 4 closed), not the brief's ~8 — but only
   **6 are genuine residue→residue assertions** (`residues-open.md:18` R14→R10, `:54` R61, `:62`
   R71, `:76` R96; `residues-closed.md:11` R4, `:26` R89→R102). The rest is domain vocabulary
   ("header blocks", "requires two occupied columns"). The brief's substantive claim — *no
   predicate, no field, no graph* — **holds**, and the backfill is 6 rows, not 94.
5. **The brief's instrument table, verified item by item:** items 1, 2, 3, 4, 7 confirmed
   non-persisting. Item 8 is wrong — `tests/etkl/test_adoption_ledger.py` computes **no page score**
   and touches no corpus (7 unit tests on synthetic dataclasses); the score gate lives in
   `tests/etkl/test_adoption_document.py` and `tests/test_corpus.py:111`. The table also **omits**
   `tests/test_corpus.py` (the repo's only real corpus-quality number), `test_doc_governance.py`,
   the membrane/closure equivalence batteries, and `test_derivation_perf.py`.
6. **Nothing in the repo maintains a metrics time series.** The only accumulating numeric series is
   the 13 register snapshots (5 days wide). `docs/loops/2026-08-10-…-baseline.md` +
   `2026-08-11-…-close.md` are a hand-written **two-point** before/after and the only pair anyone
   ever wrote.

## Unverified or assumed

- **That the four rungs can be given honest criteria at all.** Rungs 1–2 plausibly (corpus scores,
  membrane conformance, worked examples); **3–4 are vocabulary and standards-alignment work with no
  crisp oracle**, and if criteria there are unwritable the "assert + membrane" decision degrades to
  "adjudicated only" for half the arc. Nobody has tried. **Test this before writing the spec.**
- **That `prog:declaredOn < prog:reachedOn` is satisfiable retroactively.** Every rung already
  reached was reached before any criterion was declared, so the clause either needs a grandfathering
  rule or the early rungs are adjudicated rather than derived. Not thought through.
- **That the cockpit can compute the frontier cheaply enough.** Asserted from the shape of the data
  (a few file reads and regexes), never timed. The 180s cache and the 30ms contract are the budget.
- **That the arc's four stages are the right denominator.** The capability ladder in the same file
  has two rungs and does not mention the `tab:` table-compilation work that R97–R101 concern — so
  the arc may not cover where the work actually is.
- **The register economics.** This loop closes **no** existing residue row. It repairs the two
  defects in §Measured (1) and (2), which is a real but small offset against a rate measured today
  at 21/94 closed and 73 open.
- Whether the state TTL belongs at `docs/narrative/arc-state.ttl` (next to the prose it gives state
  to, visible) or under `tests/` (where `cor:` lives). Unresolved; a stray `.ttl` under `docs/` may
  need an `exclude_docs` entry in `mkdocs.yml` — unchecked.

## The next concrete action

In a **fresh session**: test the first unverified item — **try to write criteria for rungs 3 and 4**
before anything else. If they cannot be written honestly, the design above changes shape, and it is
far cheaper to learn that in an hour than in a spec.
