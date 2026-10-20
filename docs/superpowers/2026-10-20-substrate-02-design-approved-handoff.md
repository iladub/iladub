# Handoff: substrate:02 — design approved, spec not yet written (2026-10-20)

**Serves:** prog:criterion:substrate:02 — verify it is still `prog:met false` before starting.

**Topic:** substrate · **Date:** 2026-10-20

**Doc impact: none.** A handoff only.

Part 5 was written first. The session handed off at 51,104 working tokens, 1.02× the 50K
originating floor, immediately after the maintainer approved the design and before the spec was
written. The preflight log records it as a handoff.

## 5. The next concrete action, typed

1. **ASSERTED: write the spec** at `docs/superpowers/specs/2026-10-20-substrate-02-write-gate-design.md`
   from § 3 below, in the first third of a fresh session. The maintainer approved the design in chat
   ("yes go ahead"), and that approval covers *writing the spec*. Then run spec self-review, ask the
   maintainer to review the written spec, and only after that use superpowers:writing-plans.
2. **PROPOSED: the oracle in § 3.2 is buildable on CI exactly as designed.** Its premises were measured
   on macOS (aarch64, 4.2.4) only. The Linux tarball download, the sha256 pin, and `fluree server run`
   on an ephemeral port inside GitHub Actions are unmeasured. If one fails, the CI section changes,
   not the oracle. You find out in minutes, from the first CI run of the job.

## 1. Goal

Meet `prog:criterion:substrate:02` (`tests/arc-manifest.ttl:596-603`): a non-conforming write is
refused **at the write endpoint**, not inside the process that produced it. Fluree is a plug, never a
dependency (maintainer ruling 2026-10-14, recorded in user memory `fluree-substrate-decision`).

## 2. Where the primaries are

- `tests/arc-manifest.ttl:536-612`: the substrate rung's header (the measured "zero") and its three
  criteria. Each criterion names its target `prog:oracleTest`. :02's is
  `tests/substrate/test_write_gate.py::test_engine_refuses_an_ungoverned_commit`, a file that does not
  exist yet. `tests/arc-shapes.ttl` holds the M rules a met criterion must satisfy;
  `tests/test_arc_manifest.py:312-355` holds M5, M5b and M21.
- `docs/narrative/scope-evolution.md:99-102`: why the rung exists (memory, sensory, motor).
- `src/iladub/etkl/writegate.py`: `gate_admits`, the **in-process** pySHACL check against
  `vocab/shapes/iladub-shapes.ttl`. It stays as the no-Fluree guarantee. Its tests are in
  `tests/test_writegate.py` (fixtures `tests/writegate-{promoted,unpromoted}.ttl`,
  `tests/leak-attempt.ttl`).
- `tests/test_federation.py:80-84`: compiles `examples/federation/doc-a` through
  `federate.compile_document` into a real interior graph. This is the oracle's input.
- `.github/workflows/ci.yml`: today it runs `pytest -q -n auto -m "not serial"` then `-m serial`. The
  required check is the JOB `test` (CLAUDE.md § Branch protection).
- `tests/conftest.py:8-30`: corpus-reason skips are turned into failures (R173), so the repo distrusts
  silent skips.
- Fluree binary: `/opt/homebrew/bin/fluree` is 4.2.4. Linux tarballs are at
  `https://github.com/fluree/db/releases/download/v4.2.4/fluree-db-cli-x86_64-unknown-linux-gnu.tar.xz`
  (from the `fluree/tap` formula).

### Spike evidence (throwaway, scratchpad, not committed; 2026-10-20, macOS, 4.2.4)

| Probe | `--direct` (CLI) | HTTP `POST /v1/fluree/insert/spike` (`fluree server start`) |
|---|---|---|
| `iladub-shapes.ttl` inserted into the ledger's default graph | committed t=1, 63 flakes | n/a |
| `GroundedNode` without `wasPromotedBy` | refused, exit 1, SHACL report | refused, **HTTP 400**, same report |
| Conforming node plus `PromotionDecision` | committed t=2 | committed t=3, HTTP 200, tx-id and commit hash |
| `CandidateConcept` with `status asserted` (`NoLeakShape`, `sh:sparql`) | refused, `SPARQLConstraintComponent` fired | not run |
| `fluree log` after the refusals | only t=1,2,3, so no commit for any refusal | |

The binary's embedded docs say: *"A ledger with shapes but no `#config` graph enforces
unconditionally."* Enforcement can also be configured via `f:LedgerConfig` / `f:shaclDefaults` /
`f:shapesSource` in `urn:fluree:{ledger}#config`; this was not exercised.

