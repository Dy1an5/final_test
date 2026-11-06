# 用 Docker 运行 RLE-NOC

在项目根目录执行以下命令。宿主机只需要 Docker 和 Bash；完整 gem5 源码、编译工具、Python 和绘图库均在容器中准备。

## 1. 构建镜像

```bash
bash docker/run.sh build
```

默认镜像名为 `rle-noc:gem5-20.0.0.3`，使用 2 个编译进程。首次构建需要联网下载 Ubuntu、软件包和 gem5 源码，并编译模拟器。

镜像使用构建时的代码快照。修改宿主机代码后需重新执行构建；只修改强化学习脚本时会复用已编译的 gem5 层。

需要减少编译时的内存用量时：

```bash
BUILD_JOBS=1 bash docker/run.sh build
```

镜像配置：

- Ubuntu 18.04，基础镜像固定到内容摘要。
- gem5 `20.0.0.3`，校验提交 `fa70478413e4650d0058cbfe81fd5ce362101994`。
- 构建目标：`build/NULL/gem5.opt PROTOCOL=Garnet_standalone`。
- GCC、Python 2.7、SCons、NumPy、Matplotlib 使用 Ubuntu 18.04 软件仓库版本，实际安装版本保存到 `packages.txt` 和 `build-info.json`。
- 将本仓库的 `src/`、`configs/`、`util/` 合入完整官方工程，保留官方的根构建文件、`ext/`、`system/` 等缺失部分。

## 2. 验证单次仿真

```bash
bash docker/run.sh smoke
```

该命令实际运行一次 8×8 Mesh、uniform_random 流量、注入率 0.05、20,000 cycles 的 XY 仿真，通过项目的 Python 环境接口提取统计，校验接收量、延迟、仿真时间和路由编号。成功时输出 `SMOKE PASSED`。

另外两种路由可以分别验证：

```bash
bash docker/run.sh smoke --routing random_oblivious
bash docker/run.sh smoke --routing west_first
```

每次运行生成一个独立的 `outputs/smoke-时间-进程号/` 目录，其中有：

```text
run.log                       完整运行日志
run.json                      本次命令参数和启动时间
image-id.txt                  本次使用的镜像 ID
build-info.json               gem5、Python、NumPy、Matplotlib 信息
packages.txt                  容器软件包的实际版本
project-overlay.diff          本项目相对官方源码的已跟踪文件差异
project-overlay-status.txt    源码合入后新增、修改文件列表
smoke-summary.json            本次验证的统计结果
network_stats.txt             项目统计提取器的输出
m5out/                        gem5 原始统计与配置
```

## 3. 运行强化学习

先运行 1 轮 Q-learning，检查仿真、学习、表格输出和绘图是否连通：

```bash
bash docker/run.sh train qlearning --episodes 1 --seed 0
```

再按当前原始脚本的 50 轮设置运行：

```bash
bash docker/run.sh train qlearning --episodes 50 --seed 0
bash docker/run.sh train sarsa --episodes 50 --seed 0
bash docker/run.sh train expected-sarsa --episodes 50 --seed 0
```

每轮扫描 12 个注入率，每种方法 50 轮约执行 600 次仿真。每次命令独立保存到 `outputs/train-时间-进程号/`；表格、奖励和图片分别位于 `Tables/`、`Rewards_Hist/`、`Figures/`。还会保存实际执行的 Python 主脚本和环境接口代码。

`--seed` 固定 Python 和 NumPy 随机种子；gem5 沿用原脚本的默认种子。训练时 `m5out/` 沿用原代码行为，只保留最后一次仿真的统计，逐步历史保存在结果表格中。

## 4. 进入容器查看环境

```bash
bash docker/run.sh shell
```

工作目录为 `/home/tungthanhle/gem5`。沿用作者原始路径，因此不需要修改宿主机中的算法代码。退出终端后容器删除，挂载的结果仍保存在宿主机。

运行脚本使用当前用户的 UID/GID 保存结果，避免生成只能由 root 编辑的文件。不开放网络端口，不需要 GPU。

## 5. 容器内的必要适配

宿主机原始研究代码保持原样。镜像构建时只对环境接口做两项执行适配：

1. 将启动目标从 `gem5.debug` 改为已编译的 `gem5.opt`。
2. 将 `os.system()` 替换为检查退出状态的 `subprocess.check_call()`，并固定仿真工作目录，避免仿真失败后误读旧统计。

输出路径通过符号链接转到 `/results`，由宿主机脚本挂载到每次独立的结果目录。训练入口只替换请求的轮数，并设置随机种子；保留原始奖励、策略与 Q 更新公式。

这套配置用于跑通原代码。代码与论文的参数一致性、折扣因子传参、独立评估方法等问题仍见根目录 `REPRODUCTION_ZH.md`，需要在论文复现阶段分别核对。

## 6. 常见问题

若出现 `permission denied ... /var/run/docker.sock`，表示当前终端没有访问 Docker 服务的权限。先确保 `docker info` 能成功执行；若你平时使用 sudo 管理 Docker，也可以执行：

```bash
sudo bash docker/run.sh build
sudo bash docker/run.sh smoke
```

通过 sudo 运行时文件会按 root 用户保存，建议优先使用已经配置好 Docker 访问权限的普通用户终端。

若下载失败，可重试构建；已经完成的构建层会复用。默认使用官方 Ubuntu 软件源和 GitHub，不写入个人代理或凭据。Docker 的网络代理需按本机实际配置设置。

使用 `RLE_RESULTS_DIR` 更改输出根目录，或使用 `RLE_IMAGE` 更改镜像名：

```bash
RLE_RESULTS_DIR=/absolute/path/to/results bash docker/run.sh smoke
```
