# The document router — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** maintenance — project 2 of the contract:01 rescope; no criterion exists for it yet.

**Execution method: subagent-driven** (owner, 2026-11-02, in chat).

**Doc impact: none.** A new owned module `route:` and one generated test document; no released page
changes, nothing enters `etkl.ttl` (spec header's condition for `increment` is not met).

**Goal:** Given one PDF with a text layer, find the documents inside it (page-top or mid-page starts)
and say, per document, FIBO `ContractDocument`, "not a contract" (from positive evidence), or refused —
every answer a traced `dec:DecisionHolon`, scored against the synthetic set's truth (bar B1–B6).

**Architecture:** PROCEDURAL line extraction (pdfium's own line breaks) → an RDF evidence graph →
two named questions (Q-boundary per page, Q-doctype per extent) answered on a ladder **rule → Jev →
Haiku**, every rung's answer disposed by an AXIOM oracle (SPARQL) → a trace graph validated by a
`route-shapes.ttl` membrane. Model answers on the learning set are written back as owned rules keyed
by **line-text hashes**. The owner only admits proposed new types. The HDC rung is **not built** (spec
§ 9 asks the plan to propose; this plan proposes "rule + model now, HDC after its skill", decision 17).

**Tech Stack:** Python 3, rdflib, pySHACL, pypdfium2, BAML 0.222 (`baml_src/`), reportlab (test PDFs).

**Spec:** `docs/superpowers/specs/2026-11-02-document-router-design.md` (APPROVED, PR #387). Read § 4–§ 6
before any task; this plan cites them rather than restating them.

## Global Constraints

- CLAUDE.md § 8 gate: every decision is classed AXIOM / NEURAL / PROCEDURAL **in the module docstring**;
  no tuned constant, no tolerance, no geometric heuristic decides a boundary (spec § 2 anti-goals).
- A refusal is not wrong; a wrong assertion fails the bar (spec § 6 B3). When unsure, refuse.
- "Not a contract" only from cited positive evidence, never from a missing party/commitment (spec § 4).
- **No template text in any committed file.** Templates are local only (synthetic-set spec). Rules
  store `sha256(line text)`, readings store line ids, the report stores counts. Trace graphs and
  router outputs are written under `synthetic/route/` (gitignored, beside `synthetic/out/`).
- **The router never reads the truth or imports the generator** — `tests/test_synthetic_contracts_leak.py`
  scans `src/`, `readings/`, `scripts/`, `tests/`. Hence the scorer lives in `scripts/synthetic_contracts/`
  and its tests in `tests/test_synthetic_contracts_score.py` (the only allowed places).
- The router reads only the PDF bytes, never its file name.
- Namespace `route:` = `https://w3id.org/iladub/route#`. gist/FIBO IRIs appear only as objects, only in
  `vocab/ontology/route-align.ttl` and `route-types.ttl` (alignment, not import; spec § 3).
- New Haiku client is `claude-haiku-5-5`, `max_tokens 8192`, no `temperature` (compiler design § 8 call);
  the existing `Claude` / `ClaudeLongAnswer` clients are not touched.
- Live model calls only under `BAML_LIVE=1`; recording only under `ILADUB_RECORD_READINGS=1`
  (the `src/iladub/etkl/caption.py:199-245` pattern). CI never calls a model.
- `.ttl` / `.rq` population pins in `tests/test_artifact_declarations.py` (`== 254`, `== 59` at
  `:76-77` on this base) are **re-measured, never copied**, by every task that adds such a file.
- Every task report carries `## FALSIFICATION` (CLAUDE.md plan rule 4).
- One corpus-baseline regenerate, last (Task 10): `src/`, `vocab/`, `readings/`, `pyproject.toml` are inputs.

## Review Focus

1. **A page on which two documents start.** Q-boundary answers at most one start per page. Expected:
   the rule rung abstains when two STARTS cues fire on one page (Task 4 test), and the bar report lists
   any such truth page (Task 9). Not built further this loop.
2. **A blank or image-only page inside a text PDF.** Expected: no lines, no question, no holon; it is
   absorbed into the surrounding extent (Task 6 test `test_blank_page_is_absorbed`).
3. **A PDF with no text layer at all** (a scan). Expected: no crash; zero documents asserted and one
   refusal holon with reason `no-text-layer` (Task 6 test `test_scan_refuses_whole_pdf`).
4. **A model answer citing ids that are off the page, negative, duplicated, or outside the extent.**
   Expected: the oracle refuses it (Task 3 tests).
5. **A renamed copy of a PDF.** Expected: identical decisions; only the source IRI differs (Task 6 test
   `test_route_ignores_file_name`).

---

### Task 1: Model clients and the Jev seam (PROPOSED: Jev may not be reachable)

Spec § 8's first MEASURE seam. **Measured 2026-11-02:** iladub pins `baml-py==0.222.0`
(`pyproject.toml:43`) and its clients use `client<llm>` syntax (`baml_src/clients.baml:1`); hdc-contract
reaches Jev through `typesafeai.Client.new(model = "jev-1.14.0", ...)` on a **different BAML runtime**
(`baml-bridge==0.22.3.dev2026102300`). The `typesafeai` provider does not exist in 0.222. Upgrading
BAML is out of scope (it touches every existing function and the corpus baseline).

**Files:**
- Modify: `baml_src/clients.baml` (append only)
- Create: `src/iladub/route/__init__.py`, `src/iladub/route/models.py`
- Test: `tests/test_route_models.py`

**Interfaces:**
- Produces: `MODEL_IDS: dict[str, str]` (BAML client name → model id), `jev_available() -> bool`,
  `haiku_available() -> bool` in `src/iladub/route/models.py`.

- [ ] **Step 1: MEASURE whether TypeSafe exposes an OpenAI-compatible endpoint.** Read
  `https://docs.typesafe.ai` (web-fetch agent). Record in the task report: base URL, auth header, and
  whether `jev-1.14.0` is the model name there. Do not read hdc-contract code beyond the line quoted above.
- [ ] **Step 2: Append `RouterHaiku`** (`provider anthropic`, `model "claude-haiku-5-5"`, `max_tokens 8192`)
  and — **only if Step 1 found an OpenAI-compatible endpoint** — `RouterJev` (`provider openai-generic`,
  `base_url` from Step 1, `model "jev-1.14.0"`, `api_key env.TYPESAFE_API_KEY`). Add a `RouterPing`
  function per client (the `baml_src/ping.baml` shape). Run `baml-cli generate`.
- [ ] **Step 3: Live ping** (`BAML_LIVE=1`) each new client once; paste both outputs in the report.
  **Checkpoint (proposed):** if `RouterJev` is absent or its ping fails, remove `RouterJev` from
  `clients.baml`, set `jev_available()` to return `False` unconditionally with a comment citing this
  report, and raise a residue row in Task 10 ("Jev unreachable from BAML 0.222: <measured reason>").
  Haiku then decides alone (spec § 4). This is an allowed outcome, not a failure.
- [ ] **Step 4: Write failing tests** `tests/test_route_models.py`:
  - `test_model_ids_match_clients_baml`: parse `baml_src/clients.baml` text; for every `Router*` client
    (except pings) its `model "..."` equals `MODEL_IDS[name]`; `MODEL_IDS["RouterHaiku"] == "claude-haiku-5-5"`.
  - `test_nothing_live_without_flag`: with `BAML_LIVE` unset, `haiku_available()` and `jev_available()` are `False`.
- [ ] **Step 5: Implement** `models.py` (the gate mirrors `baml_caption_available`, `caption.py:74-77`;
  `jev_available` additionally requires `TYPESAFE_API_KEY` and the Step 3 outcome). Run; PASS.
- [ ] **Step 6: FALSIFICATION:** change `RouterHaiku`'s model string in `clients.baml`, show
  `test_model_ids_match_clients_baml` failing, restore with `cp`, show green.
- [ ] **Step 7: Commit** `feat(route): router model clients; Jev seam measured`.

### Task 2: The `route:` vocabulary, its alignment and its membrane

**Files:**
- Create: `vocab/ontology/route.ttl`, `vocab/ontology/route-align.ttl`, `vocab/ontology/route-types.ttl`
  (header only; the owner's admissions land here, Task 8), `vocab/shapes/route-shapes.ttl`,
  `examples/router/route-example.ttl`, `tests/route-negative-*.ttl` (one per shape, below)
- Modify: `tests/test_artifact_declarations.py` (population pins — re-measure)
- Test: `tests/test_route_vocab.py`

**Interfaces — produces these owned terms** (every task after uses exactly these names):

| term | kind | note |
| --- | --- | --- |
| `route:Line` | class | one extracted line; `prov:Entity` |
| `route:onPage`, `route:lineIndex` | int | page 1-based, line 0-based within page |
| `route:top`, `route:bottom` | decimal | output-page points from page TOP |
| `route:textSha` | string | `sha256` hex of the line's text |
| `route:Document` | class | one extent found; `route:order` (int, 1-based), `route:startsAt`/`route:endsAt` → `route:Line` |
| `route:ContractDocument` | class | ⊑ `route:Document`; aligned ⊑ FIBO `ContractDocument` in `route-align.ttl` |
| `route:BoundaryDecision`, `route:DoctypeDecision` | class | ⊑ `dec:DecisionHolon`; `route:aboutPage` (int) / `route:aboutDocument` |
| `route:StartsOption`, `route:ContinuesOption`, `route:ContractOption`, `route:NotAContractOption`, `route:RefusedOption` | `dec:Option` individuals | the closed option spaces |
| `route:rung` | → `route:RuleRung` \| `route:JevRung` \| `route:HaikuRung` \| `route:GivenRung` | `GivenRung` = "a PDF's first line starts its first document" |
| `route:modelId` | string | required iff rung is Jev/Haiku |
| `route:admittedBy` | → `route:ChecklistOracle` \| `route:BoundaryOracle` | absent on a refusal |
| `route:refusalReason` | string | required iff `dec:chosen route:RefusedOption` |
| `route:ProposedType` | class | ⊑ `iladub:CandidateConcept`; `rdfs:label`; `route:proposedFor` → `route:Document` |
| `route:BoundaryRule`, `route:DoctypeRule` | class | written-back rules; `route:cueSha`, `route:verdict`, `route:conflicted` (boolean) |

**Two decision holons per document, not one** — a deviation from spec § 5's "(call) one holon",
because Q-boundary and Q-doctype can be decided by different rungs and models, and B6 needs the rung
per answer. A document's extent is traced by the `BoundaryDecision`s of the pages it covers.

`route-shapes.ttl` (closed world, the membrane — spec § 4 and § 6 B6):
- S1 every `route:BoundaryDecision`/`DoctypeDecision` has `dec:decidedBy`, `route:rung`, `dec:rationale`
  (`rdf:langString` or `xsd:string` — do not constrain to `xsd:string`), and ≥ 1 `prov:used` unless refused;
- S2 a Jev/Haiku rung requires exactly one `route:modelId`;
- S3 `dec:chosen route:RefusedOption` ⇔ exactly one `route:refusalReason` and no `route:admittedBy`;
- S4 a `route:ContractDocument` has a `DoctypeDecision` choosing `ContractOption`, `admittedBy
  route:ChecklistOracle`;
- S5 nothing chosen `NotAContractOption` is a `route:ContractDocument`.

- [ ] **Step 1: Write failing tests** in `tests/test_route_vocab.py`: `test_example_conforms`
  (`examples/router/route-example.ttl` conforms under `inference="rdfs"`, `advanced=True`, data graph =
  example ∪ `route.ttl` ∪ `dec.ttl`); `test_negative_fails[S1..S5]` — one negative per shape, each failing
  with that shape's message; `test_core_module_is_standalone` (`route.ttl` has no `w3id.org/holon`,
  `semanticarts`, `edmcouncil` IRI); `test_fibo_alignment_target` (`route-align.ttl` has
  `route:ContractDocument rdfs:subClassOf <https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/ContractDocument>`
  and `route:Document rdfs:subClassOf <https://w3id.org/semanticarts/ns/ontology/gist/Content>`).
  **MEASURE the gist IRI** used elsewhere in `vocab/` before writing it (`grep -rn semanticarts vocab/`);
  if none, use the one above and say so in the report.
- [ ] **Step 2: Run, FAIL. Step 3: author the four `.ttl` files and the example. Step 4: run, PASS.**
- [ ] **Step 5: Re-measure** `tests/test_artifact_declarations.py` and `tests/test_source_ownership.py`;
  update the `.ttl` pin with a dated `RE-MEASURED` note in the docstring house style (`:141-165`).
  The declaration membrane requires every owned term typed and labelled — let it tell you what is missing.
- [ ] **Step 6: FALSIFICATION:** delete S4's `sh:property` from `route-shapes.ttl`, show
  `test_negative_fails[S4]` failing; restore with `cp`; green.
- [ ] **Step 7: Commit** `feat(route): route vocabulary, gist/FIBO alignment, membrane`.

### Task 3: Line extraction and the two oracles

**Files:**
- Create: `src/iladub/route/lines.py`, `src/iladub/route/oracle.py`,
  `vocab/queries/route-checklist.rq`, `vocab/queries/route-boundary.rq`
- Modify: `pyproject.toml` (add `pypdfium2>=4` to the `etkl` extra — CI installs `baml,dev,docs,etkl`,
  `.github/workflows/ci.yml:22`; today pypdfium2 arrives only transitively via pdfplumber)
- Test: `tests/test_route_lines.py`, `tests/test_route_oracle.py`

**Interfaces:**
- Produces: `@dataclass(frozen=True) class Line: page: int; index: int; text: str; top: float; bottom: float; x0: float; x1: float` with property `sha: str`;
  `extract_lines(pdf: bytes) -> list[Line]` (reading order: page, then pdfium's order);
  `lines_graph(lines: list[Line], pdf_sha: str) -> rdflib.Graph` (IRIs `urn:iladub:route:<pdf_sha[:12]>:p<page>:l<index>`);
  `BoundaryAnswer(verdict: Literal["STARTS","CONTINUES","REFUSES"], start_line: int | None, evidence_lines: tuple[int, ...])`;
  `DoctypeAnswer(kind: Literal["CONTRACT","OTHER","REFUSES"], party_lines: tuple[int,...], commitment_lines: tuple[int,...], other_evidence_lines: tuple[int,...], proposed_type: str | None, admitted_type: str | None)`
  — line ids in answers are **positions in the listing the proposer was shown** (0-based);
  `check_doctype(answer, extent: list[Line], admitted_types: set[str]) -> Verdict`,
  `check_boundary_local(answer, page_lines: list[Line], first_page: bool) -> Verdict`,
  `check_boundary_split(prev_extent, prev_doctype, next_extent, next_doctype) -> Verdict`,
  where `Verdict(admitted: bool, reason: str)`. All answer types live in `oracle.py`.

**Line extraction is PROCEDURAL — raw extraction**: walk `PdfTextPage` chars, split where pdfium's own
text emits `\r`/`\n`, box = union of non-whitespace char boxes converted to top-down; drop lines with
no non-whitespace char. **No grouping tolerance** — do not reuse `etkl/geometry.text_lines` (its
`0.6 × median` at `geometry.py:524` is exactly the tuned constant § 8 forbids here). MEASURE first that
pdfium's generated line-break chars are counted by `count_chars()` and carry an empty box; the test
below pins whatever is true.

**The oracles are AXIOM** (SPARQL over the evidence graph + the answer as triples; Python only loads
and calls): the checklist (spec § 4) and the boundary oracle, which is spec § 8's candidate made exact:

- local: CONTINUES needs ≥ 1 evidence id on the page and a page that is not the PDF's first; STARTS
  needs `start_line` on the page and in `evidence_lines`; ids in range, non-negative, no duplicates.
- split: a start at line L is admissible only if **both** extents it separates get an admitted
  Q-doctype answer and **either** their kinds differ, **or** both are CONTRACT and (the start line's
  `textSha` equals the previous extent's start line's `textSha` — a restart — **or** the two extents'
  party-line `textSha` sets are disjoint).

**Falsifier of the boundary oracle (named here, run in Task 9 — PROPOSED):** on the learning set's 16
single-document PDFs, force a STARTS at the top line of every page after the first; the oracle must
refuse every one. A single admission refutes it.

- [ ] **Step 1: Write failing tests.** `tests/test_route_lines.py` builds PDFs in `tmp_path` with reportlab:
  `test_three_lines_in_order` (three `drawString`s at y = 800, 700, 600 → 3 lines, texts exact, tops ascending),
  `test_blank_page_has_no_lines`, `test_mid_page_line_positions` (a line at y=400 has `top ≈ 842-400-font ascent` — assert `300 < top < 442`, no closer), `test_sha_is_sha256_of_text`.
  `tests/test_route_oracle.py`, verbatim:

```python
def _ext(texts, page=1):
    return [Line(page, i, t, 10.0 * i, 10.0 * i + 8, 0.0, 100.0) for i, t in enumerate(texts)]

def test_contract_needs_two_parties_and_one_commitment():
    ext = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship", "x"])
    ok = DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None)
    assert check_doctype(ok, ext, set()).admitted
    one_party = DoctypeAnswer("CONTRACT", (0,), (2,), (), None, None)
    assert not check_doctype(one_party, ext, set()).admitted
    same_line_twice = DoctypeAnswer("CONTRACT", (0, 0), (2,), (), None, None)
    assert not check_doctype(same_line_twice, ext, set()).admitted
    no_commitment = DoctypeAnswer("CONTRACT", (0, 1), (), (), None, None)
    assert not check_doctype(no_commitment, ext, set()).admitted

def test_ids_off_the_extent_are_refused():
    ext = _ext(["a", "b", "c"])
    for bad in [(0, 9), (-1, 1)]:
        assert not check_doctype(DoctypeAnswer("CONTRACT", bad, (2,), (), None, None), ext, set()).admitted

def test_other_needs_positive_evidence():
    ext = _ext(["Rules for sampling", "b"])
    assert check_doctype(DoctypeAnswer("OTHER", (), (), (0,), "Sampling rules", None), ext, set()).admitted
    assert not check_doctype(DoctypeAnswer("OTHER", (), (), (), "Sampling rules", None), ext, set()).admitted

def test_admitted_type_must_be_listed():
    ext = _ext(["Rules for sampling"])
    a = DoctypeAnswer("OTHER", (), (), (0,), None, "SamplingRules")
    assert check_doctype(a, ext, {"SamplingRules"}).admitted
    assert not check_doctype(a, ext, set()).admitted

def test_continues_refused_on_first_page():
    page = _ext(["header"])
    a = BoundaryAnswer("CONTINUES", None, (0,))
    assert not check_boundary_local(a, page, first_page=True).admitted
    assert check_boundary_local(a, page, first_page=False).admitted

def test_starts_must_cite_its_start_line():
    page = _ext(["end of A", "TITLE OF B"])
    assert check_boundary_local(BoundaryAnswer("STARTS", 1, (1,)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("STARTS", 1, (0,)), page, False).admitted

def test_split_same_kind_needs_restart_or_disjoint_parties():
    a, b = _ext(["T", "Sellers: A", "Buyers: B", "shall"]), _ext(["T2", "Sellers: A", "Buyers: B", "shall"], page=2)
    ca = cb = DoctypeAnswer("CONTRACT", (1, 2), (3,), (), None, None)
    assert not check_boundary_split(a, ca, b, cb).admitted            # same parties, no restart
    b_restart = _ext(["T", "Sellers: A", "Buyers: B", "shall"], page=2)
    assert check_boundary_split(a, ca, b_restart, cb).admitted          # restart: same title text
    b_other = _ext(["T2", "Owners: C", "Charterers: D", "shall"], page=2)
    assert check_boundary_split(a, ca, b_other, cb).admitted            # different parties

def test_split_refused_when_a_side_is_refused():
    a, b = _ext(["T", "x"]), _ext(["U", "y"], page=2)
    ok = DoctypeAnswer("OTHER", (), (), (0,), "X", None)
    refused = DoctypeAnswer("REFUSES", (), (), (), None, None)
    assert not check_boundary_split(a, ok, b, refused).admitted
```

  (Split checks compute each side's `check_doctype` themselves; a side that fails it fails the split.)
- [ ] **Step 2: Run, FAIL. Step 3: implement. Step 4: run, PASS.** Re-measure the `.rq` pin (`:77`).
- [ ] **Step 5: FALSIFICATION:** in `route-checklist.rq` drop the distinctness condition on party lines;
  show `test_contract_needs_two_parties_and_one_commitment` failing; restore; green. Repeat once for the
  disjointness clause of `route-boundary.rq` against `test_split_same_kind_needs_restart_or_disjoint_parties`.
- [ ] **Step 6: Commit** `feat(route): line extraction (PROCEDURAL) and the two oracles (AXIOM)`.

### Task 4: Written-back rules — the rule rung

**Files:**
- Create: `src/iladub/route/rules.py`, `vocab/queries/route-boundary-rule.rq`, `vocab/queries/route-doctype-rule.rq`,
  `readings/route/rules.ttl` (header + prefixes only)
- Test: `tests/test_route_rules.py`

**Interfaces:**
- Consumes: `Line`, `BoundaryAnswer`, `DoctypeAnswer` (Task 3).
- Produces: `RULES_PATH: Path`; `rule_boundary(page_lines, rules: Graph) -> BoundaryAnswer | None`;
  `rule_doctype(extent, rules: Graph) -> DoctypeAnswer | None`;
  `write_back_boundary(answer, page_lines, rules: Graph) -> None`; `write_back_doctype(answer, extent, rules: Graph) -> None`.

Rules are AXIOM, open-world derivations keyed by `route:cueSha` (spec § 6 B5; hashes keep template text
out of git). Semantics the implementer must keep:
- Boundary: if any non-conflicted STARTS cue matches a page line → STARTS at that line, evidence = it;
  if **two or more** lines match STARTS cues → abstain (`None`; Review Focus 1); else if a CONTINUES cue
  matches → CONTINUES citing every matching line; else `None`. The NOT EXISTS is page-scoped.
- Doctype: a rule fires when **every** one of its cue shas occurs in the extent; it reproduces the answer
  with ids = first occurrence. Two firing rules of different kinds → abstain.
- Write-back adds a cue; a cue already present with the **opposite** verdict/kind marks both
  `route:conflicted true`, and conflicted rules never fire. Write-back is never called on a held-out PDF
  (Task 6 enforces).

- [ ] **Step 1: Write failing tests:** `test_starts_cue_fires`, `test_two_starts_on_a_page_abstain`,
  `test_continues_needs_a_cue`, `test_conflicting_write_back_disables_both` (write STARTS then
  CONTINUES for one sha → `rule_boundary` returns `None` on a page holding that line),
  `test_doctype_rule_needs_all_cues`, `test_no_text_in_rules_file` (after write-back from lines
  `"Sellers: ACME"`, the serialized graph contains no `"Sellers"` substring).
- [ ] **Step 2: FAIL. Step 3: implement. Step 4: PASS.** Re-measure `.ttl`/`.rq` pins.
- [ ] **Step 5: FALSIFICATION:** remove the `conflicted` filter from `route-boundary-rule.rq`; show
  `test_conflicting_write_back_disables_both` failing; restore; green.
- [ ] **Step 6: Commit** `feat(route): written-back rules as hashed cues (AXIOM)`.

### Task 5: The model proposers (NEURAL)

**Files:**
- Create: `baml_src/route.baml`, `src/iladub/route/proposers.py`
- Test: `tests/test_route_proposers.py`

**Interfaces:**
- Consumes: answer types (Task 3), `MODEL_IDS`, `*_available` (Task 1).
- Produces: `@dataclass(frozen=True) class Proposed(Generic[A]): answer: A; model: str` (the model id
  that answered — the trace's `route:modelId`, S2); `Proposer` protocol with
  `boundary(listing: str, previous_tail: str) -> Proposed[BoundaryAnswer] | None`,
  `doctype(listing: str, admitted: list[str]) -> Proposed[DoctypeAnswer] | None`, attribute `client: str`;
  `RecordedProposer(live: Proposer | None, client: str, directory: Path | None = None)`;
  `default_proposers() -> list[Proposer]` (Jev first if available, then Haiku);
  `listing(lines: list[Line]) -> str` (one `"<id>\t<text>"` line per line; ids 0-based).

BAML (`route.baml`) — closed shapes only, ids never page values (CLAUDE.md § 8):
`enum PageVerdict { STARTS CONTINUES REFUSES }`, `class BoundaryReading { verdict PageVerdict; start_line int?; evidence_lines int[] }`;
`enum DocKind { CONTRACT OTHER REFUSES }`, `class DoctypeReading { kind DocKind; party_lines int[]; commitment_lines int[]; other_evidence_lines int[]; proposed_type string?; admitted_type string? }`.
Functions `RouteBoundary{Haiku,Jev}(listing, previous_tail)` and `RouteDoctype{Haiku,Jev}(listing, admitted_types)`
— one per client (`Jev` variants only if Task 1 kept `RouterJev`). The boundary prompt is given the page's
numbered lines plus the previous page's last lines **unnumbered** as `previous_tail` (context only, so no
cited id can point off the page), and asks: *does a new document start on this page, and at which line?* The doctype prompt asks
the FIBO checklist question in plain words (spec § 3 table) and says "if it is not a contract, cite the lines
that show what kind of document it is; if you cannot, refuse".

Readings are recorded like `caption.py:199-245`: key = `sha256("route-boundary\n" + client + "\n" + listing)`
(resp. `route-doctype`), directory `readings/route_boundary/` and `readings/route_doctype/`; JSON holds
the reading fields **and `"model"`** (the model id at recording time), and **no free-text note**.

- [ ] **Step 1: Write failing tests:** `test_recorded_reading_replays_without_live` (write a JSON into
  `tmp_path`, `live=None` → a `Proposed` whose `.model` is the file's `"model"`, not the current client's); `test_miss_without_live_is_none`;
  `test_records_only_under_flag` (a fake live proposer; no file without `ILADUB_RECORD_READINGS=1`, a file
  with it); `test_reading_has_no_note_field`; `test_default_order_jev_then_haiku` (monkeypatch availability).
- [ ] **Step 2: FAIL. Step 3: implement + `baml-cli generate`. Step 4: PASS.**
- [ ] **Step 5: FALSIFICATION:** make the recorder write without checking the flag; show
  `test_records_only_under_flag` failing; restore; green.
- [ ] **Step 6: Commit** `feat(route): Q-boundary and Q-doctype proposers (NEURAL, recorded)`.

### Task 6: The router — ladder, extents, trace

**Files:**
- Create: `src/iladub/route/router.py`, `src/iladub/route/__main__.py`
- Test: `tests/test_route_router.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `route(pdf: bytes, *, learn: bool, proposers: list[Proposer], rules: Graph, admitted: list[str]) -> Graph`;
  CLI `python -m iladub.route run <pdf> -o <out.ttl> [--learn]` (writes rules back to `RULES_PATH` only with `--learn`).

Behaviour (spec § 4–§ 5):
1. `extract_lines`; zero lines in the PDF → one `BoundaryDecision` chosen `RefusedOption`, reason
   `no-text-layer`, nothing else (Review Focus 3). Pages with no lines are skipped (Review Focus 2).
2. First page with lines: `GivenRung` STARTS at its first line. Each later page: rule → each proposer;
   the first answer passing `check_boundary_local` is kept *provisionally*; none → page REFUSED.
3. Extents = admitted starts in order (decidable exact computation, PROCEDURAL). **(call)** A refused page
   means the router does not know whether a document starts on it, so from the first refused page to the
   PDF's end no extent is asserted: one `route:Document` with no `startsAt`/`endsAt` and one refused
   `DoctypeDecision` (reason `boundary-refused`) stand for that tail. Extents before it are unaffected.
4. Q-doctype per extent: rule → proposers, each disposed by `check_doctype`; then each admitted STARTS is
   disposed by `check_boundary_split`; a start that fails the split is withdrawn and **both** its extents'
   documents are refused (reason `split-refused`) — never merged silently, which would assert a
   continuation nobody answered.
5. Trace: every answer is a holon per Task 2's table; `prov:used` = the cited lines' IRIs; `dec:rationale`
   in domain words with page/line positions only (no page text), e.g.
   `"contract: parties p1 l4, p1 l6; commitment p1 l12; decided by claude-haiku-5-5; admitted by the contract checklist"`.
   An OTHER answer adds a `route:ProposedType` with the model's label (or uses the `admitted_type`).
6. With `learn=True`, write back every admitted model answer (not rule answers). Validate the output graph
   against `route-shapes.ttl`; a non-conforming graph raises (producer-side guard, CLAUDE.md R89).

- [ ] **Step 1: Write failing tests** with fake proposers and reportlab PDFs:
  `test_single_contract` (one document, `route:ContractDocument`, 2 holons for a 2-page PDF + 1 doctype);
  `test_mid_page_start` (fake proposer STARTS at line 2 of page 2; two documents; second `startsAt` that line);
  `test_split_refused_withdraws_both` (fake doctype answers fail the split → two refused doctype holons, no `ContractDocument`);
  `test_blank_page_is_absorbed`; `test_scan_refuses_whole_pdf` (a reportlab page with only a drawn rectangle);
  `test_route_ignores_file_name` (same bytes → isomorphic graphs after replacing the source IRI);
  `test_rule_rung_decides_before_models` (a firing rule → the proposer is never called; holon `route:rung route:RuleRung`);
  `test_learn_false_never_writes_rules`; `test_output_conforms_to_membrane`.
- [ ] **Step 2: FAIL. Step 3: implement. Step 4: PASS.**
- [ ] **Step 5: FALSIFICATION:** skip `check_boundary_split` (keep provisional starts); show
  `test_split_refused_withdraws_both` failing; restore; green.
- [ ] **Step 6: Commit** `feat(route): the router — ladder, extents, decision trace`.

### Task 7: m4 — the mid-page test document

**Measured 2026-11-02** (pypdfium2, lowest non-space char of the last page, bottom-up points): form-fill
last pages run to the page foot (`gafta-48-3` 22.7, `gafta-79b-3` 62.5, `gafta-124-3` 36.9), so no room;
Word-export last pages leave room: **`gafta-48-3.word-export` ends at y = 325.2 of 841.92**. Hence m4 =
**`gafta-48-3` word-export + `gafta-124` unfilled** (m1's pairing, held-out fill — spec § 7).

**Files:**
- Modify: `scripts/synthetic_contracts/build.py` (`compose`, `build`), `examples/synthetic-contracts/synthetic.ttl`
  (one term: `syn:joinMidPage`, boolean, on a `syn:Component`)
- Create: `examples/synthetic-contracts/mixed/m4.ttl`, `examples/synthetic-contracts/truth/m4.ttl` (generated)
- Test: `tests/test_synthetic_contracts_build.py`

**Interfaces:** `compose(parts, doc_id, join_mid_page: frozenset[int] = frozenset())` — index k in the set
means component k's first page is drawn onto component k-1's last page.

Join rule (PROCEDURAL — the generator makes documents; nothing tuned): `y_ink` = top-down bottom of the
lowest non-whitespace char on component k-1's last page; component k's first page is placed as a form
XObject **uniformly scaled** by `s = (H - y_ink) / H_k` into the band `[y_ink, H]`, left edge at 0; its
remaining pages follow. Truth: part a's box on that page is `top 0, bottom y_ink`; part b's first box is
`top y_ink, bottom H, x0 0, x1 s·W_k`; part b's later boxes shift by one page less. Refuse (raise) when
`y_ink ≥ H` (no band).

- [ ] **Step 1: Write failing tests:** `test_mid_page_join_truth` (two reportlab parts, the first ending at
  y=500 top-down → composed page count = n1 + n2 − 1, part b's first box `top == y_ink`, part a's box on
  the join page `bottom == y_ink`); `test_join_refuses_full_page`; `test_m4_spec_is_held_out`
  (`mixed/m4.ttl` components are `gafta-48-3`/word-export and `gafta-124`/unfilled, component 2 `syn:joinMidPage true`).
- [ ] **Step 2: FAIL. Step 3: implement; build m4 locally (`python -m scripts.synthetic_contracts build`);
  commit its truth. Step 4: PASS.** Render page 8 of `synthetic/out/m4.pdf` to PNG and look at it; state
  in the report that the rules page sits below the contract's last line with no overlap.
- [ ] **Step 5: FALSIFICATION:** shift part b's first box by +1 page in `compose`; show
  `test_mid_page_join_truth` failing; restore; green.
- [ ] **Step 6: Commit** `feat(synthetic): m4, a rules document starting mid-page`.

### Task 8: Owner admission of a proposed type

**Files:**
- Create: `src/iladub/route/admit.py`; Modify: `src/iladub/route/__main__.py`
- Test: `tests/test_route_admit.py`

**Interfaces:** `admit(proposal_label: str, type_name: str, anchor: URIRef, owner: str, types_path: Path) -> URIRef`
(writes `route:<type_name> a owl:Class; rdfs:subClassOf route:Document, <anchor>; rdfs:label` plus an
`iladub:PromotionDecision` — options admit/refuse, chosen admit, `dec:decidedBy` the owner agent,
`dec:rationale` — into `route-types.ttl`); `refuse(...)` records the PromotionDecision choosing refuse and
writes no class; `admitted_types(types_path) -> list[str]`. CLI: `python -m iladub.route proposals <out.ttl>...`
(lists distinct proposed labels with counts) and `python -m iladub.route admit|refuse ...`.

- [ ] **Step 1: Failing tests:** `test_admit_writes_class_and_promotion` (result conforms to
  `dec-shapes.ttl` + `iladub-shapes.ttl`); `test_refuse_writes_no_class`; `test_admitted_types_lists_names`;
  `test_anchor_must_be_gist_or_fibo` (any other namespace raises).
- [ ] **Step 2: FAIL. Step 3: implement. Step 4: PASS.**
- [ ] **Step 5: FALSIFICATION:** drop `dec:decidedBy` from the PromotionDecision; show
  `test_admit_writes_class_and_promotion` failing; restore; green.
- [ ] **Step 6: Commit** `feat(route): owner admits or refuses a proposed type`.

### Task 9: The scorer, then the live run against the bar

**Files:**
- Create: `scripts/synthetic_contracts/score.py`, `tests/test_synthetic_contracts_score.py`,
  `docs/superpowers/2026-11-0X-router-bar-measured.md` (counts only)
- Commit (generated): `readings/route_boundary/*.json`, `readings/route_doctype/*.json`, `readings/route/rules.ttl`,
  `vocab/ontology/route-types.ttl` (if the owner admits)

**Scoring contract** (spec § 10's last bullet, stated here): truth parts **without `syn:parent`** are
documents; `contract-form`, `charter-party` → `route:ContractDocument`; `rules` → "not a contract"
(`NotAContractOption`). Sub-parts (`blank`, `table`) are ignored.

**Interfaces:** `score(route_graph: Graph, truth_graph: Graph, lines: list[Line]) -> Score` with fields
`b1_correct, b1_wrong, b2_correct, b2_wrong, refused, rung_counts: dict[str, int]`, and
`agree(a: Graph, b: Graph) -> tuple[int, int, int]` (agreeing, disagreeing asserted pairs, refused-vs-asserted).
B1: an asserted start line is correct iff its `top` lies in the truth box of the document it starts **and**
every earlier line on that page lies outside that document's boxes; an asserted CONTINUES on a page holding
a truth start is a wrong boundary. B4 compares **asserted** outcomes only and reports refused-vs-asserted
separately — **(call), flag it to the owner** in the report (a refusal is not wrong, so it cannot break agreement).

- [ ] **Step 1: Failing scorer tests** over hand-built graphs: `test_mid_page_start_scored_exact`
  (start one line too early → wrong), `test_continues_over_a_truth_start_is_wrong`, `test_refusal_counts_but_is_not_wrong`,
  `test_subparts_are_not_documents`, `test_agree_ignores_refusals`.
- [ ] **Step 2: FAIL. Step 3: implement. Step 4: PASS. Step 5: FALSIFICATION** (drop the "every earlier
  line outside" clause; `test_mid_page_start_scored_exact` fails; restore; green). **Commit.**
- [ ] **Step 6: Oracle falsifier (PROPOSED — may refute the boundary oracle).** With real Haiku doctype
  answers, force a STARTS at every later page top of the 16 single-document learning PDFs and run
  `check_boundary_split`. **If any is admitted, STOP**: report the admitted cases, do not run Step 7, and
  hand the next loop "strengthen the boundary oracle" (no oracle, no worker). Paste the counts either way.
- [ ] **Step 7: Learning pass** (`BAML_LIVE=1 ILADUB_RECORD_READINGS=1`, `--learn`), sorted order, over the
  18 learning PDFs (spec § 6 table). Then `python -m iladub.route proposals synthetic/route/*.ttl` and ask the
  owner (AskUserQuestion) to admit or refuse each proposed label. Then the **held-out pass** (no `--learn`)
  over the 9 held-out PDFs.
- [ ] **Step 8: Report** — for both sets: B1–B3 counts, refusals, B4 triples per fill, B5 rung counts on
  held-out (how many documents a rule decided with no model), B6 = membrane conformance of every output.
  The bar passes iff B3 = 0 wrong on both sets and every output conforms. Report it at that strength.
- [ ] **Step 9: Commit** readings, rules, types and the report.

### Task 10: Baseline, register, handoff

- [ ] **Step 1:** `git add` all new inputs, then `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`
  (~24 min, serial, nothing else running). Expected: `git diff -- tests/corpus-baseline/` touches only
  `inputs.json` (the router is not on the compile path). Any snapshot change is a finding — stop and report it.
- [ ] **Step 2:** residue rows (with tally snapshots) for: the HDC rung not built; Jev (if Task 1 refuted
  it); one start per page (Review Focus 1); the boundary-refused-tail call (Task 6); B4's refusal call;
  scans (phase 2); `w3id.org/iladub/route` has no redirect (MEASURE first whether `…/tab` has one).
- [ ] **Step 3:** handoff `docs/superpowers/2026-11-0X-document-router-executed-handoff.md`, part 5 first, typed.
- [ ] **Step 4:** whole-branch review (superpowers:requesting-code-review), then PR.
