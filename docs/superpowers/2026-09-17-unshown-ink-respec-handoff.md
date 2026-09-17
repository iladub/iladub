# Handoff — the unshown-ink spec is respecced: two new findings change the remedy, now write the plan

**Topic:** [[R213]]'s spec was respecced against the review's measured seams (review handoff §§ 5a–5c).
The term, the membrane and the carriage now attach to `tab:EntryCell`; the worker's ask is the
reader's, with three refusals. **Two measurements taken for the respec change what the plan must
build** — one of them blocks the review's own prescribed remedy. The next session writes the plan.

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-17. **Doc impact: none.** (The spec's own `increment` is unchanged and now also
covers one amended shipped shape — see 5b.)

Written with part 5 first, per CLAUDE.md § "The handoff's next action is TYPED". **plimslop reports
no measured turn for this project this session**, so the working-token figure is absent rather than
withheld, as in the two predecessor handoffs.

## 5. The next concrete action

### 5a. ASSERTED — write the plan against spec **§ 8**, and against § 8 only

Mechanical in its scope, not in its content: § 8 is the governing text and §§ 1.4, 2.3, 2.4, 3.1 and
4.3 above it are **superseded in place by the append** (they keep their lines — Evidence is
append-only — and their banner markers say so). A plan written from the body without § 8 rebuilds
every refuted attachment.

What the plan must carry, each already stated once in § 8 and to be **cited, not re-derived**
(plan rule 6):

- the term split across two graphs (§ 8.2), the membrane on `tab:EntryCell` (§ 8.5), both crossings
  (§ 8.6), the worker's contract with its three refusals (§ 8.7);
- **seven oracles**: O1–O5 unchanged from § 5, plus **O6** (the widened guard still refuses a cell
  carrying neither text) and **O7** (per region, populated grid cells == EntryCells, or the carriage
  refuses) — § 8.8;
- a falsification block per task (plan rule 4).

### 5b. ASSERTED — the plan's FIRST task is the `tab:WrappedCellShape` amendment, because nothing else can land without it

**RS1, measured, and it blocks the design as the review left it.** Spec § 8.2 empties the persisted
cell's `tab:cellText` so that `feed.py:254-255`'s existing `is_blank` `continue` refuses the
grounding with no new code. A cell in that shape is **refused today**:

```
$ ./.venv/bin/python scripts/unshown_ink_seam_census.py --shape
   conforms: False   (c1 = unshown, c2 = ordinary ink)
  Source Shape: tab:WrappedCellShape
  Message: A tab:Cell with a hasBBox must have non-empty cellText (drop-continuation guard).
```

All 406 gcap `tab:EntryCell`s carry a bbox, so every unshown cell hits it. The remedy is in § 8.3:
widen the guard's proof-of-carriage to *non-empty `tab:cellText` **or** non-empty `tab:unshownText`* —
**not** an exemption for cells carrying the property, which would pass a cell whose `unshownText` is
empty. It is a published shipped shape, so it ships with a conforming example and a negative one.

### 5c. PROPOSED — § 8.5's clause 2 may have no SHACL subject; RUN the provenance probe before writing it

**This is a prediction and it must be run first.** If it is wrong, the shape the plan writes has no
subject and nothing will ever fire it — the R213 failure mode wearing a green suite.

The claim to test: *does a grounded node's provenance chain reach the `tab:EntryCell` it was read
from?* What is **read, not measured**: `feed.py:257-258` takes the cell's `prov:wasDerivedFrom`
**object** (a bbox-keyed page IRI, e.g. `…#p0-677-255`) and keeps only its fragment as
`SurfaceConcept.region`; `ground.py:161-163` mints `urn:iladub:region:<that fragment>` and links the
node with `iladub:fromRegion`. So the join back to the cell, if it exists at all, is **a string
transformation between two IRI schemes**, and it was seen at one site only — the candidate path.

Three outcomes, and the plan takes a different shape under each:

1. **The chain reaches the cell** (directly or through the region-string join) → clause 2 is a SHACL
   shape as § 8.5 writes it.
2. **It reaches only a region** → clause 2 is a **producer-side guard** at the site that reads the
   cell (CLAUDE.md § Producer-side guards vs the membrane; R102 is the case), and the membrane keeps
   clause 1 only. Say so in the plan; do not invent a path.
3. **The join is a string rewrite** → it is constructible and fragile, and the plan must decide it
   deliberately rather than discover it in a shape that silently matches nothing.

Cost to run: one compiled gcap graph plus one query. Minutes, not a loop.

### 5d. ASSERTED — the plan's first MEASUREMENT is the `tab:cellText` consumer census

§ 8.9 item 5: emptying `tab:cellText` is a suppression, and its consumer census has not been taken.
Three readers are named (`feed.py:246`, `denormalization.py:163`, `recipe.py:91`); the census must
cover **every** reader in `src/`, `vocab/queries/` and `vocab/shapes/`. This is an
`enumerating-before-claiming` job — the claim *"only these three read it"* is exactly the universal
the skill exists for — and it is load-bearing for O3's bit-identical null on six documents.

