"""Project figures: scale floor plan, routes, shortest-distance graphs and the comparison with chance."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from floor_plan import path

FIG = Path(__file__).resolve().parent.parent / "figures"
MOST = "#eb6834"     # most-bought
LEAST = "#2a78d6"    # least-bought
AISLE = "#d9d8d2"
INK = "#2b2b28"
INK_2 = "#6b6a63"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": INK_2,
    "text.color": INK,
    "figure.facecolor": "white",
})


def _base_plan(ax, G, pos):
    """Draws the aisles to scale (in meters) with the entrance at the bottom."""
    for a, b in G.edges():
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.plot([x1, x2], [y1, y2], color=AISLE, lw=6, solid_capstyle="round", zorder=1)
    ax.set_aspect("equal")
    ax.invert_yaxis()  # back of the store at the top, entrance at the bottom
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.plot([4.4, 14.4], [64.5, 64.5], color=INK_2, lw=1.5)
    ax.text(9.4, 65.6, "10 m", ha="center", va="top", color=INK_2, fontsize=8)


# Offsets for some labels so they do not overlap (points, alignment).
LABELS = {
    "Butcher counter": ((0, 8), "center", "bottom"),
    "Mayo and ketchup": ((0, 8), "center", "bottom"),
    "Yogurt": ((0, 8), "center", "bottom"),
    "Fruit": ((0, 8), "center", "bottom"),
    "Milk": ((0, 8), "center", "bottom"),
    "Shampoo and shower gel": ((0, -8), "center", "top"),
}


def _products(ax, pos, group, color, marker, labels=True, size=70):
    for p in group:
        x, y = pos[p]
        ax.scatter(x, y, s=size, color=color, marker=marker, edgecolor="white", linewidth=1.5, zorder=4)
        if labels:
            off, ha, va = LABELS.get(p, ((9, 0), "left", "center"))
            if size > 100:
                off = (off[0] * 1.4, off[1] * 1.4)
            ax.annotate(p, (x, y), xytext=off, textcoords="offset points", ha=ha, va=va,
                        fontsize=8, color=INK, zorder=5,
                        bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))


def _entrance(ax, pos):
    x, y = pos["Entrance"]
    ax.scatter(x, y, s=110, color=INK, marker="s", zorder=4)
    ax.annotate("Entrance and checkout", (x, y), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=8, fontweight="bold")


def plan_figure(G, pos, most, least):
    fig, ax = plt.subplots(figsize=(6.4, 9))
    _base_plan(ax, G, pos)
    _products(ax, pos, most, MOST, "o")
    _products(ax, pos, least, LEAST, "D")
    _entrance(ax, pos)
    ax.scatter([], [], color=MOST, marker="o", label="7 most-bought")
    ax.scatter([], [], color=LEAST, marker="D", label="7 least-bought")
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.01), frameon=False, ncol=2)
    ax.set_title("Supermarket floor plan, rebuilt to scale\n(aisles laser-measured, in meters)",
                 loc="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG / "floor_plan.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def _draw_route(ax, G, pos, order, color):
    stops = ["Entrance", *order, "Entrance"]
    for a, b in zip(stops, stops[1:]):
        segment = path(G, a, b)
        xs, ys = zip(*(pos[n] for n in segment))
        ax.plot(xs, ys, color=color, lw=2, alpha=0.85, zorder=3, solid_capstyle="round")


def _number_stops(ax, pos, order):
    """Writes the visiting order inside each marker."""
    for i, p in enumerate(order, 1):
        x, y = pos[p]
        ax.text(x, y, str(i), ha="center", va="center", fontsize=7, color="white",
                fontweight="bold", zorder=6)


def routes_figure(G, pos, most, least, route_most, route_least):
    fig, axes = plt.subplots(1, 2, figsize=(11, 9))
    for ax, group, (length, order), color, marker, title in [
        (axes[0], most, route_most, MOST, "o", "7 most-bought"),
        (axes[1], least, route_least, LEAST, "D", "7 least-bought"),
    ]:
        _base_plan(ax, G, pos)
        _draw_route(ax, G, pos, order, color)
        _products(ax, pos, group, color, marker, size=190)
        _number_stops(ax, pos, order)
        _entrance(ax, pos)
        ax.set_title(f"{title}: {length:.1f} m", loc="left", fontsize=11, fontweight="bold")
    fig.suptitle("Exact shortest route from the entrance (numbers show the visiting order)",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "routes.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# Schematic node layout, based on the graphs drawn in the Extended Essay (Figures 4 and 7).
LAYOUT = {
    "most": {"Butcher counter": (3, 0), "Cheese": (5.2, 0.4), "Fruit": (3, 1.6), "Milk": (3, 3.2),
             "Eggs": (5.2, 3.8), "Yogurt": (2.6, 5.4), "Fish counter": (5.2, 8.2), "Entrance": (0, 10.5)},
    "least": {"Cocoa powder": (0, 0), "Organic food": (2.4, 0), "Salt": (2.4, 2), "Mayo and ketchup": (4.4, 2.6),
              "Ice cream": (6.6, 4.4), "Shampoo and shower gel": (4.6, 7.4), "Wine": (0, 3.4), "Entrance": (0, 10)},
}


def graphs_figure(H_most, H_least, route_most, route_least):
    """The two subgraphs from the essay, with distances recomputed on the floor plan."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 7.5))
    for ax, H, key, (length, order), color, title in [
        (axes[0], H_most, "most", route_most, MOST, "7 most-bought"),
        (axes[1], H_least, "least", route_least, LEAST, "7 least-bought"),
    ]:
        p = LAYOUT[key]
        cycle = ["Entrance", *order, "Entrance"]
        on_route = {frozenset(e) for e in zip(cycle, cycle[1:])}
        other = [e for e in H.edges if frozenset(e) not in on_route]
        route = [e for e in H.edges if frozenset(e) in on_route]
        nx.draw_networkx_edges(H, p, edgelist=other, ax=ax, edge_color=AISLE, width=1.4)
        nx.draw_networkx_edges(H, p, edgelist=route, ax=ax, edge_color=color, width=2.6)
        edge_labels = {e: f"{H.edges[e]['weight']:.1f}" for e in H.edges}
        nx.draw_networkx_edge_labels(H, p, edge_labels=edge_labels, ax=ax, font_size=7.5,
                                     font_color=INK, rotate=False,
                                     bbox=dict(fc="white", ec="none", pad=0.4))
        colors = [INK if n == "Entrance" else color for n in H.nodes]
        nx.draw_networkx_nodes(H, p, ax=ax, node_color=colors, node_size=110, edgecolors="white")
        for n, (x, y) in p.items():
            off = (8, -16) if n == "Mayo and ketchup" else (8, 6)
            ax.annotate(n, (x, y), xytext=off, textcoords="offset points", fontsize=8.5)
        ax.invert_yaxis()
        ax.axis("off")
        ax.margins(0.12)
        ax.set_title(f"{title}\nshortest Hamiltonian cycle: {length:.1f} m", loc="left",
                     fontsize=11, fontweight="bold")
    fig.suptitle("Shortest walking distances between products, in meters (shortest cycle in color)",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "graphs.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def groups_figure(lengths, length_most, length_least):
    lengths = np.asarray(lengths)
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = np.arange(np.floor(lengths.min() / 2.5) * 2.5, lengths.max() + 5, 2.5)
    ax.hist(lengths, bins=bins, color=AISLE, edgecolor="white", linewidth=1)
    for value, color, text, ha in [
        (length_least, LEAST, f"7 least-bought\n{length_least:.1f} m", "left"),
        (length_most, MOST, f"7 most-bought\n{length_most:.1f} m", "right"),
    ]:
        ax.axvline(value, color=color, lw=2)
        ax.text(value + (1 if ha == "left" else -1), ax.get_ylim()[1] * (0.95 if ha == "left" else 0.75), text, color=INK,
                ha=ha, va="top", fontsize=9)
    ax.set_xlabel("Shortest route length (m)")
    ax.set_ylabel("Groups of 7 products")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#eeeeea", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title(f"Shortest route for all {len(lengths):,} possible groups of 7 products",
                 loc="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG / "all_groups.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
