# A firing is not a fact (R259): implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:tab:07. The shared oracle also serves `tab:02`, `tab:05`, `tab:08` and
`tab:09`.

**Doc impact: increment.** Terms are added to `cor:` in `vocab/internal/corpus.ttl`, which is
internal harness vocabulary. The spec carries the same declaration.

**Goal:** make *a reason fires on a document* and *an adjudication disposes of it* readable facts,
and write the shared oracle `tests/test_corpus.py::test_escalation_reasons_are_adjudicated` so that
the census stops reporting it as dangling.

**Architecture:** firings are **lifted in memory** from the committed corpus baseline
(`tests/corpus-baseline/*.json`) onto the manifest's `cor:Document` IRIs. That lift is PROCEDURAL raw
extraction. SHACL then validates the manifest ∪ lifted firings: D1 checks the lift's cardinalities,
and D2 refuses a `cor:disposes` that names no live firing (AXIOM, closed world). The oracle is
parametrised over the live (document, reason) pairs, each `xfail(strict=True)` until the manifest
disposes it.

**Tech Stack:** Python 3, rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), pytest.

**Spec:** `docs/superpowers/specs/2026-09-18-a-firing-is-not-a-fact-design.md`. Read **§ 8 and § 8.3
first**: they supersede § 2.1's authored record, § 2.2's closed list, § 3's I3 and § 5's O1/O4.
§§ 2.3, 3 (D1–D3a), 4, 5 (O2, O3, O5) and 6 stand as amended. This plan cites those sections and
does not re-derive them.

## Global Constraints

- CLAUDE.md § 8, the gate: the lift is **PROCEDURAL** (JSON → typed RDF, no judgment, no tolerance),
  and the code must say why in a docstring. D1 and D2 are **AXIOM / SHACL**. D3 and the census fix
  are **PROCEDURAL**, because they are runner facts (spec § 4). No NEURAL part, and no tuned constant.
- Firings are **never authored** (spec § 8). No `cor:firing` triple appears in any tracked `.ttl`.
- Scope is the 7 `corpus/` documents. They are discriminated by the baseline's `pdf` field, which is
  read, never hard-coded (spec § 8).
- The oracle and the lift **must not** carry `pytest.mark.corpus`. They read only committed files
  (spec § 8, § 8.3 seam 3).
- Nothing is disposed and no `prog:met` moves (spec § 6). No `cor:disposes` triple lands in
  `tests/corpus-manifest.ttl`.
- The manifest and the residue register are append-only. Do not edit an existing adjudication.
- `vocab/` is a corpus-baseline input. After the **last** input edit, regenerate the baseline once
  (CLAUDE.md § Corpus baseline). Never run it beside pytest.
- Every task report carries `## FALSIFICATION`: remove or invert what the test pins, show the RED,
  restore with `cp`, and show the suite green (CLAUDE.md plan rule 4).

## Review Focus

1. **A manifest document with no baseline file, or a `corpus/` baseline file with no manifest
   document.** The lift must **raise**, naming both sides. Silence would read as "fires nowhere",
   and spec § 2.1 forbids exactly that: no firing means *not measured*, not *zero*. Pinned in Task 2.
2. **A constant reason whose verdict is neither `escalated` nor `superseded`.** None exists at
   `04f2a72`. The lift must raise rather than drop it. Pinned in Task 2.
3. **`test_manifest_conforms` validating the manifest alone.** Once D2 exists, the first real
   `cor:disposes` would be refused because no firings are present. The conformance test must
   validate manifest ∪ lift. Pinned in Task 3.
4. **A literal-type mismatch in D2's join.** A `cor:disposes "X"` that differs from the lifted
   `cor:reason "X"` only in datatype or language would be refused, or worse, admitted by a
   value-vs-term slip (memory: RDF/SPARQL/SHACL traps). Pinned in Task 3 with the positive control.
5. **Running `-m "not corpus"` locally.** The oracle must collect and the three corpus tests must
   still be deselected. Pinned in Task 4.

---

## File structure

