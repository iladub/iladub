# Handoff — R253's prediction is run; what is left is a measurement, not a remedy

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]]'s row.

**Topic:** [[R253]]'s prediction was run offline and live. Offline it **holds**; live, the disposal
turns out **unreliable rather than blocked** — 6 of 9 readings carry 107–110 with no `spanned` set
at all, 3 fail, and 2 of 5 full compiles reach the graph. R253's recorded figure **reproduces** as
one of three regimes, so the row stays **open, amended**. [[R255]] is raised. Nothing in `src/`,
`vocab/`, `baml_src/` or `tests/` changed.

**Date:** 2026-09-18. **Branch:** `r253-the-grain-of-the-ask`, cut from `main` at `cb3a266`.

**Doc impact: none.**

---

## 5. The next concrete action — **PROPOSED**, and the cheap half is ASSERTED

*(Part 5 first, per CLAUDE.md § "The handoff's next action is TYPED". Parts 1–4 are pointers and
records and follow below.)*

### 5a. **ASSERTED** — capture what regime (iii) actually returns. Mechanical, ~15 minutes.

**The action:** re-run `scripts/unshown_ink_live_oracle.py` until a `|A| = 0` reading appears, and
capture the `note` field and the raw BAML response beside it. The oracle already prints `note`; the
failing runs were taken through a `grep` that dropped it, and through a traced compile that never
printed it. **Nothing needs designing** — this is a print statement and patience.

Why it is asserted: the outcome is unknown but *doing it* is the work, and it is the one fact every
candidate remedy for [[R253]] depends on. Regime (iii) is 2 of 9 readings and its cause is
**unestablished**: truncation is available as an explanation (the client is at `max_tokens 16000`; a
good 110-address answer used 3198 output tokens) but is **not evidenced**. Also capture compile E's
traceback — it aborted before band 3 and the traceback was filtered by the invoking `grep`, so a
suspected fourth regime is recorded as unmeasured.

**Do not name a remedy before this is captured.** Naming one first is precisely what [[R253]] did,
and § 8 of the evidence is what that cost.

### 5b. **PROPOSED** — does deleting the span clause reduce regime (ii)?

**The prediction:** the span clause causes regime (ii) (`|A| = 110`, the 26 empty places withheld,
control fails, 110 addresses discarded), and a place-grain ask reduces its frequency.

**Measured support, and it is thin:** regime (ii) is the clause **being obeyed**, which is mechanism,
not correlation. Against that, the rephrased ask was run **twice** (both 26/26, disposing 107 and
110) versus **nine** readings of the shipped one. **n = 2 against n = 9 settles nothing** about a
reader that fails 3 in 9, which is why the rephrasing was written, run, and **not committed**.

**Why it is PROPOSED:** the effect size needed is a change in a failure rate that is itself not
established (§ 10 of the evidence: 3 in 9 is an observation, not a rate, on one crop of one
document). A loop that ships the rephrasing on two readings is repeating this loop's own near-miss.
**Run both asks enough times to separate them before changing anything**, and decide the sample size
before looking. If the two are indistinguishable, the clause is not worth touching and [[R253]]'s
remedy lies in regime (iii) instead.

**What NOT to do.** Do not add a retry loop while regime (iii)'s cause is unknown — a retry hides a
cause. Do not merge two readings under any name: `unshownink.py`'s module docstring forbids union,
intersection and vote, and there is deliberately no API for it. Do not spend the one geometric
attempt deriving a `spanned` set: **arm 1 and § 2 of the evidence show `spanned` could never have
protected an assertion** (the disagreement intersects `has_glyph`), so a span derivation buys only
the control, and on 6 of 9 readings the reader supplies the control itself.

---

## 1. Where the primaries are

