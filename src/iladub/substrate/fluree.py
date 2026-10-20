"""fluree — HTTP plug onto an external Fluree 4.x server (substrate:02).

PROCEDURAL (CLAUDE.md § 8): socket I/O, irreducible to AXIOM or NEURAL, and it makes NO decision.
It does not validate, and it reads nothing from a response body beyond the commit ``t`` on success;
the body is carried verbatim in ``CommitResult.report``. Whether a write is admitted is the
server's SHACL membrane's call. ``iladub.etkl.writegate.gate_admits`` remains the in-process
guarantee; this plug lets an oracle ask whether the *endpoint* agrees.

Status mapping (spec § 4.1): 2xx is accepted, 400 is a refusal (a value), and every other status or
connection failure raises ``FlureeEndpointError`` — a 404 from a wrong route must never read as the
membrane working.

Licence: Fluree DB 4.x is BUSL-1.1. It is used here and never redistributed nor offered as a
Database Service, and this plug imports no Fluree code (HTTP only).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from rdflib import Graph


class FlureeEndpointError(Exception):
    """Unexpected status or unreachable endpoint: not a refusal, and never to be read as one."""


@dataclass(frozen=True)
class CommitResult:
    accepted: bool
    status: int
    t: int | None
    report: str  # the engine's response body, verbatim


class FlureeEndpoint:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout  # an I/O bound; decides nothing

    def _send(self, req: urllib.request.Request) -> tuple[int, str]:
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as e:
            raise FlureeEndpointError(f"{req.full_url}: {e}") from e

    def _post(self, path: str, body: bytes, content_type: str) -> tuple[int, str]:
        req = urllib.request.Request(
            self.base_url + path, data=body, method="POST",
            headers={"Content-Type": content_type},
        )
        return self._send(req)

    def provision(self, ledger: str, shapes: Graph) -> CommitResult | None:
        """Create the ledger (201 required). Commit ``shapes`` first if non-empty; if empty,
        make no commit and return None (the only way to get an ungoverned ledger). A shapes
        commit that is not accepted raises ``FlureeEndpointError``: provisioning a ledger whose
        membrane never loaded must not look like success (producer-side guard, CLAUDE.md § R89)."""
        status, body = self._post(
            "/v1/fluree/create", json.dumps({"ledger": ledger}).encode(), "application/json")
        if status != 201:
            raise FlureeEndpointError(f"create {ledger!r}: unexpected status {status}: {body}")
        if len(shapes) == 0:
            return None
        res = self.commit(ledger, shapes)
        if not res.accepted:
            raise FlureeEndpointError(
                f"provision {ledger!r}: shapes commit refused ({res.status}): {res.report}")
        return res

    def commit(self, ledger: str, data: Graph) -> CommitResult:
        body = data.serialize(format="turtle").encode("utf-8")
        status, text = self._post(f"/v1/fluree/insert/{ledger}", body, "text/turtle")
        if 200 <= status < 300:
            return CommitResult(True, status, self._field(text, ("t",), "insert", ledger), text)
        if status == 400:
            return CommitResult(False, status, None, text)
        raise FlureeEndpointError(f"insert {ledger!r}: unexpected status {status}: {text}")

    def head_t(self, ledger: str) -> int:
        status, text = self._send(urllib.request.Request(
            f"{self.base_url}/v1/fluree/info/{ledger}", method="GET"))
        if status != 200:
            raise FlureeEndpointError(f"info {ledger!r}: unexpected status {status}: {text}")
        return self._field(text, ("ledger", "t"), "info", ledger)

    @staticmethod
    def _field(text: str, path: tuple[str, ...], what: str, ledger: str) -> int:
        """Read the commit ``t`` from a 2xx body; a body without it is an endpoint fault."""
        try:
            v = json.loads(text)
            for k in path:
                v = v[k]
        except (ValueError, KeyError, TypeError) as e:
            raise FlureeEndpointError(
                f"{what} {ledger!r}: 2xx body lacks {'.'.join(path)}: {text[:200]!r}") from e
        return v