| file | responsibility |
| --- | --- |
| `vocab/internal/corpus.ttl` (modify) | declares `corpus:Firing`, `corpus:firing`, `corpus:reason`, `corpus:live`, `corpus:superseded`, `corpus:disposes`; widens `corpus:recordedIn`'s domain to admit `corpus:Firing` |
| `tests/corpus_firings.py` (create) | the lift: `lift_firings(manifest, baseline_dir) -> Graph`. It is a helper module, not a test module, so it follows the `tests/query_terms.py` precedent and is imported as `from tests.corpus_firings import …` |
| `tests/corpus-shapes.ttl` (modify) | D1 `cor:FiringShape` and D2 `cor:DisposalShape` |
| `tests/test_corpus_firings.py` (create) | the lift's tests, over synthetic baseline directories in `tmp_path` |
| `tests/test_corpus_manifest.py` (modify) | conformance over manifest ∪ lift; D1 and D2 negatives |
| `tests/test_corpus.py` (modify) | the tag moves from the module to the three corpus tests; adds D3 |
| `scripts/oracle_test_census.py` (modify) | resolves a bare id to its parametrised ids, using M5b's rule |
| `tests/corpus-baseline/inputs.json` (regenerated) | fingerprint only |
| `docs/superpowers/residues*.md` (append) | R259's closure evidence |

---

### Task 1: Vocabulary and D1, the lifted firing's shape

**Files:** modify `vocab/internal/corpus.ttl`, `tests/corpus-shapes.ttl`, `tests/test_corpus_manifest.py`.

**Interfaces:**
- Produces the terms (`cor:` = `https://w3id.org/iladub/corpus#`; the vocab file spells it `corpus:`):
  - `cor:firing`: `cor:Document → cor:Firing`, multi-valued.
  - `cor:Firing`: a class.
  - `cor:reason`: `→ xsd:string`.
  - `cor:live` and `cor:superseded`: `→ xsd:nonNegativeInteger`.
  - `cor:disposes`: subject is an adjudication node, `→ xsd:string`.
  - `cor:recordedIn`: reused, with its domain widened to admit `cor:Firing`.
- Each comment states the spec § 2.1 semantics (two counts, never one; superseded is not repaired)
  and § 8 (lifted, never authored).
- `cor:FiringShape`, targeted by `sh:targetObjectsOf cor:firing`: exactly one `cor:reason`
  (`xsd:string`), exactly one `cor:live` and one `cor:superseded` (`xsd:nonNegativeInteger`), and
  at least one `cor:recordedIn`.

**Seam to measure first:** does any test assert that every `cor:` term a shape names is declared
(`tests/artifact_terms.py`, `tests/query_terms.py`)? If one does, it covers the new terms, and the
report should say so. **Measure, do not assume:** does `rdfs:domain` on `corpus:recordedIn` cause
`inference="rdfs"` to type a firing as `cor:Reading` and fire `cor:ReadingShape` on it
(`tests/corpus-shapes.ttl:63-73`)? If it does, change the domain rather than the shape.

- [ ] **Step 1: Failing tests.** Append the following to `tests/test_corpus_manifest.py`. It reuses
  `_neg`, `_conforms` and `READING`'s document prefix pattern from that file:

```python
FIRING = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
          'cor:series "s" ; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
          'cor:firing [ %s ] .')
OK_FIRING = ('cor:reason "KIND_NOT_SUPPORTED" ; cor:live "3"^^xsd:nonNegativeInteger ; '
             'cor:superseded "0"^^xsd:nonNegativeInteger ; '
             'cor:recordedIn "tests/corpus-baseline/f.json"')


def test_admits_a_well_formed_firing():
    ok, report = _conforms(Graph().parse(data=PREFIXES + FIRING % OK_FIRING, format="turtle"))
    assert ok, report


def test_refuses_firing_without_live_count():
    _neg(FIRING % OK_FIRING.replace('cor:live "3"^^xsd:nonNegativeInteger ; ', ''))


def test_refuses_firing_with_a_negative_count():
    _neg(FIRING % OK_FIRING.replace('"0"^^xsd:nonNegativeInteger', '"-1"^^xsd:integer'))


def test_refuses_firing_with_two_reasons():
    _neg(FIRING % (OK_FIRING + ' ; cor:reason "DATAGRID_RESIDUE"'))


def test_refuses_untraceable_firing():
    _neg(FIRING % OK_FIRING.replace(' ; cor:recordedIn "tests/corpus-baseline/f.json"', ''))
```

- [ ] **Step 2:** Run `.venv/bin/python -m pytest tests/test_corpus_manifest.py -q`. Expected: the
  four `refuses_firing` tests FAIL, because no shape exists yet. `test_admits…` may already pass.
- [ ] **Step 3:** Declare the terms and `cor:FiringShape`.
- [ ] **Step 4:** Run the same command. Expected: all PASS, including the pre-existing tests.
- [ ] **Step 5: FALSIFICATION.** Delete each of `cor:FiringShape`'s property constraints in turn and
  show its negative go RED. Restore with `cp` and show green.
- [ ] **Step 6: Commit.** `R259 task 1: cor:Firing terms and D1 FiringShape`.

### Task 2: The lift

