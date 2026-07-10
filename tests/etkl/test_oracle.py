from iladub.etkl.recipe import UnpivotOp, StripAggregationOp, Recipe
from iladub.etkl.oracle import replay, round_trip

BASE = [{"Year": "2020", "Region": "North", "__measure__": 10.0},
        {"Year": "2020", "Region": "South", "__measure__": 20.0},
        {"Year": "2021", "Region": "North", "__measure__": 11.0},
        {"Year": "2021", "Region": "South", "__measure__": 21.0}]

ORIGINAL = {("2020", "North"): "10", ("2020", "South"): "20",
            ("2021", "North"): "11", ("2021", "South"): "21",
            ("2020", "Year"): "2020", ("2021", "Year"): "2021"}


def test_replay_unpivot_regenerates_grid():
    grid = replay(BASE, Recipe((UnpivotOp("Region", "Year"),)))
    assert grid[("2020", "North")] == "10"
    assert grid[("2021", "South")] == "21"
    assert grid[("2020", "Year")] == "2020"


def test_correct_recipe_round_trips():
    v = round_trip(ORIGINAL, BASE, Recipe((UnpivotOp("Region", "Year"),)))
    assert v.ok and v.residue == ()


def test_corrupted_base_is_rejected():
    bad = [dict(x) for x in BASE]; bad[0]["__measure__"] = 999.0
    v = round_trip(ORIGINAL, bad, Recipe((UnpivotOp("Region", "Year"),)))
    assert not v.ok and v.residue                          # mismatch surfaces as residue


def test_strip_replay_readds_total_column():
    # base with a strip op: forward replay must re-add the Total column = sum(North,South)
    original = dict(ORIGINAL)
    original[("2020", "Total")] = "30"; original[("2021", "Total")] = "32"
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    v = round_trip(original, BASE, recipe)
    assert v.ok, v.residue


def test_row_axis_strip_excludes_numeric_stub_column():
    """Regression: row-axis strip must NOT write a spurious aggregate into the stub column.

    A numeric stub (Year=2020/2021) is echo'd into the grid by unpivot. The row-axis
    strip sums member_labels ("2020","2021") across every column — before the fix it
    finds the stub column "Year" numeric and writes ("Total","Year")="4041", which is
    an extra cell that was never in the original grid.  round_trip must return ok=True.
    """
    base = [{"Year": "2020", "Region": "North", "__measure__": 10.0},
            {"Year": "2020", "Region": "South", "__measure__": 20.0},
            {"Year": "2021", "Region": "North", "__measure__": 11.0},
            {"Year": "2021", "Region": "South", "__measure__": 21.0}]
    # original: measure cells + stub-echo cells + row-axis totals per region.
    # ("Total","Year") must NOT be in original — a total row has no year stub value.
    original = {
        ("2020", "North"): "10", ("2020", "South"): "20",
        ("2021", "North"): "11", ("2021", "South"): "21",
        ("2020", "Year"): "2020", ("2021", "Year"): "2021",
        ("Total", "North"): "21",   # 10 + 11
        ("Total", "South"): "41",   # 20 + 21
    }
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("row", "sum", ("2020", "2021"), "Total")))
    v = round_trip(original, base, recipe)
    assert v.ok, v.residue
