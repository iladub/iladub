# Spec — the tightest certain boundary: a wrap is tighter than every row boundary the band certifies

**Residue:** [[R208]] (`docs/superpowers/residues-open.md`, cause located 2026-09-10).
**Question inherited:** `docs/superpowers/2026-09-10-the-weld-is-noise-handoff.md` § 5a, graded
PROPOSED — *replace `gap < lead` at equality with a derivation, in a spec.*
**Written 2026-09-10**, off `d8041d8` (branch `r208-the-weld-is-noise`, PR #194, still open —
this branch is stacked on it), branch `r208-the-tightest-certain-boundary`. Written under the
originating floor (~50K working tokens at the time of writing).

**Doc impact: none.** No published term changes. No wiki or site page states the wrap-continuation
rule (`grep -rln "wrap-continuation\|group_wrapped" docs/wiki docs/*.md mkdocs.yml` is empty); the
B3 spec that does is Evidence and append-only, and its § 3 claim is corrected by this spec, not in
place.

---

## 1. The subject, reproduced at HEAD

`src/iladub/etkl/cells.py`, `group_wrapped`: a partial line (subset of the anchor's open columns,
fewer columns, no author hrule between) is absorbed into the line above iff `gap < lead`, where
`lead` is the median of the band's inter-line gaps. On graincorp-stem every body gap is 6.48 pt, so
the median IS the pitch, and each at-pitch partial line — a data row whose month column the author
left blank — is decided by the fifth decimal. `scripts/at_pitch_weld_probe.py` at `d8041d8`, p1
band 1 (`lead = 6.4800105`):

```
line  3->4  gap=6.480000000000018  gap-lead=-1.05e-05  WELDS   Mackay 60954 BUNGE …
line 25->26 gap=6.479987999999992  gap-lead=-2.25e-05  WELDS   Mackay 59847 GCOP …
line 39->40 gap=6.480010499999935  gap-lead=+0.00e+00  row     Mackay 59849 GCOP …
line 50->51 gap=6.4799880000000485 gap-lead=-2.25e-05  WELDS   Mackay 59852 GCOP …
line 60->61 gap=6.480011249999961  gap-lead=+7.50e-07  row     Mackay 59854 GCOP …
line 73->74 gap=6.480011249999961  gap-lead=+7.50e-07  row     Portland 59704 GCOP …
line 77->78 gap=6.480011249999961  gap-lead=+7.50e-07  row     Portland 59912 CARG …
```

