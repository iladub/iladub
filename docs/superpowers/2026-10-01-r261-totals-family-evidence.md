# Evidence — R261 totals family, Task 0: baseline and census (2026-10-01)

**Serves:** prog:criterion:etkl:03 — cbh is the unaccepted document whose one live escalation is
the totals family; this evidence is the "before" state Task 6's C2 diffs against, and the census
Task 3's binding rule is written from.

**Topic:** r261-totals-family · **Date:** 2026-10-01 · **Branch:** `r261-totals` · **HEAD measured:**
`bac0f81`.

**Doc impact: none.** Measurement only; no published term changes.

Plan: `docs/superpowers/plans/2026-10-01-r261-totals-family.md` (shared context + Task 0 brief
under `.superpowers/sdd/2026-10-01-r261-totals-family/`). Spec:
`docs/superpowers/specs/2026-10-01-r261-totals-family-design.md`.

This task is MEASUREMENT ONLY: no `src/` change.

---

## § 1. Baseline, recorded before any `src/` change

### 1.1 Step 1 — whole-corpus canonical-hash snapshot (Task 6 C2's "before")

Instrument: `scripts/r261_baseline.py --baseline`, run serially (nothing else running at the
time), one process. For each document: `compile_document(pdf)`, then
`rdflib.compare.to_canonical_graph(report.graph)`, sha256 over the sorted N-Triples of the
canonicalised graph, plus the raw triple count and the score.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python scripts/r261_baseline.py --baseline
```

Output:

| document | score | triples | sha256(canonical NT) |
|---|---|---|---|
| cbh-stem-2026-08-03 | 0.9103232533889468 | 13427 | `f1f7cc6ac43fe62199900160d482d4f6909166300503b4779c56fb9bad136618` |
| graincorp-capacity-2026-08-04 | 1.0 | 5859 | `4a7ffe8598fdb5d2b69f8e98cb228f85ea254132a62c2565ff4b1f0532984f68` |
| graincorp-stem-2026-07-31 | 0.9995511669658886 | 32422 | `96436660c468a30fc92a7c14af95e8d25dc4dd1bf8b71054c7dc1e616bb3375f` |
| apple-fy2026q3-statements | 0.9418604651162791 | 6255 | `f8c56e57e59947631d27def1caedaf6591683965af67abbd9dd3e01aeaee8bfc` |
| bfs-population-bilan-2023 | 0.9021428571428571 | 16778 | `4a176ec3138f99cbcd61db4c736a4fb834ba226e2d6e0aeea5d1616c358a225a` |
| ons-index-of-services-2026-02 | 0.8684895833333334 | 12454 | `4847d19fbd326488078653dbe1373d6f4d9634359b869f8b77eb6c319b336c08` |
| who-wfa-boys-zscore-0-5 | 0.9962779156327544 | 12274 | `7931db4b52d368bf32338c5e6773e3c47f79e33919b948e6ea2dd8c7fe41ea18` |

All 7 hashes are 64 hex characters (verified: `echo -n "<hash>" | wc -c` → 64 on the first row).
This is the 7-document population named by `tests/corpus-manifest.ttl`'s `cor:file` entries
(`ag-trade/graincorp-stem-2026-07-31.pdf`, `ag-trade/graincorp-capacity-2026-08-04.pdf`,
`ag-trade/cbh-stem-2026-08-03.pdf`, `gov-stats/ons-index-of-services-2026-02.pdf`,
`gov-stats/bfs-population-bilan-2023.pdf`, `financial/apple-fy2026q3-statements.pdf`,
`health/who-wfa-boys-zscore-0-5.pdf`).

**Not identical to `docs/superpowers/2026-09-28-box-split-evidence.md` § 1.1's figures** (older
commit, different branch history): cbh's triple count moved 12839 → 13427 and several other
documents' triple counts moved by tens, between 2026-09-28 and this branch's tip. That is
expected drift from loops landed in between; it is recorded here only so a future reader does not
mistake the two snapshots for the same measurement.

### 1.2 cbh p0's per-band `RegionReport` (for Task 6)

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python3 -c "
import sys; sys.path.insert(0,'src')
from iladub.etkl.document import compile_document
import glob
path = glob.glob('corpus/**/cbh*.pdf', recursive=True)[0]
rep = compile_document(path, validate_shapes=False)
prep = rep.pages[0]
for i, r in enumerate(prep.regions):
    print(i, r.kind, r.verdict, r.cells, r.tokens_asserted, r.tokens_escalated, r.table_uri)
"
```

