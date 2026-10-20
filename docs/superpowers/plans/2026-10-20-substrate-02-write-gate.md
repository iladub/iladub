# substrate:02 — the write endpoint refuses: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:substrate:02, `prog:met false` at `f01ee00` (`tests/arc-manifest.ttl:596-603`).

**Doc impact: increment**, the same as the spec: an optional module and an empty extra, and no released meaning changes.

**Goal:** A Fluree 4.2.4 HTTP endpoint, running as a separate process, refuses doc-a's ungoverned write with its own SHACL report and writes no commit. A non-required CI job proves this.

**Architecture:** A PROCEDURAL I/O plug, `iladub.substrate.fluree`, posts Turtle to Fluree and never validates. The oracle provisions a ledger whose only shapes are `iladub-shapes.ttl`. It commits the ungoverned write first and the governed write second.

**Tech Stack:** Python 3.12, `urllib`, rdflib, pytest, and the fluree 4.2.4 binary (BUSL-1.1, used and never redistributed).

**Spec:** `docs/superpowers/specs/2026-10-20-substrate-02-write-gate-design.md`. Read it in full first. The plan cites its sections and does not restate them (CLAUDE.md plan rule 6).

## Global Constraints

- The neurosymbolic gate (CLAUDE.md § 8). The adapter is PROCEDURAL I/O and makes no decision: no validation, and no inspection of the report beyond carrying it (spec § 3). No tuned constant anywhere.
- Fluree is a plug: `fluree = []` in `pyproject.toml` (spec § 4.1). Only `src/iladub/substrate/` may import `iladub.substrate`.
- Status mapping: 2xx means accepted, 400 means refused, and anything else, including a connection failure, raises `FlureeEndpointError` (spec § 4.1).
- The required job `test` stays free of Fluree. The `substrate` job is not required (spec § 6).
- A selected `substrate` test **fails** without the binary or on a version other than `4.2.4`. It never skips (spec § 4.2, R173).
- Pinned tarball sha256: `efe45dcfcf03549ea6ad475b76720188d60ca33196fef696628a9333e8aadc6f` (spec § 2).
- No implementation bodies in this plan (CLAUDE.md plan rule 1). The verbatim oracle test in Task 2 is a proposition until the implementer falsifies it (rule 4).
- Every task report carries a `## FALSIFICATION` block. Remove or invert the thing the test pins, show it failing, restore with `cp`, and show green.

## Review Focus

1. **A wrong route must not read as a refusal.** A 404 from a mistyped path raises and never yields `accepted=False`. The 404 case in Task 1's stub test pins this.
2. **A server that never comes up.** The fixture's readiness poll is bounded. On timeout the test **fails** and its message includes the server's stderr. It never hangs or skips. Pin: a Task 2 test that runs the fixture's start helper against a binary path that exits immediately (`/usr/bin/false`) and asserts `pytest.fail`-style failure within the bound.
3. **A leaked server process.** Teardown terminates the process even when a test fails. Pin: in Task 2, the fixture uses `try/finally`, and its test asserts that `proc.poll() is not None` after teardown. Run it through the helper, not the session fixture.
4. **Ledger cross-talk.** Two tests on one session server use different ledger names. Pin: Task 2's ledger-name helper returns distinct names across calls.
5. **Turtle the engine cannot parse would produce a 400 and look like a refusal.** The oracle's `INVARIANT` assertion already rules this out (spec § 5.1, row 3). There is no extra test, but reviewers check that the assertion is not weakened.

---

### Task 1: The plug, `iladub.substrate.fluree`

**Files:**
- Create: `src/iladub/substrate/__init__.py`, which holds a docstring only and names the rung and criterion.
- Create: `src/iladub/substrate/fluree.py`
- Modify: `pyproject.toml` (`[project.optional-dependencies]`, currently `:40` onward). Add `fluree = []`.
- Test: `tests/test_substrate_plug.py`, in the default suite with no marker.

