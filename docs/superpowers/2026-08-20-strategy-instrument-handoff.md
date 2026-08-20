# Handoff — the strategy instrument: the map, and the graph that makes selection strategic

**Topic:** process · **Date:** 2026-08-20 · **Branch:** none yet (start from `main`) ·
**Shape: originating** ·
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
5. **The position is FOUR FRACTIONS, not one integer** (decided after the measurement below). A
   single `stage N/4` asserts that every rung below N is finished, and measured, none of them is:
   the compiler is still under repair while stage-3 vocabulary already exists. `stage 3/4` would
   have to be wrong about three rungs to be right about one. Each rung carries its own
   met/declared count instead, and no "current position" needs to exist at all — which removes the
   question that had no honest answer.
6. **Rendered as BARS** — the maintainer's call, made after the case against them was put: a bar
   reads as a percentage, and met/declared criteria is a *checklist*, not a percentage; rung 2's
   five criteria and rung 3's six are not commensurable. Recorded, not re-litigated. Whether a
   fraction sits beside each bar to keep it legible as a count is the next session's call.

   Two rules the bars must keep, both from the design above: **unknown ≠ zero** (a rung with no
   criteria declared renders `?`, never an empty bar), and **the fill can go DOWN** — if a test a
   criterion points at goes red, the criterion un-meets. A gauge that only ratchets upward is
   measuring authorship, not state.

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

## MEASURED after the design — what is actually on each rung

Delegated inventory, 2026-08-20, same session. Every figure from a command.

| rung | measured | reading |
| --- | --- | --- |
| **1 · `etkl` compiler** | `src/iladub/etkl/` 10,807 LOC over 43 modules; `tests/etkl/` 18,073 LOC. Corpus = **7** documents, of which **1** carries a `cor:scoreFloor` and an adjudicated verdict (graincorp-stem, floor 0.95, achieved 0.9655 — recorded in `cor:rationale` PROSE, not as machine-readable data). The other 6 are `cor:Unadjudicated` | built at scale, **proven on one document of seven** |
| **2 · decidability** | `dec.ttl` 219 LOC / 7 named classes / 18 obj props; `risk.ttl` 112 / 4; 11 `sh:NodeShape` across dec-, risk-, governance-, escalation-shapes; ~1,194 LOC of worked examples with negatives. The core invariant IS enforced — `iladub:GroundedNodeShape` (`vocab/shapes/iladub-shapes.ttl:38`), wired at `compile.py:421` | **the most complete rung.** Caveat: R99 — `NoLeakShape` can never fire where it is wired |
| **3 · holon reframe** | `vocab/ontology/etkl-holons.ttl` **exists**, 103 LOC, 7 classes (`RawDocumentHolon`, `CleanDocumentHolon`, `SemanticHolon`, `AlignmentHolon`, `GroundingPortal`, `MembraneHealth`, `DocumentHolon`) + `throughPortal`/`reconciles`; 4 `*-hga-align.ttl` = 198 LOC; `iladub-hga-shapes.ttl` 40; `tests/test_hga_alignment.py` 76, asserting `"w3id.org/holon" not in text` | **341 LOC of holon fabric**, far past "not started" |
| **4 · active substrate** | 34 LOC in `src/iladub/fluree/` (two JSON-LD policy templates) + `writegate.py` 70, tested by 229. **Zero** server/runtime code (no fastapi/flask/uvicorn/asgi/Dockerfile anywhere), **zero** event-ledger implementation — the two files matching "event ledger" are both prose. `membrane.py` runs **inside the compiler process**, not at a write endpoint | **not started.** The one honest `0` |

### Two findings that outrank the position

1. **`CLAUDE.md:452-456` is STALE.** It says the holonic ontology work is *"not yet started"*.
   Measured: 341 LOC exist and `docs/holonic-interaction.md` calls itself *"partially shipped"*,
   naming exactly **two** remaining items. **A Contract-class file asserting a blank where the disk
   has content.** Fixing it is not this loop's job but somebody's.
