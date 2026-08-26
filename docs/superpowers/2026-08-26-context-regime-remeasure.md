# Context-regime audit — independent re-measurement (2026-08-26)

Facts only. Every command inline with raw output. No remedies proposed.

Corpus: `~/.claude/plimslop/corpus.jsonl`, **681 lines**, mtime `Aug 26 06:43`.
The audit under review reported 474 turn records and ~672 total; the corpus is live and
has grown by 8 turn records since. All deltas below are stated against the audit's figures.

```
$ ls -la ~/.claude/plimslop/ && wc -l ~/.claude/plimslop/corpus.jsonl
-rw-r--r--@  1 francoisrosselet  wheel  158906 Aug 26 06:43 corpus.jsonl
     681 /Users/francoisrosselet/.claude/plimslop/corpus.jsonl
```

## 0. Record shapes (measured, not assumed)

`head -3 … | python3 -m json.tool` **fails** (`Extra data: line 2 column 1`) — the file is
JSON Lines, one object per line, so it must be parsed line-wise.

```
$ python3 -c "…Counter(r.get('type') for r in recs)…"
total records: 681
Counter({'turn': 482, 'preflight': 149, 'block': 44, 'rework': 6})
```

Key-shape census (`Counter(tuple(sorted(d.keys())))`):

```
482 ('baseline','compacted','dropped','project','session','tokens','ts','type')
147 ('decision','declared','floor','note','project','session','session_source','shape','tokens','ts','type')
 44 ('action','baseline','floor','session','tokens','ts','type')
  3 ('confidence','method','note','project','session','target','tokens','ts','type')
  2 ('by','decision','floor','note','project','session','shape','tokens','ts','type')
  2 ('baseline','commit','commit_ts','confidence','method','note','project','session','target','tokens','ts','turn_ts','type')
  1 ('commit','commit_ts','confidence','method','note','project','session','target','tokens','ts','type')
```

One full example of each `type`:

```json
{"action":"warn","baseline":34650,"floor":50000,"session":"0e491601-…","tokens":197849,"ts":"2026-08-15T07:51:05Z","type":"block"}
{"baseline":34650,"compacted":false,"dropped":0,"project":"/Volumes/WD Green/dev/git/context-discipline","session":"0e491601-…","tokens":198485,"ts":"2026-08-15T07:52:41Z","type":"turn"}
{"by":"user","decision":"overridden","floor":50000,"note":"packaging the plugin; floor exceeded 4x, user instructed to proceed","project":"/Volumes/WD Green/dev/git/context-discipline","session":"0e491601-…","shape":"originating","tokens":212116,"ts":"2026-08-15T14:48:29Z","type":"preflight"}
{"confidence":"none","method":"unattributed","note":"abandoned before execution: the plan is the review gate; a subagent handed a finished ruling is a transcriber, and CLAUDE.md rule 1 says a transcriber cannot catch a plan defect","project":"/Volumes/WD Green/dev/git/iladub","session":null,"target":"delegating R87 plan authoring to a subagent","tokens":null,"ts":"2026-08-15T17:59:04Z","type":"rework"}
```