| idx | kind | verdict | cells | tok_asserted | tok_escalated | table_uri |
|---|---|---|---|---|---|---|
| 0 | NON_TABLE | ignored | 0 | 0 | 0 | — |
| 1 | UNSUPPORTED_TABLE | asserted | 170 | 190 | 0 | `…/p0/r2#htable1` |
| 2 | NON_TABLE | ignored | 0 | 0 | 0 | — |
| 3 | UNSUPPORTED_TABLE | asserted | 268 | 288 | 0 | `…/p0/r2#htable3` |
| 4 | NON_TABLE | ignored | 0 | 0 | 0 | — |
| 5 | UNSUPPORTED_TABLE | asserted | 228 | 248 | 0 | `…/p0/r2#htable5` |
| 6 | NON_TABLE | ignored | 0 | 0 | 0 | — |
| 7 | UNSUPPORTED_TABLE | asserted | 84 | 104 | 0 | `…/p0/r2#htable7` |
| 8 | NON_TABLE | ignored | 0 | 0 | 0 | — |
| 9 | UNSUPPORTED_TABLE | **escalated** | 0 | 0 | 86 | None |
| 10 | RECORD_TABLE | asserted | 28 | 35 | 0 | `…/p0#table10` |
| 11 | RECORD_TABLE | asserted | 8 | 8 | 0 | `…/p0#table11` |

Bands 2/4/6/8 (the four port-total lines) are `NON_TABLE` → ignored, booking 0/0 — this confirms
the handoff's Addendum 1 P2 table (same bands, same kinds), now measured at this branch's HEAD and
extended to band 11, which Addendum 1's table did not reach. Band 9 is the sole live escalation
(0 asserted / 86 escalated, `table_uri None`) — the "one live escalation" this criterion names.

---

## § 2. The census under the production rule (Step 2)

**Instrument:** `scripts/r261_baseline.py --census`, new this task, built on the probe's
graph-reading approach (`tab:hasCell` → `tab:atColumn` + `tab:cellText`, same population filter
as `scripts/section_total_fp_census.py`: asserted non-grid table regions with a following band)
but substituting **M6's parser** — `iladub.etkl.headers.is_numeric` +
`iladub.etkl.rows._numeric_token_sum` — for the probe/census's own `as_decimal`, and restricting
candidates to **lone lines**: a line of exactly one word that `is_numeric`.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python scripts/r261_baseline.py --census
```

Output:

```
asserted non-grid table regions             32
... having a following band                  29
... following band has >=1 lone-line num       4  <- PAIRS (D-restated)
lone-line numeric candidates (total)           4
candidates with NO column-sum match             0
candidates with >=1 column-sum match             4

MATCHES (D3: exactly-one-column binds; >1 column tied = no bind, flagged):
  BIND        cbh-stem-2026-08-03       p0 t1       374,904 = 374904  cols=[c13(n=10)]
  BIND        cbh-stem-2026-08-03       p0 t3       737,289 = 737289  cols=[c13(n=16)]
  BIND        cbh-stem-2026-08-03       p0 t5       660,363 = 660363  cols=[c13(n=14)]
  BIND        cbh-stem-2026-08-03       p0 t7       178,708 = 178708  cols=[c13(n=5)]

