# RLE-NOC 入门与复现记录

本记录基于 2026-11-02 对当前仓库的初始检查。随后已完成 Docker 构建、三种路由的低负载仿真和一轮 Q-learning 验证，详见 [`DOCKER_VALIDATION_ZH.md`](DOCKER_VALIDATION_ZH.md)。仓库原有的数据和图不能视为本次复现结果。

Docker 配置与运行入口见 [`docker/README_ZH.md`](docker/README_ZH.md)。下文中的启动障碍描述的是原始仓库；容器构建会自动补齐完整工程并配置旧版依赖。

## 1. 这个课题研究什么

论文：Md Farhadur Reza、Tung Thanh Le，*Reinforcement Learning Enabled Routing for High-Performance Networks-on-Chip*，ISCAS 2021，DOI：10.1109/ISCAS51556.2021.9401790。

[作者所在高校的论文页面](https://scholars.eiu.edu/en/publications/reinforcement-learning-enabled-routing-for-high-performance-netwo/)提供摘要和全文入口。

片上网络（NoC）连接芯片上的多个计算核心。核心之间发送数据包时，需要经过路由器和链路；流量变大时，数据包可能排队，通信延迟随之上升。

本项目的基本思路是：尝试不同的已有路由算法，根据仿真结果学习哪一种更适合当前流量条件。

需要先掌握的几个词：

| 名称 | 在本项目中的含义 |
| --- | --- |
| Mesh | 路由器排列成二维网格的网络结构 |
| 注入率（injection rate） | 生成网络流量的参数；具体单位需要结合流量发生器和虚拟网络配置核对 |
| Packet / Flit | 数据包 / 在网络中传输和流控的数据片段 |
| Latency | 数据包从发送到接收所需的时间，需记录统计单位 |
| Throughput | 单位时间实际接收的数据量，需说明是全网总量还是按节点归一化 |
| Episode | 强化学习的一轮；当前脚本一轮依次扫描多个注入率 |
| Q 表 | 保存“某个状态下选择某个动作有多好”的数值表 |

## 2. 代码实际怎样运行

当前主脚本中的流程是：

```text
注入率作为状态
  → 强化学习选择一种路由算法
  → 启动一次 gem5/Garnet 仿真
  → 读取 stats.txt 中的延迟和接收量
  → 计算奖励并更新 Q 表
  → 进入下一个注入率
```

gem5 是体系结构模拟器；Garnet 是其中的片上网络模型。这里可以先用合成流量实验，不需要先运行完整操作系统或真实应用。

以当前主脚本为准：

- 状态：流量注入率，默认从 0.05 到 0.60，步长 0.05。
- 动作：`xy`、`random_oblivious`、`west_first`。
- 奖励：平均数据包延迟取负数，并保留两位小数；延迟越小，奖励越高。
- 学习方法：SARSA、Expected SARSA、Q-learning，使用 Q 表。
- 每次动作调用一个新的 gem5 进程。这一点需要与论文描述的控制方式逐项对照。

以下是**当前代码默认值**，尚不能认定为论文全部实验的设置：

| 项目 | 当前值 | 依据 |
| --- | --- | --- |
| gem5 版本标识 | 20.0.0.3 | `src/base/version.cc` |
| 网络规模 | 64 个 CPU 节点、64 个目录控制器，8×8 Mesh | `example/icn_gym.py` 的启动命令 |
| 网络模型 | garnet2.0 | 同上 |
| 拓扑 | 三种动作均使用 Mesh_XY | 同上及三个 RL 主脚本 |
| 流量 | uniform_random | `example/icn_gym.py` |
| 仿真长度 | 每次 20,000 cycles | 同上 |
| 注入虚拟网络 | inj-vnet=0 | 同上 |
| 训练轮数 | 每种 RL 方法 50 轮 | 三个 RL 主脚本 |

默认每种 RL 方法执行约 50×12＝600 次仿真，三种方法合计约 1,800 次，因此先验证单次仿真更容易定位问题。

## 3. 优先看哪些文件

| 路径 | 作用 |
| --- | --- |
| `README.md` | 论文信息和作者给出的启动方式 |
| `interconnect-routing-gym/example/icn_gym.py` | 连接 RL 与仿真器；定义动作、奖励、启动命令 |
| `interconnect-routing-gym/example/extract_network_stats.py` | 从仿真统计文件提取数据 |
| `interconnect-routing-gym/example/basic_routing.py` | 分别运行三种固定路由，建立比较基线 |
| `interconnect-routing-gym/example/rl_QLearning_example.py` | Q-learning 实验入口 |
| `interconnect-routing-gym/example/rl_sarsa_example.py` | SARSA 实验入口 |
| `interconnect-routing-gym/example/rl_expected_sarsa_example.py` | Expected SARSA 实验入口 |
| `configs/example/garnet_synth_traffic.py` | 合成流量仿真的配置入口 |
| `configs/network/Network.py` | 把路由名称映射成仿真器的算法编号 |
| `src/mem/ruby/network/garnet2.0/RoutingUnit.cc` | C++ 路由算法实现 |
| `interconnect-routing-gym/Inter_Connect_Networks/` | 已有表格、奖励历史和图片 |
| `m5out/` | 仓库附带的一次仿真配置与统计，新的默认运行可能覆盖它 |

建议按“环境接口 → Q-learning 主脚本 → 统计提取 → C++ 路由”的顺序读代码，开始时不需要通读整个 gem5 源码。

注意：`Baseline_xyRouting_example.py` 中会随机选择多个路由算法，不能仅根据文件名就把它当作固定 XY 基线。

## 4. 已确认的启动障碍

1. **构建工程不完整。** 当前仓库没有根目录 `SConstruct`、`ext/`、`system/`，也没有脚本要求的 `build/NULL/gem5.debug`。需要取得匹配版本的完整 gem5 工程，再比较并合入本项目修改。不能只复制 `RoutingUnit.cc`，因为还涉及接口和配置改动。
2. **路径写死。** 多个脚本使用 `/home/tungthanhle/gem5/`，当前机器无法直接沿用。
3. **解释器兼容性。** 当前 `python` 是 3.14.8；`extract_network_stats.py` 第 39 行的 `print self.res` 无法通过 Python 3 语法解析。修复这一行只能解决该处语法问题，完整运行仍需核对旧版 gem5 与依赖的兼容性。
4. **当前 PATH 中未发现 Python 2、SCons、SWIG。** 具体安装版本应在确认 gem5 构建方案后确定。
5. **仿真失败可能被旧数据掩盖。** `icn_gym.py` 使用 `os.system()`，没有检查返回状态就继续读取统计。如果启动失败而旧 `m5out/stats.txt` 仍存在，可能错误使用历史数据。

这些是当前代码和环境需要处理的问题，不能仅靠 README 中的一条启动命令完成复现。

## 5. 跑通后仍需核对的结果问题

- `update_Q()` 第五个参数是折扣因子 `gamma`，但三个 RL 主脚本传入的是名为 `epsilon` 的衰减变量；动作探索概率又在另一个函数中按轮数计算。应记录原始行为，再与论文参数核对，分别保存原版与修正版实验。
- 三种动作默认共用 `Mesh_XY`。该拓扑对水平、垂直链路设置不同权重；West-first 实现又依赖路由表候选，因此需要检查它在此配置下是否获得预期的自适应选择空间。
- `icn_gym.py` 的统计历史使用模块级字典。固定路由脚本只重置自己的局部字典，需要检查不同算法的数据是否累积到同一份历史中。
- 当前脚本没有显式固定 Python/NumPy 随机种子，也没有单独的、关闭探索的最终评估流程。训练期间的曲线不能直接代替最终策略的性能评估。
- 当前吞吐量公式假定每 flit 16 字节，计算全网 Gbit/s。需要核对实际 flit 宽度、统计时间和论文是否使用相同归一化方式。
- 低延迟需要同时结合接收数量、吞吐量及未完成传输情况解读，尤其是在高注入率下。

以上是代码审查发现的核对项，尚未通过新仿真确认其实际影响。

## 6. 分阶段复现与验收

| 阶段 | 要完成的事 | 验收依据 |
| --- | --- | --- |
| A：对齐论文与工程 | 阅读论文实验部分；确认完整 gem5 20.0.0.3 工程及本项目修改 | 版本、修改清单、参数对照表可追溯 |
| B：单次固定路由 | 先运行低注入率的 XY 仿真，单独保存输出目录 | 进程成功退出；新统计中有有效接收量和延迟 |
| C：固定路由基线 | 用相同配置分别扫描三种路由算法 | 每个算法、每个注入率有独立原始统计与曲线 |
| D：小规模 RL 验证 | 少量轮数接通选动作、仿真、奖励、Q 更新 | Q 值确实更新；结果能追溯到对应仿真 |
| E：完整复现实验 | 按核对后的参数训练、独立评估并重复多个随机种子 | 延迟、吞吐量、奖励曲线及结果波动可检查 |
| F：论文结果对照 | 逐图比较条件、趋势和差异 | 说明哪些结果一致，哪些不一致，以及证据支持的原因 |

每次实验保存：代码版本与修改、环境版本、完整命令、随机种子、配置、原始统计、整理数据和绘图脚本。原始复现与后续改进使用不同输出目录。

当前已确认匹配的官方源码并完成阶段 B，以及阶段 D 的一轮 Q-learning 验证。下一步是对齐论文实验设置，完成三种固定路由的完整基线，再开展完整训练与独立评估。
