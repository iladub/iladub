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
- `cor:durable` (datatype, domain `cor:Snapshot`, `xsd:boolean`): **lifted, never authored** (§ 4.3).
- `cor:snapshotOf` (object property, domain `cor:Snapshot`, range `cor:Document`): **lifted, never
  authored** (§ 4.3), from the blob's own `"pdf"` field.

`tests/test_artifact_terms.py:441` counts declared and demanded terms (72 / 78 since R259 task 3).
Those counts move. **Measure the new figures and update the pin with its reason.** Do not
pre-compute them here.

### 4.3 The snapshot lift (`tests/corpus_firings.py`)

Add an entry point beside `lift_firings`, with this signature contract only:

- `lift_snapshots(manifest: Graph) -> Graph`. For every `(adj, cor:judgedAgainst, snap)` in the
  manifest, it reads `snap`'s `cor:blob` with `git cat-file -p` and parses it as JSON. It attaches,
  **to the same `snap` node** (adjudications and snapshots are blank nodes, and rdflib's `+` keeps
  BNode identity; **measure that on the real manifest before relying on it**):
  - one `cor:firing` per constant reason, with `cor:live`, `cor:superseded` and `cor:recordedIn`,
    built by the **same** counting code as `lift_firings`. Factor the shared `(path, data)` core out;
    do not duplicate it.
  - `cor:snapshotOf <doc>`: the manifest document whose `cor:file` matches the blob's `"pdf"` field.
    A `"pdf"` matching no manifest document raises, as `lift_firings` does (`:53-58`).
  - `cor:durable true|false`: true iff the blob equals `git rev-parse <c>:<recordedIn path>` for
    `c = HEAD` or some commit on `git rev-list --first-parent HEAD`.
    - In PR CI, HEAD is the merge ref, whose first parent is `main` and whose tree holds the PR's
      final files. That is exactly the set that survives a squash, so the probe's intermediate blob
      reads `false` there.
    - Locally, on a multi-commit branch, intermediate commits sit on the first-parent chain and read
      `true`. **That gap is recorded, not closed.** CI is where it binds.
- A blob that `git cat-file` cannot resolve **raises**. It never yields an empty firing set,
  because a silent zero would make D2 refuse for the wrong reason, or admit nothing.

**Call sites.** It is called only from the tests that validate D2 (`test_manifest_conforms` and the
D2 negatives in `tests/test_corpus_manifest.py`, plus `test_is_disposed_agrees_with_disposal_shape`).
**Never at import of `tests/test_corpus.py`** (R325: a lift refusal at import is a session-wide
collection error, and a git read makes it likelier). `is_disposed` and `ADJUDICATED`
(`tests/test_corpus.py:202-215`) stay as they are, because whether a reason is disposed is a fact of
the manifest, and whether the disposal is admissible is D2's question. **MEASURE whether any other
D2-validating test exists before declaring the list closed.**

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
- New rows, if raised, carry the `(c/t closed)` snapshot. The local-first-parent gap (§ 4.3) is a
  candidate row.

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
blob where it had live > 0. **MEASURE that such a blob exists on `main`'s first-parent history**
(R318 moved five documents' baselines, so one probably exists). If none exists, the test is built
from a synthetic manifest plus a test-local git repo, and the task report says why.

A strict xfail exits 0, so `met true` stays an authored claim (handoff § 2): five criteria share this
oracle. The PR states the pytest line showing the two params **passed**, not merely the exit code.

## 6. Costs the loop carries

- `vocab/` is a compile input, so after the **last** input edit and after `git add`, run one
  `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` (~24 min, serial, nothing
  else running) and commit `tests/corpus-baseline/`. Then write the blobs into the manifest (§ 4.5).
  The manifest is not a compile input (`scripts/corpus_baseline.py:56`, **measure**), so this ordering
  does not re-stale the gate.
- `lift_snapshots` runs `git` subprocesses: a few per disposal, two disposals. Measure the added test
  time.

## 7. What is NOT done

- No repair of KIND_NOT_SUPPORTED in `src/`. The five bands are not tables, and disposal is the
  honest verdict. No change to the kind gate.
- R44 and R71 are not closed. Their *edges* on tab:07 are deleted with a reason.
- No disposal of DATAGRID_RESIDUE (apple, bfs, ons) or REGION_TILING_FAILED (bfs). Those are other
  criteria's parameters of the same oracle and stay strict xfail.
- R325 (the import-time lift) is not fixed, only not worsened.
- The local first-parent gap (§ 4.3) is not closed.
- No superseding-adjudication machinery (rejected by R323's ruling).