who-wfa p0 '21' is a lone-line candidate: False
```

### 2.1 The census table, restated

| document | page | table idx | candidate | columns matched (D3) | verdict |
|---|---|---|---|---|---|
| cbh-stem-2026-08-03 | 0 | 1 | `374,904` | 1 (`c13`, n=10) | TRUE |
| cbh-stem-2026-08-03 | 0 | 3 | `737,289` | 1 (`c13`, n=16) | TRUE |
| cbh-stem-2026-08-03 | 0 | 5 | `660,363` | 1 (`c13`, n=14) | TRUE |
| cbh-stem-2026-08-03 | 0 | 7 | `178,708` | 1 (`c13`, n=5) | TRUE |

4 pairs, 4 candidates, 4 matches, all TRUE, all exactly-one-column (D3's tie case — more than one
column matching the same candidate — occurs **0** times in this corpus). `who-wfa p0`'s `21` is
**not** a lone-line candidate.

### 2.2 The divergence from "the census's 5" — a finding, not a defect to fix

Addendum 1/2 of `docs/superpowers/2026-10-01-r261-totals-family-spec-handoff.md` record **24
pairs, 5 matches (4 TRUE + 1 FALSE, who-wfa `21`)**, under the old census's rule: `as_decimal`
applied to **every word of every line** in the following band. Under the production rule (M6's
parser, lone lines only) this task measures **4 pairs, 4 candidates, 4 matches, all TRUE**. The
false match is gone, and so are 20 of the 24 pairs.

**The divergence is attributable almost entirely to the lone-line restriction, not to the M6
parser.** Measured directly (diagnostic script, not committed — see below): across the same 29
"following" bands there are **10 lone lines in total**. Of those, **4** are `is_numeric` under M6
(the four cbh port totals, all matched) and **6** are not. Of the 6 non-numeric-under-M6 lone
lines, **0** would have parsed under the old `as_decimal` either (`is_numeric False but as_decimal
True` count = 0) — so **the parser difference costs nothing on this corpus**; every pair the old
census found and the lone-line census does not came from a **multi-word** line (a dense data row,
not a standalone printed total), which the lone-line restriction is designed to exclude.

### 2.3 CONTROL — who-wfa p0's `21` is excluded because its line is not lone, not because it fails to parse

Directly measured, `who-wfa-boys-zscore-0-5.pdf`, page 0, table idx 4 (the census's FALSE):

- **The all-words variant finds the match.** Re-running the old census's own `as_decimal` +
  per-column-sum comparison on just this band confirms the historical finding: `21` equals column
  1's sum (ordinal column, `Decimal('21')`), i.e. `ALL-WORDS MATCH: 21 -> cols [1]`.
- **Its line is not a lone line.** The line containing `21` is:
  `['1:', '9', '21', '0.0029', '11.5486', '0.11261', '8.2', '9.2', '10.3', '11.5', '12.9', '14.5', '16.2']`
  — **13 words**, a full data row of the z-score table beneath it, not a printed total standing
  alone. The lone-line rule excludes it by construction.

This is the CONTROL the brief asked for: the all-words variant finds the known match, and the
lone-line rule excludes it for the stated reason (not a lone line), not because M6's parser
rejects `21` (it does not — `is_numeric("21")` is `True`).

### 2.4 Consequence for the plan

**The corpus never exercises the "worker says no" arm.** With who-wfa's `21` excluded at the
candidate-selection stage (never reaching a worker ask), the only arm the corpus's lone-line
candidates exercise is "worker says yes, arithmetic confirms" (cbh's four port totals). The "worker
says no" and "worker abstains" arms are pinned **only synthetically** (Task 4), per the brief's
instruction. This also means D3's "exactly one matching column, or no bind" tie case has **zero**
corpus instances to date — Task 3's test for it is necessarily synthetic too.

---

## § 3. Diagnostic script (not committed)

The parser-vs-lone-line attribution in § 2.2 and the per-band `as_decimal` check in § 2.3 were run
as one-off inline `python3 -c` commands (reproduced above) rather than committed scripts, since
they are diagnostics explaining the committed instrument's output, not the instrument itself. The
committed instrument is `scripts/r261_baseline.py` (both `--baseline` and `--census`), which
reproduces §§ 1.1 and 2.1 exactly on re-run.

---

## § 4. Commands run (for reproduction)

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python scripts/r261_baseline.py --baseline
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python scripts/r261_baseline.py --census
```

Both run serially, one process at a time (corpus-runs-are-serial). macOS has no `timeout`; the
first `--baseline` run exceeded the default 120s foreground window and was moved to background by
the harness, then read on completion — no `timeout` wrapper was used or needed.

---

## § 5. Review fix round 1 (2026-10-01, append-only — nothing above this line is edited)

### 5.1 The committed census dropped the region/band mismatch guard

`scripts/section_total_fp_census.py:101-104` carries a guard the §§ 1–2 run of
`scripts/r261_baseline.py --census` did not: `extra = len(prep.regions) - len(bands); if extra !=
0 and page not in adopted: skip, counted as SKIPPED`. The committed script has now been fixed
(`run_census`: `adopted = set(rep.adopted)` per document, the same `extra`/`skip` test before the
per-region loop, a `skipped` list, and a printed `SKIPPED <n>` line) so the "same population filter
as `scripts/section_total_fp_census.py`" claim in the module docstring (§ 2, "Instrument") is now
true of the code. **Per instruction, the corpus was NOT re-run for this fix** — §§ 1–2's figures
above (4 pairs, 4 candidates, 4 matches, 32/29 tables/following) are **not** retroactively
corrected and are **not** claimed to already reflect the guard.

