# Spec — the register serves the arc: a loop names what it serves, selection comes from the arc, and a row can be PARKED

**Residue:** none — a process spec. **Question inherited:**
`docs/superpowers/2026-09-11-the-register-serves-the-arc-handoff.md` § 5a (ASSERTED: write this
spec) and § 5b (PROPOSED: residues cluster under a few architectural questions — falsified here,
§ 2). **Serves:** maintenance — this loop moves no criterion; it changes how the next ones are chosen.
**Written 2026-09-11**, off `3635e08`, branch `the-register-serves-the-arc-spec`, at ~32K working
tokens (under the originating floor).
**Doc impact: none.** No published term changes. The rules below bind handoffs, the register and two
repo-internal instruments (`scripts/cockpit.py`, `scripts/residue_graph.py`); the one Contract edit
(§ 3.3, CLAUDE.md § Deferred residues) is proposed here and made only on the maintainer's explicit
request, as that section's class requires.

---

## 1. The mechanism, measured — the register moves, the arc does not, and nothing joins them

The handoff's part 2 carries the figures at `0bc7aca` (arc line `etkl 2/7 · dec 11/17 · holon 5/6
· tab 1/10 · substrate 0/3 · frontier 13 · ready 15`; last `prog:met` flip 2026-08-31; 13 frontier
rows, all August, all open). Re-measured 2026-09-11 at `3635e08`, and extended:

```
$ ls docs/superpowers/2026-09-*handoff*.md | wc -l                          47
$ grep -l "prog:criterion" docs/superpowers/2026-09-*handoff*.md | wc -l     1   (the 2026-09-11 handoff itself)
$ rows closed in September (CLOSED 2026-09-* stamps, residues-closed.md)     21
  of those named by any prog:blockedBy                                        0
