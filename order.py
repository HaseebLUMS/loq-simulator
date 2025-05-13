from datetime import datetime
from typing import TYPE_CHECKING

class Order:
    def __init__(
            self, order_id: int, side: str,
            price: int, quantity: int,
            timestamp: int, tmp: int, I_m):
        self.order_id = order_id
        self.side = side  # 'bid' or 'ask'
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp or int(datetime.now().timestamp() * 1_000_000)
        self.tmp = tmp  # basically client ID
        self.I_m = I_m  #  mid-price ID

    def __repr__(self):
        return f"Order(id={self.order_id}, side={self.side}, price={self.price}, quantity={self.quantity}, timestamp={self.timestamp})"

    def __lt__(self, other):
        """Define less-than for automatic sorting by timestamp within SortedList."""
        if self.timestamp == other.timestamp: return self.tmp < other.tmp
        return self.timestamp < other.timestamp