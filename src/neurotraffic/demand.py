from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DemandProfile:
    arrivals: dict[str, np.ndarray]

    def at(self, link_id: str, step: int) -> float:
        series = self.arrivals.get(link_id)
        if series is None or step >= len(series):
            return 0.0
        return float(series[step])


def make_wave_demand(
    sources: tuple[str, ...],
    horizon: int,
    base_rate: float,
    peak_rate: float,
    seed: int = 7,
) -> DemandProfile:
    """Generate reproducible source-link demand with morning/evening waves."""

    rng = np.random.default_rng(seed)
    x = np.linspace(0, 2 * np.pi, horizon)
    arrivals: dict[str, np.ndarray] = {}

    for idx, source in enumerate(sources):
        phase = idx / max(1, len(sources)) * np.pi
        wave = (np.sin(x + phase) + 1.0) / 2.0
        lam = base_rate + (peak_rate - base_rate) * wave
        arrivals[source] = rng.poisson(lam).astype(float)

    return DemandProfile(arrivals)

