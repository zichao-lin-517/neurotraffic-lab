from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from neurotraffic.network import TrafficNetwork


class Controller(Protocol):
    name: str

    def choose_actions(
        self,
        network: TrafficNetwork,
        queues: dict[str, float],
        step: int,
    ) -> dict[str, tuple[str, ...]]:
        """Return allowed incoming links for each intersection."""


@dataclass
class FixedTimeController:
    cycle: int = 8
    name: str = "fixed_time"

    def choose_actions(
        self,
        network: TrafficNetwork,
        queues: dict[str, float],
        step: int,
    ) -> dict[str, tuple[str, ...]]:
        del queues
        actions = {}
        phase = (step // max(1, self.cycle)) % 2
        for node_id in network.signalized_nodes:
            incoming = network.incoming(node_id)
            if not incoming:
                actions[node_id] = ()
                continue
            actions[node_id] = tuple(link for i, link in enumerate(incoming) if i % 2 == phase)
        return actions


@dataclass
class MaxPressureController:
    name: str = "max_pressure"

    def choose_actions(
        self,
        network: TrafficNetwork,
        queues: dict[str, float],
        step: int,
    ) -> dict[str, tuple[str, ...]]:
        del step
        actions = {}
        for node_id in network.signalized_nodes:
            incoming = network.incoming(node_id)
            if not incoming:
                actions[node_id] = ()
                continue

            pressures: list[float] = []
            for link_id in incoming:
                downstream = network.successors(link_id)
                expected_downstream = sum(queues.get(out, 0.0) * ratio for out, ratio in downstream)
                pressures.append(queues.get(link_id, 0.0) - expected_downstream)

            phases = [
                tuple(link for i, link in enumerate(incoming) if i % 2 == 0),
                tuple(link for i, link in enumerate(incoming) if i % 2 == 1),
            ]
            phase_scores = [
                sum(max(0.0, pressures[incoming.index(link)]) for link in phase)
                for phase in phases
            ]
            actions[node_id] = phases[int(np.argmax(phase_scores))]
        return actions


def build_controller(name: str, cycle: int = 8) -> Controller:
    if name == "fixed_time":
        return FixedTimeController(cycle=cycle)
    if name == "max_pressure":
        return MaxPressureController()
    raise ValueError(f"Unknown controller: {name}")
