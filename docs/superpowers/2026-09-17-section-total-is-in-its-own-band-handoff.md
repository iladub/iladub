# Handoff — the section total is in its own band ([[R47]] re-confirmed, [[R77]] re-stated)

**Topic:** The section total is in its own band — [[R47]] re-confirmed at HEAD, [[R77]] re-stated
as the second gate, no remedy designed.

**Serves:** prog:criterion:tab:04 — [[R77]] is one of its three blockers

**Date:** 2026-09-17. **Tree:** branch `section-total-is-in-its-own-band`, cut from `main` at
`275659a`.

**Doc impact: none.**

This loop MEASURED and built nothing. It was handed [[R77]] as its subject after the previous
handoff's § 5a was run and refuted in one command.

---

## 5. The next concrete action

### 5a. PROPOSED — close the measurement hole BEFORE designing any remedy

**Typed PROPOSED because the false-positive denominator is incomplete, and the obvious
discriminator is the one this loop already refused to key a rule on.**

The adjacency-tightened surface is `true=4 false=4`, but **6 pages were skipped** — apple p0/p1/p2,
bfs p5, ons p7/p8 — because the census mapped regions to bands by index and those pages have no
1:1 correspondence (e.g. apple p2: 8 bands, 10 regions). Those are not clean pages; they are
*unmeasured* ones, and they are on the two documents with the largest escalation surface in the
corpus. **The `false=4` figure is a floor, not a count.**

The prediction worth registering before it is run: **the skipped pages add more false positives
than the measured ones did**, because a page whose region count exceeds its band count is a page
where bands were split or peeled — exactly the shape that puts a stray number beside a table it
does not belong to. If that holds, arithmetic-plus-adjacency is not a sufficient disposer on this
corpus and the honest product of the next loop is a **recorded refusal**, not a remedy.

**The probe is a correspondence fix, not a new instrument:** replace the index-based region↔band
mapping with a y-overlap match (a region's band is the one whose `[top, bottom]` it falls inside),
re-run, and report `true/false` with **zero** pages skipped. Run it FIRST. The script is in this
loop's evidence § 11 lineage; it is ~30 lines and one corpus pass (~5 min, serial — never two
corpus compiles at once).

**Do not adopt the 1-line/6-line discriminator that the data suggests.** Every true positive's
following band has 1 line and every false positive's has 6, and that is the cbh-fitted shape
(4 instances corpus-wide, all one page). Adopting it would be the overfitting this repo forbids
with zero tolerance; falsify it on the six unmeasured pages first.

### 5b. ASSERTED — what is mechanically finished and must not be redone

- **Do not re-measure the `gap_factor` arm.** It is REFUTED with numbers: every cut on cbh p0 is
  5.24x-6.11x the median against a 1.8x threshold, so no value admits the total and keeps the four
  panels apart. `detect_bands` reads the author correctly.
- **Do not re-derive the column sums.** Column 13 equals each printed total exactly on 4 of 4
  panels (members 10/16/14/5), matching the grid path's independent `{20:10, 42:16, 63:14, 74:5}`.
  The disposer exists and is exact; only the window is missing.
- **Do not treat this as a discovery.** [[R47]] has owned the band-separation finding since
  2026-08-04, naming the specimen *"in a separate `detect_bands` band from the grid"*. This loop
  re-confirmed it at HEAD and added the refutation, the constructibility and the composition.
- **Do not close [[R77]] by fixing `is_aggregation_shaped` alone.** It is the second gate and is
  unreachable while R47's window gate stands; closing it alone moves nothing.
- **Do not trust R77's predicted score movement.** `0.0698 -> ~0.074` is impossible: the totals are
  `ignored` bands booking 0 asserted and 0 escalated tokens, so their ink is in neither operand.

### 5c. PROPOSED — the design fork is named but NOT chosen

