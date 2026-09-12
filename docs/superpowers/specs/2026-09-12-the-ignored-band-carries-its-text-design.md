# Spec — the ignored band carries its text: R212's carrier

**Serves:** prog:criterion:etkl:02 — `ag-trade/graincorp-capacity-2026-08-04.pdf`
(`tests/arc-manifest.ttl:210`). R212 is a **prerequisite** of that criterion's measures, ruled
2026-09-12; it is not a criterion of its own.
**Date:** 2026-09-12. **Branch:** `r212-carry-the-ignored-bands-text`, cut from `ec1dc4e`.

**Doc impact: none.** This loop ships a spec and no code. Nothing queues for a release tag and
nothing blocks one.

Part 5 of the accompanying handoff is written first; this spec is written in the session's first
third, under the originating floor.

## 0. The ruling this spec rests on

Asked at review on 2026-09-12, with `specs/2026-09-11-the-span-the-author-drew-design.md` in front
of them, the maintainer **refuted** that spec's reading and ruled:

> The **machine**, not the contract author, derives graincorp's capacity measure name from the
> page's title and footer.

Recorded in that spec's § 0/§ 3.3/§ 5/§ 6 and in [[R212]]'s row (PR #209, `f1df625`). The
consequence is this spec's whole reason to exist: **a licence the machine must consume needs a
carrier in the graph**, and today there is none.

**Two further rulings, 2026-09-12, on this spec's § 6 open items.** Asked at review with the census
in front of them, the maintainer ruled:

> 1. **All.** Every ignored band is carried — not a selected subset.
> 2. **`etkl:`.** The carried term lives in the `etkl` namespace.

Both were § 6 questions when this spec was drafted; they are answers now, and § 3 and § 6 are
corrected below. Ruling 1 confirms the drafted design rather than changing it, so nothing downstream
of it moves. Ruling 2 settles a choice the spec had deliberately left open, and it is the right
home: `etkl` is the doc-holon fabric (Raw/Clean/GroundingPortal/MembraneHealth), and a band the
reader ignored is document fabric, not table vocabulary. **Recorded here and in the handoff's § 2.**

## 1. What is already measured

Pointers, not restatements. Each was run by an earlier session.

| fact | where |
| --- | --- |
| graincorp's title/print-line/issuer/footer are absent from the compiled graph — 0 hits in 5710 triples | [[R212]]'s row; spec `2026-09-11-the-span-the-author-drew-design.md` § 2.1 |
| the proposer is called with `surface_text = ""` and never sees the page | that spec § 2.2 |
| graincorp's **real header** (`Year \| Elevation Period \| Mackay … Portland`) sits in its own one-line band, ignored as *fewer than 2 lines* | `tests/arc-manifest.ttl:204-205` |
| the corpus battery's proposer abstains, so no leaf grounds under it | that spec § 2.3 |

## 2. Measured this session, on `ec1dc4e`

**2.1 — The loss is 35% of the corpus's band ink, not a graincorp quirk.** Census over
`corpus/*/*.pdf`, replicating `compile_tables`' exact band ordering (the multi-table escalation is
tested *before* `classify`, so a multi-table band never reaches the NON_TABLE branch and is not
counted as ignored). Instrument: `scratchpad/ignored_band_census.py`, this session.

```
bands                    191
ignored                  146        <- 76% of all bands
ignored_with_text        146        <- every one of them carries words
ignored_ink             2935 words
ink_all                 8413 words  <- 34.9% of band ink reaches no triple
reason: fewer than 2 columns   77
reason: fewer than 2 lines     69
```

Per document, ignored bands / their ink:

```
gov-stats/ons-index-of-services-2026-02.pdf   70 bands  1356 words
gov-stats/bfs-population-bilan-2023.pdf       46 bands  1403 words
health/who-wfa-boys-zscore-0-5.pdf             8 bands     9 words
ag-trade/graincorp-stem-2026-07-31.pdf         7 bands    73 words
financial/apple-fy2026q3-statements.pdf        6 bands    54 words
ag-trade/cbh-stem-2026-08-03.pdf               5 bands     9 words
ag-trade/graincorp-capacity-2026-08-04.pdf     4 bands    31 words
```