2. **THE ARC OMITS MOST OF THE REPO.** The `tab:` table-reading work measures **28,554 LOC** —
   **64%** of all `src/` Python, **82%** of all `vocab/ontology` + `vocab/shapes` lines, **72%** of
   all test LOC. The four stages do not name it. So `stage ?/4` was not only missing state, it was
   measuring against a map that omits two-thirds of the territory. **This is the likeliest single
   cause of "I have no notion how complete the epic is": the epic actually being worked is not on
   the map.** Whether table-reading becomes a fifth rung, or the arc is re-cut, is a decision about
   what iladub *is* — deliberately left to the maintainer in a fresh session.

### The denominators mostly already exist, in prose

This retires the loop's biggest unknown. Three of four rungs already carry a countable criterion
set that **predates any claim about it** — which is the independence `prog:declaredOn <
prog:reachedOn` was invented to manufacture, obtained for free:

- **rung 1** — `tests/corpus-manifest.ttl`: documents with a pinned floor and an adjudicated
  verdict. **1/7.**
- **rung 3** — `docs/holonic-interaction.md` § *Planned work (not done yet)*: exactly two items
  (a membrane-health check computing `etkl:membraneHealth`; a full raw→clean traversal example).
  **0/2 remaining.**
- **rung 4** — `docs/narrative/scope-evolution.md` §4 names its own three requirements: immutable
  event ledger, validation-at-write, in-engine policy. **0/3.**
- **rung 2** has no declared denominator anywhere. The most complete rung is the one that cannot
  yet say so.

So the work is **lifting existing prose into a countable form**, not inventing criteria. The
authoring risk the design worried about is much smaller than assumed.

## Unverified or assumed

- ~~**That the four rungs can be given honest criteria at all.**~~ **LARGELY ANSWERED** by the
  inventory above: three of four rungs already carry a countable criterion set in prose. **Rung 2
  remains open** — it has no declared denominator anywhere, and it is the rung whose completeness is
  least in doubt, so nobody ever wrote down what would count.
- **That `prog:declaredOn < prog:reachedOn` is satisfiable retroactively.** Every rung already
  reached was reached before any criterion was declared, so the clause either needs a grandfathering
  rule or the early rungs are adjudicated rather than derived. Not thought through.
- **That the cockpit can compute the frontier cheaply enough.** Asserted from the shape of the data
  (a few file reads and regexes), never timed. The 180s cache and the 30ms contract are the budget.
- ~~**That the arc's four stages are the right denominator.**~~ **REFUTED, measured:** they are not.
  See finding 2 above — 64/82/72% of the repo sits in work the arc does not name. What replaces or
  extends the arc is undecided and is the maintainer's call.
- **The register economics.** This loop closes **no** existing residue row. It repairs the two
  defects in §Measured (1) and (2), which is a real but small offset against a rate measured today
  at 21/94 closed and 73 open.
- Whether the state TTL belongs at `docs/narrative/arc-state.ttl` (next to the prose it gives state
  to, visible) or under `tests/` (where `cor:` lives). Unresolved; a stray `.ttl` under `docs/` may
  need an `exclude_docs` entry in `mkdocs.yml` — unchecked.

## The next concrete action

In a **fresh session** — the previous "test whether rung 3/4 criteria can be written" is done, and
the answer was yes. What replaces it is a decision, not a measurement:

**Does table-reading become a fifth rung, or is the arc re-cut?** Two-thirds of the repo is not on
the map, and every fraction the gauge renders is measured against that map. Decide this before
writing the spec — the criteria, the shapes and the bars all inherit from it. Then lift the three
existing prose denominators (corpus manifest, holonic-interaction's two items, scope-evolution §4's
three requirements) into countable form, and write rung 2's, which nobody has ever written.
