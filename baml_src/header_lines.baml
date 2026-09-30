// "How many leading lines of this drawn box are column headers?" — box-split spec § 10.3.3.
//
// A box the author drew is compiled positionally today: row 0 is its header line. Some boxes have
// no boxhead at all — their first line is already data — and then row 0 is read as labels that
// label nothing. Measured in the spec (§ 10.1): whether row 0 is header or data is UNDERDETERMINED
// by style, so it is a reading judgement a person makes at a glance, and it is asked of a reader
// (CLAUDE.md § 8, "One geometric attempt, then NEURAL").
//
// THE ANSWER IS A CLOSED INT, never text: `header_lines` is a count in 0..(number of listed
// lines), and `iladub.etkl.headerlines.ask_header_lines` refuses any answer outside that range
// (the closed-answer check, PR #256). It is then disposed ONE WAY by `row-zero-differs.rq`: a style
// or datatype witness that row 0 differs from its body refutes a `0`. The note never carries page
// text (the `ReadBoxhead` rule).
//
// THE CLIENT is the small one, `Claude` (Haiku 4.5): the question is one a reader answers at a
// glance. `ClaudeLongAnswer`'s comment (clients.baml) records Haiku measured WRONG on a region
// question that turned on colour; that is a precedent for a finding if this worker's live answer
// is wrong, not a licence to switch the model before it is measured (plan Task 3d.5).

class HeaderLines {
  header_lines int @description("how many of the listed lines, counted from the top, are column headers; 0 if the first line is already data")
  note string @description("one short sentence on how you read it; NEVER any text or value from the page")
}

function CountHeaderLines(page: image, ncols: int, listing: string) -> HeaderLines {
  client Claude
  prompt #"
    {{ _.role("user") }}
    {{ page }}

    The image shows one table the author drew as a box. It has {{ ncols }} columns. Below is
    every line of it, top to bottom, numbered from L0, with its cells in column order separated
    by " | " (an empty cell shows as nothing between two separators):

    {{ listing }}

    READ IT AS A PERSON READS A TABLE. How many of its leading lines are column headers — lines
    that name what the columns hold, rather than being rows of the table's data?

    - If L0 already reads as data — one more row like the rows beneath it — the answer is 0.
      A table can have no header line at all; 0 is a correct answer.
    - If the first line names the columns and the rest are data, the answer is 1.
    - If the header wraps or stacks over several lines, count every one of them.

    Answer with the count only. Never write any text, number or value that appears in the table —
    not in note, not anywhere.
    {{ ctx.output_format }}
  "#
}