**2.2 — graincorp-capacity's four ignored bands are exactly the licence, plus the header.**
Verbatim from the same run:

```
p0 b0  lines=1 ink= 5 [fewer than 2 lines]   'GrainCorp Operations Ltd ABN 52003875401'
p0 b1  lines=2 ink= 2 [fewer than 2 columns] 'ELEVATION CAPACITY TABLE | As At Tuesday, 4 August 2026'
p0 b2  lines=1 ink= 9 [fewer than 2 lines]   'Year Elevation Period Mackay Gladstone Fisherman Islands Carrington Port Kembla Geelong Portland'
p0 b4  lines=1 ink=15 [fewer than 2 lines]   'GrainCorp advise that the tonnages shown are indicative only and are subject to change. 1'
```

b1 and b4 are the licence the maintainer ruled on. **b2 is the page's real header** — so R212's
carrier and [[R166]] are measurably the same four bands, and § 4 states where the line between them
falls.

**2.3 — The ignored branch emits one thing, and only on borderless bands.**
`compile.py:814-824`: when `band.unit_markers` is non-empty it mints `{doc}#region{idx}` purely as a
hanger and calls `_emit_unit_markers(graph, cand_uri, band, None)`; then a `RegionReport`, then
`continue`. No `iladub:CandidateConcept`, no `SourceRegion`, and `ascii_view` goes to the in-memory
report only. `absorb_unit_markers` returns the band unchanged when `band.rules` is non-empty
(`unitmarker.py:90-91`), so a *ruled* ignored band emits **zero triples**.

**2.4 — Emission and score accounting are decoupled, and the NON_TABLE branch increments neither
counter.** The score is `asserted / (asserted + escalated)` (`document.py:1760`;
per-page `:1555`). `escalate_region` *emits* a proposition, while `escalated_total` is incremented
separately by its caller (`compile.py:802-803`). The NON_TABLE branch increments nothing. **So a
carrier that touches neither counter leaves every corpus score byte-identical** — and that is what
makes this loop safe to ship against a rung whose criteria are pinned scores.

**2.5 — The existing furniture carrier cannot reach an ignored band.** `tab:RegionCaption`
(`tab.ttl:409-417`) has two emitters — `compile._emit_band_captions` (`compile.py:200-221`) and
`rowrole.emit_reading_evidence` (`rowrole.py:254-259`). Emitter A reads `band.captions`, populated
only by `peel_leading_captions` (`gridregion.py:137-168`), which abstains unless the band has **≥3
distinct rule x-positions**; emitter B runs only inside a header-region role reading. **Both require
a table region, so neither can ever fire on a NON_TABLE band.** A caption node also carries exactly
four triples — `rdf:type`, `tab:captionText`, `tab:captionRow`, inbound `tab:hasCaption` — with **no
page, no bbox, no `prov:wasDerivedFrom`**, and **no SHACL NodeShape targets it** (the shape
inventory is `vocab/shapes/tab-shapes.ttl:14,38,60,78,90,108,127,156,170,189,202,209,239,248,286,307,323,335,366,385,403,410`). → [[R218]].

**2.6 — The vocabulary for a non-table text block already exists, and was deliberately kept out of
the graph.** `tab:PriorPageTextBlock` / `tab:ContinuationPageTextBlock` / `tab:BelowTableBlock` /
`tab:AboveTableBlock`, with `tab:blockText` — *"the block's exact surface text, its lines in reading
order"* — and `tab:pageOrdinal` (`tab.ttl:567-586`). The family's own header says **"Transient:
never asserted into a holon"**, and every node is scoped to `tab:ContinuationPairUnderTest`, the one
page pair whose licence is being decided.

