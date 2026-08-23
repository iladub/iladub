# The faithful worktree — closing R114 by making M19's environment honest

**Topic:** the arc / the M19 ablation instrument · **Date:** 2026-08-23 · **Origin:** [[R114]],
measured out to a wider root cause · **Tree:** `main` @ `8523462`, clean ·
**Runner:** `./.venv/bin/python` (3.12.0, pytest 9.0.3, rdflib 7.6.0) — **never `python3`**.

**Doc impact:** increment — CI gains a job. The wiki gains nothing this loop. `CLAUDE.md` gains nothing. CI
gains a job, which is a Manual-class fact (`.github/workflows/ci.yml`) and is described in §6.
No published assertion changes; no contradiction with a released artifact.

---

## §1 The question

[[R114]] states a fact and proposes three remedies:

> `etkl:01`'s oracle cannot EXECUTE inside a worktree, so no edge can ever be asserted at either
> of its ends — and it is the `etkl` rung's only met criterion.

Taken at face value this is a corpus problem with a corpus fix. **Measured, it is not.** It is one
face of a property of the instrument:

> **M19's ablation worktree is not a faithful environment for the oracles it runs.**

A `git worktree add --detach <wt> HEAD` checkout contains exactly the *committed* tree. Every input
an oracle needs that is **not committed** is silently absent, and M19 reads that absence as
evidence about the graph. There are three measured faces of this, and they fail in three
*different directions* — which is why one of them was found as a residue, one as a review
deferral, and one only by writing this spec.

**The question this loop answers:** *can the instrument be made to know the difference between
"the ablation caused this" and "this environment could never have run it"?* — and if so, does
`etkl:01` then ground anything.

## §2 What is measured before anything is designed

Every figure below was produced against `8523462` in this session and carries its command. Nothing
here is quoted from a residue row or a prior loop's evidence without re-derivation; where a
re-derivation **disagrees** with the record, §11 records the correction.

### §2.1 The three faces

| face | mechanism, measured | direction of the error | status before this loop |
| --- | --- | --- | --- |
| **F1 — `corpus/`** | gitignored (`.gitignore:43-44`, *"fetched by `scripts/fetch_corpus.py`, never committed"*). `tests/test_corpus.py:66-67` calls `pytest.skip("corpus not populated: …")` on absence | scored *"did not execute"* (`test_arc_ablation.py:241-242`) → M19 **refuses** the edge on the arm that ran it (`:353-355`, `:365-367`) | [[R114]] |
| **F2 — `baml_client/`** | gitignored (`.gitignore:30`), CI-generated (`ci.yml:23-24`), `git ls-files \| grep -c baml_client` → `0` | collection ERROR → scored `FAILED` (`:224`, `:231-234`) → arm 1 **admits** an edge on no evidence (`:346-352`) | [[R118]], live mechanism |
| **F3 — the editable install** | `.venv/lib/python3.12/site-packages/_editable_impl_iladub.pth` pins the main tree. Measured from inside a worktree: `iladub.__file__` = `/Volumes/WD Green/dev/git/iladub/src/iladub/__init__.py` while `cwd` = the worktree | a deleted `src/` artifact still imports → arm 2 **false green** | already declared, `test_arc_ablation.py:87-111` limitation 4 |

**F1 refuses truthfully-shaped edges; F2 admits unfounded ones; F3 would pass what should fail.**
F2 is the dangerous one, F1 is the blocking one, F3 is latent — **zero** of the 29 declared
artifact files live under `src/` (§11.2), so F3 has no live instance and this loop does not fix it.

### §2.2 The collection census, re-measured

```
$ git worktree add --detach "$WT" HEAD          # 8523462
$ cd "$WT" && "$REPO/.venv/bin/python" -m pytest --collect-only -q | tail -4
ERROR tests/test_extract_baml.py
ERROR tests/test_loop.py
ERROR tests/test_m4_databook.py
ERROR tests/test_m4_pipeline.py
ERROR tests/test_targeted.py
ERROR tests/test_to_rdf.py
!!!!!!!!!!!!!!!!!!! Interrupted: 6 errors during collection !!!!!!!!!!!!!!!!!!!!
1293 tests collected, 6 errors in 4.85s
```

