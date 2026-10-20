# The write endpoint refuses: meeting substrate:02 with a Fluree plug (design, 2026-10-20)

**Serves:** prog:criterion:substrate:02. `prog:met false` was re-verified on 2026-10-20 at `f824f0d`
(`tests/arc-manifest.ttl:596-603`).

**Doc impact: increment.** The released package gains an optional module, `iladub.substrate.fluree`,
and an empty `fluree` extra. Nothing already released changes meaning, and the compile path does not
touch the new module (§ 4.1).

**Approved:** Approach A from `docs/superpowers/2026-10-20-substrate-02-design-approved-handoff.md`
§ 3. The maintainer approved it on 2026-10-20 ("ok for A", then "yes go ahead"). § 2 records what has
changed since that approval: measurements taken while writing this spec, including one seam that
changes the order of the oracle's steps.

## 1. Goal

Meet `substrate:02`: *"a non-conforming write is refused AT THE WRITE ENDPOINT, not inside the
process that produced it."* The endpoint is a Fluree 4.2.4 HTTP server, which is a separate process.
Its ledger holds `vocab/shapes/iladub-shapes.ttl` and nothing else (§ 7, parity of the full membrane). The refusal is the
engine's own SHACL report, returned as an HTTP 400, and no commit is written.

Fluree is a **plug and never a dependency**. The maintainer ruled this on 2026-10-14 (user memory
`fluree-substrate-decision`). The in-process guarantee `writegate.gate_admits`
(`src/iladub/etkl/writegate.py:30-33`) stays as it is and keeps working without Fluree. The engine is
defence in depth, not a replacement.

Scope is :02 only. :01 (the immutable event ledger) and :03 (in-engine policy) are later loops that
will reuse the same adapter.

## 2. Measured while writing this spec (2026-10-20, macOS aarch64, fluree 4.2.4)

A throwaway spike lives in the scratchpad and is not committed. It compiles doc-a exactly the way
`tests/test_federation.py:78-84` does and drives a `fluree server run --memory` over HTTP with
`urllib`.

| Probe | Result |
|---|---|
| `fluree server run --memory --listen-addr 127.0.0.1:0` | Binds, but the log prints `addr=127.0.0.1:0` and never the real port. **The fixture must choose a free port itself.** |
| `POST /v1/fluree/create` with body `{"ledger":"probe"}` | **201**, `t: 0`. `/fluree/create` returns 404. |
| `POST /v1/fluree/insert/probe` with the iladub shapes, as `text/turtle` | 200 |
| Insert doc-a's interior (31 triples) | **200**, `t: 2`, with a commit hash |
| Insert the interior minus the grounded node's `iladub:wasPromotedBy` | **400**, `"SHACL validation failed with 1 violation(s): 1. INVARIANT: every grounded node must be produced by a promotion decision. … MinCountConstraintComponent"` |
| `GET /v1/fluree/info/probe` after the refusal | `ledger.t: 2`. The refusal wrote no commit. |
| pySHACL on the interior against `iladub-shapes.ttl`, with `inference="none"` and with `"rdfs"` | conforms in both cases |
| pySHACL on the stripped interior | does not conform |
| `rdf:type` values in the interior | `iladub:{GroundedNode, PromotionDecision, CandidateConcept, SourceRegion, Suggester}`, `dec:Option`, `tx:Offer` |
| Linux x86_64 tarball for v4.2.4 | sha256 `efe45dcfcf03549ea6ad475b76720188d60ca33196fef696628a9333e8aadc6f`, matching the release's own `.sha256` asset. It contains a `fluree` binary and `LICENSE`. |
| `LICENSE` in that tarball | `BUSL-1.1`. The Additional Use Grant forbids only offering a *Database Service* (§ 6). |

This settles three of the handoff's § 4 unknowns: the port, the create route, and doc-a passing
without RDFS. The RDFS question is settled only for this input, which uses `iladub:` classes
directly; § 7 keeps the general case open.

**The seam this spike found.** The refused focus node is a **blank node** (`_:fdb-…`). The stripped
graph fails only because inserting it mints *fresh* blank nodes, so its grounded node is a new node
with no promotion. If the compiler ever gave grounded nodes IRIs, the handoff's order would break:
commit the interior first, then commit the stripped copy. Fluree validates the ledger's post-state,
so the stripped triples would merge into a node that already carries `wasPromotedBy`. The engine
would then accept the write, and the oracle would fail for a reason unrelated to the endpoint. **So
the oracle commits the ungoverned write first, into an empty governed ledger (§ 5).** That order holds
whether nodes are blank or named.

## 3. Classification under the neurosymbolic gate (CLAUDE.md § 8)

