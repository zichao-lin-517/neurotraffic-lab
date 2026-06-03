from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Link:
    """Directed road link between two intersections."""

    link_id: str
    start: str
    end: str
    capacity: float
    free_flow_time: int
    storage: float


@dataclass(frozen=True)
class Intersection:
    """Signalized intersection with incoming and outgoing links."""

    node_id: str
    incoming: tuple[str, ...]
    outgoing: tuple[str, ...]


@dataclass(frozen=True)
class TrafficNetwork:
    links: dict[str, Link]
    intersections: dict[str, Intersection]
    turn_ratios: dict[tuple[str, str], float]
    sources: tuple[str, ...]
    sinks: tuple[str, ...]

    def incoming(self, node_id: str) -> tuple[str, ...]:
        return self.intersections[node_id].incoming

    def outgoing(self, node_id: str) -> tuple[str, ...]:
        return self.intersections[node_id].outgoing

    def successors(self, link_id: str) -> list[tuple[str, float]]:
        return [
            (to_link, ratio)
            for (from_link, to_link), ratio in self.turn_ratios.items()
            if from_link == link_id
        ]

    @property
    def signalized_nodes(self) -> tuple[str, ...]:
        return tuple(self.intersections.keys())


def make_grid_network(
    rows: int,
    cols: int,
    capacity: float = 24.0,
    free_flow_time: int = 1,
    storage: float = 80.0,
) -> TrafficNetwork:
    """Create a bidirectional Manhattan-style grid network.

    Boundary links act as demand sources and sinks. The graph is intentionally compact
    so experiments can run without a heavyweight microscopic simulator.
    """

    if rows < 2 or cols < 2:
        raise ValueError("rows and cols must both be at least 2")

    nodes = [f"n{r}_{c}" for r in range(rows) for c in range(cols)]
    links: dict[str, Link] = {}

    def add_link(start: str, end: str) -> None:
        link_id = f"{start}->{end}"
        links[link_id] = Link(link_id, start, end, capacity, free_flow_time, storage)

    for r in range(rows):
        for c in range(cols):
            node = f"n{r}_{c}"
            if c + 1 < cols:
                add_link(node, f"n{r}_{c + 1}")
                add_link(f"n{r}_{c + 1}", node)
            if r + 1 < rows:
                add_link(node, f"n{r + 1}_{c}")
                add_link(f"n{r + 1}_{c}", node)

    incoming_by_node = {node: [] for node in nodes}
    outgoing_by_node = {node: [] for node in nodes}
    for link in links.values():
        outgoing_by_node[link.start].append(link.link_id)
        incoming_by_node[link.end].append(link.link_id)

    intersections = {
        node: Intersection(
            node,
            tuple(sorted(incoming_by_node[node])),
            tuple(sorted(outgoing_by_node[node])),
        )
        for node in nodes
    }

    turn_ratios: dict[tuple[str, str], float] = {}
    for node in nodes:
        incoming = incoming_by_node[node]
        outgoing = [link_id for link_id in outgoing_by_node[node] if links[link_id].end != node]
        for in_link in incoming:
            candidates = [out for out in outgoing if links[out].end != links[in_link].start]
            if not candidates:
                continue
            ratio = 1.0 / len(candidates)
            for out_link in candidates:
                turn_ratios[(in_link, out_link)] = ratio

    sources = tuple(
        link_id
        for link_id, link in links.items()
        if _is_boundary(link.start, rows, cols) and not _is_boundary(link.end, rows, cols)
    )
    sinks = tuple(
        link_id
        for link_id, link in links.items()
        if not _is_boundary(link.start, rows, cols) and _is_boundary(link.end, rows, cols)
    )

    if not sources:
        sources = tuple(_boundary_outgoing_links(links.values(), rows, cols))
    if not sinks:
        sinks = tuple(_boundary_incoming_links(links.values(), rows, cols))

    return TrafficNetwork(links, intersections, turn_ratios, sources, sinks)


def _is_boundary(node_id: str, rows: int, cols: int) -> bool:
    row, col = (int(part) for part in node_id[1:].split("_"))
    return row in {0, rows - 1} or col in {0, cols - 1}


def _boundary_outgoing_links(links: Iterable[Link], rows: int, cols: int) -> list[str]:
    return [link.link_id for link in links if _is_boundary(link.start, rows, cols)]


def _boundary_incoming_links(links: Iterable[Link], rows: int, cols: int) -> list[str]:
    return [link.link_id for link in links if _is_boundary(link.end, rows, cols)]

