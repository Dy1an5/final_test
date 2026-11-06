"""选路理解练习的补充对照：python3 commit1/learning/route_experiments.py。

只用标准库，结果写到本文件旁的 results/，不调用 gem5。
所有路线参数和观测波动都为教学设定，不对应真实硬件测量。
"""

import csv
from pathlib import Path
from statistics import mean

from simple_route_demo import ROUTES, average_delay, learn


RESULTS = Path(__file__).resolve().parent / "results"
LOADS = (2, 4, 6, 8, 10, 12, 16, 20, 30, 40)


def save_table(name, headers, rows):
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / (name + ".csv")).open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)
    print("\n" + name)
    print(" | ".join(headers))
    for row in rows:
        print(" | ".join(f"{value:.3f}" if isinstance(value, float) else str(value)
                         for value in row))


def load_comparison():
    rows = []
    for packets in LOADS:
        delay_a = average_delay(packets, "A")
        delay_b = average_delay(packets, "B")
        best = "A" if delay_a <= delay_b else "B"
        selected = learn(packets)
        rows.append((packets, delay_a, delay_b, best, selected))
    save_table("load_comparison", ["包数", "A耗时", "B耗时", "较快路线", "学习选择"], rows)


def strategy_comparison():
    # 每种包数出现次数相同，各场景的平均耗时再取平均。
    delay_a = mean(average_delay(packets, "A") for packets in LOADS)
    delay_b = mean(average_delay(packets, "B") for packets in LOADS)
    learned = mean(average_delay(packets, learn(packets)) for packets in LOADS)
    oracle = mean(min(average_delay(packets, route) for route in ROUTES)
                  for packets in LOADS)
    rows = [("固定A", delay_a), ("固定B", delay_b),
            ("等概率随机选择的理论平均", (delay_a + delay_b) / 2),
            ("各场景学习200次后的选择", learned), ("已知全部耗时后直接取最小", oracle)]
    save_table("strategy_comparison", ["方法", "场景平均耗时"], rows)


def capacity_comparison():
    rows = []
    for capacity in (1, 2, 3, 5, 8):
        routes = {"A": (1, 2), "B": (2, capacity)}
        rows.append((capacity, average_delay(20, "A", routes),
                     average_delay(20, "B", routes), learn(20, routes=routes)))
    save_table("capacity_comparison", ["B容量", "20个包A耗时", "20个包B耗时", "学习选择"], rows)


def learning_comparison():
    # 每个训练次数采用相同的四个场景，每个场景重复50个随机种子。
    # 训练耗时添加[-1,1]的波动；检查最终选择时使用无波动耗时。
    packets_list = (2, 6, 10, 20)
    rows = []
    for rounds in (1, 5, 20, 100, 500):
        correct = 0
        delays = []
        for packets in packets_list:
            best_delay = min(average_delay(packets, route) for route in ROUTES)
            for seed in range(50):
                selected = learn(packets, rounds=rounds, seed=seed, noise=1.0)
                delay = average_delay(packets, selected)
                correct += abs(delay - best_delay) < 1e-9
                delays.append(delay)
        rows.append((rounds, 100 * correct / len(delays), mean(delays)))
    save_table("learning_comparison", ["每场景学习次数", "较快路线选择比例%", "评估平均耗时"], rows)


def exploration_comparison():
    # 在与上一项相同的四个场景中比较不同的尝试比例。
    rows = []
    for exploration in (0.0, 0.1, 0.2, 0.5, 1.0):
        correct = 0
        for packets in (2, 6, 10, 20):
            best_delay = min(average_delay(packets, route) for route in ROUTES)
            for seed in range(50):
                selected = learn(packets, rounds=100, exploration=exploration,
                                 seed=seed, noise=1.0)
                correct += abs(average_delay(packets, selected) - best_delay) < 1e-9
        rows.append((exploration, 100 * correct / 200))
    save_table("exploration_comparison", ["随机尝试比例", "较快路线选择比例%"], rows)


def main():
    print("教学条件下的补充实验：全部时间均为模型步数。")
    load_comparison()
    strategy_comparison()
    capacity_comparison()
    learning_comparison()
    exploration_comparison()
    print(f"\nCSV 保存到：{RESULTS}")


if __name__ == "__main__":
    main()
