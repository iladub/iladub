# Handoff — GLiNER2: the count was taken, and the thread closes on it

**Topic:** the ASSERTED action 5a of `docs/superpowers/2026-09-10-gliner2-population-count-handoff.md`
— count the cells a model-backed proposer (spec placement A) could ever touch on the manifest corpus,
before running the spec's cost gate T1. The spec itself stays on the unmerged branch
`only-a-refusal-admits-the-model` (`docs/superpowers/specs/2026-09-10-only-a-refusal-admits-the-model-design.md`,
read with `git show`).
**Written 2026-09-10 at ~35K working tokens**, under the originating floor; part 5 is typed anyway,
per CLAUDE.md § "The handoff's next action is TYPED".

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. PROPOSED — [[R207]]: the only admissible cells are section markers, and an AXIOM already binds them

The ceiling on cbh is 49 cells and every one of them is a section marker (`is_section_marker=True`,
injected by `feed._inject_section_captions`) whose text — `KWINANA`, `ALBANY`, `GERALDTON`,
`ESPERANCE` — is a `skos:prefLabel` in the contract's port scheme. `scheme_member`
(`src/iladub/ground.py:81`) admits each of them today; nothing calls it, because `ground_concept`
reaches a marker through `exact_field`, which compares the marker's *text* to the contract's *field
names* and finds no field called `KWINANA`. The disposal is a marker-aware branch: for a
`is_section_marker` concept, try scheme membership over the scheme-bound fields; ground on a unique
hit. No model, no tuned constant, an oracle already in the file.

**Why proposed, not asserted:** whether those 49 cells are *missing* is unmeasured. cbh
exact-grounds 134 cells over 58 records, under 5 fields; if the port already grounds per row from a
port column, the marker binding duplicates it and the row needs `owl:sameAs`-style reconciliation,
not a new grounding. **Measure first:** count records on cbh with no `cbh:port` triple after
`ground_document`. If it is ~58, 5a is a 49-cell gain on the page's actual port assignment; if ~0,
the marker binding is redundant and R207 becomes a note.

### 5b. PROPOSED — [[R208]]'s 22 refusals are two data rows read as one record, keyed by a blank month

