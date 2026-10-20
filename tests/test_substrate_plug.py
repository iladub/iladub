"""Default-suite tests for the Fluree plug (substrate:02, spec 2026-10-20 § 5.3). No Fluree needed."""
from __future__ import annotations

import re
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef

from iladub.substrate.fluree import FlureeEndpoint, FlureeEndpointError

_STATUS = {"ok200": 200, "bad400": 400, "nf404": 404, "err500": 500}


class _Stub(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.creates = 0
        self.inserts = 0


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silence
        pass

    def _reply(self, status, body):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if self.path == "/v1/fluree/create":
            self.server.creates += 1
            return self._reply(201, '{"t": 0}')
        m = re.fullmatch(r"/v1/fluree/insert/(\w+)", self.path)
        if m:
            self.server.inserts += 1
            status = _STATUS.get(m.group(1), 200)
            body = '{"t": 7}' if status == 200 else '{"error":"SHACL validation failed"}'
            return self._reply(status, body)
        self._reply(404, "{}")


@pytest.fixture()
def stub():
    srv = _Stub()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv, f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def _g() -> Graph:
    g = Graph()
    g.add((URIRef("urn:a"), URIRef("urn:p"), Literal("x")))
    return g


def test_status_mapping(stub):
    _, url = stub
    ep = FlureeEndpoint(url)
    ok = ep.commit("ok200", _g())
    assert ok.accepted is True and ok.t == 7
    bad = ep.commit("bad400", _g())
    assert bad.accepted is False and bad.status == 400 and bad.t is None
    assert "SHACL" in bad.report
    for name in ("nf404", "err500"):
        with pytest.raises(FlureeEndpointError):
            ep.commit(name, _g())


def test_connection_refused_raises():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    with pytest.raises(FlureeEndpointError):
        FlureeEndpoint(f"http://127.0.0.1:{port}").commit("x", _g())


def test_provision_empty_shapes_makes_no_commit(stub):
    srv, url = stub
    assert FlureeEndpoint(url).provision("ok200", Graph()) is None
    assert srv.creates == 1 and srv.inserts == 0


def test_plug_is_isolated():
    root = Path(__file__).resolve().parent.parent / "src" / "iladub"
    pat = re.compile(r"iladub\.substrate|from \.+substrate")
    offenders = []
    for p in root.rglob("*.py"):
        if "substrate" in p.relative_to(root).parts[:1]:
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if pat.search(line):
                offenders.append(f"{p}:{n}: {line.strip()}")
    assert offenders == []


# ---- agreement + fixture-helper tests (substrate:02 task 2); none needs the fluree binary ----

def test_in_process_membrane_agrees_on_the_ungoverned_input():
    from iladub.etkl.writegate import gate_admits
    from tests.substrate.doc_a import compiled_interior, ungoverned

    res = gate_admits(ungoverned(compiled_interior()), Graph())
    assert not res.conforms
    assert "INVARIANT: every grounded node must be produced by a promotion decision." \
        in res.report_text
    assert gate_admits(compiled_interior(), Graph()).conforms  # control: the governed one passes


def test_ungoverned_removes_exactly_the_one_promotion():
    from rdflib import Namespace
    from tests.substrate.doc_a import compiled_interior, ungoverned

    wpb = Namespace("https://w3id.org/iladub#").wasPromotedBy
    full = compiled_interior()
    assert len(list(full.triples((None, wpb, None)))) >= 1
    assert len(full) - len(ungoverned(full)) == len(list(full.triples((None, wpb, None))))
    assert list(ungoverned(full).triples((None, wpb, None))) == []


_FAKE = """import socket, sys, time
port = int(sys.argv[-1].rsplit(":", 1)[1])
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", port)); s.listen(5)
{tail}
"""


def _fake_binary(tmp_path, tail):
    import os
    import sys
    (tmp_path / "fake.py").write_text(_FAKE.format(tail=tail))
    p = tmp_path / "fakefluree"  # a sh wrapper: a shebang cannot carry a path containing spaces
    p.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{tmp_path / "fake.py"}" "$@"\n')
    os.chmod(p, 0o755)
    return str(p)


def test_start_helper_fails_fast_when_the_binary_exits_immediately():
    import time
    from tests.substrate.server import running_server

    t = time.monotonic()
    with pytest.raises(pytest.fail.Exception, match="exited with"):
        with running_server("/usr/bin/false", ready_bound=10.0):
            pass
    assert time.monotonic() - t < 10.0


def test_start_helper_fails_at_the_bound_with_stderr_when_never_ready(tmp_path):
    from tests.substrate.server import running_server

    binary = _fake_binary(tmp_path, 'sys.stderr.write("boom-marker\\n"); sys.stderr.flush()\n'
                                    "s.close(); time.sleep(60)")
    with pytest.raises(pytest.fail.Exception, match="boom-marker"):
        with running_server(binary, ready_bound=1.0):
            pass


def test_teardown_terminates_the_process_even_when_the_body_fails(tmp_path):
    from tests.substrate.server import running_server

    binary = _fake_binary(tmp_path, "time.sleep(60)")
    seen = {}
    with pytest.raises(RuntimeError, match="test body failed"):
        with running_server(binary, ready_bound=10.0) as (proc, _url):
            seen["proc"] = proc
            assert proc.poll() is None
            raise RuntimeError("test body failed")
    assert seen["proc"].poll() is not None


def test_ledger_names_are_distinct():
    from tests.substrate.server import ledger_namer

    f = ledger_namer()
    names = [f() for _ in range(50)]
    assert len(set(names)) == 50
    assert ledger_namer()() != ledger_namer()()
