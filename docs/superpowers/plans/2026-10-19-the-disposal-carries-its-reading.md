# The disposal carries its reading — Implementation Plan

**Serves:** prog:criterion:tab:07 — `prog:met false` at `0280030` (`tests/arc-manifest.ttl:1359`).

**Doc impact: none.** Same as the spec: test-side shapes, an internal vocabulary term, manifest
rows, register rows.

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task by task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Meet `tab:07` by disposing of KIND_NOT_SUPPORTED on bfs and ons, with D2 judged at each
disposal's own dated reading (R323 as ruled).

**Architecture:** A new procedural lift, `lift_snapshots`, reads the git blob a disposal names and
attaches that reading's firings, its document and its durability to the disposal's `cor:Snapshot`
node. D2 (`cor:DisposalShape`) then judges each disposal against its own snapshot, never against
the current baseline.

**Tech stack:** rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), `git` subprocesses, pytest.

**Spec:** `docs/superpowers/specs/2026-10-19-the-disposal-carries-its-reading-design.md`. Every
design decision is argued there. This plan **cites** it (`spec § n`) and does not restate it
(CLAUDE.md plan rule 6).

## Global Constraints

- CLAUDE.md § 8 gate: the classifications are spec § 4.1. Any decision code beyond them is a defect.
- No implementation source in this plan (plan rule 1). Tests are given where they are the contract.
  **Every plan-supplied test is a proposition until its task's FALSIFICATION block shows it failing
  with its subject removed** (rule 4). If a supplied test cannot be made to pass as written, say so
  in the task report and substitute the satisfiable form with the same force. Never weaken it (rule
  5 precedent).
- Cite symbols, not lines, for downward same-file references (rule 7). Re-measure every `file:line`
  you write **after** the edit.
- Never at import of `tests/test_corpus.py` (spec § 4.3, R325): `lift_snapshots` is not called there.
- `scripts/corpus_baseline.py regenerate` runs once, after the **last** `vocab/` edit, serially,
  with nothing else running (CLAUDE.md § Corpus baseline).
- Evidence files are append-only. Manifest adjudications are appended, never edited (spec § 4.5).
- Branch, PR, green `test` check. No direct push to `main`.

## Task 0 — the CI probe (DONE 2026-10-19, before this plan was written)

Spec § 8's open premise asked whether the PR checkout carries `origin/main`. It was probed by throwaway
draft PR #356 (closed unmerged), with a step before install, run `39192986440`:

```
+ git rev-parse HEAD HEAD^1 HEAD^2
ba1abe25…   02800300…   66fd9219…        ← merge ref; first parent = origin/main
+ git rev-parse --verify origin/main
02800300b51d2ee6ac429b5de570d6e339a6e57c
+ git log --first-parent --oneline -3 origin/main
0280030 … (#353)   cbacae6 … (#352)   25ff1bd … (#351)
+ git log --first-parent --raw --no-abbrev --format=%H -2 origin/main -- tests/corpus-baseline/bfs-population-bilan-2023.json
ff2c0de3…  :100644 100644 f99d3e68… 626eef5f… M
fc0c24a5…  :000000 100644 0000000… f99d3e68… A
```

**The premise holds.** `origin/main` exists on a `pull_request` event, with full first-parent
history and `--raw` blob shas. No `ci.yml` change is needed. Not probed: the `push: main` event.
`actions/checkout` with `fetch-depth: 0` fetches every branch, so it is expected to hold there too.
That is unverified and is listed under § Unverified.

## Review Focus

Spec § 5 has no test for any of these five. Each is pinned in the task named.

1. **`origin/main` absent** (a fresh clone with no remote, or a detached CI). The lift must raise.
   It must not fall back to HEAD's chain (spec § 4.3). → Task 1, `test_snapshot_without_origin_main_raises`.
2. **Cache leaking across repos.** The per-path history cache, if keyed on path alone, would let
   one `tmp_path` repo's history answer for another or for `_REPO`. → Task 1,
   `test_durability_cache_does_not_cross_repos`.
3. **A manifest with no `cor:judgedAgainst`** (main today, before Task 4). `lift_snapshots` must
   return an empty graph without touching git, so that `test_manifest_conforms` does not start
   depending on `origin/main` before any disposal does. → Task 1, `test_no_snapshots_needs_no_git`.
