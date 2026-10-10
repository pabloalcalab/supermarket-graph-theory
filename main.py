"""Runs the full analysis and writes the figures to figures/.

Usage:  python main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import numpy as np

from figures import graphs_figure, groups_figure, plan_figure, routes_figure
from floor_plan import build_floor_plan, essay_subgraphs, shortest_distances
from routes import all_groups, edges_only_distances, nearest_neighbor_route, optimal_route
from survey import EXCLUDED, load_survey, monthly_purchases, pick_groups


def main():
    # 1. Survey: purchases per month for each product
    score = monthly_purchases(load_survey())
    most, least = pick_groups(score)
    print("Purchases per month from the survey (100 respondents, 29 products):")
    for product, value in score.items():
        tag = " <- most-bought" if product in most else " <- least-bought" if product in least else ""
        note = f"  (excluded: {EXCLUDED[product]})" if product in EXCLUDED else ""
        print(f"  {product:24s} {value:5.2f}{tag}{note}")

    # 2. Floor plan and shortest walking distances between all measured products
    G, pos = build_floor_plan()
    located = most + least
    dist = shortest_distances(G, ["Entrance", *located])

    # 3. Exact shortest route for each group. It is computed with free movement and, separately,
    #    using only the edges drawn in the essay. If both match, the essay's simplification was valid.
    H = essay_subgraphs(dist)
    route_most, route_least = optimal_route(dist, most), optimal_route(dist, least)
    route_most_h = optimal_route(edges_only_distances(H["most"]), most)
    route_least_h = optimal_route(edges_only_distances(H["least"]), least)
    assert route_most_h[0] == route_most[0] and route_least_h[0] == route_least[0], \
        "the essay's simplified graphs lose the optimum"
    route_most, route_least = route_most_h, route_least_h  # same length; this order follows the drawn edges
    increase = (route_most[0] / route_least[0] - 1) * 100
    print(f"\nShortest route, 7 most-bought:  {route_most[0]:.1f} m  {' > '.join(route_most[1])}")
    print(f"Shortest route, 7 least-bought: {route_least[0]:.1f} m  {' > '.join(route_least[1])}")
    print(f"The most-bought route is {increase:.1f}% longer.")
    for name, group in [("most-bought", most), ("least-bought", least)]:
        print(f"  Nearest neighbor ({name}): {nearest_neighbor_route(dist, group)[0]:.1f} m")
    print("  Using only the edges drawn in the essay does not change the optimum.")

    print("\nEssay distances that do not match the floor plan:")
    for group in ("least", "most"):
        for a, b, d in H[group].edges(data=True):
            if abs(d["weight"] - d["essay"]) > 0.05:
                print(f"  {a} - {b}: essay {d['essay']:.1f} m, floor plan {d['weight']:.1f} m")

    # 4. Could it be chance? Shortest route for every possible group of 7
    lengths = np.array(all_groups(dist, located))
    as_long = int((lengths >= route_most[0]).sum())
    as_short = int((lengths <= route_least[0]).sum())
    print(f"\nOf the {len(lengths)} possible groups of 7 among the 14 measured products:")
    print(f"  {as_long} have a route as long as the most-bought or longer "
          f"({100 * as_long / len(lengths):.1f}%). Longest possible: {lengths.max():.1f} m.")
    print(f"  {as_short} have a route as short as the least-bought or shorter "
          f"({100 * as_short / len(lengths):.1f}%). Shortest possible: {lengths.min():.1f} m.")
    print(f"  Median of all groups: {np.median(lengths):.1f} m.")

    # 5. Figures
    plan_figure(G, pos, most, least)
    routes_figure(G, pos, most, least, route_most, route_least)
    graphs_figure(H["most"], H["least"], route_most, route_least)
    groups_figure(lengths, route_most[0], route_least[0])
    print("\nFigures saved to figures/")


if __name__ == "__main__":
    main()
