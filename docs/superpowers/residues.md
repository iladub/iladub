# Residue register

Deferred items from the ET(K)L loops, in one tracked place. Each row records what the residue is,
where it was **measured** (never assumed), why it was deferred, and what would close it.

**This register is canonical.** Loops append rows here; a loop that closes a residue **strikes** its
number (`~~R92~~`), records the closure evidence in place, and moves the full row from
[`residues-open.md`](residues-open.md) to [`residues-closed.md`](residues-closed.md) — **it does not
delete the row.** Specs may describe a residue in prose, but the list of open residues lives here.

> ⚠️ **CORRECTED 2026-08-17** (E4, plan `plans/2026-08-17-the-gate-and-the-label.md` Task 3): this
> paragraph used to say a closing loop *"deletes its row in the same change."* CLAUDE.md § Deferred
> residues reverses that, and for a stated reason — a deleted row erases the proof of repair and
> silently shrinks the tally's denominator, which is the one number that shows the register is not
> pure degradation. The reversal was recorded in CLAUDE.md on 2026-08-12 and never propagated here.

Started 2026-07-29 (Loop D), collecting items previously scattered across four specs and the SDD
ledger.

## The tally (convention added 2026-08-12)

**Raising a residue is visible; closing one is not.** A register that only counts what it opens
reads as pure degradation — R92 sounds like ninety-two defects and nothing repaired. So every new
row records, in parentheses after its number, **the state of the register at the moment it was
raised**: `| R97 (18/87 closed) |` means that when R97 went in, 18 of the 87 rows then present
were closed. (Corrected 2026-08-20: this example read `17/87` while the row it quotes —
`residues-open.md:77` — reads `18/87`. The example is quoted from a real row and must match it.)

The parenthetical is a **snapshot and is never updated afterwards**. That is the point — read
down the column and the ratio is a trend line: a register whose closed-fraction climbs is a
project paying its debts, one whose fraction falls is accumulating them, and neither fact is
legible from the highest number alone.

Two consequences for how rows are handled:

- **Closed rows are struck (`~~R4~~`), never deleted.** They are the other half of the
  denominator. A deleted row silently improves nothing and erases the evidence of repair.
- **A closing change records the closure evidence in the row it strikes** — what was measured,
  and what now prevents recurrence.

**As of 2026-09-01: 147 rows, 41 closed, 106 open.** (Ten numbers between R1 and R96 were never
issued as rows; the denominator is rows that exist, not the highest number.) **CORRECTED 2026-09-01** (loop `progress-census`): this line read *"As of 2026-08-24: 116 rows, 24 closed, 92 open"* and was **31 rows and 17 closures stale** — measured by parsing the file's own rows (`^\| R\d+ \|`, status column), not by trusting the header. Nothing machine-checks this line; `test_residue_register_integrity.py` pins the index/detail correspondence but not the HEADER's arithmetic, which is why it drifted through 20 loops unnoticed. That is the same class as the stale rows the three-way split was built to prevent. Was 18 closed at
`e3f447a`; loop `the-gate-and-the-label` closed ~~R102~~ and ~~R104~~ and loop 1 of the R97–R104
split closed ~~R103~~, none raising a new row; loop `the-arc-has-a-denominator` raised R105, R106,
R107, R108, and — at loop close, from its whole-branch review and its warning attribution —
R109, R110, R111 and R112, and closed ~~R105~~ in
task 6; loop `the-arc-has-edges` raised R113–R119 at close and R120 in its final-review fix wave,
and closed none; loop `the-worktree-that-resolves` closed R121 and R118 (task 5) and raised R122
and R123 (task 6, at loop close), then raised R124 and R125 (final whole-branch review fix wave,
2026-08-23) — R124 records that spec §4.4's stated mechanism is superseded by the shipped
materialise-before-unlink ordering, R125 records the pre-existing, not-this-branch's, unconstrained
`prog:oracleArtifact` path shape. **R126 was raised by no loop at all** (2026-08-24): the direction-setting session for `holon:05` ran the criterion's cheapest invalidating measurement *before* writing its spec, and found the property's declared `rdfs:domain` is a class nothing instantiates. A row raised by pre-flight measurement rather than by a loop's residue is the cheapest kind this register holds, and the closed-fraction cannot tell it from a leak either. **The previous line's "88 open" had already undercounted by one
before task 5's edit** (111 rows summed at the time — 89 open + 22 closed — not 110) — corrected
there to the re-run figure rather than carried forward.

**`the-worktree-that-resolves` is 2 closed / 2 raised, and the two raised rows are of different
kinds.** [[R122]] is a question the loop's own spec (§9) declined **before it started** and
recorded as declined — the shape [[R115]] and [[R113]] already have. [[R123]] is different and is
the more useful of the two: it exists because task 6 **re-ran a census task 4 had asserted from
reading** and found it refuted — *"zero of the 29 declared artifacts are `.py`"* is false, two are.
A row raised by an instrument refuting its own loop's prose is [[R120]]'s class again, third
instance in two loops, and the closed-fraction cannot tell that apart from a leak.

