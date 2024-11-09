from typing import TYPE_CHECKING, List
from LOB import LimitOrderBook
from order import Order
import random
import utils

TOTAL_ORDERS = 10_000

def create_order_sequence() -> List[Order]:
    n = TOTAL_ORDERS
    orders = []
    timestamp = 1  # Start timestamps from 1
    buy_range = [1, 2, 3]
    sell_range = [3, 4, 5]

    for order_id in range(1, n + 1):
        # Randomly choose side as 'buy' or 'sell'
        side = 'buy' if random.choice([True, False]) else 'sell'

        # Set price based on side
        price = random.choice(buy_range) if side == 'buy' else random.choice(sell_range)

        quantity = 1

        # Create order with incremental timestamp
        order = Order(order_id=order_id, side=side, price=price, quantity=quantity, timestamp=timestamp)
        orders.append(order)

        # Increment timestamp for the next order
        timestamp += 1

    return orders


def emulate_loq(orders: List[Order]):
    # TODO ...
    return orders

def compare_matched_orders(o1: List[int], o2: List[int]):
    return utils.find_longest_common_subsequence(o1, o2)

def main():
    # Create a sequence of orders, containing several prices, and traders
    orders = create_order_sequence()

    # Feed them to a ME, which maintains an LOB and processes the sequence, and get output O denoting which order got matched with what other order
    lob = LimitOrderBook()
    for o in orders:
        lob.add_order(o)

    o1 = lob.get_matched_orders_sequence()
    print("Matched orders1: ", len(o1))

    # Also feed the sequence to a LOQ simulator, which reorders the sequence emulating how LOQ would do it
    reordered_orders = emulate_loq(orders)

    # Feed then reordered sequence to ME and get the output O'
    lob = LimitOrderBook()
    for o in reordered_orders:
        lob.add_order(o)

    o2 = lob.get_matched_orders_sequence()
    print("Matched orders2: ", len(o2))

    # Compare o1 to o2
    l = compare_matched_orders(o1, o2)
    print("Common matched orders: ", (100.0*l/len(o1)), "%")

if __name__ == "__main__":
    main()