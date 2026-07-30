# Ground the GrainCorp records (Loop K — the capstone)

- **Date:** 2026-07-30
- **Author:** François Rosselet
- **Status:** **Shipped** (2026-07-30, branch `iladub-graincorp-grounding`). Eleventh loop
  of the GrainCorp real-document push (A = PR #67 … J = PR #76). **Measured at close
  (capstone, local):** 33 records → **460 concepts, 137 grounded** (each behind exactly one
  `PromotionDecision` — 137 == 137), **323 honestly quarantined**. By field:
  **Month 32/32** — every injected suppressed key grounds through the pattern (the loop's
  point, end-to-end); Port 29/32; Status 29/30 (the boxed `'Accepted Accepted'`
  quarantines); Total 27/28; **Commodity 20/30 — the stem ships non-grain cargo
  (`Woodchip` ×6, `Cement` ×3) and the grain scheme correctly refuses it**, plus the boxed
  `'Sorghum Sorghum'`. The season keys inject as `GC Fin Year` (the column's real header)
  ×33 and quarantine — the contract declares no such field. Unconstrained fields (vessels,
  exporters, dates, times, references) quarantine by design. Score/cells unchanged
  0.9496/509. Full suite 698 passed / 5 skipped.
- **Origin:** Loop I's named non-goal ("grounding the group key as a SurfaceConcept per
  record") + the fact that the real document has never been run through `ground_document`.
  This is the first loop that connects the table-recovery push back to iladub's
  differentiator — the assert/propose/promote epistemics and the contract-as-ontology —
  rather than deepening recovery itself.

---

## 1. Purpose and scope

Two halves, one vertical slice ending at the grounding portal:

1. **Feed enrichment** — records gain their recovered group keys as groundable
   `SurfaceConcept`s (with provenance to the source cell), and blank placeholder cells stop
   minting noise propositions.
2. **A shipping-stem contract** — small, illustrative, committed under `examples/shipping/`
   (the third-party PDF never is) — so the real document grounds end-to-end:
   contract-verified values become `GroundedNode`s behind `PromotionDecision`s; everything
   the contract cannot verify quarantines honestly as `iladub:CandidateConcept`s.

**Measured baseline (2026-07-30).** A GrainCorp record (row 10) carries 15 concepts with
real messy values: `Port: 'Mackay'`, `Name Of Ship: 'TBA'`, `Date ETA of Ship: 'Blank'`
(the author literally prints the word), `Date of Grain Loading Commencement: '(blank)'`
(the author's literal placeholder, recognized since loop A), `Total: '25,000'`, `Status: 'Accepted'`, `Commodity: 'Sorghum'` —
and **no Month or Season concept at all** (suppressed by the author on 30 of 33 data rows;
recovered as structure by loops H/I but never reaching the portal as content).

**Non-goals:** no change to `ground_concept`/`ground.py` (zero new grounding logic); no
live BAML dependency in committed tests; no score/cells change (feed-side loop — failure
condition as always); vessel/exporter/date fields deliberately carry no verifiable
constraint and quarantine (credibility over completeness, §7).

**Success criteria:**

1. **Injection:** a suppressed-key record gains `Month`/`Season` concepts whose value is
   the group key and whose region is the SOURCE cell the key came from (§6); a column the
   record already populates (Port) is NOT duplicated; nested groups sharing one label cell
   inject once.
2. **Blank hygiene:** cells whose text satisfies `celltype.is_blank` (loop A's convention:
   `''` / `'(blank)'` / `'-'`) are dropped from records — nothing to ground, no noise
   propositions. The literal `'Blank'` string is NOT a marker: it stays, and quarantines.
3. **Contract:** `examples/shipping/stem-contract.ttl` + `stem-terms.ttl` (SKOS: commodity
   scheme, port scheme) + `stem-shapes.ttl` (`sh:in` for Status; `sh:pattern` for Total and
   Month) loads via the shipped `load_contract` and verifies through the shipped
   `ground_concept`: `'Sorghum'`/`'Mackay'` ground (scheme), `'Accepted'` grounds (sh:in),
   `'25,000'` grounds (pattern), `'Aug 26'` grounds (pattern) — and `'TBA'`, `'Blank'`,
   an off-scheme commodity, an unlisted status all quarantine. Patterns/`sh:in` sets are
   **contract-author declarations** (the PR #55 soundness relocation), not tuned constants.
4. **Offline by construction:** the contract's property local names match the normalized
   header texts (`port`, `commodity`, `status`, `total`, `month`), so grounding runs on the
   exact-match path with an abstaining proposer — no live model in any committed test.
5. **Shipped-fixture guard:** the transplant/offer feed tests byte-identical (no blanks, no
   derived groups there — both feed changes inert).
6. **GrainCorp capstone (local, uncommitted):** `ground_document` over the compiled stem +
   contract → measured tallies (grounded / proposed counts; every grounded node behind a
   PromotionDecision; injected Month concepts grounding through the pattern), recorded in
   the spec status and ledger.
7. Full suite green (baseline 677 / 5).

## 2. Components

### 2.1 `feed.py::table_records` — blank-drop + group-key injection

- **Blank-drop:** in the cell loop, skip concepts whose `cellText` satisfies
  `iladub.etkl.celltype.is_blank` (reuse — never a second marker list). A row whose cells
  are all blank mints no record (nothing to say — honest).
- **Injection:** per record row, for each `tab:DerivedRowGroup` of the owning table that
  `coversRow` the row: label cell → its `atColumn` → the column's header path (the existing
  `_column_header_path` map) is the concept **text**; the label cell's `cellText` is the
  **value**; the label cell's provenance fragment is the **region**; its bbox x0/y0 feed the
  existing x-sort so the injected concept lands in natural column order. Injected ONLY when
  the record has no concept at that column (fill the suppressed key, never duplicate) and
  at most once per column (nested same-cell groups inject once).
- Pure RDF reads; no constants; record identity and ordering logic untouched.

### 2.2 `examples/shipping/` — the contract triple

`stem-contract.ttl` (contract + 5 fields, following the transplant contract's exact
vocabulary: `etkl:SemanticDataContract`/`targetClass`/`hasField`/`fillsProperty`/
`admissibleScheme`), `stem-terms.ttl` (SKOS concepts: grains in `ship:scheme-commodity`,
the stem's public ports in `ship:scheme-port`), `stem-shapes.ttl` (a
`ship:ShippingSlotShape` with `sh:in` on status, `sh:pattern` on total
(`^[0-9]{1,3}(,[0-9]{3})*$`) and month (`^[A-Z][a-z]{2} [0-9]{2}$`)). Namespace
`ship: <https://example.org/shipping#>` — illustrative, like `tx:`. Values are drawn from
the public document's vocabulary; the PDF itself is never committed.

### 2.3 Tests + the capstone measurement

Feed units (synthetic graphs); contract units through the real `ground_concept`; an E2E on
the loop H/I fixture (compile → inject → ground against a fixture-matched mini-contract);
the GrainCorp run stays a controller measurement (§1.6).

## 3. Gate & discipline

No new §8 decision: injection is PROCEDURAL raw extraction (RDF reads); verification is the
shipped contract-SHACL membrane (closed world, where it belongs); the NEURAL proposer seam
is untouched and abstains in tests. No language matching in the feed — column identity
drives injection, never text. Blank recognition reuses the one owned `is_blank` convention.

## 4. Residues

- Expected new residue: **fields without verifiable constraints stay propositions**
  (vessels, exporters, dates, times) — by design, not a defect; named with measured counts
  at close.
- The R18 refused groups mean some records still lack a Port-group parent path — their
  Month/Season still inject (month groups confirmed); no new mechanism needed.