**Files:** create `tests/corpus_firings.py` and `tests/test_corpus_firings.py`.

**Interfaces:**
- Consumes: Task 1's terms.
- Produces: `lift_firings(manifest: rdflib.Graph, baseline_dir: pathlib.Path) -> rdflib.Graph`. It
  returns **only** the lifted triples, `<doc> cor:firing [ a cor:Firing ; cor:reason ; cor:live ;
  cor:superseded ; cor:recordedIn ]`, with one firing per (document, constant reason).
  `cor:recordedIn` is the baseline file's repo-relative path, for example
  `"tests/corpus-baseline/bfs-population-bilan-2023.json"`. Also produces
  `live_pairs(graph: rdflib.Graph) -> list[tuple[str, str]]`: the sorted (document IRI, reason)
  pairs whose `cor:live` > 0.

**Invariants. Each one gets a test, and the implementer writes the body:**
1. **Join (§ 8.3 seam 1).** A baseline file is in scope **iff** its `pdf` starts with `"corpus/"`.
   It joins the manifest `cor:Document` whose `"corpus/" + cor:file` equals `pdf`. `held-out/` files
   are ignored.
2. **Bijection.** If a manifest document has no in-scope baseline file, or an in-scope file has no
   manifest document, the lift **raises**, naming the unmatched side (Review Focus 1). `inputs.json`
   has no `pdf` field and is skipped by that fact, not by its filename.
3. **Constant reasons only.** A region's `reason` counts iff it fully matches `[A-Z][A-Z_]*`. That
   is the classifier § 8 measured, and it separates escalation constants from the free-text
   classification reasons in `regions._reason`. Free-text reasons are ignored.
4. **Verdict mapping.** `escalated` counts toward `cor:live` and `superseded` counts toward
   `cor:superseded`. Any other verdict on a constant reason **raises** (Review Focus 2).
5. A document with no constant-reason region gets **no** firing node. It is still *measured*,
   because invariant 2 proves its file exists. This is the § 2.1 "zero vs silence" distinction,
   carried by the bijection rather than by a zero node.
6. The docstring states the § 8 classification: PROCEDURAL raw extraction, irreducible because
   its input is a JSON file and not a graph.

- [ ] **Step 1: Failing tests.** In `tests/test_corpus_firings.py`, use a `tmp_path` fixture to
  write a two-document manifest (Turtle) and baseline JSONs in the real shape
  (`{"pdf": …, "pages": [{"regions": [{"reason": …, "verdict": …}]}]}`; measured in
  `tests/corpus-baseline/bfs-population-bilan-2023.json`). Write one test per invariant 1–5:
  - (1) a `held-out/` file is ignored, and the join is by `pdf`;
  - (2a) a missing file raises, (2b) an orphan `corpus/` file raises;
  - (3) `"fewer than 2 lines"` is not lifted;
  - (4a) 3 escalated plus 2 superseded gives live 3 / superseded 2, and (4b) a constant reason with
    verdict `asserted` raises;
  - (5) a clean document has no `cor:firing`;
  - `live_pairs` omits a 0-live firing.

  Also add one test that lifts the **real** manifest and baseline and asserts that the result
  conforms to `tests/corpus-shapes.ttl` together with the manifest. That is D1 over real data.
- [ ] **Step 2:** Run it and show RED (ImportError).
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run it and show green.
- [ ] **Step 5: MEASUREMENT, the O4 replacement. Report it; do not commit it as a test.** Print
  `live_pairs` and every firing's live/superseded over the real data. It must reproduce spec § 8.3's
  profile exactly, with the **six** live pairs: apple `DATAGRID_RESIDUE`; bfs `DATAGRID_RESIDUE`,
  `KIND_NOT_SUPPORTED`, `REGION_TILING_FAILED`; ons `DATAGRID_RESIDUE`, `KIND_NOT_SUPPORTED`. If it
  differs, stop and report before building on it.
- [ ] **Step 6: FALSIFICATION.** In turn: drop the `corpus/` filter, swap live and superseded, and
  replace the bijection raise with a skip. Show the owning test go RED each time. Restore with `cp`.
- [ ] **Step 7: Commit.** `R259 task 2: lift firings from the corpus baseline`.

### Task 3: D2, the disposal guard, and conformance over manifest ∪ lift

**Files:** modify `tests/corpus-shapes.ttl` and `tests/test_corpus_manifest.py`.

