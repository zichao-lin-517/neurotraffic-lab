# Experiment Design

## Default Scenario

The default experiment uses a 4x4 Manhattan-style network with directional links,
wave-shaped source demand, finite road storage, and signalized intersections.

## Controllers

- `fixed_time`: alternates phases by a fixed cycle.
- `max_pressure`: selects the phase group with the largest positive
  upstream-downstream queue pressure.

## Metrics

- `mean_delay`: cumulative queue delay divided by horizon.
- `total_throughput`: vehicles that exited sink links.
- `mean_queue`: average total queue length across all steps.
- `peak_queue`: maximum total queue length during the run.
- `final_queue`: total queue length at the final simulation step.

## Reproducibility

Every YAML config includes a random seed. Result files are written to an explicit
output directory under `runs/`.
