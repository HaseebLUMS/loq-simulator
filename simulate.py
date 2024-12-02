from typing import List
import argparse
import numpy as np
from LOB import LimitOrderBook
from order import Order
import random
import utils
import config
import LOQ

def create_order_sequence(n) -> List[Order]:
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
            late = abs(t2[o] - t1[o])
            res[o] = late
            data.append(late)

    if config.LOGGING:
        print("50p Lateness: ", np.percentile(data, 50))
        print("90p Lateness: ", np.percentile(data, 90))
        print("99p Lateness: ", np.percentile(data, 99))
        print("Longest common subsequence: ", utils.find_longest_common_subsequence(o1, o2))

    return data

    # return utils.find_longest_common_subsequence(o1, o2)

def combine_halves(reordered_halves: List[List[Order]]):
    # reverse each list for efficient pop
    for h in reordered_halves: h.reverse()

    orders = []
    while True:
        remaining = False
        for h in reordered_halves:
            if (len(h) == 0): continue
            remaining = True
            orders.append(h.pop())
        if remaining == False: break
    return orders

def simulate(queue_size=None, total_orders=None):
    queue_size = queue_size if queue_size is not None else config.QUEUE_SIZE
    total_orders = total_orders if total_orders is not None else config.TOTAL_ORDERS

    # Create a sequence of orders
    orders = create_order_sequence(total_orders)

    # Feed them to a ME, which maintains an LOB and processes the sequence, and get output o1 denoting the matched orders in the sequence they got matched
    lob = LimitOrderBook()
    for o in orders: lob.add_order(o)

    o1 = lob.get_matched_orders_sequence()

    halves: List[List[Order]] = utils.create_halves(orders, config.TOTAL_LOQS)
    
    # Also feed the sequence to a LOQ simulator, which reorders the sequence emulating how LOQ would do it
    reordered_halves: List[List[Order]] = []
    for h in halves: reordered_halves.append(LOQ.emulate_loq(h, win=int((queue_size/100)*len(h))))

    # # Checking if they are monotonic
    # for h in reordered_halves:
    #     bids = []
    #     asks = []
    #     for o in h:
    #         if o.side == 'bid': bids.append(o)
    #         else: asks.append(o)

    #     h = bids
    #     for i in range(1, len(h)):
    #         if (h[i].timestamp >= h[i-1].timestamp): continue
    #         print("Halves Not monotonic!")
    #         exit(1)
        
    #     h = asks
    #     for i in range(1, len(h)):
    #         if (h[i].timestamp >= h[i-1].timestamp): continue
    #         print("Halves Not monotonic!")
    #         exit(1)

    reordered_orders = combine_halves(reordered_halves)

    # Counter network reordering by processing the `reordered_orders` in such a way
    # that ME only processes an order o from LOQ1 if it has received order o with larger ts from LOQ2 or LOQ2 has no orders left

    reordered_orders = LOQ.counter_local_loq_effect(reordered_orders)

    # Feed then reordered sequence to ME and get the output o2
    lob = LimitOrderBook()
    for o in reordered_orders:
        lob.add_order(o)
    
    o2 = lob.get_matched_orders_sequence()

    return compare_matched_orders(o1, o2)
    # print("largest common subsequence of MATCHED orders at ME: ", (100.0*l/max(len(o1), len(o2))), "%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some orders.")
    parser.add_argument(
        "--queue_size", "-qs",
        type=int,
        help="Size of the queue",
    )
    parser.add_argument(
        "--total_orders", "-to",
        type=int,
        help="Total number of orders",
    )

    args = parser.parse_args()

    # Pass command-line arguments to main
    simulate(queue_size=args.queue_size, total_orders=args.total_orders)
