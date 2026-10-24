// "Which of these lines are this table's own caption: its title, its unit line?" — R336, spec
// 2026-10-24 § 3.3.
//
// After `ReadBoxhead` is disposed, some header-block lines hold only words it filed as
// `other_words` — not column headers. Some of those are the table's own title or unit line, and
// some are the page's (a running head, a section heading, a note). Which is which is a reading
// judgement a person makes at a glance; it is never line position (CLAUDE.md § 8, and the
// 2026-09-17 ruling forbids "the lines above the boxhead" as a heuristic). So it is asked.
//
// A SEPARATE WORKER, not a wider `ReadBoxhead`: a boxhead recording is keyed on the question's
// column count and listing, not on its prompt or schema, so a wider question would replay every
// recorded boxhead answer as an answer to a question no compile asks any more.
//
// THE ANSWER IS INDICES, NEVER TEXT: `caption_lines` holds candidate numbers from the listing
// supplied, so it cannot carry a value that is on the page. `caption.dispose_captions` checks every
// index arithmetically: each is a listed candidate, the set is non-empty, contiguous in page order,
// and ends on the line directly above the topmost surviving column label. Anything else is NO
// CLAIM.
//
// THE CLIENT is the small one, `Claude` (Haiku 4.5): the question is one a reader answers at a
// glance — the `header_lines.baml` precedent and its reasoning. If its live answers are measured
// wrong, that is a finding to record, not a licence to switch the model before it is measured.

class CaptionLines {
  caption_lines int[] @description("the C-numbers of the listed lines that are this table's own caption (its title, its unit line); empty if none is")
  refuses bool @description("true if none of the listed lines is this table's own caption, or you cannot tell")
  note string @description("one short sentence on how you read it; NEVER any text or value from the page")
}

function ReadCaption(page: image, ncols: int, listing: string) -> CaptionLines {
  client Claude
  prompt #"
    {{ _.role("user") }}
    {{ page }}

    The image shows the top of one table: the lines above its column headers, its column
    headers, then its first rows of data. The table has {{ ncols }} columns.

    Below are some of the lines above the column headers, top to bottom, numbered from C0. Each
    word has its index and, after the @, its left and right edge on the page in points:

    {{ listing }}

    READ IT AS A PERSON READS A PAGE. Which of these lines are THIS TABLE'S OWN CAPTION — its
    title, or the line that states its unit (for example "in millions")?

    - A line that belongs to the page rather than to this table — a running head, a section
      heading, a page number, a note about something else — is not this table's caption.
    - If none of the lines is this table's caption, or you cannot tell, set refuses to true and
      leave caption_lines empty. Refusing is a correct answer.

    Answer with the C-numbers only. Never write any text, number or value that appears on the
    page — not in note, not anywhere.
    {{ ctx.output_format }}
  "#
}
