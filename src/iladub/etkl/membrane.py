"""membrane — the ONE place any SHACL validation runs (spec 2026-08-06).

Both closed-world membranes (tiling.region_tiles' per-region gate and compile._validate's
whole-graph pass) call this seam. They keep their DISTINCT shape sets — that distinction is
semantic (intra-region vs whole-graph) and is not this module's business.

Gate classification (CLAUDE.md §8): PROCEDURAL engine glue only. No decision lives here —
the decisions are the SHACL shapes. Irreducible: a validator must be invoked from somewhere,
and the invocation carries no domain decision.
"""
from __future__ import annotations

import os
import re

from rdflib import Graph, RDF


def engine_name() -> str:
    """The engine this process validates with.

    rudof (Rust) is preferred where installed; pySHACL is the fallback AND the escape hatch:
    `ILADUB_MEMBRANE=pyshacl` re-runs any suspect verdict under the reference engine without
    a code change. Correctness is established by tests/etkl/test_membrane_equiv.py, not by
    trust — see spec 2026-08-06 §3.3.

    Fails LOUD, not silent: an `ILADUB_MEMBRANE` value that names neither engine is a
    misconfiguration, not a silent fallback — and forcing `rudof` on a process where
    `pyrudof` isn't importable must not quietly resolve to pySHACL, or an operator who
    thinks they forced the new engine has actually re-run the old one unnoticed.
    """
    forced = os.environ.get("ILADUB_MEMBRANE")
    if forced:
        if forced not in ("pyshacl", "rudof"):
            raise ValueError(
                f"ILADUB_MEMBRANE={forced!r} is not a known engine (expected 'pyshacl' or "
                f"'rudof')")
        if forced == "rudof" and not rudof_available():
            raise ValueError(
                "ILADUB_MEMBRANE=rudof was forced but pyrudof is not installed")
        return forced
    return "rudof" if rudof_available() else "pyshacl"


def validate(data_graph: Graph, shapes_graph: Graph, ont_graph: Graph,
             engine: str | None = None) -> tuple[bool, str]:
    """(conforms, report_text) for `data_graph` against `shapes_graph`.

    Both engines now validate the SAME subclass-only-closed artifact (spec
    2026-08-06-subclass-only-closure-design.md, spec 2026-08-13-membrane-parity-design.md §3):
    the seam expands `data_graph` with `subclass_closure`, serializes it to N-Triples ONCE via
    `_payload`, and hands each engine its own inference turned OFF — with each engine parsing
    that one shared document through its own parser. **Both engines receive the same N-Triples
    document; each parses it with its own parser; parser differences are engine differences** —
    that is the parity contract, and `ILADUB_MEMBRANE=pyshacl` isolates the engine (plus its
    parser) as intended, rather than also swapping the inference semantics underneath it. SHACL
    advanced features on. Callers must not depend on the report's exact wording — it differs by
    engine; only its content (shape names, focus nodes) is stable.

    `engine` NAMES THE ENGINE THIS CALL SITE WANTS, and it outranks `ILADUB_MEMBRANE`.
    Its reason changed on 2026-08-13 and the difference matters to anyone reading this:

    HISTORY, no longer justification. Until this date `engine` was a CAPABILITY PIN, and
    `compile._DEC_ENGINE = "pyshacl"` used it. MEASURED 2026-08-10: rudof cannot evaluate an
    `sh:sparql` constraint whose focus node is a blank node — it binds `$this` through
    `VALUES $this { _:b… }`, which is illegal SPARQL, and raises `ValueError: … expected
    UNDEF` instead of returning a verdict. `dec-shapes.ttl:23` and `iladub-shapes.ttl:67`
    are exactly such constraints, and the promotion emitters mint blank-node subjects
    (`ground.py:90,145`, `promote.py:67,114,158`, `splitkey.py:125`). `_payload` now
    SKOLEMIZES, so the membrane can no longer hand rudof a blank-node focus node at all and
    the pin is gone (spec 2026-08-13-membrane-parity-design.md §4.3, closing R88).

    **rudof did NOT gain the capability — we routed around it.** That upstream incapacity is
    still pinned, directly against `pyrudof` on an un-skolemized serialization, by
    `tests/etkl/test_membrane_equiv.py::test_rudof_itself_still_cannot_evaluate_sparql_on_a_blank_node_focus`.
    It is the standing justification for the skolemize step; when it starts failing, the step
    can be reconsidered.

    What survives is the LOUDNESS rule, and it is unchanged: an `ILADUB_MEMBRANE` that
    conflicts with an explicit `engine=` RAISES rather than quietly running the other engine.
    An operator who thinks they forced one engine must never be handed the other's verdict
    unannounced (the same rule `engine_name` already keeps). No caller in `src/` passes
    `engine` any more; it remains for tests and for an operator's one-off differential.

    The report text is DE-SKOLEMIZED here, at the public seam, and deliberately NOT inside
    the leg functions: a skolem IRI is an artifact of this module's transport and must never
    reach the human who reads a refusal, but `tests/etkl/test_membrane_equiv.py`'s differential
    compares one engine's raw results graph against the other's raw report, and cleaning only
    the side that goes through a leg function would manufacture a difference that is ours, not
    the engines'.
    """
    if engine is None:
        engine = engine_name()
    else:
        if engine not in ("pyshacl", "rudof"):
            raise ValueError(
                f"engine={engine!r} is not a known engine (expected 'pyshacl' or 'rudof')")
        forced = os.environ.get("ILADUB_MEMBRANE")
        if forced and forced != engine:
            raise ValueError(
                f"ILADUB_MEMBRANE={forced!r} conflicts with an explicit engine={engine!r} at "
                f"this call site. Resolving it silently would hand an operator who forced one "
                f"engine the other engine's verdict unannounced.")
    if engine == "rudof":
        conforms, report = _validate_rudof(data_graph, shapes_graph, ont_graph)
    else:
        conforms, report = _validate_pyshacl(data_graph, shapes_graph, ont_graph)
    return conforms, _deskolemize(report)


