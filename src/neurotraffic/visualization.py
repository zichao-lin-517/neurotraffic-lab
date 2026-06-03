from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def generate_experiment_plots(
    timeseries: pd.DataFrame,
    intersection_queues: pd.DataFrame,
    comparison: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        output_dir / "congestion_timeseries.png",
        output_dir / "intersection_queue_heatmap.png",
        output_dir / "controller_comparison.png",
    ]
    plot_congestion_timeseries(timeseries, paths[0])
    plot_intersection_queue_heatmap(intersection_queues, paths[1])
    plot_controller_comparison(comparison, paths[2])
    return paths


def plot_congestion_timeseries(frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    for controller, group in frame.groupby("controller"):
        ax.plot(group["step"], group["total_queue"], linewidth=2, label=controller)

    ax.set_title("Network Congestion Over Time")
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Total queued vehicles")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_intersection_queue_heatmap(frame: pd.DataFrame, path: Path) -> None:
    controller = "max_pressure" if "max_pressure" in set(frame["controller"]) else frame["controller"].iloc[0]
    selected = frame[frame["controller"] == controller]
    top_nodes = (
        selected.groupby("intersection")["queue"]
        .max()
        .sort_values(ascending=False)
        .head(10)
        .index
    )
    pivot = (
        selected[selected["intersection"].isin(top_nodes)]
        .pivot_table(index="intersection", columns="step", values="queue", aggfunc="mean")
        .fillna(0.0)
        .loc[top_nodes]
    )

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=150)
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="magma")
    ax.set_title(f"Intersection Queue Heatmap ({controller})")
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Intersection")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    fig.colorbar(image, ax=ax, label="Queued vehicles")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_controller_comparison(frame: pd.DataFrame, path: Path) -> None:
    metrics = ["mean_delay", "total_throughput", "mean_queue"]
    titles = ["Mean Delay", "Total Throughput", "Mean Queue"]
    colors = ["#2f6f8f", "#39a275", "#d17a22"]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), dpi=150)
    for ax, metric, title, color in zip(axes, metrics, titles, colors):
        ax.bar(frame["controller"], frame[metric], color=color)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", alpha=0.25)

    fig.suptitle("Controller Strategy Comparison", y=1.03)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
