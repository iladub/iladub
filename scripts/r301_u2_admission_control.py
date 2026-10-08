"""U2 negative control: is dec:DecisionHolonShape actually exercised on the kept {t}-admission?
Withdraw as in r301_u2_admission_probe, then (i) remove all but one dec:optionSpace, (ii) remove dec:decidedBy;
each must make _validate refuse via the dec leg."""
import runpy, io, contextlib, re
from collections import Counter
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ns = runpy.run_path(__file__.replace("r301_u2_admission_control.py", "r301_u2_admission_probe.py"))
g, C, DEC, adm = ns["g"], ns["C"], ns["DEC"], ns["adm"]
from rdflib import Graph
def run(tag, gg):
    ok, text, legs = C._validate(gg)
    print(f"[{tag}] conforms={ok} legs={legs} shapes={dict(Counter(re.findall(r'Source Shape: (\S+)', text)))}")
g1 = Graph(); [g1.add(t) for t in g]
opts = list(g1.objects(adm, DEC.optionSpace))
for o in opts[1:]: g1.remove((adm, DEC.optionSpace, o))
run("optionSpace cut to 1", g1)
g2 = Graph(); [g2.add(t) for t in g]
g2.remove((adm, DEC.decidedBy, None))
run("decidedBy removed", g2)
