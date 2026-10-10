"""Builds the supermarket floor plan as a graph of aisles, with distances in meters.

Every aisle crossing is a node: ("C", 5) means column C, row 5. Every product is one more
node, inserted in the aisle segment where it was measured. Edges are aisle segments and
their weight is their length in meters.
"""

from pathlib import Path

import networkx as nx
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
COLUMNS = ["L", "C", "R"]


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name, comment="#", dtype={"from": str, "to": str, "row_or_column": str})


def build_floor_plan() -> tuple[nx.Graph, dict]:
    """Returns the floor-plan graph and the (x, y) position in meters of each node, for drawing."""
    segments = _read("floor_plan_segments.csv")
    blocked = _read("floor_plan_blocked.csv")
    products = _read("product_locations.csv")

    vertical = segments[segments.type == "vertical"]
    widths = segments[segments.type == "horizontal"].set_index("from")["meters"]
    rows = list(range(1, int(vertical["to"].astype(int).max()) + 1))
    cut = {(r.column, int(r[2]), int(r[3])) for r in blocked.itertuples()}

    # Positions: x grows to the right, y grows from the back of the store towards the entrance.
    x = {"L": 0.0, "C": widths["L"], "R": widths["L"] + widths["C"]}
    y = {1: 0.0}
    for s in vertical.itertuples():
        y[int(s[3])] = y[int(s[2])] + s.meters

    G = nx.Graph()
    pos = {(col, r): (x[col], y[r]) for col in COLUMNS for r in rows}
    for r in rows:  # horizontal aisles
        G.add_edge(("L", r), ("C", r), weight=widths["L"])
        G.add_edge(("C", r), ("R", r), weight=widths["C"])
    for s in vertical.itertuples():  # vertical aisles
        a, b = int(s[2]), int(s[3])
        for col in COLUMNS:
            if (col, a, b) not in cut:
                G.add_edge((col, a), (col, b), weight=s.meters)

    entrances = []
    for p in products.itertuples():
        start, end = p[4], p[5]
        if p.type == "horizontal":
            row = int(p.row_or_column)
            _insert(G, pos, p.product, (start, row), (end, row), p.meters)
        elif p.type == "vertical":
            col = p.row_or_column
            _insert(G, pos, p.product, (col, int(start)), (col, int(end)), p.meters)
        elif p.type == "crossing":
            node = (p.row_or_column, int(start))
            G.add_edge(p.product, node, weight=0.0)
            pos[p.product] = pos[node]
        elif p.type == "entrance":  # it can open onto several aisles
            node = (p.row_or_column, int(start))
            G.add_edge(p.product, node, weight=p.meters)
            entrances.append((node, p.meters))
    if entrances:  # drawn centered below the aisles it opens onto
        x_ent = sum(pos[n][0] for n, _ in entrances) / len(entrances)
        y_ent = max(pos[n][1] + m for n, m in entrances)
        pos["Entrance"] = (x_ent, y_ent)
    return G, pos


def _insert(G, pos, name, a, b, meters_from_a):
    """Splits segment a–b in two and places the product `meters_from_a` away from a."""
    length = G[a][b]["weight"]
    if not 0 <= meters_from_a <= length:
        raise ValueError(f"{name}: {meters_from_a} m does not fit in a {length} m segment")
    G.remove_edge(a, b)
    G.add_edge(a, name, weight=meters_from_a)
    G.add_edge(name, b, weight=round(length - meters_from_a, 2))
    t = meters_from_a / length
    pos[name] = (pos[a][0] + t * (pos[b][0] - pos[a][0]), pos[a][1] + t * (pos[b][1] - pos[a][1]))


def shortest_distances(G: nx.Graph, places: list[str]) -> dict:
    """Shortest walking distance between every pair of places (Dijkstra's algorithm)."""
    return {a: nx.single_source_dijkstra_path_length(G, a, weight="weight") for a in places}


def path(G: nx.Graph, a, b) -> list:
    """Nodes along the shortest path from a to b."""
    return nx.dijkstra_path(G, a, b, weight="weight")


def essay_subgraphs(dist: dict) -> dict:
    """The two subgraphs drawn in the Extended Essay, with every edge recomputed on the plan.

    Each edge keeps the floor-plan distance (`weight`) and the one computed by hand in the
    essay (`essay`), so both can be compared.
    """
    edges = _read("essay_graphs.csv")
    graphs = {}
    for group, rows in edges.groupby("group"):
        H = nx.Graph()
        for r in rows.itertuples():
            H.add_edge(r[2], r[3], weight=round(dist[r[2]][r[3]], 1), essay=r.meters_essay)
        graphs[group] = H
    return graphs
