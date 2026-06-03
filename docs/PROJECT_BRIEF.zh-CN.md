# NeuroTraffic Lab 中文项目介绍

## 项目概述

NeuroTraffic Lab 是一个面向智能交通系统实验的 Python 框架。项目提供轻量级城市交通数字孪生、交通信号控制基准、可复现实验指标和图时序数据接口，可用于快速验证交通控制策略与后续时空预测模型。

## 背景

交通信号控制与交通流预测是智能交通系统中的基础问题。完整实验通常需要把路网建模、交通需求生成、交通状态演化、信号控制决策和评价指标连接起来。NeuroTraffic Lab 提供了一个紧凑、可复现、易扩展的实验管线，便于在接入 SUMO、CityFlow 等更重型仿真器之前进行算法迭代。

## 核心能力

- 使用有向图表示城市路网、路段、路口和转向关系。
- 内置队列式宏观交通仿真器，支持容量约束、道路存储约束和下游溢出。
- 支持固定周期控制和 max-pressure 控制两个信号控制基线。
- 通过 YAML 配置管理网络规模、需求强度、随机种子、控制策略和输出目录。
- 输出全网时序指标、路口排队长度、策略对比表和可视化图。
- 提供图时序数据结构和邻接矩阵构建接口，便于后续接入 STGCN、DCRNN、Graph WaveNet 等模型。

## 实验流程

```text
YAML 配置
  -> 路网生成
  -> 需求生成
  -> 交通仿真
  -> 信号控制策略
  -> 指标计算
  -> CSV 与图表输出
```

## 运行方式

```bash
python -m pip install -e ".[dev]"
python -m neurotraffic.cli compare --config examples/grid4x4_compare.yaml
python -m pytest
```

实验结果会写入：

```text
runs/grid4x4_compare/
  summary.csv
  comparison_table.csv
  timeseries.csv
  intersection_queues.csv
  congestion_timeseries.png
  intersection_queue_heatmap.png
  controller_comparison.png
```

## 示例结果

在默认 `4x4` 网格路网实验中，`max_pressure` 控制策略相对 `fixed_time` 控制策略降低了平均延误，并提升了总吞吐量。完整实验设置和结果解释见 [Benchmark report](BENCHMARK_REPORT.md)。

## 扩展方向

- 增加 ST-GNN 交通预测基线。
- 接入 SUMO 或 CityFlow 微观交通仿真器。
- 增加更多需求模式和路网规模的 benchmark。
- 构建交通状态回放和路口诊断可视化界面。
