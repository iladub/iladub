# A superseded firing is disposed by publisher truth — loop B (design, 2026-10-29)

**Serves:** prog:criterion:tab:05 — loop B of two. Loop A (PR #382, `123301e`) made apple p2's
adopted grid scorable: 57 `CORRECT`, every other outcome 0. This loop lets that truth dispose of the
superseded firings on the page it covers, which meets tab:05. It moves tab:02 forward but does not
meet it or tab:09 (§ 7).

**Topic:** tab · **Date:** 2026-10-29

**Doc impact: none.** All new terms go in `vocab/internal/corpus.ttl`, which is declared
*"REPO-INTERNAL, UNPUBLISHED, NOT w3id-REGISTERED"* (its own header, lines 3–7). Nothing outside
`docs/superpowers/` or the tests cites it: `git grep -n vocab/internal -- mkdocs.yml .github
scripts/release_gate.py docs/w3id` → no output. No released meaning changes.

**Status: DRAFT for the maintainer.** The design was approved in chat on 2026-10-29, along with two
rulings made directly (§ 2). Written under the originating floor.

## 1. Goal

`tab:05` reads *"…either it fires on the 7-document corpus and every firing document carries a dated
cor:adjudication naming and disposing of it…"* (`tests/arc-manifest.ttl:1317-1325`). On the corpus,
MATRIX_AMBIGUOUS fires on **one** document. That firing is **superseded**: data-grid adoption
replaced the region. Today it cannot be disposed, and nothing checks it (§ 3).

After this loop:

- an adjudication may dispose of a reason whose firings in its snapshot are **all superseded**, but
  only when that snapshot's publisher truth proves the adopted reading correct on every page where
  the reason fired;
- apple carries one such adjudication, disposing of MATRIX_AMBIGUOUS and REGION_TILING_FAILED;
- the oracle test covers every firing pair, superseded ones included;
- `tab:05` is `prog:met true`.

## 2. Inputs and rulings

- **The disposal rule** (maintainer, 2026-10-29, in chat; recorded in
  `docs/superpowers/2026-10-29-superseded-arm-by-publisher-truth-handoff.md` § 3): a superseded firing
  is disposed only when publisher truth proves the adopted reading correct, never by counting it as
  absent. It is admitted only if the snapshot's truth covers every page carrying such a firing, and
  on each covered page every truth cell is `CORRECT` and no asserted cell is unclaimed. The whole
  truth table must be perfect. That is a sufficient condition, not a tight one, and it needs no
  mapping from regions to truth cells, which would need geometry.
- **This spec supersedes the old ruling.** `specs/2026-10-28-tiling-matrix-roundtrip-design.md`
  § "Ruled 2026-10-28" item 2 ("superseded counts as fires nowhere") is replaced, as loop A's spec
  § 2.1 recorded already. This spec builds the replacement.
- **Ruled 2026-10-29, directly (AskUserQuestion), this session:**
  - **R1:** a truth table's page coverage is read from the **dated snapshot blob**, not from
    `provenance.json` at HEAD. A disposal is append-only (`tests/corpus-shapes.ttl` § D2 comment:
    *"a later repair of the cause must not unseat it"*). A coverage read at HEAD would let a later
    `provenance.json` edit change a past disposal's verdict.
  - **R2:** apple's adjudication disposes of **both** MATRIX_AMBIGUOUS and REGION_TILING_FAILED,
    since both are on the same page with the same proof. The oracle test widens to **live ∪
    superseded** pairs.

## 3. Measured (at `main` `123301e`)

**M1 — firings per corpus snapshot, by reason, verdict and page index.** Command: a census over
`tests/corpus-baseline/*.json` that reads each region whose `reason` fully matches
`[A-Z][A-Z_]*` (the `_CONSTANT` of `tests/corpus_firings.py`) and groups by (reason, verdict).
Results for the 7 `corpus/` documents:

| document | reason | live | superseded |
|---|---|---|---|
| apple | MATRIX_AMBIGUOUS | 0 | 1 (p2) |
| apple | REGION_TILING_FAILED | 0 | 4 (p2) |
| apple | DATAGRID_RESIDUE | 1 (p2) | 0 |
| bfs | BOXHEAD_EXCEEDS_RECORD | 0 | 1 |
| bfs | REGION_TILING_FAILED | 3 | 0 |
| bfs | ROUND_TRIP_FAIL | 0 | 6 |
| bfs | KIND_NOT_SUPPORTED | 2 | 1 |
| bfs | DATAGRID_RESIDUE | 1 | 0 |
| ons | REGION_TILING_FAILED | 0 | 2 |
| ons | ROUND_TRIP_FAIL | 0 | 4 |
| ons | KIND_NOT_SUPPORTED | 1 | 3 |
| ons | DATAGRID_RESIDUE | 2 | 0 |

cbh, graincorp-capacity, graincorp-stem and who-wfa have no constant-reason firings. Fed and
who-covid fire MATRIX_AMBIGUOUS, but they are `held-out/` (`"pdf"` key), so `lift_firings` skips
them (`corpus_firings.py`, `lift_firings`: `if … not pdf.startswith("corpus/"): continue`).

**M2 — a page's index in the blob is its page number.** `scripts/corpus_verdict_snapshot.py:66-72`
(the `refused_texts` docstring): *"A page's number IS its index into `rep.pages`"*. `_snapshot_of`
writes `"pages"` from `rep.pages` in order. Apple's blob has 3 pages, and every apple firing above is
at index 2.

**M3 — the truth block carries outcome counts but no pages.** Apple's committed `"truth"` is
`{"table-1": {"CORRECT": 57, "LOST": 0, "MARKED_LABEL": 0, "MISATTACHED": 0, "MISSING": 0,
"REFUSED": 0, "SPURIOUS": 0, "UNCLAIMED": 0, "WRONG_VALUE": 0}}`. The pages are known when the
block is written, because `truth_block` (`corpus_verdict_snapshot.py`, `truth_block`) calls
`load_truth`, which returns `rows, pages` from `provenance.json` (`src/iladub/truth.py:65-72`). They
are then dropped. Apple's `provenance.json` gives `"pages": [2]`; Fed's gives `[0]`.

**M4 — the shape refuses superseded-only ink.** `cor:DisposalShape` constraint (4)
(`tests/corpus-shapes.ttl`, the message *"…no LIVE cor:firing…"*) requires `cor:live ?n` with
`?n > 0`. It is pinned by `tests/test_corpus_manifest.py`:
- `test_refuses_disposal_of_superseded_only_ink` (:210, bfs ROUND_TRIP_FAIL);
- `test_refuses_disposal_on_the_wrong_document` (:214, ons REGION_TILING_FAILED);
- `test_refuses_disposal_whose_own_reading_holds_no_live_firing` (:264).

**M5 — the oracle test cannot see tab:05's firing.** `test_escalation_reasons_are_adjudicated`
(`tests/test_corpus.py`, ~:240) parametrises over `live_pairs(ADJUDICATED)`, and `live_pairs`
(`tests/corpus_firings.py:180`) keeps only `cor:live > 0`. Apple MATRIX_AMBIGUOUS has live 0, so
**tab:05's own `prog:oracleTest` has no parameter for the only corpus firing of its reason.** If
tab:05 were declared met today, its oracle would pass without checking anything.

**M6 — what reads the truth block.** `git grep -n '"truth"' tests scripts src` (excluding the
baseline JSON) finds:
- `scripts/corpus_verdict_snapshot.py:98`, which writes it;
- `tests/test_ground_truth_floor.py:33-34`;
- `tests/test_ground_truth_score.py:296-297`, which reads `snap["truth"]["table-1"]` as an
  outcome→count map.

**MEASURE in the plan:** whether either reader iterates every key of a table's dict. A new `pages`
key inside it would then be read as an outcome.

**M7 — R62 is this firing.** R62 (`residues-open.md:53`, raised 2026-08-06) records *"one
`MATRIX_AMBIGUOUS` and four `REGION_TILING_FAILED` regions remain on page 0"* of apple. Today's
apple snapshot holds exactly 1 MATRIX_AMBIGUOUS and 4 REGION_TILING_FAILED, all superseded and all at
index 2. The counts match and the page index does not.

**MEASURE in the plan** before acting on R62: why "page 0" became index 2, whether the PDF in
`corpus/` changed or R62 counted pages differently. The `cor:file`/sha history in the manifest
settles it.

## 4. Oracles first

What would show this design wrong, on real input:

- **O1 — vacuous admission.** The new arm admits a superseded-only disposal when:
  - the snapshot has no truth block;
  - a firing page is not covered by any truth table;
  - the covering table has any non-`CORRECT` outcome above 0, `UNCLAIMED` included; or
  - `CORRECT` is 0.

  Each case is a negative test built by **mutating apple's real blob**, not a synthetic one, and each
  must refuse with the arm's own message.
- **O2 — the existing refusals move.** bfs ROUND_TRIP_FAIL and ons REGION_TILING_FAILED have no truth,
  so they must stay refused under (4). The three M4 tests must stay green **unchanged**.
- **O3 — the real disposal.** The apple adjudication, judged against the durable post-regenerate
  apple blob, validates with zero results under `cor:DisposalShape`.
- **O4 — the oracle sees it.** After widening, `test_escalation_reasons_are_adjudicated` has an
  `apple-MATRIX_AMBIGUOUS` parameter. It **passes** with the adjudication present, and it **fails**
  (strict xfail flips) when the adjudication's `cor:disposes "MATRIX_AMBIGUOUS"` is deleted.
- **O5 — the widening is honest.** Exactly the four other superseded-only pairs appear as new strict
  xfail parameters (bfs BOXHEAD_EXCEEDS_RECORD, bfs ROUND_TRIP_FAIL, ons REGION_TILING_FAILED, ons
  ROUND_TRIP_FAIL), and no previously passing parameter changes outcome.
- **O6 — bytes.** After `regenerate`, `git diff -- tests/corpus-baseline/` moves only the `"truth"`
  blocks of apple and Fed (each gains `pages`) and `inputs.json`. Any other change is a defect of
  this loop, because nothing it touches compiles.

## 5. Design

Each part is classified per CLAUDE.md § 8.

### 5.1 The snapshot's truth table records its pages (PROCEDURAL, raw extraction)

`truth_block` writes the `pages` that `load_truth` already returns next to the outcome counts of
each table. The exact JSON shape, nested or sibling, is the plan's to choose, after M6's
measurement. The constraint: a reader of outcome counts must never see `pages` as an outcome. This
step is irreducibly procedural for the same reason the snapshot writer is: it serialises a Python
result to a file. It decides nothing.

### 5.2 The lift carries pages and truth (PROCEDURAL, raw extraction)

The shared counting core (`_count_firings`) gains each firing's set of page indices, read from the
blob's page order (M2). For a snapshot node, `lift_snapshots` emits:

- per firing, one `cor:onPage` per page index carrying a firing of that reason, of any verdict;
- per truth table, a `cor:TruthTable` node attached by `cor:truth`. It carries one `cor:coversPage`
  per page, and one count per outcome, either as a property per outcome or as an outcome/count pair.
  The plan picks one and declares it in `vocab/internal/corpus.ttl`.

The lift judges nothing, which keeps it in the class `corpus_firings.py`'s own docstring already
justifies. Every new term is declared in `vocab/internal/corpus.ttl` with a comment that cites this
spec.

**`lift_firings` (the current-baseline lift on document nodes) also gains `cor:onPage`**, from the
same core, so the two lifts don't drift. It does **not** gain truth: the current baseline plays no
part in a disposal (shape comment, D2).

### 5.3 Constraint (4) gains a superseded arm (AXIOM, constraint, closed world)

Constraint (4) is rewritten as a disjunction. A `cor:disposes ?value` judged against `?snap` is
admitted iff:

- **(4a)** as today: the snapshot holds a firing of `?value` with `cor:live > 0`; **or**
- **(4b)** the snapshot holds a firing of `?value` with `cor:superseded > 0`, **and** for every
  `cor:onPage ?p` of that firing there is a `cor:TruthTable` of `?snap` that:
  - covers `?p`,
  - has `CORRECT > 0`, and
  - has **no** other outcome above 0.

The closure is **holon-scoped**: `NOT EXISTS` ranges over the one snapshot `$this` names, never
over the corpus. It is a membrane over what may count as disposed, and it derives nothing (§ 8:
"never use closed-world to derive"). The existing message stays for a reason that fails both arms,
so O2 holds with the M4 tests untouched. **(4b)'s own refusals get a distinct message** naming the
uncovered or imperfect page, so O1's tests can assert which condition refused.

The value-equality join (`?reason = ?value`) is kept exactly, for the reasons the shape comment
records.

### 5.4 The oracle widens (test code)

`live_pairs` is joined by a `firing_pairs` (live ∪ superseded), from the same graph. The
parametrisation of `test_escalation_reasons_are_adjudicated` moves to it. Undisposed pairs stay
strict xfail, so O5's four new pairs record debt honestly and do not hide it.

### 5.5 Apple's adjudication, and the arc

Apple gets a dated `cor:adjudication` with:
- `cor:disposes "MATRIX_AMBIGUOUS"` and `cor:disposes "REGION_TILING_FAILED"`;
- `cor:judgedAgainst` the post-regenerate apple snapshot (`cor:blob` + `cor:recordedIn`, durable on
  `main`);
- a rationale stating the 57/57 proof.

The snapshot must be durable, so **the adjudication lands after the regenerate commit is on
`main`**. That is either a second PR, or one PR whose `_durable` check passes via `HEAD:<path>`,
which `_durable` admits first. The plan measures which, against `_durable` (`corpus_firings.py`).

Then, in `tests/arc-manifest.ttl`:
- `tab:05` → `prog:met true` with its date, and its `prog:blockedBy "R62"` edge resolved per M7
  (M8 refuses a met criterion that is blocked);
- tab:05's stale `compile.py:830` in its `prog:statement` is corrected in place, per the
  2026-10-28 D4 ruling (R74 spec § "Ruled");
- the stale `# FIRES n` comments (R237) above tab:05 are not touched beyond tab:05's own.

## 6. Tests (shape of the contract; bodies are the plan's)

- `tests/test_corpus_manifest.py`: O1's five refusals over a mutated apple blob, plus O3's
  admission. The M4 three stay **unchanged**: they are the control.
- `tests/test_corpus_firings*.py` (or wherever the lift is tested): `cor:onPage` and
  `cor:TruthTable` facts lifted from apple's real blob.
- `tests/test_corpus.py`: O4 and O5.
- `tests/test_ground_truth_*.py`: still green after 5.1, the pin's form adjusted only if M6 requires
  it.

Every task carries the `## FALSIFICATION` block (CLAUDE.md plan rule 4). The falsification for 5.3
deletes (4b)'s `CORRECT > 0` conjunct and shows the `CORRECT = 0` refusal test failing.

## 7. What is NOT done

- **tab:02 and tab:09 are not met.** bfs fires REGION_TILING_FAILED **live** (3). ons
  REGION_TILING_FAILED, ons and bfs ROUND_TRIP_FAIL, and bfs BOXHEAD_EXCEEDS_RECORD are superseded
  but have no truth set. Each needs a publisher truth set of its own, as a separate loop.
- **No geometry, no region→truth-cell mapping.** The whole-table condition stays sufficient and not
  tight. A page with a perfect truth table and an unrelated superseded region on it is disposed with
  it, which is the accepted cost of R1/R2 and of the 10-29 rule.
- **No live firing is disposed by truth.** Apple's live DATAGRID_RESIDUE stays tab:08's subject. The
  arms do not overlap, because (4b) requires `cor:superseded > 0` and admits nothing about live ink.
- **Held-out documents are not adjudicated.** Fed's MATRIX_AMBIGUOUS is live, and its truth scores
  `CORRECT 0`.
- **No compile change.** Nothing under `src/iladub/etkl/` moves. The regenerate is required only
  because `scripts/corpus_verdict_snapshot.py` is a corpus-baseline input.

## 8. Unverified

- M6: whether the truth-block readers iterate keys. This decides 5.1's JSON shape.
- M7: why R62's "page 0" is index 2 today.
- Whether one PR can carry both the regenerate and the adjudication (§ 5.5, `_durable` via `HEAD:`).
- That O6 holds: the regenerate moves only the two truth blocks and `inputs.json`. **Proposed**: if
  any other byte moves, stop before committing and diagnose.
