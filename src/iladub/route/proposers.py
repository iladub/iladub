"""The router's model proposers for Q-boundary and Q-doctype, with recorded replay.

NEURAL (CLAUDE.md § 8): both questions are reading judgements a person answers at a glance
(does a new document start here? what kind of document is this?), so a model proposes and an oracle
disposes (Task 3: route-boundary.rq, route-checklist.rq). A proposer's answer is never trusted here:
this module validates no id and holds no clause; a reading that cites a line off the page is refused
by the oracle, not by a check in this file.

The answers are closed shapes of line ids and enum values (baml_src/route.baml), never page text,
and a recording holds no free-text note, so it carries no template text.

PROCEDURAL — the recording and the wiring (a hash lookup, a file, an environment gate). Irreducible
to AXIOM/NEURAL: whether a file exists and which clients are reachable are facts about the process.
`RecordedProposer` mirrors `etkl/caption.RecordedCaptionReader`.

THE KEY IS THE QUESTION, every input of it: sha256 of the prefix, the client, and each input the
model was shown. A different previous page tail, or a different admitted-type list, is a different
question and misses the recording rather than replaying a stale answer.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from iladub.route.lines import Line
from iladub.route.models import MODEL_IDS, haiku_available, jev_available
from iladub.route.oracle import BoundaryAnswer, DoctypeAnswer

A = TypeVar("A")

_READINGS = pathlib.Path(__file__).resolve().parents[3] / "readings"
BOUNDARY_DIR = _READINGS / "route_boundary"
DOCTYPE_DIR = _READINGS / "route_doctype"


@dataclass(frozen=True)
class Proposed(Generic[A]):
    answer: A
    model: str  # the model id that answered: the trace's route:modelId


class Proposer(Protocol):
    client: str

    def boundary(self, listing: str, previous_tail: str) -> "Proposed[BoundaryAnswer] | None": ...

    def doctype(self, listing: str, admitted: list[str]) -> "Proposed[DoctypeAnswer] | None": ...


def listing(lines: list[Line]) -> str:
    """One `<id>\\t<text>` line per line; ids are 0-based positions in `lines`. PROCEDURAL."""
    return "\n".join(f"{i}\t{ln.text}" for i, ln in enumerate(lines))


def boundary_key(client: str, previous_tail: str, listing: str) -> str:
    return hashlib.sha256(f"route-boundary\n{client}\n{previous_tail}\n{listing}".encode("utf-8")).hexdigest()


def doctype_key(client: str, admitted: list[str], listing: str) -> str:
    names = "\n".join(sorted(admitted))
    return hashlib.sha256(f"route-doctype\n{client}\n{names}\n{listing}".encode("utf-8")).hexdigest()


def _boundary_json(p: Proposed[BoundaryAnswer]) -> dict:
    a = p.answer
    return {"verdict": a.verdict, "start_line": a.start_line,
            "evidence_lines": list(a.evidence_lines), "model": p.model}


def _boundary_from(d: dict) -> Proposed[BoundaryAnswer]:
    start = d.get("start_line")
    return Proposed(BoundaryAnswer(d["verdict"], None if start is None else int(start),
                                   tuple(int(i) for i in d.get("evidence_lines", []))), d["model"])


def _doctype_json(p: Proposed[DoctypeAnswer]) -> dict:
    a = p.answer
    return {"kind": a.kind, "party_lines": list(a.party_lines),
            "commitment_lines": list(a.commitment_lines),
            "other_evidence_lines": list(a.other_evidence_lines),
            "proposed_type": a.proposed_type, "admitted_type": a.admitted_type, "model": p.model}


def _doctype_from(d: dict) -> Proposed[DoctypeAnswer]:
    ints = lambda k: tuple(int(i) for i in d.get(k, []))
    return Proposed(DoctypeAnswer(d["kind"], ints("party_lines"), ints("commitment_lines"),
                                  ints("other_evidence_lines"), d.get("proposed_type"),
                                  d.get("admitted_type")), d["model"])


@dataclass
class RecordedProposer:
    """Replays a recorded reading; on a miss asks `live` (if any) and, only when
    `ILADUB_RECORD_READINGS=1`, writes the answer down. No recording and no live proposer: None.
    `directory` defaults to the module's directories AT CALL TIME (so a patched attribute is honoured)."""
    live: "Proposer | None"
    client: str
    directory: "pathlib.Path | None" = None

    def _replay_or_ask(self, directory, key, from_json, to_json, ask):
        path = directory / f"{key}.json"
        if path.exists():
            return from_json(json.loads(path.read_text(encoding="utf-8")))
        if self.live is None:
            return None
        got = ask()
        if got is not None and os.environ.get("ILADUB_RECORD_READINGS") == "1":
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(to_json(got), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return got

    def boundary(self, listing, previous_tail):
        directory = self.directory if self.directory is not None else BOUNDARY_DIR
        return self._replay_or_ask(directory, boundary_key(self.client, previous_tail, listing),
                                   _boundary_from, _boundary_json,
                                   lambda: self.live.boundary(listing, previous_tail))

    def doctype(self, listing, admitted):
        directory = self.directory if self.directory is not None else DOCTYPE_DIR
        return self._replay_or_ask(directory, doctype_key(self.client, admitted, listing),
                                   _doctype_from, _doctype_json,
                                   lambda: self.live.doctype(listing, admitted))


def _plain(x):
    """A BAML enum or str as its plain string value."""
    return getattr(x, "value", x)


class BamlProposer:
    """The live proposer for one client: `RouteBoundary<Name>` / `RouteDoctype<Name>` in
    baml_src/route.baml, resolved lazily by client name so importing this module never needs
    `baml_client` (it is gitignored and generated). NEURAL — the model proposes."""

    def __init__(self, client: str):
        self.client = client
        self._suffix = client.removeprefix("Router")

    def _fn(self, stem: str):
        from baml_client import sync_client
        return getattr(sync_client.b, f"{stem}{self._suffix}")

    def boundary(self, listing, previous_tail):
        r = self._fn("RouteBoundary")(listing, previous_tail)
        answer = BoundaryAnswer(_plain(r.verdict), None if r.start_line is None else int(r.start_line),
                                tuple(int(i) for i in r.evidence_lines))
        return Proposed(answer, MODEL_IDS[self.client])

    def doctype(self, listing, admitted):
        r = self._fn("RouteDoctype")(listing, list(admitted))
        ints = lambda xs: tuple(int(i) for i in xs)
        answer = DoctypeAnswer(_plain(r.kind), ints(r.party_lines), ints(r.commitment_lines),
                               ints(r.other_evidence_lines), r.proposed_type, r.admitted_type)
        return Proposed(answer, MODEL_IDS[self.client])


def default_proposers() -> list[RecordedProposer]:
    """Jev first if reachable, then Haiku always. Haiku replays recordings with no key or client;
    its live proposer is attached only under `BAML_LIVE=1`. PROCEDURAL wiring."""
    out = []
    if jev_available():
        out.append(RecordedProposer(live=BamlProposer("RouterJev"), client="RouterJev"))
    out.append(RecordedProposer(live=BamlProposer("RouterHaiku") if haiku_available() else None,
                                client="RouterHaiku"))
    return out
