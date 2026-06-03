from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ExperimentConfig:
    rows: int
    cols: int
    horizon: int
    seed: int
    base_rate: float
    peak_rate: float
    controllers: tuple[str, ...]
    output_dir: Path
    fixed_time_cycle: int = 8


def load_config(path: str | Path) -> ExperimentConfig:
    with Path(path).open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    return ExperimentConfig(
        rows=int(raw["network"]["rows"]),
        cols=int(raw["network"]["cols"]),
        horizon=int(raw["experiment"]["horizon"]),
        seed=int(raw["experiment"].get("seed", 7)),
        base_rate=float(raw["demand"]["base_rate"]),
        peak_rate=float(raw["demand"]["peak_rate"]),
        controllers=tuple(raw["experiment"]["controllers"]),
        output_dir=Path(raw["experiment"].get("output_dir", "runs")),
        fixed_time_cycle=int(raw.get("controller", {}).get("fixed_time_cycle", 8)),
    )

