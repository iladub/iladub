# The disposal carries its reading — meeting tab:07 by adjudication (design, 2026-10-19)

**Serves:** prog:criterion:tab:07 — `prog:met false` re-verified 2026-10-19 at `0280030`
(`tests/arc-manifest.ttl:1359`).

**Doc impact: none.** Test-side shapes, an internal vocabulary term (`vocab/internal/`, never
published), manifest rows and register rows. No released artifact changes meaning.

**Approved:** approach 1 of `docs/superpowers/2026-10-18-tab07-adjudication-handoff.md` § 5 item 3,
by the maintainer 2026-10-19, conditional on the CI probe of § 5 item 4, which ran first (§ 2).

## 1. Goal and the ruling it implements

Meet `tab:07`: KIND_NOT_SUPPORTED is disposed of by a dated `cor:adjudication` on every corpus
document it fires live on. It fires live on bfs (3) and ons (2) and nowhere else (§ 3). The oracle is
`tests/test_corpus.py::test_escalation_reasons_are_adjudicated`. Its two KIND_NOT_SUPPORTED
parameters turn from strict xfail into passes by derivation (`_adjudication_param`,
`tests/test_corpus.py:218-222`), and no marker is hand-removed.

**R323, ruled by the maintainer 2026-10-17:** D2 (`cor:DisposalShape`) is judged at the disposal's
**own dated reading**, never at the current baseline. Measured today: D2 joins `cor:disposes` to
`?doc cor:firing ?f` (`tests/corpus-shapes.ttl:106-118`), and the only firings in the graph are
lifted from the **current** baseline directory (`tests/test_corpus_manifest.py:44`,
`tests/corpus_firings.py:46`). So a later repair that drives `cor:live` to 0 would make D2 refuse an
append-only disposal that was true when written. Superseding adjudication was rejected.

## 2. The probe (handoff § 5 item 4), run before this spec

Draft PR #354, closed unmerged. A CI step before install ran `git cat-file -t/-p` on three blobs:

| Blob | Where it lived | Resolved in PR CI |
|---|---|---|
| `53a2490…` | only in the PR head's tree | yes |
| `b91d5f1…` | only in an earlier PR-branch commit, overwritten by head | **yes** |
| `2f01e0d…` | `main:tests/corpus-baseline/apple-fy2026q3-statements.json` | yes |

The checkout is the merge ref `dab106c` (merge of head into `0280030`), `fetch-depth: 0`.

**The seam the probe exposes:** the intermediate blob resolves only because it is an ancestor of the
PR head (second parent of the merge ref). After the squash merge it is in no commit on `main`. A
disposal naming it would pass its own PR and dangle on `main` forever. Reachability alone is
therefore **not** the guard (§ 4.3).

## 3. The firings, measured 2026-10-19 at `0280030`

From `tests/corpus-baseline/*.json`, regions with `reason == "KIND_NOT_SUPPORTED"`:

| Document | Page/region | Verdict | The band (handoff § 2, from per-page compile) |
|---|---|---|---|
| bfs | p0 r0 | escalated | press-release masthead |
| bfs | p5 r15 | escalated | sources line and footnotes |
| bfs | p6 r1 | escalated | table title "T3" |
| ons | p0 r1 | escalated | release masthead and contents list, with a 3-column label/value release block |
| ons | p7 r0 | escalated | table title "IOS1" |
| ons | p7 r3, p8 r2 | superseded | (grid adoption; not disposed — superseded is not repaired, § 2.1 of R259 spec) |

None of the five is a table. The disposal text says so per band. It names ons p0 r1's block as
**metadata**. It says the two titles are **context that does not reach their tables** (Core design
principle 5), as the R288 ruling did for the cbh Note. That last part is a defect being recorded, not
excused. The band descriptions come from the handoff. **The implementer re-renders each band
before writing its disposal** (`band_text` is carried on escalated regions since R318) and quotes
what the page says, not what this table says.

## 4. Design

### 4.1 Gate classification (CLAUDE.md § 8)

