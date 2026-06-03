# Contributing

Thanks for helping improve NeuroTraffic Lab.

## Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m neurotraffic.cli compare --config examples/grid4x4_compare.yaml
```

## Contribution Areas

- New signal-control controllers, such as actuated control, backpressure variants,
  or reinforcement-learning policies.
- Forecasting baselines, such as historical average, STGCN, DCRNN, and Graph
  WaveNet.
- New benchmark scenarios with documented demand, seed, metrics, and expected
  output artifacts.
- Visualization improvements for network playback and intersection diagnostics.
- SUMO or CityFlow adapters.

## Pull Request Checklist

- Keep changes scoped and reproducible.
- Add or update tests for behavior changes.
- Run `python -m pytest`.
- Run at least one example experiment if metrics or simulation behavior changed.
- Update README or docs when changing user-facing commands or outputs.

