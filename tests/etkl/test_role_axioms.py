import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")
QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries")


# ---- graph builders (both axes via a covers-predicate arg) ----
def _hdr(g, t, u, lvl, lbl, covers, cpred):
    g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
    g.add((u, TAB.headerLevel, Literal(lvl)))
    if lbl is not None:
        lc = URIRef(str(u) + "-l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
    for c in covers:
        g.add((u, cpred, c))


def _leaves(g, t, leafpred, *xs):
    cls = TAB.LeafColumn if leafpred == TAB.hasLeafColumn else TAB.LeafRow
    for x in xs:
        g.add((x, RDF.type, cls)); g.add((t, leafpred, x))


def _build(axis):
    """Return a dict label->(graph, table) of shapes on `axis` ('column'|'row')."""
    cp = TAB.coversColumn if axis == "column" else TAB.coversRow
    lp = TAB.hasLeafColumn if axis == "column" else TAB.hasLeafRow
    out = {}

    g = Graph(); t = EX.t; a, b, c = EX.a, EX.b, EX.c            # flat: 3 single level-0
    _leaves(g, t, lp, a, b, c)
    _hdr(g, t, EX.hA, 0, "Name", [a], cp); _hdr(g, t, EX.hB, 0, "Age", [b], cp); _hdr(g, t, EX.hC, 0, "City", [c], cp)
    out["flat"] = (g, t)

    g = Graph(); t = EX.t; y, n, s, e, w = EX.y, EX.n, EX.s, EX.e, EX.w   # region: stub + spanned
    _leaves(g, t, lp, y, n, s, e, w)
    _hdr(g, t, EX.hY, 0, "Year", [y], cp); _hdr(g, t, EX.hR, 0, "Region", [n, s, e, w], cp)
    _hdr(g, t, EX.hN, 1, "North", [n], cp); _hdr(g, t, EX.hS, 1, "South", [s], cp)
    _hdr(g, t, EX.hE, 1, "East", [e], cp); _hdr(g, t, EX.hW, 1, "West", [w], cp)
    out["region"] = (g, t)

    g = Graph(); t = EX.t; q = [EX["q%d" % i] for i in range(4)]  # hier: 3 levels
    _leaves(g, t, lp, *q)
    _hdr(g, t, EX.hM, 0, "Metrics", q, cp)
    _hdr(g, t, EX.h23, 1, "2023", [q[0], q[1]], cp); _hdr(g, t, EX.h24, 1, "2024", [q[2], q[3]], cp)
    for i, nm in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        _hdr(g, t, EX["hq%d" % i], 2, nm, [q[i]], cp)
    out["hier"] = (g, t)
    return out


def _battery():
    b = {}
    for axis in ("column", "row"):
        for k, v in _build(axis).items():
            b["%s-%s" % (axis, k)] = (axis, v[0], v[1])
    return b


# ---- frozen reference: a port of _axis_dimensions (the anti-overfit oracle) ----
def _ref_axis_dimensions(g, t, axis):
    cp = TAB.coversColumn if axis == "column" else TAB.coversRow
    lp = TAB.hasLeafColumn if axis == "column" else TAB.hasLeafRow
    leaves = sorted(g.objects(t, lp), key=str)
    nodes = [h for h in g.objects(t, TAB.hasHeaderNode) if any(True for _ in g.objects(h, cp))]
    if not nodes:
        return []
    def label(h):
        lc = g.value(h, TAB.hasLabel); return str(g.value(lc, TAB.cellText)) if lc is not None else None
    by_level = {}
    for h in nodes:
        lvl = int(g.value(h, TAB.headerLevel)); cov = frozenset(g.objects(h, cp))
        by_level.setdefault(lvl, []).append((h, label(h), cov))
    dims, pending = [], None
    for lvl in sorted(by_level):
        ln = by_level[lvl]; multi = [x for x in ln if len(x[2]) > 1]
        singles = set().union(*[x[2] for x in ln if len(x[2]) == 1]) if any(len(x[2]) == 1 for x in ln) else set()
        if len(multi) == 1 and (multi[0][2] | singles) >= set(leaves) and not (multi[0][2] & singles):
            pending = multi[0][1]; continue
        seen, vals = set(), []
        for _, lbl, _c in sorted(ln, key=lambda z: min(str(c) for c in z[2])):
            if lbl is not None and lbl not in seen:
                seen.add(lbl); vals.append(lbl)
        dims.append((axis, lvl, pending, tuple(vals))); pending = None
    return dims


def _run(query_file, *graphs):
    union = Graph()
    for g in graphs:
        union += g
    out = Graph()
    for tr in union.query(open(os.path.join(QUERIES, query_file), encoding="utf-8").read()):
        out.add(tr)
    return out


def test_name_levels_marks_the_naming_parent():
    for key, (axis, g, t) in _battery().items():
        marks = _run("name-levels.rq", g)
        # collect (parent-label, named-level) from the marks and compare to the reference's named levels
        marked = {(str(g.value(g.value(p, TAB.hasLabel), TAB.cellText)), int(l))
                  for p, _, l in marks.triples((None, TAB.namesLevel, None))}
        # reference naming: a level whose emitted dim carries a name means the parent named it
        ref_named = {(nm, lvl) for (ax, lvl, nm, vals) in _ref_axis_dimensions(g, t, axis) if nm is not None}
        assert marked == ref_named, "%s: marks=%s ref=%s" % (key, marked, ref_named)


def _pipeline_dims(g, t):
    """Run pass1 + pass2 and read PivotedDimension RDF into (axis, level, name, frozenset(values))."""
    marks = _run("name-levels.rq", g)
    out = _run("recover-dimensions.rq", g, marks)
    dims = []
    for d in out.subjects(RDF.type, TAB.PivotedDimension):
        axis = str(out.value(d, TAB.onAxis)); lvl = int(out.value(d, TAB.atLevel))
        nm = out.value(d, TAB.dimensionName); nm = str(nm) if nm is not None else None
        vals = frozenset(str(v) for v in out.objects(d, TAB.hasDimensionValue))
        dims.append((axis, lvl, nm, vals))
    return sorted(dims, key=lambda z: (z[0], z[1]))


def test_pipeline_matches_axis_dimensions_semantics():
    for key, (axis, g, t) in _battery().items():
        ref = sorted(((ax, lvl, nm, frozenset(vals)) for (ax, lvl, nm, vals) in _ref_axis_dimensions(g, t, axis)),
                     key=lambda z: (z[0], z[1]))
        got = _pipeline_dims(g, t)
        assert got == ref, "%s: got=%s ref=%s" % (key, got, ref)
