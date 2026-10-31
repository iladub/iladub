"""Seeded fake values for the synthetic contract set's fill specs (spec § 4.2). Licence: Apache-2.0.

Justified PROCEDURAL (CLAUDE.md § 8): this module GENERATES fake strings; it reads no document
and answers no span/read/group question. The kind of a field is chosen from the words of its
own key (our key vocabulary), and the lengths/ranges below are generation parameters, not
reading tolerances. Every value is our own fake string — never a real company, never template
text. The generator must never be called from a reader.
"""
from __future__ import annotations

import random
import re

PORTS = ("Rotterdam", "Hamburg", "Antwerp", "Constanta", "Odessa", "Novorossiysk", "Santos",
         "Rosario", "New Orleans", "Houston", "Vancouver", "Durban", "Mombasa", "Alexandria",
         "Karachi", "Chittagong", "Singapore", "Lagos", "Genoa", "Valencia", "Piraeus",
         "Gdansk", "Klaipeda", "Tema", "Dar es Salaam")
COMMODITIES = ("milling wheat", "feed barley", "yellow maize", "soya beans", "rapeseed",
               "sunflower meal", "white rice", "sorghum", "oats", "lentils")
SUFFIXES = ("Trading", "Agri", "Commodities", "Grain", "Shipping", "Marine", "Holdings")
LEGAL = ("Ltd", "SA", "GmbH", "BV", "LLC")
_ONSET = ("b", "br", "d", "dr", "f", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z")
_VOWEL = ("a", "e", "i", "o", "u", "ai", "ou")
_CODA = ("", "n", "r", "l", "s", "x")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")
SHORT_AT = 160.0  # blanks narrower than this get compact values (a generation choice)


def _syll(rng: random.Random, n: int) -> str:
    return "".join(rng.choice(_ONSET) + rng.choice(_VOWEL) + rng.choice(_CODA) for _ in range(n)).capitalize()


def _token(rng: random.Random) -> str:
    return _syll(rng, 1) + rng.choice("xzqk") + str(rng.randint(2, 9))


def party(rng: random.Random, compact: bool) -> str:
    if compact:
        return _syll(rng, 2)
    return f"{_syll(rng, 2)} {rng.choice(SUFFIXES)} {rng.choice(LEGAL)}"


def kind_of(key: str) -> str:
    w = set(re.split(r"[.\-]", key))
    for kind, words in (
        ("signature", {"signature"}), ("day", {"day"}), ("year", {"year"}),
        ("month", {"month"}), ("date", {"date", "deadline"}),
        ("port", {"port", "place", "location", "destination", "cfr", "cif", "origin", "position",
                  "point"}),
        ("party", {"party", "buyer", "seller", "owner", "broker", "charterer", "payee",
                   "contractor", "sender", "certifier", "payer", "consigning"}),
        ("price", {"price", "rate", "amount", "cost", "brokerage", "commission", "freight"}),
        ("quantity", {"quantity", "tonnage", "total", "represented"}),
        ("percent", {"percent"}), ("days", {"days"}), ("period", {"period"}),
        ("goods", {"goods", "cargo", "commodity", "description", "specification", "guaranteed",
                   "variety", "purity"}),
        ("number", {"number"}), ("vessel", {"name", "flag", "class", "registry", "built"}),
    ):
        if w & set(words):
            if kind == "party" and "number" in w:
                continue
            return kind
    return "token"


def draw(key: str, rng: random.Random, width: float) -> str:
    kind, compact = kind_of(key), width < SHORT_AT
    if kind == "signature":
        return _syll(rng, 2) + " " + _syll(rng, 2)
    if kind == "day":
        return f"{rng.randint(1, 28)}th"
    if kind == "year":
        return str(rng.randint(1985, 2019))
    if kind == "month":
        return rng.choice(MONTHS)[:3] + "."
    if kind == "date":
        d, m = rng.randint(1, 28), rng.choice(MONTHS)
        return f"{d} {m[:3] if compact else m} 2027"
    if kind == "port":
        return rng.choice(PORTS) if not compact else _syll(rng, 1)
    if kind == "party":
        return party(rng, compact)
    if kind == "price":
        v = f"{rng.randint(2, 480)}.{rng.randint(0, 99):02d}"
        return v if compact else rng.choice(("USD ", "EUR ")) + v + " per tonne"
    if kind == "quantity":
        v = f"{rng.randint(5, 60) * 500}"
        return v if compact else v + " metric tonnes"
    if kind == "percent":
        return f"{rng.randint(2, 9) * 10} pct"
    if kind == "days":
        return f"{rng.randint(2, 9)} days"
    if kind == "period":
        m = rng.choice(MONTHS)
        return f"{m[:3]} 2027" if compact else f"{m} 2027 seller's option"
    if kind == "goods":
        return rng.choice(COMMODITIES) if not compact else _token(rng)
    if kind == "number":
        return f"SYN-{rng.randint(1000, 9999)}"
    if kind == "vessel":
        return f"MV {_syll(rng, 2)}" if not compact else _syll(rng, 1)
    return _token(rng)