Two candidate homes for the window, and this loop deliberately chose neither: widen
`_confirm_section_total`'s window to the following band, or build [[R47]]'s trailing-strip
peel/carry so the total enters the band as a row. The §8 class differs between them and is not
obvious — *"does this printed block belong to the table above it"* is a reading judgement, not a
geometric one. Typed PROPOSED: it is a design decision whose evidence (5a) is not yet complete.

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-17-section-total-is-in-its-own-band-evidence.md`. § 3 is the
  ignored-region dump, § 5 the instrumented bail-out, § 6 the refuted `gap_factor` arm, § 7 the
  4/4 column sums, § 8 the two gates, § 10 the population caveat, § 11 what is NOT established.
- **The rows** — [[R47]] (owns the window gap), [[R50]] (adjacent, insufficient alone), [[R77]]
  (the arc-serving row, second gate), all amended in place in `residues-open.md` + `residues.md`.
- **The code** — `document._confirm_section_total` (`document.py:1136`), `bands.detect_bands`
  (`bands.py:37`), the ignore rule (`regions.py:91`), the disposer
  (`rows.detect_aggregation_rows`, `datagrid.confirms_aggregate`).
- **The vocabulary is already there** — `tab:SectionTotal` + `tab:confirmsSection`
  (`vocab/ontology/tab.ttl:551-556`); nothing new is needed.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| R243's § 5a prediction refuted; it is two defects, not one | evidence § 1 |
| R77's claim true, mechanism re-stated as the SECOND gate | R77's row; evidence § 8 |
| The `gap_factor` remedy is refuted, not untried | R47's row; evidence § 6 |
| R50's walk-back is insufficient alone on the real specimen | R50's row; evidence § 9 |
| The arithmetic is NOT self-disposing (4 false positives survive adjacency) | evidence § 11 |
| No rule may be keyed on the one-line-numeric-band shape | evidence § 10, § 11 |
| The design fork is named, not chosen | § 5c above — **nowhere else**, so it is open |

## 3. Unverified or assumed

- **The six skipped pages** (apple p0/p1/p2, bfs p5, ons p7/p8) — unmeasured, not clean. § 5a.
- **The 1-line/6-line discriminator** — a correlation on n=8, explicitly not adopted.
- **Why vessel row 26 is `unplaceable`** — the other half of [[R243]], untouched.
- **Whether a correctly-drawn decoration rectangle would be regressed** — inherited from the
  previous loop, unchanged and undetectable on this corpus.
- The band↔region index correspondence held on cbh p0 (10/10) and was *verified per page* rather
  than assumed — which is what produced the skip list rather than silent wrong answers.

## 4. What this session did, and what it cost

Ran the previous handoff's § 5a probe (refuted in one command), took [[R77]] as the maintainer's
chosen subject, and measured: the page-scope region dump, document-vs-page scope divergence, the
instrumented `_confirm_section_total` bail-out, the live band-gap geometry, the 4/4 column sums,
the corpus shape census, and the false-positive surface at two tightnesses. Amended three register
rows and their index hooks. Built nothing.

**The cost worth carrying: three near-misses, all of the same family — a measurement that would
have been wrong in the direction of confidence.**

1. **A one-directional graph query nearly produced "the repaired rows carry no cells."** Querying
   a leaf row's *outgoing* triples returns `rdf:type tab:LeafRow` and nothing else; the cells
   attach by **incoming** `tab:atRow`. Had that stood, the remedy would have been declared dead on
   arrival. **Check both directions before concluding absence from a graph.**
2. **`timeout` does not exist on macOS** — already in the register, and I used it anyway; the
   command ran nothing and the census had to be re-run. Read the output, not the exit code.
3. **The loose false-positive census was nearly reported as the answer.** At its loosest the
   figure was 4 true / 11 false; tightened it is 4/4. Neither is the "real" number — the first is
   an upper bound and the second has six pages missing. **A census whose denominator you have not
   audited is a claim, not a measurement.**