**Eight raised, none closed, is the honest reading of that last clause and it is worth saying
out loud.** `the-arc-has-edges` added a capability (a criterion→criterion dependency graph, its
membrane and its landscape) rather than repaying debt; its rows are limitations it
*named in its own spec* before it started (R113, R114, R115) or findings its own instruments
and its own reviews produced (R116, R117, R118, R119, R120), and two — R117 and R118 — were
found only because the loop
built something that could refute a claim. R120 is a different kind again: the final whole-branch
review found a figure the loop had *shipped in source* and could no longer re-derive, which is a
row a loop can only raise about itself. A loop that raises rows it discovered by refuting
itself is not the same as one that leaks them, but the closed-fraction does not know that, and
this register is deliberately the kind that does not let the distinction flatter the number.

**Verified, not asserted — and re-run whenever this line is edited:**

```
$ awk -F'|' '/^\| R[0-9]/ {print $3}' docs/superpowers/residues.md | sort | uniq -c
  25  closed
 102  open
```

> **UPDATED 2026-08-25** (loop `the-membrane-reports-its-health`, Task 7), by re-running the command
> above rather than by arithmetic on the sentence. **127 rows, 25 closed, 102 open.** The loop closed
> ~~R126~~ (Tasks 1+3 gave the `etkl` doc-holon fabric its first instance datum) and raised eleven:
> R130 in Task 6, and R127, R128, R129, R131, R132, R133, R134, R135, R136, R137 here. **1 closed /
> 11 raised is the honest reading**, and the composition is worth stating because the closed-fraction
> cannot see it. **Seven were named in the spec BEFORE the loop started** (§9's *"what this loop does
> NOT do"* and §11) — R127–R129 and R131–R134 — so they are declared scope boundaries, not leaks.
> **Four the loop's own instruments produced, and those are the ones worth reading:** R130, when Task
> 6's enumerator measured 164 unreachable pairs and refuted its own tripwire's premise; R135, when
> M19's ablation refuted an edge M17 had just forced this task to assert; and R136 + R137, which came
> out of Task 7's **falsification round** — the deliberate attempt to break its own record and see
> what caught it. Two things did not: a met criterion may cite *"Planned work (not done yet)"* as its
> source (R136), and this register has no integrity check of its own (R137). That fourth kind is
> [[R120]]'s class — a loop refuting itself — and it is the only kind a loop can raise about itself.

> ⚠️ **CORRECTED 2026-08-21** (task 6). This line read *"As of 2026-08-20: 94 rows, 21 closed, 73
> open"* and was stale by two rows: R105 and R106 were appended on 2026-08-21 without it being
> re-run, so the register under-reported its own size the day after the note above was written.
> Third recurrence of the same drift. The command is the authority; this sentence is a convenience.

> ⚠️ **CORRECTED 2026-08-20** (loop `the-arc-has-a-denominator`). This line said *"As of 2026-08-17:
> 94 rows, 20 closed"* and had been stale by one since ~~R103~~ closed. The staleness was found by
> `scripts/cockpit.py`, which reads the rows rather than this sentence and had been printing 21/94
> while the prose said 20 — the gauge caught the register. **A figure in prose beside a figure that
> is counted will drift; the command above is the authority, this sentence is a convenience.**

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |

## Why this file is an index (split 2026-08-12)

The register reached **146,716 characters — roughly 36.7k tokens**. CLAUDE.md tells every
contributor to *check the register*, and at that size doing so costs about **46% of the entire
40%-of-window budget** the context rule allows for design work. The instruction had become
impossible to follow, so nobody followed it: rows were grepped, not read, and stale rows
(R87, R88) were consumed as fact and cost real sessions.

So this file is now the **index**, readable in full for a few thousand tokens. The full text
of each row lives in two detail files, and you open only the rows you need:

- **[`residues-open.md`](residues-open.md)** — the open rows, in full.
- **[`residues-closed.md`](residues-closed.md)** — the closed rows, kept as evidence of repair.

**A row's one-line summary below is a POINTER, never the residue.** Do not act on it, quote it
in a spec, or plan against it without opening the full row — that shortcut is exactly how R87
and R88 propagated wrong. The index tells you *whether* to read; the detail file tells you *what*.

## Index

| # | Status | Summary — a pointer only; open the detail file before acting |
| --- | --- | --- |
| R1 | closed | CLOSED with R13 (Loop G attempt 2, 2026-07-30) |
| R2 | closed | CLOSED for the ruled path (Loop F, 2026-07-29) |
| R3 | open | Nested-subset vote |
| R4 | closed | CLOSED for the ruled hierarchical path (Loop H, 2026-07-30) |
| R5 | open | Proposal inputs not recorded |
| R6 | open | Centre-only merge candidate |
| R7 | open | Live BAML path unreachable |
| R8 | open | `ProposeHeaderSpan` missing |
| R9 | open | Conservation shape unreachable |
| R10 | open | `detect_bands` cuts one line too high |
| R11 | open | Mixed header rows |
| R12 | open | Split-table recurrence |
| R13 | closed | CLOSED for the ruled path (Loop G attempt 2, 2026-07-30) |
| R14 | open | The collapse can delete an author-drawn boundary |
| R15 | open | NEURAL residual: a wide label over blank/unclaimed columns |
| R16 | open | The UNRULED path keeps the split-number defect |
| R18 | open | Groups without a confirmed total stay ungrouped — and an unconfirmed total POLLUTES the next group |
| R19 | closed | CLOSED (Loop R41 Task 5, 2026-08-05) |
| R20 | open | Unconstrained contract fields stay propositions |
| R23 | open | `dg:AssertionInNavShape` unreachable from live extractor output |
| R24 | open | A wiki page citing an untracked/gitignored path is permanently exempt from staleness with a green membrane |
| R25 | open | The ≥2-references wiki admission rule is unenforced |
| R26 | open | The release gate fails OPEN on a same-day or backdated contradiction |
| R27 | open | `_IMPACT` scans the whole file unanchored |
| R28 | open | The promotion queue is one-shot |
| R29 | closed | CLOSED (Loop M Task 3, 2026-08-02) |
| R30 | open | The parent-vs-wrap-fragment residual fires INSIDE the engaged header block, not outside it |
| R31 | open | A double-drawn header-block border disengages the law |
| R32 | open | Loop L amplifies a pre-existing Loop G defect: header-confirmed boundary refinement can fabricate a column boundary the author never drew |
| R33 | closed | CLOSED FOR MARKED DOCUMENTS (Loop O, 2026-08-03) — the continuation LICENCE |
| R34 | open | The carried-header MATCHING law is Python control flow, not an AXIOM — and its `carried_header_roles` entry point is public and unguarded |
| R35 | closed | CLOSED (Loop N, 2026-08-03) |
| R36 | open | The feed's pass-3 identity guarantee is enforced on the `row_id` STRING, not the minted record subject |
| R37 | open | The document-level arithmetic pass's retraction semantics are a MODELLING CHOICE, not a derived fact |
| R38 | open | `feed._header_path` DOES read a `tab:DerivedRowGroup`'s `tab:headerLevel` |
| R39 | open | `vocab/queries/row-group-nesting.rq` (loop I's AXIOM, unchanged) is now the dominant cost in a chained document's compile |
| R40 | open | The document's outermost total (`Grand Total`) reads as an unconfirmed, ungrouped row |
| R42 | closed | CLOSED (Loop Q Task 7, 2026-08-04) |
| R43 | open | ONS gov-stats document: 1× `REGION_TILING_FAILED` plus an unnamed oddity — an `UNSUPPORTED_TABLE` kind carrying verdict `asserted` |
| R44 | open | BFS gov-stats document: 2× `KIND_NOT_SUPPORTED`, 2× `REGION_TILING_FAILED`, 5× `ROUND_TRIP_FAIL` |
| R45 | closed | CLOSED 2026-08-31 — `matrix._level_tops` deleted; a header level is a band line. WHO 0.5597 → 0.9096, 3 escalations → 0 |
| R46 | open | Fetcher hardening — `_pdf_facts` crashes uncaught on non-PDF bytes at BOTH call sites |
| R47 | open | Both the grid-region peel and the hrule-box weld are scoped LEADING-only — a trailing full-width strip is neither peeled nor welded |
| R48 | open | `sectiongraph._leading_box_y`'s header-box-candidate selection can, on a document shape the interior-crossing test does not discriminate, locate a… |
| R49 | open | Spec §4.2's GRAPH-level key form (`tab:DerivedRowGroup` covering a section's rows, `tab:hasLabel` → the source heading cell, `prov:wasDerivedFrom`… |
| R50 | open | `document._confirm_section_total`'s totals oracle reads only the table's LAST row as the total candidate — several STACKED trailing lines below a s… |
| R51 | open | `document._band_subgraph`'s subject-collection licence leans on the `_index_suffix` URI-prefix minting convention holding everywhere a new subject… |
| R52 | open | Class-level documentation debt: `tab:DetectedAggregationRow` (loop H), `tab:continuesTable` (loop M), and `tab:SectionTotal` (loop Q) ship with NO… |
| R53 | open | `iladub:GroundedNodeShape` validates `groundsTo`'s PRESENCE only (`sh:minCount 1`), never its RESOLUTION — a `GroundedNode` whose `groundsTo` IRI r… |
| R54 | open | `feed.table_records`'s identity-prefix and the loop-Q E2E's cascade marker-set both assume the section HEADING is drawn ABOVE its notices — a posit… |
| R55 | closed | CLOSED (loop-quantity, 2026-08-06) — WITH ITS ATTRIBUTION CORRECTED |
| R56 | open | The hierarchical `n == 0` ROUND_TRIP_FAIL branch does not carry absorbed unit markers |
| R57 | open | Membrane redundancy — 8.2 s of the final pass's 12.6 s re-checks shapes the region gate already checked |
| R58 | closed | CLOSED (loop-subclass, 2026-08-06) |
| R59 | open | Real-document agreement is necessary but NOT sufficient evidence for an engine swap |
| R60 | open | rudof's n-triples parse is now the membrane's dominant cost |
| R61 | open | Emitter-typing is now an unenforced invariant — **0 instances measured 2026-08-18; the 14 live are emitter/ontology disagreement, and the probe is renamed** |
| R62 | open | Apple page 0 is unlocked by one band, not compiled |
| R63 | open | `unit-marker-column.rq`'s OWN-COLUMN purity check treats only `tab:Blank` as a wildcard, not `tab:ParenthesizedNumber` |
| R64 | open | Abstention (`tab:ParenthesizedNumber`/`tab:datatypeAbstains`) weakens the header-boundary scan |
| R65 | open | `celltype._CURRENCY`'s `[\d,]+` admits a comma-only numeric body |
| R66 | open | The reader's `optionSpace` is thin — `kind`'s three-value enum is the only judgement in the recorded chain with more than two options; every other… |
| R67 | open | The recorded chain is complete at compile-path granularity, not at query granularity |
| R68 | open | No real corpus document exercises the transposed path — the R55 ordering (`looks_transposed` before `transpose_is_coherent`) is proven only on synt… |
| R71 | open | The kind gate is load-bearing |
| R72 | closed | CLOSED (loop-data-grid, 2026-08-08) |
| R74 | open | The cbh data grid leaks one row from a SECOND table on the same page |
| R76 | open | Spec-writing discipline: proposal and disposal must come from DIFFERENT sources |
| R77 | open | cbh's four panel totals are missed on the SCORE path too, for the identical no-label reason |
| R78 | open | An unparseable member cell is summed as zero by `confirms_aggregate` |
| R79 | open | An adopted page's unread structure is escalated as ONE page-level residue candidate |
| R80 | open | apple p1's indent hierarchy is read by nobody |
| R83 | open | At PAGE scope an adopted page's `rep.graph` escalates nothing for a band the grid never TOUCHED, while the report still books its tokens |
| R84 | open | `adoption.build_ledger` counts every admitted line's tokens as asserted, whether or not any band was scoring that ink |
| R85 | open | `transpose-coherent.rq` is quadratic in row count |
| R86 | open | A quarantined concept mints NO decision holon, so the proposition half of the epistemics is unattributed |
| R87 | closed | CLOSED 2026-08-16 — wired into `compile._DEC_SHAPE_FILES` AND furnished by `escalation-furnish.rq`; the wiring alone was measured insufficient |
| R88 | closed | CLOSED 2026-08-13 — skolemized at the payload seam; `compile._DEC_ENGINE` deleted |
| R89 | open | `BandRecorder.record`'s Python guard now duplicates two constraints the membrane enforces — **rule adopted 2026-08-17 (in CLAUDE.md); application to that guard still open** |
| R90 | open | The bbox is dropped from every `ROUND_TRIP_FAIL` proposition |
| R91 | closed | `document.py:1498` and `datagrid.emit_data_grid` now both emit `dec:decidedBy` on the same admission holon |
| R92 | closed | CLOSED 2026-08-12 — the 39 float-valued `xsd:decimal` emitters are converted, and a tripwire prevents the 40th |
| R93 | closed | CLOSED 2026-08-12 with R92 |
| R94 | closed | CLOSED 2026-08-13 — one N-Triples artifact, both legs; own prescribed remedy REFUTED (parser is inside the engine boundary) |
| R95 | open | `_payload`/`_payload_nt`'s `audit=False` escape hatch is a standing hazard, fenced by a substring-scan test |
| R96 | open | `audit_literals`'s LEXICAL half is a silent no-op if rdflib's `NORMALIZE_LITERALS` global is ever `False` |
| R97 | open | Four wired `tab:` shapes the corpus does not exercise — 0 focus nodes each |
| R98 | closed | CLOSED 2026-08-31 — the shape is LIVE: R45 gave who-wfa's already-refused pair (1,2) a table on both sides, so the withheld edge is now written |
| R99 | open | `iladub:NoLeakShape` can never fire at compile — 11 focus nodes, unreachable term |
| R100 | open | `dec:EscalationShape` live at document scope, idle at page scope; registry cannot say so |
| R101 | open | A green CI tick can cover less than it looks — a module-level skip guard hides a whole module behind one skip line |
| R102 | closed | CLOSED 2026-08-17 (`b09dbd1`) — the `dec` leg is unconditional at document scope; re-measured 769/769, 0 never (was 316) |
| R103 | closed | CLOSED 2026-08-20 — NO: admitting `tab-datagrid.ttl` to `_FULL_ONT` is a provable no-op (27 pages, closure delta **0**); no ontology subject reaches an engine, so `ONT_VISIBLE` and `OUTSIDE_MEMBRANE` were the same case all along |
| R104 | closed | CLOSED 2026-08-17 (`742e862`) — `_validate` returns the refusing legs; `_refusal_message` names them |
| R105 | closed | CLOSED 2026-08-21 (task 6, Ruling 18) — **M10**: every criterion's `prog:source` path must exist and its line be in range; the `etkl` join is kept beside it, not replaced |
| R106 | open | A `prog:met true` arc criterion can cite evidence containing ZERO focus nodes for the shape it claims — the membrane says `shacl_ok=True` either way; the rule that catches it is prose |
| R107 | open | The arc membrane admits two `prog:Rung` nodes sharing one `prog:rungKey` — both readers are immune today, for **different** reasons; "that is luck, not design" |
| R108 | open | A `prog:blockedBy` naming a **closed** register row is admitted — M7 checks presence, not state, and R105 is now exactly such a row |
| R109 | open | Two divergent `<path>:<line>` parsers — M5 strips the line, M10 checks it; one defect wearing four faces, all latent, all measured |
| R110 | open | The arc membrane's own messages degrade: two unnumbered `sh:nodeKind` refusals and three predicates with no property shape |
| R111 | open | Strip legibility: `frontier`/`ready` carry no unit, the docstring illustration is stale, and a dead `else 0.0` would render the forbidden `0/0` |
| R112 | open | 60 invisible `ResourceWarning`s — pytest never un-ignores the class, so the reported warning count is not the raised count |
| R113 | open | A5's ablation grounds consumption at FILE granularity — an edge means "X's oracle needs this file", never "X needs the term at line n" |
| R114 | open | `etkl:01`'s oracle cannot EXECUTE in a worktree (gitignored corpus), so no edge can be asserted at either of its ends — and it is the `etkl` rung's only met criterion. **REMEDY CORRECTED 2026-08-23: [[R121]] (the un-ablatable half) is now CLOSED; what remains is the corpus (still deliberately not materialised) and [[R113]] (file granularity)** |
| R115 | open | The 80% orphan question is NOT subsumed by the dependency graph: 72 of 87 open rows block no criterion of any rung (re-measured at the tree's final state; the row's original 65 of 80 predates this loop's own seven rows) |
| R116 | open | M20 candidate: an orphan `rdf:Statement` rationale node, and a `prog:dependencyRationale` on a criterion, are refused by nothing — dead prose is admitted |
| R117 | closed | **CLOSED 2026-08-29** by D2 (`vocab/queries/alignment-subject.rq`) + the membrane's extension to every tracked `.ttl` — and its live instance was finally found (six `tab:aggFn*` in `tab-fno-align.ttl`), quoted RED then repaired by declaring them. Re-authoring `holon:02 → holon:01` is NOT included and is carried forward as `R151`. Nothing checks that the terms `iladub-hga-align.ttl` aligns are DECLARED — a dangling subclass ships green, and that is why `holon:02 -> holon:01` was refuted |
| R118 | closed | CLOSED 2026-08-23 in two halves: Task 4 (`5f2cad9`) makes a collection ERROR score `FAILED` only when its exception names a removed path; Task 2 (`2d08f06`) materialises `baml_client`, removing the only live instance (**6** modules, re-derived at close, not 5 — `tests/test_to_rdf.py` breaks transitively). Full evidence in `residues-closed.md` |
| R119 | open | M19's progress-line parser assumes `pyproject.toml` carries no `addopts` — fails loudly, never falsely, but undeclared |
| R120 | open | The 44/18 blast-radius figures cited in `test_arc_ablation.py`'s docstring are not reproducible from repo state — the pair census never shipped. **A second unreproducible number found in the same docstring, 2026-08-23 (M7): `9 endpoint criteria` was the 7-edge figure; corrected to 8** |
| R121 | closed | CLOSED 2026-08-23 (Task 1, `7e4f84c`) — `_run_module` prepends `<worktree>/src` to `PYTHONPATH`, outranking the editable-install `.pth`; no library file touched. Full evidence in `residues-closed.md` |
| R122 | open | The question `the-worktree-that-resolves` declines to ask: after §4.1 re-roots `src/`, is any oracle still resolving evidence to the main tree? Two styles measured and closed; a third is not ruled out and nothing would notice one |
| R123 | open | A declared `prog:oracleArtifact` that is a Python MODULE is real consumption §4.5 refuses to score (it raises) — and Task 4's "zero are `.py`" census is REFUTED: **2 of the 29 are**, `tests/etkl/fixtures.py` (`tab:06`) and `tests/etkl/test_vacuity_registry.py` (`tab:10`) |
| R124 | open | Spec §4.4's stated mechanism (a pre-empted deletion) is superseded by the shipped code's ordering — `_materialise` runs BEFORE `_ablate`'s unlink loop, so no false green from pre-emption is possible; the real hazard is a gitignored artifact smuggled past the committed-tree check |
| R125 | open | Pre-existing GC2 exposure: no `sh:pattern` constrains a `prog:oracleArtifact` path, so a declared `../../x` or absolute path would let `_ablate`'s `unlink()` mutate outside the worktree; `_scores`' bare substring containment is also unanchored on separators |
| R126 | closed | CLOSED 2026-08-25 by `holon:05` (`the-membrane-reports-its-health`, Tasks 1+3), on the row's OWN vehicle: `compile_document(simple_table_pdf)` now emits **331** triples of which **2** have `_DOC` as subject (`a etkl:CompiledDocumentHolon`, `etkl:membraneHealth etkl:Intact`), and **2 of 13** `rdf:type` values are `etkl:`. `etkl:CompiledDocumentHolon ⊑ etkl:DocumentHolon`, so the property's `rdfs:domain` is instantiated. **Page scope is unchanged (0 of 326) and that is deliberate** — see the row. Full evidence in `residues-closed.md` |
| R127 | open | `dec:rationale` has no cardinality cap while `dec:EventShape` caps `dec:condition` at 1, so a second (e.g. language-tagged) rationale — which CLAUDE.md explicitly permits — makes every document containing that escalation refuse at document scope. **Left open deliberately: it is the only measured lever into a document-scope refusal and FOUR shipped tests ride it. Closing it requires re-homing them in the same act** |
| R128 | closed | **CLOSED 2026-08-30** by `the-membrane-returns-a-verdict`: `dec:SupersessionShape` + `dec:SupersededOnceShape` in `dec-shapes.ttl`, a conforming `examples/supersession.ttl` and four negatives. **The cardinality is on the IN-degree, and a corpus measurement decided that** — max OUT-degree is **5** (apple's datagrid admission supersedes five verdicts), so the `sh:maxCount 1` the row invited would have refused a correct document; max IN-degree is 1, which is the precondition `why-escalated.rq` and `effective-chain.rq` both rest on and neither enforced. `sh:nodeKind` was written, measured vacuous at the membrane, and removed — see `R152`. Full evidence in `residues-closed.md` |
| R129 | closed | **CLOSED 2026-08-30** by `the-membrane-returns-a-verdict`: `membrane.suggester_agent` refuses a non-IRI suggester as an `AssertionError` carrying the offending value, called from all **5** mint sites. The check is rdflib's own `URIRef.n3()`, so it is exactly as strict as the serializer that used to crash. The row's own gap — *the end-to-end route was read from the call chain, not driven* — is driven now, through `ground_concept`. Full evidence in `residues-closed.md` |
| R130 | open | `holon:05` §4.9's `(query, term)` registry ships its REVERSE arm only — the FORWARD arm ("every idle query is registered") has no population enumerator, because over the 29 `.rq` files mentioned in `src/**.py` the criterion yields **164** unreachable pairs of which **162 are a category error** (the query runs over a transient `urn:iladub:evidence:` graph, never the compiled one). Numbered R130, not the ruled R128 — see the row |
| R131 | open (half (a) done) | A PAGE-scope refusal preempts the document-scope one, so `Compromised` reports document-scope refusals ONLY. **PARTIAL 2026-08-30: (a) the page site now raises `MembraneRefusal`, so one `except` clause sees both scopes — and the seam was MEASURED first: 14 page-scope `_validate` calls across all 7 tracked documents, 0 refusing, so no real input reaches that raise and the oracle must INJECT. (b) minting page-scope health is unbuilt and stays `holon:06`'s** |
| R132 | open | Every compiled document shares ONE document IRI — `_DOC` is a module constant (`compile.py:22`) and `compile_document` takes no `doc_uri`, so the health subject is the same node for every document and carries no link to the `…/doc/p{n}` URIs holding all the content. **6 non-doc files hardcode the literal, not the spec's 5** |
| R133 | closed | **CLOSED 2026-08-30** by `the-membrane-returns-a-verdict`: `_validate(graph, legs=())` REFUSES instead of raising `IndexError`, because a validation that checked nothing and returned `True` fails upward (CLAUDE.md §7). The deferral rationale is re-measured, not carried: `_legs_for_document` is total and never returns `()`. Full evidence in `residues-closed.md` |
| R134 | open | The grounding portal has no health signal: `src/iladub/feed.py:642-643` guards a different graph behind a different boundary with a bare `assert` that `python -O` erases, and `etkl:GroundingPortal` is instantiated NOWHERE in `*.py`/`*.rq`. `holon:06` territory |
| R135 | closed | **CLOSED 2026-08-28** by the declaration instrument (`tests/query_terms.py` + `vocab/shapes/query-declaration-shapes.ttl`): O1 was RED on a REAL leak — `risk:order`, named by `escalation-furnish.rq` and declared by no ontology — declaring it turned the corpus green, and `holon:05 → holon:01` was re-authored (`6268437`) and now SURVIVES its two-sided ablation. **`R117` is NOT closed by this**: it is about subclass-axiom subjects in a `.ttl` and this instrument reads `.rq` only — see `R142`, `R143` | Nothing checks that an `etkl:` term a RUNTIME artifact names is DECLARED anywhere — `membrane-health.rq` BINDs `etkl:Intact`/`Weakened`/`Compromised` as bare IRIs, so M19 arm 1 refuted `holon:05 → holon:01` on 2026-08-25 (deleting `etkl-holons.ttl` leaves the oracle green). Same CLASS as R117, different artifact: R117 is about `iladub-hga-align.ttl`'s subclass axioms, this is about a `.rq` |
| R136 | open | A criterion can be `prog:met true` while its own `prog:source` points into *"Planned work (not done yet)"*, and NOTHING refuses it. M10 checks only that the `<path>:<line>` RESOLVES, never what the line says — measured by reverting this loop's own doc move and finding `tests/test_arc_manifest.py` + `tests/test_doc_governance.py` green at **31 passed** (two modules, NOT the full suite; see the row) |
| R137 | closed | **CLOSED 2026-08-31** — `tests/test_residue_register_integrity.py` pins the three-file invariant (index↔detail, one home each, struck iff closed). Both falsifications that stayed green on 2026-08-25 now fail |
| R138 | closed | **CLOSED 2026-08-31** — §4.5's five citations are now SYMBOL references to `_seal`; plan-rule 7 was committed and caught inside the same edit. Other sections of the file still drift, out of this row's scope |
| R139 | closed | A same-file citation pointing DOWNWARD is falsified by the very edit correcting it — the `holon:05` fix wave's first attempt shifted its own cited line numbers before the reflow was made line-neutral; "measure before writing" does not guard this class. **PARTIAL 2026-08-25: the convention half is now CLAUDE.md plan-rule 7; the row stays OPEN on its instrument half — nothing machine-checks it**. **SECOND measured instance 2026-08-31**, in `.md` this time, committed while applying the rule's own remedy — the instrument half now has two. **CENSUS 2026-08-31: the prescribed lint is REFUTED — recall 0/4 (every real instance is a bare `:NNN`), precision 0.7% tree-wide — but a narrow `.py`-comments form scores 4/4 recall at 20% FP. A THIRD live instance found and fixed: `compile.py` cited `:1124` for a call at `:1200`, rotted twice. What remains is a DESIGN decision, not a measurement** **CLOSED 2026-08-31: the instrument is BUILT** — `tests/test_source_citations.py`, a PROCEDURAL extractor feeding a closed-world SHACL membrane; it reproduced the census (7 tokens, 4 sites) and all four were repaired line-neutrally with no allowlist. The census's own regex was defective, so two of its findings are corrected in the row. `docs/**` stays out — see [[R153]] |
| R140 | closed | CLOSED 2026-08-27 by plimslop `5064705` (PR #2) on the row's own second branch — `PLIMSLOP_MODE_ORIGINATING=warn` **documented** as a deliberate standing setting in plimslop's README, dated, costed, with a named release trigger. Not "restore `block`", because the measurement forbade it: **150 of 153 preflight records were written AFTER their session's stop warning, 3 before**, so the Stop hook produces the override data and flipping the mode mid-observation would confound R141 §5's prediction with an instrument change. `reader override` now prints the hold and the live count every run and says `HOLD RELEASED` at `n>=20`. Falsification caught its own weak test (inversion 2 passed; the FIXTURE was fixed, not the assertion). **Uncosted and still true: `block` has never enforced once** |
| R141 | open (code landed) | The ruled unit is now **enforced** — plimslop `fb6b64e` gates `stop.py`/`preflight`/`report.py` on `working = tokens + dropped − baseline`, deletes the unsatisfiable-gate guard, and ships a `reader override` view whose definition reproduces the audit's 39/72 and 35/67 exactly. **Stays open on its last clause only**: §5's prediction needs *observed* records under the new gate and there are **n=0** today. Counterfactual re-score: 40% (17/43) against 51% (38/74) — a re-score of old decisions, NOT the prediction coming true |
| R142 | closed | **CLOSED 2026-08-29** by `vocab/internal/{prog,docgov,corpus}.ttl` — THREE namespaces, not two, and declared INTERNALLY: the row's own stated closure (`vocab/ontology/prog.ttl`) is refused because it contradicts three recorded statements. Exemption deleted. Two owned namespaces have NO ontology file at all — `prog:` (9 terms) and `docgov:` (12 terms) — so the declaration instrument must EXCLUDE them by construction, and the arc's own measuring apparatus is itself undeclared. **Both figures CORRECTED 2026-08-29: the vocabularies are 21 and 23; 9/12 is only what the `.rq`-only instrument sees, and the row's stated oracle passes green without closing it** |
| R143 | closed | **CLOSED 2026-08-29**: population is every tracked `.ttl` (139), the three-way split settled POSITIONALLY (used-as-vocabulary) before any membrane read a `.ttl`, headline **209 → 203** (the 6 are `sh:namespace` literals — the row's own warning, see `R149`), and the instrument was NOT green on its first run. The declaration instrument's population is `.rq` ONLY — `vocab/shapes/*.ttl`, `examples/**` and `tests/*.ttl` name owned terms too, and are both unchecked and UNCENSUSED. This is the row that would subsume `R117`. **CENSUSED 2026-08-29: 209 undeclared across the four families, majority category error — the arc mints instance IRIs inside its own vocabulary namespace** |
| R144 | closed | **CORRECTED IN PLACE, THEN CLOSED 2026-08-29 — this row's central measurement is FALSE and had been since `tab-fno-align.ttl` was written.** `R117`'s hypothetical was realized: six dangling `tab:aggFn*`. `R135`'s M5 looked with an `.rq`-shaped instrument in the one family it cannot read. `R117` remains OPEN with NO LIVE INSTANCE — the oracle gap is real, the leak is absent. Recorded explicitly so that a reviewer who finds its hypothetical unrealized does not read the row as stale |
| R145 | open | A criterion's oracle can be a WHOLE-TREE INTEGRITY test, and that broadens what the ablation reads as a dependency — MEASURED at 6 of the 7 non-align ontologies, not 1. Correct for the edge this loop authored; a hazard in M19's one forbidden direction for any future edge out of `holon:05` |
| R146 | open | Enumerated individuals are unreachable by ANY positional demand — 46 already-declared owned IRIs are node-role-only, and `corpus:`'s three verdicts entered by AUTHORSHIP, never by the membrane. Deliberately not patched: inferring from absence is what CLAUDE.md §8 forbids |
| R147 | open | `tab:product`: a dangling alignment OBJECT, reached by neither D1 nor D2. Widening D2 to objects was considered and REFUSED — an align module's objects are the foreign terms by construction |
| R148 | open | The `.rq` half demands every owned IRI a query names REGARDLESS OF ROLE — the asymmetry the `.ttl` half exists to avoid. Harmless today (measured), a defect the moment an authored query names an instance IRI |
| R149 | open | A register row's stated caveat does not bind the row's own numbers — `R143` warned about exactly the contamination its own headline carried. Raised as an observation; no lint proposed until someone measures how often it would fire |
| R150 | open | An owned term named ONLY inside an `sh:sparql` query STRING is invisible to every positional rule. One live instance: `docgov:inWikiIndex`, used by a shape and emitted by the extractor, undeclared until this loop declared it as surplus **SECOND LIVE INSTANCE 2026-08-31**: 7 of `srccite:`'s 8 terms are named only inside `source-citation-shapes.ttl`'s `sh:select` string; the census moved by ONE, not eight |
| R151 | open | `holon:02 → holon:01` is still unauthored — and the remedy this row stated is **REFUTED, corrected in place 2026-08-29**: the prediction was run first, the oracle stayed GREEN under ablation, and the edge must not be authored until the membrane is made ablation-legible |
| R152 | closed | **CLOSED 2026-08-31** — a guard over every shape file reaching `membrane._payload_nt` (compile ∪ grounding, tiling proven covered) machine-checks the skolemization premise. Does NOT make `sh:nodeKind` work |
| R153 | open | The downward-citation instrument cannot see MARKDOWN, and one of R139's three measured instances was in `.md` — committed while applying the very rule it broke. The census measured 71-99% FP over `docs/**` because a citation there is a NARRATIVE whose referent crosses heading boundaries; no bounded lexical window resolves it, so this is a real gap and not a deferred chore |
| R154 | closed | `rule_aware_lines` buckets per CHARACTER by centre, so a ruled boundary falling inside a word run shreds it — WHO's `Z-scores (weight in kg)` becomes 7 fragments. **CLOSED 2026-08-31: the row's two-population framing is REFUTED — every crossing is the same artefact, a text run chopped, so no discriminator was needed.** `_row_dividers` declines a boundary that cuts ink, ROW-LOCALLY (`xs` untouched, so unlike the failed word-atomicity variant `header_body_split` does not collapse). WHO's header 7 fragments → 2, its real header row byte-identical, no document regresses. The score movements are a denominator effect and license nothing |
| R155 | open | The residual division on WHO's header line is a WORD GAP, not a mid-word cut, so `_row_dividers` cannot reach it: at character level a word gap and a column gutter are the same picture. `'Z-scores (weight in'` + `'kg)'` still cross the membrane as two top-level header nodes. This is R154's own *"a header line needs BOTH readings at once"*, narrowed to the one case that survives the flush predicate **ENRICHED 2026-09-01: FOUR discriminators measured, ALL REFUTED, code built and REVERTED.** Population is **4790**, not the row's "exactly one". Kerning (0.042pt) and word spacing (2.758pt) differ only in MAGNITUDE, so the GEOMETRIC half is now measured-impossible without a tuned constant. `mcid` is exact on WHO/cbh and **refuted by bfs**, which tags nine labels as one item (page 6: `324 → 53` cells) — its score ROSE 0.35→0.94 while refusals rose, a collapse wearing an improvement's clothes. **RECLASSIFIED NEURAL**, with a five-sided oracle whose O3/O4 legs are new |
| R156 | open | Closing [[R154]] moved cbh page-0 band 9 `UNSUPPORTED_TABLE`→`RECORD_TABLE` on a band welding TWO side-by-side tables. **NARROWED BY MEASUREMENT: the emitted structure is IDENTICAL either side (13 EntryCell / 16 hasCell / 9 hasLeafRow in both) — the conflation is PRE-EXISTING, and the whole delta is ONE type triple plus four cellText fidelity repairs.** Open question is the type triple alone. Half (b): page-0 score drops 0.0698→0.0571 and four ESCALATED regions change reason, invisible at document scope |
| R157 | open | A census scoped to ONE PAGE cannot validate a rule that runs on EVERY page. [[R155]]'s C3 design named its own failure mode, measured it at **0 in 3613** and **five of seven byte-identical** — all page 0 — and the risk was live on **page 6**: bfs `324 → 53` cells. Naming a risk then measuring it out of scope is worse than not measuring it. Same shape as [[R149]], one layer down |
| R158 | closed | **Corpus REACH is unmeasured as a corpus property, and has been filed one instance at a time for a month.** [[R68]] (no document exercises the transposed path), [[R97]] (four `tab:` shapes, 0 focus nodes), [[R99]] (unreachable body term), [[R45]]'s five vacuous PASS rows and PR #109's inert 27-page zero-delta are **five framings of one fact**: the 7-document corpus does not enter the code under test. Distinct from the progress census's candidate B — a document can carry a score floor and still never reach the changed function; reach and target are independent. Raised by the census that REFUTED candidate A (8 of 9 loops carried power evidence, 89%) | **CLOSED 2026-09-01 — the prediction was RUN and is REFUTED: 6 of 16 changed functions are reached by <=3 of 7 documents (37.5%), not 'most'; 10 of 16 are reached by ALL SEVEN.** The framing does not survive as a corpus property. The instrument this row asked for is built and committed: `scripts/reach_probe.py`, reporting reach beside the score. Its own first version was WRONG in the understating direction (one shared process attributed every `lru_cache`d function to whichever document ran first) — pinned by `tests/test_reach_probe.py`. The successor question is [[R159]]
| R159 | open | Reach is **bimodal** — 10 of 16 changed functions at 7/7, 3 at 0/7, only 3 in between — and the reading offered for it ("a spine every document walks, limbs the corpus never touches") is a story fitted by the session that measured it. Corpus-wide the same shape appears (122 at 7/7 against 8 at 4/7) but the claim and its check came from ONE run. Also unanswered by [[R158]]'s own closure text: whether a 0/7 row is a corpus gap to fill with documents or an honest statement that a change was narrow — [[R146]] forbids inferring from absence, so nothing here licenses "grow the corpus" | Measured 2026-09-01, `docs/superpowers/2026-09-01-corpus-reach-measured.md`; instrument `scripts/reach_probe.py` | Deferred because the falsifying run is the same run that produced the claim, and a second population (unit-test reach, or the CLI) is a separate instrument | An independent population measured with the committed instrument, and a stated rule for what a 0/7 row obliges a loop to do |