### 5e. ASSERTED — what must NOT be redone

- **Do not re-run O1 or O2 to establish anything.** Both passed blind and are recorded; re-run O2
  only as a regression against § 8.7's changed ask.
- **Do not re-measure** region count (122), crop cost (0.05–0.54 s), crop legibility, the `tab:Blank`
  census, RF2's reach figures, or the address identity — every one is in the review or § 8, and
  `scripts/unshown_ink_seam_census.py` re-runs all of them (`--regions --blank --grain --graph
  --shape --address`).
- **Do not re-open the term or the fork** (`tab:UnshownInk`, a `tab:CellDatatype` that abstains) and
  do not re-litigate R213 option (c).
- **Do not write `tab:cellDatatype` on a persisted cell** — § 8.2's measured hazard: `rdfs:domain
  tab:GridCell` (`tab.ttl:273`) under `inference="rdfs"` infers the cell into the transient class.
  R19 is the same mechanism on the same vocabulary.
- **Do not write any shape over `tab:GridCell`.** It is 0 in the compiled graph.
- **Do not carry a colour into `src/`.**
- **Do not assume gcap's address identity generalises** (§ 8.4) and **do not build [[R250]]'s
  derivation**.

## 1. Where the primaries are

- **The governing text:** the spec's **§ 8**, appended to
  `docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md`. §§ 8.1–8.9 map
  one-to-one onto the sections they replace or amend.
- **The review that caused it:** `docs/superpowers/2026-09-17-unshown-ink-spec-review.md`
  (RF1–RF8 and the two blind runs).
- **The instrument, now six modes:** `scripts/unshown_ink_seam_census.py`
  `--regions | --blank | --grain | --graph <pdf> | --shape | --address`. The last two are new and
  carry RS1 and RS2.
- **The rows:** [[R213]] (amended three times today) and [[R251]].
- **The seams, all measured:** `feed.py:246-258` (the assertion site and the provenance question),
  `celltype.is_blank` (`celltype.py:67-82`), `headers._grid_cells` (`headers.py:66-81`),
  `grid_evidence` (`celltype.py:138-160`), the five EntryCell minting sites (`holon.py:154,214,314`
  via `holon.py:41`; `holon.py:628`; `datagrid.py:691`), `tab:WrappedCellShape`
  (`tab-physical-shapes.ttl:26-42`), `tab:cellDatatype` (`tab.ttl:273`).

## 2. What was decided, and where it is recorded

- **The term, its property and the whole membrane move to `tab:EntryCell`**; the datatype stays on
  the transient side because that is where homogeneity is computed. Spec § 8.2, § 8.5; R213's row.
- **The persisted cell's `tab:cellText` is emptied and the transcription moves to
  `tab:unshownText`** — chosen for fail-safe: every consumer that does not know the term gets the
  truthful answer by default, where keeping `"0"` would need a guard per grounding site. § 8.2.
- **`tab:WrappedCellShape` is amended, not exempted** (RS1). § 8.3, O6.
- **The carriage checks the two address spaces agree per region** rather than trusting index
  arithmetic (RS2). § 8.4, § 8.6, O7.
- **The worker's ask is a reader's, enhancement forbidden, with a grid-disagreement abstention and an
  address-only closed output**; the null control is the unpopulated grid position and comes free in
  the reader's answer, with R211's spanning column exempted. § 8.7.
- **Nothing was implemented, and no `src/` file was touched.** This loop appended one spec section,
  added two instrument modes, and amended one register row.

## 3. Unverified or assumed

- **§ 8.5 clause 2's subject is unestablished** — 5c is the probe, and it is the one PROPOSED item
  here.
- **RS2's address identity is empirical**: one region, one document, five minting sites, and
  `datagrid.py:691` keys its IRI off a different counter entirely.
- **The `tab:cellText` consumer census has not been taken** (5d), so O3's bit-identical null on six
  documents is a prediction, not a derivation.
- **`tab:EntryCell` coverage is measured on graincorp-capacity only** (406/406).
- **The enhancement prohibition stays unenforceable from the answer alone**; no control page exists
  on which the reading route and the analysis route diverge.
- **The blind readers are not the shipped worker** — `baml_src/` still holds five text functions and
  no image input.
- **RF5's grain problem and § 7's fourth case are untouched.**

## 4. What this session did

Read the review and its handoff, then measured the two things the respec turns on rather than
transcribing the prescription: validated a hand-built unshown cell against the shipped physical
shapes (RS1, which refuted the prescribed remedy), and compared the grid address space against the
persisted `tab:EntryCell` index space cell by cell on graincorp-capacity (RS2, 406/406 and 110/110 by
set identity). Checked the RDFS-domain hazard on `tab:cellDatatype` before letting the design put a
datatype on the persisted cell. Then appended spec § 8, shipped both measurements as census modes,
and amended R213's row in both register files.
