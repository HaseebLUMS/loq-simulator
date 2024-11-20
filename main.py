from typing import TYPE_CHECKING, List

import numpy as np
from LOB import LimitOrderBook
from order import Order
import random
import utils
import config
import LOQ

def create_order_sequence() -> List[Order]:
    n = config.TOTAL_ORDERS
    orders: List[Order] = []
    timestamp = 1  # Start timestamps from 1
    bid_range = list(range(config.BID_RANGE[0], config.BID_RANGE[1]+1))
    ask_range = list(range(config.ASK_RANGE[0], config.ASK_RANGE[1]+1))

    for order_id in range(1, n + 1):
        # Randomly choose side as 'bid' or 'ask'
        side = 'bid' if random.choice([True, False]) else 'ask'

        # Set price based on side
        price = random.choice(bid_range) if side == 'bid' else random.choice(ask_range)

        quantity = 1

        # Create order
        order = Order(order_id=order_id, side=side, price=price, quantity=quantity, timestamp=timestamp)
        orders.append(order)

        # Increment timestamp for the next order
        timestamp += 1

    return orders

def compare_matched_orders(o1: List[int], o2: List[int]):
    t1 = {}
    t2 = {}
    for i, o in enumerate(o1): t1[o] = i
    for i, o in enumerate(o2): t2[o] = i

    res = {}
    data = []
    for o in t1:
        if o in t2 and o in t1:
            late = t2[o] - t1[o]
            res[o] = late
            data.append(late)

    print("25p Lateness: ", np.percentile(data, 25))
    print("50p Lateness: ", np.percentile(data, 50))
    print("90p Lateness: ", np.percentile(data, 90))
    print("99p Lateness: ", np.percentile(data, 99))
    return utils.find_longest_common_subsequence(o1, o2)

def combine_halves(half1: List[Order], half2: List[Order]): return [item for pair in zip(half1, half2) for item in pair]

def main():
    # Create a sequence of orders
    orders = create_order_sequence()

    # Feed them to a ME, which maintains an LOB and processes the sequence, and get output o1 denoting the matched orders in the sequence they got matched
    lob = LimitOrderBook()
    for o in orders: lob.add_order(o)

    o1 = lob.get_matched_orders_sequence()

    half1, half2 = utils.create_random_halves(orders)
    # Also feed the sequence to a LOQ simulator, which reorders the sequence emulating how LOQ would do it
    reordered_orders1 = LOQ.emulate_loq(half1, win=int((config.QUEUE_SIZE/100)*config.TOTAL_ORDERS))
    reordered_orders2 = LOQ.emulate_loq(half2, win=int((config.QUEUE_SIZE/100)*config.TOTAL_ORDERS))

    reordered_orders = combine_halves(reordered_orders1, reordered_orders2)

    # Feed then reordered sequence to ME and get the output o2
    lob = LimitOrderBook()
    for o in reordered_orders:
        lob.add_order(o)

    o2 = lob.get_matched_orders_sequence()

    print("Matched orders1: ", len(o1))
    print("Matched orders2: ", len(o2))

    l = compare_matched_orders(o1, o2)
    print("largest common subsequence of MATCHED orders at ME: ", (100.0*l/max(len(o1), len(o2))), "%")

if __name__ == "__main__":
    main()