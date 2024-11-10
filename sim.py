import heapq
from typing import TYPE_CHECKING, List
from LOB import LimitOrderBook
from order import Order
import random
import utils

TOTAL_ORDERS = 10

def create_order_sequence() -> List[Order]:
    n = TOTAL_ORDERS
    orders: List[Order] = []
    timestamp = 1  # Start timestamps from 1
    bid_range = [1, 2, 3, 4, 5]
    ask_range = [4, 5, 6, 7, 8]

    for order_id in range(1, n + 1):
        # Randomly choose side as 'bid' or 'ask'
        side = 'bid' if random.choice([True, False]) else 'ask'

        # Set price based on side
        price = random.choice(bid_range) if side == 'bid' else random.choice(ask_range)

        quantity = 1

        # Create order with incremental timestamp
        order = Order(order_id=order_id, side=side, price=price, quantity=quantity, timestamp=timestamp)
        orders.append(order)

        # Increment timestamp for the next order
        timestamp += 1

    for o in orders:
        print(o)
    return orders

def emulate_loq(orders: List[Order], win) -> List[Order]:
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


def compare_matched_orders(o1: List[int], o2: List[int]):
    return utils.find_longest_common_subsequence(o1, o2)

def main():
    # Create a sequence of orders, containing several prices, and traders
    orders = create_order_sequence()
    # orders = [
    #     Order(1, 'bid', 5, 1, 1),
    #     Order(2, 'ask', 5, 1, 2),
    #     Order(3, 'ask', 4, 1, 3),
    # ]

    # Feed them to a ME, which maintains an LOB and processes the sequence, and get output O denoting which order got matched with what other order
    lob = LimitOrderBook()
    for o in orders:
        lob.add_order(o)

    o1 = lob.get_matched_orders_sequence()
    print("Matched orders1: ", len(o1))

    # Also feed the sequence to a LOQ simulator, which reorders the sequence emulating how LOQ would do it
    reordered_orders = emulate_loq(orders, win=3)
    # reordered_orders = utils.windowed_shuffle(orders, 10)

    # Feed then reordered sequence to ME and get the output O'
    lob = LimitOrderBook()
    for o in reordered_orders:
        lob.add_order(o)

    o2 = lob.get_matched_orders_sequence()
    print("Matched orders2: ", len(o2))

    # Compare o1 to o2
    if o1 == o2:
        print("Exactly the same")
    else:
        print("Different matched orders")
    
    print(o1)
    print(o2)
    # l = compare_matched_orders(o1, o2)
    # print("Common matched orders: ", (100.0*l/len(o1)), "%")

if __name__ == "__main__":
    main()