# 第一阶段：项目理解与简单实验

报告入口：[项目初步分析报告](项目初步分析报告.md)。

本目录整理了代码阅读笔记、独立编写的教学小程序和实验结果。实验采用人为设定的路线与耗时，只用于理解排队、路线选择和评分学习，不代表论文复现结果。

```text
commit1/
├── README.md
├── 项目初步分析报告.md
└── learning/
    ├── 01_link_queue.py       # 观察均匀发送与集中发送的排队差别
    ├── simple_route_demo.py   # 两条假想路线的选择练习
    ├── route_experiments.py   # 五组参数与策略对照
    ├── q_learning_terminal.py # Q-learning 的逐步教学演示
    └── results/              # 五份对照实验 CSV
```

在仓库根目录运行，使用 Python 3 标准库即可：

```bash
python3 commit1/learning/01_link_queue.py
python3 commit1/learning/01_link_queue.py --burst
python3 commit1/learning/simple_route_demo.py
python3 commit1/learning/route_experiments.py
```

补充对照脚本会更新 `commit1/learning/results/` 下的五份 CSV。需要逐步观察 Q-learning 时，可以运行：

```bash
python3 commit1/learning/q_learning_terminal.py --episodes 1
```

原项目说明、模拟源码和 Docker 环境仍位于仓库根目录。