4. **One negative, one message.** A disposal refused by constraint 1 must not also report
   constraints 2–4. Otherwise "assert which message refused" is unreadable. → Task 2: constraints
   2–4 range only over an existing `judgedAgainst`; every negative asserts an exact message set.
5. **The intermediate blob of the implementer's own branch.** Locally, a baseline committed and then
   overwritten on the feature branch resolves but is not durable. → Task 1, `test_intermediate_branch_blob_is_not_durable`.

---

### Task 1: `lift_snapshots`

**Files:**
- Modify: `tests/corpus_firings.py` (`lift_firings`, `live_pairs`, new `lift_snapshots`)
- Test: `tests/test_corpus_firings.py`

**Interfaces:**
- Produces: `lift_snapshots(manifest: Graph, repo: Path = _REPO) -> Graph`. It returns only the
  lifted triples. For each `(adj, cor:judgedAgainst, snap)` in `manifest`, it reads `snap`'s
  `cor:blob` and `cor:recordedIn` and attaches to `snap` itself (same BNode, spec § 8 A0):
  - one `cor:firing` per constant reason (`cor:Firing`, `cor:reason`, `cor:live`,
    `cor:superseded`, `cor:recordedIn "<path>@<blob>"`);
  - `cor:snapshotOf <doc>`;
  - `cor:durable "true"|"false"^^xsd:boolean`.
- Produces: `live_pairs` skips non-URIRef subjects.
- Unchanged: `lift_firings(manifest, baseline_dir) -> Graph`. It must produce an isomorphic graph to
  the one it produces today.

**Invariants** (spec § 4.3; not restated here, only listed):
- One counting core, shared by both lifts. It takes the `recordedIn` string as a parameter.
- An unresolvable blob raises. A `"pdf"` matching no manifest `cor:file` raises. A missing
  `origin/main` raises when, and only when, durability must be decided.
- `durable` is true iff the blob equals `git rev-parse HEAD:<path>` in `repo`, or appears as a
  post-image blob of `<path>` in `git log --first-parent --raw --no-abbrev origin/main -- <path>`.
  There is one history query per (repo, origin/main sha, path), and it is cached.
- No git subprocess runs when the manifest holds no `cor:judgedAgainst`.

**Seam to MEASURE before writing:** how `git log --raw` reports the post-image when a commit deletes
the path (`000000…` post-image). A deleted path's all-zero sha must never match a blob. Also measure
the cache's added cost in Task 2 (spec § 6). Do not assume it.

- [ ] **Step 1: Write the failing tests.** Add a `tmp_path` repo fixture and the tests below. The
  fixture is test glue, given here because it is the contract the R323 test (Task 2) also uses.

