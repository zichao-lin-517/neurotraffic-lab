# Architecture

NeuroTraffic Lab is organized as a small research platform rather than a single
script. The goal is to keep simulation, control, metrics, and forecasting
interfaces independent enough to evolve.

## Data Flow

```text
YAML config
  -> grid network generator
  -> wave demand generator
  -> traffic simulator
  -> controller policy
  -> step records
  -> metrics tables and plots
```

## Core Modules

- `network.py`: directed road graph with links, intersections, turn ratios,
  source links, and sink links.
- `demand.py`: reproducible demand profiles indexed by source link and step.
- `controllers.py`: control policies that map current queues to allowed incoming
  links at each intersection.
- `simulator.py`: queue-based traffic dynamics with link capacity, finite
  storage, spillback, and throughput accounting.
- `metrics.py`: summary metrics and strategy comparison tables.
- `visualization.py`: reproducible experiment plots.
- `forecasting.py`: graph time-series container and adjacency extraction for
  future ST-GNN models.

## Extension Points

### Add a Controller

Implement the `Controller` protocol in `controllers.py`:

```python
def choose_actions(network, queues, step) -> dict[str, tuple[str, ...]]:
    ...
```

Then register it in `build_controller`.

### Add a Benchmark

Create a YAML file in `examples/` with:

- network shape
- demand rates
- controller list
- seed
- output directory

The CLI will automatically write CSV files and plots.

### Add Forecasting

Use `forecasting.adjacency_from_network` to convert the road graph into an
adjacency matrix, then build tensors with shape `[time, link, feature]`.

