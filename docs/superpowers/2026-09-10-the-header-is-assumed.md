# Loop record — the header row is assumed, not derived

**Branch** `r166-the-header-is-assumed`, off `4905355`. **Subject:** [[R166]]'s surviving p2 half
and the question the nil-glyph handoff § 5b left graded PROPOSED.
**Spec:** `docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md`.

**Doc impact: none.**

## 1. What was asked, and what came back

§ 5b asked: *"read what band 6 asserts today, then ask whether any decidable signal distinguishes
it from a real header without a tuned constant."* It named the two outcomes: an axiom, or a ruling
that the answer is NEURAL. **The measurement produced a third thing first — the population is not
two apple bands but twelve corpus bands, eleven of which assert a row that is not a header** — and
then the ruling: no in-band signal exists, and the two candidate marks are unavailable *by
construction*, not merely absent. Spec § 2 and § 3 carry the tables; they are not restated here.

## 2. The instrument

`scripts/header_row_census.py`, committed. It prints, per asserted table, the `tab:LabelCell`
texts the graph carries and the first data row beneath them — both graph-derived, so the reading
does not depend on re-identifying the band. Where it *does* re-identify the band (for the datatype
profile) it CHECKS the identification and prints `aligned=no` when the check fails; that fired
once, on bfs p5 band 13, and that row's profile columns are correctly absent.

Run: `PYTHONPATH=. .venv/bin/python scripts/header_row_census.py` (≈6 min, whole corpus).

## 3. Falsification

Both new tests in `tests/etkl/test_header_row_is_assumed.py` were inverted, seen RED, and restored.

| # | inversion | result |
| --- | --- | --- |
| F1 | `holon.py`'s `g.add((lc, RDF.type, TAB.LabelCell))` → `TAB.RegionCaption` | 1 RED (the detector) |
| F2 | `classify-kind.rq`'s `IF(?nhw = ?nc && !?mis, …)` → `IF(true, …)` | 1 RED (the corner pin) |
| F2a | the same gate weakened only to `?nhw <= ?nc` | **2 PASSED — no red** |

**F2a is the one to read.** It was run as F2's first attempt and failed to falsify anything, which
is how the two-clause structure of § 3(b) was found: a blank corner trips the strict-order clause
`!?mis` as well as the count, so weakening the count alone still refuses the band. The arm is
closed twice over, and the spec says so because the falsification refused to cooperate.

## 4. What was NOT done

No compiler behaviour changed. The reasoning is spec § 4: the change the census argues for refuses
12 of 12 record-table readings (11 upright, 1 transposed) and re-baselines every corpus score in the suite, which is a plan's
work, not a measurement's. [[R166]] therefore stays **open**, amended rather than closed.

## 5. One prediction RUN before the handoff shipped, and refuted

The handoff's part 5b was drafted recommending the loop-M carriage seam for bfs p6, on the ground
that bfs p6 band 2 asserts through the flat-record branch where apple's asserts through the matrix
branch — *"a different emitter"*. It was run rather than shipped:
`scripts/forced_carriage_spike.py corpus/gov-stats/bfs-population-bilan-2023.pdf 6 2 4` returns
`header_reading=None` for band 2 and `carried_roles_for(...) -> None`, with `baseline=276
forced=276`. **One site mints a `CarriedHeaderReading` — `ruledroles.py:549`, in the hierarchical
assert path — so the emitter distinction the prediction rested on does not exist.** 5b is regraded
and the fork is stated with three arms; see [[R201]].

## 6. Corrections made in-session

- **The mechanism R166 names is incomplete, and the first version of this spec overstated the
  correction.** R166 says the reader takes the first line as the header; the deeper fact is that
  `classifygraph.classify_evidence:53` names it `tab:HeaderWord` before any query runs. The spec's
  first draft added that `header_body_split` *"is never called on this path"* — **false**, and
  caught by grepping the call sites rather than by reading the branch: it IS called at
  `compile.py:172` while a ruled band is built, to decide whether a candidate column boundary lies
  in the header region. It does not decide the label row, which is the claim that survives.
- **`residues-open.md:75` → `:119`.** The spec's first draft cited R166's row from memory of the
  index rather than from the file.
