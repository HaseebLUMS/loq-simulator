import heapq
from typing import TYPE_CHECKING, List
from order import Order

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

def counter_local_loq_effect(orders: List[Order]) -> List[Order]:
    # use o.tmp to identify the LOQ index
    print("TODO: counter_local_loq_effect")
    return orders