```python
import json, subprocess
from rdflib import Literal, URIRef
from rdflib.namespace import XSD
from tests.corpus_firings import lift_snapshots

_DOC = "urn:d:a"
_PATH = "tests/corpus-baseline/a.json"


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _baseline(regions):
    return json.dumps({"pdf": "corpus/fam/a.pdf", "pages": [{"regions": [
        {"reason": r, "verdict": v} for r, v in regions]}]})


def _commit(repo, regions, msg):
    p = repo / _PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_baseline(regions))
    _git(repo, "add", _PATH)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", f"HEAD:{_PATH}")


def _repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    return tmp_path


def _publish(repo):
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


def _manifest(blob, path=_PATH):
    return Graph().parse(data=f"""@prefix cor: <https://w3id.org/iladub/corpus#> .
        <{_DOC}> a cor:Document ; cor:file "fam/a.pdf" ;
            cor:adjudication [ cor:disposes "R_X" ;
                cor:judgedAgainst [ a cor:Snapshot ; cor:recordedIn "{path}" ;
                                    cor:blob "{blob}" ] ] .""", format="turtle")


def _snap(g):
    return next(g.subjects(COR.snapshotOf, URIRef(_DOC)))


def test_snapshot_lifts_the_firings_of_its_own_blob(tmp_path):
    repo = _repo(tmp_path)
    old = _commit(repo, [("R_X", "escalated"), ("R_X", "escalated"), ("R_Y", "superseded")], "1")
    _commit(repo, [], "2")                     # the current baseline no longer fires R_X
    _publish(repo)
    g = lift_snapshots(_manifest(old), repo=repo)
    s = _snap(g)
    by_reason = {str(g.value(f, COR.reason)): f for f in g.objects(s, COR.firing)}
    assert sorted(by_reason) == ["R_X", "R_Y"]
    assert int(g.value(by_reason["R_X"], COR.live)) == 2
    assert int(g.value(by_reason["R_Y"], COR.superseded)) == 1
    assert {str(o) for o in g.objects(by_reason["R_X"], COR.recordedIn)} == {f"{_PATH}@{old}"}
    assert g.value(s, COR.durable) == Literal(True)        # historical, on origin/main


def test_intermediate_branch_blob_is_not_durable(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "base")
    _publish(repo)
    _git(repo, "checkout", "-q", "-b", "feat")
    mid = _commit(repo, [("R_X", "escalated"), ("R_X", "escalated")], "mid")
    head = _commit(repo, [("R_X", "escalated")] * 3, "head")
    assert lift_snapshots(_manifest(mid), repo=repo).value(None, COR.durable) == Literal(False)
    assert lift_snapshots(_manifest(head), repo=repo).value(None, COR.durable) == Literal(True)


def test_unresolvable_blob_raises(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    with pytest.raises(Exception):
        lift_snapshots(_manifest("0" * 40), repo=repo)


def test_snapshot_of_an_unknown_pdf_raises(tmp_path):
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    m = _manifest(blob)
    m.remove((URIRef(_DOC), COR.file, None))
    m.add((URIRef(_DOC), COR.file, Literal("fam/other.pdf")))
    with pytest.raises(ValueError, match="corpus/fam/a.pdf"):
        lift_snapshots(m, repo=repo)


def test_snapshot_without_origin_main_raises(tmp_path):           # Review Focus 1
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _commit(repo, [], "2")                                         # blob is not HEAD's
    with pytest.raises(Exception, match="origin/main"):
        lift_snapshots(_manifest(blob), repo=repo)


def test_durability_cache_does_not_cross_repos(tmp_path):          # Review Focus 2
    (tmp_path / "a").mkdir(); (tmp_path / "b").mkdir()
    a, b = _repo(tmp_path / "a"), _repo(tmp_path / "b")
    x = _commit(a, [("R_X", "escalated")], "1"); _commit(a, [], "2"); _publish(a)
    _commit(b, [], "1"); _publish(b)
    # the same bytes stored in b as a loose object: resolvable there, on no commit of b's main
    loose = tmp_path / "x.json"
    loose.write_text(_baseline([("R_X", "escalated")]))
    assert _git(b, "hash-object", "-w", str(loose)) == x
    assert lift_snapshots(_manifest(x), repo=a).value(None, COR.durable) == Literal(True)
    assert lift_snapshots(_manifest(x), repo=b).value(None, COR.durable) == Literal(False)


def test_no_snapshots_needs_no_git(tmp_path):                      # Review Focus 3
    m = Graph().parse(data='@prefix cor: <https://w3id.org/iladub/corpus#> .\n'
                           '<urn:d:a> a cor:Document ; cor:file "fam/a.pdf" .', format="turtle")
    assert len(lift_snapshots(m, repo=tmp_path / "not-a-repo")) == 0


def test_live_pairs_ignores_snapshot_subjects(tmp_path):
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    assert live_pairs(lift_snapshots(_manifest(blob), repo=repo)) == []
```

  `test_durability_cache_does_not_cross_repos` relies on git's content addressing: the same bytes
  get the same blob sha in both repos. The repo-`a` call runs first, so a cache keyed on `path`
  alone answers repo `b` from `a`'s history. Its falsification is that key.

- [ ] **Step 2: Run them and see them fail.** `PYTHONPATH=src .venv/bin/python -m pytest
  tests/test_corpus_firings.py -q`. Expected: ImportError on `lift_snapshots`, or FAIL.
- [ ] **Step 3: Implement** to the interface and invariants above. Update the module docstring's
  § 8 classification to cover the git read (spec § 4.1 row 3).
- [ ] **Step 4: Run the file, then the whole always-on suite** (`-n auto -m "not serial"`). Read
  `N passed`, not the exit code. `lift_firings`' existing tests must pass unchanged.
- [ ] **Step 5: FALSIFICATION.** For each of: the cached-history clause of `durable`, the
  HEAD-tree clause, the unresolvable-blob raise, the origin/main raise, the URIRef filter in
  `live_pairs` and the cache key. Remove or invert it, show the named test failing, restore with
  `cp` from a saved copy, and show the file green.
- [ ] **Step 6: Commit.**

### Task 2: vocabulary and D2 at the disposal's own reading

