// "What is the role of this number, marked on the page with a red box?" — R261 loop (b), P4/P4b
// (`docs/superpowers/2026-10-02-r261-grand-total-role-probe.md`).
//
// A grand total sits beneath several per-table totals with identical typography (same column, same
// rules above/below, same font) — arithmetic alone cannot tell "sums the operand totals" from
// "is one more table total" or "is a value inside a table." That is a reading judgement a person
// makes at a glance, so it is asked of a reader (CLAUDE.md § 8, "One geometric attempt, then
// NEURAL"), disposed against the page's own bound totals (the conjunction that binds a grand total
// is arithmetic AND this reading — spec § 3, mirroring `printed_total.baml`'s table-level
// conjunction).
//
// THE ANSWER IS A CLOSED ENUM, never text: `table_total | total_of_totals | other | cannot_tell`,
// with NO note field — the same never-quote discipline as `printed_total.baml` (P1's note leaked
// page values).
//
// THE WORDING is P4/P4b's, `scripts/r261_grand_total_role_probe.py` `PROMPT`, carried verbatim. Two
// lines differ: `{value}` (Python `str.format`) becomes `{{ value }}`, and the probe's literal
// `Reply with JSON only: {"answer": ...}` is replaced by BAML's `ctx.output_format`, which renders
// the same closed one-field shape. P4b (the derived D7-union crop) held the decision rule fixed
// before the run: `1,951,264` -> `total_of_totals` x3, no null -> `total_of_totals` (evidence § 3-4).
// Its one miss — `22,858`, an in-table cell, read as `table_total` on the derived crop — does not
// bind anything (`table_total` binds nothing in the conjunction) and is raised as [[R287]], not
// fixed by rewording here.
//
// THE CLIENT is the small one, `Claude` (Haiku 4.5) — the model P4/P4b measured.

enum TotalRoleAnswer {
  TABLE_TOTAL @alias("table_total")
  TOTAL_OF_TOTALS @alias("total_of_totals")
  OTHER @alias("other")
  CANNOT_TELL @alias("cannot_tell")
}

class TotalRoleVerdict {
  answer TotalRoleAnswer
}

function AskTotalRole(page: image, value: string) -> TotalRoleVerdict {
  client Claude
  prompt #"
    {{ _.role("user") }}
    {{ page }}

    The image shows part of a page. One number is marked with a red box: {{ value }}.

    READ IT AS A PERSON READS THE PAGE. What is the number in the red box?

    Answer exactly one of:
    - table_total: the total of the one table directly above it.
    - total_of_totals: a total that sums the totals of several tables.
    - other: something else (a value inside a table, a note, a label, ...).
    - cannot_tell: the image does not let a reader decide.

    {{ ctx.output_format }}
  "#
}
