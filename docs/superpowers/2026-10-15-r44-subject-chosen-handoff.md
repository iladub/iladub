# Handoff: R44 chosen as the next loop's subject; ink census delegated (2026-10-15)

**Serves:** prog:criterion:tab:07 — R44's live surface is mostly `KIND_NOT_SUPPORTED`, and tab:07 is the criterion R44 blocks with the widest corpus reach.

**Doc impact: none.** A handoff; the spec the next session writes carries any increment.

Part 5 drafted first, at about 45K working tokens, under the 50K originating floor; revised after the census. Subject selection and the
census brief took the session's originating budget, so no spec is written here.

## 5. The next concrete action, typed

The census settled the first draft's fork (context around tables, or body prose?) and opened a second.

1. **ASSERTED:** read the appendix. It is the measured population, and its two findings beyond the brief
   change what the loop is.
2. **ASSERTED, and the maintainer's choice between two loops:**
   - **(a) The carried text of every escalation is lossy.** `iladub:surfaceText` on an escalated
     candidate is `render_ascii(band)` (`compile.py:1281` → `holon.py:584`; verified this session),
     and that renderer truncates and overwrites. Whitespace-insensitive, it loses text in **59 of 71**
     live regions. Two accepted adjudications blame "the text layer" for mangling that the renderer
     causes: bfs `corpus-manifest.ttl:454` (verified this session) and ons `:114` (not re-read). This
     breaks provenance to the page (CLAUDE.md §6), and it is **bounded**: the exact text already
     exists as `bands.band_text`, which `etkl:bandText` uses. It is PROCEDURAL, a raw-extraction fact
     with no reading judgement, so the §8 justification is short. It moves every escalated
     candidate's literal, so the corpus baseline's `graph_sha256` moves on every document with an
     escalation, which is expected. The two adjudications have to be corrected by a **new** dated
     adjudication. They are append-only evidence (CLAUDE.md § Documentation governance) and are
     never edited.
   - **(b) The band-role reading (tab:07 proper).** **PROPOSED.** On the 7-document corpus, all 7
     live firings (bfs 5, ons 2) are non-table text around a table: masthead, table title, source
     line, footnotes, captions. That is the census's role reading, a proposition. The held-out set is
     not like that: arxiv's 47 firings are 32 bibliography entries plus prose, equations and chart
     labels, and 3 of fed-h41's `REGION_TILING_FAILED` firings are **table body rows with data
     values**. So a context-carrier fits the corpus and would be **fitted to it** if it were taken to
     be the whole of `KIND_NOT_SUPPORTED`. The root is upstream: `regions.py:87-97` makes any band
     with ≥2 lines and ≥2 inferred columns an `UNSUPPORTED_TABLE` candidate. No class types a band's
     role today (appendix § vocab), and no NEURAL worker reads one. **No oracle, no worker:** the
     spec names the oracle that disposes a role proposal before it names the worker.
   - **Recommendation:** (a) first. It is a §6 defect on every escalation, it is small, and (b)'s
     oracle will want the exact text that (a) produces. Expect to find out within minutes whether
     this is wrong: if `band_text` and the region's ink disagree on any of the 71 regions, (a)'s
     premise is false.
3. **ASSERTED:** both findings beyond the brief are **not yet register rows**. Raise them in the
   next loop's first commit, with this appendix as the measurement. The two findings are the lossy
   `surfaceText` and the escalated-token under-count (word objects counted, not whitespace words).

## 1. Goal

Choose and scope the next loop. Done: the maintainer chose **R44** (2026-10-15, this session) over R74,
substrate:01-03 and tab:10.

## 2. Where the primaries are

- `docs/superpowers/residues-open.md`, row **R44**: read its ✎ updates of 2026-09-15 and 2026-09-16
  (the round-trip half is a REPORTING defect; reading defects split out as R238 (closed) and R239).
- `docs/superpowers/2026-10-05-accept-bfs.md` §2: bfs's live escalations at `c410604`, with ink.
- `tests/corpus-baseline/*.json`: live escalation counts per document (the "before" of any change;
  never re-run main for a before; CLAUDE.md § Corpus baseline).
- `tests/arc-manifest.ttl`: `prog:criterion:tab:02`, `tab:07` (and `tab:09`).
- The census: appendix below.

## 3. What was decided, and where it is recorded