**Files:**
- Modify: `vocab/internal/corpus.ttl` (spec § 4.2)
- Modify: `tests/corpus-shapes.ttl` (`cor:DisposalShape` and its rationale comment, spec § 4.4)
- Modify: `tests/test_corpus_manifest.py` (`test_manifest_conforms`, `_with_disposal`, D2 tests)
- Modify: `tests/test_corpus_firings.py` (`test_real_lift_conforms_to_firing_shape`)
- Modify: `tests/test_artifact_terms.py` (census pin)

**Interfaces:**
- Consumes: `lift_snapshots` (Task 1), and the Task 1 test fixture (`_repo`, `_commit`, `_publish`).
  Import it or move it to a shared test module. Do not copy it.
- Produces: `_with_disposal(doc_iri, reason, snapshot_of=None) -> Graph`. It returns the real
  manifest plus an injected disposal whose `cor:judgedAgainst` is a `cor:Snapshot` of
  `snapshot_of or doc_iri`'s baseline file at `git rev-parse HEAD:<path>`. Then it adds
  `lift_firings` and `lift_snapshots`, the latter **after** the injection.
- Produces: `_d2_refusals(g: Graph) -> set[str]`, the `sh:resultMessage` of every result whose
  `sh:sourceShape` is `cor:DisposalShape` or one of its `sh:property` shapes.
- The four messages, verbatim. Shape and tests both use these strings:
  - M1 `"cor:disposes without exactly one cor:judgedAgainst snapshot"`
  - M2 `"cor:judgedAgainst names a snapshot of a different document than the one holding this adjudication"`
  - M3 `"cor:judgedAgainst names a snapshot that is not durable on main"`
  - M4 `"cor:disposes names a reason with no LIVE cor:firing in the snapshot this adjudication was judged against"`

**Invariant (Review Focus 4):** M2–M4 bind an existing `?snap` via `$this cor:judgedAgainst ?snap`.
A disposal without one yields exactly `{M1}`.

**Seams to MEASURE before writing:**
- The census figures. The A9 prediction (72/78 → 75/81, or +1 each if constraint 3 is written as
  `sh:path cor:durable`) is a proposition. Run the census and pin what it says, with the reason in
  the comment beside the existing two.
- That the synthetic document below conforms to every **non-D2** shape. Run it with the D2 shape
  removed before relying on it as a positive.
- `git rev-parse HEAD:<path>` from `_with_disposal`. In CI the checkout is a merge ref, whose HEAD
  tree holds the PR's baseline (Task 0).

- [ ] **Step 1: Write the failing tests.** Change every existing D2 test in
  `tests/test_corpus_manifest.py` to assert an exact refusal set:
  - positives (`test_admits_disposal_of_a_live_firing`, `…_typed_xsd_string`) assert `ok` **and**
    `_d2_refusals(g) == set()`;
  - unfired, misspelt, superseded-only, wrong document and `@en` assert `_d2_refusals(g) == {M4}`.

  Then add:

```python
def test_refuses_disposal_without_a_reading():
    g = Graph().parse(MANIFEST, format="turtle")
    g.parse(data=PREFIXES + f'<{BFS}> cor:adjudication [ cor:by "t" ; '
            'cor:on "2026-10-19"^^xsd:date ; cor:rationale "t" ; '
            'cor:disposes "KIND_NOT_SUPPORTED" ] .', format="turtle")
    g += lift_firings(g, BASELINE)
    g += lift_snapshots(g)
    assert _d2_refusals(g) == {M1}


def test_refuses_disposal_judged_against_another_documents_reading():
    # ons fires KIND_NOT_SUPPORTED live too, so only constraint 2 can refuse this
    assert _d2_refusals(_with_disposal(BFS, '"KIND_NOT_SUPPORTED"', snapshot_of=ONS)) == {M2}


def _synthetic(blob):
    return Graph().parse(data=PREFIXES + f"""
        <urn:d:a> a cor:Document ; cor:file "fam/a.pdf" ; cor:url "https://example.org/a" ;
            cor:series "s" ; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ;
            cor:adjudication [ cor:by "t" ; cor:on "2026-10-19"^^xsd:date ; cor:rationale "t" ;
                cor:disposes "R_X" ;
                cor:judgedAgainst [ a cor:Snapshot ;
                    cor:recordedIn "tests/corpus-baseline/a.json" ; cor:blob "{blob}" ] ] .""",
        format="turtle")


def _lifted(m, repo):
    return m + lift_firings(m, repo / "tests" / "corpus-baseline") + lift_snapshots(m, repo=repo)


def test_r323_disposal_is_judged_at_its_own_reading(tmp_path):     # spec § 5, R323 as ruled
    repo = _repo(tmp_path)
    old = _commit(repo, [("R_X", "escalated")], "fires")
    _commit(repo, [], "repaired")                                  # 0 live NOW
    _publish(repo)
    g = _lifted(_synthetic(old), repo)
    ok, report = _conforms(g)
    assert ok and _d2_refusals(g) == set(), report


def test_refuses_disposal_whose_own_reading_holds_no_live_firing(tmp_path):
    repo = _repo(tmp_path)
    old = _commit(repo, [("R_X", "superseded")], "1")
    _publish(repo)
    assert _d2_refusals(_lifted(_synthetic(old), repo)) == {M4}


def test_refuses_disposal_judged_against_a_non_durable_reading(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "base")
    _publish(repo)
    _git(repo, "checkout", "-q", "-b", "feat")
    mid = _commit(repo, [("R_X", "escalated")] * 2, "mid")         # the #354-shaped blob
    _commit(repo, [("R_X", "escalated")] * 3, "head")
    assert _d2_refusals(_lifted(_synthetic(mid), repo)) == {M3}
```

  Add `lift_snapshots(manifest)` to `test_manifest_conforms` and to
  `test_real_lift_conforms_to_firing_shape` (spec § 4.3 call sites).

- [ ] **Step 2: Run and see them fail.** The positives fail first, on the new tests' imports.
- [ ] **Step 3: Implement.** Vocabulary terms per spec § 4.2: the two domain widenings are
  documentation, so do not write a test for them (A7). Rewrite D2 per spec § 4.4 with M1–M4, and
  rewrite its rationale comment citing the spec and R323, **keeping** the value-equality paragraph.
  Then `_with_disposal` and `_d2_refusals`.
- [ ] **Step 4: Run** `tests/test_corpus_manifest.py`, `tests/test_corpus_firings.py`,
  `tests/test_corpus_is_disposed.py` and `tests/test_artifact_terms.py`, then the always-on suite.
  Record the suite wall time and compare it with `main`'s for the same command (spec § 6, "measure
  the added test time").
- [ ] **Step 5: FALSIFICATION.**
  - Point constraint 4's join back at `?doc cor:firing`. `test_r323_…` fails.
  - Drop each of constraints 1–4 in turn. Its named negative fails.
  - Make M2–M4 not bind `?snap`. `test_refuses_disposal_without_a_reading` fails, because its set
    is no longer `{M1}`.
  - Restore by `cp` and show the suite green.
- [ ] **Step 6: Commit.** `git add` every new or modified `vocab/` file **before** Task 3.

### Task 3: regenerate the corpus baseline

**Files:** `tests/corpus-baseline/**` (generated).

- [ ] **Step 1:** Confirm that no `vocab/`, `src/`, `readings/`, `pyproject.toml` or
  `scripts/corpus_*` edit is still pending (`git status`). Confirm nothing else is running (no
  pytest, no compile).
- [ ] **Step 2:** `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`. This is
  about 24 minutes, serial and unattended. Block on it in-turn rather than idling on a background
  wait.
- [ ] **Step 3: Measure the blast radius:** `git diff --stat -- tests/corpus-baseline/`. Spec § 8
  predicts that only `inputs.json` moves. Record what actually moved. If any document's JSON moved,
  stop and report it: the vocab edit was supposed to be inert, and something reads it.
- [ ] **Step 4:** Commit, then record the blob for each file:
  `git rev-parse HEAD:tests/corpus-baseline/bfs-population-bilan-2023.json` and the same for
  `ons-index-of-services-2026-02.json`. On `main` (`0280030`) they are `626eef5f…` and `8f913d5c…`.
  If the bytes are unchanged, they are those, and they are durable before this PR merges.

### Task 4: the two disposals, and the pins they break

**Files:**
- Modify: `tests/corpus-manifest.ttl` (append only)
- Modify: `tests/test_corpus_is_disposed.py`

- [ ] **Step 1: Read the bands, not the spec's table.** The baseline JSON does not carry the text.
  Measured: KIND regions carry only `anchor, cells, kind, reason, table, verdict`. `band_text`
  (`src/iladub/etkl/bands.py`, symbol `band_text`) is applied in `compile_tables`. Re-render each of
  the five bands (spec § 3) by a per-page compile, and quote what the page says.