**Precedent figure, cited rather than re-measured for this run:** the identical skip condition, run
over the full 27-page corpus, found **`SKIPPED 0`**
(`docs/superpowers/2026-09-17-the-false-positive-denominator-evidence.md:115`: *"A page-scope
census over all 27 pages returned `PAGES SEEN 27 SKIPPED 0 MATCHES 2`"*). The handoff this task
restates from records the same figure at **document** scope, the scope §§ 1–2 above use:
`docs/superpowers/2026-10-01-r261-totals-family-spec-handoff.md` Addendum 2's census re-run states
*"27 pages, 0 skipped"* for `scripts/section_total_fp_census.py` itself, run at `5e33652`.

**This is an inference, not a measurement, for the run that produced §§ 1–2 above.** The guard was
absent from the code at the time that run executed, so nothing in §§ 1–2 demonstrates `SKIPPED 0`
for *this* script's population — it is inferred from the cited precedent (same guard, same
document-scope call shape, same corpus, run close in time) holding at 0 in every prior measurement
anyone has taken of it. The next time `--census` is run (Task 3 or later), its own `SKIPPED` line
is the first actual measurement of this script's own population under the restored guard, and
should be read as superseding this inference.

### 5.2 Minor fixes to the committed script

- Removed the unused `import re` and `_BNODE` (dead code left from the `corpus_verdict_snapshot.py`
  pattern this script was built from; `_canonical_hash` uses `rdflib.compare.to_canonical_graph`'s
  own blank-node canonicalisation, never a regex normalisation).
