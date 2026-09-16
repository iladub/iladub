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

## 3. Results — identity HOLDS, 27 of 27 canton rows

**The 92 cells are the right cells.** Every canton row's col-0 label is **that row's own** canton
name and its col-11 value **that row's own** `en %`, and the total reconstruction is exact.

### 3a. The controls — all three pass

```
### CONTROL P — reproduce PR #239 § 3d under alignment
    12c/46r/496 cells, c0=46, c11=46  -> PASS
### CONTROL U — the probe distinguishes the two universes
    decoration c0=18 vs alignment c0=46  -> PASS
### CONTROL S — a deliberately broken pairing must FAIL
    shift null: 0 pass, 27 fail  -> PASS
```

**Control S is what earns the verdict**, and it earned it: pairing row *i*'s emitted cells
against row *i+1*'s source words drives **C1 to 0/27**. The checker can fail, so its passing
means something.

**One detail of S worth keeping, because it shows why C1 and not C3 is load-bearing:** under the
shift, **C3 still passes 2 of 27** — line 38 (`Schwyz`, last `1.5`) against `Obwald`'s `1.5`, and
line 44 (`Soleure`, last `1.6`) against `Bâle-Ville`'s `1.6`. Adjacent cantons can share a growth
rate, so a final-cell check alone would have called a knowingly broken pairing correct twice. The
total sequence check does not have that weakness.

### 3b. The two universes, side by side

```
=== universe=decoration: 15c 46r, 404 placed cells
    col fill: c0:18  c1:46  c2:27  c3:19  c4:27  c5:19  c6:46  c7:46  c8:21
              c9:25  c10:19 c11:27 c12:18 c13:27 c14:19
    col 0 sample: ['7 415 102', '7 459 128', '7 508 739', '7 593 494']   <- DATA, not labels
=== universe=alignment: 12c 46r, 496 placed cells
    col fill: c0:46  c1:45  c2:38  c3:27  c4:46  c5:46  c6:46  c7:46  c8:46
              c9:18  c10:46 c11:46
    col 0 sample: ['2005', '2006', '2007', '2008']
```

### 3c. The verdict, per row class

| | C1 reconstruction | C2 *as pre-registered* | C2' amended | C3 | C3' |
| --- | --- | --- | --- | --- | --- |
| **27 canton rows** | **27/27** | 24/27 | **27/27** | 27/27 | 27/27 |
| **19 year rows (T1)** | **19/19** | 17/19 | **19/19** | 19/19 | 19/19 |

C1 is exact word-sequence equality against `line.words` — every word, in order, no loss, no
duplication, no reordering. On all 46 admitted rows it holds.

### 3d. C2 AS PRE-REGISTERED WAS MIS-SPECIFIED — reported, not quietly replaced

The three canton "failures" are **not** identity failures, and the run makes that unambiguous
because C1 passed on every one of them:

```
line 33  C1ok C2FAIL C2'ok C3ok  label='Suisse 3'            truth[0]='Suisse'
line 48  C1ok C2FAIL C2'ok C3ok  label='Appenzell Rh.-Ext.'  truth[0]='Appenzell'
line 49  C1ok C2FAIL C2'ok C3ok  label='Appenzell Rh.-Int.'  truth[0]='Appenzell'
```

C2 compared a **cell** against the line's first **word**, but a cell legitimately holds a
multi-word run. The cells are correct; the check was wrong. C2' is the threshold-free repair —
the col-0 cell's words must be a **prefix** of the line's word sequence, the last cell's a
**suffix** — and it reads 27/27.

**Both forms stay in the instrument's output and in the table above.** Amending a check after
seeing the numbers is precisely how a refuted claim gets rescued (PR #238 § 5's own lesson), and
the only defence available is showing the original verdict beside the amended one.

### 3e. THE PRE-REGISTERED PREDICTION IS REFUTED — right rows, wrong reason

§ 1f predicted that if any canton row failed, it would be a long name — `Appenzell Rh.-Ext.`,
`Appenzell Rh.-Int.`, `Bâle-Campagne`, `Saint-Gall` — whose run centre falls right of col 0's
boundary, **truncated with its tail fused into col 1**.

**That did not happen.** The long names are carried **whole** in col 0: `'Appenzell Rh.-Ext.'`
is one cell, and `Bâle-Campagne` and `Saint-Gall` pass every check including the
pre-registered C2. Two of the four names I named did flag — **for the checker's defect, not the
placement's**. The prediction picked the right rows by the wrong mechanism, which is a refutation
and is recorded as one rather than claimed as a hit.

§ 1f's second expectation is **also refuted, in the opposite direction**: it said
`absorb_unit_markers` may **drop** footnote marker glyphs. Measured, they are **kept and fused
into the label cell** — `'Suisse 3'`, `'2010 2'`, `'2011 3'`. Raised as [[R242]].

### 3f. What this does NOT establish — the column semantics are a different question

C1 proves the **row-wise** reconstruction: every word lands in some column, in source order. It
does **not** prove the interior column **boundaries are semantically right** — that the value in
col 4 sits under *Naissances vivantes* rather than its neighbour. *"Whether alignment's 12
columns are the RIGHT 12"* remains open, exactly as PR #237 and PR #239 left it.

And the fills above show why that question is sharper than it looked: **col 3 is filled by the 27
canton rows only and col 9 by 18 year rows only.** One 12-column universe spans **two different
tables** — T1 (19 year rows) and T2 (27 canton rows) — so a column index means different things
depending on which table the row belongs to. This **pre-exists the switch** (46 rows under both
universes) and is not caused by it. Raised as [[R241]].

## 4. What this loop did NOT do

Per § 1g and the ruling: no remedy designed, no scope ruled, [[R240]] untouched. The switch is
still **unbuilt** — `_boundaries_from_decoration` is patched by an instrument, not changed in
shipped code — so [[R238]] stays **open**.