**Six**, not the five [[R118]]'s amendment records. The sixth is `tests/test_to_rdf.py`, which
breaks *transitively* — `tests/test_to_rdf.py:4` imports `iladub.extract_baml`, and
`src/iladub/extract_baml.py:8` is `from baml_client import sync_client`. R118 enumerated the
modules whose own module-scope line names `baml_client`; a transitive importer is invisible to
that method. `.github/workflows/ci.yml:23` already names the right number in its own step title
(*"Generate baml_client (gitignored; 6 test modules import it)"*).

### §2.3 The feasibility probe — the existence proof this spec is built on

The single risk that could have made this loop worthless is *"the oracle still will not run once
the input is there."* It was retired before designing anything:

```
$ ln -sfn "$REPO/corpus" "$WT/corpus" && ln -sfn "$REPO/baml_client" "$WT/baml_client"
$ cd "$WT" && "$REPO/.venv/bin/python" -m pytest --collect-only -q | tail -1
1314 tests collected in 1.99s                      # was 1293 collected, 6 errors

$ time "$REPO/.venv/bin/python" -m pytest \
    "tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-stem-2026-07-31.pdf]" -v
tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-stem-2026-07-31.pdf] PASSED [100%]
======================== 1 passed in 164.37s (0:02:44) =========================
```

**`etkl:01`'s oracle executes and PASSES in a worktree once its input is materialised**, and the
six collection errors vanish in the same step. The probe used symlinks; §4.1 explains why the
shipped form must not.

**Cost, which is the whole design constraint:** 164.37 s. Task 1 of the previous loop measured
every other met criterion's oracle at **≤ 1.24 s**, and the whole live M19 leg at **5.69 s over 6
edges / 9 endpoints**. `etkl:01` is two orders of magnitude more expensive than anything M19 has
ever run.

### §2.4 The A6 ceiling on the `etkl` rung — R114's remedy column is wrong about this

Read with `graph.objects()` throughout, never `graph.value()`:

| criterion | line | `met` | `oracleTest` | `oracleArtifact` |
| --- | --- | --- | --- | --- |
| `etkl:01` | 149 | **true** (`2026-08-03`) | `test_corpus.py::test_expected_verdict[…graincorp-stem…]` | `tests/corpus-manifest.ttl` |
| `etkl:02`–`etkl:07` | 182–232 | false | one `test_expected_verdict[…]` each | **`tests/corpus-manifest.ttl`** (all six) |

All seven declare **the same single artifact file**. A6 refuses any asserted edge whose ends share
an artifact file (`tests/arc-shapes.ttl:319`), so:

> **No `etkl` → `etkl` edge can ever be asserted, corpus or no corpus.** This is a property of the
> manifest, not of the environment, and no remedy in R114's last column changes it.

R114 closes with *"this makes the entire `etkl` rung un-assertable today, which is why (a) or (b)
is worth more than (c)."* That is half right: (a) makes `etkl:01`'s **cross-rung** ends assertable,
and nothing makes the rung internally assertable.

What *is* reachable, measured over the 17 met criteria:

```
etkl:01 artifacts: {'tests/corpus-manifest.ttl'}
met criteria sharing that artifact file (A6): none
met criteria sharing that oracle test (A3):   none
=> met partners passing A3+A6 with etkl:01: 16
```

**`etkl:01` is A3/A6-clean against all 16 other met criteria** — modulo A4's date filter
(`metOn 2026-08-03`). So R114 really is the only thing standing at its ends, and the envelope is
real rather than notional.

### §2.5 CI, measured

`.github/workflows/ci.yml` runs **one** job: `pip install -e ".[baml,dev,docs,etkl]"` (`:22`),
`baml-cli generate --from baml_src` (`:23-24`), then a bare `pytest -q` (`:26`). **No `-m` filter
and no corpus fetch.**

Two consequences, both load-bearing:

1. `baml_client` **is** available in CI and F2 never fires there. F2 is a local-and-worktree
   hazard; it is real, but it is not a CI redness today.
2. `corpus/` is **never** present in CI. `pytestmark = pytest.mark.corpus` at
   `tests/test_corpus.py:22` deselects nothing, because markers only deselect under `-m` — those
   tests run in CI and skip. **So today an `etkl` edge would ground on the maintainer's machine
   and refuse in CI.**

