from datetime import datetime
from typing import TYPE_CHECKING

class Order:
    def __init__(self, order_id: int, side: str, price: int, quantity: int, timestamp: int=None):
        self.order_id = order_id
        self.side = side  # 'bid' or 'ask'
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp or int(datetime.now().timestamp() * 1_000_000)
        self.tmp = 0  # Scratch space

    def __repr__(self):
        return f"Order(id={self.order_id}, side={self.side}, price={self.price}, quantity={self.quantity}, timestamp={self.timestamp})"

    def __lt__(self, other):
        """Define less-than for automatic sorting by timestamp within SortedList."""
        return self.timestamp < other.timestamp