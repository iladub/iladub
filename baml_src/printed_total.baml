// "Is this number, printed beneath a table, the total of that table?" — R261 spec § 3.2.
//
// A lone number printed beneath a table may be that table's total, or a note, a page number, a
// value of the next table. Exact arithmetic finds the numbers that COULD be a column's total; it
// cannot tell a total from a coincidence (who-wfa's `21` sums an ordinal column and is not a
// total). That is a reading judgement a person makes at a glance, so it is asked of a reader
// (CLAUDE.md § 8, "One geometric attempt, then NEURAL"), and only on an arithmetic match.
//
// THE ANSWER IS A CLOSED ENUM, never text: `yes | no | cannot_tell`, with NO note field. P1
// measured the note leaking page values (the R261 spec-handoff Addendum 2, finding 1), and a
// closed answer cannot hold a free note to the never-quote rule. `iladub.etkl.printedtotal`
// binds only on `yes` AND the exact sum (spec § 2.4); every other answer binds nothing.
//
// ONE QUESTION, TABLE LEVEL ONLY. The total-of-totals wording was probed (P3) and REFUTED
// (`docs/superpowers/2026-10-01-r261-totals-family-evidence.md` § 6.4), so no second function
// exists here (controller ruling R4).
//
// THE WORDING is P1's, measured on the D7 crop (evidence § 6.5: 4/4 true totals `yes` x3, the
// false `21` `no` x3, no `yes` in 21 null asks; n = 5 is the corpus, not a sample). One line
// differs: the probe's literal `Reply with JSON only: {"answer": ...}` is replaced by BAML's
// `ctx.output_format`, which renders the same closed one-field shape. Task 5's recorded readings
// are taken through THIS function, so they are the evidence for it.
//
// THE CLIENT is the small one, `Claude` (Haiku 4.5) — the model P1 measured.

enum PrintedTotalAnswer {
  YES @alias("yes")
  NO @alias("no")
  CANNOT_TELL @alias("cannot_tell")
}

class PrintedTotalVerdict {
  answer PrintedTotalAnswer
}

function AskPrintedTotal(page: image, value: string) -> PrintedTotalVerdict {
  client Claude
  prompt #"
    {{ _.role("user") }}
    {{ page }}

    The image shows the bottom of a table and what is printed directly beneath it.

    Beneath the table, the number {{ value }} is printed.

    READ IT AS A PERSON READS A TABLE. Is {{ value }} the total of the table above it — the sum of
    the values in one of its columns, printed as that column's total?

    Answer exactly one of:
    - yes: it is the table's total.
    - no: it is something else (a note, a page number, a label, a value of another table, ...).
    - cannot_tell: the image does not let a reader decide.

    {{ ctx.output_format }}
  "#
}