The 14 tracked modules that read `corpus/` collect **209 tests** between them
(`test_corpus.py` 10, `test_corpus_stem.py` 13, `test_cbh_e2e.py` 3, `etkl/test_datagrid.py` 59,
`etkl/test_decision_queries.py` 4, `etkl/test_decisionlog.py` 17, `etkl/test_escalation_wiring.py`
7, `etkl/test_adoption_document.py` 10, `etkl/test_closure_equiv.py` 17,
`etkl/test_decimal_typing.py` 13, `etkl/test_membrane_equiv.py` 31,
`etkl/test_kind_gate_is_load_bearing.py` 10, `etkl/test_escalation_furnish.py` 10,
`etkl/test_supersession_queries.py` 5). **209 is the envelope that changes state if CI gains the
corpus**, not a count of tests that currently skip — establishing the latter needs a full
CI-shaped run and is a MEASURE box for the plan (§10.7), not a claim made here.

## §3 What proposes, what disposes, and why they are independent

The discipline this repo requires of any loop (see `docs/superpowers` passim, and CLAUDE.md §3):
name the proposer, name the disposer, and show they are not the same reading.

| | |
| --- | --- |
| **Proposition** | *"Copying the declared environment inputs into the ablation worktree makes it a faithful environment for the oracles M19 runs."* |
| **Disposer** | **An un-ablated control run.** Before any artifact is deleted, every endpoint oracle is run in a worktree with the environment materialised and **nothing removed**. Every requested node id must report `PASSED`. |
| **Independent?** | **Yes, and this is the point.** The control inspects no materialisation logic, no declared input list and no path. It asks one question — *does this oracle pass here when nothing has been taken away?* — and a `SKIPPED`, an `ERROR` or a `FAILED` answers it identically: **the environment is not faithful, and nothing measured in it grounds anything.** |

The control is what converts F1, F2 and F3-if-it-ever-goes-live from three separately-diagnosed
defects into one refusal, and it would have caught all three without knowing any of them existed.

**Consequence, stated up front:** an oracle that fails the control is an **instrument failure**,
not evidence. It must `RuntimeError` with the transcript — exactly as an unresolved node id
already does (`test_arc_ablation.py:243-249`) — and must never be scored. This is the single
most important behavioural claim in this spec.

## §4 The design

### §4.1 Materialisation — by copy, never by symlink

`_ablate` (`test_arc_ablation.py:253`) gains a step between `git worktree add` (`:263`) and the
first `target.unlink()` (`:273`): copy each declared environment input into the worktree.

**Copy, not the symlink the §2.3 probe used.** `_ablate`'s whole job is to *delete declared
artifacts*. Through a symlinked directory, `Path.unlink()` deletes the real file **in the main
tree**. The corpus is irreplaceable in practice — `docs/superpowers/specs/2026-08-02-real-document-generalization-design.md:32-34`
records that GrainCorp's 2025 stem URLs are already 404, and every entry is sha256-pinned to a
specific edition. A copy makes the destructive path structurally impossible for **4.5 M**
(`du -sh corpus` → `4.5M`; `baml_client` is 27 small files).

This is a design decision taken on measurement, not a preference, and the implementer must not
"optimise" it back to a symlink.

### §4.2 The declared inputs, and where the declaration lives

Two entries: `corpus/` and `baml_client/`, each carrying **why it is absent from a checkout**
(gitignored-and-fetched; gitignored-and-generated).

**The declaration lives in the instrument, not in `tests/arc-manifest.ttl`.** Two reasons, and the
first is binding: Global Constraint 4 of the previous loop — *code never writes
`tests/arc-manifest.ttl`* (`arc-manifest.ttl:16-18`) — and more fundamentally, *"this repo's test
environment needs a generated client"* is *not a claim about the arc*. Putting it in the manifest
would make the graph assert something it does not know.

### §4.3 Materialisation is best-effort; the control run is what makes it demand-driven

