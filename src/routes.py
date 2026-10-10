"""Shortest route that leaves the entrance, visits a list of products and returns to the checkout.

This is the traveling salesman problem (TSP). In the Extended Essay it was solved by hand with
the nearest-neighbor algorithm, a heuristic that does not guarantee the optimum. With 7
products it can be solved exactly: this module uses dynamic programming (Held-Karp), which
gives the same answer as trying all 5,040 possible orders, only much faster.
"""

from itertools import combinations, permutations

START = "Entrance"  # the checkout is next to the entrance


def optimal_route(dist: dict, products: list[str]) -> tuple[float, list[str]]:
    """Held-Karp: minimum length and visiting order, starting and ending at the entrance."""
    n = len(products)
    # best[(subset, last)] = (length, previous); the subset is stored as a bitmask
    best = {(1 << i, i): (dist[START][p], None) for i, p in enumerate(products)}
    for size in range(2, n + 1):
        for group in combinations(range(n), size):
            subset = sum(1 << i for i in group)
            for last in group:
                previous = subset ^ (1 << last)
                best[(subset, last)] = min(
                    (best[(previous, k)][0] + dist[products[k]][products[last]], k)
                    for k in group
                    if k != last
                )
    full = (1 << n) - 1
    length, last = min((best[(full, k)][0] + dist[products[k]][START], k) for k in range(n))
    order, subset = [], full
    while last is not None:
        order.append(products[last])
        subset, last = subset ^ (1 << last), best[(subset, last)][1]
    return round(length, 1), order[::-1]


def brute_force_route(dist: dict, products: list[str]) -> float:
    """Tries every possible order. Used to check that Held-Karp is correct."""
    def length(order):
        stops = [START, *order, START]
        return sum(dist[a][b] for a, b in zip(stops, stops[1:]))
    return round(min(length(o) for o in permutations(products)), 1)


def nearest_neighbor_route(dist: dict, products: list[str]) -> tuple[float, list[str]]:
    """The method used in the essay: always go to the closest product not yet visited."""
    pending, current, order, total = set(products), START, [], 0.0
    while pending:
        nxt = min(pending, key=lambda p: dist[current][p])
        total += dist[current][nxt]
        order.append(nxt)
        pending.remove(nxt)
        current = nxt
    total += dist[current][START]
    return round(total, 1), order


def all_groups(dist: dict, located: list[str], n: int = 7) -> list[float]:
    """Optimal route length of every possible group of n products among those on the plan.

    Answers the question: is the group of most-bought products more spread out than a
    group of 7 products picked at random?
    """
    return [optimal_route(dist, list(g))[0] for g in combinations(located, n)]


def edges_only_distances(H) -> dict:
    """Distance matrix that only allows moving along the edges drawn in graph H."""
    inf = float("inf")
    return {a: {b: (H[a][b]["weight"] if H.has_edge(a, b) else inf) for b in H.nodes} for a in H.nodes}
