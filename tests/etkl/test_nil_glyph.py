"""The nil glyph — [[R167]]'s oracles O1-O3 (spec `2026-09-09-the-nil-glyph-design.md` §5).

US-GAAP writes a missing value as an em-dash. `celltype.is_blank` recognised the ASCII `-`
and not its typographically-correct spelling, so `_cell_datatype('—')` returned `tab:Text`
— and a `tab:Text` cell does NOT abstain (`tab:datatypeAbstains`), so one nil cell
disqualified its whole column from `stub-data-split.rq`'s data suffix.

The spellings are declared in `vocab/ontology/tab.ttl` and READ by the recogniser, not
duplicated in Python: `tab:Blank`'s published `rdfs:comment` already enumerated them in
prose, so a Python-only fix would have made the published contract false (spec §4).
"""
from rdflib import Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")


# ---- O1: the two glyphs type as Blank, and nothing already accepted regresses ----

def test_the_nil_glyphs_type_as_blank():
    """O1. The em-dash U+2014 and en-dash U+2013 are missing values, not text."""
    from iladub.etkl.celltype import _cell_datatype, is_blank

    for glyph in ["—", "–"]:
        assert is_blank(glyph), f"U+{ord(glyph):04X} is a nil marker"
        assert _cell_datatype(glyph) == TAB.Blank, f"U+{ord(glyph):04X}"
    # surrounding whitespace is stripped, exactly as for the ASCII hyphen
    assert is_blank("  —  ")


def test_the_spellings_already_accepted_do_not_regress():
    """O1, other half. `''`, `(blank)` and the ASCII `-` were blank before this loop."""
    from iladub.etkl.celltype import _cell_datatype, is_blank

    for s in ["", "   ", "-", "(blank)", "(BLANK)"]:
        assert is_blank(s), repr(s)
        assert _cell_datatype(s) == TAB.Blank, repr(s)


# ---- O2: the ontology is the source of the set, not a mirror of it ----

def test_the_recogniser_accepts_exactly_the_spellings_the_ontology_declares():
    """O2 — the oracle that makes the declaration LOAD-BEARING rather than decorative.

    The set is compared against `vocab/ontology/tab.ttl` as parsed, so deleting a
    `tab:nilSpelling` triple turns this RED. Without it, arm (b) of spec §4 would be a
    Python literal with an ontology comment beside it — which is the two-sources-of-truth
    state `tab:CellDatatypeFamily`'s own published comment argues against.

    The empty cell is deliberately NOT a declared spelling: absence of ink is structural,
    not a marker anyone writes (spec §4, "scope of (b)").

    The literal four-member set below is a PIN, not a third source of truth: the equality
    that matters is `_NIL_SPELLINGS == declared`, and the pin exists so that removing a
    spelling cannot pass by shrinking both sides at once. Adding a fifth marker is a
    deliberate act and edits this line.
    """
    from iladub.etkl.celltype import _NIL_SPELLINGS, _ONT

    declared = {str(o).strip().lower()
                for o in _ONT.objects(TAB.Blank, TAB.nilSpelling)}
    assert declared, "tab.ttl declares no tab:nilSpelling — the recogniser has no source"
    assert _NIL_SPELLINGS == declared
    # and the set is the four markers this loop leaves behind
    assert declared == {"(blank)", "-", "–", "—"}


def test_every_declared_spelling_is_recognised():
    """O2, the other direction: a spelling declared in the ontology and not recognised by
    the code is the same defect as one recognised and not declared."""
    from iladub.etkl.celltype import is_blank, _ONT

    declared = [str(o) for o in _ONT.objects(TAB.Blank, TAB.nilSpelling)]
    # NON-VACUITY: with no declarations the loop below asserts nothing and this test would
    # pass on a tree where the ontology half was never written.
    assert len(declared) == 4, declared
    for o in declared:
        assert is_blank(o), f"declared but not recognised: {o!r}"


# ---- O3: equality, never containment ----

def test_a_dash_inside_other_text_is_not_a_missing_value():
    """O3. The guard against widening `is_blank` into a keyword/substring list — the
    failure mode [[R78]] is reserved for (`..`, `n/a`, genuinely AMBIGUOUS markers).

    `'2020—2024'` is a range and `'a — b'` is prose; both carry ink and neither is missing.
    """
    from iladub.etkl.celltype import _cell_datatype, is_blank

    for s in ["2020—2024", "a — b", "——", "-5", "--", "— net", "—0"]:
        assert not is_blank(s), repr(s)
    assert _cell_datatype("2020—2024") == TAB.Text
    assert _cell_datatype("-5") == TAB.Numeric


# ---- the published contract no longer contradicts the code ----

def test_the_published_comment_does_not_enumerate_the_spellings_in_prose():
    """`tab:Blank`'s `rdfs:comment` used to read "empty, the self-declaring '(blank)', or a
    lone '-'" — a prose enumeration that this loop's fourth spelling would have falsified.
    The enumeration now lives in `tab:nilSpelling` triples; the comment must POINT at them
    rather than restate them, or the drift returns the next time a glyph is added."""
    from iladub.etkl.celltype import _ONT

    comment = str(_ONT.value(TAB.Blank, __import__("rdflib").RDFS.comment))
    assert "nilSpelling" in comment
    assert "lone '-'" not in comment


# ---- the CONSEQUENCE, not just the typing: the stub|data split R167 measured ----

def test_one_nil_cell_no_longer_disqualifies_its_column_from_the_data_suffix():
    """The defect R167 actually measured, pinned end-to-end on a SYNTHETIC grid rather than
    on apple — the corpus holds exactly one em-dash (spec §2) and it sits on an escalated
    band, so no corpus document can carry this pin.

    `tab:Text` does not abstain, so before this loop ONE nil cell made its whole column
    non-data and pushed the stub|data split from k=1 to k=2 — the split apple p2's merged
    reading returned (`stub-data-split.rq`'s `SUM(IF(?ct = tab:Text, 1, 0)) = 0`). Typed
    `tab:Blank` the cell abstains, the column is homogeneous Numeric, and k is 1 again.

    The grid is deliberately the minimal shape that shows it: two data columns of numbers,
    one nil cell in the first of them, one text stub column.
    """
    import os
    from rdflib import Literal
    from rdflib.namespace import XSD
    from iladub.etkl import celltype

    qdir = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    grid = [
        (0, 0, "Item"),   (0, 1, "2023"), (0, 2, "2024"),
        (1, 0, "Net"),    (1, 1, "10"),   (1, 2, "20"),
        (2, 0, "Other"),  (2, 1, "—"),    (2, 2, "30"),
    ]
    g = celltype.grid_evidence(grid, 3)
    k = celltype.run_scalar(os.path.join(qdir, "stub-data-split.rq"), g,
                            bindings={"split": Literal(1, datatype=XSD.integer)})
    assert k == 1, (
        "one nil cell disqualified its column from the data suffix — the em-dash is voting "
        "as tab:Text instead of abstaining as tab:Blank"
    )