## 3. What was decided, and where it is recorded

All of the following were decided in the 2026-10-20 session. **They are recorded nowhere but this
file** until the spec is written, so they are settled maintainer choices but not yet in a spec.

- **Subject:** substrate (the ready rung), chosen over the frontier rows R44, R74 and R62
  (AskUserQuestion).
- **Scope:** **substrate:02 only, first.** :01 (history) and :03 (policy) are later loops on the same
  adapter.
- **Oracle venue:** a **separate, non-required CI job `substrate`** that installs a pinned fluree
  binary. The required `test` job stays fluree-free.
- **Approach A** (approved), with **only `iladub-shapes.ttl`** in the ledger. That was the session's
  stated lean, and the maintainer's "ok for A" did not contest it. Re-confirm it when presenting the
  spec.

### 3.1 Unit: `iladub.substrate.fluree`, the plug
- `FlureeEndpoint(base_url)` has `provision(ledger, shapes: Graph)` (create the ledger, then commit
  the shapes as its first transaction), `commit(ledger, data: Graph) -> CommitResult` (POST Turtle to
  `/v1/fluree/insert/{ledger}`) and `head_t(ledger)`.
- `CommitResult` holds `accepted`, `t`, `status`, and the engine's `report` text as given.
- It uses `urllib` only. A `fluree` extra exists as the declared plug and has no dependencies.
- **It never validates.** It is PROCEDURAL under the neurosymbolic gate (I/O, irreducible), and the
  docstring says so. `writegate.gate_admits` stays as the in-process guarantee; the engine is defence
  in depth.
- Nothing in the compile path imports or calls it.

### 3.2 The oracle: `tests/substrate/test_write_gate.py`, marker `substrate`
- A session fixture runs `fluree server run` on a free port with a temporary storage directory, and
  tears it down afterwards.
- `test_engine_refuses_an_ungoverned_commit`:
  1. Provision with `iladub-shapes.ttl`.
  2. Commit doc-a's compiled interior: accepted, and `t` advances.
  3. Strip every `wasPromotedBy` triple from one grounded node and commit again. Expected: HTTP 400,
     `head_t` unchanged, and the report contains the `INVARIANT` message.
- **Falsification:** provision without shapes, and step 3 is accepted.
- **Default-suite control:** in-process pySHACL rejects the same stripped graph, so the two membranes
  are shown to agree on this one input.

### 3.3 CI and the arc
- A new job `substrate`, **not** a required check. It downloads the pinned v4.2.4 Linux tarball,
  verifies sha256, installs `.[dev,etkl,fluree]`, and runs `pytest -m substrate`.
- The required `test` job deselects with `-m "not serial and not substrate"`.
- A selected `substrate` test **fails** when the binary is absent; it never skips (R173, M19).
- `substrate:02 prog:met true` is flipped by hand in the implementation PR, once the job is green
  on that PR.

### 3.4 What is NOT done (raise as register rows)
- Who may delete or retract the shapes, so whether the membrane is self-protecting. That is
  substrate:03.
- Parity of the full membrane (dec, tab and etkl shapes) between Fluree's SHACL engine and pySHACL.
- RDFS inference. pySHACL validates with `inference="rdfs"` against `iladub.ttl`/`dec.ttl`, and
  whether Fluree's target matching follows `rdfs:subClassOf` is unmeasured. The oracle sidesteps it
  by using `iladub:` classes directly.
- BUSL-1.1: CI downloads and uses the binary but does not redistribute it. A licence note belongs in
  the spec.
- The corpus baseline: a new `src/` file is a compile input, so run `corpus_baseline.py regenerate`
  after the last input edit and expect an empty snapshot diff.

## 4. Unverified or assumed

- Everything in the spike was measured on macOS aarch64 only. Linux CI behaviour is unmeasured.
- `fluree server run` accepting a `--listen-addr` with port 0, or the fixture needing to pick a free
  port itself: unmeasured. The spike used `server start --listen-addr 127.0.0.1:18090`.
- Whether `fluree create` must run before an HTTP insert, or `/v1/fluree/create` is the HTTP route
  for it: the spike created the ledger via the CLI before starting the server. The adapter's
  `provision` needs this measured.
- Whether doc-a's compiled interior contains *only* `iladub:` targets that `iladub-shapes.ttl`
  validates cleanly without RDFS inference. If it fails step 2 in Fluree, that is the RDFS-parity
  residue biting, and the spec must handle it before planning.
- Side observation, not this loop: `prog:criterion:tab:04` still names R77 in `prog:blockedBy`, but
  R77 is closed. That is a stale edge.
