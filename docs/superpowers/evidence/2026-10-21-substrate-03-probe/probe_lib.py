"""probe03 shared harness: start `fluree server run --memory` as tests/substrate/server.py does,
send stdlib-urllib requests, and log every request/response verbatim. Measurement only."""
import contextlib, json, os, socket, subprocess, tempfile, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = "/opt/homebrew/bin/fluree"

F = "https://ns.flur.ee/db#"
EX = "http://example.org/"
ETKL = "https://w3id.org/iladub/etkl#"
PROV = "http://www.w3.org/ns/prov#"
SH = "http://www.w3.org/ns/shacl#"
U, A, B, W, S = (EX + x for x in ("U", "A", "B", "W", "S"))
PC = F + "AccessPolicy"

PREFIXES = f"""PREFIX ex: <{EX}>
PREFIX etkl: <{ETKL}>
PREFIX prov: <{PROV}>
PREFIX sh: <{SH}>
PREFIX f: <{F}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def server():
    port = free_port()
    err = tempfile.TemporaryFile()
    proc = subprocess.Popen([BIN, "server", "run", "--memory", "--listen-addr", f"127.0.0.1:{port}"],
                            stdout=subprocess.DEVNULL, stderr=err)
    try:
        deadline = time.monotonic() + 30
        while True:
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
                break
            except OSError:
                if proc.poll() is not None or time.monotonic() > deadline:
                    err.seek(0)
                    raise RuntimeError(err.read().decode())
                time.sleep(0.1)
        yield Client(f"http://127.0.0.1:{port}")
    finally:
        proc.terminate()
        proc.wait(timeout=10)


class Client:
    def __init__(self, base):
        self.base = base
        self.log = []

    def req(self, method, path, body=None, headers=None, label=""):
        headers = dict(headers or {})
        data = body.encode() if isinstance(body, str) else body
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                st, txt = resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            st, txt = e.code, e.read().decode("utf-8", "replace")
        self.log.append({"label": label, "method": method, "path": path, "headers": headers,
                         "body": body, "status": st, "response": txt})
        return st, txt

    # --- helpers --------------------------------------------------------------------------
    def create(self, ledger):
        return self.req("POST", "/v1/fluree/create", json.dumps({"ledger": ledger}),
                        {"Content-Type": "application/json"}, label=f"create {ledger}")

    def t(self, ledger):
        st, txt = self.req("GET", f"/v1/fluree/info/{ledger}", label="info")
        try:
            return json.loads(txt)["ledger"]["t"]
        except Exception:
            return f"?({st})"

    def insert_ttl(self, ledger, ttl, headers=None, label=""):
        h = {"Content-Type": "text/turtle", **(headers or {})}
        return self.req("POST", f"/v1/fluree/insert/{ledger}", ttl, h, label=label)

    def update(self, ledger, sparql, headers=None, label=""):
        h = {"Content-Type": "application/sparql-update", **(headers or {})}
        return self.req("POST", f"/v1/fluree/update/{ledger}", PREFIXES + sparql, h, label=label)

    def insert_jsonld(self, ledger, doc, headers=None, label=""):
        h = {"Content-Type": "application/json", **(headers or {})}
        return self.req("POST", f"/v1/fluree/insert/{ledger}", json.dumps(doc), h, label=label)

    def sparql(self, ledger, q, headers=None, label=""):
        h = {"Content-Type": "application/sparql-query", "Accept": "application/sparql-results+json",
             **(headers or {})}
        return self.req("POST", f"/v1/fluree/query/{ledger}", PREFIXES + q, h, label=label)

    def count_docs(self, ledger, headers=None, label=""):
        st, txt = self.sparql(ledger, "SELECT ?d WHERE { ?d a ex:Doc }", headers, label=label)
        return st, _nrows(txt), txt

    def jsonq(self, ledger, q, headers=None, label=""):
        h = {"Content-Type": "application/json", **(headers or {})}
        return self.req("POST", f"/v1/fluree/query/{ledger}", json.dumps(q), h, label=label)

    def dump(self, name):
        p = os.path.join(HERE, f"{name}.log.json")
        with open(p, "w") as fh:
            json.dump(self.log, fh, indent=1)
        return p


def _nrows(txt):
    try:
        v = json.loads(txt)
    except ValueError:
        return None
    if isinstance(v, dict) and "results" in v:
        return len(v["results"]["bindings"])
    if isinstance(v, list):
        return len(v)
    return None


def ident(iri, policy_class=True):
    h = {"fluree-identity": iri}
    if policy_class:
        h["fluree-policy-class"] = PC
    return h


def short(txt, n=220):
    return " ".join(txt.split())[:n]


# --- fixture data ---------------------------------------------------------------------------
BASE_TTL = f"""@prefix ex: <{EX}> . @prefix etkl: <{ETKL}> . @prefix prov: <{PROV}> .
@prefix sh: <{SH}> .
ex:DocShape a sh:NodeShape ; sh:targetClass ex:Doc ;
  sh:property [ sh:path ex:title ; sh:minCount 1 ] .
ex:d1 a ex:Doc ; ex:title "one" ; etkl:sensitivity ex:tagPublic .
ex:d2 a ex:Doc ; ex:title "two" ; etkl:sensitivity ex:tagClinical .
ex:d3 a ex:Doc ; ex:title "three" ; etkl:sensitivity ex:tagSecret .
ex:roleClinician etkl:grantsTag ex:tagPublic , ex:tagClinical .
ex:roleSteward etkl:grantsTag ex:tagPublic , ex:tagClinical , ex:tagSecret .
ex:U etkl:hasRole ex:roleClinician .
ex:A prov:actedOnBehalfOf ex:U .
ex:W etkl:hasRole ex:roleClinician .
ex:S etkl:hasRole ex:roleSteward .
"""
# ex:B: an agent with no principal (mentioned only so it exists as a subject)
BASE_TTL += "ex:B a prov:SoftwareAgent .\nex:A a prov:SoftwareAgent .\n"

# the view policy, verbatim from src/iladub/fluree/f-policy-template.jsonld
VIEW_QUERY_ASIS = json.dumps({"where": [
    {"@id": "?$identity", PROV + "actedOnBehalfOf": {"@id": "?principal"}},
    {"@id": "?principal", ETKL + "hasRole": {"@id": "?role"}},
    {"@id": "?role", ETKL + "grantsTag": {"@id": "?tag"}},
    {"@id": "?$this", ETKL + "sensitivity": {"@id": "?tag"}}]})


def policy_node(pid, action, query, required=True, on_class=None, on_property=None, allow=None):
    n = {"@id": pid, "@type": [F + "AccessPolicy"], F + "action": [{"@id": F + action}]}
    if required:
        n[F + "required"] = True
    if query is not None:
        n[F + "query"] = query
    if allow is not None:
        n[F + "allow"] = allow
    if on_class:
        n[F + "onClass"] = [{"@id": c} for c in on_class]
    if on_property:
        n[F + "onProperty"] = [{"@id": p} for p in on_property]
    return n


POLICIES_USED = {}


def store_policy(c, ledger, node, headers=None, label=""):
    POLICIES_USED[node["@id"]] = node
    return c.insert_jsonld(ledger, {"@graph": [node]}, headers, label=label or f"store {node['@id']}")


def dump_policies(name):
    p = os.path.join(HERE, f"{name}.policies.jsonld")
    with open(p, "w") as fh:
        json.dump({"@graph": list(POLICIES_USED.values())}, fh, indent=1)
    return p
