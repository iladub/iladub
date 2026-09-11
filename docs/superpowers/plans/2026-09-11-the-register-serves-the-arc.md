# The register serves the arc — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Topic:** register-serves-arc · **Serves:** maintenance — this plan moves no criterion; it changes
how the next subject is chosen. · **Written 2026-09-11**, branch `the-register-serves-the-arc-plan`,
stacked on `the-register-serves-the-arc-spec` (PR #201, `test` in progress when this was cut), at
~30K working tokens.

**Goal:** every loop document declares what it serves, the strip counts those declarations beside
`frontier` and `ready`, and a register row can be PARKED by the maintainer without leaving the tally
or the graph — with the one instrument that would silently drop a parked row fixed first.

**Architecture:** three regex readers over markdown and one Turtle file, all inside instruments the
repo already has. `scripts/cockpit.py` gains `serves()`, `serves_window()` and `parked()` beside
`topic()` and `residues()`, under its performance contract (no rdflib). `scripts/residue_graph.py`
reads a qualified status the way `tests/test_residue_register_integrity.py:40` already does, and
reports the structural parking candidates. `tests/test_arc_manifest.py`'s environment leg gains
**M21**: a criterion may not be `prog:blockedBy` a parked row. Nothing decides anything: three
counts, one refusal, no threshold.

**Tech Stack:** Python 3.12 under `.venv/bin/python` (never `python3` — `tests/test_arc_manifest.py`
docstring), pytest, `re`. rdflib only inside tests.

**Spec:** `docs/superpowers/specs/2026-09-11-the-register-serves-the-arc-design.md` — § 3.1–3.3
carry each rule, its expression, its oracle and what it must not touch; § 7 is the task list this
plan expands. **Cite the spec, do not re-derive it** (CLAUDE.md § Plan authoring rule 6).

**Doc impact: none.** No published term changes; `prog:` is repo-internal
(`tests/arc-manifest.ttl` header). The one Contract edit is task 5, gated on the maintainer.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **CLAUDE.md § 8 gate — every change is PROCEDURAL** (spec § 5): reading markdown and a Turtle
   file by regex, and a filesystem fact no SHACL engine can see (the M7 argument,
   `tests/test_arc_manifest.py:1-35`). **No tuned constant.** `_WINDOW` (`scripts/cockpit.py:103`)
   is reused, never introduced; the parking-candidate condition is structural — *named by no
   `prog:blockedBy`* and *no OPEN neighbour* — never an age. A date literal in a status cell is a
   record, not a threshold.
2. **Evidence is append-only** (CLAUDE.md § Documentation governance). No file under
   `docs/superpowers/` dated before this plan is edited. The 47 September handoffs never receive a
   `Serves:` line. The spec's `61 → 36` correction stays where the spec put it.
3. **The tally convention is the maintainer's** (CLAUDE.md § Deferred residues) and is cited, not
   restated. A parked row is `open`: it is in `t`, not in `c`, and its `(c/t closed)` snapshot is
   untouched. **No row is parked by this plan's tasks 1–4.**
4. **Plan rules 1–7 (CLAUDE.md § Plan authoring).** No function body appears here. Tests are
   supplied verbatim and are **propositions**: a test that cannot be made to pass has found a plan
   or spec defect — say so in the task report and substitute the satisfiable form carrying the same
   force; never weaken the assertion. **Every task ships a `## FALSIFICATION` block** (rule 4).
5. **The cockpit's performance contract** (`scripts/cockpit.py:76-80`): no rdflib, no network, no
   pytest, no corpus; a render reads a few small files. `serves_window()` reads the first 4000
   characters of each dated loop document in the window — the same slice `topic()` reads
   (`cockpit.py:322`) — and nothing more.
6. **Two readers of one fact must agree** (`cockpit.py:37-45`). The manifest membership `serves()`
   checks is read by the `_CRITERION` regex (`cockpit.py:188`), which M9/M9b license; the test in
   task 2 pins the regex's criterion set against rdflib's typed-node set, the same way
   `test_the_strips_reading_equals_rdflibs_reading_of_the_same_file` pins `arc()`.
7. **A refusal is not a default** (spec § 3.1). Wherever a value is absent, malformed, or not in
   the manifest, the strip prints nothing or `?` — never a guess.

## Measured before writing (`main` at `72a608a` + spec commit `f1129a9`, 2026-09-11)

Every load-bearing claim below carries its measurement (rule 2). Re-measure any that a task depends
on **after** the edits that precede it (rule 7).

| claim | measurement |
| --- | --- |
| `residue_graph.py` drops the two qualified rows | `.venv/bin/python scripts/residue_graph.py` → `rows 198 … 46 open` in the largest component, and its `status` dict has **196** entries, 133 `open`; the integrity regex over the same index gives **198 / 135**. The two missing: **R131, R141** (`residues.md:255,265`). The script's `rows` dict (from the detail files) has all 198, so the JSON already emits those two nodes with `"status": null`. |
| the integrity regex | `tests/test_residue_register_integrity.py:40`: `^\| *(R\d+) *\| *([A-Za-z]+)[^|]*\|` |
| the parking candidates, once the graph reads all 135 open rows | open ∧ not named by any `prog:blockedBy` ∧ no open neighbour in either direction: **80 rows** (13 numbered ≥ 150). **The spec's 78 was counted on 133 open rows**; R131 and R141 both qualify structurally, so the corrected figure is 80. Task 4's oracle uses 80. |
| the live `Serves:` line | exactly one in the repo: `docs/superpowers/2026-09-11-the-register-serves-the-arc-spec-handoff.md:4` = `**Serves:** maintenance — the loop changes how …`. The value is the **first token**; prose follows after ` — `. |
| the newest loop doc today | `cockpit._newest_loop_doc()` → that same handoff; `topic()` → `register-serves-ar` (18-char cut). |
| loop docs in the trailing 7 days / in September | `ls docs/superpowers/ \| grep -E "^2026-09-(0[5-9]\|1[01]).*(handoff\|brief).*\.md$" \| wc -l` → **35**; all September → **48** (the spec counted 47 before its own handoff landed). |
| `_criteria()` drops a criterion with no `prog:met` | `cockpit.py:225-226` — so membership must be read from `_CRITERION` matches directly, not from `_criteria()`. |
| `_CRITERION` captures the rung only | `cockpit.py:188`: one group, `([A-Za-z0-9_-]+)`, and the slug is `[A-Za-z0-9_.-]+` uncaptured. |
| `residues()` has five 3-tuple unpack sites | `cockpit.py:380` and `tests/test_cockpit.py:147,231,242,251`. Widening the tuple would touch all five; a sibling `parked()` touches none. |
| the arc line may carry **no digit** with no manifest | `tests/test_cockpit.py:132`: `assert not re.search(r"\d", arc_line)`. A `serves 0/1/34` segment with the manifest absent would fail it. |
| verdict words the strip may not emit | `tests/test_cockpit.py:197`: `{"stuck","stalled","blocked","ok","healthy","converging"}`. `parked`, `serves`, `maintenance` are not among them. |
| M7 helpers | `tests/test_arc_manifest.py:63` `REGISTER`, `:118` `blocked_rows(graph)`, `:237` `register_rows()` (`@lru_cache(maxsize=1)`, frozenset of ids), `:294` `environment_refusals(graph)`, `:331-335` the M7 branch, `:678` `test_m7_…`, fixture `tests/arc-m7-dangling-residue-leak.ttl` (names `R999`). `_refused_by_environment` (`:355`) asserts SHACL-clean **and** exact refusal set. |
| free refusal number | `grep -rn "M20\b\|M21\b" tests/ docs/superpowers/specs/ scripts/` → M20 is reserved for R116 (`specs/2026-08-23-the-faithful-worktree-design.md:264`), M11 for R106 (`tests/arc-shapes.ttl:24`); **M21 is unclaimed.** |
| refusal counts stated in prose | `tests/test_arc_manifest.py:1,6` ("eighteen"; "Fifteen of the eighteen … NOT here"; five environment questions listed `:19-25`); `tests/arc-shapes.ttl:10-13` ("FOURTEEN of the EIGHTEEN"); `environment_refusals` docstring `:295`. No test asserts the number; the prose is what task 4 updates. |
| `Doc impact:` is read by regex | `tests/docgov_extract.py:114`: `\*{0,2}Doc impact:\*{0,2}\s*(none\|increment\|contradiction)\b` — this plan's header form is that form. |
| the live-newest-handoff pin | `tests/test_cockpit.py:291` requires the newest loop doc to declare `**Topic:**`; task 2 adds the `Serves:` twin. PR #198 failed CI on the Topic half once (memory). |

---

### Task 1: `residue_graph.py` reads a qualified status

**Files:**
- Modify: `scripts/residue_graph.py:41-47` (`read_rows`, the index loop)
- Create: `tests/test_residue_graph.py`

**Interfaces:**
- Consumes: `tests/test_residue_register_integrity.py::index_rows()` — `{id: status}` over the index,
  the reader of record for the index (its regex is the one the spec names, § 3.3).
- Produces: `read_rows() -> tuple[dict[int, set[int]], dict[int, str], dict[int, str]]` unchanged
  in shape; `status[n]` is the **first word** of the status cell for every index row, never dropped
  for a qualifier. Task 4 extends this same function with a fourth return value.

**Invariant.** The set of ids and the status word the script reads equal what `index_rows()` reads,
row for row. The label text (group 3 today) is unchanged for unqualified rows.

- [ ] **Step 1: Write the failing test**

```python
"""`scripts/residue_graph.py` — the register as a graph. It must read every index row the
integrity test reads, or the graph it draws is missing the rows it cannot parse.

Measured 2026-09-11 before this test existed: the script's index regex required the status word
to be followed directly by ` | `, so the two rows whose status carries a parenthetical qualifier
(`R131 | open (half (a) done)`, `R141 | open (code landed)`) were absent from its `status` dict —
196 rows read where the index has 198. A parked qualifier (spec 2026-09-11 § 3.3) would drop every
parked row from the very graph that decides whether a row may be parked.
"""
from scripts import residue_graph
from tests.test_residue_register_integrity import index_rows


def test_the_graph_reads_every_index_row_the_integrity_test_reads():
    _rows, status, _label = residue_graph.read_rows()
    expected = {int(rid[1:]): s for rid, s in index_rows().items()}
    assert status == expected, (
        f"the graph and the integrity test disagree about the index: "
        f"missing {sorted(set(expected) - set(status))}, "
        f"extra {sorted(set(status) - set(expected))}, "
        f"differing {[n for n in status if n in expected and status[n] != expected[n]]}")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_residue_graph.py -q`
Expected: FAIL — `missing [131, 141]`.

- [ ] **Step 3: Replace the index regex**

Replace the pattern at `scripts/residue_graph.py:43` with one whose status group is the integrity
test's — `([A-Za-z]+)` followed by `[^|]*` to swallow the qualifier — and whose label group still
captures the third cell. State the regex once in the code with a comment citing
`tests/test_residue_register_integrity.py:40` as the reader of record. Do not touch `rows` (the
detail-file loop) or `read_criteria`.

- [ ] **Step 4: Run the test and the script**

Run: `.venv/bin/python -m pytest tests/test_residue_graph.py tests/test_residue_register_integrity.py -q`
Expected: PASS. Then `.venv/bin/python scripts/residue_graph.py` — the `largest … open` figure and
the hubs line must be **unchanged** (R131/R141 are not hubs and their status was `None` before, so
only counts that key on `status == 'open'` may move; record the before/after lines in the task
report).

- [ ] **Step 5: Commit**

```bash
git add scripts/residue_graph.py tests/test_residue_graph.py
git commit -m "fix(residue_graph): read a qualified status word the way the integrity test does — R131/R141 were dropped"
```

## FALSIFICATION (Task 1)
Restore the old regex (`(\w+) \| `), run step 4's test: it must go RED with `missing [131, 141]`.
Restore the new one, suite green. Paste both runs in the task report.

---

### Task 2: `cockpit.serves()` — the newest loop document names what it serves

**Files:**
- Modify: `scripts/cockpit.py` — `_CRITERION` (`:188`), new `_criterion_ids()`, new `_serves_of(path)`,
  new `serves()`, `work()` (`:326-340`)
- Modify: `tests/test_cockpit.py` — five new tests
- Modify: `docs/superpowers/2026-09-11-the-register-serves-the-arc-the-plan-handoff.md` already carries
  `**Serves:** maintenance` (this loop's handoff; see § Handoff below) — nothing to edit, verify only.

**Interfaces:**
- Consumes: `_newest_loop_doc() -> str | None` (`cockpit.py:283`), `_read(path)`, `ARC_MANIFEST`.
- Produces:
  - `_CRITERION` gains a **second group** capturing the slug (`[A-Za-z0-9_.-]+`); group 1 is unchanged
    so `_criteria()` (`:216`) needs no edit.
  - `_criterion_ids() -> frozenset[str]` — every `"<rung>:<slug>"` whose subject line `_CRITERION`
    matches, **met or not, `prog:met` present or not** (measured: `_criteria()` drops the latter).
    Empty frozenset when the manifest is unreadable.
  - `_serves_of(path: str) -> str | None` — reads `^\*\*Serves:\*\*\s*(\S+)` (re.M) over the first
    4000 characters; returns `"maintenance"` for that literal token, `"<rung>:<slug>"` when the token
    is `prog:criterion:<rung>:<slug>` **and** that id is in `_criterion_ids()`, else `None`. Task 3
    calls this per file.
  - `serves() -> str | None` — `_serves_of(_newest_loop_doc())`, `None` when there is no doc.
  - `work() -> str` renders `topic · serves · subject · branch`, each part dropped when its source
    is silent (the existing rule, `:333-335`).

**Invariants.** (a) The value is the first whitespace-delimited token after the field, so the live
line `**Serves:** maintenance — the loop …` reads `maintenance` (measured, handoff `:4`). (b) A
token that is neither `maintenance` nor a manifest criterion yields `None` — no segment, no
fallback (Global Constraint 7). (c) With `ARC_MANIFEST` absent, a criterion token yields `None`
(membership is unknowable) while `maintenance` still renders — it needs no manifest.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_cockpit.py`)

```python
_MANIFEST_1 = ('@prefix prog: <https://w3id.org/iladub/progress#> .\n'
               'prog:criterion:etkl:05 a prog:Criterion ;\n'
               '    prog:ofRung "etkl" ;\n'
               '    prog:met false .\n')


def _serves_doc(tmp_path, monkeypatch, header: str, manifest: str | None = _MANIFEST_1):
    """A newest loop doc with the given header line, against a one-criterion manifest."""
    doc = tmp_path / "2026-09-11-a-loop-handoff.md"
    doc.write_text(f"# t\n\n**Topic:** etkl · **Date:** 2026-09-11 ·\n{header}\n", encoding="utf-8")
    monkeypatch.setattr(cockpit, "_newest_loop_doc", lambda: str(doc))
    monkeypatch.setattr(cockpit, "_run", lambda *a: "a-branch\n")
    if manifest is None:
        monkeypatch.setattr(cockpit, "ARC_MANIFEST", str(tmp_path / "absent.ttl"))
    else:
        m = tmp_path / "manifest.ttl"
        m.write_text(manifest, encoding="utf-8")
        monkeypatch.setattr(cockpit, "ARC_MANIFEST", str(m))


def test_a_document_that_serves_a_criterion_renders_its_rung_and_slug(tmp_path, monkeypatch):
    """Spec 2026-09-11 § 3.1 (i): `prog:criterion:etkl:05` in the manifest renders `etkl:05`."""
    _serves_doc(tmp_path, monkeypatch, "**Serves:** prog:criterion:etkl:05")
    assert cockpit.serves() == "etkl:05"
    assert cockpit.work() == "etkl · etkl:05 · a-loop · a-branch"


def test_a_document_that_declares_maintenance_renders_the_word(tmp_path, monkeypatch):
    """§ 3.1 (ii). The value is the first token: the live handoff writes
    `**Serves:** maintenance — <why>` and the prose after the dash is not the value."""
    _serves_doc(tmp_path, monkeypatch, "**Serves:** maintenance — this loop moves no criterion")
    assert cockpit.serves() == "maintenance"
    assert cockpit.work() == "etkl · maintenance · a-loop · a-branch"


def test_a_criterion_absent_from_the_manifest_renders_no_segment(tmp_path, monkeypatch):
    """§ 3.1 (iii): a refusal, not a default. `etkl:99` is not a top-level subject."""
    _serves_doc(tmp_path, monkeypatch, "**Serves:** prog:criterion:etkl:99")
    assert cockpit.serves() is None
    assert cockpit.work() == "etkl · a-loop · a-branch"


def test_a_document_with_no_serves_line_gets_none_invented(tmp_path, monkeypatch):
    """§ 3.1 (iv)."""
    _serves_doc(tmp_path, monkeypatch, "")
    assert cockpit.serves() is None
    assert cockpit.work() == "etkl · a-loop · a-branch"


def test_prose_in_the_serves_field_is_refused_not_read(tmp_path, monkeypatch):
    """`the etkl rung` is neither the literal nor an IRI; the strip prints nothing rather than
    guessing, exactly as `topic()` does with an absent field."""
    _serves_doc(tmp_path, monkeypatch, "**Serves:** the etkl rung")
    assert cockpit.serves() is None


def test_the_criterion_ids_the_regex_reads_equal_rdflibs_typed_nodes():
    """Global Constraint 6: `_criterion_ids()` is a second reader of the manifest, and gets the
    same pin `arc()` has. Every `prog:Criterion` typed node, met or not, must be in the set."""
    from rdflib import RDF, Graph, Namespace
    prog = Namespace("https://w3id.org/iladub/progress#")
    g = Graph()
    g.parse(cockpit.ARC_MANIFEST, format="turtle")
    typed = {str(s).rsplit("criterion:", 1)[1] for s in g.subjects(RDF.type, prog.Criterion)}
    assert cockpit._criterion_ids() == frozenset(typed), (
        "the regex reader and rdflib disagree about which criteria exist; rdflib is right")


def test_the_live_newest_handoff_declares_what_it_serves():
    """The live half of § 3.1, the twin of `test_the_live_newest_handoff_declares_a_topic`:
    whatever a fresh session would open right now must say what it serves — a criterion IRI in
    `tests/arc-manifest.ttl` or the literal `maintenance`. This is the one test that goes RED on
    the current tree only if the newest handoff omits the line (spec § 5)."""
    path = cockpit._newest_loop_doc()
    assert path is not None, "no dated brief/handoff on disk"
    assert cockpit.serves() is not None, (
        f"{path} declares no readable `**Serves:**` — a criterion IRI present in the manifest, "
        "or `maintenance`")
```

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_cockpit.py -q -k "serves or criterion_ids"`
Expected: FAIL — `AttributeError: module 'scripts.cockpit' has no attribute 'serves'` (and
`_criterion_ids`).

- [ ] **Step 3: Implement**

In `scripts/cockpit.py`: add the slug group to `_CRITERION`; write `_criterion_ids()`,
`_serves_of()`, `serves()` beside `topic()` with a docstring stating that `Serves:` is the second
AUTHORED figure on the strip and what bounds it (the manifest membership — unlike `topic()`, a
criterion value IS checked against a named set, which is the strengthening `topic()`'s docstring
`:316-318` asked for and did not build); extend `work()`'s `parts` tuple to
`(topic(), serves(), entry_point())`. **MEASURE before editing `work()`** that
`test_the_work_line_degrades_on_a_detached_head` (`:281`) monkeypatches `topic` and `entry_point`
but not `serves` — with a live newest doc declaring `maintenance`, that test's expected
`"some-loop"` would become `"maintenance · some-loop"`. Add `monkeypatch.setattr(cockpit, "serves",
lambda: None)` to that test and say so in the task report; that is a test whose premise moved,
not a weakened assertion.

- [ ] **Step 4: Run the whole cockpit file**

Run: `.venv/bin/python -m pytest tests/test_cockpit.py -q`
Expected: all PASS, including the two pre-existing agreement tests. Then
`.venv/bin/python scripts/cockpit.py --no-color --refresh` and paste line 1 in the task report —
it must now read `register-serves-ar · maintenance · …`.

- [ ] **Step 5: Commit**

```bash
git add scripts/cockpit.py tests/test_cockpit.py
git commit -m "feat(cockpit): serves() — the newest loop doc names the criterion it serves, or maintenance; refused values print nothing"
```

## FALSIFICATION (Task 2)
Delete the membership check in `_serves_of` (return the id for any `prog:criterion:` token):
`test_a_criterion_absent_from_the_manifest_renders_no_segment` must go RED. Restore; green. Second
arm: temporarily rename the live handoff's `**Serves:**` to `**Server:**` in the working tree;
`test_the_live_newest_handoff_declares_what_it_serves` must go RED; `git checkout` the file; green.

---

### Task 3: `cockpit.serves_window()` — three counts on the arc line

**Files:**
- Modify: `scripts/cockpit.py` — `_newest_loop_doc()` (`:283-292`) refactored over a new
  `_loop_docs()`, new `serves_window()`, `_arc_line()` (`:348-370`)
- Modify: `tests/test_cockpit.py` — two new tests; one existing test extended

**Interfaces:**
- Consumes: `_serves_of(path)` (task 2), `_WINDOW` (`:103`), `_criterion_ids()`.
- Produces:
  - `_loop_docs() -> list[str]` — absolute paths of every `YYYY-MM-DD-*.md` under
    `docs/superpowers/` whose name contains `handoff` or `brief` (the filter `_newest_loop_doc`
    already applies, `:288-289`); `[]` on `OSError`. `_newest_loop_doc()` becomes `max()` over it by
    basename and is otherwise unchanged.
  - `serves_window() -> tuple[int, int, int] | None` — over the docs whose filename date `d`
    satisfies `(today - d).days < _WINDOW` (the comparison `velocity()` uses, `:169`): the count
    whose `_serves_of` is a criterion id, the count that is `"maintenance"`, the count that is
    `None`. **`None` when `_criterion_ids()` is empty** (manifest unreadable), for the reason
    `frontier_counts()` returns `(None, None)` (`:251-255`): with no manifest, "criterion" cannot be
    told from "refused", and a fabricated three-way split is worse than `?`.
  - `_arc_line()` appends a segment `serves a/m/–` after `ready`, rendering `serves ?` when
    `serves_window()` is `None`. The dash is U+2013.

**Invariants.** (a) A refused value (`_serves_of` → `None` on a present line) counts in the third
bucket, the same bucket as an absent line: the strip already treats "unreadable" as "silent" in
`topic()`, and a fourth bucket would be a verdict about prose. State this in the docstring. (b) The
segment is three counts and no threshold; no colour tone keys on it beyond `mute` (the
`frontier` tone). (c) `test_the_arc_gauge_reports_unknown_and_must_not_guess` (`:106-133`) stays as
written: `serves ?` carries no digit.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_cockpit.py`)

```python
def _window_docs(tmp_path, monkeypatch, headers: dict[str, str]):
    """`{filename: header-line}` → a docs dir the strip reads as its loop documents."""
    paths = []
    for name, header in headers.items():
        p = tmp_path / name
        p.write_text(f"# t\n\n**Topic:** x ·\n{header}\n", encoding="utf-8")
        paths.append(str(p))
    monkeypatch.setattr(cockpit, "_loop_docs", lambda: paths)
    m = tmp_path / "manifest.ttl"
    m.write_text(_MANIFEST_1, encoding="utf-8")
    monkeypatch.setattr(cockpit, "ARC_MANIFEST", str(m))


def test_serves_window_counts_criterion_maintenance_and_silence_inside_the_window(tmp_path, monkeypatch):
    """Spec § 3.2: three counts, no verdict. A doc dated outside `_WINDOW` days is not counted;
    a refused value counts with the silent ones — the strip does not grade prose."""
    import datetime as dt
    today = dt.date.today().isoformat()
    old = (dt.date.today() - dt.timedelta(days=cockpit._WINDOW + 30)).isoformat()
    _window_docs(tmp_path, monkeypatch, {
        f"{today}-a-handoff.md": "**Serves:** prog:criterion:etkl:05",
        f"{today}-b-handoff.md": "**Serves:** maintenance — why",
        f"{today}-c-brief.md": "",
        f"{today}-d-handoff.md": "**Serves:** prog:criterion:etkl:99",
        f"{old}-e-handoff.md": "**Serves:** prog:criterion:etkl:05",
    })
    assert cockpit.serves_window() == (1, 1, 2)
    arc_line = _strip(cockpit.render(color=False)).splitlines()[1]
    assert "serves 1/1/2" in arc_line, arc_line


def test_serves_window_is_unknown_without_a_manifest(tmp_path, monkeypatch):
    """With no manifest a criterion token cannot be told from a refused one, so the split is
    unknowable and renders `?` — the same refusal `frontier` makes (`cockpit.py:251-255`)."""
    import datetime as dt
    today = dt.date.today().isoformat()
    _window_docs(tmp_path, monkeypatch, {f"{today}-a-handoff.md": "**Serves:** maintenance"})
    monkeypatch.setattr(cockpit, "ARC_MANIFEST", str(tmp_path / "absent.ttl"))
    assert cockpit.serves_window() is None
    arc_line = _strip(cockpit.render(color=False)).splitlines()[1]
    assert "serves ?" in arc_line, arc_line
```

And extend `test_the_arc_gauge_reports_unknown_and_must_not_guess` by one line after `:131`'s loop:
`assert "serves ?" in arc_line, arc_line` — the digit assertion at `:132` already covers the rest.

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_cockpit.py -q -k "serves_window or must_not_guess"`
Expected: FAIL — `no attribute 'serves_window'` / `no attribute '_loop_docs'`; the extended test
fails on `serves ?`.

- [ ] **Step 3: Implement**

`_loop_docs()`, `_newest_loop_doc()` over it, `serves_window()`, and the `_arc_line()` segment.
Read the date from the basename's first ten characters with `date.fromisoformat`; a name that does
not parse is skipped (the listing regex already requires the `\d{4}-\d{2}-\d{2}-` prefix, `:288`).
Update the module docstring's arc-line block (`:18-28`) with one line for `serves a/m/–`, stating
what each count is and that none is a verdict.

- [ ] **Step 4: Run the file and the strip**

Run: `.venv/bin/python -m pytest tests/test_cockpit.py -q` → all PASS.
`.venv/bin/python scripts/cockpit.py --no-color --refresh` → line 2 ends
`frontier 13  ready 15  serves 0/2/34` or thereabouts (36 docs in the window today, of which this
loop's handoff and the spec handoff declare `maintenance`; **re-measure**, the window slides daily).
Paste it.

- [ ] **Step 5: Commit**

```bash
git add scripts/cockpit.py tests/test_cockpit.py
git commit -m "feat(cockpit): serves a/m/– on the arc line — how many loops in the window served a criterion, declared maintenance, or said nothing"
```

## FALSIFICATION (Task 3)
Remove the date filter in `serves_window()` (count every loop doc):
`test_serves_window_counts_…` must go RED with `(2, 1, 2)`. Restore; green. Second arm: make
`serves_window()` return `(0, 0, 0)` when the manifest is absent — both `…is_unknown_without_a_manifest`
and `…must_not_guess` must go RED (a digit reached the arc line). Restore; green.

---

### Task 4: PARKED — a qualifier on `open` that every reader survives, and M21

**Files:**
- Modify: `tests/test_residue_register_integrity.py` — two new tests (the module's readers need no
  change: `_INDEX_ROW` already routes on the first word, `:40`)
- Modify: `tests/test_arc_manifest.py` — new `parked_rows()`, the M21 branch in
  `environment_refusals` (`:294-336`), new test; docstring counts `:1-25`, `:295`
- Modify: `tests/arc-shapes.ttl:10-13` (header prose: the refusal count)
- Create: `tests/arc-m21-parked-blocker-leak.ttl`
- Modify: `scripts/cockpit.py` — new `parked()`, `render()` line 1 (`:397-404`), module docstring
  `:11-12`
- Modify: `scripts/residue_graph.py` — `read_rows()` fourth return value, a `parked n` line, JSON
  node field, and `--candidates`
- Modify: `tests/test_cockpit.py`, `tests/test_residue_graph.py` — new tests

**Interfaces:**
- Consumes: task 1's `read_rows()`; `residues()` (`cockpit.py:137`); `register_rows()`,
  `blocked_rows()`, `environment_refusals()` (`test_arc_manifest.py:237,118,294`).
- Produces:
  - **The qualifier, stated once, here.** Index status cell: `open (parked YYYY-MM-DD)`. Detail row
    in `residues-open.md`: the row's last cell gains `**PARKED YYYY-MM-DD:** <reason>`; the row moves
    nowhere and is never struck. The regex every reader shares:
    `^\| *R\d+ *\| *open \(parked (\d{4}-\d{2}-\d{2})\)`.
  - `cockpit.parked() -> int` — the count of index rows matching that regex. **A sibling of
    `residues()`, not a fourth element of its tuple** (measured: five 3-tuple unpack sites). `render()`
    line 1 gains `parked n` after the `closed` fraction, always rendered, tone `mute`.
  - `test_arc_manifest.parked_rows() -> frozenset[str]` — ids whose index status matches the
    regex; **not** `lru_cache`d, so a test can point `REGISTER` at a fixture (`register_rows()`'s
    cache is the seam the M21 test must not need to clear).
  - `environment_refusals()` gains, after the M7 branch: for every `(iri, residue)` in
    `blocked_rows(graph)` with `residue in parked_rows()`, append
    `f"M21: {iri} is prog:blockedBy {residue!r}, which is parked — a criterion cannot wait on a row nobody is pursuing; unpark it in the same change"`.
  - `residue_graph.read_rows() -> tuple[rows, status, label, parked]` with `parked: set[int]`;
    `main` prints `parked {n}` on the components line; JSON nodes gain `"parked": bool`;
    `--candidates` prints, one per line, `R{n}` for every row that is `open`, in no
    `read_criteria()` value, and has no neighbour (either direction) whose status is `open` —
    the structural condition of spec § 3.3, computed and never decided.

**Invariants.** (a) `residues()` is not edited: `c/t` cannot move. (b) The integrity test's five
existing tests pass unchanged on a register with a parked row. (c) M21 fires from the filesystem
only: the fixture is SHACL-clean and earns no M7 (it names a row that exists).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_residue_register_integrity.py`:

```python
def _register(tmp_path, monkeypatch, index: str, open_: str, closed: str = ""):
    """Point the module's readers at a synthetic register (its three inputs)."""
    (tmp_path / "residues.md").write_text(index, encoding="utf-8")
    (tmp_path / "residues-open.md").write_text(open_, encoding="utf-8")
    (tmp_path / "residues-closed.md").write_text(closed, encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "INDEX", tmp_path / "residues.md")
    monkeypatch.setattr(sys.modules[__name__], "DETAIL",
                        {"open": tmp_path / "residues-open.md",
                         "closed": tmp_path / "residues-closed.md"})


def test_a_parked_row_routes_to_the_open_file_and_is_not_struck(tmp_path, monkeypatch):
    """Spec 2026-09-11 § 3.3: PARKED is a qualifier on `open`, never a third file or a closure.
    The first word still routes; the qualifier is prose to every reader here."""
    _register(tmp_path, monkeypatch,
              index="| R7 | open (parked 2026-09-11) | x |\n| R8 | closed | y |\n",
              open_="| R7 (1/2 closed) | x. **PARKED 2026-09-11:** no loop cites it. |\n",
              closed="| ~~R8~~ (1/2 closed) | y |\n")
    assert index_rows() == {"R7": "open", "R8": "closed"}
    test_every_index_status_is_open_or_closed()
    test_every_index_row_has_exactly_one_detail_row_in_the_file_its_status_names()
    test_every_detail_row_has_an_index_row()
    test_a_row_is_struck_if_and_only_if_it_is_filed_closed("open")
    test_a_row_is_struck_if_and_only_if_it_is_filed_closed("closed")


def test_a_struck_parked_row_is_a_half_done_closure_and_is_refused(tmp_path, monkeypatch):
    """Parking is not closing: a parked row that somebody struck is the same contradiction the
    strike test already refuses, and the qualifier must not hide it."""
    _register(tmp_path, monkeypatch,
              index="| R7 | open (parked 2026-09-11) | x |\n",
              open_="| ~~R7~~ (1/2 closed) | x. **PARKED 2026-09-11:** reason |\n")
    with pytest.raises(AssertionError):
        test_a_row_is_struck_if_and_only_if_it_is_filed_closed("open")
```

(`import sys` joins the imports at `:25`.)

Append to `tests/test_arc_manifest.py`, in the environment-leg section after `test_m7_…` (`:681`):

```python
def test_m21_a_blocking_edge_to_a_parked_residue_is_refused(tmp_path, monkeypatch):
    """Spec 2026-09-11 § 3.3 (ii): a row the maintainer has parked may not be what a criterion
    waits on — the two claims contradict, and the fix is to unpark it in the same change.

    Two arms. CONTROL first: against the live register, where no row is parked, the fixture is
    admitted by the environment leg, which proves the refusal below comes from the qualifier and
    nothing else. Then the register is a fixture in which the named row IS parked."""
    fixture = REPO / "tests" / "arc-m21-parked-blocker-leak.ttl"
    g = Graph().parse(fixture, format="turtle")
    assert environment_refusals(g) == [], "the control must be admitted against the live register"

    index = tmp_path / "residues.md"
    index.write_text("| R1 | open (parked 2026-09-11) | x |\n", encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "REGISTER", index)
    _refused_by_environment("arc-m21-parked-blocker-leak.ttl", "M21")
```

**MEASURE before writing the fixture**: `_refused_by_environment` asserts the exact refusal set is
`{"M21"}`, so the fixture must earn no M7 — it names `R1`, which `register_rows()` (cached from the
LIVE index, and the monkeypatch does not clear it) contains — and no M5/M10: it is `prog:met false`
(M5 bites only on met) and its `prog:source` must resolve (M10 is universal). Copy the M7 fixture's
`prog:source` line, which resolves today (`arc-m7-dangling-residue-leak.ttl:12`), and re-check it
resolves. `R1` is `closed` live; no environment refusal keys on that (measured: `environment_refusals`
`:294-336` reads presence only).

Append to `tests/test_cockpit.py`:

```python
def test_a_parked_row_is_counted_and_the_tally_does_not_move(tmp_path, monkeypatch):
    """Spec § 3.3 (iii): parking changes neither `c` nor `t`. The qualifier is read by one new
    counter and is invisible to the one the maintainer's convention defines."""
    _register(tmp_path, monkeypatch, index=_INDEX_4)
    before = cockpit.residues()[:2]
    assert cockpit.parked() == 0
    _register(tmp_path, monkeypatch,
              index=_INDEX_4.replace("| R4 | open |", "| R4 | open (parked 2026-09-11) |"))
    assert cockpit.residues()[:2] == before == (2, 4)
    assert cockpit.parked() == 1
    line1 = _strip(cockpit.render(color=False)).splitlines()[0]
    assert "parked 1" in line1, line1
```

Append to `tests/test_residue_graph.py`:

```python
def test_the_graph_reports_parked_rows_and_the_structural_candidates():
    """Spec § 3.3: a candidate is open, named by no prog:blockedBy, and has no OPEN neighbour.
    Measured 2026-09-11 with every index row read (task 1): 80 candidates; the spec's 78 was
    counted before R131 and R141 were readable. No row is parked on this tree."""
    rows, status, _label, parked = residue_graph.read_rows()
    assert parked == set()
    crit = residue_graph.read_criteria()
    front = {r for v in crit.values() for r in v}
    open_ = {n for n, s in status.items() if s == "open"}
    nb = {}
    for a, refs in rows.items():
        for b in refs:
            if b in rows:
                nb.setdefault(a, set()).add(b)
                nb.setdefault(b, set()).add(a)
    expected = sorted(n for n in open_ if n not in front and not (nb.get(n, set()) & open_))
    assert residue_graph.candidates(rows, status, crit) == expected
    assert len(expected) == 80
```

(`candidates(rows, status, crit) -> list[int]` is the function `--candidates` prints; state it
in `residue_graph.py` and let the test derive the same set independently — that is what makes the
`80` a pin rather than a restatement.)

- [ ] **Step 2: Run them to verify they fail**

Run:
`.venv/bin/python -m pytest tests/test_residue_register_integrity.py tests/test_arc_manifest.py::test_m21_a_blocking_edge_to_a_parked_residue_is_refused tests/test_cockpit.py::test_a_parked_row_is_counted_and_the_tally_does_not_move tests/test_residue_graph.py -q`
Expected: the integrity fixture tests PASS already (the qualifier is prose to `_INDEX_ROW` — record
that; it is the spec's claim that no reader needs redefinition, confirmed), M21 FAILS on the missing
fixture, `parked` FAILS with `no attribute`, the graph test FAILS on unpacking three into four.

- [ ] **Step 3: Implement, in this order**

1. `tests/arc-m21-parked-blocker-leak.ttl` — the M7 fixture with `R1` in place of `R999` and the
   header comment saying what M21 refuses and that the register it is refused against is a test
   fixture, since the live register parks nothing until the maintainer's triage (task 6).
2. `parked_rows()` and the M21 branch in `test_arc_manifest.py`; update the module docstring
   (`:1-25`: nineteen refusals, sixteen not in SHACL, six environment questions, M21 listed with
   M7) and `environment_refusals`'s docstring `:295`; update `tests/arc-shapes.ttl:10-13` to
   "FOURTEEN of the NINETEEN" and name M21 beside M7.
3. `cockpit.parked()` and the line-1 segment; module docstring `:11-12`.
4. `residue_graph.py`: fourth return value, `candidates()`, `--candidates`, the printed count, the
   JSON field; module docstring gains the `--candidates` usage line and the sentence that the list
   is a structural set and no decision.

- [ ] **Step 4: Run the four files**

Run: `.venv/bin/python -m pytest tests/test_residue_register_integrity.py tests/test_arc_manifest.py tests/test_cockpit.py tests/test_residue_graph.py -q`
Expected: all PASS. `.venv/bin/python scripts/residue_graph.py --candidates | wc -l` → `80`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_residue_register_integrity.py tests/test_arc_manifest.py tests/arc-shapes.ttl \
        tests/arc-m21-parked-blocker-leak.ttl scripts/cockpit.py scripts/residue_graph.py \
        tests/test_cockpit.py tests/test_residue_graph.py
git commit -m "feat(register): PARKED as a qualifier on open — read by the graph and the strip, refused as a blocker (M21), invisible to the tally"
```

## FALSIFICATION (Task 4)
Three arms, one per instrument. (a) Strip the qualifier handling from `cockpit.parked()` (return 0):
`test_a_parked_row_is_counted_…` must go RED on `parked() == 1` **while the `(2, 4)` assertion
before it still holds** — paste the traceback showing which line failed; that is the proof parking
never touched the tally. (b) Delete the M21 branch: `test_m21_…` must go RED on the exact-set
assertion with `set()`. (c) In `candidates()`, drop the open-neighbour clause: the graph test must
go RED with a count above 80. Restore all three; green.

---

### Task 5: CLAUDE.md § Deferred residues — **on the maintainer's explicit request only**

**Files:**
- Modify: `CLAUDE.md` § Deferred residues (after the "Count what you close" bullets)

**Gate.** CLAUDE.md is the Contract class, *"edited only on explicit request"*. This task is not
executed by an agent on its own reading of the plan. The proposed text is carried here so the request
can be answered in one edit:

```markdown
**A row can be PARKED, and parked is not closed (2026-09-11).** A parked row is one the maintainer
has decided, by date, not to pursue. It stays `open`, keeps its number in `t` and out of `c`, keeps
its evidence and its raise-time snapshot, and is never struck. In the index its status cell reads
`open (parked YYYY-MM-DD)`; in `residues-open.md` the row appends `**PARKED YYYY-MM-DD:** <reason>`
and moves nowhere. Parking is a maintainer's decision in a dated triage pass — never a loop's, never
an instrument's, never an age. Only a row named by no `prog:blockedBy` and with no OPEN neighbour in
the register's link graph may be parked (`scripts/residue_graph.py --candidates` lists them). The
first loop that cites a parked row unparks it in the same change. A criterion may not be
`prog:blockedBy` a parked row (M21).

**Every dated handoff or brief declares what it serves.** One header line
`**Serves:** prog:criterion:<rung>:<nn>` (an IRI present in `tests/arc-manifest.ttl`) or
`**Serves:** maintenance`, followed by prose after a dash if wanted. The strip reads the first token
only and prints nothing for anything else. § 5a names its subject from the strip's `ready` or
`frontier`; `residues.md` is opened to find what blocks a chosen criterion, never to find a
subject.
```

- [ ] **Step 1:** Ask. If the maintainer says yes, apply the text verbatim, run
  `.venv/bin/python -m pytest tests/test_doc_governance.py -q` (CLAUDE.md is Contract-class and the
  lint knows it), commit with `docs(CLAUDE.md): PARKED and Serves: — on the maintainer's request`.
  If not asked or not granted, **this task is skipped and the task report says so.**

## FALSIFICATION (Task 5)
None possible for prose; the report states whether the request was made and answered.

---

### Task 6: The triage pass — **maintainer present**

**Files:**
- Modify: `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md` — only the rows the
  maintainer parks

**Gate.** Not started without the maintainer in the session. Spec § 3.3: parking is their decision,
per row, dated, with a reason.

- [ ] **Step 1:** `.venv/bin/python scripts/residue_graph.py --candidates` — the 80 (re-measure;
  task 1 and any register change since move it). Present them with their index lines.
- [ ] **Step 2:** For each row the maintainer parks: index cell → `open (parked 2026-MM-DD)`; the
  open-file row gains `**PARKED 2026-MM-DD:** <their reason>` at the end of its last cell. Nothing
  else on the row changes. Rows they do not name are not touched.
- [ ] **Step 3:** Run
  `.venv/bin/python -m pytest tests/test_residue_register_integrity.py tests/test_arc_manifest.py tests/test_cockpit.py tests/test_residue_graph.py -q`
  → all PASS; `scripts/cockpit.py --no-color --refresh` line 1 shows `parked n` with their count and
  the `c/t` unchanged from before the pass. Paste both.
- [ ] **Step 4:** Commit as `register: park N rows — the maintainer's triage of 2026-MM-DD`, listing
  the ids in the body.

## FALSIFICATION (Task 6)
The tally: `cockpit.residues()[:2]` before and after the pass must be equal; paste both figures. If
they differ, a parked row was struck or moved, and the integrity test in task 4 says which.

---

## Self-review against the spec

- § 3.1 rule/expression/oracle (i)–(iv) + live test → task 2. § 3.1 "must not touch" → Global
  Constraint 2.
- § 3.2 measure `serves a/m/–` → task 3; the § 3.2 prediction is not a task (it is run by the next
  three loops' handoffs; § Handoff below carries it as PROPOSED).
- § 3.3 the fix-first instrument → task 1; oracles (i)–(iii) → task 4; the M7-style refusal is M21.
- § 7 tasks 5 and 6 → tasks 5 and 6, gated as the spec gates them.
- § 4's fork is not a task; it is the maintainer's and is recorded in the handoff.
- **One deviation from the spec's letter, stated once:** spec § 3.3 says `cockpit.residues()` gains a
  parked count; the plan puts it in a sibling `parked()` because five sites unpack the 3-tuple
  (measured). The oracle is unchanged in force. **One correction:** the candidate set is 80, not 78.
- No function body appears in this plan; the one regex stated (the qualifier) is an interface shared
  by four readers and is stated once, in task 4.
