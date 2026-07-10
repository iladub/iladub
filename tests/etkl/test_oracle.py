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