`Mackay Mackay`, `Wheat Wheat`, `Wheat Chickpeas`, `Accepted Accepted`, `15,000 15,000` (22 of
graincorp's 48 exact-refusals) look like textual fusion and are not: `pdftotext -layout` lines 21–22 show two
consecutive Mackay rows, the second with a blank month cell. The prediction is that `table_records`'
row segmentation keys on a column the continuation row leaves blank, so the two rows arrive as one
record with every cell doubled. **Why proposed:** the cause is read off `pdftotext`, not off the
record's provenance; a run printing `rec.row_id` and the cell regions for those 19 concepts confirms
or refutes it in one pass of `scripts/placement_population.py` with the region printed.

### 5c. ASSERTED, and the maintainer's — the GLiNER2 spec branch is refuted and needs a disposition

The spec's § 6.6 said it could refute itself. It has, before T1 and without a model loaded: the
model's raw population is in columns the contracts do not declare, its admissible population is
0 + 49, and the 49 need an AXIOM. The branch is unpushed. Whether it is pushed as a refuted record
(Evidence, append-only) or dropped is an owner decision; nothing else in this repo depends on it.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the instrument | `scripts/placement_population.py` | the three branches replayed per cell, and the ceiling test; its docstring says what the ceiling does NOT establish |
| the figures | § 2 of this file, and `docs/superpowers/residues-open.md` rows [[R206]] [[R207]] [[R208]] | the raw / ceiling split per document |
| the action this answers | `docs/superpowers/2026-09-10-gliner2-population-count-handoff.md` § 5a–5b | the prediction that was refuted on its number and confirmed on its consequence |
| the spec | branch `only-a-refusal-admits-the-model`, § 3.1 (contract-gating), § 6.6 (self-refutation) | that A filters to oracle-bearing fields and abstains on an empty set — the count shows the set is non-empty and the *values* are what fail |
| the seam | `src/iladub/ground.py:190-215` (`ground_concept`), `:73` (`exact_field`), `:81` (`scheme_member`), `:107` (`_grounds_to`) | why a proposer can only ever name a contract field |
| the two contracts | `examples/shipping/stem-contract.ttl:15-19`, `examples/shipping/cbh-contract.ttl:19-23` | 5 fields each; 2 scheme-bound each; the rest value-constrained (stem: all 3) or bare (cbh: id, client) |
| the section-marker injection | `src/iladub/feed.py:368` | `SurfaceConcept(text, text, region, is_section_marker=True)` — text and value are the caption |

## 2. What was measured (2026-09-10, HEAD `6842c5f`, `scripts/placement_population.py`)

| | graincorp-stem (p. 1) | cbh-stem (p. 1) |
| --- | --- | --- |
| score / records / cells | 0.9659 / 133 / 1850 | 0.9095 / 58 / 909 |
| contract fields (oracle-bearing) | 5 (5) | 5 (3) |
| exact-grounded | 585 | 134 |
| exact-refused | 48 | 1 |
| **RAW — novel, the proposer would be asked** | **1217** | **774** |
| novel: distinct labels / values / (label, value) | 12 / 282 / 325 | 31 / 295 / 378 |
| **CEILING — novel values some oracle admits** | **0** | **49** |
| ceiling breakdown | — | `KWINANA` 17, `ALBANY` 15, `GERALDTON` 11, `ESPERANCE` 6 → all `port`, all section markers |

The 12 novel labels on graincorp are `GC Fin Year`, `Unique Slot Reference Number`, `Exporter`,
`Name Of Ship`, three nomination dates/times, `Date ETA of Ship`, `Date ETD of Ship`, two loading
dates — every one a real column of the stem that `stem-contract.ttl` does not declare. cbh's 31
include the analogous vessel/date/time columns plus the port captions and the maintenance notices
carried as section markers.

**What the number says.** The predecessor's 5b predicted *under 100 cells, under 30 strings*. On the
raw count that is refuted by an order of magnitude: 1991 cells, 577 distinct values. On the
consequence it is confirmed and sharpened: a proposer can only name a contract field, an oracle
admits only a value the field's scheme or constraint recognises, and across both contracts the set
of novel values any oracle recognises is **49, in 4 strings, none of which needs a model to bind**.
The population is bounded by *contract coverage*, not by proposer quality — the cheapest possible
proposer and the best possible one have the same ceiling on these two documents. GLiNER2's T1–T8
are not run; the thread ends here with no dependency ([[R206]]).

**What it does not say.** A contract declaring `Exporter`, `Name Of Ship` or the date columns with
a scheme or a value constraint would create a population overnight; the ceiling is a fact about
these two contracts, not about shipping stems. And the 48 graincorp refusals are a separate,
structural finding ([[R208]]), not a proposer population.

## 3. What was decided, and where that decision is recorded

- **The GLiNER2 thread closes with no dependency, on this corpus.** Recorded in [[R206]] and here.
  Reversible by a contract that declares the undeclared columns with an oracle.
- **The predecessor's read (A conditionally / B restricted to textual fusion / C dropped)** is
  now: A refuted by count; B's only candidate population ([[R208]], 22 cells) is structural on
  inspection, so B has no measured textual-fusion population at all; C untouched. Recorded here.
- The spec branch's disposition is the maintainer's (5c). Recorded nowhere but here.

## 4. Unverified or assumed

- **5a's premise** — that cbh's rows lack a per-row port — is unmeasured (the check is named in 5a).
- **5b's cause** is read off `pdftotext -layout`, not off record provenance.
- **`table_records` is the only path that feeds `ground_document`**, so the raw count equals the
  proposer's population. `feed.py:631-640` reads that way; not traced further, same as the
  predecessor's assumption.
- **The ceiling uses a scratch `BNode` as the offer** for `_value_conforms`; the focused shape
  targets it, so the result is value-only, which is what the ceiling asks. Not separately tested.
- **The instrument's figures were taken twice** — once by a scratch copy, once by the committed
  script after a URI change (spaces in `row_id` replaced, to silence rdflib warnings) — and the two
  runs agree on every figure above. That is a reproducibility check, not a correctness one.