| Decision | Class | Why |
|---|---|---|
| Is this disposal admissible? | **AXIOM — constraint (SHACL)** | Closed world at the membrane. D2 rewritten (§ 4.4). |
| Which firings did the disposal's own reading hold? | **PROCEDURAL — raw extraction** | The input is a git blob of JSON, not a graph. Same justification as `tests/corpus_firings.py:3-7`. No judgement, no tolerance. |
| Is the recorded blob durable on `main`? | **PROCEDURAL — raw extraction** | Reading git's object store and first-parent history is extraction of a fact. The admissibility judgement over it is SHACL (§ 4.3). |
| Is this band a table? | **None in code** | A human judgement, authored as the adjudication's rationale and signed off by the maintainer's merge. |

### 4.2 Vocabulary (`vocab/internal/corpus.ttl`)

**Do not reuse `cor:Reading`.** `cor:ReadingShape` requires exactly one `cor:value` (a decimal score,
`tests/corpus-shapes.ttl:64-66`). A baseline snapshot has no score, and inventing one is forbidden
(principle 7). New, minimal terms:

- `cor:Snapshot` (class): a committed corpus-baseline file at one content address.
- `cor:judgedAgainst` (object property, domain `cor:Adjudication`, range `cor:Snapshot`): the
  reading the adjudication was judged at.
- `cor:blob` (datatype property, domain `cor:Snapshot`, `xsd:string`): the git blob sha of that
  file. Content-addressed, so it survives the squash merge, and it can name a baseline regenerated
  inside the disposal's own PR, which a commit sha cannot do.
- Widen `cor:recordedIn`'s domain union to admit `cor:Snapshot` (it already admits `cor:Firing`,
  `vocab/internal/corpus.ttl:229-231`).
- Widen `cor:firing`'s domain, which today is `cor:Document`, so that it also admits
  `cor:Snapshot`. (measured: `vocab/internal/corpus.ttl:249-252`).
  Both widenings are **documentation**. `_conforms` passes no `ont_graph`, so no `rdfs:domain` is
  in the validated graph, and RDFS ignores `owl:unionOf` anyway (§ 8 A7). They keep the vocabulary
  honest. No test "verifies" them.
- `cor:durable` (datatype, domain `cor:Snapshot`, `xsd:boolean`): **lifted, never authored** (§ 4.3).
- `cor:snapshotOf` (object property, domain `cor:Snapshot`, range `cor:Document`): **lifted, never
  authored** (§ 4.3), from the blob's own `"pdf"` field.

`tests/test_artifact_terms.py:441` counts declared and demanded terms (72 / 78 since R259 task 3).
Those counts move. **Measure the new figures and update the pin with its reason.** Do not
pre-compute them here.

### 4.3 The snapshot lift (`tests/corpus_firings.py`)

Add an entry point beside `lift_firings`, with this signature contract only:

- `lift_snapshots(manifest: Graph, repo: Path = _REPO) -> Graph`. Every git call runs in `repo`.
  That parameter is what makes the R323 test constructible (§ 5, § 8 A1). For every
  `(adj, cor:judgedAgainst, snap)` in the manifest, it reads `snap`'s `cor:blob` with
  `git cat-file -p` and parses it as JSON. It attaches, **to the same `snap` node**. Adjudications
  and snapshots are blank nodes, and rdflib's `+` keeps BNode identity, measured on the real
  manifest 2026-10-19 (§ 8):
  - one `cor:firing` per constant reason, with `cor:live`, `cor:superseded` and `cor:recordedIn`,
    built by the **same** counting code as `lift_firings`. Factor the shared core out and do not
    duplicate it. The core takes the `recordedIn` string **as a parameter**. A snapshot firing
    records `<path>@<blob>`, because the bytes at `<path>` in HEAD may differ from the ones read,
    and `_recorded_in` promises "never a path that was not read" (`tests/corpus_firings.py:27-29`;
    § 8 A6).
  - `cor:snapshotOf <doc>`: the manifest document whose `cor:file` matches the blob's `"pdf"`
    field. A `"pdf"` matching no manifest document raises, as `lift_firings` does (`:53-58`).
  - `cor:durable true|false`: true iff the blob is the one at `<recordedIn path>` in **HEAD's
    tree**, or the one at that path in some commit on
    `git log --first-parent origin/main -- <path>` (one history query per path, cached for the
    session; § 8 A4). This is anchored to `origin/main` and **not** to HEAD's first-parent chain
    (§ 8 A3):
    - in a stacked PR the merge ref's first parent is the base branch, whose intermediate commits
      would read `true`;
    - locally, the old definition admitted every commit of a multi-commit branch.

    The anchored definition closes both cases.
    **Unmeasured, probe before building:** that the `ci.yml` checkout (`fetch-depth: 0`) has
    `origin/main` on a `pull_request` event. Run one CI step, as #354 did. If it is absent, the
    lift **raises**. It never falls back to HEAD's chain.