**Interfaces:**
- Produces: `FlureeEndpoint(base_url: str, timeout: float = 30.0)`, with:
  - `.provision(ledger: str, shapes: Graph) -> CommitResult | None`
  - `.commit(ledger: str, data: Graph) -> CommitResult`
  - `.head_t(ledger: str) -> int`
- Also produces: `CommitResult(accepted: bool, status: int, t: int | None, report: str)` (frozen) and `FlureeEndpointError(Exception)`.
- `provision` contract (spec § 4.1): `POST /v1/fluree/create` with body `{"ledger": <name>}`. A 201 is required, and any other status raises. If `shapes` is non-empty, it then commits them and returns that `CommitResult`. **If `shapes` is empty, it returns `None` and makes no commit.**
- Measured routes (spec § 2): create `/v1/fluree/create`, insert `/v1/fluree/insert/{ledger}` with `text/turtle`, and info `GET /v1/fluree/info/{ledger}` → `json["ledger"]["t"]`.
- The insert response carries `t`, for example `{"ledger_id":"probe","t":2,…}`. Read `CommitResult.t` from it on 2xx, and set it to `None` on 400.

The module docstring must state: PROCEDURAL because it is socket I/O, irreducible, and makes no decision; `writegate.gate_admits` is the in-process guarantee; and the BUSL-1.1 sentence from spec § 6.

- [ ] **Step 1: Write the failing tests** in `tests/test_substrate_plug.py`:
  - `test_status_mapping`. A standard-library `http.server.ThreadingHTTPServer` on `127.0.0.1:0`, in a daemon thread, answers `POST /v1/fluree/insert/<x>` with the status named by `<x>` (`ok200`, `bad400`, `nf404`, `err500`). The 200 body is `{"t": 7}` and the 400 body is `{"error":"SHACL …"}`. Assert:
    - `ok200` gives `accepted is True` and `t == 7`.
    - `bad400` gives `accepted is False`, `status == 400`, and a `report` containing `"SHACL"`.
    - `nf404` and `err500` each raise `FlureeEndpointError`.
  - `test_connection_refused_raises`. Point `commit` at a port bound and then closed. Expect `FlureeEndpointError`.
  - `test_provision_empty_shapes_makes_no_commit`. The stub counts insert calls: `provision(…, Graph())` gives 1 create call, 0 insert calls, and returns `None`.
  - `test_plug_is_isolated`. Walk `src/iladub/**/*.py` outside `src/iladub/substrate/` and fail on any line matching `iladub\.substrate` or `from \.+substrate`.
- [ ] **Step 2:** `.venv/bin/python -m pytest -q tests/test_substrate_plug.py` fails because the module is absent. Record the output.
- [ ] **Step 3:** Implement the module to the contract above (`urllib.request`, `json`, rdflib `serialize(format="turtle")`).
- [ ] **Step 4:** The same command is green. Read the `N passed` line, not the exit code (memory: macOS phantom greens).
- [ ] **Step 5: FALSIFICATION.** (a) Map 400 to `accepted=True`: `test_status_mapping` fails. (b) Treat 404 as a refusal: it fails. (c) Add `import iladub.substrate` to `src/iladub/etkl/federate.py`: `test_plug_is_isolated` fails. Restore each with `cp` from a saved copy and show green.
- [ ] **Step 6:** Commit.

### Task 2: The oracle, run locally against the Homebrew fluree 4.2.4

**Files:**
- Create: `tests/substrate/__init__.py`, **only if** the measurement below requires it.
- Create: `tests/substrate/doc_a.py`, with `compiled_interior() -> Graph` and `ungoverned(g: Graph) -> Graph` (spec § 4.2).
- Create: `tests/substrate/conftest.py`, with the session fixture `fluree_endpoint`. It returns a `FlureeEndpoint` and a `fresh_ledger()` name helper.
- Create: `tests/substrate/test_write_gate.py`
- Modify: `pyproject.toml` `markers` (`:100-103`). Add `"substrate: needs the fluree 4.2.4 binary; runs only in the non-required substrate CI job (substrate:02)"`.
- Modify: `tests/test_substrate_plug.py`. Add the default-suite agreement test and the fixture-helper tests from Review Focus 2–4.

