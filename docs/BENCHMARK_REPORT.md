# Benchmark Report: 4x4 Grid Signal Control

## Objective

Compare a static fixed-time signal controller with a dynamic max-pressure
controller on a reproducible 4x4 urban grid.

## Command

```bash
python -m neurotraffic.cli compare --config examples/grid4x4_compare.yaml
```

## Configuration

- Network: 4x4 Manhattan-style grid
- Horizon: 180 simulation steps
- Demand: wave-shaped source demand
- Seed: 7
- Controllers: `fixed_time`, `max_pressure`

## Results

| controller | mean_delay | total_throughput | mean_queue | peak_queue | final_queue | delay_reduction_vs_fixed_time_pct | throughput_gain_vs_fixed_time_pct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed_time | 646.69 | 10063.96 | 646.69 | 992.32 | 861.75 | 0.00 | 0.00 |
| max_pressure | 282.00 | 11744.20 | 282.00 | 498.02 | 421.80 | 56.39 | 16.70 |

## Interpretation

Max-pressure control uses local queue pressure to prioritize movements with high
upstream congestion and lower downstream congestion. In this scenario, it
reduces mean delay by 56.39% and increases throughput by 16.70% relative to
fixed-time control.

The result is not a universal claim that max-pressure always dominates every
fixed-time plan. It is a reproducible benchmark showing that the simulator,
metrics, and controller interface can reveal meaningful policy differences.

## Artifacts

- `runs/grid4x4_compare/comparison_table.csv`
- `runs/grid4x4_compare/timeseries.csv`
- `runs/grid4x4_compare/intersection_queues.csv`
- `runs/grid4x4_compare/congestion_timeseries.png`
- `runs/grid4x4_compare/intersection_queue_heatmap.png`
- `runs/grid4x4_compare/controller_comparison.png`