- **The decision itself is AXIOM, and it is not new.** "May this write cross?" is `iladub:GroundedNodeShape`,
  a closed-world SHACL constraint at the membrane. This loop re-authors no shape and adds none. It
  changes *where* the existing constraint is evaluated.
- **The adapter is PROCEDURAL.** It does HTTP I/O and serialises a graph to Turtle. That is
  irreducible, because no ontology performs a socket write. It makes no decision: it never validates
  and never inspects the report beyond carrying it. The docstring says this, and so does this
  paragraph.
- No tuned constant appears anywhere. The fixture's readiness wait is a bounded poll on a TCP
  connect. It answers "is the process up", not a reading judgement.

## 4. Design

### 4.1 `src/iladub/substrate/fluree.py`: the plug

`src/iladub/substrate/__init__.py` is empty apart from a docstring that names the rung. The new module
sits beside the existing `src/iladub/fluree/` template directory, which this loop does not touch.

Interface:

- `FlureeEndpoint(base_url: str, timeout: float = 30.0)`. A timeout is an I/O bound and decides
  nothing.
- `provision(ledger: str, shapes: Graph) -> CommitResult`. It calls `POST /v1/fluree/create` and
  requires 201, then commits `shapes` as the ledger's first transaction. **Invariant:** if `shapes`
  is empty, it creates the ledger and makes no shapes commit. That is the falsification arm (§ 5.2),
  and it is the only way to get an ungoverned ledger.
- `commit(ledger: str, data: Graph) -> CommitResult`. It sends `POST /v1/fluree/insert/{ledger}` with
  `Content-Type: text/turtle`.
- `head_t(ledger: str) -> int`. It calls `GET /v1/fluree/info/{ledger}` and returns `ledger.t`.
- `CommitResult` is a frozen dataclass: `accepted: bool`, `status: int`, `t: int | None`, `report: str`.
  `report` is the engine's response body, verbatim.

**Refusal is a value, and an unexpected status is an error.** 2xx means `accepted=True`. **400 means
`accepted=False`**, with the body carried in `report`. Every other status, and every connection
failure, raises `FlureeEndpointError`. The reason is measured, not stylistic: `/fluree/create`
returned **404** in the spike (§ 2). An adapter that treated any 4xx as a refusal would let a wrong
route read as the membrane working. The producer-side raise is the guard (CLAUDE.md § R89).

**Dependencies:** `urllib` and `rdflib` only. `pyproject.toml` gains `fluree = []`, which declares the
plug and installs nothing. **Isolation invariant:** no module under `src/iladub/` other than
`iladub.substrate` imports `iladub.substrate`. A default-suite test greps for this (§ 5.3).

### 4.2 The oracle: `tests/substrate/test_write_gate.py`, marker `substrate`

Shared input is in `tests/substrate/doc_a.py`. `compiled_interior()` builds doc-a exactly as
`tests/test_federation.py:78-84` does. `ungoverned(interior)` returns a copy with every
`iladub:wasPromotedBy` triple removed from one grounded node. That module is plain Python with no
marker, so the default suite can import it (§ 5.3).

Fixture, session-scoped, in `tests/substrate/conftest.py`:

- The binary is `$ILADUB_FLUREE_BIN`, or else `shutil.which("fluree")`.
- **If the binary is absent, the fixture calls `pytest.fail`, never `pytest.skip`.** A selected
  substrate test has been asked to prove something. R173 and `tests/conftest.py:8-30` treat silent
  skips as failures, and this follows the same posture.
- `fluree --version` must report `4.2.4`. The oracle is a claim about one engine version, so it
  refuses to run against another.
- Choose a free port: bind `127.0.0.1:0`, read the port, close the socket. Then start
  `fluree server run --memory --listen-addr 127.0.0.1:<port>`, poll a TCP connect until it succeeds
  (bounded), and terminate the process at teardown. `--memory` writes nothing to the working tree.
- Each test uses a fresh ledger name, so tests on the same server share nothing.