$ open rows numbered >= 150                                                  36   (23 more are closed)
```

**The handoff's "61 open rows ≥ 150" is wrong; the population is 36.** The 59 numbers from R150 to
R208 are 36 open + 23 closed rows, so § 5b's triage is over 36, not 61. Corrected here because the
handoff is Evidence and cannot be edited.

**The graph measurement that decides this spec.** On `scripts/residue_graph.py --json` (198 rows,
166 `[[R…]]` edges, 13 criterion→row edges), restricting traversal to OPEN rows:

```
open rows connected to a frontier row through open rows only:  13  — the 13 frontier rows themselves
open rows with no open neighbour and not named by a criterion: 78  of 133 open
```

**No open row links to any frontier row, directly or through other open rows.** The 79-row live
component reaches the frontier (R97, R99) only through closed rows. The September chain is not
merely un-named by the arc; it is disconnected from it in the register's own link graph. Every
`[[R…]]` a September row wrote points sideways into its own chain.

## 2. § 5b falsified — the rows do cluster, and half the clusters bear on no criterion

The 36 open rows ≥ 150, triaged by the question each bears on (from the index text and the row's
links; the assignment is a reading and is listed so it can be disputed row by row):

| question | rows | n | criterion it bears on |
| --- | --- | --- | --- |
| which line is the header, whose reading has authority | R155 R160 R162 R166 R180 R201 R203 R204 R205 | 9 | etkl:05, etkl:06; tab:02, tab:05, tab:08 |
| the one-band run's mechanics (R165's children) | R168 R169 R170 R171 R202 | 5 | the same, indirectly (bfs, apple) |
| what the evidence-doc figure gates may fire on | R188 R190 R192 R193 R194 R195 R196 R197 R199 R200 | 10 | **none** |
| what CI and the declaration lints can see | R150 R151 R153 R173 R184 | 5 | **none** (R151: holon:02→01 edge; no row blocks it) |
| method rows (a census's scope or power) | R157 R159 R164 R191 | 4 | none by construction |
| singletons | R156 (cbh weld → tab:01), R163 (MATRIX_AMBIGUOUS reason → tab:05), R206 (GLiNER2) | 3 | mixed |

**What holds of § 5b:** 29 of 36 fall under four questions; the register is a tree with few roots.
**What fails:** the middle layer would not make them closable against the arc, because two of the
four roots — 15 rows, including both open hubs R188 (in-degree 8) and R173 (in-degree 10) — bear on
**no criterion of any rung**. They are the repo's discipline about its own evidence and its own CI,
and the arc counts documents compiled, shapes shipped, escalations disposed. A `res:question` term
linking them to criteria would have nothing to link to. **So the layer is not built** (§ 6). What
is built instead is the typed declaration in § 3.1, whose `maintenance` value *is* the name for
exactly this class, and a fork for the maintainer (§ 4).

## 3. The three changes — one rule each, its expression, its oracle, and what it must not touch

Two conventions already in the repo are reused rather than invented: the handoff header's bold
`**Field:**` lines that `scripts/cockpit.py` reads (`topic()` reads `**Topic:**`), and the index
status cell's **parenthetical qualifier**, which `tests/test_residue_register_integrity.py:40`
already routes on the first word alone (`_INDEX_ROW = ^\| *(R\d+) *\| *([A-Za-z]+)[^|]*\|`) and
which two live rows already use (`R131 | open (half (a) …`, `R141 | open (code landed)`).

### 3.1 A loop names the criterion it serves, or declares itself maintenance

**Rule.** Every dated handoff or brief under `docs/superpowers/` written after this spec carries one
header line `**Serves:** <value>`, where `<value>` is a criterion IRI present as a top-level subject
in `tests/arc-manifest.ttl` (`prog:criterion:etkl:05`) or the literal `maintenance`. It names what
the document's part 5a would advance if it succeeded. Anything else — prose, a rung name, a residue
number — is a refusal, not a default: the strip prints nothing rather than guessing, exactly as
`topic()` does.

**Expression.** `cockpit.serves()` beside `topic()`, same file, same regex family; the manifest's
criterion IRIs are read with the `_CRITERION` regex the strip already trusts (its performance
contract forbids rdflib there). `work()` renders `topic · serves · subject · branch`; `maintenance`
renders as the word, a criterion as its `rung:nn`.

**Oracle (falsifying).** Fixture tests in `tests/test_cockpit.py`, the shape of
`test_the_work_line_renders_the_declared_topic`: (i) a doc declaring `prog:criterion:etkl:05`
renders `etkl:05`; (ii) a doc declaring `maintenance` renders `maintenance`; (iii) a doc declaring
`prog:criterion:etkl:99` — not in the manifest — renders no segment; (iv) no line, no segment. Plus
the live half, `test_the_live_newest_handoff_declares_what_it_serves`, the shape of
`test_the_live_newest_handoff_declares_a_topic`. Falsification per task: delete the criterion
membership check and (iii) must go red.

**Must not touch.** The 47 September handoffs are Evidence (append-only, prospective from
`5743af3`); nothing is backfilled. The rule binds the newest document only, which is why the live
test is on `_newest_loop_doc()` and not a census. This document's own header carries the line.

### 3.2 Selection comes from the arc, not from the newest handoff

**Rule.** A handoff's § 5a names its subject from the strip's `ready` or `frontier` derivations
(`vocab/queries/arc-unblocked.rq`, `arc-frontier.rq`) — the criterion first, then the register row
that blocks it — or declares `maintenance` and says in one sentence why the arc is not served
this loop. `residues.md` is opened to find what blocks a chosen criterion, never to find a subject.

**Expression.** No new instrument decides this; a reading judgement cannot be lint-checked without
a tuned proxy. What is built is the **measure**: `cockpit.serves_window()` — over the trailing
`_WINDOW` days the strip already uses for velocity, the count of dated handoffs/briefs whose
`Serves:` is a criterion, `maintenance`, or absent — rendered on the arc line as
`serves a/m/–` beside `frontier` and `ready`. Three counts, no threshold, no verdict: the same
posture as `frontier 13`.

**Oracle (falsifying).** The prediction this spec makes, typed PROPOSED: **once the line exists,
the criterion count in the window leaves zero within the next three loops.** If three consecutive
loops declare `maintenance` while `ready` stays at 15, the handoff-selection mechanism was not the
cause of the flat arc line, and § 4's fork is the remedy, not this rule. Today's reading is the
baseline: `serves 0/0/47` over the 47 September documents (`serves 0/1/…` once this spec's handoff
lands).

**Must not touch.** `frontier`/`ready` are counts, not verdicts (handoff part 1); the new segment is
the same. No loop is refused for declaring maintenance.

### 3.3 A third register state, PARKED — a qualifier on `open`, never a third file or a closure

**Rule.** A parked row is one the maintainer has decided, by date, not to pursue: it stays open,
keeps its evidence, keeps its number in the tally's denominator, and is never struck. Parking is a
**decision by the maintainer, in one triage pass, recorded with a date and a reason** — never by
a loop, never by an instrument, never by age. Only a row that is (a) named by no `prog:blockedBy`
and (b) has no OPEN neighbour in the register's link graph may be parked; today that set is **78
of 133 open rows** (§ 1), of which 13 are numbered ≥ 150. A parked row is **unparked by the first
loop that cites it** (`[[Rn]]` in a new row or a handoff § 5a) or the first criterion that names
it — the qualifier is removed in that same change.

**Expression.** In `residues.md` the status cell reads `open (parked YYYY-MM-DD)`; in
`residues-open.md` the row appends `**PARKED YYYY-MM-DD:** <reason>` and moves nowhere. This keeps
every existing reader correct without redefinition: the integrity test routes on `open`;
`cockpit.residues()` counts `^\| R\d+ \|` and `\| closed \|`, so `c/t` is untouched and a parked
row is an open one in both numerator and denominator; the `(c/t closed)` raise-time snapshot the
maintainer ruled is not redefined, because parking changes neither `c` nor `t`. Two instruments
gain a count: `cockpit.residues()` renders `parked n` after `closed`, and
`scripts/residue_graph.py` reports parked as a status.

**One instrument is wrong today and must be fixed first.** `residue_graph.py:43`'s index regex
`\| (\w+) \| ` requires the status word to be followed directly by ` | `, so a qualified status is
**dropped**: it reads 133 open rows where the index has 135 — R131 and R141 are missing from the
graph. A parked qualifier would silently remove every parked row from the very graph that decides
whether a row may be parked. The fix is the integrity test's regex (`([A-Za-z]+)[^|]*`), and its
oracle is that the script's row count equals the integrity test's.

**Oracle (falsifying).** (i) Integrity test: a parked index row routes to `residues-open.md` and is
not struck — extend `test_a_row_is_struck_if_and_only_if_it_is_filed_closed` with a parked fixture.
(ii) A new test in the M7 environment leg's style (`tests/test_arc_manifest.py:333` reads the
register from the filesystem): **a row named by `prog:blockedBy` may not carry `parked`** — fixture
manifest naming a parked row must be refused. (iii) `cockpit.residues()` on a fixture index with one
parked row returns the same `closed, total` as without the qualifier and `parked == 1`. Falsification:
strip the qualifier handling and (iii)'s parked count must fall to 0 while `c/t` stays — that is the
proof parking never touched the tally.

**Must not touch.** The `(c/t closed)` convention (CLAUDE.md § Deferred residues); the never-delete
rule; `residues-closed.md`. **No row is parked by this loop** — the triage pass is the maintainer's
and is § 7's last task, gated on their presence.

## 4. The fork this spec hands the maintainer — what counts the 15 rows that serve nothing

Fifteen open rows (§ 2, the two "none" clusters) are work no rung counts. Two arms, neither taken
here:

- **(A) `maintenance` is their name and that is enough.** The arc counts the product; the
  evidence discipline is the cost of producing it, visible on the strip as `serves a/m/–` and
  bounded by § 3.2's prediction. Recommended: it adds no vocabulary and the strip already shows
  whether maintenance is crowding out the arc.
- **(B) A sixth rung, or criteria under an existing one, for the repo's own evidence discipline.**
  Rungs are settled at five and unordered (`tests/arc-manifest.ttl` header, decision 8); adding one
  is the maintainer's ruling, and it would make R173 and R188 frontier rows overnight — which is
  either the honest count or a way to let the register keep steering the arc from inside.

## 5. Global constraints

- **CLAUDE.md § 8 gate.** Every change here is PROCEDURAL: reading markdown and a Turtle file by
  regex in `scripts/cockpit.py`, under that file's stated performance contract (no rdflib), and a
  filesystem check in the M7 style. No tuned constant: `_WINDOW` is reused, not introduced; the
  parked-candidate condition is structural (named / has an open neighbour), not aged.
- **Evidence is append-only.** No handoff is edited; the 61→36 correction lives here and in this
  loop's handoff.
- **The tally convention is the maintainer's** and is cited, not restated: CLAUDE.md § Deferred
  residues.
- **Plan discipline (CLAUDE.md § Plan authoring).** The plan that follows states signatures and the
  oracles above; falsification per task; the live test in § 3.1 is the one test that goes RED on
  the current tree only if this spec's own handoff omits the line — the plan must say so.

## 6. What this loop does NOT do, and why

- **No `res:`/`prog:` question layer.** § 2: two of four roots have no criterion to link to.
- **No new criteria or rung.** § 4 is the maintainer's fork.
- **No backfill of `Serves:` into 47 handoffs.** Evidence rule; and a backfilled value is a fact
  the backfiller made up.
- **No automatic parking, no age rule.** A row parked by a clock is a tuned constant wearing a
  process.
- **No parked detail file.** A third file would need a third routing word, and the integrity test's
  two-word membrane is the thing that stopped R87/R88 from being consumed as fact.
- **The donation plan** (`plans/2026-09-11-grid-donation.md`) is unaffected; when it ships, its
  handoff declares `**Serves:** prog:criterion:etkl:05`.

## 7. The plan's task list (interfaces only; the plan supplies oracles verbatim, bodies never)

1. `residue_graph.py` status regex → integrity-test regex; oracle: row count 198 with 135 open.
2. `cockpit.serves()` + `work()` segment + the four fixture tests + the live test (§ 3.1).
3. `cockpit.serves_window()` + arc-line segment `serves a/m/–` + fixture test (§ 3.2).
4. PARKED: integrity fixture, M7-style refusal, `residues()` parked count (§ 3.3).
5. CLAUDE.md § Deferred residues: the PARKED paragraph and the `Serves:` line — **on the
   maintainer's explicit request only**; the plan carries the proposed text.
6. The triage pass — **maintainer present**: the 78 candidates, parked by decision, dated.
