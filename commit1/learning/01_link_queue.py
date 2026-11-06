#!/usr/bin/env python3
"""从零观察发送和排队：python3 commit1/learning/01_link_queue.py [--burst]。

这是教学用的离散时间模型，不是完整 NoC 仿真。
约定：每拍开始产生包，每拍最多传一个包，包在本拍结束时到达。
等待区容量不设上限，接收方总能接收；暂不模拟 flit 和流控。
"""

import argparse
from collections import deque


def simulate(arrivals):
    # arrivals 中的整数表示每拍新产生几个完整的数据包。
    waiting = deque()
    next_packet_id = 1
    tick = 0
    delays = []

    while tick < len(arrivals) or waiting:
        tick += 1
        count = arrivals[tick - 1] if tick <= len(arrivals) else 0

        # 本拍开始：新包加入等待区，排在已有包后面。
        new_names = []
        for _ in range(count):
            name = "P{}".format(next_packet_id)
            next_packet_id += 1
            waiting.append((name, tick))
            new_names.append(name)

        # 本拍最多传一个包；先排队的先发送。
        if waiting:
            name, created_tick = waiting.popleft()
            wait = tick - created_tick
            delay = wait + 1  # 等待时间，加上连线传输的一拍。
            delays.append(delay)
            sent = "{} 到达 B（等待 {} 拍，传输 1 拍，总用时 {} 拍）".format(
                name, wait, delay)
        else:
            sent = "连线空闲"

        print("第 {} 拍：".format(tick))
        print("  A 新产生：{}".format("、".join(new_names) or "无"))
        print("  本拍传送：{}".format(sent))
        print("  拍末仍在排队：{}".format(
            "、".join(name for name, _ in waiting) or "无"))

    print("\nB 共收到 {} 个包，平均每个包用时 {:.2f} 拍。".format(
        len(delays), sum(delays) / len(delays) if delays else 0.0))
    return delays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--burst", action="store_true", help="第一拍一次产生三个包")
    args = parser.parse_args()

    arrivals = [3, 0, 0] if args.burst else [1, 1, 1]
    print("A（发送方）── 每拍最多传一个包 ──→ B（接收方）")
    print("一拍就是模型向前推进一步；这里不指定真实的秒数。")
    print("三拍的新包数量：{}\n".format(arrivals))
    simulate(arrivals)


if __name__ == "__main__":
    main()
