#!/usr/bin/env python3
"""Q-learning 教学示例：只用 Python 标准库，不调用 gem5。

运行：python3 commit1/learning/q_learning_terminal.py
逐步看一轮：python3 commit1/learning/q_learning_terminal.py --episodes 1

延迟全部为人为设定的教学数据，不是 NoC 仿真，也不是论文实验结果。
保留原项目的“负载 → 选路由 → 负延迟奖励 → Q 更新”结构。
为便于理解，使用三个负载、固定探索率和独立的 alpha/gamma 参数；
动作不会改变下一个负载，每轮按固定顺序扫描三个负载。
"""

import argparse
import random


ACTIONS = ("xy", "random_oblivious", "west_first")
STATES = (0.10, 0.30, 0.60)

# 每一行依次对应三种动作的延迟。人为安排不同负载下的最佳动作，
# 只是为了观察算法能否从反馈中学出这张表的规律。
TEACHING_LATENCIES = {
    0.10: (15.0, 18.0, 20.0),
    0.30: (45.0, 30.0, 38.0),
    0.60: (150.0, 110.0, 70.0),
}


def choose_action(q_values, epsilon, rng):
    """epsilon 概率随机尝试，其余时间选择当前 Q 值最大的动作。"""
    if rng.random() < epsilon:
        return rng.randrange(len(ACTIONS)), "探索"
    return max(range(len(ACTIONS)), key=lambda a: q_values[a]), "利用"


def update_q(old_q, next_best_q, reward, alpha, gamma):
    """对应原项目 icn_gym.py 中的 update_Q()。"""
    return old_q + alpha * (reward + gamma * next_best_q - old_q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=1000, help="训练轮数，默认 1000")
    parser.add_argument("--show-episodes", type=int, default=2, help="打印前几轮的细节")
    parser.add_argument("--seed", type=int, default=0, help="随机种子")
    args = parser.parse_args()
    if args.episodes < 1 or args.show_episodes < 0:
        parser.error("episodes 必须大于 0，show-episodes 必须不小于 0")

    rng = random.Random(args.seed)
    alpha = 0.1  # 学习率：每次更新接受多少新信息。
    gamma = 0.9  # 折扣因子：对下一状态预期收益的重视程度。
    epsilon = 0.2  # 探索率：20% 的机会随机选择动作。
    q_table = {state: [0.0] * len(ACTIONS) for state in STATES}

    print("这是人为延迟表上的 Q-learning 教学演示，不运行 gem5。")
    print("所有延迟均为教学数值，不能用于评价真实路由性能。")
    print("alpha={}，gamma={}，epsilon={}\n".format(alpha, gamma, epsilon))

    for episode in range(1, args.episodes + 1):
        if episode <= args.show_episodes:
            print("第 {} 轮：".format(episode))

        for index, state in enumerate(STATES):
            # 1. 当前状态是负载；从 Q 表选择一种路由算法。
            action, reason = choose_action(q_table[state], epsilon, rng)

            # 2. 这里查教学表；原项目在这个位置调用 gem5 获得延迟。
            latency = TEACHING_LATENCIES[state][action]
            reward = -latency

            # 3. 进入下一个负载；本轮最后一步没有未来收益。
            if index + 1 < len(STATES):
                next_state = STATES[index + 1]
                next_best_q = max(q_table[next_state])
            else:
                next_best_q = 0.0

            # 4. 只更新当前“负载—动作”对应的那个 Q 值。
            old_q = q_table[state][action]
            new_q = update_q(old_q, next_best_q, reward, alpha, gamma)
            q_table[state][action] = new_q

            if episode <= args.show_episodes:
                print("  负载={:.2f}，{}选择 {}，教学延迟={:.1f}，奖励={:.1f}".format(
                    state, reason, ACTIONS[action], latency, reward))
                print("  Q = {:.3f} + {} × ({:.1f} + {} × {:.3f} - ({:.3f})) = {:.3f}".format(
                    old_q, alpha, reward, gamma, next_best_q, old_q, new_q))
        if episode <= args.show_episodes:
            print()

    print("训练 {} 轮后的 Q 表（数值越大越好）：".format(args.episodes))
    print("负载       xy       random_oblivious       west_first")
    for state in STATES:
        print("{:.2f}   {:9.3f}   {:18.3f}   {:14.3f}".format(state, *q_table[state]))

    print("\n关闭探索后，各负载的选择：")
    for state in STATES:
        best = max(range(len(ACTIONS)), key=lambda a: q_table[state][a])
        table_best = min(range(len(ACTIONS)), key=lambda a: TEACHING_LATENCIES[state][a])
        print("  {:.2f} → {}；教学表中最低延迟的动作：{}".format(
            state, ACTIONS[best], ACTIONS[table_best]))
    print("\nQ 值包含未来奖励，因此不等于当前这一步的负延迟。")
    print("少量轮数的输出只展示更新过程，不代表已经学会最佳选择。")


if __name__ == "__main__":
    main()