**This differs from the obvious design and the difference matters.** The tempting form is a
mapping — *"`test_corpus.py` requires `corpus/`"* — consulted to decide what to materialise and
to fail loudly when it is missing. Rejected: that mapping is hand-maintained, drifts silently, and
is the shape CLAUDE.md's neurosymbolic gate calls prima facie evidence of a decision in the wrong
place.

The shipped form needs no mapping:

1. **Materialise every declared input that exists in the main tree.** Best effort. An input absent
   from the main tree is not an error — it is simply not copied.
2. **Run the control.** Endpoint oracles, un-ablated, in the materialised worktree.
3. **A control failure raises**, and the message names the failing node id, its outcome, and
   which declared inputs were and were not materialised — so a developer who has never run
   `scripts/fetch_corpus.py` gets *"corpus/ not materialised (absent from the main tree); run
   `scripts/fetch_corpus.py`"* rather than a bare red.
4. Only then ablate and score, unchanged.

**Demand is discovered, never declared.** A machine without a corpus and a manifest with no
corpus-dependent endpoint materialises nothing, needs nothing, and behaves exactly as today —
which is the case for all **6** currently-asserted edges, none of which has an `etkl` end
(§2.4). The moment an `etkl` edge is asserted, the same machine gets a loud, actionable raise.
This is CLAUDE.md § R89's producer-side guard: fail at the call site that can fix it.

### §4.4 The disjointness invariant

> **The set of materialised paths and the set of ablatable artifact paths must be disjoint.**

Enforced as a producer-side guard that raises **before** the first worktree is created, naming the
colliding path. Not a comment, not a test-only assertion.

Today it holds vacuously — the 29 declared artifact files live under `tests/` (9), `examples/`
(12) and `vocab/` (8), and none under `corpus/` or `baml_client/` (§11.2). It is exactly that
vacuity that makes it worth enforcing: the day someone declares a `prog:oracleArtifact` under
`corpus/`, the materialiser would restore the file the ablation had just deleted and **every arm-1
run would go silently green**. That is a false-assertion path, and it must be closed by a raise
rather than by the observation that nobody has done it yet.

### §4.5 One control worktree, not one per endpoint

The control deletes nothing, so a single worktree serves every endpoint in an
`ablation_refusals` invocation: create it once, materialise once, run the union of endpoint
oracle ids, tear down. Cost today ≈ one worktree + ~5 s; with an `etkl:01` endpoint, + ~164 s
once — not once per edge. The ablation's existing per-criterion grouping (C2 of the previous
loop) is untouched.

## §5 Where each rule lives — and why this loop adds no new M-number

`tests/arc-shapes.ttl` gains **nothing**. This loop introduces no membrane refusal, and the
reason is a distinction the previous loop already drew and this one must not blur:

| kind | means | mechanism | home |
| --- | --- | --- | --- |
| **refusal** | *the graph asserts something the evidence will not support* | a message, collected and returned | `arc-shapes.ttl` (M12–M18) / `test_arc_ablation.py` (M19) |
| **instrument failure** | *the instrument cannot judge at all* | `RuntimeError` with the transcript | `test_arc_ablation.py` only |

A control-run failure and a disjointness collision are both **instrument failures**. Neither is
statable over the graph — SHACL cannot see whether a directory exists on the machine running it —
and dressing either as an "M20" would put a closed-world constraint on an open-world fact about
the filesystem, which CLAUDE.md's gate forbids in as many words. (**M20 is already spoken for** by
[[R116]]'s orphan-rationale candidate; this loop must not take that number.)

What *does* change in M19: F1's *"did not execute"* refusal path (`:353-355`, `:365-367`) becomes
**unreachable via a missing environment input**, because the control raises first. It stays
reachable for a genuine `XFAIL`/`XPASS`, and its existing terminal-width test must still pass.

## §6 CI — a second job, and the maintainer's ruling on why

**Ruled by the maintainer, 2026-08-23, over three stated alternatives:** CI fetches the corpus, in
a **dedicated job**, rather than declaring capability in the graph or asserting on one machine.

- A new job installs, generates `baml_client`, fetches the corpus **through a cache keyed on the
  tracked `cor:sha256` pins** in `tests/corpus-manifest.ttl`, and runs the corpus leg plus M19's
  ablation. The cache key is the pin set, so the network is touched only on a miss.
