"""Create one horizontal figure for the three toy-model datasets.

This file is standalone; it does not depend on the other plotting scripts.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


BLUE = "#6F9ED6"
ORANGE = "#EE945D"
GREEN = "#63B982"
PURPLE = "#B38AD8"
EDGE = "#D0D0D0"
SPECIAL_EDGE = "#888888"
NODE_SIZE = 230


def connected_random_graph(n, p, seed):
    graph = nx.erdos_renyi_graph(n, p, seed=seed)
    components = list(nx.connected_components(graph))
    for left, right in zip(components[:-1], components[1:]):
        graph.add_edge(next(iter(left)), next(iter(right)))
    return graph


def enforce_min_distance(positions, min_distance=0.30, iterations=400):
    """Push spring-layout vertices apart to prevent visual overlap."""
    positions = {
        node: np.asarray(coordinates, dtype=float).copy()
        for node, coordinates in positions.items()
    }
    nodes = list(positions)
    for _ in range(iterations):
        changed = False
        for left_index, left in enumerate(nodes):
            for right in nodes[left_index + 1:]:
                difference = positions[left] - positions[right]
                distance = np.linalg.norm(difference)
                if distance < 1e-9:
                    difference = np.array([0.01, 0.01])
                    distance = np.linalg.norm(difference)
                if distance < min_distance:
                    displacement = difference / distance * (min_distance - distance) / 2
                    positions[left] += displacement
                    positions[right] -= displacement
                    changed = True
        if not changed:
            break

    center = np.mean(list(positions.values()), axis=0)
    return {node: coordinates - center for node, coordinates in positions.items()}


def spring_positions(graph, seed):
    positions = nx.spring_layout(graph, seed=seed, k=0.95, iterations=600)
    positions = enforce_min_distance(positions, min_distance=0.34)
    return {node: (1.18 * xy[0], xy[1]) for node, xy in positions.items()}


def unique_color_graphs():
    rng = np.random.default_rng(12)
    background = connected_random_graph(20, 0.16, 12)
    background_labels = rng.choice([0, 1], size=20)
    background_colors = [BLUE if value == 0 else ORANGE for value in background_labels]

    query = connected_random_graph(13, 0.20, 24)
    query_labels = rng.choice([0, 1], size=13)
    query_colors = [BLUE if value == 0 else ORANGE for value in query_labels]
    query_colors[0] = GREEN

    return (
        (background, spring_positions(background, 20), background_colors, []),
        (query, spring_positions(query, 35), query_colors, []),
    )


def graph_without_color_pair(n, p, colors, forbidden, seed):
    rng = np.random.default_rng(seed)
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for u in range(n):
        for v in range(u + 1, n):
            if {colors[u], colors[v]} == set(forbidden):
                continue
            if rng.random() < p:
                graph.add_edge(u, v)
    while not nx.is_connected(graph):
        components = [list(c) for c in nx.connected_components(graph)]
        added = False
        for u in components[0]:
            for v in components[1]:
                if {colors[u], colors[v]} != set(forbidden):
                    graph.add_edge(u, v)
                    added = True
                    break
            if added:
                break
    return graph


def unique_pair_graphs():
    palette = {0: BLUE, 1: ORANGE, 2: GREEN, 3: PURPLE}
    rng = np.random.default_rng(123)

    background_colors = rng.choice([0, 1], size=22)
    bg_special = rng.choice(22, size=2, replace=False)
    background_colors[bg_special[0]] = 2
    background_colors[bg_special[1]] = 3
    background = graph_without_color_pair(
        22, 0.14, background_colors, (2, 3), seed=124
    )

    query = connected_random_graph(14, 0.22, 456)
    query_colors = rng.choice([0, 1], size=14)
    query_special = rng.choice(14, size=2, replace=False)
    query_colors[query_special[0]] = 2
    query_colors[query_special[1]] = 3
    query.add_edge(*query_special)

    return (
        (
            background,
            spring_positions(background, 30),
            [palette[value] for value in background_colors],
            [],
        ),
        (
            query,
            spring_positions(query, 40),
            [palette[value] for value in query_colors],
            [tuple(query_special)],
        ),
    )


def connected_bipartite(blue_nodes, orange_nodes, p, seed):
    rng = np.random.default_rng(seed)
    graph = nx.Graph()
    graph.add_nodes_from(blue_nodes + orange_nodes)
    for u in blue_nodes:
        for v in orange_nodes:
            if rng.random() < p:
                graph.add_edge(u, v)
    for node, choices in [(u, orange_nodes) for u in blue_nodes] + [
        (v, blue_nodes) for v in orange_nodes
    ]:
        if graph.degree(node) == 0:
            graph.add_edge(node, int(rng.choice(choices)))
    while not nx.is_connected(graph):
        first, second = [list(c) for c in nx.connected_components(graph)][:2]
        for u in first:
            candidate = next(
                (
                    v for v in second
                    if (u in blue_nodes) != (v in blue_nodes)
                ),
                None,
            )
            if candidate is not None:
                graph.add_edge(u, candidate)
                break
    return graph


def triangle_positions(blue_nodes, orange_nodes, query=False):
    positions = {}
    if query:
        positions[blue_nodes[0]] = (0.0, 0.95)
        positions[blue_nodes[1]] = (0.48, 0.95)
        positions[blue_nodes[2]] = (0.24, 0.50)
        for node, y in zip(blue_nodes[3:], np.linspace(0.0, -0.75, len(blue_nodes) - 3)):
            positions[node] = (0.24, y)
    else:
        for node, y in zip(blue_nodes, np.linspace(1.0, -1.0, len(blue_nodes))):
            positions[node] = (0.0, y)
    for node, y in zip(orange_nodes, np.linspace(1.0, -1.0, len(orange_nodes))):
        positions[node] = (1.5, y)
    return positions


def unique_triangle_graphs():
    bg_blue = list(range(6))
    bg_orange = list(range(6, 17))
    background = connected_bipartite(bg_blue, bg_orange, 0.30, 123)
    matching = [(0, 1), (2, 3)]
    background.add_edges_from(matching)

    q_blue = list(range(5))
    q_orange = list(range(5, 14))
    query = connected_bipartite(q_blue, q_orange, 0.36, 456)
    triangle = [(0, 1), (1, 2), (2, 0)]
    query.add_edges_from(triangle)

    return (
        (
            background,
            triangle_positions(bg_blue, bg_orange),
            [BLUE] * len(bg_blue) + [ORANGE] * len(bg_orange),
            matching,
        ),
        (
            query,
            triangle_positions(q_blue, q_orange, query=True),
            [BLUE] * len(q_blue) + [ORANGE] * len(q_orange),
            triangle,
        ),
    )


def draw_graph(ax, graph_data, subtitle):
    graph, positions, node_colors, special_edges = graph_data
    special_keys = {frozenset(edge) for edge in special_edges}
    normal_edges = [edge for edge in graph.edges() if frozenset(edge) not in special_keys]

    nx.draw_networkx_edges(
        graph, positions, ax=ax, edgelist=normal_edges,
        edge_color=EDGE, width=1.25, alpha=0.9,
    )
    if special_edges:
        nx.draw_networkx_edges(
            graph, positions, ax=ax, edgelist=special_edges,
            edge_color=SPECIAL_EDGE, width=2.8,
        )
    nx.draw_networkx_nodes(
        graph, positions, ax=ax, node_color=node_colors,
        node_size=NODE_SIZE, edgecolors="white", linewidths=0.9,
    )
    ax.set_title(subtitle, fontsize=10, pad=5)
    ax.margins(0.10)
    ax.set_axis_off()


def main():
    datasets = (
        ("Unique-color", 1, unique_color_graphs(), r"Background: $G(1000, 0.003)$", r"Query: $S_i\sim G(30,0.1)$"),
        ("Unique-pair", 2, unique_pair_graphs(), r"Background: $G(1000, 0.003)$", r"Query: $S_i\sim G(30,0.1)$"),
        ("Unique-triangle", 3, unique_triangle_graphs(), "Background: connected bipartite", r"Query: $|V(S_i)|=30$"),
    )

    figure = plt.figure(figsize=(18, 5.6), constrained_layout=True)
    outer = figure.add_gridspec(1, 3, wspace=0.035)

    for column, (title, k_star, graphs, bg_title, query_title) in enumerate(datasets):
        panel = outer[column].subgridspec(2, 2, height_ratios=[0.12, 0.88], wspace=-0.08)
        title_ax = figure.add_subplot(panel[0, :])
        title_ax.text(0.5, 0.68, title, ha="center", va="center", fontsize=17, weight="bold")
        title_ax.text(0.5, 0.04, rf"$k^*={k_star}$", ha="center", va="center", fontsize=13)
        title_ax.set_axis_off()

        draw_graph(figure.add_subplot(panel[1, 0]), graphs[0], bg_title)
        draw_graph(figure.add_subplot(panel[1, 1]), graphs[1], query_title)

    # Vertical separators between the three dataset cases.
    for x in (1 / 3, 2 / 3):
        figure.add_artist(
            plt.Line2D(
                [x, x], [0.04, 0.96], transform=figure.transFigure,
                color="#B8B8B8", linewidth=1.2,
            )
        )

    output = Path(__file__).resolve().parent / "combined_toy_datasets_horizontal.png"
    figure.savefig(output, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved combined figure to {output}")


if __name__ == "__main__":
    main()