`test_engine_refuses_an_ungoverned_commit` (the criterion's `prog:oracleTest`, named verbatim):

1. Provision ledger `L` with `iladub-shapes.ttl`, then record `t0 = head_t(L)`.
2. Commit `ungoverned(compiled_interior())`. Assert `accepted is False`, `status == 400`,
   `head_t(L) == t0`, and that `"INVARIANT: every grounded node must be produced by a promotion
   decision."` appears in `report`. That string is the `sh:message` at
   `vocab/shapes/iladub-shapes.ttl:40`, so the engine is quoting *our* membrane and not a generic error.
3. Commit `compiled_interior()`, the governed write. Assert `accepted is True` and
   `head_t(L) == t0 + 1`. This step is the control: without it, a ledger that refused *everything*
   would pass step 2.

## 5. Oracles and falsification

### 5.1 What each assertion rules out

| Assertion | Ruled-out world |
|---|---|
| step 2 `status == 400`, `accepted is False` | The engine accepts ungoverned writes. |
| step 2 `head_t` unchanged | The engine reports a refusal but commits anyway. |
| step 2 `INVARIANT` text in `report` | The 400 comes from something else, such as malformed Turtle or a route error. |
| step 3 accepted, `t0 + 1` | The ledger refuses everything, so step 2 shows nothing about the membrane. |

### 5.2 Falsification (the implementer runs and records it, per plan rule 4)

- **Provision with an empty shapes graph.** Step 2 must then be *accepted*, and the test must fail
  at step 2. This shows the refusal comes from the shapes in the ledger, not from the engine or the
  adapter.
- **Map 400 to `accepted=True` in the adapter.** The test must fail. This shows the adapter carries
  the refusal and does not absorb it.

### 5.3 Default-suite tests (run in the required `test` job, with no Fluree)

- **The two membranes agree on this input.** `gate_admits(ungoverned(compiled_interior()), Graph())`
  does not conform, and its report contains the same `INVARIANT` message. This shows only that both
  membranes refuse this one input, not that they agree in general (§ 7).
- **The adapter's status mapping.** A stub HTTP server from the standard library returns 200, 400,
  404 and 500. The results must be accepted, refused, raise and raise, in that order.
- **Isolation.** Grep `src/iladub/` for `iladub.substrate` and `from ..substrate`. Matches outside
  `src/iladub/substrate/` fail.

## 6. CI, licence, the arc, and the baseline

- **A new job, `substrate`, in `.github/workflows/ci.yml`. It is NOT a required check.** The ruleset
  requires `test` alone (CLAUDE.md § Branch protection), and this loop changes nothing in it. Steps:
  checkout, Python 3.12, download the v4.2.4 x86_64 Linux tarball, verify the sha256 from § 2 (pinned
  in the workflow, not fetched), install it on `PATH`, `pip install -e ".[dev,etkl,fluree]"`, then
  `pytest -q -m substrate`.
- **The required `test` job deselects substrate tests**: `-m "not serial and not substrate"`. The
  serial step's `-m serial` is unchanged. Register the marker in `pyproject.toml`.
- **Licence.** Fluree DB 4.x is BUSL-1.1. CI *uses* the binary but neither redistributes it nor offers
  it as a Database Service. The repo vendors no Fluree bytes, and the plug imports no Fluree code. A
  sentence to that effect goes in the module docstring.
- **The arc.** In the implementation PR, set `substrate:02 prog:met true` by hand, once the
  `substrate` job is green on that PR. Add a dated comment above the criterion that names the job
  run. That PR's description must say plainly that the proving job is *not* required, so `main` can
  later regress it without being blocked. That gap becomes a register row (§ 7).
- **Corpus baseline.** `src/iladub/substrate/*` and `pyproject.toml` are compile inputs. After the
  last input edit, and after `git add`, run `corpus_baseline.py regenerate`. The expected snapshot
  diff is **empty**, because the compile path never imports the plug. A non-empty diff is a finding.

## 7. What is NOT done (each becomes a register row in the implementation PR)

- **The proving job is not required.** If `substrate` goes red, `main` keeps merging. Making it
  required would make every PR depend on a third-party binary download. That is a maintainer choice
  and is deliberately not taken here.
- **Whether the membrane protects itself.** Nothing stops a writer from retracting the shapes and
  then committing ungoverned data. That is substrate:03 (in-engine policy).
- **Parity of the full membrane.** Only `iladub-shapes.ttl` is in the ledger. The dec, tab, etkl and
  doc-a shapes are not tested against Fluree's SHACL engine.
- **RDFS-aware targeting.** pySHACL runs with `inference="rdfs"`. Nobody has measured whether Fluree's
  `sh:targetClass` follows `rdfs:subClassOf`. Doc-a avoids the question because it types `iladub:`
  classes directly (§ 2).
- **Linux behaviour** is unmeasured until the first `substrate` job runs. If it fails, the CI section
  changes and the oracle does not.

## 8. Unverified at the time of writing

- Everything in § 2 was measured on macOS aarch64, except the tarball's hash and contents.
- The bounded TCP poll is enough for readiness: the spike waited 2 s and the server was up.
  Unmeasured whether the HTTP routes are live once the port accepts a connection.
- Whether the response to `insert` reports the same `t` that `head_t` reads afterwards. The spike read
  `t` from both and they agreed (2 and 2), on one sample.
- Doc-a's interior holds exactly **one** grounded node, and it is a blank node (measured 2026-10-20).
  `ungoverned` strips that one. A document with several grounded nodes would test whether one
  unpromoted node among conforming ones is refused. This loop does not test that.