| | |
| --- | --- |
| evidence | `docs/superpowers/2026-09-18-the-grain-of-the-ask-evidence.md` — **every figure with its command**; § 7 is the reading table, § 9 the regimes |
| instruments | `scripts/unshown_ink_grain_control.py` (4 offline arms, 2 null, one process each), `scripts/unshown_ink_live_oracle.py` (O8; raw recall/control independent of `dispose`) |
| the row | [[R253]] in `residues.md` — **open, amended**, not closed |
| raised | [[R255]] in `residues.md` + `residues-open.md` |
| the shipped subject | `src/iladub/etkl/unshownink.py` (`dispose`, `region_unshown`), `baml_src/unshown_ink.baml` (the ask), `src/iladub/etkl/compile.py:485-505` (the gated wiring) |
| prior spec | `docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md` — **§ 8 governs** |

**No spec ships from this loop.** One was written and is not committed; the evidence § 8 records what
it claimed and why it is unsettled rather than refuted.

## 2. What was decided, and where it is recorded

- **R253 stays OPEN and is amended, not closed** — recorded in `residues.md`'s R253 row. Its symptom
  reproduces (regime ii) while its explanation (*"nothing in the pipeline can supply that set"*) is
  beside the point, because on 6 of 9 readings nothing has to.
- **The rephrased ask is not committed** — recorded in the evidence § 8 and in R253's amendment. The
  reason is sample size, not a refuted mechanism. **This decision is recorded nowhere else**, so it
  is reversible: a loop with adequate n may take it straight back up.
- **`spanned` was NOT removed**, even though no production caller supplies it and one test pins it.
  Removing it is a defensible cleanup that this loop deliberately did not bundle with an unsettled
  design question. Recorded here only — also reversible.
- **Every observed failure is fail-closed** — recorded in the evidence § 9, with the note that
  regimes (ii) and (iii) cost *facts*, never *truth*.

## 3. What is UNVERIFIED, and must not be asserted

- **Regime (iii)'s cause** (`|A| = 0`, `refuses_grid=False`) — unestablished. Truncation is a
  suspect, not a finding.
- **Regime (iv)** — compile E aborted before band 3; the traceback is **not captured**. Do not assume
  it is the same as (iii).
- **All frequencies.** 3 of 9 readings, 2 zeros and 1 abort in 5 compiles, one crop, one document,
  one session. **Not rates.** Do not quote them as rates, including in a spec's motivation.
- **The rephrasing's effect** — two readings. Unmeasured, in both directions.
- **[[R252]] is untouched**: the address spaces still disagree on six of seven documents, so no claim
  of corpus reach is available from this loop.
- **[[R254]] is untouched**: the over-reporting reader remains unguarded, and nothing here detects it.
- **No score movement.** Every arm and compile reports `score=1.0000`; the score is blind to cell
  carriage ([[R240]]).
- **Why there are two `page_bands` call sites** — located, never explained. That is [[R255]].

## 4. Traps this loop paid for

1. **A conclusion drawn at six readings of a non-deterministic reader was wrong at nine.** The first
   draft of the evidence concluded R253 was flatly refuted and would have closed the row. Two more
   traced runs — the cheapest control there is, and one not in the spec's oracle list — reversed it.
   **When the subject is a model's answer, more samples of the same thing is a control.**
2. **A control can pass and still settle nothing.** Three shipped-ask readings scoring 26/26 looked
   like a refutation of the span-clause mechanism; row 9 is that clause being obeyed. A passing
   control bounds nothing unless its n is stated against the failure rate it must separate.
3. **`dispose` collapses two regimes into one figure** — it returns the empty set on any refusal, so
   *"the ask made the reader withhold"* and *"the reader found nothing"* are the same output. The
   oracle now prints raw recall and raw control independently for exactly this reason.
4. **An instrument sharing one interpreter across arms fabricated a finding** — arm 3 reported
   `[110, 0]` from one reading and one spanned set. One process per arm; `main()` re-execs itself.
5. **A `grep` on a live run drops the evidence you will want.** Both `|A| = 0` runs lost their `note`,
   and compile E lost its traceback. Tee the full output to a file, then grep the file.
6. **`baml_client` is generated at the repo root**, so a script under `scripts/` must put the repo
   root on `sys.path` or `baml_reader_available()` returns False and the oracle reports NOT RUN —
   which reads exactly like a missing API key.
7. **The prompt was restored with a scripted edit against a `cp` backup, never `git checkout`** — the
   trap recorded in the previous handoff, honoured here.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
