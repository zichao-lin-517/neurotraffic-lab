from neurotraffic.controllers import MaxPressureController
from neurotraffic.config import ExperimentConfig
from neurotraffic.demand import make_wave_demand
from neurotraffic.metrics import summarize
from neurotraffic.network import make_grid_network
from neurotraffic.simulator import TrafficSimulator
from neurotraffic.cli import run_experiment


def test_simulator_runs_and_produces_metrics() -> None:
    network = make_grid_network(rows=3, cols=3)
    demand = make_wave_demand(network.sources, horizon=24, base_rate=2.0, peak_rate=6.0)
    simulator = TrafficSimulator(
        network=network,
        demand=demand,
        controller=MaxPressureController(),
        horizon=24,
    )

    records = simulator.run()
    summary = summarize(records)

    assert len(records) == 24
    assert records[-1].node_queues
    assert summary["mean_queue"] >= 0.0
    assert summary["total_throughput"] >= 0.0


def test_run_experiment_writes_tables_and_plots(tmp_path) -> None:
    config = ExperimentConfig(
        rows=3,
        cols=3,
        horizon=12,
        seed=7,
        base_rate=1.0,
        peak_rate=4.0,
        controllers=("fixed_time", "max_pressure"),
        output_dir=tmp_path,
    )

    summary = run_experiment(config)

    assert set(summary["controller"]) == {"fixed_time", "max_pressure"}
    assert (tmp_path / "timeseries.csv").exists()
    assert (tmp_path / "intersection_queues.csv").exists()
    assert (tmp_path / "comparison_table.csv").exists()
    assert (tmp_path / "congestion_timeseries.png").exists()
    assert (tmp_path / "intersection_queue_heatmap.png").exists()
    assert (tmp_path / "controller_comparison.png").exists()