**Interfaces:**
- Consumes: `lift_firings` and Task 1's terms.
- Produces: `cor:DisposalShape`, with target `sh:targetSubjectsOf cor:disposes`. Adjudications in the
  manifest are **untyped** blank nodes (`tests/corpus-manifest.ttl:37`), so a class target would
  never fire. **Invariant (spec § 3 D2 as strengthened by § 8):** for each `cor:disposes ?r` on
  adjudication `$this`, the document that holds `$this` via `cor:adjudication` must have a
  `cor:firing` whose `cor:reason` is `?r` and whose `cor:live` > 0. Anything else is refused,
  including superseded-only firings.

**Seam to measure:** `test_manifest_conforms` (`tests/test_corpus_manifest.py:34`) validates the
manifest **alone**. Change it to validate manifest ∪ `lift_firings(manifest, baseline_dir)`, or the
first real disposal is refused (Review Focus 3).

- [ ] **Step 1: Failing tests.** The negatives inject an adjudication into the **real** manifest's
  bfs or ons document. Spec O2 names bfs:

```python
from tests.corpus_firings import lift_firings

BASELINE = REPO / "tests" / "corpus-baseline"
BFS = "urn:iladub:corpus:bfs-population-bilan-2023"
ONS = "urn:iladub:corpus:ons-index-of-services-2026-02"


def _with_disposal(doc_iri: str, reason: str) -> Graph:
    g = Graph().parse(MANIFEST, format="turtle")
    g += lift_firings(g, BASELINE)
    g.parse(data=PREFIXES + f'<{doc_iri}> cor:adjudication [ cor:by "t" ; '
            f'cor:on "2026-10-16"^^xsd:date ; cor:rationale "t" ; cor:disposes "{reason}" ] .',
            format="turtle")
    return g


def test_admits_disposal_of_a_live_firing():          # positive control (Review Focus 4)
    ok, report = _conforms(_with_disposal(BFS, "KIND_NOT_SUPPORTED"))
    assert ok, report


def test_refuses_disposal_of_an_unfired_reason():     # spec O2
    ok, _ = _conforms(_with_disposal(BFS, "TRANSPOSED"))
    assert not ok


def test_refuses_disposal_of_a_misspelt_reason():     # spec § 8.3, O1 as amended
    ok, _ = _conforms(_with_disposal(BFS, "NOT_A_REASON"))
    assert not ok


def test_refuses_disposal_of_superseded_only_ink():   # spec § 8, strengthened D2
    ok, _ = _conforms(_with_disposal(BFS, "ROUND_TRIP_FAIL"))   # 0 live / 6 superseded
    assert not ok


def test_refuses_disposal_on_the_wrong_document():
    ok, _ = _conforms(_with_disposal(ONS, "REGION_TILING_FAILED"))  # ons: 0 live / 2 superseded
    assert not ok
```

  Then change `test_manifest_conforms` to validate manifest ∪ lift.
- [ ] **Step 2:** Run and show RED: the four refusal tests fail.
- [ ] **Step 3:** Write `cor:DisposalShape`.
- [ ] **Step 4:** Run `.venv/bin/python -m pytest tests/test_corpus_manifest.py tests/test_corpus_firings.py -q`
  and show all green.
- [ ] **Step 5: FALSIFICATION.** (a) Drop the `cor:live > 0` condition: `…superseded_only…` must go
  RED. (b) Drop the document-scoping join: `…wrong_document…` must go RED, because bfs has 2 live
  `REGION_TILING_FAILED`. (c) Revert `test_manifest_conforms` to manifest-alone, add a real
  `cor:disposes "KIND_NOT_SUPPORTED"` to bfs in a scratch copy of the manifest, and show the
  conformance test refuse it. Restore everything with `cp`.
- [ ] **Step 6: Commit.** `R259 task 3: D2 disposal guard over manifest ∪ lifted firings`.

### Task 4: D3, the shared oracle

**Files:** modify `tests/test_corpus.py`.

**Interfaces:**
- Consumes: `lift_firings` and `live_pairs`.
- Produces: `test_escalation_reasons_are_adjudicated`, parametrised over `live_pairs` of
  manifest ∪ lift. Ids are `<stem>-<REASON>`, where the stem is the IRI's local name. Each pair whose
  document has **no** adjudication carrying `cor:disposes <reason>` gets
  `pytest.mark.xfail(strict=True, reason=…)`. The marker is computed from the graph at collection
  time, never from a Python list (spec § 3 D3a). The **body** asserts, from the same graph, that the
  document has an adjudication disposing that reason.

**Seams:**
- Move `pytestmark = pytest.mark.corpus` (`tests/test_corpus.py:22`) onto the three tests that read
  `corpus/` (`test_expected_verdict`, `test_grounding_where_contracted`, `test_corpus_coverage_report`;
  measure that this is all of them). The new test carries **no** corpus mark (§ 8.3 seam 3).
