"""理解选路原理的小练习：python3 commit1/learning/simple_route_demo.py。

A 路线近但每步只能送 2 个包，B 路线远但每步能送 5 个包。
假设一批包同时出发，各路线独立排队，每步发送的包一起到达。
这些条件是人为设定的，不对应项目中的三种真实路由规则。
"""

import random


# 每条路线分别记录：基础传输时间、每步最多发送的包数。
ROUTES = {"A": (1, 2), "B": (2, 5)}


def average_delay(packet_count, route, routes=None):
    if packet_count < 1:
        raise ValueError("包数必须大于 0")
    if routes is None:
        routes = ROUTES
    travel_time, capacity = routes[route]
    if capacity < 1:
        raise ValueError("每步发送容量必须大于 0")
    # 编号从 0 开始：前 capacity 个包不等待，下一批等待 1 步。
    delays = [travel_time + i // capacity for i in range(packet_count)]
    return sum(delays) / packet_count


def learn(packet_count, rounds=200, exploration=0.2, seed=0,
          routes=None, noise=0.0):
    if routes is None:
        routes = ROUTES
    rng = random.Random(seed)  # 固定随机数，方便重复观察。
    scores = {route: 0.0 for route in routes}
    for _ in range(rounds):
        if rng.random() < exploration:  # 留出一些机会尝试另一条路线。
            route = rng.choice(list(routes))
        else:
            route = max(scores, key=scores.get)

        observed_delay = average_delay(packet_count, route, routes)
        if noise:
            observed_delay += rng.uniform(-noise, noise)
        reward = -observed_delay
        # 新的评分向这次得到的评价靠近一点。
        scores[route] += 0.2 * (reward - scores[route])

    return max(scores, key=scores.get)


def main():
    print("人为设定的路线练习；时间单位为模型中的一步。")
    for packet_count in (2, 20):
        delay_a = average_delay(packet_count, "A")
        delay_b = average_delay(packet_count, "B")
        selected = learn(packet_count)
        print(f"同时发送 {packet_count} 个包：A 平均 {delay_a:.2f} 步，"
              f"B 平均 {delay_b:.2f} 步；练习后选择 {selected}")


if __name__ == "__main__":
    main()
