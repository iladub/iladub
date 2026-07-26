"""writegate — enforce iladub's promotion invariant at the Fluree WRITE/commit gate.

STRUCTURAL: the commit gate reuses the full iladub epistemic membrane (iladub-shapes.ttl) —
a grounded node without an accountable promotion is REJECTED at commit. AUTHORIZATION (below):
a static f:modify AccessPolicy authorizes the write only to the promotion's dec:decidedBy agent.
This module is PROCEDURAL glue (graph parse, validate delegation, substring presence check) —
no domain decision, no tuned constant, no CONSTRUCT. f: is Fluree's vocabulary, consumed only
via the src/iladub/fluree/ template.
See docs/superpowers/specs/2026-07-25-fmodify-write-gate-design.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph, Namespace, RDF

from ..validate import validate, ValidationResult

_SHAPES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "shapes", "iladub-shapes.ttl")


def commit_gate_shapes() -> Graph:
    """The commit-gate shape-set: the full iladub epistemic membrane (reused, not re-authored)."""
    return Graph().parse(_SHAPES, format="turtle")


def gate_admits(transaction: Graph, knowledge: Graph) -> ValidationResult:
    """Would this transaction be admitted at the commit? Validate it against the iladub
    membrane; .conforms False => REJECTED (e.g. a grounded node with no accountable promotion)."""
    return validate(transaction, commit_gate_shapes(), knowledge)


F = Namespace("https://ns.flur.ee/db#")

# The full IRIs the f:modify f:query must reference to authorize a write ONLY to the
# promotion's accountable decider.
_MODIFY_REFS = (
    "?$identity",
    "https://w3id.org/iladub#wasPromotedBy",
    "https://w3id.org/iladub/dec#decidedBy",
)


@dataclass(frozen=True)
class ModifyVerdict:
    ok: bool
    is_modify: bool          # the policy is an f:AccessPolicy with f:action f:modify
    wires_accountable: bool  # its f:query resolves ?$identity through wasPromotedBy -> decidedBy


def certify_modify_authorization(f_modify_policy: Graph) -> ModifyVerdict:
    """Certify the f:modify policy authorizes a grounded-node write ONLY to the promotion's
    accountable dec:decidedBy agent: a SINGLE f:AccessPolicy with f:action f:modify whose
    OWN f:query wires ?$identity through wasPromotedBy -> decidedBy. The is_modify /
    wires_accountable flags are graph-wide (for diagnostics); ok requires one policy with both."""
    is_modify = False
    wires_accountable = False
    ok = False
    for pol in f_modify_policy.subjects(RDF.type, F.AccessPolicy):
        pol_is_modify = (pol, F.action, F.modify) in f_modify_policy
        pol_wires = any(
            all(ref in str(q) for ref in _MODIFY_REFS)
            for q in f_modify_policy.objects(pol, F.query)
        )
        is_modify = is_modify or pol_is_modify
        wires_accountable = wires_accountable or pol_wires
        if pol_is_modify and pol_wires:
            ok = True
    return ModifyVerdict(ok=ok, is_modify=is_modify, wires_accountable=wires_accountable)