- **The subject is R44, scoped toward its `KIND_NOT_SUPPORTED` and `REGION_TILING_FAILED` live
  firings.** Recorded nowhere but this file (the maintainer's choice was made in-session). Reversible.
- R44's round-trip half is not a reading subject: recorded in R44's 2026-09-16 ✎.

## 4. Unverified or assumed

- Live counts per reason, measured this session from `tests/corpus-baseline/*.json` at `9d3c73c`
  (verdict == `escalated`): `KIND_NOT_SUPPORTED` arxiv 47, who-covid 7, fed-h41 6, bfs 3, ons 2
  (65 in total); `REGION_TILING_FAILED` fed-h41 4, bfs 2. These are counts only. **Which ink they
  are is the census's job, and until it is read the "context around tables" premise in § 5.2 is a
  proposition.**
- The cockpit's `ready 3` (unmet criteria naming no `prog:blockedBy`: substrate:01-03) and the
  landscape's `12 ready` (no unmet criterion *dependency*) answer different questions. Both are
  correct; noted so the next session doesn't take them for a contradiction.

## Appendix: ink census (delegated measurement)

Delegated to a subagent at `9d3c73c`. Measurement only, nothing tracked edited. Its instrument
(`census.py`, which wraps `compile.escalate_region` in-process and reads `bands.band_text(band)`) lived in
the session scratchpad and **does not survive this session**. The method is stated here so the census
can be rebuilt.

**Control: PASSED on all 5 documents.** Live counts by reason equal `tests/corpus-baseline/*.json`
exactly, the (page, region, reason) lists are identical, and the scores are identical. The join was
on (page, region index) and the candidate IRI, **never on `anchor`**. `/adopt#` re-compile captures
were excluded. Each document was compiled in its own process, serially.

### Role totals (the subagent's reading judgement: a PROPOSITION, read off the text, not the rendered page)

| doc | set | live K / R | roles |
| --- | --- | --- | --- |
| bfs | corpus | 3 / 2 | masthead 1, table-title 1, mixed 3 (source line + footnotes ×2; running header + 2 chart captions + footer ×1) |
| ons | corpus | 2 / 0 | table-title 1, mixed 1 (masthead + table of contents) |
| who-covid | held-out | 7 / 0 | masthead 1, footnote 1, body-prose 2, table boxhead 1, mixed 2 (one is table body + totals + footnotes) |
| fed-h41 | held-out | 6 / 4 | masthead 1, mixed 6 (table title + unit line + boxhead), **table body rows with data values 3 (all R)** |
| arxiv | held-out | 47 / 0 | bibliography entry 32, body-prose 4, chart labels 4, mixed 4, caption 1, author block 1, equation 1 |

K = `KIND_NOT_SUPPORTED`, R = `REGION_TILING_FAILED`.

### Verbatim samples (exact `band_text`, ⏎ = line break)

- bfs p0r0 K 6: `Communiqué de presse⏎Embargo: 22.8.2024, 8h30`
- bfs p4r0 R 36: `Communiqué de presse OFS⏎G1 Composantes de l'évolution démographique, de 1971 à 2023⏎G2 Population résidante permanente étrangère selon la nationalité, au 31.12.2023⏎OFFICE FÉDÉRAL DE LA STATISTIQUE OFS, ESPACE DE L'EUROPE 10, CH-2010 NEUCHÂTEL 5`.
  The graph's surfaceText for the same region reads `G1 Composantesde l'évolutidémographiquede 1971à2023`.
- bfs p6r1 K 16: `T3 Population résidante permanente par classe d'âge et rapports de dépendance selon le⏎canton, au 31.12.2023`
- bfs p6r11 R 3: `Source: OFS - STATPOP⏎1 Nombre de personnes de moins de 20 ans pour 100 personnes de 20 à 64 ans⏎2 …`. This region books **3 tokens for 38 words**.
- ons p7r0 K 19: `IOS1 IOS: Index of Services 1⏎Chained volume indices …`. The graph's surfaceText reads `IOS1 IOSIndeoServic1s`.
- fed p6r4 R 20: `Capital accounts⏎Capital paid in 37,182 + 15 + 1,117⏎Surplus 6,785 0 0⏎Other capital accounts 0 0 0`. These are table body rows.
- arxiv p10r1 K: `[1] JimmyLeiBa,JamieRyanKiros,andGeoffreyEHinton. Layernormalization. …`. This is one bibliography entry per region.

### Code and vocabulary map (as reported; file:line at `9d3c73c`)

- `KIND_NOT_SUPPORTED`: `compile.py:1876-1890`. It fires when the kind is `UNSUPPORTED_TABLE`, the band is not
  a matrix candidate, and `classify_hierarchical` returns None. `UNSUPPORTED_TABLE` comes from
  `classify-kind.rq` via `regions.classify` (`regions.py:87-97`). `REGION_TILING_FAILED` is emitted at
  `compile.py:1377-1390`, `:1614-1627` and `:1838-1851`; every bfs and fed firing comes from the
  hierarchical site. **The criteria statements in `tests/arc-manifest.ttl` cite stale lines**
  (`:656/763/939`, `:978`).
- Existing vocabulary: `tab:RegionCaption` / `tab:captionText` / `tab:hasCaption` / `tab:SectionCaption`
  (`vocab/ontology/tab.ttl:574-581`) have domain `tab:Table` and are emitted only for an asserted
  table. They are emitted **0** times on all five documents. `etkl:IgnoredBand` (`etkl.ttl:222-236`)
  carries only NON_TABLE bands. **No class types a text band's role**: there is no title, footnote,
  source note, masthead, prose or heading class.
- NEURAL: no worker reads a whole band's role. The nearest is `ProposeHeaderRowRoles`
  (`header_rowrole.baml`), and it works only inside an already-classified header.
- Criteria: tab:02 and tab:07 are met by a dated `cor:adjudication` that disposes of every firing.
  bfs (`corpus-manifest.ttl:453-454`) and ons (`:113-114`) already have adjudications that name every
  firing with matching token counts, but neither disposes of them by a readable fact (R259). The
  oracle the criteria name, `tests/test_corpus.py::test_escalation_reasons_are_adjudicated`, **does
  not exist** (R259).

### Unverified (the subagent's own list, plus mine)

- Every role label is a reading of the extracted text, not of the rendered page. The least certain
  are who p0r2 (two columns interleaved), arxiv p0r4 (margin stamp), and the "masthead" vs
  "table-title" calls on fed.
- "The text layer is clean" is shown through `band_text` joining the band's words, not by rendering
  the page.
- The 59/71 loss count compares whitespace-stripped strings, so a word-order difference would count
  as loss.
- The cause of the token under-count is inferred, not traced.
- The ons adjudication text at `:114` was not re-read by this session. bfs `:454` was.