- A blob that `git cat-file` cannot resolve **raises**. It never yields an empty firing set,
  because a silent zero would make D2 refuse for the wrong reason, or admit nothing.

**Call sites, enumerated 2026-10-19** (`grep -rn "lift_firings\|is_disposed\|corpus-shapes" tests/`).
`lift_snapshots` is added wherever D2 is validated over the real manifest:

- `test_manifest_conforms` (`tests/test_corpus_manifest.py:39`).
- `_with_disposal` (`tests/test_corpus_manifest.py:132`). It must call `lift_snapshots` **after**
  the injection, because the injected `judgedAgainst` node does not exist before it. The injection
  must carry a **valid durable snapshot**: without one, constraint 1 refuses every injected
  disposal. That breaks the two positive controls and the agreement test, and every D2 negative
  passes for the wrong reason.
- `test_real_lift_conforms_to_firing_shape` (`tests/test_corpus_firings.py:129`). It validates the
  full `corpus-shapes.ttl`, D2 included, over manifest ∪ `lift_firings`, and refuses once
  constraints 2–4 need lifted snapshot facts.

**Every D2 negative asserts WHICH constraint refused** (its `sh:message`), not merely `not ok`.
Otherwise constraint 1 makes the negatives vacuous.

**Never at import of `tests/test_corpus.py`** (R325: a lift refusal at import is a session-wide
collection error, and a git read makes it likelier). `is_disposed` and `ADJUDICATED`
(`tests/test_corpus.py:202-215`) are unchanged in code. Whether a reason is disposed is a fact of
the manifest; whether the disposal is admissible is D2's question. **Their pins in
`tests/test_corpus_is_disposed.py` are not unchanged.** Every pin built on the real bfs/ons KIND
pair breaks or goes vacuous once the real disposal lands (§ 8 A2):

- `test_no_disposal_is_not_disposed` fails;
- `test_disposal_on_the_other_document_is_not_disposed` fails;
- `test_language_tagged_disposal_is_not_disposed` fails;
- the `@en` arm of `test_is_disposed_agrees_with_disposal_shape` fails for bfs-KIND and ons-KIND;
- `test_disposal_of_a_live_firing_is_disposed` still passes with its injection deleted.

Re-target each pin to a pair that stays undisposed (bfs `DATAGRID_RESIDUE` or
`REGION_TILING_FAILED`). For the agreement test, compare over a manifest **without** the loop's
disposal. **`live_pairs` filters its subjects to URIRefs**, so snapshot nodes can never be read as
documents. No current caller passes it snapshot output (§ 8 A8), so this is a guard, pinned by a
test.

### 4.4 D2, rewritten (`tests/corpus-shapes.ttl:106-118`)

Target is still `sh:targetSubjectsOf cor:disposes`. The shape holds four constraints, each with
its own `sh:message`:

1. `cor:judgedAgainst`: exactly one (`sh:minCount 1 ; sh:maxCount 1`). A disposal with no reading
   is refused.
2. The snapshot is **of this document**: `?doc cor:adjudication $this` and `?snap cor:snapshotOf
   ?doc`. A bfs disposal judged against the ons baseline is refused.
