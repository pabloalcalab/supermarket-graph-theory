"""Checks that the code reproduces the Extended Essay and that the exact algorithm is correct.

Usage:  python -m pytest
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from floor_plan import build_floor_plan, essay_subgraphs, shortest_distances
from routes import brute_force_route, nearest_neighbor_route, optimal_route
from survey import load_survey, monthly_purchases, pick_groups

# Totals computed by hand in the essay (purchases per month).
ESSAY_TOTALS = {
    "Milk": 2.54, "Fruit": 3.71, "Eggs": 2.69, "Fish counter": 2.69, "Butcher counter": 3.15,
    "Yogurt": 2.71, "Water": 1.19, "Toilet paper": 1.32, "Shampoo and shower gel": 0.71,
    "Sugar": 0.48, "Salt": 0.47, "Cookies": 1.45, "Coffee": 1.19, "Ice cream": 0.67,
    "Pickles": 0.83, "Olive oil": 0.80, "Legumes": 1.45, "Dry pasta": 1.46, "Wine": 0.75,
    "Cocoa powder": 0.70, "Frozen pizza": 0.98, "Cured ham": 1.72, "Cheese": 2.42,
    "Packaged chicken": 1.95, "Fuet sausage": 1.24, "Sliced bread": 1.76,
    "Mayo and ketchup": 0.53, "Organic food": 0.62,
}
# Cereal is left out: in the original spreadsheet "every 4 months" was typed as 0.0162 instead
# of 0.162 (the survey chart shows 16.2%), so its total moves from 0.87 to 0.90.

# Essay distances that do not match the floor plan (see README).
MISMATCHES = {
    frozenset({"Entrance", "Milk"}),
    frozenset({"Entrance", "Butcher counter"}),
    frozenset({"Ice cream", "Organic food"}),
    frozenset({"Yogurt", "Milk"}),
}


@pytest.fixture(scope="module")
def data():
    score = monthly_purchases(load_survey())
    most, least = pick_groups(score)
    G, _ = build_floor_plan()
    dist = shortest_distances(G, ["Entrance", *most, *least])
    return score, most, least, dist


def test_scores_match_the_essay(data):
    score = data[0]
    for product, total in ESSAY_TOTALS.items():
        assert score[product] == pytest.approx(total, abs=0.006), product


def test_groups_match_the_essay(data):
    _, most, least, _ = data
    assert set(most) == {"Fruit", "Butcher counter", "Yogurt", "Eggs", "Fish counter", "Milk", "Cheese"}
    assert set(least) == {"Salt", "Mayo and ketchup", "Organic food", "Ice cream", "Cocoa powder",
                          "Shampoo and shower gel", "Wine"}


def test_floor_plan_reproduces_the_measured_distances(data):
    dist = data[3]
    for H in essay_subgraphs(dist).values():
        for a, b, d in H.edges(data=True):
            if frozenset({a, b}) in MISMATCHES:
                assert d["weight"] != pytest.approx(d["essay"], abs=0.05)
            else:
                assert d["weight"] == pytest.approx(d["essay"], abs=0.05), (a, b)


@pytest.mark.parametrize("group", ["most", "least"])
def test_held_karp_matches_brute_force(data, group):
    _, most, least, dist = data
    products = most if group == "most" else least
    assert optimal_route(dist, products)[0] == brute_force_route(dist, products)


def test_nearest_neighbor_never_beats_the_optimum(data):
    _, most, least, dist = data
    for products in (most, least):
        assert nearest_neighbor_route(dist, products)[0] >= optimal_route(dist, products)[0]
