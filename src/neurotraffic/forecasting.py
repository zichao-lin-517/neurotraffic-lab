from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from neurotraffic.network import TrafficNetwork


@dataclass(frozen=True)
class GraphTimeSeries:
    """ST-GNN-ready graph time-series container.

    features shape: [time, num_links, num_features]
    adjacency shape: [num_links, num_links]
    """

    link_ids: tuple[str, ...]
    features: np.ndarray
    adjacency: np.ndarray


def adjacency_from_network(network: TrafficNetwork) -> tuple[tuple[str, ...], np.ndarray]:
    link_ids = tuple(sorted(network.links))
    index = {link_id: i for i, link_id in enumerate(link_ids)}
    adjacency = np.zeros((len(link_ids), len(link_ids)), dtype=np.float32)
    for (from_link, to_link), ratio in network.turn_ratios.items():
        adjacency[index[from_link], index[to_link]] = ratio
    return link_ids, adjacency


class ForecastingModel:
    """Minimal interface for future PyTorch ST-GNN models."""

    def fit(self, series: GraphTimeSeries) -> None:
        raise NotImplementedError

    def predict(self, history: GraphTimeSeries, horizon: int) -> np.ndarray:
        raise NotImplementedError

