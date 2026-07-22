from iladub.etkl.headers import HeaderNode
from iladub.etkl.span import build_reading, flank_context


def _tree():
    # parent "Current Visit" over cols 1..4 (col4 = tied flank, ambiguous), plus three
    # deeper sub-header leaves for cols 1,2,3 and a header-empty flank (no leaf for col4).
    parent = HeaderNode(0, (1, 2, 3, 4), "Current Visit", None, 250.0, True, 4)
    a = HeaderNode(1, (1,), "Analyte", 0, 150.0)
    r = HeaderNode(1, (2,), "Result", 0, 250.0)
    u = HeaderNode(1, (3,), "Unit", 0, 350.0)
    return (parent, a, r, u)


def test_absorb_keeps_flank_and_clears_ambiguous():
    out = build_reading(_tree(), 0, 4, "absorb")
    assert out[0].covers == (1, 2, 3, 4)
    assert out[0].ambiguous is False and out[0].ambiguous_flank is None


def test_standalone_drops_flank_and_adds_empty_leaf():
    out = build_reading(_tree(), 0, 4, "standalone")
    assert out[0].covers == (1, 2, 3)          # flank removed from the span
    assert out[0].ambiguous is False
    # a header-empty flank becomes a new top-level leaf covering exactly (4,)
    leaves = [n for n in out if n.covers == (4,) and n.parent is None]
    assert len(leaves) == 1 and leaves[0].level == 0 and leaves[0].text == ""


def test_standalone_reparents_existing_leaf_for_the_flank():
    # if a deeper leaf already covers the flank, re-root it instead of adding an empty one
    tree = _tree() + (HeaderNode(1, (4,), "Flag", 0, 450.0),)
    out = build_reading(tree, 0, 4, "standalone")
    roots4 = [n for n in out if n.covers == (4,) and n.parent is None]
    assert len(roots4) == 1 and roots4[0].text == "Flag" and roots4[0].level == 0
    assert not any(n.covers == (4,) and n.text == "" for n in out)   # no spurious empty leaf


def test_flank_context_carries_labels_and_side():
    ctx = flank_context(_tree(), 0, 4)
    assert ctx["span_label"] == "Current Visit"
    assert ctx["leaf_labels"] == ["Analyte", "Result", "Unit"]
    assert ctx["flank_label"] == ""            # header-empty flank
    assert ctx["flank_side"] == "right"        # flank == max(covers)
