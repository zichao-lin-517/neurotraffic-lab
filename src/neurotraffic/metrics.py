from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from neurotraffic.simulator import StepRecord


def records_to_frame(records: list[StepRecord], controller: str) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            key: value
            for key, value in asdict(record).items()
            if key != "node_queues"
        }
        for record in records
    )
    frame["controller"] = controller
    return frame


def node_queues_to_frame(records: list[StepRecord], controller: str) -> pd.DataFrame:
    rows = []
    for record in records:
        for node_id, queue in record.node_queues.items():
            rows.append(
                {
                    "step": record.step,
                    "controller": controller,
                    "intersection": node_id,
                    "queue": queue,
                }
            )
    return pd.DataFrame(rows)


def summarize(records: list[StepRecord]) -> dict[str, float]:
    if not records:
        return {
            "mean_delay": 0.0,
            "total_throughput": 0.0,
            "mean_queue": 0.0,
            "peak_queue": 0.0,
            "final_queue": 0.0,
        }
    horizon = len(records)
    return {
        "mean_delay": records[-1].delay / horizon,
        "total_throughput": records[-1].throughput,
        "mean_queue": sum(record.total_queue for record in records) / horizon,
        "peak_queue": max(record.total_queue for record in records),
        "final_queue": records[-1].total_queue,
    }


def build_comparison_table(summary: pd.DataFrame) -> pd.DataFrame:
    table = summary.copy()
    if "fixed_time" not in set(table["controller"]):
        return table

    baseline = table.loc[table["controller"] == "fixed_time"].iloc[0]
    table["delay_reduction_vs_fixed_time_pct"] = (
        (baseline["mean_delay"] - table["mean_delay"]) / baseline["mean_delay"] * 100.0
    )
    table["throughput_gain_vs_fixed_time_pct"] = (
        (table["total_throughput"] - baseline["total_throughput"])
        / baseline["total_throughput"]
        * 100.0
    )
    return table


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
