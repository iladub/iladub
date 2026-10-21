import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
with server() as c:
    L="smoke"
    print(c.create(L))
    print(c.t(L))
    st,txt=c.insert_ttl(L,BASE_TTL); print(st,short(txt))
    print(c.t(L))
    print(c.count_docs(L))
    st,txt=c.insert_ttl(L,"@prefix ex: <http://example.org/> . ex:bad a ex:Doc ."); print("invalid",st,short(txt,400))
    st,txt=c.update(L,"INSERT DATA { ex:d4 a ex:Doc ; ex:title \"four\" }"); print("upd",st,short(txt))
    print(c.t(L))
    c.dump("smoke")