- **The existing job is unchanged** — bare `pytest -q`, corpus absent, same pass/fail surface. The
  209 tests of §2.5 do not move into it.
- A dead third-party URL therefore turns **one clearly-named job** red, with a message about
  fetching, instead of failing every build for a reason unrelated to the change under test.

**The maintainer was told the cost and chose it**: a live external dependency on rot-prone
third-party URLs enters CI. The containment above is the mitigation, and the residue row this
loop writes must state the exposure plainly rather than treat the cache as a solution to rot.

## §7 The reading, and what it may honestly yield

With the instrument faithful, `etkl:01`'s **16** A3/A6-clean met partners (§2.4) are re-read for
dependency, and whatever grounds is authored at the grade the membrane permits — asserted via
`prog:dependsOn` where M19's two arms ground it, proposed with exactly one `rdf:Statement`
rationale otherwise, per the previous loop's settled vocabulary.

**The result may be zero asserted edges, and zero ships as a result.** The previous loop's author
already swept all 43 criteria and recorded nine readings rejected with a stated reason
(`2026-08-22-arc-edges-authored.md` §1), `etkl` among them — so a re-read that finds nothing is
*confirmation*, not omission. What changes is that the finding would then rest on a measurement
rather than on a routing-around, which is the whole of R114's *"the routing is a hand discipline
recorded in prose."*

**The reading is written before the ablation is run**, and the loop's evidence must show that
ordering the only way one commit can: by including candidate readings the membrane can never
ground.

## §8 What this loop does NOT do

- **It does not make the `etkl` rung assertable.** §2.4: A6 forbids it permanently. Only
  `etkl:01`'s cross-rung ends are reachable.
- **It does not fix F3.** The editable-install non-hermeticity stays declared, with zero live
  artifacts, its census corrected (§11.2). Fixing it means an isolated install per worktree, which
  costs more than the hazard is worth while no artifact lives under `src/`.
- **It does not close** [[R113]] (file granularity), [[R115]] (the orphan question),
  [[R116]] (M20), [[R117]] (the alignment-declaration gap), [[R119]] (`addopts`) or
  [[R120]] (the uncommitted census). R118 is closed only in its **live mechanism**; its general
  form — *read the ERROR's exception, not merely its existence* — is a strictly stronger remedy
  than the control run and stays open unless the implementer closes it too.
- **It touches no `prog:met` value**, adds no criterion, and does not mirror the register into
  the graph.
- **It does not speed up the suite.** It adds ~164 s to any M19 run with an `etkl:01` endpoint,
  and a job to CI.

## §9 The falsifying oracle, and what failure looks like

**The loop's headline claim:** *`etkl:01`'s oracle, inside a worktree M19 actually creates,
reports `PASSED` — not `SKIPPED`.* Measured today at 164.37 s under a hand-built symlink probe
(§2.3); the loop must reproduce it through the shipped copy-based path.

Three falsifications, each mandatory per CLAUDE.md § Plan authoring rule 4:

1. **Delete the materialisation step.** The control run must go **red naming the missing input**,
   and the ablation must not proceed. If the suite stays green, the control pins nothing.
2. **Declare a `prog:oracleArtifact` under `corpus/` in a fixture.** The disjointness guard must
   raise **before** any worktree is created. If it raises later — or not at all — §4.4 is prose.
3. **Point a declared input at a path absent from the main tree.** Materialisation must stay
   silent, and the control must still pass, because no endpoint needed it (§4.3). If this raises,
   the design is declared-demand and not discovered-demand, and every developer without a corpus
   gets a red suite for nothing.

**What a real failure of this spec looks like**, stated so it is recognised rather than explained
away: the control run passes, the ablation runs, and `etkl:01` still yields no edge — leaving a
164-second cost and a CI job bought for nothing. That outcome is **acceptable and must be
reported as-is** (§7). The *unacceptable* outcome is an asserted `etkl` edge whose arm-1 evidence
is a `FAILED` that the control never checked.

## §10 Definition of done

1. `etkl:01`'s oracle reports `PASSED` inside a worktree created by the shipped `_ablate`, with
   the transcript in the loop's evidence.
