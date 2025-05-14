from collections import deque
import heapq
from itertools import groupby, zip_longest
from typing import TYPE_CHECKING, Dict, List
from order import Order
import config

def process_queues_for_loqv3(orders: List[Order], win: int):
    queue = []
    # Fill the queue
    window = orders[0:win]
    for order in window: heapq.heappush(queue, (order.timestamp, order.client, order))

    reordered_orders = []

    for order in orders[win:]:
        if queue: reordered_orders.append(heapq.heappop(queue)[2])

        heapq.heappush(queue, (order.timestamp, order.client, order))

    while queue: reordered_orders.append(heapq.heappop(queue)[2])

    return reordered_orders

def criticality(o: Order):
    '''returns 0 if critical, 1 o.w.'''
    if o.side == 'bid':
        if o.price >= config.MID_PRICE - config.ACTION_WINDOW: return 0  # yes critical
        else: return 1
    else:
        if o.price <= config.MID_PRICE + config.ACTION_WINDOW: return 0
        else: return 1

# LOQ with action window, also accounting mid-price in prioritization tuple
def emulate_loq_v4(orders: List[Order], win: int) -> List[Order]:
    queue = []

    window = orders[0:win]
    for order in window:
        heapq.heappush(queue, (order.I_m, criticality(order), order.timestamp, order.client, order))

    reordered_orders = []

    for order in orders[win:]:
        if queue: reordered_orders.append(heapq.heappop(queue)[-1])
        heapq.heappush(queue, (order.I_m, criticality(order), order.timestamp, order.client, order))

    while queue: reordered_orders.append(heapq.heappop(queue)[-1])
    return reordered_orders

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
    for index, seq in enumerate(orders):
        for o in seq:
            o.tmp = index
            if o.tmp not in per_q_orders: per_q_orders[o.tmp] = deque()
            per_q_orders[o.tmp].append(o)

    res = []
    while True:
        min_ts = 10**100  # a very large number like INT_MAX
        min_client = 10**100
        ind = -1
        for loq_id in per_q_orders:
            if len(per_q_orders[loq_id]) == 0: continue

            if per_q_orders[loq_id][0].timestamp == min_ts:
                if per_q_orders[loq_id][0].client < min_client:
                    min_ts = per_q_orders[loq_id][0].timestamp
                    min_client = per_q_orders[loq_id][0].client
                    ind = loq_id
            elif per_q_orders[loq_id][0].timestamp < min_ts:
                min_ts = per_q_orders[loq_id][0].timestamp
                min_client = per_q_orders[loq_id][0].client
                ind = loq_id

        if ind == -1: break
        res.append(per_q_orders[ind].popleft())
    return res