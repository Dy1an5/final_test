# Docker 环境验证记录

验证日期：2026-11-02。宿主机：Linux x86_64。

镜像：`rle-noc:gem5-20.0.0.3`。环境为 Ubuntu 18.04、gem5 20.0.0.3、Python 2.7.17、NumPy 1.13.3、Matplotlib 2.1.1，协议为 `Garnet_standalone`。

构建和运行方式见 [`docker/README_ZH.md`](docker/README_ZH.md)。

## 已实际执行的检查

1. 镜像成功构建，带有本项目修改的 `gem5.opt` 编译通过。最终构建日志保存于 `outputs/docker-build.log`。
2. 通过项目的 `icn_routing_gym()` 接口分别运行三种路由，均通过有效统计和路由编号检查。
3. 运行一轮 Q-learning，12 次仿真正常退出，Q 表发生更新。
4. 检查结果表中注入率、动作、延迟、吞吐量、轮次均有 12 个记录；奖励文件有 1 轮记录；PNG 文件有效。
5. Shell 和新增 Python 脚本通过语法检查，`git diff --check` 通过。

三种低负载仿真均使用 8×8 Mesh、uniform_random、注入率 0.05、20,000 cycles、inj-vnet=0：

| 路由 | 平均数据包延迟（原始统计值） | 接收 flit 数 | 接口计算的全网吞吐量（Gbit/s） |
| --- | ---: | ---: | ---: |
| XY | 15.590671 | 64034 | 409.8176 |
| Random oblivious | 15.662549 | 64033 | 409.8112 |
| West-first | 15.590671 | 64034 | 409.8176 |

该延迟采用原统计单位；本次 Ruby 时钟为 1 GHz，数值可按周期解读。正式论文对比仍需统一单位与归一化方式。

本次结果目录：

- XY：`outputs/smoke-20261102T020738Z-21403/`
- Random oblivious：`outputs/smoke-20261102T020756Z-21834/`
- West-first：`outputs/smoke-20261102T020757Z-21969/`
- Q-learning：`outputs/train-20261102T020758Z-22074/`

以上目录是本机生成的文件，已通过 `.gitignore` 排除，不随仓库代码提交。

Q-learning 验证命令：

```bash
bash docker/run.sh train qlearning --episodes 1 --seed 0
```

生成的主要文件：

```text
Tables/QL_xy_12_1.csv
Rewards_Hist/Reward_history_qlearning_xy.csv
Figures/QL_xy_12_1_RLNOC.png
executed_script.py
executed_icn_gym.py
run.log
```

## 这次验证的范围

本次证明环境能够编译、运行仿真，并完成 Q-learning 的学习与结果输出流程。SARSA 和 Expected SARSA 的训练命令已配置，尚未在本次验证中运行；完整 50 轮训练和论文各图的复现也尚未完成。

运行日志中保留了原配置产生的时钟取整、DRAM 容量匹配等提示。本次没有为了消除提示而改动原实验时钟或内存参数。正式复现实验时应与论文配置继续核对。