3. The snapshot is **durable**: `cor:durable true`. An in-PR intermediate blob is refused.
4. The snapshot holds a **live** firing of the disposed reason. This is the existing join, re-rooted
   from `?doc cor:firing` to `?snap cor:firing`, keeping value equality (`?reason = ?value`) and its
   recorded rationale (`:97-104`). It is holon-scoped (it closes over the one snapshot), and the
   current baseline's firings play **no part**.

The rationale comment is rewritten to cite this spec and R323's ruling. **Do not drop** the
value-equality paragraph: the `xsd:string` / `@en` tests still pin it.

### 4.5 The two disposals (`tests/corpus-manifest.ttl`)

One new adjudication per document, appended, never edited into an existing one. The existing
adjudications that name the reason (bfs `:127, 454, 470`; ons `:114, 465`) stay byte-identical. Each
new one carries `cor:by`, `cor:on "2026-10-19"` or the actual date, `cor:rationale` (§ 3's band-by-band
judgement), `cor:disposes "KIND_NOT_SUPPORTED"`, and `cor:judgedAgainst [ a cor:Snapshot ;
cor:recordedIn "<baseline path>" ; cor:blob "<sha>" ]`.

**Which blob.** The one the PR **commits last** for that file. After `regenerate` (§ 6), take
`git rev-parse HEAD:<path>` *after* committing the regenerated baseline, and only then write the
blob into the manifest. Also measure whether the regenerated bfs/ons JSON is byte-identical to the
`0280030` one. The vocab edit should not change any document's output, but that is a prediction,
and `git diff -- tests/corpus-baseline/` is the measurement. If it is identical, the blob is the
current `main` one.

The agent composes the disposal text. The maintainer signs it off by merging the PR, and the PR
body says so.

### 4.6 The criterion and its edges (`tests/arc-manifest.ttl:1351-1361`)

- `prog:met true`, `prog:metOn` the merge date. Delete `prog:blockedBy "R44" , "R71"` **in the same
  act**, because M8 (`tests/arc-shapes.ttl:149-153`) refuses any blocked met criterion. Precedent: the
  R166 deletion at `:228-234`, which replaces the edge with a comment saying what stood there and
  why it went.
- **The reason each edge goes**, which is an inference to re-argue in the PR, not to copy. An edge
  names a row *whose closure would advance this criterion* (`:1174-1175`), and closing neither row
  disposes of any of the five firings:
  - **R71** is about suppressing `looks_transposed` on two graincorp-stem bands, and none of the five
    is a stem band. R71 stays open, and its edge on criterion 03 is untouched.
  - **R44** is a three-reason bfs row with no shared root cause. Its KIND_NOT_SUPPORTED share is
    disposed of here, not repaired. R44 stays open for `ROUND_TRIP_FAIL`, `REGION_TILING_FAILED`
    and `DATAGRID_RESIDUE`.
- Fix the stale comment at `:1351` ("bfs only" → bfs 3 live, ons 2 live + 2 superseded). Fix the
  statement's `compile.py:978` citation. **MEASURE the emitter's current line** (the handoff measured
  `src/iladub/etkl/compile.py:1876-1890`), and prefer citing the symbol over a line. Read the manifest's
  editing rules (`:17`) before touching a `prog:statement`.

### 4.7 Register

- Strike R323 and record the ruling (§ 1) and this loop's closure evidence in its row.
- Correct R44's KIND count ("4 (3 live + 1 superseded)" → 3 live, 0 superseded) **by appending a
  dated correction**, not by editing the old figure.
- New rows, if raised, carry the `(c/t closed)` snapshot. Raise one row for the band-level relevance
  hole (§ 7, § 8 A5).

## 5. Oracles and falsification