Note the two distinct fields on a `turn`: `tokens` (that turn's absolute context) and
`baseline` (the pre-conversation context the hook recorded for the session). **They are
different numbers**, and claim (1) is about `baseline`.

---

## (1) Session baseline — **REPRODUCED** (all three figures exact)

```
$ python3 -c "…first turn per session by ts, print ts, session[:8], tokens, baseline…"
```

| first-turn ts | session | first-turn `tokens` | `baseline` | project |
|---|---|---:|---:|---|
| 2026-08-15T07:52:41Z | 0e491601 | 198,485 | 34,650 | context-discipline |
| 2026-08-15T16:29:14Z | fa3a9815 | 15,658 | **15,658** | plimslop |
| 2026-08-15T16:49:14Z | 40adbfdc | 87,504 | 25,474 | iladub |
| 2026-08-15T17:53:06Z | 39c5a2cb | 76,551 | 25,673 | iladub |
| 2026-08-15T20:54:02Z | 6b839517 | 116,166 | 26,231 | iladub |
| 2026-08-15T21:27:04Z | 947f6849 | 118,823 | 25,655 | iladub |
| 2026-08-16T03:04:30Z | 051c08aa | 173,515 | 26,929 | iladub |
| 2026-08-17T04:10:25Z | e5589987 | 43,947 | 27,057 | iladub |
| 2026-08-17T05:00:12Z | 5e79bc6f | 63,934 | 39,204 | iladub |
| 2026-08-17T05:18:55Z | 109e9206 | 61,575 | 40,081 | iladub |
| 2026-08-17T09:28:11Z | f5742e20 | 91,922 | 41,153 | iladub |
| 2026-08-17T12:23:21Z | efa20122 | 111,756 | 40,884 | iladub |
| 2026-08-17T17:02:22Z | 6643b353 | 121,476 | 40,311 | iladub |
| 2026-08-18T04:22:02Z | 9a861c69 | 67,508 | 40,785 | iladub |
| 2026-08-20T04:41:42Z | 2c7a771f | 141,773 | 40,804 | iladub |
| 2026-08-20T07:16:00Z | 4d75a97d | 116,203 | 43,926 | iladub |
| 2026-08-20T08:52:52Z | 23bae8bb | 171,412 | **44,194** | iladub |
| 2026-08-20T10:18:22Z | c2ea865d | 99,149 | 44,181 | iladub |
| 2026-08-20T11:12:11Z | 1416d480 | 178,058 | 44,164 | iladub |
| 2026-08-20T17:26:24Z | 1f8eb791 | 81,335 | **44,193** | iladub |
| 2026-08-21T03:46:46Z | 69433ea3 | 84,381 | 44,186 | iladub |
| 2026-08-21T04:39:14Z | b6c28045 | 106,255 | 44,189 | iladub |
| 2026-08-21T06:14:12Z | f436ba37 | 93,664 | 44,211 | iladub |
| 2026-08-22T03:52:40Z | 98ba96fb | 100,273 | 44,179 | iladub |
| 2026-08-22T06:09:49Z | d9934810 | 90,301 | 44,211 | iladub |
| 2026-08-22T06:53:31Z | b4547c0f | 140,270 | 44,333 | iladub |
| 2026-08-22T07:11:01Z | 324d8c26 | 115,789 | 44,443 | iladub |
| 2026-08-23T04:26:12Z | 1ea2b6f2 | 132,703 | 44,499 | iladub |
| 2026-08-23T05:35:38Z | e4085db3 | 86,797 | 44,468 | iladub |
| 2026-08-23T06:01:16Z | 41e253a6 | 134,685 | 44,848 | iladub |
| 2026-08-23T06:30:35Z | 4de3b220 | 74,870 | 44,486 | iladub |
| 2026-08-23T08:19:08Z | 054874e4 | 79,798 | 44,621 | iladub |
| 2026-08-25T05:46:43Z | 2486a3d8 | 71,420 | 44,900 | iladub |
| 2026-08-25T06:46:45Z | 9bb5573b | 90,666 | 45,606 | iladub |
| 2026-08-25T07:35:22Z | dfbd4687 | 83,205 | 45,483 | iladub |
| 2026-08-25T08:37:46Z | 88411a57 | 106,589 | 45,467 | iladub |
| 2026-08-25T09:25:43Z | 4566f374 | 184,481 | 45,497 | iladub |
| 2026-08-25T10:29:15Z | 521dc1ac | 100,531 | 45,744 | iladub |
| 2026-08-25T11:18:17Z | ed59a1fb | 237,349 | 45,535 | iladub |
| 2026-08-25T11:35:45Z | 7f00b460 | 114,831 | 45,533 | iladub |
| 2026-08-25T12:45:43Z | abfa472a | 89,013 | 45,642 | iladub |
| 2026-08-25T13:52:51Z | 29fbbda2 | 96,214 | 45,572 | iladub |
| 2026-08-25T16:02:33Z | 88d7a667 | 123,515 | 45,645 | iladub |
| 2026-08-25T18:35:54Z | 585a336e | 118,702 | 45,602 | iladub |
| 2026-08-26T03:40:39Z | c645be47 | 49,771 | **46,243** | iladub |

45 sessions carry turn records.

- **15,658 on 2026-08-15** — exact match, session `fa3a9815` (project `plimslop`, not iladub).
  It is simultaneously the first-turn `tokens` and the `baseline`.
- **~44,190 on 2026-08-20** — five of the six 2026-08-20 sessions sit in 43,926–44,194;
  the four later ones average 44,183. Exact values 44,194 / 44,181 / 44,164 / 44,193.
  Reproduced as an approximation; the outlier is the day's first session at 40,804.
- **46,243 on 2026-08-26** — exact match, session `c645be47`.

Verdict: **REPRODUCED**, delta 0 on the two exact figures.

**Today's session baseline (2026-08-26):** two sessions have records today —
`585a336e` (baseline 45,602, carried over from 2026-08-25) and `c645be47`
(baseline **46,243**, first turn 03:40:39Z at 49,771 tokens).

---

## (2) Override rate from preflight — **REPRODUCED** (39/72 and 35/67 exact)

```
$ python3 -c "…Counter over preflight records…"
preflight records: 149
by decision: Counter({'proceed': 75, 'overridden': 39, 'stop': 19, 'handoff': 16})
by shape   : Counter({'originating': 63, 'executing': 55, 'mechanical': 31})
by declared: Counter({'proceed': 112, 'stop': 19, 'handoff': 16, None: 2})
by project : Counter({'iladub': 141, 'plimslop': 6, 'context-discipline': 2})

decision x shape:
   ('proceed','mechanical') 31   ('proceed','executing') 25   ('overridden','executing') 20
   ('overridden','originating') 19  ('proceed','originating') 19  ('stop','originating') 13
   ('handoff','originating') 12  ('stop','executing') 6  ('handoff','executing') 4

floor by shape: originating→50000 (63), executing→150000 (55), mechanical→None (31)
```

Floors are carried **in the records themselves** and match the stated floors exactly
(originating 50,000; executing 150,000; mechanical ungated/`null`).

```
$ python3 -c "…gated = shape in {originating,executing}; exceed = tokens > floor…"
gated (originating+executing) preflight records: 118
gated records whose tokens EXCEED the declared floor: 72   -> 61.0% of gated
  decision split of exceeders: Counter({'overridden': 39, 'stop': 18, 'handoff': 15})

iladub-only gated: 113  exceeding: 67  59.3%
  decision split: Counter({'overridden': 35, 'stop': 17, 'handoff': 15})

decision==overridden total: 39      decision==stop total: 19
overridden, iladub only  : 35      stop, iladub only   : 18
```

- Overall override rate among floor-exceeding preflights: **39/72 = 54.2%** — audit's 54% (39/72) **exact**.
- iladub-only: **35/67 = 52.2%** — audit's 52% (35/67) **exact**.
- **19 logged `stop` decisions** — exact (18 of the 19 are among the floor-exceeders; 18 are iladub).

Override ratio (`tokens / floor`):

```
override ratio among the 72 exceeders: median=1.81x  max=7.72x  min=1.00x
  max record: 2026-08-15T20:13:57Z originating 385,833 tokens, decision=overridden
override ratio among decision==overridden (n=39): median=1.43x  max=7.72x
```

Verdict: **REPRODUCED**, delta 0 on all three audit figures.

---

## (3) Turns under 50K — **REPRODUCED** (3; denominator 482, audit said 474)

```
$ python3 -c "…turn tokens distribution…"
turn records total: 482
under 50,000: 3
under 50,000 (iladub only): 2 of 429
min=15658 p10=105937 median=174843 p90=316225 max=426935 mean=191185

the sub-50K turns:
  2026-08-15T16:29:14Z fa3a9815  15,658  plimslop  compacted=False
  2026-08-17T04:10:25Z e5589987  43,947  iladub    compacted=False
  2026-08-26T03:40:39Z c645be47  49,771  iladub    compacted=False
```

The count **3** reproduces exactly. The denominator is **482**, not 474 — a +8 delta
explained by the corpus having grown since the audit (all 8 additions are ≥ 50K, so the
numerator is unchanged). Each of the three is the *first* turn of its session.

Verdict: **REPRODUCED**, numerator delta 0, denominator delta +8 (corpus growth).

---

## (4) Block vs warn — **REPRODUCED**, and the override is in `~/.claude/settings.json`

```
$ python3 -c "…block records…"
block records: 44
action values: Counter({'warn': 44})
floor values : Counter({50000: 44})
sessions     : 44
records with an action field of ANY type: Counter({('block','warn'): 44})
ts range: 2026-08-15T07:51:05Z -> 2026-08-26T03:57:29Z
```

44 records of `type: "block"`, **all 44 carry `action: "warn"`**, one per session, all at
the 50,000 floor. No record anywhere in the corpus carries `action` with any other value.

**Shipped default** — `/Volumes/WD Green/dev/git/plimslop/plimslop/stop.py:39-41`
(the file is at `plimslop/stop.py`, not repo-root `stop.py`):

```python
#: Enforcement strength tracks evidence grade. `originating` is literature
#: anchored, so it blocks; `executing` rests on nothing, so it must not.
DEFAULT_MODES = {"originating": "block", "executing": "warn", "mechanical": "off"}
```

`_modes()` (`:44-51`) lets `PLIMSLOP_MODE_<SHAPE>` env vars replace any of the three with
`block`/`warn`/`off`. `decide()` (`:54-80`) returns `block` only when
`modes["originating"] == "block"`.

**`~/.claude/settings.json` DOES override it.** The Stop hook command is:

```json
"Stop": [{"hooks": [{"type": "command",
  "command": "PLIMSLOP_MODE_ORIGINATING=warn PYTHONPATH=\"/Volumes/WD Green/dev/git/plimslop\" python3 -m plimslop.stop 2>/dev/null || true",
  "timeout": 10}]}]
```

`PLIMSLOP_MODE_ORIGINATING=warn` is set inline on the hook command, downgrading the shipped
`block` to `warn`. (The `UserPromptSubmit` hook runs `plimslop.hook` with no such override.)

The second, independent downgrade path in `stop.py:68-73` — return `warn` whenever
`session.baseline >= LOWEST_FLOOR`, because the gate would otherwise be unsatisfiable — is
**not** what produced these 44 records:

```
$ python3 -c "…block records with baseline >= 50000…"
block records with baseline >= 50000 (would warn anyway per stop.py:68): 0 of 44
max baseline among block records: 46243
```

Every one of the 44 has a baseline below 50,000, so all 44 reached the `mode == "warn"`
branch at `:78` via the settings.json env var.

Verdict: **REPRODUCED**, delta 0.

---

## Summary

| Claim | Audit | Measured | Verdict |
|---|---|---|---|
| (1) baselines 15,658 / ~44,190 / 46,243 | 3 figures | 15,658; 44,164–44,194 (four late 08-20 sessions avg 44,183); 46,243 | **REPRODUCED** |
| (2) override 54% (39/72), iladub 52% (35/67), 19 stops | — | 39/72 = 54.2%; 35/67 = 52.2%; 19 stops | **REPRODUCED** |
| (3) 3 of 474 turns under 50K | 3/474 | 3/482 | **REPRODUCED** (denominator +8, corpus grew) |
| (4) all 44 block records `action: "warn"` | 44 | 44/44 warn | **REPRODUCED** |

Median override ratio among the 72 floor-exceeding preflights: **1.81x**; max **7.72x**
(385,833 tokens against a 50,000 originating floor, 2026-08-15T20:13:57Z).