- [ ] **Step 2: Append two adjudications** at the end of the manifest, using the separate-statement
  convention its cbh-stem block documents (the comment above `<urn:iladub:corpus:cbh-stem-2026-08-03>`
  near the end of the file): no existing line moves. Each carries the content of spec § 4.5, with
  `cor:judgedAgainst` naming the Task 3 blob. `cor:by` follows the house form: "composed by Claude
  … (agent) on branch …; the accountable human sign-off is François Rosselet's review and merge of
  the commit that carries this node".
- [ ] **Step 3: Measure the breakage the spec predicts (A2).** Run `tests/test_corpus_is_disposed.py`.
  Record which tests fail. The spec predicts four failures, plus one test that goes vacuous. The
  vacuous one cannot show red, so show it by deleting its injection and seeing it still pass.
- [ ] **Step 4: Re-target** per spec § 4.3. The single-pair pins move to bfs `DATAGRID_RESIDUE`,
  which is live and undisposed (measured: `live_pairs(ADJUDICATED)` holds bfs and ons
  `DATAGRID_RESIDUE`). The other-document pin injects on ons `DATAGRID_RESIDUE` and asks about bfs.
  Rewrite its comment. The agreement test validates over a manifest from which the adjudications
  disposing of `(doc, reason)` are removed, so that `@en` compares like with like. Add one test that
  pins the URIRef filter of `live_pairs` on the **real** manifest ∪ snapshots: no BNode appears.
- [ ] **Step 5: The oracle.** Run `PYTHONPATH=src .venv/bin/python -m pytest -rA
  "tests/test_corpus.py::test_escalation_reasons_are_adjudicated" -q`. The bfs and ons
  KIND_NOT_SUPPORTED params must read **PASSED**, not XPASS and not xfail. Quote the lines.
- [ ] **Step 6: FALSIFICATION.**
  - Delete the bfs disposal. Its param is xfail again, and `test_manifest_conforms` still passes.
  - Swap the ons blob for an intermediate commit's blob from your own branch. `test_manifest_conforms`
    refuses with M3.
  - Delete each re-targeted pin's injection. The pin fails.
  - Restore and show it green.
- [ ] **Step 7: Commit.**

### Task 5: the criterion and the register

**Files:** `tests/arc-manifest.ttl`, `docs/superpowers/residues.md`,
`docs/superpowers/residues-open.md` (and `residues-closed.md` if that is where struck rows go:
measure the R259 precedent).

- [ ] **Step 1:** Do spec § 4.6 in one edit. Set `met true` and `metOn`, and replace the
  `blockedBy` edges with a comment in the R166 form, re-arguing R44/R71 in your own words. Fix the
  `:1351` comment. Re-cite the statement's emitter as the symbol `compile_tables`: measured, the
  `"KIND_NOT_SUPPORTED"` literals sit at `src/iladub/etkl/compile.py:1880-1890`, inside the `def`
  at `:1189`. **Confirm that enclosure yourself**, because a nested `def` would make the awk measure
  wrong. Read the editing rules at the head of the file first.
- [ ] **Step 2:** Do spec § 4.7. Strike R323 with its closure evidence. Append a dated correction to
  R44. Raise the band-level relevance row with its `(c/t closed)` snapshot, counted at the moment it
  is raised.
- [ ] **Step 3:** `tests/test_arc_manifest.py` and the always-on suite. FALSIFICATION: restore one
  `blockedBy` and show M8 refusing.
- [ ] **Step 4:** Commit. Run `scripts/corpus_baseline.py check` (the CI gate). Open the PR. Its
  body states that the maintainer signs the disposals off by merging, and quotes the Task 4 Step 5
  PASSED lines.

## Unverified

- `origin/main` on the `push: main` event (Task 0). If it is absent there, `main`'s own CI fails on
  the first post-merge run, loudly, through the raise. It is not a silent failure.
- The census figures (A9) and the regenerate's blast radius (§ 8). Both are predictions, and both
  are measured in their tasks.
- Every plan-supplied test in Tasks 1–2. None was run while this plan was written. They are
  propositions until each task's FALSIFICATION shows them failing (Global Constraints).
- The per-call cost of `lift_snapshots` against roughly 25 call sites (spec § 6), which is measured
  in Task 2.
