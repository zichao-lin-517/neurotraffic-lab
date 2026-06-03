import pandas as pd

from neurotraffic.forecasting import adjacency_from_network
from neurotraffic.metrics import build_comparison_table
from neurotraffic.network import make_grid_network


def test_adjacency_from_network_matches_link_count() -> None:
    network = make_grid_network(rows=3, cols=3)
    link_ids, adjacency = adjacency_from_network(network)

    assert len(link_ids) == len(network.links)
    assert adjacency.shape == (len(network.links), len(network.links))
    assert adjacency.sum() > 0.0


def test_comparison_table_adds_baseline_improvement_columns() -> None:
    summary = pd.DataFrame(
        [
            {
                "controller": "fixed_time",
                "mean_delay": 100.0,
                "total_throughput": 1000.0,
                "mean_queue": 100.0,
            },
            {
                "controller": "max_pressure",
                "mean_delay": 70.0,
                "total_throughput": 1100.0,
                "mean_queue": 70.0,
            },
        ]
    )

    table = build_comparison_table(summary)

    max_pressure = table[table["controller"] == "max_pressure"].iloc[0]
    assert max_pressure["delay_reduction_vs_fixed_time_pct"] == 30.0
    assert max_pressure["throughput_gain_vs_fixed_time_pct"] == 10.0