**Interfaces:**
- Consumes: Task 1's `FlureeEndpoint`, `CommitResult`, `FlureeEndpointError`.
- Produces: `compiled_interior`, `ungoverned`, the `fluree_endpoint` fixture, and the oracle node ID `tests/substrate/test_write_gate.py::test_engine_refuses_an_ungoverned_commit`, verbatim from `tests/arc-manifest.ttl:602`.

**MEASURE before writing, and do not assume:**
- (a) Do `tests/` subdirectories import as `tests.<sub>.<mod>` under `pythonpath = ["."]` (`pyproject.toml:99`), and do any existing ones carry an `__init__.py`? Run `ls tests/*/__init__.py` and try one import. The answer decides whether `tests/substrate/__init__.py` exists.
- (b) Does `collectable_node_ids()` (`tests/test_arc_manifest.py`, cached above `:232`) collect **without** a `-m` filter? If it applies the default deselection, M5b will refuse the Task 4 flip. Read its body and record what it runs.
- (c) Doc-a has exactly one grounded node, a blank node (spec § 8). `ungoverned` removes `(gn, iladub:wasPromotedBy, *)` for that one node, and the helper asserts the count is 1. A count other than 1 is a finding, not something to work around.

`doc_a.compiled_interior()` replicates `tests/test_federation.py:78-84` exactly. Import from there, or copy the five constructor lines. Do not re-derive them.

The fixture contract (spec § 4.2): it reads the binary from `$ILADUB_FLUREE_BIN` or `shutil.which("fluree")`. It calls `pytest.fail` if the binary is absent or if `--version` is not `fluree 4.2.4`. It picks a free port by bind-then-close, starts `server run --memory --listen-addr 127.0.0.1:<port>`, and polls a bounded TCP connect; on timeout it fails with the captured stderr. It terminates the process in `finally`. Factor the start and stop into a plain helper so Review Focus 2 and 3 can test it without the session fixture.

- [ ] **Step 1: Write the oracle**, verbatim. This is the criterion's contract (spec § 4.2 steps 1–3).

```python
import pytest
from rdflib import Graph

from iladub.etkl.writegate import commit_gate_shapes
from tests.substrate.doc_a import compiled_interior, ungoverned

pytestmark = pytest.mark.substrate

INVARIANT = "INVARIANT: every grounded node must be produced by a promotion decision."


def test_engine_refuses_an_ungoverned_commit(fluree_endpoint):
    ep, fresh_ledger = fluree_endpoint
    ledger = fresh_ledger()
    ep.provision(ledger, commit_gate_shapes())
    t0 = ep.head_t(ledger)

    refused = ep.commit(ledger, ungoverned(compiled_interior()))
    assert refused.accepted is False
    assert refused.status == 400
    assert INVARIANT in refused.report
    assert ep.head_t(ledger) == t0

    admitted = ep.commit(ledger, compiled_interior())
    assert admitted.accepted is True
    assert ep.head_t(ledger) == t0 + 1
```

Adjust the import path only if measurement (a) requires it, and say so in the report.

- [ ] **Step 2: Write the default-suite agreement test** in `tests/test_substrate_plug.py`. `gate_admits(ungoverned(compiled_interior()), Graph())` does not conform, and the `INVARIANT` string appears in its results text. The fixture-helper tests from Review Focus 2–4 go here too, and must not depend on the real binary.
- [ ] **Step 3:** `.venv/bin/python -m pytest -q -m substrate tests/substrate` fails because the fixture is absent. Then implement `doc_a.py` and `conftest.py`.
- [ ] **Step 4:** `.venv/bin/python -m pytest -q -m substrate tests/substrate` gives 1 passed. `.venv/bin/python -m pytest -q tests/test_substrate_plug.py` is green.
- [ ] **Step 5: FALSIFICATION** (spec § 5.2). (a) Change the oracle's `provision` argument to `Graph()`: the test fails **at the `accepted is False` line**. Quote that line in the report. (b) The Task 1 400→accepted mutation fails the oracle as well. (c) Set `ILADUB_FLUREE_BIN=/nonexistent`: the test **fails**, and is neither skipped nor errored as a skip. Restore with `cp` and show green.
- [ ] **Step 6:** `.venv/bin/python -m pytest -q -m "not serial and not substrate" -n auto` is green, and `tests/substrate` contributes 0 tests to it. Commit.

