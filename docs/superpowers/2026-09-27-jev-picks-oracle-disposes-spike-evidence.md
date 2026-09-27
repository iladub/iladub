# Evidence — arm A spike: text-only pieces enumerate, Jev picks, drawn marks dispose (2026-09-27)

**Serves:** maintenance — the maintainer's "test A first" spike for the Jev-decides architecture; it meets no criterion

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `extent-oracle-evidence` (PR #277) · **src measured:** `2fe5ed6`

**Doc impact: none.**

This follows `2026-09-27-jev-decides-architecture-handoff.md` § 5. That handoff's first question, *when
Jev decides between reasoning pieces, what refuses a wrong decision?*, was put to the maintainer with
three arms:
- **A:** Jev picks, and an exact oracle still disposes.
- **B:** Jev's pick is admitted on its own.
- **C:** a mix, depending on the kind of judgement.

The maintainer answered **"let's test A first"**. That instruction is recorded nowhere but this file.
The spike was approved with one design constraint: **the pieces that propose must not be the marks that
dispose**. Candidates and evidence come from text only, and the oracle uses only drawn vector marks.

## Protocol (throwaway; the script is kept below and in `internal/`)

**Enumeration (PROCEDURAL, with no thresholds).** Every candidate cut becomes a question to Jev.

**Jev (four coarse-to-fine rounds, each a closed choice with an abstain option):**

1. **Line boundaries.** One question per pair of adjacent lines: does the same object continue, or does
   a different one start?
2. **Empty strips.** One question per x-strip that is empty across a multi-line run from round 1:
   are these side-by-side objects, or columns of one object?
3. **Piece roles.** For each piece: table, caption, note, prose, page furniture, a lone value, or
   cannot tell.
4. **Line roles.** For each line of a table piece: caption, headings, data, a group label, a total,
   a note, furniture, or cannot tell.

**Candidate extents.** For each table piece, the host enumerates **8 trim variants**: the headings,
data and group-label lines, plus every combination of {totals, notes, captions}.

**Oracle (lead 2's exact form).** A variant is admitted iff its word set **equals** the word set of
one author-drawn box. If the page has no marks, the oracle abstains.

**Conditions.**
- **R:** raw numbered line text.
- **E:** R plus computed evidence statements in each question. For line boundaries, these are the gap
  ratio to the page median, word x-overlap counts, numeric share and a caption-like prefix. For strips,
  they are width relative to the median word gap, the strip's width rank, and how many lines have
  words on both sides.

**Ideal.** The same rounds answered from ground truth. This is the ceiling of the question set.

**Ground truth.**
- A table's extent is its column headings plus body. Titles, captions, sources, notes and page
  furniture are outside it; totals are inside.
- It is transcribed from the lead-2 rule census and renders, as regions in the script's `PAGES`.
- **On pages where the drawn box bounds exactly that, the oracle matches ground truth by construction.**
  This spike therefore measures what the host and Jev PROPOSE, and whether the oracle refuses the
  rest. The validity of the marks as an oracle rests on lead 2, not on this spike.

**Development vs held-out.**
- The question set was **iterated on the 6 dev pages after seeing their failures**. Round 4 and the
  "group of rows" role were added then, and lines are grouped by text-line identity, not rounded y.
- It was frozen before the 8 held-out pages were run.
- apple p0/p1 were left out of the held-out set, because lead 2 already measured that the oracle
  breaks there (interior rules pair only into slices).

## Results (MEASURED; 3 repeats per condition, frozen protocol)

Each cell sums over the tables and the 3 repeats.

| pages | cond | table×rep | exact extent among the variants | admitted, = GT | admitted, ≠ GT | correct, oracle abstains |
|---|---|---|---|---|---|---|
| dev (cbh p0, bfs p5/p6, ons p4, WHO p0, apple p2) | ideal | 12 | 12 | 10 | 0 | 1 |
| dev | R | 36 | 23 | 20 | **0** | 3 |
| dev | E | 36 | 26 | 23 | **0** | 3 |
| held-out (WHO p1/p2, ons p7/p8, gcap p0, graincorp-stem p0–2) | ideal | 8 | 8 | 4 | 0 | 0 |
| held-out | R | 24 | 5 | 1 | **3** | 0 |
| held-out | E | 24 | 13 | 3 | **0** | 0 |

Some ideal extents are refused, because the author's box and the ground-truth convention disagree on
1 dev page (apple p2, where the boxes are slices) and 4 held-out pages; see "What this shows", item 3.

### Per page (held-out; the same verdict in all 3 repeats unless stated)

| page | R | E | what failed |
|---|---|---|---|
| WHO p1 | Jaccard 0.99 | exact, refused | R reads the spanner "Z-scores (weight in kg)" as a caption. The box's bottom rule (y 482) lies below the footer "WHO Child Growth Standards", so it refuses the correct extent |
| WHO p2 | Jaccard 0.98 | exact, refused | as WHO p1 (rule at y 320) |
| ons p7 | 0.56 | 0.56 | both split the "Percentage change" sub-blocks off as separate objects |
| ons p8 | 0.27 | 0.27 | as ons p7 |
| gcap p0 | exact; **the title variant is admitted** | exact, refused | the author drew the title "ELEVATION CAPACITY TABLE" and the date line inside the box |
| stem p0 | exact in 1 of 3 | exact in 1 of 3, refused | the box contains the title "SHIPPING STEM" and the date |
| stem p1 | 0.68–0.72 | 0.38–0.69 | extent errors (not diagnosed) |
| stem p2 | admitted in 1 of 3 | admitted in 3 of 3 | — |

### Dev pages (frozen protocol, 3 repeats)

- **cbh p0.** E separates the side-by-side stock and maintenance tables (Jaccard 0.97 for stock, 3/3).
  R does not (0.18–0.32, 3/3). The stock miss under E is the single heading word "TOTAL". In one E
  repeat the maintenance table merged elsewhere (Jaccard 0.0).
- **bfs p5:** 2/2 admitted in every condition and repeat.
- **bfs p6.** The box contains the "Source" line. Jev never labels it a note inside a table variant
  that the oracle matches: the best Jaccard is 0.99 and nothing is admitted.
- **ons p4:** the correct extent every time. It stays a proposition, because the page has no marks.
- **WHO p0.** E admits the extent (3/3). R reads the spanner as a caption (0/3).

## What this shows

1. **A holds, in the E condition.**
   - No extent that differs from ground truth was admitted in 60 table-runs under E, on dev or
     held-out pages.
   - The oracle's exactness is what carries this. Jev's near-misses (Jaccard 0.88–0.99) are refused,
     not rounded up.
2. **Computed evidence beats raw text, measured for the first time.**
   - Held-out: 13/24 exact under E against 5/24 under R.
   - cbh side-by-side: Jaccard 0.97 against 0.18–0.32.
   - The E condition also avoided R's gcap admission.
   - This is the maintainer's "deterministic reasoning pieces" claim, and it is the opposite of
     Probe A/B's result for *spatial text*. **Computed evidence statements are not spatial text.**
3. **The oracle defines what an extent IS, and authors disagree about that.**
   - The observed boxes vary by author:
     - cbh draws totals outside the box;
     - bfs p6 puts the source inside it;
     - gcap and stem put the title inside it;
     - WHO p1/p2 put the footer inside it.
   - Enumerating trim variants raises yield, but it hands the definition of an extent to the author's
     box. **R's 3 "wrong" admissions on gcap are exactly that**: the table plus its boxed title, and
     every word of the table itself was right.
   - Two responses are possible:
     - **(a)** redefine an extent as "whatever the author boxed", with Jev's line roles carried inside
       it, so a boxed title is a labelled caption line rather than an error;
     - **(b)** stop enumerating the caption and furniture variants, and accept the lower yield.
   - This is a design decision for the maintainer. It is **not ruled**.
4. **Yield on held-out pages is low: 3/24 admitted under E.**
   - Of E's 13 exact held-out table-runs, 10 are refused by the box convention (WHO ×6, gcap ×3,
     stem p0 ×1).
   - The largest reading failure is ons p7/p8, whose "Percentage change" sub-blocks Jev reads as
     separate objects. That is arguably a defensible reading, and the author drew no rule between them.

## Unverified

- **Scale.** 14 pages, 20 tables, 3 repeats. Jev is non-deterministic, and the cbh maintenance merge
  appeared in 1 of 3 E repeats.
- **Ground truth for apple p2** includes its "Supplemental" lines, which is an arbitrary choice.
- **stem p1 was not diagnosed.**
- **Cost.** 766 recorded call files, cents in total; not itemised.
- **Where the calls are.** The raw requests and responses are at
  `internal/benchmarks/jev-2026-09-27/spike-A/calls2/` (confidential, untracked; checked for
  credentials: none), next to `results.jsonl`. The E and R rows in the tables above are the reps
  `h1`–`h3` there. `spike_tuned_on_dev.py` is the pre-freeze version.

## Reproduction

Run from the repo root with `CF_ACCOUNT_ID`/`CF_API_TOKEN` set:
`./.venv/bin/python spike.py {ideal|R|E} <rep> [page keys…]`. Results are appended to `results.jsonl`.
The script follows verbatim. It includes the diagnostic `wrong_diff` added after the held-out run,
which changes output only.

```
"""THROWAWAY spike — architecture A: text-only deterministic pieces enumerate every candidate cut,
Jev decides each cut and each piece's role, the author's drawn marks dispose the resulting extents.

usage: spike.py COND REP      COND in {ideal, R, E}
  ideal = answers derived from ground truth (the ceiling of the question set)
  R     = Jev, raw line text only
  E     = Jev, raw line text + computed evidence statements
"""
import json, os, re, sys, time, statistics, urllib.request
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines

C = "/Volumes/WD Green/dev/git/iladub/corpus/"
OUT = os.path.dirname(os.path.abspath(__file__))
COND, REP = sys.argv[1], sys.argv[2]

# Ground truth: table extent = boxhead + body, captions/sources/notes outside. Regions (x0,y0,x1,y1),
# words by centre. Transcribed from the lead-2 rule census + render (2026-09-27-extent-two-leads-evidence.md).
W = 2000
PAGES = {
 "cbh0": ("ag-trade/cbh-stem-2026-08-03.pdf", 0,
          [(38,105,1152,200),(38,241,1152,384),(38,434,1152,561),(38,602,1152,656),(38,690,449,731),(544,690,690,722)]),
 "bfs5": ("gov-stats/bfs-population-bilan-2023.pdf", 5, [(71,82,524,262.5),(71,354,524,611)]),
 "bfs6": ("gov-stats/bfs-population-bilan-2023.pdf", 6, [(71,93,524,491)]),
 "ons4": ("gov-stats/ons-index-of-services-2026-02.pdf", 4, [(0,58,W,623)]),
 "who0": ("health/who-wfa-boys-zscore-0-5.pdf", 0, [(57,100,785,466)]),
 "apl2": ("financial/apple-fy2026q3-statements.pdf", 2, [(0,102,W,703)]),
}
HELD = {
 "who1": ("health/who-wfa-boys-zscore-0-5.pdf", 1, [(0,100,W,457)]),
 "who2": ("health/who-wfa-boys-zscore-0-5.pdf", 2, [(0,100,W,295)]),
 "ons7": ("gov-stats/ons-index-of-services-2026-02.pdf", 7, [(0,93,W,588)]),
 "ons8": ("gov-stats/ons-index-of-services-2026-02.pdf", 8, [(0,98,W,587)]),
 "gcap0": ("ag-trade/graincorp-capacity-2026-08-04.pdf", 0, [(42,87,818,408)]),
 "stem0": ("ag-trade/graincorp-stem-2026-07-31.pdf", 0, [(12,68,833,457)]),
 "stem1": ("ag-trade/graincorp-stem-2026-07-31.pdf", 1, [(12,49,833,570)]),
 "stem2": ("ag-trade/graincorp-stem-2026-07-31.pdf", 2, [(12,49,833,511)]),
}
PAGES.update(HELD)
# Oracle boxes = author-drawn marks. Same as GT where the marks bound the table exactly; ons p4 has
# none (abstain); apple's full-width rules pair only into interior slices.
AP = [112,148,347,362,461,476,604,618,647,661]
ORACLE = {k: v[2] for k, v in PAGES.items()}
ORACLE["ons4"] = []
ORACLE.update({"who1": [(0,100,W,482)], "who2": [(0,100,W,320)], "gcap0": [(42,66,818,408)],
               "stem0": [(12,49,833,457)]})
ORACLE["apl2"] = [(0,a,W,b) for a, b in zip(AP, AP[1:])]

CAP = re.compile(r"^(T\d+|Table\s*\d+|IOS\d+|Figure\s*\d+)\b")
NUM = re.compile(r"[-–(]?[$€£]?\d[\d.,:/']*\)?%?")
cen = lambda w: ((w.x0 + w.x1) / 2, (w.top + w.bottom) / 2)
inside = lambda w, r: r[0] <= cen(w)[0] <= r[2] and r[1] <= cen(w)[1] <= r[3]
txt = lambda ws: " ".join(w.text for w in sorted(ws, key=lambda w: w.x0))


def jev(state, qs, tag):
    out, chunk, size, n = {}, {}, 0, 0
    for q, v in qs.items():
        if chunk and size + len(v["instructions"]) > 60000:
            out.update(jev1(state, chunk, f"{tag}-{n}")); chunk, size, n = {}, 0, n + 1
        chunk[q] = v; size += len(v["instructions"])
    if chunk: out.update(jev1(state, chunk, f"{tag}-{n}"))
    return out


def jev1(state, qs, tag):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run"
    body = {"model": "typesafe/jev", "input": {"state": state, "questions": qs}}
    req = urllib.request.Request(url, json.dumps(body).encode(), {
        "Authorization": f"Bearer {os.environ['CF_API_TOKEN']}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r: resp = json.load(r); break
        except Exception as e:
            err = e; time.sleep(3)
    else: raise err
    json.dump({"req": body, "resp": resp}, open(f"{OUT}/calls2/{tag}.json", "w"), indent=1)
    return {q: a.get("choice") for q, a in resp["result"]["result"]["answers"].items()}


def gt_of(w, gts):
    for k, r in enumerate(gts):
        if inside(w, r): return k
    return None


def run_page(key):
    f, p, gts = PAGES[key]
    ws = extract_words(C + f, p)
    lines = sorted([l for l in text_lines(ws) if l.words], key=lambda l: l.top)
    L = [list(l.words) for l in lines]
    state = "Text of one PDF page, line by line, top to bottom. Each line is numbered.\n" + \
            "\n".join(f"L{i}: {txt(l)}" for i, l in enumerate(L))
    gaps = [lines[i+1].top - lines[i].bottom for i in range(len(L) - 1)]
    med = statistics.median(gaps) if gaps else 1
    tag = f"{COND}-{REP}-{key}"

    # ---- round 1: one question per line boundary
    SAME, DIFF, UNK = "the same object continues", "a different object starts", "cannot tell"
    q1, ideal1 = {}, {}
    for i in range(len(L) - 1):
        a, b = L[i], L[i+1]
        ev = ""
        if COND == "E":
            ov = sum(1 for w in b if any(w.x0 <= v.x1 and v.x0 <= w.x1 for v in a))
            nb = sum(1 for w in b if NUM.fullmatch(w.text)); na = sum(1 for w in a if NUM.fullmatch(w.text))
            ev = (f"\nEvidence computed from the page: the blank gap between the two lines is "
                  f"{gaps[i]/med:.1f}x the page's median gap between lines; {ov} of the {len(b)} words of "
                  f"L{i+1} sit horizontally under some word of L{i}; numbers are {na} of {len(a)} tokens on "
                  f"L{i} and {nb} of {len(b)} on L{i+1}; L{i+1} "
                  f"{'begins like a numbered table caption' if CAP.match(txt(b)) else 'does not begin like a numbered caption'}.")
        q1[f"b{i}"] = {"type": "choice", "instructions":
            f"L{i}: {txt(a)[:300]}\nL{i+1}: {txt(b)[:300]}\nReading the page as a person would: does L{i+1} "
            f"continue the same object as L{i} (the same table including its column headings, the same "
            f"paragraph, the same list), or does a different object (another table, a title or caption, "
            f"a note, a paragraph) start at L{i+1}?{ev}", "criteria": {SAME: None, DIFF: None, UNK: None}}
        shared = {gt_of(w, gts) for w in a} & {gt_of(w, gts) for w in b} - {None}
        ideal1[f"b{i}"] = SAME if shared else DIFF
    ans1 = ideal1 if COND == "ideal" else jev(state, q1, tag + "-r1")
    runs, cur = [], [0]
    for i in range(len(L) - 1):
        if ans1[f"b{i}"] == SAME: cur.append(i + 1)
        else: runs.append(cur); cur = [i + 1]
    runs.append(cur)

    # ---- round 2: every x-strip empty across a multi-line run
    SIDE, COLS = "two different objects side by side", "columns or parts of the same object"
    q2, ideal2, strips = {}, {}, {}
    for r, run in enumerate(runs):
        if len(run) < 2: continue
        rw = [w for i in run for w in L[i]]
        iv = sorted((w.x0, w.x1) for w in rw)
        empt, hi = [], iv[0][1]
        for x0, x1 in iv[1:]:
            if x0 > hi: empt.append((hi, x0))
            hi = max(hi, x1)
        wgaps = [b.x0 - a.x1 for i in run for a, b in zip(sorted(L[i], key=lambda w: w.x0),
                                                              sorted(L[i], key=lambda w: w.x0)[1:])]
        mg = statistics.median(wgaps) if wgaps else 1
        order = sorted(range(len(empt)), key=lambda k: -(empt[k][1] - empt[k][0]))
        for k, (x0, x1) in enumerate(empt):
            qid = f"r{r}s{k}"; strips[qid] = (r, x0, x1)
            show = [(i, txt([w for w in L[i] if w.x1 <= x0]), txt([w for w in L[i] if w.x0 >= x1])) for i in run]
            body = "\n".join(f"L{i}: left «{a[:120]}»  |  right «{b[:120]}»" for i, a, b in show[:8])
            ev = ""
            if COND == "E":
                both = sum(1 for _, a, b in show if a and b)
                ev = (f"\nEvidence computed from the page: the strip is {(x1-x0)/mg:.1f}x the median gap "
                      f"between adjacent words in these lines; it is the {order.index(k)+1}. widest of the "
                      f"{len(empt)} empty strips in these lines; {both} of {len(run)} lines have words on both sides.")
            q2[qid] = {"type": "choice", "instructions":
                f"Lines L{run[0]}-L{run[-1]} have an empty vertical strip running through all of them. "
                f"The words left and right of it:\n{body}\nDoes this strip separate two different objects "
                f"placed side by side (e.g. two tables, a table and a note), or does it only separate "
                f"columns or parts of one object?{ev}", "criteria": {SIDE: None, COLS: None, UNK: None}}
            L_ = {gt_of(w, gts) for w in rw if w.x1 <= x0} - {None}
            R_ = {gt_of(w, gts) for w in rw if w.x0 >= x1} - {None}
            ideal2[qid] = COLS if (L_ & R_) or not (L_ or R_) else SIDE
    ans2 = ideal2 if COND == "ideal" else jev(state, q2, tag + "-r2")
    pieces = []
    for r, run in enumerate(runs):
        cuts = sorted(strips[q][1:] for q in strips if strips[q][0] == r and ans2.get(q) == SIDE)
        bounds, lo = [], -1
        for x0, x1 in cuts: bounds.append((lo, (x0 + x1) / 2)); lo = (x0 + x1) / 2
        bounds.append((lo, 1e9))
        for a, b in bounds:
            pw = [w for i in run for w in L[i] if a <= cen(w)[0] < b]
            if pw: pieces.append(pw)

    # ---- round 3: what is each piece
    ROLES = {"TAB": "a table (its column headings and/or its rows of data)",
             "CAP": "the title or caption of a table", "NOTE": "a source line, note or footnote",
             "PROSE": "running text", "FURN": "page header, footer or page number",
             "VAL": "a lone value or label", "UNK": "cannot tell"}
    q3, ideal3 = {}, {}
    for k, pw in enumerate(pieces):
        ls = sorted({round(w.top) for w in pw})
        rows = [txt([w for w in pw if round(w.top) == t]) for t in ls]
        ev = ""
        if COND == "E":
            n = sum(1 for w in pw if NUM.fullmatch(w.text))
            ev = (f"\nEvidence computed from the page: {len(rows)} lines, {len(pw)} words, {n} of them numbers; "
                  f"{'the first line begins like a numbered caption' if CAP.match(rows[0]) else 'no numbered caption at its start'}.")
        show = rows if len(rows) <= 12 else rows[:8] + ["…"] + rows[-3:]
        q3[f"p{k}"] = {"type": "choice", "instructions":
            "This block of the page:\n" + "\n".join(s[:200] for s in show) +
            f"\nWhat is it?{ev}", "criteria": {v: None for v in ROLES.values()}}
        g = [gt_of(w, gts) for w in pw]
        ideal3[f"p{k}"] = ROLES["TAB"] if sum(x is not None for x in g) * 2 > len(g) else ROLES["PROSE"]
    ans3 = ideal3 if COND == "ideal" else jev(state, q3, tag + "-r3")
    props = [frozenset(id(w) for w in pw) for k, pw in enumerate(pieces) if ans3.get(f"p{k}") == ROLES["TAB"]]

    # ---- round 4 (fine): the role of each line inside a table piece; trim before proposing
    LR = {"CAP": "title, caption or subtitle of the table", "HEAD": "column headings",
          "DATA": "a row of data", "GRP": "a label heading a group of rows", "TOT": "a total or subtotal row", "NOTE": "source, note or footnote",
          "FURN": "page header, footer or page number", "UNK": "cannot tell"}
    lineof = {id(w): i for i, l in enumerate(L) for w in l}
    tabs = [pw for k, pw in enumerate(pieces) if ans3.get(f"p{k}") == ROLES["TAB"]]
    q4, rowsof = {}, {}
    for t, pw in enumerate(tabs):
        ls = sorted({lineof[id(w)] for w in pw})
        rows = [txt([w for w in pw if lineof[id(w)] == y]) for y in ls]
        for j, y in enumerate(ls):
            rowsof[f"t{t}l{j}"] = (t, y)
            ctx = "\n".join(("» " if i == j else "  ") + r[:160] for i, r in enumerate(rows) if abs(i - j) <= 4)
            q4[f"t{t}l{j}"] = {"type": "choice", "instructions": "A table block of the page; the marked line (») is "
                f"line {j+1} of {len(rows)}:\n{ctx}\nWhat is the marked line, within this table?",
                "criteria": {v: None for v in LR.values()}}
    ans4 = {} if COND == "ideal" else jev(state, q4, tag + "-r4")
    trim = {}
    for conv, keep in (("with_totals", {"HEAD", "DATA", "GRP", "TOT"}), ("no_totals", {"HEAD", "DATA", "GRP"})):
        kv = {LR[k] for k in keep}
        trim[conv] = [frozenset(id(w) for w in pw if ans4.get(next(q for q, v in rowsof.items() if v == (t, lineof[id(w)]))) in kv)
                      for t, pw in enumerate(tabs)] if COND != "ideal" else None

    # ---- score + dispose
    gtsets = [frozenset(id(w) for w in ws if inside(w, r)) for r in gts]
    orsets = [frozenset(id(w) for w in ws if inside(w, r)) for r in ORACLE[key]]
    res = {"page": key, "cond": COND, "rep": REP, "n_gt": len(gts), "n_prop": len(props),
           "abstain": {"r1": list(ans1.values()).count(UNK), "r2": list(ans2.values()).count(UNK),
                       "r3": list(ans3.values()).count(ROLES["UNK"])}, "nq": [len(q1), len(q2), len(q3)]}
    exact = sum(1 for g in gtsets if g in props)
    best = [round(max((len(g & p) / len(g | p) for p in props), default=0), 2) for g in gtsets]
    verd = []
    for pset in props:
        right = pset in gtsets
        v = "abstain" if not orsets else ("admit" if pset in orsets else "refuse")
        verd.append((v, right))
    byid = {id(w): w for w in ws}
    diff = []
    for g in gtsets:
        pb = max(props, key=lambda p: len(g & p) / len(g | p), default=frozenset())
        diff.append({"missing": txt([byid[i] for i in g - pb])[:160], "extra": txt([byid[i] for i in pb - g])[:160]})
    res["diff"] = diff
    # frozen protocol: the host enumerates trim variants, the oracle admits the one equal to a box
    if COND != "ideal":
        from itertools import combinations
        opt = ["TOT", "NOTE", "CAP"]
        V = {"right": 0, "wrong": 0, "exact": 0, "abstain_right": 0}
        for t, pw in enumerate(tabs):
            vs = set()
            for k in range(4):
                for extra in combinations(opt, k):
                    kv = {LR[x] for x in {"HEAD", "DATA", "GRP", *extra}}
                    vs.add(frozenset(id(w) for w in pw if ans4.get(next(q for q, v in rowsof.items() if v == (t, lineof[id(w)]))) in kv))
            vs.discard(frozenset())
            if any(v in gtsets for v in vs): V["exact"] += 1
            adm = [v for v in vs if v in orsets]
            for v in adm:
                if v not in gtsets:
                    g = max(gtsets, key=lambda g: len(g & v))
                    V.setdefault("wrong_diff", []).append((txt([byid[i] for i in g - v])[:120], txt([byid[i] for i in v - g])[:120]))
            V["right"] += sum(1 for v in adm if v in gtsets); V["wrong"] += sum(1 for v in adm if v not in gtsets)
            if not orsets and any(v in gtsets for v in vs): V["abstain_right"] += 1
        res["variants"] = V
    for conv, tp in (trim or {}).items():
        if not tp: continue
        tp = [x for x in tp if x]
        vv = [("abstain" if not orsets else ("admit" if x in orsets else "refuse"), x in gtsets) for x in tp]
        res[conv] = {"exact": sum(1 for g in gtsets if g in tp), "admit_right": vv.count(("admit", True)),
                     "admit_wrong": vv.count(("admit", False)), "refuse_right": vv.count(("refuse", True)),
                     "abstain_right": vv.count(("abstain", True)),
                     "J": [round(max((len(g & x) / len(g | x) for x in tp), default=0), 2) for g in gtsets],
                     "diff": [(lambda pb: (txt([byid[i] for i in g - pb])[:90], txt([byid[i] for i in pb - g])[:90]))(
                         max(tp, key=lambda x: len(g & x) / len(g | x), default=frozenset())) for g in gtsets]}
    res.update(exact=exact, best_jaccard=best,
               admit_right=verd.count(("admit", True)), admit_wrong=verd.count(("admit", False)),
               refuse_right=verd.count(("refuse", True)), refuse_wrong=verd.count(("refuse", False)),
               abstain_right=verd.count(("abstain", True)), abstain_wrong=verd.count(("abstain", False)),
               runs=len(runs), pieces=len(pieces))
    return res


if __name__ == "__main__":
    keys = sys.argv[3:] or list(PAGES)
    with open(f"{OUT}/results.jsonl", "a") as fo:
        for k in keys:
            r = run_page(k); print(json.dumps(r)); fo.write(json.dumps(r) + "\n")
```
