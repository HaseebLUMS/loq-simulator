from sortedcontainers import SortedDict, SortedList
from typing import TYPE_CHECKING, List
from order import Order
from datetime import datetime

'''
lob = LimitOrderBook()
lob.add_order(Order(1, 'bid', 100, 10))
lob.add_order(Order(2, 'ask', 95, 5))
lob.add_order(Order(3, 'ask', 105, 8))
lob.add_order(Order(4, 'bid', 100, 15))
lob.display_order_book()
'''
class LimitOrderBook:
    def __init__(self):
        # SortedDict sorts prices automatically
        self.bid_orders = SortedDict(lambda x: -x)  # Highest price first for bids
        self.ask_orders = SortedDict()  # Lowest price first for asks
        self.matched = []
        self.inserted = []

    def add_order(self, order: Order):
        """Add a new order to the LOB at the correct price level."""
        self.inserted.append(order.order_id)
        order_book = self.bid_orders if order.side == 'bid' else self.ask_orders
        if order.price not in order_book:
            order_book[order.price] = SortedList()

        # Add the order directly to the SortedList, which maintains order by timestamp
        order_book[order.price].add(order)
        self.match_orders()

    def match_orders(self):
        """Match bid and ask orders based on price and timestamp priority."""
        while self.bid_orders and self.ask_orders:
            best_bid = self.bid_orders.peekitem(0)  # Highest bid
            best_ask = self.ask_orders.peekitem(0)  # Lowest ask

            if best_bid[0] >= best_ask[0]:  # Check if there's a match
                bid_order: Order = best_bid[1][0]  # Oldest order at the highest bid price
                ask_order: Order = best_ask[1][0]  # Oldest order at the lowest ask price
                matched_quantity = min(bid_order.quantity, ask_order.quantity)

                self.matched.append(bid_order.order_id)
                # self.matched.append(ask_order.order_id)

                # Update order quantities
                bid_order.quantity -= matched_quantity
                ask_order.quantity -= matched_quantity

                # Remove orders that have been completely matched
                if bid_order.quantity == 0:
                    best_bid[1].pop(0)
                    if not best_bid[1]:  # Remove price level if no orders remain
                        del self.bid_orders[best_bid[0]]
                if ask_order.quantity == 0:
                    best_ask[1].pop(0)
                    if not best_ask[1]:  # Remove price level if no orders remain
                        del self.ask_orders[best_ask[0]]
            else:
                break  # No more matches possible

    def display_order_book(self):
        """Display the current state of the order book."""
        print("\nOrder Book:")
        print("bid Orders:")
        for price, orders in self.bid_orders.items():
            for order in orders:
                print(order)

        print("ask Orders:")
        for price, orders in self.ask_orders.items():
            for order in orders:
                print(order)
        print("")

    '''Get the order ids of all the bids that got matched, in the order they got matched'''
    def get_matched_orders_sequence(self) -> List[str]:
        return self.matched
    
    '''Get the order ids in the insertion order'''
    def get_inserted_orders_sequence(self) -> List[str]:
        return self.inserted

# lob = LimitOrderBook()
# lob.add_order(Order(1, 'bid', 100, 10))
# lob.add_order(Order(2, 'ask', 95, 5))
# lob.add_order(Order(3, 'ask', 105, 8))
# lob.add_order(Order(4, 'bid', 100, 15))
# lob.display_order_book()