| Oracle | Must pass | Falsify by |
|---|---|---|
| `test_escalation_reasons_are_adjudicated[bfs-KIND_NOT_SUPPORTED]`, `[ons-…]` | pass (not xfail) | delete one disposal → that param is xfail again |
| `test_manifest_conforms` (manifest ∪ lift_firings ∪ lift_snapshots) | conforms | replace a disposal's blob with the probe's intermediate-shaped one → refused on constraint 3 |
| **R323's own case**: a disposal whose reason has 0 live in the *current* baseline, with a durable snapshot holding live > 0 | **admitted** | point D2's join back at `?doc cor:firing` → this test fails |
| A disposal whose own snapshot holds 0 live for the reason | refused | drop constraint 4 → admitted |
| A disposal with no `cor:judgedAgainst` | refused | drop constraint 1 |
| A disposal on bfs judged against the ons baseline blob | refused | drop constraint 2 |
| An unresolvable blob | `lift_snapshots` raises | swallow the error → test fails |
| The existing D2 negatives (unfired, misspelt, superseded-only, wrong document, `@en`) and the `xsd:string` positive | unchanged verdicts, re-rooted onto a snapshot | as recorded at R259 |
| arc manifest M8 | conforms with `met true` and no edges | restore one `blockedBy` → M8 refuses |

**The R323 case needs a constructible setup** (CLAUDE.md plan rule 5). Construct it by injecting a
disposal on a document where the reason has **0 live now**, judged against a durable historical
blob where it had live > 0. **Measured 2026-10-19: no such blob exists for any manifest document.**
The one reason on `main`'s first-parent baseline history with historical live > 0 and current 0 is
caltrain KIND_NOT_SUPPORTED (4 → 0, blob `6b11ea9f9f` at `fc0c24a5`). Caltrain is held-out, and
`lift_firings` skips it. So the test is built from a **synthetic manifest plus a test-local git
repo** (`tmp_path`, `git init`), passed as `lift_snapshots(..., repo=tmp_path)`. It has two
commits on that repo's `main`:

1. commits the baseline with live > 0;
2. replaces it with live = 0.

The disposal is judged against commit 1's blob. In that repo, `origin/main` is supplied as a ref
the test creates.

A strict xfail exits 0, so `met true` stays an authored claim (handoff § 2): five criteria share this
oracle. The PR states the pytest line showing the two params **passed**, not merely the exit code.

## 6. Costs the loop carries

- `vocab/` is a compile input, so after the **last** input edit and after `git add`, run one
  `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` (~24 min, serial, nothing
  else running) and commit `tests/corpus-baseline/`. Then write the blobs into the manifest (§ 4.5).
  The manifest is not a compile input (`scripts/corpus_baseline.py:56`, **measure**), so this ordering
  does not re-stale the gate.
- `lift_snapshots` runs `git` subprocesses: one `cat-file` per disposal, plus one first-parent
  history query per baseline path, cached for the session. `main` has 560 first-parent commits; a
  `rev-parse` per commit costs about 8 ms, so 400 commits is 3.2 s per call. `git log
  --first-parent --raw --no-abbrev -- <path>` takes 0.15 s (§ 8 A4). The lift is called by roughly
  25 tests (D2 negatives, the agreement params × 3 spellings), so the uncached per-commit scan is
  refused. Measure the added test time.

## 7. What is NOT done

- No repair of KIND_NOT_SUPPORTED in `src/`. The five bands are not tables, and disposal is the
  honest verdict. No change to the kind gate.
- R44 and R71 are not closed. Their *edges* on tab:07 are deleted with a reason.
- No disposal of DATAGRID_RESIDUE (apple, bfs, ons) or REGION_TILING_FAILED (bfs). Those are other
  criteria's parameters of the same oracle and stay strict xfail.
- R325 (the import-time lift) is not fixed, only not worsened.
- **Band-level relevance is unguarded** (§ 8 A5). This was already true before this loop.
  `_DISPOSED` and D2 both work per document × reason. A disposal judged against today's bfs blob
  also covers any **future** KIND_NOT_SUPPORTED on bfs, including a real table the kind gate starts
  refusing after a regression. Neither D2 nor the oracle notices. That is consistent with R323's
  ruling (disposals are append-only and judged at their own reading), but it is a hole. It is
  recorded as a residue row. Any guard (for example current live ≤ snapshot live) is a count proxy
  and needs its own gate classification first.
