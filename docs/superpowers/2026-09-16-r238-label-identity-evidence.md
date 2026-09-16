# Evidence — are the 92 carried cells the RIGHT cells? bfs p5 label identity

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Doc impact: none.**

The subject ruled in `2026-09-16-identity-before-remedy-ruling.md`: before any remedy is
designed and before scope is ruled, verify that the 92 cells PR #239 measured are the **right**
cells. That ruling supersedes the preceding handoff's § 5a.

---

## 1. The reading rule, PRE-REGISTERED

**Written and committed before the probe was run.** This section and the instrument land in one
commit, and the figures land in a later one; the git order is the claim. The reason is this
repo's own recorded failure mode — a verdict formed after seeing the numbers is
indistinguishable, in the write-up, from a measurement (PR #239 § 2, and the `r234` loop's
*"a positive result is not self-interpreting"*).

### 1a. What is being asked

PR #239 § 3d measured **cardinality and side of the rectangle**: under the alignment universe
col 0 sits at x ≈ 72 (left of the decoration rectangle's `124.3` edge) and col 11 at x ≈ 514
(right of `495.3`), **both full at 46 of 46 rows**. It did not measure **identity**, and the
sample it printed read `2005` / `2006` — the T1 time-series rows — not the canton names
[[R238]]'s symptom names (*"nothing says which row is Zurich"*).

### 1b. Why a year cannot exhibit the risk

`_place_for_emit` keys a run on its **centre** (`datagrid.py:764`). A 4-character year is a
short run whose centre sits deep inside col 0. The canton labels are long left-aligned runs —
`Appenzell Rh.-Ext.`, `Bâle-Campagne`, `Saint-Gall` — and a long run's centre can fall **right**
of col 0's boundary, landing in col 1 where it displaces or fuses with that row's first data
value. **That is the concrete failure mode § 3d's sample was structurally unable to show**, and
it is named here before the probe runs so that finding it is a prediction met and not finding
it is a prediction refuted.

### 1c. Source truth, and why it is independent

Truth is `line.words` sorted by `x0` — the raw extraction the pipeline itself saw, carrying
**no column decision**. The independence that matters is from the column decision, not from word
extraction. Corroborated independently by a direct `pdfplumber.extract_words()` dump of page 5,
whose 27 canton lines run `Suisse` (top 383.0) to `Jura` (top 606.2), each complete from
x0 ≈ 72.2 to x1 ≈ 522.7, plus 19 T1 year rows — **46 admitted rows, matching § 3d's count.**

### 1d. The three checks, threshold-free and total

| # | Check | Passes when |
| --- | --- | --- |
| **C1** | **Reconstruction.** Concatenate the emitted cell texts in column order. | The result reproduces the line's own word sequence **exactly**. Subsumes label identity: a label in the wrong column, or a name split across col 0 / col 1, is a sequence mismatch. |
| **C2** | **Edges.** | Col 0 carries the line's leading ink; the last column its trailing ink. |
| **C3** | **Pairing.** | Each canton row's emitted label is **that row's own** canton name, and its final cell **that row's own** `en %` value. |

A canton row is identified **structurally** — an admitted row whose leading word is non-numeric
— not from a curated list. The 19 year rows are printed rather than discarded.

### 1e. Controls — if any fails, the verdict is VOID

| # | Control | Must read |
| --- | --- | --- |
| **P** | **Positive.** Reproduce § 3d. | Under `alignment`: 12 columns, 46 rows, **496** placed cells, col 0 and col 11 full at **46/46**. A probe that cannot reproduce the figure it is auditing is at the wrong seam. |
| **U** | **Universe null.** | Under the shipped `decoration` universe the same probe reads col 0 at **18** cells holding DATA values, not labels. A probe blind to the difference between universes is measuring itself. |
| **S** | **Shift null.** Pair row *i*'s emitted cells against row *i+1*'s source words. | **Mismatches on essentially every canton row.** This is the one that earns the verdict: a clean 27/27 is self-validating unless the checker can be shown to FAIL on a pairing known to be broken. |

Control S is the load-bearing one, for the reason this repo has now paid for three times
(`r235` v1's self-validating census; `r234`'s *"a null result is not self-validating"`;
PR #236's centre-key control that was inert until a null ran).

### 1f. The PREDICTION, registered before the data exists

**P and U pass; C1–C3 pass on the short canton names; the open question is the long ones.**
Stated sharply so it can be wrong: if any canton row fails, the most likely failures are
`Appenzell Rh.-Ext.`, `Appenzell Rh.-Int.`, `Bâle-Campagne` and `Saint-Gall`, and the failure
shape is **col 0 empty or truncated with the name's tail fused into col 1**, not a label paired
with the wrong row's values — the label and the values come from one `line` object, so a
cross-row mis-pairing is not structurally available on this page.

**A distinction the run must not blur:** the T1 year rows are **split across source lines** (the
`État de la population` pair sits on its own line at x 136–460 for most years), so those lines
are not whole source rows and a C1 failure there means something different from a C1 failure on
a canton row. They are reported separately.

**Expected in passing, not a failure:** `absorb_unit_markers` drops footnote marker glyphs (the
superscript `1`/`2`/`3` at x ≈ 71–88), so a reconstruction may legitimately lack a marker word.
Named here so it cannot be reported afterwards as an explanation.

### 1g. What this loop will NOT do with the result

**Record it, not design against it.** The ruling defers R240 and the scope classification
explicitly. If identity holds, scope becomes the live question and it is the maintainer's
(CLAUDE.md § 8). If identity fails, the +92 headline is **withdrawn** and the subject returns to
column identity — and that, too, is recorded rather than repaired here.

### 1h. The falsifier, both ways

- **Identity holds** → the switch's value stands as measured; scope becomes the live question.
- **Identity fails** → [[R238]]'s symptom is *not* fixed by refusing decoration, the +92 headline
  is withdrawn, and the switch would assert unsupported facts (§ 7) rather than carry cells.

---

## 2. The instrument

`scripts/r238_label_identity.py` — § 8 class **PROCEDURAL**: it runs shipped derivations over a
shipped input and prints the comparison; it decides nothing, carries no threshold and no
tolerance, and changes no shipped file. It reuses PR #239's patch mechanism
(`_boundaries_from_decoration` returns `None`), whose reach into the compile path was measured
at `d653036` and proven by that loop's null control.

    PYTHONPATH=src:. .venv/bin/python scripts/r238_label_identity.py

## 3. Results

**NOT YET RUN.** This section is written after § 1 is committed.
