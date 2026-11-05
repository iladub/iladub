// The document router's two questions (spec 2026-11-02 document-router § 4): Q-boundary and
// Q-doctype, each a reading a person answers at a glance.
//
// THE ANSWER IS LINE NUMBERS, NEVER TEXT: every `int` below is a number from the listing supplied,
// so no field can carry a value that is on the page (CLAUDE.md § 8). The oracles
// (vocab/queries/route-boundary.rq, route-checklist.rq) dispose each id; nothing here is trusted.
// There is no free-text note: a recording must hold no template text.
//
// One function per client; only `RouterHaiku` exists (task-1 report: no BAML client reaches Jev).

enum PageVerdict {
  STARTS
  CONTINUES
  REFUSES
}

class BoundaryReading {
  verdict PageVerdict
  start_line int? @description("the number of the line where the new document starts; null unless verdict is STARTS")
  evidence_lines int[] @description("the numbers of the listed lines that show the new document starts there")
}

enum DocKind {
  CONTRACT
  OTHER
  REFUSES
}

class DoctypeReading {
  kind DocKind
  party_lines int[] @description("numbers of the listed lines that name a party to the agreement")
  commitment_lines int[] @description("numbers of the listed lines that state a commitment one party makes")
  other_evidence_lines int[] @description("when kind is OTHER: numbers of the listed lines that show what kind of document this is")
  proposed_type string? @description("when kind is OTHER: a short name for the kind of document, if you can give one")
  admitted_type string? @description("when kind is OTHER and the document is one of the admitted types: that type's name, exactly as given")
}

function RouteBoundaryHaiku(listing: string, previous_tail: string) -> BoundaryReading {
  client RouterHaiku
  prompt #"
    {{ _.role("user") }}
    Below is one page of a PDF, as numbered lines (number, a tab, the line's text). Above it, for
    context only, are the last lines of the previous page; those have no numbers and cannot be cited.

    PREVIOUS PAGE, LAST LINES:
    {{ previous_tail }}

    THIS PAGE:
    {{ listing }}

    Read it as a person turning pages would. Does a NEW DOCUMENT start on this page, and at which
    line? A new document is a different document beginning, not a new section of the same one.

    - STARTS: a new document begins on this page. Set start_line to the number of its first line and
      list in evidence_lines the numbers of the lines that show it (a title, a heading, a first page).
    - CONTINUES: this page carries on the document of the previous page.
    - REFUSES: you cannot tell. Refusing is a correct answer.

    Answer with line numbers only. Never copy text from the page.

    {{ ctx.output_format }}
  "#
}

function RouteDoctypeHaiku(listing: string, admitted_types: string[]) -> DoctypeReading {
  client RouterHaiku
  prompt #"
    {{ _.role("user") }}
    Below is one document, as numbered lines (number, a tab, the line's text).

    {{ listing }}

    What kind of document is this? Is it a contract: an agreement with at least two named parties
    and at least one commitment that a party makes?

    - CONTRACT: list in party_lines the numbers of lines naming the parties (at least two different
      parties) and in commitment_lines the numbers of lines stating a commitment (at least one).
    - OTHER: it is not a contract. Cite in other_evidence_lines the lines that show what kind of
      document it is (for example a heading naming rules or a notice). If it is one of these admitted
      types, give that name exactly in admitted_type: {{ admitted_types }}. Otherwise you may give a
      short name in proposed_type. If you cannot cite lines that show what it is, refuse.
    - REFUSES: you cannot tell, or the evidence is not there. Refusing is a correct answer. A missing
      party or commitment is a reason to refuse, never a reason to say OTHER.

    Answer with line numbers and names only. Never copy text from the page.

    {{ ctx.output_format }}
  "#
}