def _validate_pyshacl(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    """pySHACL's own inference is OFF (`inference="none"`): the seam supplies the SAME
    subclass-only closure `_validate_rudof` uses, via `subclass_closure`, so this path no
    longer materialises domain/range typing either (R19's mechanism — see
    `subclass_closure`'s docstring). Before this, `_validate_pyshacl` was the ONLY path that
    still ran full RDFS inference (`inference="rdfs"`), so any install without `pyrudof` (core
    and `[etkl]` installs both lack it) kept R19 alive under a different name.

    Takes `_payload`'s re-parsed Graph — not `subclass_closure`'s output directly (spec
    2026-08-13 §3): the two engines must be handed the SAME artifact, and the artifact is the
    N-Triples document, not the in-memory graph that produced it."""
    from pyshacl import validate as _v
    graph_payload, _ = _payload(data_graph, ont_graph)
    conforms, _, text = _v(
        graph_payload, shacl_graph=shapes_graph, inference="none", advanced=True)
    return bool(conforms), text


_RUDOF = None          # persistent instance: shapes parse ONCE (0.02 s), data resets per call


def rudof_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("pyrudof") is not None


def _rudof_instance(shapes_graph):
    """One instance per process, keyed by the shapes graph's identity — the two call sites
    use DIFFERENT shape sets, so a single cached instance would validate against the wrong
    one. Shapes parsing is 0.02 s; data loading (0.58 s on an 8k-triple page) dominates and
    is per-call regardless.

    The cache holds a STRONG reference to `shapes_graph` deliberately, compared with `is`:
    an id()-only key is unsafe because CPython reuses object ids after garbage collection, so
    a freed shapes graph's address could later be handed to an unrelated Graph, silently
    matching the stale cache entry and validating against the wrong shape set with no error.
    That the two production call sites (`compile._FULL_SHAPES`, `tiling._TILING_SHAPES`)
    happen to hold process-lifetime singletons is not a guarantee a future caller inherits —
    keeping the graph alive here removes the hazard regardless of caller lifetime."""
    global _RUDOF
    import pyrudof
    if _RUDOF is None or _RUDOF[0] is not shapes_graph:
        r = pyrudof.Rudof(pyrudof.RudofConfig())
        r.read_shacl(shapes_graph.serialize(format="turtle"), format=pyrudof.ShaclFormat.Turtle)
        _RUDOF = (shapes_graph, r)
    return _RUDOF[1]


def _conforms_from_report(report: str) -> bool:
    """The verdict, read as RDF rather than matched as text.

    A substring test over the report is unsound: rudof echoes offending literal values into
    sh:value, so a graph containing the token would flip the verdict — measured, a violating
    graph read as conforming. Fails CLOSED: an unparseable or ambiguous report is never
    conformance.
    """
    from rdflib import Graph as _Graph, Literal as _Literal
    from rdflib.namespace import SH
    try:
        g = _Graph().parse(data=report, format="turtle")
    except Exception:
        return False
    vals = list(g.objects(None, SH.conforms))
    return len(vals) == 1 and vals[0] == _Literal(True)


def _rudof_on_payload(nt_payload: str, shapes_graph) -> tuple[bool, str]:
    """Drive rudof over an ALREADY-BUILT N-Triples payload. The whole of `_validate_rudof`
    below except the payload construction.

    It exists as its own seam because two tests must reach rudof with a payload the membrane's
    literal-hygiene guard forbids (`_payload` called with the guard disabled — see `_payload`'s
    docstring), and the alternative shapes are both worse: adding an `audit` parameter to
    `_validate_rudof` would put a guard-disarming switch on a PRODUCTION entry point, and
    copying these six lines into the tests would let this leg's engine settings
    (`ShaclValidationMode.Native`, the Turtle result format) drift out of step with the tests
    that claim to reproduce them.
    Splitting the seam keeps one definition of "how this repo drives rudof" and leaves the
    production entry point with no way to turn the guard off.

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue — an invocation, no decision."""
    import pyrudof
    r = _rudof_instance(shapes_graph)
    r.reset_data()
    r.read_data(nt_payload, format=pyrudof.RDFFormat.NTriples)
    r.validate_shacl(mode=pyrudof.ShaclValidationMode.Native)
    report = str(r.serialize_shacl_validation_results(
        pyrudof.ResultShaclValidationFormat.Turtle))
    return _conforms_from_report(report), report


def _validate_rudof(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    """rudof does NO inference of its own — the seam now supplies a SUBCLASS-ONLY closure
    (spec 2026-08-06-subclass-only-closure-design.md), not the old full RDFS closure:
    domain/range typing is gone by design (the R19 mechanism), and its literal-subject filter
    is what makes the payload parseable by rudof's strict reader.

    Takes `_payload_nt`'s N-Triples string — the same document `_payload` hands pySHACL, minus
    the re-parse into a `Graph` this leg has no use for (`pyrudof.read_data` takes a string).
    `_payload_nt` is called with its `audit` default, so this leg RAISES on a literal the guard
    forbids; there is deliberately no parameter here that can turn that off."""
    nt_payload = _payload_nt(data_graph, ont_graph)
    return _rudof_on_payload(nt_payload, shapes_graph)


def audit_literals(graph: Graph) -> None:
    """INVARIANT GUARD, not a repair — same idiom as `subclass_closure`'s literal-subject
    filter ("an INVARIANT GUARD here, not a repair", in that function's own docstring further
    down this file). Raises `ValueError` on the first violation and otherwise
    does nothing; it never rewrites, coerces, or normalises a literal — a repair belongs to the
    emitter, never to engine glue (CLAUDE.md §2).

    Two invariants, licensed by spec 2026-08-13-membrane-parity-design.md §4.2 / P5 (measured:
    17 TYPE, 0 LEXICAL hits across the 1141-test fast suite, every one in a test fixture, none
    in a `src/` emitter; 0 violations on every corpus-marked test, 36, on real documents):

    - LEXICAL — a literal's lexical form must equal what rdflib's OWN parser produces for that
      same string under the same datatype. Catches the `5e-05` class (spec P2): exponential
      notation is outside `xsd:decimal`'s lexical space, so rdflib's N-Triples parser silently
      rewrites it to `0.00005` on the way back in — the guard makes that silent rewrite
      unreachable instead of letting `_payload`'s round trip launder it.
    - TYPE — a literal's `.value` Python type must equal the type that same reparse produces.
      Catches R92's class: minting an `xsd:decimal` literal from a bare Python `round()` (rather
      than `Decimal(str(round(...)))`) keeps a Python `float` as `.value` while its lexical
      form is a valid `xsd:decimal`, so pySHACL's own `isinstance(value, Decimal)` datatype
      check refuses it while rudof — which only ever reads the lexical form — admits it.

    Both invariants are measured by actually reparsing the literal's own lexical form
    (`Literal(str(o), datatype=o.datatype)`) rather than consulting rdflib's private datatype
    table by IRI: the guard is then exactly as strict as `_payload`'s own N-Triples round trip
    (`_validate_pyshacl`'s docstring), and can never drift out of step with it.

    LEXICAL is checked FIRST: a lexical defect also produces a spurious type mismatch on
    reparse (the `5e-05` literal above is float-valued too), so checking TYPE first would
    misreport a lexical defect as a type one and hide the actual defect class from the raised
    message.

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue. A representation-invariant
    check against rdflib's own parser — it inspects no business value, shape, or domain
    decision, and the comparison is exact equality, never a tuned constant or tolerance.
    """
    from rdflib import Literal as _Literal

    for s, p, o in graph:
        if not isinstance(o, _Literal) or o.datatype is None:
            continue
        lexical = str(o)
        reparsed = _Literal(lexical, datatype=o.datatype)
        qname = graph.namespace_manager.qname(o.datatype)
        if str(reparsed) != lexical:
            raise ValueError(
                f"non-canonical lexical form on {p} at {s!r}: {lexical!r} is typed {qname} but "
                f"rdflib's own parser round-trips it to {str(reparsed)!r} — the transport would "
                f"silently rewrite this literal (spec 2026-08-13-membrane-parity-design.md "
                f"§4.2, LEXICAL)")
        if type(o.value) is not type(reparsed.value):
            raise ValueError(
                f"float-valued {qname} on {p} at {s!r}: .value is a Python "
                f"{type(o.value).__name__}, not a {type(reparsed.value).__name__} — a validator "
                f"whose datatype check is isinstance(value, {type(reparsed.value).__name__}) "
                f"refuses this literal while one reading only the lexical form admits it (R92, "
                f"spec 2026-08-13-membrane-parity-design.md §4.2, TYPE). Use "
                f"Decimal(str(round(x, n))) rather than round(x, n) when minting an {qname} "
                f"literal.")


# The skolem IRI space this module mints, and the ONLY definition of it: `_payload_nt` builds
# skolem IRIs from these two strings and `_deskolemize` strips exactly the same prefix, so the
# two can never drift apart. They are passed EXPLICITLY rather than taking rdflib's defaults
# (`https://rdflib.github.io/.well-known/genid/rdflib/N…`, MEASURED on rdflib 7.6.0) because a
# de-skolemizer keyed on another library's private default silently stops matching the day that
# default moves — and a silent miss here leaks a skolem IRI into a human-read refusal.
#
# `.well-known/genid/` is RDF 1.1 §3.5's skolemization form; the authority is the iladub
# namespace root because these IRIs are ours. Gate note (CLAUDE.md §8): an IRI namespace, not a
# tuned constant — no verdict, threshold or tolerance depends on its value.
_SKOLEM_AUTHORITY = "https://w3id.org/iladub/"
_SKOLEM_BASEPATH = ".well-known/genid/membrane/"
_SKOLEM_PREFIX = _SKOLEM_AUTHORITY + _SKOLEM_BASEPATH

# The label class is whatever an N-Triples/Turtle IRI may carry: everything except the
# delimiters RDF 1.1 excludes from IRIREF. The optional angle brackets let one substitution
# handle rudof's Turtle report (`<…>`) and pySHACL's prose report alike.
_SKOLEM_IRI = re.compile("<?" + re.escape(_SKOLEM_PREFIX) + r'([^\s<>"{}|\\^`]+)>?')


def _deskolemize(report: str) -> str:
    """Put the blank-node labels back into REPORT TEXT. Never applied to data.

    Skolemization (see `_payload_nt`) is a transport mechanism: it exists so rudof is never handed
    a blank-node focus node. A human reading a refusal must not have to know that. MEASURED
    (spec §2 P3): before this, `Focus Node: <https://rdflib.github.io/.well-known/genid/rdflib/
    Nbb35…>` is what a reader got.

    It runs on the report STRING, not on a parsed results graph, because the two engines' reports
    are different kinds of document — rudof's is Turtle, pySHACL's is prose — and only the text
    is common to both. It runs AFTER `_conforms_from_report` has read the verdict, never before:
    a de-skolemized label is a blank-node label again, and an unusual label could make the Turtle
    unparseable, which `_conforms_from_report` reads (correctly, for its own purpose) as
    non-conformance. The verdict must never depend on presentation.

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue — the inverse of a serialization
    step this module performs itself, over its own IRI space. No domain decision, no tolerance.
    """
    return _SKOLEM_IRI.sub(lambda m: "_:" + m.group(1), report)


def _payload_nt(data_graph: Graph, ont_graph: Graph, *, audit: bool = True) -> str:
    """THE artifact — the N-Triples document both engines validate. See `_payload`.

    Split out from `_payload` so the rudof leg can stop paying for a `Graph` it never uses:
    `pyrudof.read_data` takes this string, and re-parsing it into an rdflib `Graph` only to
    discard it is pure waste. MEASURED 2026-08-13 on the real 8.6k-triple stem page
    (corpus/ag-trade/graincorp-stem-2026-07-31.pdf page 0, 9,286-triple closure, 1.34 MB of
    N-Triples): the re-parse alone is 170 ms, and end to end `_payload` is 339 ms against this
    function's 192 ms — 148 ms per call the rudof leg no longer pays, against a 761 ms leg.
    rudof is the DEFAULT engine wherever `pyrudof` is installed and `tiling.region_tiles` calls
    the membrane once per candidate region, so that was the most-exercised path in the repo
    paying for nothing.
    """
    expanded = subclass_closure(data_graph, ont_graph)
    if audit:
        audit_literals(expanded)
    # SKOLEMIZE — the unpin (spec 2026-08-13 §4.3, closing R88). AFTER `audit_literals`, so the
    # guard still sees the graph exactly as the emitters built it, and BEFORE serialization,
    # because the point is that no `_:b` label ever reaches an engine.
    #
    # WHY: rudof raises rather than answering on an `sh:sparql` constraint whose focus node is a
    # blank node (it emits `VALUES $this { _:b… }`, which is illegal SPARQL). Skolemization
    # removes every blank node, so the question cannot arise. MEASURED verdict-neutral for
    # pySHACL in both directions and unblocking for rudof in both (spec §2 P3, four independent
    # confirmations), and no shape can tell the difference: no shape file uses `sh:nodeKind` and
    # no `sh:sparql` body tests `isBlank`/`isIRI`/`isURI`/`BNODE` (spec §2 P4).
    #
    # It is a transport concern only. The skolemized graph is a copy that dies with this call,
    # and `_deskolemize` takes the labels back out of the report text at the public seam.
    return expanded.skolemize(
        authority=_SKOLEM_AUTHORITY, basepath=_SKOLEM_BASEPATH).serialize(format="nt")


def _payload(data_graph: Graph, ont_graph: Graph, *, audit: bool = True) -> tuple[Graph, str]:
    """The ONE artifact both engines validate (spec 2026-08-13 §3, closing R94's asymmetry).

    `pyrudof.read_data` takes a string; rudof can never be handed a live rdflib `Graph` — so
    "hand rudof a live-equivalent graph" is not an option, and the only shape parity can take is
    a single shared serialization that each engine then parses with its OWN parser. **Both
    engines receive the same N-Triples document; each parses it with its own parser; parser
    differences are engine differences** — that is the whole contract, and it replaces the
    previous, false claim that the two legs already shared a graph.

    Before this, `_validate_pyshacl` validated `subclass_closure`'s live Graph directly while
    `_validate_rudof` validated `expanded.serialize(format="nt")` — two DIFFERENT artifacts
    built from the same closure call, so a divergence between the legs could be an artifact
    difference wearing an engine's name. This function removes that class of confound: it
    closes, serializes to N-Triples exactly ONCE, and re-parses that one string back into the
    Graph pySHACL validates — so pySHACL's input is now, byte-for-byte, the same document
    rudof's input has always been.

    `audit` runs `audit_literals` (spec §4.2) over the closure before serializing — the literal-
    hygiene guard that parity itself blinded (byte-parity makes both legs consume the SAME
    repaired document, so the old accidental pySHACL-vs-rudof split on a float-valued
    `xsd:decimal` disappeared along with the divergence it happened to catch). Defaults to ON;
    turning `audit` off is a HAZARD, not a preference, and is fenced by
    `test_the_audit_escape_hatch_is_not_used_in_production` (tests/etkl/test_decimal_typing.py)
    to exactly the two tests that must construct the forbidden form on purpose to falsify the
    guard or pin the transport it guards against — never a `src/` call site.

    The document itself is built by `_payload_nt`; this function adds the re-parse pySHACL needs
    (it takes a `Graph`, never a string). The rudof leg calls `_payload_nt` directly — same
    bytes, no wasted parse. **Both engines still receive the same document**; only pySHACL pays
    to turn it back into a graph, because only pySHACL can be handed one.

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue. A validator must be handed
    bytes from somewhere, and deciding how those bytes are produced and shared carries no
    domain decision — nothing here inspects a value, a shape, or a threshold. No tuned
    constant or tolerance appears.
    """
    nt_payload = _payload_nt(data_graph, ont_graph, audit=audit)
    return Graph().parse(data=nt_payload, format="nt"), nt_payload


def rdfs_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """SUPERSEDED for production (spec 2026-08-06-subclass-only-closure-design.md): the seam now
    calls `subclass_closure`. This function is RETAINED as the reference implementation the
    closure differential (tests/etkl/test_closure_equiv.py) compares against — it is what
    pySHACL's `inference="rdfs"` produces, so it is the baseline any claim of "no verdict
    changed" must be measured against. Not called in production.

    A NEW graph: data + ontology axioms, RDFS-expanded, minus every literal-subject triple.

    Reproduces exactly what pySHACL's `inference="rdfs"` does today — subclass closure AND
    domain/range typing (the latter is the R19 mechanism, deliberately preserved here; the
    successor loop, spec 2026-08-06 §7, is where dropping it is argued and measured).

    The ontology is mixed in via pySHACL's own `inoculate()` (the RDFS/OWL axiom whitelist:
    classes and properties typed/predicated as RDFS or OWL vocabulary), NOT a full graph
    union. `Validator.mix_in_ontology()` uses `inoculate()` by default (`PYSHACL_USE_FULL_MIXIN`
    is unset in this repo), so a full union would inject ontology content — arbitrary
    non-axiom triples the ontology graph happens to carry — that pySHACL never puts in the
    validated graph. That mismatch would make the Task 4 engine differential compare two
    different graphs, not two engines on the same graph. Calling pySHACL's function (rather
    than re-implementing the whitelist by hand) guarantees the match and tracks upstream.

    The literal-subject filter is NOT optional: owlrl's closure emits triples whose subject
    is a Literal (`"307.47"^^xsd:decimal rdf:type rdfs:Resource`), which is illegal RDF.
    rdflib tolerates them; a strict parser rejects the whole graph. They are semantically
    vacuous, so dropping them changes no verdict.

    The RDFS semantics class is pySHACL's own `CustomRDFSSemantics`, NOT plain
    `owlrl.RDFS_Semantics`. Plain `RDFS_Semantics` runs owlrl's `one_time_rules()`, which
    does literal VALUE-SPACE unification and fabricates triples: measured on the
    test_row_groups fixture, a cell with `tab:onPage "0"^^xsd:integer` came out of closure
    ALSO carrying a fabricated `"0.0"^^xsd:decimal` twin, invented from an unrelated
    xsd:decimal elsewhere in the graph because 0 and 0.0 are the same value. That fabricated
    literal then fails `sh:datatype xsd:integer` — rudof would refuse a graph pySHACL admits.
    pySHACL avoids this itself (`pyshacl/inference/custom_rdfs_closure.py`: `CustomRDFSSemantics`
    overrides `one_time_rules()` to a no-op, with the docstring "These rules usually add
    'hidden' literals to the graph in such a way that breaks some SHACL validation tests").
    We reuse pySHACL's own class rather than re-suppressing the rule by hand, for the same
    reason as the `inoculate` mix-in above: the two engines must validate the same graph.
    """
    from pyshacl.inference.custom_rdfs_closure import CustomRDFSSemantics
    from pyshacl.rdfutil.inoculate import inoculate
    from rdflib import Literal as _Literal
    import owlrl
    merged = Graph()
    merged += data_graph
    inoculate(merged, ont_graph)
    owlrl.DeductiveClosure(CustomRDFSSemantics).expand(merged)
    out = Graph()
    for s, p, o in merged:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    return out


def subclass_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """A NEW graph: the data plus its own rdfs:subClassOf type closure. Nothing else.

    The ontology is READ for its `rdfs:subClassOf` axioms and never mixed in, so no ontology
    node can become a focus node and the validated graph is data plus its type closure.
    Axioms are sourced from `ont_graph` ONLY: any `rdfs:subClassOf` triple appearing in
    `data_graph` itself is copied through into the output (it is ordinary data, like any other
    triple) but is never consulted for materialisation — inert today, since nothing under
    `src/iladub/` emits `rdfs:subClassOf` into a data graph.

    WHAT THIS DELIBERATELY DOES NOT DO (spec 2026-08-06-subclass-only-closure-design.md):
    domain/range typing. A node no longer becomes a `tab:Cell` merely by carrying
    `tab:hasBBox` — that inference is the R19 accident, and dropping it closes that hazard at
    its root. Measured on the real stem page: the only typings lost are 2,105 vacuous
    `rdfs:Resource`, 207 ontology-node types, and 18 `tab:LabelCell` — and NO shape targets
    `tab:LabelCell`, so no verdict changes. Consequence to know: `sh:class tab:BBox` becomes
    FALSIFIABLE again, because `tab:hasBBox`'s range no longer types its object regardless
    (all 586 bbox objects on the real page are explicitly typed, so nothing relied on it).

    The literal-subject filter is an INVARIANT GUARD here, not a repair: no code path in this
    function can emit a literal-subject triple (unlike owlrl's closure, which emitted 1,533).

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue — a transitive closure over
    declared axioms. No domain decision, no tuned constant.
    """
    from rdflib import Literal as _Literal
    from rdflib.namespace import RDFS

    supers: dict = {}
    for a, _, b in ont_graph.triples((None, RDFS.subClassOf, None)):
        supers.setdefault(a, set()).add(b)
    changed = True                       # transitive closure over the axioms, computed once
    while changed:
        changed = False
        for a in list(supers):
            for b in list(supers[a]):
                for c in supers.get(b, ()):
                    if c not in supers[a]:
                        supers[a].add(c)
                        changed = True

    out = Graph()
    for s, p, o in data_graph:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    for s, _, cls in data_graph.triples((None, RDF.type, None)):
        if isinstance(s, _Literal):
            continue
        for c in supers.get(cls, ()):
            out.add((s, RDF.type, c))
    return out
