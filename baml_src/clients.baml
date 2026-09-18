client<llm> Claude {
  provider anthropic
  options {
    model "claude-haiku-4-5-20251001"
    api_key env.ANTHROPIC_API_KEY
    max_tokens 2000
  }
}

// R213's region reader. It differs from the shared `Claude` client in TWO ways, each measured on
// graincorp-capacity band 3 (27 x 16, 406 populated cells, 110 of them unshown), never chosen.
//
// (1) THE TOKEN BUDGET. The reader answers with one object per empty grid position — 110 of them
//     here, more on a denser region — and 2000 tokens TRUNCATES that mid-array: the same crop
//     returned a complete answer on one run and an unparseable one on the next (the successful
//     run used 3198 output tokens). A budget that sometimes fits is a defect, not a tolerance.
//
// (2) THE MODEL, and this is the load-bearing one. O2 was run as a regression against this ask
//     (spec § 8.8: never to re-establish the 110, only to check the shipped ask still returns it):
//
//       claude-haiku-4-5   |A| = 148   68 of 110 found   79 FALSE POSITIVES on cells with ink
//       claude-sonnet-5    |A| = 110  109 of 110 found    0 false positives
//
//     Haiku's own note gives it away — it reported "cells with dark backgrounds ... that show no
//     visible text", i.e. it classified by BACKGROUND rather than reading the place. That is the
//     refuted colour instrument re-entering through the worker, which is RF7's failure mode
//     exactly. Sonnet reproduces the blind runs' disposal through the shipped prompt, missing one
//     cell (22, 2) and inventing none, and independently returns (1, 6) — the one non-degenerate
//     null-control position. So the ASK is right and the small model is not able to answer it;
//     do not downgrade this client to save cost without re-running O2.
client<llm> ClaudeLongAnswer {
  provider anthropic
  options {
    model "claude-sonnet-5"
    api_key env.ANTHROPIC_API_KEY
    max_tokens 16000
  }
}