**2.7 — Whole-band surface text has one exact existing function.** `document._band_text`
(`document.py:540-548`): words left-to-right, lines top-to-bottom, newline-joined, *"raw extraction,
and the whole of it — no normalisation, no case folding, no stripping"*, whose docstring already
argues the §7 stance this spec needs. It is module-private.

**2.8 — What a corpus-wide proposition would move.** `tests/etkl/test_vacuity_registry.py:441-447`
records that `iladub:CandidateConcept` is present on **3 of the 7** compiled graphs (apple, bfs,
who-wfa). Since every one of the 7 documents has ignored bands (§ 2.1), minting candidates for them
would make that 7 of 7 and falsify the registered asymmetry. Measured by grep this session: no test
pins "an ignored band emits zero triples".

## 3. The reading

**The carried node is a committed fact in an owned namespace, with page provenance, that is neither
asserted nor escalated.**

- **Why not a proposition (`iladub:CandidateConcept`).** A title is not a concept awaiting promotion
  into the grounded graph; it is context the document carries (§5). Minting one would require a
  suggester and a confidence that no one measured — fabrication under §7 — and would falsify § 2.8's
  registered 3-of-7. **Refused.**
- **Why not `tab:RegionCaption`.** It cannot reach the band at all (§ 2.5), and adopting it would
  inherit a node with no provenance-to-the-page, which §6 requires. **Refused.**
- **Why not the transient block family.** Reusing `tab:PriorPageTextBlock` would promote a term
  whose declared contract is *never asserted into a holon*, and whose every instance is scoped to a
  page pair under test. Redefining a published term's status is a worse defect than minting a new
  one. **Refused** — but its `tab:blockText` shape is the right *model*, and the new term should
  read like it.
- **What is carried:** for every band whose verdict is `ignored`, one node per band carrying the
  band's exact surface text (§ 2.7's function is the definition), its page, its band index, and
  `prov:wasDerivedFrom` the document. Provenance reuses the `iladub:SourceRegion` + `iladub:onPage`
  family (`iladub.ttl:104-116`), **not** `tab:onPage`, whose `rdfs:domain tab:Cell` would retype the
  node as a cell — the R69 mechanism that term was narrowed to prevent.
- **No selection judgment — RULED "all", § 0.** *Every* ignored band is carried, with no rule
  deciding which bands are "furniture". A band's text is carried because the reader ignored it, not
  because anything read it. This is no longer the spec author's choice to revisit.
- **The namespace is `etkl:` — RULED, § 0.** The local name is the plan's to fix; the namespace is
  not.

**§8 gate — PROCEDURAL, and irreducible.** This is raw extraction: source → typed RDF facts. Every
value written is passed in or derived mechanically (the text by concatenation, the page off
`Word.page`, the index off the loop). It makes no decision: there is no threshold, no tolerance, and
no span/read/group/role question, because the band's verdict was already decided upstream by the
existing AXIOM. Had the carrier chosen *which* ignored bands deserve carriage, that choice would be
NEURAL and would need an oracle — which is precisely why it does not choose.

**The membrane.** The new term ships with a SHACL NodeShape making text and page **required** — the
failure § 2.5 records for `tab:RegionCaption` is a typed-but-empty stub, and the shape is what
forbids it — plus a conforming worked example and a negative example that must fail.

**The invariant, stated once:** *carriage changes what is in the graph and changes no number that
grades a document.* Its oracle is § 5.

## 4. What this loop does NOT do

- **It does not make any ignored band a header.** graincorp b2 (§ 2.2) is carried as text and stays
  ignored. Reading it as the page's header is [[R166]]/[[R211]] Layer A, and carriage neither helps
  nor hinders that.
- **It does not hand the text to the proposer.** That is the second half of the spec § 5 step 2
  prerequisite and needs a signature change to `ProposeGrounding(surface_text, value, field_labels)`
  (`baml_src/ground_propose.baml:8`) plus a call-site change in `BamlGroundingProposer`
  (`propose_ground.py:48-61`). It cannot be built before the text is in the graph to be read out of.
  **Next loop.**
