"""iladub assertion/proposition boundary invariants (monorepo layout)."""
import os
from rdflib import Graph
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT,"vocab","ontology"); SH = os.path.join(ROOT,"vocab","shapes")
EX  = os.path.join(ROOT,"examples"); TST = os.path.join(ROOT,"tests")

def _g(*p):
    g=Graph()
    for x in p: g.parse(x, format="turtle")
    return g
def _v(data, shapes, ont):
    c,_,t = validate(_g(*data), shacl_graph=_g(shapes), ont_graph=_g(*ont),
                     inference="rdfs", advanced=True); return c,t

S=os.path.join(SH,"iladub-shapes.ttl"); O=os.path.join(ONT,"iladub.ttl")

def test_proposal_wellformed():
    c,t=_v([os.path.join(EX,"proposal.ttl")],S,[O]); assert c,t
def test_promotion_grounds():
    c,t=_v([os.path.join(EX,"proposal.ttl"),os.path.join(EX,"promotion.ttl")],S,[O]); assert c,t
def test_promotion_is_real_decision_holon():
    c,t=_v([os.path.join(EX,"proposal.ttl"),os.path.join(EX,"promotion.ttl")],
           os.path.join(SH,"dec-shapes.ttl"),[os.path.join(ONT,"dec.ttl")]); assert c,t
def test_leak_rejected():
    c,_=_v([os.path.join(TST,"leak-attempt.ttl")],S,[O]); assert not c