### Task 3: CI — the `substrate` job, and deselection in `test`

**Files:**
- Modify: `.github/workflows/ci.yml`. In the `test` step at `:25`, change the filter to `-m "not serial and not substrate"`. Add a job `substrate`.

The `substrate` job (spec § 6): `ubuntu-latest`. Steps: checkout; setup-python 3.12 with pip cache; `curl -sSL` the x86_64 tarball named in spec § 2; `echo "<pinned sha>  <file>" | sha256sum -c -`; extract it and put the directory on `$GITHUB_PATH`; `pip install -e ".[dev,etkl,fluree]"`; then `pytest -q -m substrate`. **Do not rename job `test`.** That name is the required check (CLAUDE.md § Branch protection).

- [ ] **Step 1:** Edit the workflow. Push the branch and open the PR **without** `--auto`.
- [ ] **Step 2: PROPOSED.** The job goes green on its first run. This is the handoff's one unmeasured premise, Linux behaviour (spec § 7). If it fails, fix the CI steps only; the oracle does not change. Record the run URL and the `1 passed` line from its log.
- [ ] **Step 3: FALSIFICATION.** Push a commit that corrupts one hex digit of the pinned sha. The `substrate` job fails at `sha256sum -c`. Revert it in the next commit and the job is green again. Both run URLs go in the report.

### Task 4: The arc, the register, the baseline

**Files:**
- Modify: `tests/arc-manifest.ttl:596-603`. Set `prog:met true` and add `prog:metOn "<date the substrate job went green>"^^xsd:date`. M2 (`tests/arc-shapes.ttl:122`) requires `metOn`. `retrospective` stays false, because `metOn` > `declaredOn` (M4, `:143`). Above the criterion, add a dated comment naming the green `substrate` run URL and saying the job is not required.
- Modify: `docs/superpowers/residues.md` and `docs/superpowers/residues-open.md`. Add one row each for the five items in spec § 7. Each row records the tally at the moment it is raised: count the index's closed rows and total rows when writing it; do not copy a figure from anywhere. The current last row is R326 (measured at `f01ee00`).
- Regenerate: `tests/corpus-baseline/`.

- [ ] **Step 1:** Make the manifest edit, then run `.venv/bin/python -m pytest -q tests/test_arc_manifest.py`. It is green, including M5b. If M5b refuses, measurement 2(b) was wrong: stop and report.
- [ ] **Step 2: FALSIFICATION.** Temporarily rename the oracle function. `test_arc_manifest.py` refuses with M5b. Restore with `cp`.
- [ ] **Step 3:** Add the register rows. `.venv/bin/python -m pytest -q tests/test_doc_governance.py tests/test_arc_manifest.py` is green.
- [ ] **Step 4:** After `git add` of every new input file, run `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`. It takes about 24 minutes, serially, with nothing else running (memory: corpus runs are serial). **Expected:** `git diff --stat -- tests/corpus-baseline/` shows only `inputs.json`. Any snapshot change is a finding (spec § 6); stop and report it.
- [ ] **Step 5:** Full local gate: `.venv/bin/python -m pytest -q -n auto -m "not serial and not substrate"`, then `-m serial`, then `-m substrate`. Read each `N passed`. Commit and push. Both `test` and `substrate` must be green on the PR before merging. The PR description states that `substrate` is not required (spec § 6).
