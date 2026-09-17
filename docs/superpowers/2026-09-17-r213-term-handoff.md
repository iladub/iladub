# Handoff — R213's term: ink the author hid

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on this row.

**Date:** 2026-09-17. **Doc impact: none.**

Written at the end of the session that merged PR #259 and PR #260, with part 5 first, per
CLAUDE.md § "The handoff's next action is TYPED". **No harness token figure was reported to
plimslop this session** (`~/.claude/plimslop/corpus.jsonl` carries no `measured` entry for it), so
the usual working-token figure is absent rather than withheld. The session ran two merges and a
full corpus compile; the spec was deferred to a fresh context on that basis, not on a measurement.

## 5. The next concrete action

### 5a. ASSERTED — write the R213 term spec, in a fresh session, spec first

The ruling exists and does not need re-taking: **2026-09-13, option (c)** — an invisible glyph is
carried as a **typed absence or a proposition**, never as the `0` it reads. Option (a) (carry the
`0`) was refused under §7, option (b) (emit nothing) under §5. `residues-open.md:146` is the row.
The loop designs the term and ships it. It does **not** re-open the ruling, and it does **not**
build [[R250]]'s derivation.

### 5b. ASSERTED — the gap the term fills, measured

`tab:Blank` covers **two** of the three cases, in its own published comment
(`vocab/ontology/tab.ttl:260-261`): *"one carrying no ink at all, or one whose whole text is a
MARKER the author writes to mean 'nothing here'"*, with the markers enumerated as `tab:nilSpelling`
(`tab.ttl:303`: `"(blank)"`, `"-"`, `"–"`, `"—"`). The third case — **ink that is present and
which the page does not show** — has no term. Today gcap's 110 invisible glyphs read `0`, so they
type as `tab:Numeric`, they **vote** in every homogeneity judgement, and they are grounded as
tonnages. `tab:Blank` abstains from those judgements (`tab.ttl:293-297`, `tab:datatypeAbstains`),
which is the behaviour the new term most likely needs, and the spec must say so explicitly rather
than inherit it by resemblance.

### 5c. ASSERTED — the seam, measured, and it is the expensive part

**No colour is read anywhere in `src/`.** `grep -rn "non_stroking_color\|stroking_color"
src --include='*.py'` → **no hits**; the only `page.rects` use is `datagrid.py:184`, for geometry.
Words come from `geometry.extract_words` (`geometry.py:41-50`, `page.extract_words(...)`), and a
`Word` carries no colour. So the measurement R213 recorded was made by a throwaway probe, and the
shipped reader cannot currently tell an invisible glyph from a printed one. **Extending extraction
to carry the glyph's colour and the fill beneath it is the loop's real work**, and it is
PROCEDURAL raw extraction under §8, in the same class `geometry.py:79` already names for the
vector-line reader. Name the §8 class in the spec for each part; the *classification* of an
invisible glyph is not the extraction.

### 5d. PROPOSED — what the term should be, and how it could fail

A new `tab:CellDatatype` (the lattice is declared OPEN, `tab.ttl:259`) whose cells abstain, plus a
property recording that the glyph was read and suppressed, so the reading says *there is a glyph
here the page does not show* rather than asserting `0`. **This is a proposition, not a plan.** Two
ways it fails: (1) a datatype may be the wrong carrier, because the value is not absent, it is
hidden, and a *datatype* that abstains still loses the fact that ink exists — a proposition
(`iladub:CandidateConcept`) may be the ruling's other branch and the better one; (2) the dark cells
are one publisher's palette, so a term named after *invisibility* may be naming a rendering
accident rather than an authoring act. Decide in the spec, with the ruling's own words (*typed
absence **or** a proposition*) as the fork.

### 5e. ASSERTED — the generality limit is n = 1, and no corpus document can lift it

All 110 invisible glyphs are in graincorp-capacity; the other six documents have **zero**. The
colour discriminator is threshold-insensitive on this corpus (a 0.1935-wide empty band) and that
is a property of dark-navy-on-dark-navy, not of the class. A second specimen in mid-grey on
light-grey lands inside the band, and then the threshold decides and §8 sends the class to NEURAL.
**Do not let the spec's oracle be "the band is empty"** — say what happens when it is not.

### 5f. ASSERTED — what must NOT be done

Do not build [[R250]]'s derivation in this loop (it is blocked on this one, measured in
`2026-09-17-r250-furniture-field-names-evidence.md`), do not re-litigate option (c), and do not
tune a colour threshold: the band's width is a measurement, and a constant chosen inside it is the
§8 defect the gate names.

## 1. Where the primaries are

- Ruling and row: `docs/superpowers/residues-open.md:146` ([[R213]]).
- The two existing absence terms: `vocab/ontology/tab.ttl:259-261`, `:293-303`.
- Cell typing: `src/iladub/etkl/celltype.py:77-124`.
- Extraction seam: `src/iladub/etkl/geometry.py:41-50`.
- The blocked consumer: [[R250]] in `residues-open.md`, evidence
  `docs/superpowers/2026-09-17-r250-furniture-field-names-evidence.md`.
- This session's ruling note: `docs/superpowers/2026-09-17-r249-half-b-ruling.md`.

## 2. What was decided, and where it is recorded

- **R249 half (b): no worker; the measure name is derived per [[R212]]** (maintainer, 2026-09-17).
  PR #259, `db49647`. R249 closed.
- **R213 option (c)** (maintainer, 2026-09-13), unchanged and unimplemented.
- **R250 raised and measured**: the ruled derivation does not exist, and the shipped route hands
  the furniture to the proposer (`src/iladub/feed.py:747-757`). PR #260, `e5d61b6`.

## 3. Unverified or assumed

- Whether a datatype or a proposition is the right carrier for hidden ink — 5d, undecided.
- Whether `tab:datatypeAbstains` is the right behaviour for the new term — inherited by
  resemblance to `tab:Blank`, not measured.
- Whether any corpus document other than gcap would be touched by the extraction change — the
  colour read is new, so its cost and its effect on the seven scores are **unmeasured**.
- R250's elimination rule (drop words already claimed as a column label or key value) is fitted to
  its one firing document and is not established.

## 4. What this session did

Ruled R249 half (b) and closed the row (#259); raised R250; measured R250's first step with
`scripts/furniture_field_names.py` (#260), finding `capacity` in gcap's title, all four field names
in its furniture, and 110 of 149 asks being R213's zeros. Parking-candidate count moved 90 → 92 →
91, each step recorded with its control in `tests/test_residue_graph.py`.
