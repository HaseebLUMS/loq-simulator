from collections import deque
import heapq
from itertools import zip_longest
from typing import TYPE_CHECKING, Dict, List
from order import Order
import config

def emulate_loq(orders: List[Order], win: int) -> List[Order]:
    bids = []
    asks = []

    # Fill the queue
    window = orders[0:win]
    for order in window:
        if order.side == 'bid': heapq.heappush(bids, (-order.price, order.timestamp, order))
        else: heapq.heappush(asks, (order.price, order.timestamp, order))

    reordered_orders = []

    # Dequeu round robin and keep on filling the queue with remaining orders
    for order in orders[win:]:
        if bids: reordered_orders.append(heapq.heappop(bids)[2])
        if asks: reordered_orders.append(heapq.heappop(asks)[2])

        if order.side == 'bid': heapq.heappush(bids, (-order.price, order.timestamp, order))
        else: heapq.heappush(asks, (order.price, order.timestamp, order))

    # Drain the queue
    while bids or asks:
        if bids: reordered_orders.append(heapq.heappop(bids)[2])
        if asks: reordered_orders.append(heapq.heappop(asks)[2])

    return reordered_orders

def process_queues_for_loqv3(orders: List[Order], win: int):
    queue = []
    # Fill the queue
    window = orders[0:win]
    for order in window: heapq.heappush(queue, (order.timestamp, order))

    reordered_orders = []

    for order in orders[win:]:
        if queue: reordered_orders.append(heapq.heappop(queue)[1])

        heapq.heappush(queue, (order.timestamp, order))

    while queue: reordered_orders.append(heapq.heappop(queue)[1])

    return reordered_orders

# Latest LOQ version
# Does not do round robin, does lowest timestamp instead
# + defines an action window, stuff inside the action window is sorted based on ts
# and the stuff outside of the window is also sorted based on ts
# => This is as opposed to sorting everything together based on ts
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

# Does not do round robin, does lowest timestamp instead
def emulate_loq_v2(orders: List[Order], win: int) -> List[Order]:
    bids = []
    asks = []

    # Fill the queue
    window = orders[0:win]
    for order in window:
        if order.side == 'bid': heapq.heappush(bids, (-order.price, order.timestamp, order))
        else: heapq.heappush(asks, (order.price, order.timestamp, order))

    reordered_orders = []

    for order in orders[win:]:

        if bids and (not asks or bids[0][1] <= asks[0][1]): reordered_orders.append(heapq.heappop(bids)[2])
        elif asks: reordered_orders.append(heapq.heappop(asks)[2])

        if order.side == 'bid': heapq.heappush(bids, (-order.price, order.timestamp, order))
        else: heapq.heappush(asks, (order.price, order.timestamp, order))

    while bids or asks:
        if bids and (not asks or bids[0][1] <= asks[0][1]): reordered_orders.append(heapq.heappop(bids)[2])
        elif asks: reordered_orders.append(heapq.heappop(asks)[2])

    return reordered_orders


# Emulate: ME only processes an order o from LOQ1 if it has received order o with larger ts from LOQ2 or LOQ2 has no orders left
def combine_orders_from_loqs(orders: List[List[Order]]) -> List[Order]:
    per_loq_orders: Dict[int, deque[Order]] = {}
    for seq in orders:
        for o in seq:
            if o.tmp not in per_loq_orders: per_loq_orders[o.tmp] = deque()
            per_loq_orders[o.tmp].append(o)

    res = []
    while True:
        min_ts = 10**100  # a very large number like INT_MAX
        ind = -1
        for loq_id in per_loq_orders:
            if len(per_loq_orders[loq_id]) == 0: continue

            if per_loq_orders[loq_id][0].timestamp < min_ts:
                min_ts = per_loq_orders[loq_id][0].timestamp
                ind = loq_id

        if ind == -1: break
        res.append(per_loq_orders[ind].popleft())
    return res


# TODO: find who has the lowest ask (highest bid) with the lowest tg
# Not Used Now
def counter_local_loq_effect_based_on_price_ts(orders: List[Order]) -> List[Order]:
    per_loq_orders: Dict[int, List[deque[Order]]] = {}
    for o in orders:
        if (o.tmp not in per_loq_orders):
            per_loq_orders[o.tmp] = [deque(), deque()]  # [bids, asks]
        if o.side == 'bid': per_loq_orders[o.tmp][0].append(o)
        else: per_loq_orders[o.tmp][1].append(o)

    # Get the highest bid with lowest ts
    
    # Get the lowest ask with lowest ts

    res_bids: List[Order] = []
    while True:
        max_bid_price = 0
        min_ts = -1
        ind = -1
        for loq_id in per_loq_orders:
            if len(per_loq_orders[loq_id][0]) == 0: continue
            if per_loq_orders[loq_id][0][0].price > max_bid_price:
                max_bid_price = per_loq_orders[loq_id][0][0].price
                ind = loq_id
                min_ts = per_loq_orders[loq_id][0][0].timestamp

            if per_loq_orders[loq_id][0][0].price == max_bid_price and per_loq_orders[loq_id][0][0].timestamp < min_ts:
                min_ts = per_loq_orders[loq_id][0][0].timestamp
                ind = loq_id

        if ind == -1: break
        res_bids.append(per_loq_orders[ind][0].popleft())

    res_asks: List[Order] = []
    while True:
        min_ask_price = 10**100  # arbitrary large num
        min_ts = -1
        ind = -1
        for loq_id in per_loq_orders:
            if len(per_loq_orders[loq_id][1]) == 0: continue
            if per_loq_orders[loq_id][1][0].price < min_ask_price:
                min_ask_price = per_loq_orders[loq_id][1][0].price
                ind = loq_id
                min_ts = per_loq_orders[loq_id][1][0].timestamp

            if per_loq_orders[loq_id][1][0].price == min_ask_price and per_loq_orders[loq_id][1][0].timestamp < min_ts:
                min_ts = per_loq_orders[loq_id][1][0].timestamp
                ind = loq_id

        if ind == -1: break
        res_asks.append(per_loq_orders[ind][1].popleft())

    
    res_orders: List[Order] = [item for pair in zip_longest(res_bids, res_asks) for item in pair if item is not None]
    return res_orders