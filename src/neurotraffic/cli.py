from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from neurotraffic.config import ExperimentConfig, load_config
from neurotraffic.controllers import build_controller
from neurotraffic.demand import make_wave_demand
from neurotraffic.metrics import (
    build_comparison_table,
    node_queues_to_frame,
    records_to_frame,
    summarize,
    write_csv,
)
from neurotraffic.network import make_grid_network
from neurotraffic.simulator import TrafficSimulator
from neurotraffic.visualization import generate_experiment_plots


def run_experiment(config: ExperimentConfig) -> pd.DataFrame:
    network = make_grid_network(config.rows, config.cols)
    demand = make_wave_demand(
        network.sources,
        horizon=config.horizon,
        base_rate=config.base_rate,
        peak_rate=config.peak_rate,
        seed=config.seed,
    )

    frames = []
    node_queue_frames = []
    summaries = []
    for name in config.controllers:
        controller = build_controller(name, cycle=config.fixed_time_cycle)
        simulator = TrafficSimulator(
            network=network,
            demand=demand,
            controller=controller,
            horizon=config.horizon,
            seed=config.seed,
        )
        records = simulator.run()
        frames.append(records_to_frame(records, controller.name))
        node_queue_frames.append(node_queues_to_frame(records, controller.name))
        summaries.append({"controller": controller.name, **summarize(records)})

    output_dir = config.output_dir
    result_frame = pd.concat(frames, ignore_index=True)
    node_queue_frame = pd.concat(node_queue_frames, ignore_index=True)
    summary_frame = pd.DataFrame(summaries)
    comparison_frame = build_comparison_table(summary_frame)
    write_csv(result_frame, output_dir / "timeseries.csv")
    write_csv(node_queue_frame, output_dir / "intersection_queues.csv")
    write_csv(summary_frame, output_dir / "summary.csv")
    write_csv(comparison_frame, output_dir / "comparison_table.csv")
    generate_experiment_plots(result_frame, node_queue_frame, comparison_frame, output_dir)
    return comparison_frame


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="neurotraffic")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--config", required=True)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--config", required=True)

    args = parser.parse_args(argv)
    config = load_config(Path(args.config))
    summary = run_experiment(config)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
