from collections import deque
import heapq
from itertools import zip_longest
from typing import TYPE_CHECKING, Dict, List
from order import Order
import config

def process_queues_for_loqv3(orders: List[Order], win: int):
    queue = []
    # Fill the queue
    window = orders[0:win]
    for order in window: heapq.heappush(queue, (order.timestamp, order.tmp, order))

    reordered_orders = []

    for order in orders[win:]:
        if queue: reordered_orders.append(heapq.heappop(queue)[2])

        heapq.heappush(queue, (order.timestamp, order.tmp, order))

    while queue: reordered_orders.append(heapq.heappop(queue)[2])

    return reordered_orders

# LOQ with action window, also accounting mid-price in prioritization tuple
def emulate_loq_v4(orders: List[Order], win: int) -> List[Order]:
    res: List[Order] = []

    orders_with_same_I_m: List[Order] = []
    for o in orders:
        if (len(orders_with_same_I_m) == 0):
            orders_with_same_I_m.append(o)
        elif (o.I_m == orders_with_same_I_m[-1].I_m):
            orders_with_same_I_m.append(o)
        else:
            tmp_res = emulate_loq_v3(orders_with_same_I_m, win)
            for elem in tmp_res: res.append(elem)
            orders_with_same_I_m = [o]

    if (len(orders_with_same_I_m)):
        tmp_res = emulate_loq_v3(orders_with_same_I_m, win)
        for elem in tmp_res: res.append(elem)

    return res

# LOQ with action window, not accounting mid-price in prioritization tuple
def emulate_loq_v3(orders: List[Order], win: int) -> List[Order]:
    # the ones within action window
    orders1 = []

    # the ones outside of the action window
    orders2 = []

    for o in orders:
        if o.side == 'bid':
            if o.price >= config.MID_PRICE - config.ACTION_WINDOW:
                orders1.append(o)
            else: orders2.append(o)
        else:
            if o.price <= config.MID_PRICE + config.ACTION_WINDOW:
                orders1.append(o)
            else: orders2.append(o)

    res = process_queues_for_loqv3(orders1, win)
    res += process_queues_for_loqv3(orders2, win)
    return res

# Emulate: ME only processes an order o from P1 if it has received order o with larger ts from P2 or P2 has no orders left
def combine_orders_from_downstreams(orders: List[List[Order]]) -> List[Order]:
    per_q_orders: Dict[int, deque[Order]] = {}
    for seq in orders:
        for o in seq:
            if o.tmp not in per_q_orders: per_q_orders[o.tmp] = deque()
            per_q_orders[o.tmp].append(o)

    res = []
    while True:
        min_ts = 10**100  # a very large number like INT_MAX
        min_tmp = 10**100
        ind = -1
        for loq_id in per_q_orders:
            if len(per_q_orders[loq_id]) == 0: continue

            if per_q_orders[loq_id][0].timestamp == min_ts:
                if per_q_orders[loq_id][0].tmp < min_tmp:
                    min_ts = per_q_orders[loq_id][0].timestamp
                    min_tmp = per_q_orders[loq_id][0].tmp
                    ind = loq_id
            elif per_q_orders[loq_id][0].timestamp < min_ts:
                min_ts = per_q_orders[loq_id][0].timestamp
                min_tmp = per_q_orders[loq_id][0].tmp
                ind = loq_id

        if ind == -1: break
        res.append(per_q_orders[ind].popleft())
    return res