- `who_wfa_21_lone` now takes the **first** hit only (`if who_wfa_21_lone is None and ...`), not the
  last line scanned that happens to contain `21`. On this corpus the result is unchanged (`False`),
  since who-wfa p0 table idx 4's following band has exactly one line containing `21` among its six
  lines (§ 1.2/§ 2.3's dump), but the prior code's last-hit semantics were an unintended artifact of
  iteration order, not a stated design.

### 5.3 The exact diagnostic commands behind §§ 2.2 and 2.3

§ 3 above says these were "reproduced above" — they were paraphrased, not pasted verbatim. The
actual commands run (both inline, not committed, per § 3's reasoning) are reproduced here in full.

**§ 2.2's parser-vs-lone-line attribution** (10 lone lines total / 4 `is_numeric` / 0 lost to the
parser):

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python3 -c "
import sys; sys.path.insert(0,'src')
from decimal import Decimal, InvalidOperation
from iladub.etkl.classifygraph import TAB
from iladub.etkl.compile import page_bands
from iladub.etkl.document import compile_document
from iladub.etkl.headers import is_numeric
import pathlib

def as_decimal(text):
    if text is None: return None
    s = str(text).strip().replace(',', '').replace('%','').replace('\$','').strip()
    if s in ('', '-', '.'): return None
    neg = s.startswith('(') and s.endswith(')')
    if neg: s = s[1:-1].strip()
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    return -d if neg else d

GRID=str(TAB.DataGrid)
pdfs = sorted(pathlib.Path('corpus').rglob('*.pdf'))
lone_line_total=0
lone_line_isnumeric_true=0
lone_line_isnumeric_false_but_asdecimal_true=0
examples=[]
for pdf in pdfs:
    path=str(pdf)
    rep = compile_document(path, validate_shapes=False)
    for page, prep in enumerate(rep.pages):
        repair = frozenset(i for pg,i in rep.repaired_bands if pg==page)
        bands = page_bands(path, page, section_repair_bands=repair)
        for i,r in enumerate(prep.regions):
            if r.verdict!='asserted' or r.table_uri is None or r.anchor==GRID: continue
            if i+1>=len(bands): continue
            nxt=bands[i+1]
            for ln in nxt.lines:
                if len(ln.words)==1:
                    lone_line_total+=1
                    w=ln.words[0].text
                    if is_numeric(w):
                        lone_line_isnumeric_true+=1
                    elif as_decimal(w) is not None:
                        lone_line_isnumeric_false_but_asdecimal_true+=1
                        examples.append((pdf.stem, page, i, w))
print('total lone lines in all following bands:', lone_line_total)
print('is_numeric True (M6):', lone_line_isnumeric_true)
print('is_numeric False but as_decimal True (parser-only loss):', lone_line_isnumeric_false_but_asdecimal_true)
for e in examples[:20]:
    print(' ', e)
"
```

**Caveat on this diagnostic, not on § 2.2's conclusion:** like the pre-fix `--census`, this inline
command carries no region/band mismatch guard either — it is a one-off explanatory script, not the
committed instrument, and § 5.1's `SKIPPED 0` inference applies to it the same way.

**§ 2.3's CONTROL** (who-wfa p0 table idx 4, all-words variant finds `21 -> col 1`, the line has 13
words):

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python3 -c "
import sys; sys.path.insert(0,'src')
from decimal import Decimal, InvalidOperation
from iladub.etkl.classifygraph import TAB
from iladub.etkl.compile import page_bands
from iladub.etkl.document import compile_document, _index_suffix
import glob

def as_decimal(text):
    if text is None: return None
    s = str(text).strip().replace(',', '').replace('%','').replace('\$','').strip()
    if s in ('', '-', '.'): return None
    neg = s.startswith('(') and s.endswith(')')
    if neg: s = s[1:-1].strip()
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    return -d if neg else d

path = glob.glob('corpus/**/who-wfa*.pdf', recursive=True)[0]
rep = compile_document(path, validate_shapes=False)
page=0
prep = rep.pages[page]
repair = frozenset(i for pg,i in rep.repaired_bands if pg==page)
bands = page_bands(path, page, section_repair_bands=repair)
GRID=str(TAB.DataGrid)
i=4
r = prep.regions[i]
print('verdict', r.verdict, 'table_uri', r.table_uri, 'anchor==GRID', r.anchor==GRID)
nxt = bands[i+1]
per_col={}
for entry in rep.graph.objects(r.table_uri, TAB.hasCell):
    col = rep.graph.value(entry, TAB.atColumn)
    if col is None: continue
    val = as_decimal(rep.graph.value(entry, TAB.cellText))
    if val is None: continue
    try:
        ci=_index_suffix(col, r.table_uri,'c')
    except Exception:
        ci=str(col)
    per_col.setdefault(ci, []).append(val)
sums = {ci: sum(v, Decimal(0)) for ci,v in per_col.items()}
print('col sums', sums)
for ln in nxt.lines:
    for w in ln.words:
        d = as_decimal(w.text)
        if d is not None and d in sums.values():
            cols = [ci for ci,s in sums.items() if s==d]
            print('ALL-WORDS MATCH:', w.text, '-> cols', cols, 'line words:', [x.text for x in ln.words], 'n_words_in_line', len(ln.words))
"
```

---

## § 6. Task 1 — P3 (total-of-totals wording, a proposition) and P1 re-run on the D7 crop (2026-10-01, append-only)

**Serves:** prog:criterion:etkl:03, via Task 1's step in the plan
(`.superpowers/sdd/2026-10-01-r261-totals-family/task-1-brief.md`).

### 6.0 Decision rules — fixed in the task brief BEFORE any call, reproduced verbatim here

Both rules were authored in the task brief handed to this loop, before any probe ran, and were
not altered afterward. Reproduced here for the record, not re-derived:

- **P3.** *"the grand total binds in this loop iff `1,951,264` gets yes ×3 AND none of the 4 null
  asks (each port total asked the grand-total question) gets yes. If not: record, DO NOT reword,
  state the loop drops the total-of-totals level."*
- **P1 on the D7 crop.** *"Holds iff port totals yes ×3, `21` no, no null yes. If it does NOT
  hold: STOP, record it, report DONE_WITH_CONCERNS with the numbers — do not restore the 8-line
  crop."*

### 6.1 Probe changes (`scripts/r261_total_question_probe.py`)

- **D7 crops.** `crop()` (the old `tail_lines`-of-8 table crop) is replaced by `crop_table(path,
  page, band, line)` — the whole previous (table) band, through the candidate's own line, no
  tail-line constant — and a new `crop_union(path, page, lines)` — the union box of a set of
  lines, used for the total-of-totals level (the four port-total lines plus the `1,951,264`
  line). Both keep the probe's existing render `resolution=150` and the 4-unit padding.
- **Closed output, no `note`.** `ask(png, prompt_text)` now returns one of `"yes" | "no" |
  "cannot_tell" | "UNPARSED" | "HTTP<code>"`. A reply is accepted only if it parses as JSON whose
  **only** key is `answer` with one of the three values; anything else (extra keys, a different
  value, unparseable JSON) is recorded as `UNPARSED`. Applies to both wordings.
- **Second wording, `PROMPT2`** — the brief's draft verbatim, with the same closed-JSON-only
  instruction appended (no `note`), per the resolutions ("closed output... for BOTH wordings").
  The worker is not given the operands' values; only `{value}` (the candidate under test) is
  substituted.
- The per-case tuple built in the `cases` loop now carries the candidate's own `Line` object
  (`ln`) instead of the whole following band (`nxt`), so `crop_table` can crop through exactly
  that line rather than the whole next band. **This does not change which cases are collected**
  (verified below, § 6.2): still 12 candidates, 5 matches, same population as Addendum 2.

### 6.2 Structural smoke test (`P1_REPEAT=1`, not the recorded evidence)

Run first, to catch a crop/parsing defect before spending the 3-repeat budget:

```
ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \
  P1_REPEAT=1 env -u BAML_LIVE .venv/bin/python scripts/r261_total_question_probe.py
```

```
--- P3: total-of-totals wording, D7 union crop ---
P3 grand  1,951,264 -> yes
P3 null     374,904 -> yes
P3 null     737,289 -> yes
P3 null     660,363 -> no
P3 null     178,708 -> cannot_tell
--- P1 on the D7 table-level crop: 12 numeric candidates; 5 exact-sum matches ---
MATCH cbh-     p0 t1      374,904 -> yes
MATCH cbh-     p0 t3      737,289 -> yes
MATCH cbh-     p0 t5      660,363 -> yes
MATCH cbh-     p0 t7      178,708 -> yes
null  who-wfa  p0 t2            7 -> no
null  who-wfa  p0 t3            1 -> no
null  who-wfa  p0 t4            7 -> no
MATCH who-wfa  p0 t4           21 -> no
null  who-wfa  p1 t2            7 -> no
null  who-wfa  p1 t3            1 -> no
null  who-wfa  p1 t4            7 -> no
null  who-wfa  p2 t1            7 -> no
```

Population confirmed unchanged by the `ln`-vs-`nxt` refactor: 12 candidates, 5 matches (same as
Addendum 2). Already visible here (n=1, not the decision evidence): two of the four P3 null asks
answer `yes`.

### 6.3 Recorded run (`P1_REPEAT=3`, the decision evidence)

```
ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \
  P1_REPEAT=3 env -u BAML_LIVE .venv/bin/python scripts/r261_total_question_probe.py
```

```
--- P3: total-of-totals wording, D7 union crop ---
P3 grand  1,951,264 -> yes yes cannot_tell
P3 null     374,904 -> yes yes yes
P3 null     737,289 -> yes yes yes
P3 null     660,363 -> yes yes no
P3 null     178,708 -> cannot_tell cannot_tell cannot_tell
--- P1 on the D7 table-level crop: 12 numeric candidates; 5 exact-sum matches ---
MATCH cbh-     p0 t1      374,904 -> yes yes yes
MATCH cbh-     p0 t3      737,289 -> yes yes yes
MATCH cbh-     p0 t5      660,363 -> yes yes yes
MATCH cbh-     p0 t7      178,708 -> yes yes yes
null  who-wfa  p0 t2            7 -> no no no
null  who-wfa  p0 t3            1 -> no no cannot_tell
null  who-wfa  p0 t4            7 -> no no no
MATCH who-wfa  p0 t4           21 -> no no no
null  who-wfa  p1 t2            7 -> no no no
null  who-wfa  p1 t3            1 -> no no no
null  who-wfa  p1 t4            7 -> no no no
null  who-wfa  p2 t1            7 -> no no no
```

Both runs (§ 6.2, § 6.3) were run serially, nothing else compiling at the same time
(corpus-runs-are-serial); macOS has no `timeout` and none was used. `ANTHROPIC_API_KEY` was never
printed; it was read via the prefix shown and passed only as the `x-api-key` HTTPS header inside
`ask()`.

### 6.4 P3 verdict — FAILS the decision rule; the total-of-totals level is DROPPED

Applying § 6.0's rule to § 6.3's recorded answers:

| requirement | measured | met? |
|---|---|---|
| `1,951,264` gets *yes* ×3 | `yes yes cannot_tell` | **NO** |
| no null gets *yes* | `374,904` -> `yes yes yes`; `737,289` -> `yes yes yes`; `660,363` -> `yes yes no`; `178,708` -> `cannot_tell` ×3 | **NO** — 3 of 4 nulls draw at least one *yes*, two of them *yes* ×3 |

Both conjuncts fail, not just one: the grand total itself is not stably *yes*, **and** three of
the four port totals are themselves answered *yes* to "is {value} the grand total?" when shown
the same union-box image. Per the rule, this is **not reworded**. The total-of-totals level is
dropped from this loop: cbh's `1,951,264` is **not** bound by this loop's mechanism, and
`tab:totalOf`/the total-of-totals matching branch (spec § 2.2 second bullet) is **not
implemented** — only table-level `PrintedTotal` binding (the four port totals) proceeds to Tasks
2-4. cbh is therefore **not accepted** by this loop (consistent with spec § 0's framing that
acceptance was never guaranteed, and with task-1-brief step 2's "cbh is then not accepted by this
loop (Task 7 records why)").

**Reading, not a rule revision.** The failure mode is informative for whoever later tries a
second wording: asked over an image that shows all five numbers at once, the model appears to
answer "is {value} *a* total shown on the page" rather than "is {value} *the sum of* the totals
shown on the page" — every port total scores close to the grand total itself (2 of 4 at a clean
*yes* ×3, one split 2-1, only the smallest, `178,708`, drawing `cannot_tell` ×3 instead of a
*yes*). This is a wording/discrimination problem, not an arithmetic one — arithmetic was never
asked to do anything here; P3 tests the worker alone. No rewording was attempted in this loop
(the rule forbids it).

### 6.5 P1-on-D7 verdict — HOLDS

Applying § 6.0's rule to § 6.3's recorded answers:

| requirement | measured | met? |
|---|---|---|
| all 4 port totals *yes* ×3 | `374,904`->`yes yes yes`, `737,289`->`yes yes yes`, `660,363`->`yes yes yes`, `178,708`->`yes yes yes` | **YES** |
| `21` gets *no* | `no no no` | **YES** |
| no null gets *yes* | all 7 nulls: `no no no` / `no no cannot_tell` / `no no no` / `no no no` / `no no no` / `no no no` / `no no no` — zero `yes` across 21 asks | **YES** |

**P1 holds on the D7 table-level crop** (the whole previous band through the candidate line,
replacing the old 8-line-tail crop). The result reproduces Addendum 2's P1 finding (4/4 TRUE at
*yes* ×3, the FALSE at *no* ×3, zero *yes* among the nulls) on the differently-cropped image, so
the table-level wording and crop are not sensitive to the tail-line constant removal — the D7
table-level crop is confirmed usable for Tasks 2-4, and the 8-line crop is **not** restored.

