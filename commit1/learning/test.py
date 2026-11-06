from collections import deque


def simulate_test():
    waiting = deque()
    next_packet_id = 1
    tick = 0
    delays = []
