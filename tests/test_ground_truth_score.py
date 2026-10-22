from iladub.truth import normalise


def test_normalise_is_exactly_the_three_declared_rules():
    assert normalise("  Week ended\n  Jan 1, 2025 ") == "Week ended Jan 1, 2025"
    assert normalise("-    20,940") == "-20,940"
    assert normalise("+ 62") == "+62"
    assert normalise("a - b") == "a - b"          # a sign is stripped only when leading and before a digit
    assert normalise("Ｒeserve") == "Reserve"      # NFKC
    assert normalise("Reserve") != normalise("reserve")  # no case folding
