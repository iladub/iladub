# Handoff — R207: a section marker grounds on the unique scheme that carries its value

**Topic:** the PROPOSED action 5a of `docs/superpowers/2026-09-10-gliner2-the-count-handoff.md`
— measure whether cbh's rows already carry a port, and if not, bind the section marker through
the scheme oracle already in `ground.py`. The measurement came back 58 of 58 without a port, so
the loop built the branch. Part 5 was written before the docs, at ~75K working tokens — over the
originating floor, so each action below is graded on its own line.

**Doc impact: increment.** `docs/wiki/concepts/dimension-split.md` gains a dated paragraph
stating that the section key reaches the record as a value only since this loop; no vocabulary
changes, no site page.

---

## 5. The next concrete action

### 5a. PROPOSED — [[R208]]'s weld is in the emitter's leaf-row structure, and one dump names the mint

The blank-key cause in `table_records` is **refuted** (§ 2): the joined values are one
`tab:EntryCell` per column in the compiled graph, and the page's band holds the three Mackay
lines as three separate `Line`s. So the weld happens between `page_bands` and the EntryCells,
inside the hierarchical table's row structure — and the fused record's identity is a row PATH
(`2026/27 > Oct 26 > Mackay Mackay Mackay`, no `p1 htable1-rN` suffix), which says the port
column was read as a row-header level. The prediction: a repeated row-header value in
consecutive lines (`Mackay` ×3) is read as ONE spanning header cell and its lines welded into
one leaf row. **Run before building on it:** for `p1 htable1`, print the `tab:LeafRow` whose
cells' bbox `y0` is 71.31 and every row-header / `tab:DerivedRowGroup` node covering it, then
read the mint in `hierarchical.py` / `rowheaders.py` / `rows.py`. It is falsified in one run if
the LeafRow already spans three lines before any row-header derivation. **What the pattern does
NOT explain:** Nov 26 has four consecutive Mackay lines and only the first two weld (213.87 +
220.35; 226.83 and 233.31 stay separate), so "repeated value" alone is not the rule.

### 5b. ASSERTED, and the maintainer's — the GLiNER2 spec branch still needs a disposition

Carried verbatim from the predecessor's 5c: branch `only-a-refusal-admits-the-model` is refuted
before T1 (R206) and unpushed. Push as a refuted record, or drop; nothing depends on it. This
loop removed the last live thread from it — the 49-cell ceiling is now 0.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the branch | `src/iladub/ground.py` — `marker_field`, the `elif` in `ground_concept`, `_UNIQUE_ADMITTING_FIELD_RULE` | AXIOM: unique scheme admission derives the field; zero or two abstain; not called on non-markers |
| the shared rule | `src/iladub/splitkey.py` — `_MEMBERSHIP_RULE` now aliases the ground constant | one suggester IRI at both grains (per name there, per value here) |
| the pins | `tests/test_ground_section_marker.py` (6 tests, synthetic) · `tests/test_cbh_e2e.py::test_cbh_every_sectioned_record_carries_its_section_port` (corpus) | falsified in § 3 |
| the instrument | `scripts/placement_population.py` — replays the marker branch as `marker-grounded` | the R206 figures re-taken under the branch (§ 2) |
| the wiki increment | `docs/wiki/concepts/dimension-split.md` § "Attribution never waits for naming", dated paragraph | the sentence that was false at record level, and since when it is true |
| the 5a/5b measurements of the predecessor | scratch scripts, not committed; their outputs are transcribed in § 2 | re-run from the description if needed: ground cbh with the abstaining proposer, count records with no `cbh:port` |

## 2. What was measured (2026-09-10, on `b599ef3` + this branch)

**5a of the predecessor — the premise.** cbh, abstaining proposer, before the branch:

| | value |
| --- | --- |
| records / grounded / proposed | 58 / 134 / 775 |
| records with **no** `cbh:port` | **58 of 58** |
| properties any record carries | client 45, commodity 44, volume 45, type 45 — never port |
| records whose identity prefix is not among its own markers | 0 |

After the branch (`tests/test_cbh_e2e.py`, printed): grounded **183**, proposed **726**; all 49
section-prefixed records carry exactly one `cbh:port` equal to their prefix; the 9 unsectioned
records carry none; the grounded targets are exactly the four ports the page sections under
(the scheme's fifth, Bunbury, is never grounded).

**The instrument, re-run under the branch** (`scripts/placement_population.py`):

| | graincorp-stem | cbh-stem |
| --- | --- | --- |
| tally | novel 1217 · exact-grounded 585 · exact-refused 48 (unchanged) | novel **725** · **marker-grounded 49** · exact-grounded 134 · exact-refused 1 |
| CEILING | 0 (unchanged) | **0** (was 49) |

**5b of the predecessor — R208's location.** graincorp p1, the joined records:

- `rec[38]` identity `2026/27 > Oct 26 > Mackay Mackay Mackay`; every cell's region is at
  `y=71` (`p1-96-71`, `p1-162-71`, …) — ONE EntryCell per column carries the three lines' text.
- `page_bands(pdf, 1)` band 1 holds the three Mackay lines as three `Line`s: top 71.31, 77.79,
  84.27 (bottom 76.59, 83.07, 89.55); the neighbouring Gladstone lines at 97.23… are read as
  separate records (`… > Gladstone > p1 htable1-r2`, `-r3`, `-r4`).
- Six joined records in all: indices 38, 54, 70, 91, 93, 110. Nov 26 (rec 54): lines 213.87 +
  220.35 welded, 226.83 and 233.31 not.

So the weld is downstream of lines and upstream of the feed; `table_records` is not the site.

## 3. What was decided, and where that decision is recorded

- **The branch is AXIOM and marker-scoped.** Recorded in `marker_field`'s docstring and pinned
  by `test_a_data_cell_carrying_a_scheme_value_is_not_a_marker_and_stays_quarantined`.
- **Ambiguity abstains** (two admitting schemes → quarantine). Pinned by
  `test_a_marker_two_schemes_carry_is_quarantined_not_guessed`.
- **One suggester IRI for both grains** of the unique-admitting-field rule. Recorded at the
  constant's definition in `ground.py`; `splitkey.py` aliases it.
- **Falsification:** with the `elif` replaced by `elif False`, 3 of 7 pins fail
  (`…grounds_on_every_record…`, `…records_the_membership_rule…`, the corpus pin); restored, 7 pass.
  Recorded nowhere but here and the PR body.
- **R207 closed, R208 amended.** `docs/superpowers/residues-closed.md`, `residues-open.md`,
  index `residues.md`.

## 4. Unverified or assumed

- **The corner where a caption literally equals a field name** (`Port` as a section caption):
  `exact_field` wins first and the scheme refuses the value, so it quarantines as today. Reasoned,
  not tested.
- **`scheme_member` returns the first concept whose prefLabel matches**, so two concepts in ONE
  scheme sharing a prefLabel are not detected as ambiguous by `marker_field` — it counts
  admitting FIELDS, not concepts. Pre-existing property of the oracle, unchanged here.
- **The instrument's URI warnings** (`>` and `/` in the probe subject) still print; the
  predecessor silenced only spaces. Noise, not a figure.
- **5a's pattern** (repeated row-header value welds) is a reading of one page, and Nov 26
  already half-contradicts it (§ 2).
- The full suite was not run in-session (~61 minutes, [[R181]]'s figure); the related suites
  were: `test_ground_section_marker`, `test_feed_section_keys`, `test_split_key_naming`,
  `test_concept_feed`, `test_suggester_guard` (60 passed), `test_cbh_e2e` (4 passed).