The same instrument run over **every band of every corpus document** (the run is transcribed in
§ 7; the script is the probe extended to enumerate the certain pairs) finds the whole candidate
population: **30 partial-line candidates in 4 of 7 documents** — graincorp-stem 15 (p0 2, p1 7,
p2 6), apple 8, bfs 5, ons 2; cbh-stem, graincorp-capacity and who have none. `gap < lead` welds
**8** of them: the 6 graincorp at-pitch data rows (all wrong — R208's 22 joined-row refusals), 1
bfs header wrap and 1 ons footnote wrap (both genuine).

## 2. Why no constant, and why the source's own precision does not help either

**The noise is in the source, not in Python.** graincorp-stem's content stream states its text
matrices to six decimals, and the jitter is in the sixth: the raw `Tm` ty operands read
`90.879997`, `82.080002`, `73.279999` — single-precision round-off the generator wrote into the file
around a 2-decimal grid. After the page's `0.750000 … cm` scaling they become the word tops
`71.31424202250003 / 77.79424202250004 / 84.27424127249998` the probe prints. So the handoff's
second candidate derivation — *round to the precision the source states* — is **REFUTED by
measurement**: the source states 6 decimals (`distinct decimals in ty: [6]`, 225 of 225 operands)
and the disagreement between at-pitch gaps is ~2e-5 pt, *above* that resolution. Rounding to the
stated precision leaves every one of the seven decisions where it is. Inferring that the generator
used float32 and rounding to *that* quantum would be a hypothesis about the author's tool, not a
statement the source makes — and a constant by another name.

**A tolerance is the tuned constant CLAUDE.md § 8 forbids**, and the predecessor's spike
(`round(·, 2)` on both sides) was run to measure blast radius, not to ship. Its figures are the
reproduction target in § 6.

**B3's third candidate — a distribution-aware bimodal split** (`specs/2026-07-22-b3-…` § 3) — has
nothing to split here: on graincorp-stem all 79 gaps of p1 band 1 lie within 0.85 pt and 77 of them
within 5e-5 pt of one value. The at-pitch candidates ARE the pitch cluster. A split would need a
cluster-count or bandwidth decision, which is a constant. Not adopted.

## 3. The derivation — the tightest certain boundary

Conditions 2 and 3 are sound: a line that is *not* a subset partial of the line above it — it tiles
as many columns, or a column the previous line left closed, or an author hrule lies between — is a
**row boundary by construction**. Those pairs need no gap to be decided, so their gaps are
*measurements of what a row boundary looks like in this band*, made by the same instrument on the
same page with the same noise. Call them the **certain pairs**.

**The rule.** A candidate line continues the line above iff

```
gap < tightest_row_gap        where  tightest_row_gap = min(gap over the band's certain pairs)
```

— a wrap must be **tighter than every row boundary the band certifies**. That is the
evidence-positive reading § 8 asks for: a merge is asserted only when there is positive evidence the
gap is *not* a row gap, and a gap that is indistinguishable from an observed row boundary is a row.
Under `gap < lead` the same candidate was asserted a wrap whenever it was tighter than the *typical*
row, which at uniform pitch is a coin flip on noise.

**Measured, not reasoned** (§ 7): on graincorp-stem p1 band 1 the certain pairs number 72, their
gaps span `[6.479965, 7.320001]`, and every candidate gap is ≥ 6.479988, so **all 7 are refused**;
p2 band 1: 64 certain, 6 candidates, 0 welded; p0 band 2: 2 candidates, 0 welded. The pair carrying
the minimum is a full data row (`line 62->63: Gladstone 59771 …`), so the handoff's § 4 assumption
that the minimum lies on a certain pair is confirmed. The four B3 pins hold unchanged (certain pairs
at exactly 20: gaps 5 and 19 merge, 20 does not, a tight full row never does), and the strict-xfail
detector **passes** (`noisy at pitch: pitch_min=19.99999, weld=0`).

**Where the band has no certain pair** — every line a subset partial of the one above, so the band
certifies no row boundary at all — the rule has no minimum to take. **Decision: fall back to `lead`**,
B3's rule. Rationale: with no certified boundary the median is a comparison *among candidates* —
"tighter than the typical gap between these partial lines" — and that is the only evidence the band
offers. Measured: exactly 3 corpus bands have this shape (bfs p0 b0, p6 b1, p6 b2 — two- to
four-line header blocks), and the fallback leaves each of their 5 candidates where `gap < lead` had
them (1 welded, a header wrap). The alternative — refuse every candidate when nothing is certified —
was **not run**; its known cost is that bfs p6 b2's genuine three-line header wrap becomes three rows
and bfs's graph hash moves. Recorded as the one arm of this design that a later loop may reverse.

**Certain pairs are consecutive lines, not anchor-relative.** The loop's own structural test compares
line j to the *anchor's accumulated* columns (`merged_into[i]`); the certain set is defined on raw
consecutive pairs (j-1, j) and enumerated once before the loop, so the threshold is a property of the
band, not of the loop's state. The hrule veto counts as certification: a vetoed pair is an
author-drawn row boundary and its gap enters the minimum.

### § 8 gate classification — PROCEDURAL, inherited from B3 § 2, on the same argument

`tightest_row_gap` is a derived statistic of the band (a minimum over a structurally-defined
population), as `lead` was (a median over the band's gaps). It carries no constant, no tolerance and
no tuned margin; the comparison stays strict. It is not AXIOM because no evidence graph exists at
this point of the pipeline — `group_wrapped` runs on `Line`s before `classifygraph` mints a triple —
and it is not NEURAL because the question is not "which columns does X span" but "is this gap a row
gap", which the band's own certain pairs answer exactly. The code comment must say this.

## 4. The honest limits — stated before they are measured, two of them, both visible

**(a) A minimum is not jitter-robust where a median is.** In a band whose rows are genuinely
irregular, one tight certified boundary refuses every genuine wrap just under it: a wrap with gap in
`[tightest_row_gap, lead)` that `gap < lead` accepted is now refused. This is the handoff's known
cost. Measured over the corpus: **0** of the 30 candidates lie in that interval (apple's 8 sit at
27.9-28.6 pt against a lead of 14.16; ons's genuine wrap at 11.76 sits under a `tightest_row_gap` of
25.68; bfs's 5 are in fallback bands). No corpus document has the shape; that is not evidence of
absence. **Direction of the residual:** a refused wrap is a partial row with blank cells — visible to
tiling and to the placement instrument as a suppressed-key row. A wrongly accepted wrap is R208: two
records fused into one that passes tiling and reaches the grounded graph. B3 § 3 claimed the
round-trip backstop escalates a mis-merge; the predecessor refuted that. The residual now sits on
the side the membrane can see.

**(b) At uniform pitch, the rule still has a noise floor — one order of magnitude lower.** An
at-pitch candidate welds iff its gap is the *tightest of every gap in the band*: under exchangeable
noise that is one chance in `n_certain + 1` per candidate — 1 in 73 on graincorp p1 — where
`gap < lead` was one in two (6 of 13 welded). On the corpus the margin is 2.3e-5 pt (candidates ≥
6.479988, certain minimum 6.479965). This is a **residual, not a silent class**, and it is only ever
reachable when the source's own coordinates disagree below its stated precision (§ 2). The docstring
records it; no xfail pins it, because nothing on record is planned to close it.

## 5. Change contract (interfaces and oracles — no bodies)

- **`cells.group_wrapped`** — add the certain-pair enumeration and `tightest_row_gap`; the `while`
  gate compares against it, falling back to `lead` when the certain set is empty. Retire the
  docstring's "accepted jitter tradeoff" paragraph and state § 3 and § 4 in its place. Invariants:
  strict `<`; hrule veto unchanged; conditions 2/3 unchanged; a band with no certain pair behaves
  byte-identically to `d8041d8`.
- **`scripts/at_pitch_weld_probe.py`** — print the certain-pair count, `tightest_row_gap`, and per
  candidate both verdicts, so § 7 is reproducible in one command.
- **`tests/etkl/test_wrap_continuation.py`** — remove the strict `xfail` marker on
  `test_at_pitch_partial_line_under_coordinate_noise_is_still_not_merged` (it passes); keep the four
  B3 pins. Add, verbatim or equivalent, with falsification evidence per rule 4:
  - **T1 fallback** — a band with no certain pair (every line a strict subset of the one above),
    gaps tighter and looser than the median: the tighter merges, the looser does not — byte-identical
    to the B3 rule.
  - **T2 hrule certifies** — a band whose only certain pair is hrule-vetoed at a gap tighter than the
    median; a candidate between that gap and the median is refused.
  - **T3 the disclosed cost** — a certified boundary tighter than the body pitch, a candidate between
    them: refused. Pinned as *intended*, so the limit in § 4(a) is a test, not a comment.
- **Oracles**, all at the branch's HEAD versus `d8041d8`:
  - O1 the probe on graincorp p1 band 1: `welded 0` of 7.
  - O2 `scripts/corpus_verdict_snapshot.py`: six graph hashes unchanged; graincorp-stem p1 **77**
    leaf rows, p2 **68** (the spike's figures, without the spike's constant).
  - O3 `scripts/placement_population.py` on graincorp-stem: exact-refused **24** (from 48);
    `cellText` values whose first and last token repeat: **0** (from 56).
  - O4 falsification: with the gate reverted to `gap < lead`, the detector and T2/T3 fail, T1 and
    the four B3 pins still pass.

## 6. What is NOT done

- The chained-anchor case (line j+1 welding onto an already-fused anchor) is unchanged in form; it
  inherits the new threshold. Not separately pinned.
- The refuse-when-nothing-certified arm (§ 3) is named, costed, not run.
- The § 4(b) residual is stated, not closed; nothing on record closes it without a constant.
- R208 does not close in this spec. It closes when § 5's O1-O4 are green on a merged branch; the
  register row records this spec as the next measurement.
- The B3 spec is not edited (Evidence, append-only); its § 3 backstop claim stays refuted on record
  in R208's row and the predecessor's handoff.

## 7. The measurement this spec rests on (2026-09-10, `d8041d8`, corpus populated)

Instrument: the probe extended to enumerate certain pairs and print both verdicts, over
`corpus/*/*.pdf`, every page, every band with ≥ 1 candidate. Bands with no candidate are omitted.

```
graincorp-stem p0 b2: lines=61 lead=6.480000 pitch_min=6.479965 certain=58 cands=2 weld<lead=0 weld<pitch_min=0
graincorp-stem p1 b1: lines=80 lead=6.480010 pitch_min=6.479965 certain=72 cands=7 weld<lead=3 weld<pitch_min=0
graincorp-stem p2 b1: lines=71 lead=6.480000 pitch_min=6.479965 certain=64 cands=6 weld<lead=3 weld<pitch_min=0
apple          p0 b2: lines=41 lead=14.160000 pitch_min=8.64 certain=36 cands=4 weld<lead=0 weld<pitch_min=0
apple          p1 b2: lines=40 lead=14.160000 pitch_min=8.64 certain=35 cands=4 weld<lead=0 weld<pitch_min=0
bfs            p0 b0: lines=2  lead=20.533780 pitch_min=None certain=0 cands=1 weld<lead=0 (fallback)
bfs            p5 b2: lines=3  lead=6.441974 pitch_min=5.974647 certain=1 cands=1 weld<lead=0 weld<pitch_min=0
bfs            p6 b1: lines=2  lead=12.237120 pitch_min=None certain=0 cands=1 weld<lead=0 (fallback)
bfs            p6 b2: lines=4  lead=8.603400 pitch_min=None certain=0 cands=3 weld<lead=1 (fallback)
ons            p4 b0: lines=32 lead=20.640000 pitch_min=11.76 certain=30 cands=1 weld<lead=0 weld<pitch_min=0
ons            p4 b2: lines=3  lead=18.720000 pitch_min=25.68 certain=1 cands=1 weld<lead=1 weld<pitch_min=1
B3 fixtures: sub 5 → merge/merge; sub 19 → merge/merge; sub 20 → row/row; full tight → no candidate;
             noisy at pitch (the detector) → weld<lead=1, weld<pitch_min=0
```

graincorp p1 band 1, distinct certain gaps (count): 6.479965 (3), 6.479988 (7), 6.479989 (3),
6.479999 (7), 6.48 (3), 6.48001 (5), 6.480011 (21), 6.599996 (1), 6.600002 (1), 7.320001 (1).
Source precision: `cm` = `0.750000 0.000000 0.000000 -0.750000 0.000000 595.320007`; 225 `Tm`
operators on p1, every ty stated to 6 decimals.

**What would refute this spec:** a corpus document, or a synthetic band drawn from a real generator,
whose genuine wraps sit between the tightest certified boundary and the median — § 4(a)'s interval,
empty on this corpus. The plan's O2 (six hashes unchanged) is the first place it would show.