### 6.6 CONTROL (in place of FALSIFICATION — a probe script, not src/, has nothing to falsify)

The null asks ARE the control for both probes, by construction (brief step 2/3): a number that
the arithmetic would never bind, asked the same question as a true candidate, to see whether the
worker discriminates by reading or by surface pattern.

- **P1's control (7 asks, D7 table crop):** every null — small counts and a percentage-column
  member (`7`, `1`, `7`, `7`, `1`, `7`, `7` across who-wfa's three pages) — answers `no` or
  `cannot_tell`, never `yes`, across 21 asks. The worker does not mistake an arbitrary number
  standing near a table for that table's total.
- **P3's control (4 asks, D7 union crop) is the one that FAILS**, and that failure is the
  finding: the four port totals, each itself a true table-level total and each visible in the
  same cropped image as `1,951,264`, are answered `yes` to "is {value} the grand total?" at a
  combined 8 *yes* / 1 *no* / 3 `cannot_tell` across 12 asks — a higher *yes* rate than the
  target `1,951,264` itself (`yes yes cannot_tell`, 2/3). The control is what shows the wording
  does not discriminate "a total" from "the total of the totals" on this image.

### 6.7 Doc impact of this section

**None.** No vocabulary or published term changes; § 0's header `Doc impact: none` (set by Task
0) continues to describe this whole evidence file, including this section — this task adds no
`tab:` term, and the spec's `tab:totalOf`/total-of-totals vocabulary (design § 4) is not
implemented in this loop (§ 6.4).
