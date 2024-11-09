from sortedcontainers import SortedDict, SortedList
from typing import TYPE_CHECKING
from order import Order
from datetime import datetime

'''
lob = LimitOrderBook()
lob.add_order(Order(1, 'buy', 100, 10))
lob.add_order(Order(2, 'sell', 95, 5))
lob.add_order(Order(3, 'sell', 105, 8))
lob.add_order(Order(4, 'buy', 100, 15, datetime(2024, 11, 9, 12, 30)))  # Custom timestamp
lob.display_order_book()
'''
class LimitOrderBook:
    def __init__(self):
        # SortedDict sorts prices automatically
        self.buy_orders = SortedDict(lambda x: -x)  # Highest price first for buys
        self.sell_orders = SortedDict()  # Lowest price first for sells

    def add_order(self, order: Order):
        """Add a new order to the LOB at the correct price level."""
        order_book = self.buy_orders if order.side == 'buy' else self.sell_orders
        if order.price not in order_book:
            order_book[order.price] = SortedList()

        # Add the order directly to the SortedList, which maintains order by timestamp
        order_book[order.price].add(order)
        print(f"Order added: {order}")
        self.match_orders()

    def match_orders(self):
        """Match buy and sell orders based on price and timestamp priority."""
        while self.buy_orders and self.sell_orders:
            best_bid = self.buy_orders.peekitem(0)  # Highest bid
            best_ask = self.sell_orders.peekitem(0)  # Lowest ask

            if best_bid[0] >= best_ask[0]:  # Check if there's a match
                bid_order = best_bid[1][0]  # Oldest order at the highest bid price
                ask_order = best_ask[1][0]  # Oldest order at the lowest ask price
                matched_quantity = min(bid_order.quantity, ask_order.quantity)

                # Print match details
                print(f"Matched {matched_quantity} units at {ask_order.price} between Order {bid_order.order_id} and Order {ask_order.order_id}")

                # Update order quantities
                bid_order.quantity -= matched_quantity
                ask_order.quantity -= matched_quantity

                # Remove orders that have been completely matched
                if bid_order.quantity == 0:
                    best_bid[1].pop(0)
                    if not best_bid[1]:  # Remove price level if no orders remain
                        del self.buy_orders[best_bid[0]]
                if ask_order.quantity == 0:
                    best_ask[1].pop(0)
                    if not best_ask[1]:  # Remove price level if no orders remain
                        del self.sell_orders[best_ask[0]]
            else:
                break  # No more matches possible

    def display_order_book(self):
        """Display the current state of the order book."""
        print("\nOrder Book:")
        print("Buy Orders:")
        for price, orders in self.buy_orders.items():
            for order in orders:
                print(order)

        print("Sell Orders:")
        for price, orders in self.sell_orders.items():
            for order in orders:
                print(order)
        print("")

# lob = LimitOrderBook()
# lob.add_order(Order(1, 'buy', 100, 10))
# lob.add_order(Order(2, 'sell', 95, 5))
# lob.add_order(Order(3, 'sell', 105, 8))
# lob.add_order(Order(4, 'buy', 100, 15))
# lob.display_order_book()