- It does not author the capacity contract, close [[R212]]'s downstream measures, or adjudicate
  etkl:02.
- It does not change the corpus battery's abstaining proposer.
- It does not repair `tab:RegionCaption` ([[R218]]).

## 5. The oracle

A plan is a fresh session's work; this spec states what must falsify it, not how.

1. **The carriage arm, in CI.** A synthetic `Band` that classifies NON_TABLE, compiled through the
   public API, puts its exact text and its page in the graph. Synthetic because `corpus/` is
   gitignored (`.gitignore:52`) and no PDF is committed — tests build `Band(...)` directly, as
   ~10 files under `tests/etkl/` already do.
2. **The falsification arm.** Remove the emitter; show the test fail; restore; show it green
   (plan rule 4).
3. **The membrane arm.** A carried node missing its text or its page must be refused by the new
   shape — the negative example that must fail.
4. **The invariant arm — the one that can actually sink this.** Every corpus document's score is
   **byte-identical** before and after, and so is its asserted/escalated token ledger.
   `scripts/corpus_verdict_snapshot.py:47-89` already dumps per-region verdicts plus a canonical
   graph SHA-256; the graph hash *must* move (that is the point) while the scores must not. Run it
   both sides.
5. **The corpus arm, which does NOT run in CI.** That graincorp's title and footer are in the graph
   is corpus-gated (`pytest.mark.corpus`, `tests/test_corpus.py:20`) and skips where the PDFs are
   absent. **A green CI is not evidence for this arm** — it must be run locally and its output
   pasted into the evidence, or it is unmeasured.

**The seam the plan must measure before writing the call** (rule 3): `document.licence_evidence`
already enumerates non-table text blocks per page to build § 2.6's transient family. **Measure
whether it enumerates the same bands this carrier would, and whether it is reachable off a
recognized page pair** — it may be the producer, or it may be scoped to pairs and therefore useless
here. Do not assume either; the answer changes where the emitter goes.

## 6. Unverified or assumed

- **The 146/2935 census counts bands, not distinct text.** A running head repeated on 27 pages is
  counted 27 times, and `ons` (70 bands) and `bfs` (46) dominate the total. How much *distinct*
  furniture text the corpus loses is **not measured**. → [[R219]]. The graincorp figures (§ 2.2) are
  a single page and are exact.
- **The census re-derives bands via `page_bands` + `classify` rather than capturing the list
  `compile_tables` actually used.** `scripts/unbooked_ink_census.py:61-80` monkeypatch-captures the
  real list and asserts band/report alignment; this instrument does not. The ordering was replicated
  by reading (§ 2.1), not proven equal. A plan that pins a count should fork that script instead.
- ~~**Whether carriage is wanted for all 146 bands or only some documents is a maintainer
  question** this spec answers by carrying all of them (§ 3). It is reversible.~~ **ANSWERED
  2026-09-12: all** (§ 0). The drafted reading was confirmed, not refuted, so nothing downstream of
  it moves — but it is a ruling now, not the spec author's choice.
- **"No test pins zero-emission on the ignored path"** is one grep over `tests/`, not an enumeration.
- ~~The term's namespace (`tab:` vs `etkl:`) is not fixed here.~~ **ANSWERED 2026-09-12: `etkl:`**
  (§ 0). The term's local name remains the plan's to fix.

## 7. Residues raised

- **[[R218]]:** `tab:RegionCaption` carries no page, no bbox and no `prov:wasDerivedFrom`, and no
  SHACL shape targets it — the weakest-provenance carried node in the repo, against §6 (§ 2.5).
- **[[R219]]:** the ignored-band census counts bands, not distinct text; repeated running heads are
  counted once per page, so the "how much is lost" figure is an upper bound (§ 6).