- `test_corpus.py` already parses the manifest at collection time (`:40-59`), so spec § 7's
  collection-time rdflib worry is moot. Reuse that parse if it fits; do not add a second one.
- **`conftest.py` guard:** the new test never skips, so the R173 guard must stay silent. Show that it
  does.

- [ ] **Step 1:** Write the test. Expected at HEAD: **6 XFAIL**, 0 pass, 0 fail.
- [ ] **Step 2:** Run `.venv/bin/python -m pytest tests/test_corpus.py -m "not corpus" -rxX -q` and
  show 6 xfailed with the three corpus tests deselected (Review Focus 5). Then run
  `pytest tests/test_corpus.py --collect-only -q -m "not serial"` (the CI selector) and show the
  6 ids plus the corpus tests.
- [ ] **Step 3: FALSIFICATION, the O3 flip.** (a) In a scratch copy of the manifest, add
  `cor:disposes "KIND_NOT_SUPPORTED"` to bfs and point the test at it. That param goes XFAIL → PASS,
  the other 5 stay XFAIL. (b) Replace the body's disposal check with `pass`: the 6 params XPASS, and
  strict turns each into FAIL. That proves the body checks something. (c) In a scratch baseline copy,
  set bfs's `KIND_NOT_SUPPORTED` regions to `superseded`: the param must **disappear**, not pass.
  Restore with `cp`.
- [ ] **Step 4: Commit.** `R259 task 4: test_escalation_reasons_are_adjudicated (6 strict xfail)`.

### Task 5: The census resolves a parametrised oracle, and O5

**Files:** modify `scripts/oracle_test_census.py`.

**Interfaces:** change the presence test at `:99` (`elif t not in present`) so that a declared id is
present iff it collects exactly **or** some collected id starts with `t + "["`. That is M5b's rule,
`tests/test_arc_manifest.py:232-236`, and the comment should cite it by **symbol** (`_collects`), not
by line (CLAUDE.md plan rule 7). There is no test module for the census (measured: `ls tests | grep
census` lists only `test_section_repair_census.py`, which covers something else), so the script's
own three controls are its oracle.

- [ ] **Step 1: RED first.** Before editing, run `.venv/bin/python scripts/oracle_test_census.py` and
  show the shared id reported **DANGLING**, even though Task 4 made it collect. That shows seam 4 is
  real.
- [ ] **Step 2:** Edit.
- [ ] **Step 3: O5.** Run it again. The shared id is no longer dangling, the null control
  `test_this_id_is_invented` is still reported absent, and all three controls PASS. Record the
  before and after dangling counts.
- [ ] **Step 4: FALSIFICATION.** Widen the rule to a bare `startswith(t)` with no `"["`, and show
  whether the null control still holds. Then show that a declared `…::test_escalation_reasons_are_adj`
  prefix would wrongly resolve under the widened rule. Restore with `cp`.
- [ ] **Step 5: Commit.** `R259 task 5: census resolves a bare id to its parametrised ids (O5)`.

### Task 6: Baseline fingerprint, register, close

- [ ] **Step 1:** Run the full local gate: `.venv/bin/python -m pytest -q -n auto -m "not corpus and not serial"`
  and then `-m serial`. Read `N passed`, not the exit code (memory: phantom greens).
- [ ] **Step 2:** `git add` every new file. Then, with nothing else running, run `PYTHONPATH=src
  .venv/bin/python scripts/corpus_baseline.py regenerate` (about 24 min). **Expected:** only
  `tests/corpus-baseline/inputs.json` changes. `vocab/internal/corpus.ttl` should not be loaded by
  the compiler, so the snapshots should be byte-identical. If any snapshot changes, **stop**: it
  means the compile reads `corpus.ttl`, and that is a finding to report. Then run `check`.
- [ ] **Step 3:** In the register, strike `~~R259~~` in `residues.md` and record the closure evidence
  in place in `residues-open.md`: Task 5's census before and after, plus the commit. Check R259's
  "what would close it" first, and if it asks for more than O5, say so and do not strike. Leave R260
  open.
- [ ] **Step 4:** Make sure `prog:met` is unchanged on all five criteria
  (`git diff main -- tests/arc-manifest.ttl` is empty).
- [ ] **Step 5:** Commit, push the branch, open the PR, and wait for `test` green.

## What this plan deliberately does not do

Spec § 6 stands. In addition: the five `# FIRES` comments in `tests/arc-manifest.ttl` are not
touched. They now contradict the lift (for example, `tab:07`'s says bfs only, and the lift shows bfs
3 + ons 2). Retiring them is the loop that disposes a reason, which can point readers at the fact.
