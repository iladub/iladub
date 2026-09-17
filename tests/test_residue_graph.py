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
    _rows, status, _label, _parked = residue_graph.read_rows()
    expected = {int(rid[1:]): s for rid, s in index_rows().items()}
    assert status == expected, (
        f"the graph and the integrity test disagree about the index: "
        f"missing {sorted(set(expected) - set(status))}, "
        f"extra {sorted(set(status) - set(expected))}, "
        f"differing {[n for n in status if n in expected and status[n] != expected[n]]}")


def test_the_graph_reports_parked_rows_and_the_structural_candidates():
    """Spec § 3.3: a candidate is open, named by no prog:blockedBy, and has no OPEN neighbour.
    Measured 2026-09-11 with every index row read (task 1): 80 candidates; the spec's 78 was
    counted before R131 and R141 were readable. No row is parked on this tree.
    RE-MEASURED 2026-09-11 (the-negative-half): 80 -> 81 — R209 is open, blocks no criterion
    and links only to the closed R179, so it is a candidate by § 3.3's own rule.
    RE-MEASURED 2026-09-11 (etkl-02-r166-first): 81 -> 82 — R210 is open, blocks no criterion and
    links to no row; R166, now named by etkl:02's prog:blockedBy, was not a candidate before or after.
    RE-MEASURED 2026-09-12 (R201/R203, grid donation): 82 -> 84 — R216 and R217 are open, block no
    criterion, and link only to the now-CLOSED R201/R203 that raised them, so both are candidates by
    § 3.3's own rule, exactly as R209 was against the closed R179. MEASURED that the delta is those
    two and nothing else: 84 candidates total, both present, and 82 excluding them — closing R201
    and R203 changed no other row's candidacy (a closed row was never a candidate, and neither was
    anyone's only open neighbour).
    RE-MEASURED 2026-09-12 (R212, the ignored band's carrier): 84 -> 87 — R218, R219 and R220 are
    open, block no criterion, and each has exactly ONE neighbour, the now-CLOSED R212 (R218 and R219
    were raised by R212's spec; R220 by its carrier, the edge coming from R212's own closure text).
    All three are candidates by § 3.3's own rule, exactly as R216/R217 were against the closed
    R201/R203 and R209 against the closed R179. MEASURED that the delta is those three and nothing
    else, by recomputing `candidates` against the HEAD versions of the three register files and
    against this tree: 84 before, 87 after, ADDED = [218, 219, 220], REMOVED = [].
    RE-MEASURED 2026-09-13 (the span the author drew, the plan loop): 87 -> 88 — R221 is open,
    blocks no criterion, and links only to the now-CLOSED R139, the citation-rot row whose class it
    belongs to, so it is a candidate by § 3.3's own rule exactly as R218-R220 were against the
    closed R212 and R216/R217 against the closed R201/R203. MEASURED that the delta is that one row
    and nothing else, by recomputing `candidates` against the HEAD versions of the register files
    and against this tree: 87 before, 88 after, ADDED = [R221], REMOVED = [].
    RE-MEASURED 2026-09-13 (the span the author drew, the EXECUTING loop): 88 -> 93, and the five
    decompose into two kinds. Closing [[R211]] removed the only OPEN neighbour of the three rows it
    RAISED — R213, R214 and R215 each link to R211 and to nothing else open — so all three become
    candidates by § 3.3's own rule without any row being added. R222 and R223 are the other kind: new
    open rows blocking no criterion and linking only to the now-CLOSED R211, exactly as R218-R220
    stood against the closed R212 and R216/R217 against the closed R201/R203. This is the first entry
    here where a CLOSURE, not a raise, is most of the delta. MEASURED and not reasoned, by recomputing
    `candidates` against the HEAD versions of the register files and against this tree: 88 before,
    93 after, ADDED = [213, 214, 215, 222, 223], REMOVED = [].
    RE-MEASURED 2026-09-13, same loop — and the MECHANISM IS NEW TO THIS LIST: 93 -> 92,
    ADDED = [], REMOVED = [213]. No row was raised, closed or parked. An AMENDMENT'S PROSE cited
    [[R157]] while qualifying R213's colour-discriminator claim, and R157 is open, so R213 gained
    an open neighbour and stopped being a candidate (its other links — 172, 176, 211 — are all
    closed, so R157 alone did it). Every prior entry above moved because a STATUS moved; this one
    moved because a row started CITING another row. Worth knowing before reading any delta here as
    progress: an amendment that cites an open row moves this count without changing a single
    status. Measured by recomputing against HEAD (`c1a5484`) and against this tree.
    RE-MEASURED 2026-09-13 by the etkl:04 loop, hours later: 92 -> 91, ADDED = [], REMOVED = [202].
    Again no row was raised, closed or parked. R202's row was amended to record that its two
    unpaired ons regions ARE the datagrid fallback's appended region, and that amendment cites
    [[R224]], which is open — so R202 gained an open neighbour and left the candidate set, exactly
    as R213 did one entry above. **That makes the mechanism the entry above calls "NEW TO THIS LIST"
    a RECURRING class, not a one-off**: two independent movements on the same day, both from an
    amendment's prose rather than from any status. The loop's own new rows [[R224]] and [[R225]]
    add NOTHING to this count — each cites an open row ([[R213]] and [[R224]] respectively), so
    neither is structurally isolated. Measured by recomputing `candidates` against HEAD
    (`580cfcb`) and against this tree.
    RE-MEASURED 2026-09-13 by the [[R224]] repair loop: 91 -> 91, ADDED = [], REMOVED = [] — and
    the STILLNESS IS A CANCELLATION, not an absence of movement, which is why it is recorded at
    all. [[R224]] was CLOSED, and R202's only open neighbour was R224 (that is the entry two above,
    which removed R202 from this set when the citation was authored), so the closure alone would
    have returned R202 to the candidates. It did not, because the same loop raised [[R226]] and
    R226's prose cites [[R202]] — a NEW ROW's prose replacing the open neighbour a STATUS change
    had just taken away. The two entries above show prose moving this count on its own; this one
    shows prose CONCEALING a status move by exactly cancelling it, so a reader must not take an
    unchanged count as evidence that no row changed status. [[R225]] stays out of the set for an
    unrelated reason, checked rather than assumed: it cites [[R44]], which is open. Measured by
    recomputing `candidates` against the pre-edit tree and against this one.
    RE-MEASURED 2026-09-14 by the [[R225]] CLOSING loop: 91 -> 90, ADDED = [], REMOVED = [170] —
    and the notable half is what did NOT move it. That loop closed TWO rows ([[R225]], [[R227]])
    and raised TWO ([[R228]], [[R229]]), and not one of those four status changes altered any
    row's candidacy: every row R225 neighbours still has another open neighbour, R227's only
    neighbour R171 is open, and both new rows cite open rows so neither is structurally isolated.
    The entire delta is [[R170]] leaving the set, and the cause is PROSE: R228's row cites R170
    while recording that O3 — the standing detector for R170's 976 unguarded cells — was AMENDED
    with measured `D1_MOVES` pins rather than loosened to `>=`. R170 was open and isolated (its
    only other neighbour, R165, is closed) and gained an open neighbour by being mentioned. Third
    instance of the mechanism the entries above call recurring — after R213 via R157 and R202 via
    R224 — and the first where a loop's own NEW row de-candidates a row it merely CITED, rather
    than an amendment doing it. **So a closing loop can move this count without closing anything,
    and can close two rows without moving it at all**; read the delta by mechanism, never as
    progress. Measured by recomputing `candidates` against `HEAD~2` (the tree before this loop
    touched the register) and against this one, with the edge direction checked as well: R228's
    row cites R170 and R170's does not cite R228, so the graph's undirected neighbour construction
    is what carries it.
    RE-MEASURED 2026-09-17 by the loop that refused the decoration universe: 90 -> 92,
    ADDED = [242, 243], REMOVED = []. That loop CLOSED one row ([[R238]]) and raised two
    ([[R243]], [[R244]]), and the delta decomposes into the two kinds this list already knows —
    neither of them "progress". [[R243]] is the RAISE kind: new, open, blocking no criterion, and
    linking only to the now-CLOSED R238 that raised it, exactly as R218-R220 stood against the
    closed R212. [[R242]] is the CLOSURE kind and is the one worth reading: it was raised days
    earlier, changed nothing about itself, and entered this set only because its ONLY neighbour
    was R238 — closing R238 removed its last open neighbour. [[R244]] adds nothing despite being
    new, because its prose cites [[R188]], which is open — the same reason R225 stayed out against
    R44. MEASURED and not reasoned, by recomputing `candidates` against the HEAD versions of the
    three register files and against this tree. **The override was CONTROLLED in both directions**,
    and that is new to this list: a first attempt discovered the module's three inputs by
    `isinstance(v, Path)` when they are module-level STRINGS, so it rebound nothing, measured the
    same tree twice and would have reported ADDED = [] as a clean result. A rebinding that matches
    no attribute does not raise — so it must be proved to bite (the count must move) and to
    release (restoring must return the original count) before its delta means anything.
    RE-MEASURED 2026-09-17 by the loop that re-stated R47/R50/R77 (branch
    `section-total-is-in-its-own-band`): 92 -> 90, ADDED = [], REMOVED = [47, 50].
    **A THIRD mechanism, and it is neither of the two above.** That loop CLOSED nothing and
    RAISED nothing — it AMENDED three existing rows and shipped no code. R47 and R50 are open,
    named by no criterion, and had no open neighbour; the amendments cite [[R77]] from R47's row
    and [[R47]] from R50's, and R77 is open, so each gained its FIRST open neighbour and left the
    set. The count therefore moves on a loop that changed no row's STATUS at all — the sharpest
    form yet of this docstring's own warning to read the delta by mechanism and never as progress,
    since here there is no progress to read either way. Controlled in both directions exactly as
    the paragraph above requires: bite True (92 != 90), release True (restoring the three
    module-level strings returns 90).
    RE-MEASURED 2026-09-17 by the NEURAL worker foundation spec loop (branch
    `neural-worker-foundation-spec`): 90 -> 91, ADDED = [248], REMOVED = []. The plain first
    mechanism: R248 was RAISED open, is named by no criterion, and its only link is [[R212]],
    which is closed — so it enters the set on arrival. Controlled: with the two register edits
    stashed the count is 90, restored it is 91.
    RE-MEASURED 2026-09-17 by the review of that spec (branch `neural-worker-spec-review`):
    91 -> 90, ADDED = [], REMOVED = [248]. The prose mechanism: the new row R249 cites [[R248]]
    and R249 is open, so R248 gained its first open neighbour and left the set; R249 itself cites
    the open [[R213]] and never entered it."""
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
    assert len(expected) == 90
