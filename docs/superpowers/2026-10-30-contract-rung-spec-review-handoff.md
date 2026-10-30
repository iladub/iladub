# Handoff 2026-10-30: fold the builder check into the contract-rung spec

## 1. Goal

Revise `docs/superpowers/specs/2026-10-30-contract-rung-design.md` (branch `contract-rung-spec`) so
it passes a builder check, then take it to the maintainer.

## 2. Where the primaries are

- **The spec**, in this branch. § 3 holds the measurements and § 5 the gate. The mechanical fixes
  from the review are already applied:
  - line numbers;
  - the rung count stated at `scope-evolution.md:23`;
  - the collision with `src/iladub/contract.py` (now Q7);
  - the rung-key grep.
- **Its source brief:** hdc-contract
  `docs/superpowers/2026-10-30-handoff-rescope-specs.md` § 3, which holds the maintainer's
  rulings (untracked in that repo's checkout).
- **Measurement scripts:** `heading_match.py` and `coverage.py`, in the hdc-contract session
  scratchpad (`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-hdc-contract/2c778714-515a-4871-a46b-f74e6e9eadc0/scratchpad/`).
  They are ephemeral, so re-create them from spec § 3 if they are gone. Run them in hdc-contract
  with `uv run --with rdflib --with pyyaml python <script>`.
- **The segmenter being ported:** hdc-contract `src/hdcc/ingest/extract.py:11-116`.

## 3. What the builder check found that is still open (recorded only here)

A fresh subagent ran the check against iladub `bbac3de` and hdc-contract `4b576f0`. Its claims
below were not all re-measured (see § 4).

1. **§ 5 doesn't classify every part of the segmenter.** These pieces are unclassified:
   - `_LEADERS [….]{3,}`, where `{3,}` is a threshold;
   - `_LONE_NUM`;
   - the `\f` handling;
   - `_HEAD_TOKEN`'s character class;
   - the one-line heading carry-over at `extract.py:100-108`;
   - where the last clause ends: signature blocks and annexes become its body.

   Each piece needs a row, or must be removed.
2. **"Number greater than the previous start" is a filter.** It silently drops numbered lines
   such as cross-references, so it is a judgement about which lines are clauses, not plain
   extraction. Either the § 5 row argues this, or the extractor emits every candidate and lets a
   declared rule choose.
3. **The contiguity constraint:** must the first clause be 1? The reviewer reports:
   - 3 of the 80 forms start above 1 (120 at 2, 129 at 3);
   - 14 of the 80 (311 clauses) have gaps.

   So the membrane as written refuses those forms, and M-i's "241 would fall back" assumes they
   compile. Fix the M-i reading and decide what the membrane admits.
4. **`membrane.validate` needs an `ont_graph`** (`etkl/membrane.py:45`). The spec should say which:
   ctr.ttl, plus the alignment, plus the scheme?
5. **What is arbitrated:** § 6.5 says untyped clauses only, while § 4 also routes the `also` types.
   And a clause typed wrongly (48 cl.7) never reaches arbitration. State all three flows.
6. **The truth is mostly unconfirmed:** 43 of the 49 hero rows are `needs_trader_check: true`.
   contract:01 must say it scores against unconfirmed truth.
7. **§ 7 against Q6:** an adjudication alone can pass 48 cl.7 under § 7's statement. Decide whether
   that is intended.
8. **§ 10's escape hatch** ("if review rejects the segmentation argument, it goes to the
   maintainer") defers the gate. It should be settled with the maintainer before a plan.
9. **Smaller items:**
   - Should the scope-evolution heading put the key in backticks (`` ### `contract` — … ``),
     like the existing headings?
   - The contract:01 statement should note that the 2 untyped hero clauses are expected.

## 4. Unverified or assumed

- The reviewer's 80-form counts were not re-measured by this session: 3 forms starting above 1,
  and 14 forms / 311 clauses with gaps.
- `43 of 49 needs_trader_check`: not re-measured.
- Ruling 5's reading (the ingest moves to iladub) is still unconfirmed by the maintainer.
- Everything in spec § 11.
- The hdc-contract companion spec has not been started.

## 4b. Done in the follow-up session (2026-10-30, uncommitted)

- The § 4 counts were re-measured and folded into spec § 3 as M-o and M-p. 3 forms start above 1
  (120, 202, 129); 14 forms / 311 clauses have gaps; 42 of the 49 rows are flagged (not 43).
- Items 1-3 are folded into spec § 5, with one row per construct. Gaps are the segmenter's misses
  (M-o), so the membrane is **contiguous from 1**: 67/80 forms are admitted and 13 refused. M-i is
  restated over the admitted forms (220 fallback). The extractor is restated untuned (M-r):
  `\d+`, `[….]{2,}`, the letter-case heading token, the maximal carry-over, and a kept
  `ctr:preamble`. The trailing signature/footer is documented in § 6.5.
- Scripts: `gaps.py`, `variants.py`, `refused.py`, `coverage.py` and `heading_match.py`, in
  `/private/tmp/claude-501/-Volumes-WD-Green-dev-git-hdc-contract/9b1760f4-94d2-4cf9-8ac4-1361fa846c8e/scratchpad/`.
  They are ephemeral.
- Still open: § 3 items 4-9.

## 5. Next concrete action

In a fresh session, re-measure the two counts in § 4. Then rewrite spec § 5 with one row per
segmenter construct (§ 3 items 1-2) and decide the contiguity rule (item 3), before touching the
rest of the list.