2. `pytest --collect-only -q` inside that worktree reports **0 collection errors** (from 6).
3. The control run is implemented, and a node id failing it **raises** with the transcript rather
   than being scored — pinned by a test, with falsification 1 above.
4. The disjointness guard raises before worktree creation — pinned, with falsification 2.
5. Best-effort materialisation confirmed non-fatal — pinned, with falsification 3.
6. `ablation_refusals` over the **live** manifest still returns `[]`, and the real tree is
   `git status --porcelain`-clean before and after.
7. **MEASURE box for the plan, not answered here:** the wall-clock and pass/fail delta of the new
   CI job — run the corpus leg on a corpus-present tree and report it. §2.5's 209 is an envelope,
   not a prediction, and the job's real cost must be measured before the workflow is committed.
8. `etkl:01`'s 16 partners re-read; every edge found authored at the membrane's grade; **the count
   stated whatever it is, zero included.**
9. R118's row corrected to 6, and limitation 4's census corrected to 29 (§11) — in the tracked
   artifacts, not only in this spec.
10. The residue row for the CI corpus fetch written, stating the rot exposure plainly (§6).

## §11 Corrections to the record this loop owes

Both were found by re-deriving a number this repo already had in writing, which is the method
CLAUDE.md § Plan authoring rule 2 exists to force.

### §11.1 [[R118]] says five modules; there are six

§2.2. `tests/test_to_rdf.py` breaks transitively through `src/iladub/extract_baml.py:8`. R118's
amendment enumerated module-scope `baml_client` imports and a transitive importer is invisible to
that method. `.github/workflows/ci.yml:23` already carries the correct 6.

### §11.2 `test_arc_ablation.py` limitation 4 cites 35 artifacts; there are 29

The docstring (`:87-111`) states *"all 35 `prog:oracleArtifact` values live under `vocab/` (14),
`examples/` (12), `tests/` (9)"*. Measured over all 43 criteria with `graph.objects()`:

```
distinct artifact FILES across all 43 criteria: 29
by top dir: {'tests': 9, 'examples': 12, 'vocab': 8}
any under src/: []
raw oracleArtifact TRIPLES: 48
```

`examples` 12 and `tests` 9 match; **`vocab` is 8, not 14, and the total is 29, not 35.** The 14
is the *triple* count for `vocab/` — the citation mixes one namespace counted as triples with two
counted as distinct files.

**The claim limitation 4 actually rests on is correct**: zero artifacts under `src/`, confirmed
independently here, so F3 has no live instance and no conclusion drawn from limitation 4 is
affected. The census beside it is wrong, and this is [[R120]]'s shape — a load-bearing number
in shipped source that nobody could re-derive — one file over from where R120 found it.

---

## Appendix — the four rejected designs, with the reason each was rejected

Recorded so a later session does not re-derive them. The first three were put to the maintainer
as explicit alternatives on 2026-08-23; the fourth was rejected on measurement.

| rejected | why |
| --- | --- |
| **Declare capability in the graph** (`prog:requiresEnvironment`, grade an unrunnable edge down to a proposition) | Coherent and closed-world, but it ships **no asserted `etkl` edge ever** and encodes a fact about the CI environment into a graph about the architecture. Maintainer chose the CI fetch instead. |
| **Assert locally, record "not judged" in CI** | The strongest edges in the graph would rest on a leg that ran on exactly one machine. This is the false-green shape the repo has paid for repeatedly. |
| **One CI job, fetch everything** | Simplest and most honest, but moves 209 tests (§2.5) and an unmeasured wall-clock into the build in the same change that fixes an instrument, and surfaces any skip-hidden failure as this loop's red. |
| **A committed synthetic stand-in document** (R114 remedy (b)) | `etkl:01`'s oracle would then measure a different document than the criterion was declared against (`tests/corpus-manifest.ttl:24-44`, sha256-pinned to a specific edition). That changes what the criterion **means** — an epistemic cost, not an engineering one. |
| **Symlink rather than copy** | `_ablate` unlinks declared artifacts; through a symlinked directory that deletes the real file in the main tree, and the corpus cannot be re-fetched (§4.1). |
| **A declared oracle→input mapping** | Hand-maintained, drifts silently, and makes every corpus-less developer's suite red for an input nothing needed. The control run discovers demand instead (§4.3). |