- No superseding-adjudication machinery (rejected by R323's ruling).

## 8. Adversarial premise review, 2026-10-19 (before any plan)

The premises were probed by the controller, then attacked by an independent reviewer. Each finding
below is measured. Each **BLOCKING** finding is folded into the section it cites.

| # | Sev. | Finding | Measurement | Folded into |
|---|---|---|---|---|
| A0 | holds | rdflib keeps BNode identity across `Graph + Graph` on the real manifest | probe: injected triple on a manifest adjudication BNode survives `m + o` with its other triples | § 4.3 |
| A1 | BLOCKING | The R323 test needs a test-local repo, but the lift as specified had no repo argument | `tests/corpus_firings.py:22` hard-codes `_REPO`; no manifest document has an R323 case on `main` (caltrain only, held-out) | § 4.3 signature, § 5 |
| A2 | BLOCKING | Landing the real disposal breaks or empties every `is_disposed` pin built on bfs/ons KIND (5 sites) | in-memory simulation: lang-tag test gets `is_disposed = True`; agreement `@en` arm: `True` vs conforms `False`; the two "not disposed" tests assert the opposite of the new manifest | § 4.3 |
| A2′ | BLOCKING | The call-site list was incomplete: `test_real_lift_conforms_to_firing_shape` validates D2. `_with_disposal` without a snapshot makes constraint 1 refuse everything, so the negatives go vacuous | `tests/test_corpus_firings.py:129-135`; `tests/test_corpus_manifest.py:132-138` | § 4.3 |
| A3 | AMEND | `durable` = HEAD's first-parent chain is wrong for stacked PRs (`ci.yml:5` `pull_request:` has no branch filter) and locally | the merge ref's first parent is the PR's base | § 4.3, anchored to `origin/main`; § 7's local gap item withdrawn |
| A4 | AMEND | Cost: an uncached per-commit scan, repeated per lift call | 560 first-parent commits; 8 ms per `rev-parse`; one `git log --raw` takes 0.15 s | § 4.3, § 6 |
| A5 | AMEND | Relevance is unguarded at band level (an old hole, now explicit) | `tests/test_corpus.py:207-211` works per doc × reason | § 7, § 4.7 row |
| A6 | AMEND | A snapshot firing's `recordedIn` would name a path whose HEAD bytes were not read | `tests/corpus_firings.py:27-29` docstring | § 4.3 (`path@blob`) |
| A7 | NOTE | The domain widening has no validation effect: `_conforms` passes no `ont_graph`. RDFS ignores `owl:unionOf`, so the union domain never types a snapshot `cor:Document` | probe: a Snapshot with `cor:firing` conforms on data alone; with `corpus.ttl` as `ont_graph` and the **old** domain, DocumentShape fires | § 4.2 (the widening is documentation; do not "verify" it by test) |
| A8 | NOTE | `live_pairs` reads every `cor:firing` subject as a document | `tests/corpus_firings.py:96-101`; today's callers never see snapshot output | § 4.3 (URIRef filter, pinned) |
| A9 | NOTE | Census prediction 72/78 → 75/81 (`judgedAgainst`, `blob`, `Snapshot` demanded; `durable` and `snapshotOf` live only inside `sh:select` strings, which are not nodes). Writing constraint 3 as `sh:path cor:durable` adds 1 to each | reviewer probe | § 4.2: **still measure, do not transcribe** |
| A10 | NOTE | The `snapshotOf` join could be AXIOM (lift a raw `cor:pdf` literal, join it to `cor:file` in constraint 2). It stays PROCEDURAL only because it mirrors `lift_firings`' refusal | — | § 4.1, left to the plan author to argue |

Also checked, and they hold: the manifest is not a compile input (`scripts/corpus_baseline.py:55-56`),
and nothing in `src/` reads `vocab/internal/`, so the regenerate is required ceremony and should
move no bfs/ons byte. M8 is the only arc rule that `met true` touches, since no live `dependsOn`
targets tab:07 (`tests/arc-manifest.ttl:1771-1781`). The R44/R71 arguments match the edge
definition at `:1174-1178`.

**Open premise, to probe first in the plan (proposed, may fail):** does the PR checkout carry
`origin/main`? If it does not, A3's anchor needs `git fetch origin main` in `ci.yml`, or a
different anchor. Either way the plan's first task finds out in one CI run, not after building on it.
