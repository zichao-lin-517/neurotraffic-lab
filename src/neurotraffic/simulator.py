from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from neurotraffic.controllers import Controller
from neurotraffic.demand import DemandProfile
from neurotraffic.network import TrafficNetwork


@dataclass
class SimulationState:
    queues: dict[str, float]
    cumulative_delay: float = 0.0
    throughput: float = 0.0


@dataclass
class StepRecord:
    step: int
    total_queue: float
    delay: float
    throughput: float
    node_queues: dict[str, float]


class TrafficSimulator:
    """A compact queue-based traffic simulator for fast algorithm iteration."""

    def __init__(
        self,
        network: TrafficNetwork,
        demand: DemandProfile,
        controller: Controller,
        horizon: int,
        seed: int = 7,
    ) -> None:
        self.network = network
        self.demand = demand
        self.controller = controller
        self.horizon = horizon
        self.rng = np.random.default_rng(seed)
        self.state = SimulationState(queues={link_id: 0.0 for link_id in network.links})

    def run(self) -> list[StepRecord]:
        records = []
        for step in range(self.horizon):
            records.append(self.step(step))
        return records

    def step(self, step: int) -> StepRecord:
        queues = self.state.queues
        for source in self.network.sources:
            link = self.network.links[source]
            queues[source] = min(link.storage, queues[source] + self.demand.at(source, step))

        actions = self.controller.choose_actions(self.network, queues, step)
        moved: dict[str, float] = {link_id: 0.0 for link_id in self.network.links}
        exited = 0.0

        for node_id, allowed_incoming in actions.items():
            del node_id
            for in_link in allowed_incoming:
                link = self.network.links[in_link]
                discharge = min(queues[in_link], link.capacity)
                if discharge <= 0:
                    continue

                successors = self.network.successors(in_link)
                if not successors or in_link in self.network.sinks:
                    queues[in_link] -= discharge
                    exited += discharge
                    continue

                accepted = 0.0
                for out_link, ratio in successors:
                    out = self.network.links[out_link]
                    desired = discharge * ratio
                    room = max(0.0, out.storage - queues[out_link] - moved[out_link])
                    flow = min(desired, room)
                    moved[out_link] += flow
                    accepted += flow
                queues[in_link] -= accepted

        for link_id, flow in moved.items():
            queues[link_id] += flow

        total_queue = float(sum(queues.values()))
        node_queues = {
            node_id: float(sum(queues[link_id] for link_id in intersection.incoming))
            for node_id, intersection in self.network.intersections.items()
        }
        self.state.cumulative_delay += total_queue
        self.state.throughput += exited

        return StepRecord(
            step=step,
            total_queue=total_queue,
            delay=self.state.cumulative_delay,
            throughput=self.state.throughput,
            node_queues=node_queues,
        )
